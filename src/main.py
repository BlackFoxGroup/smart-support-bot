"""VPS to VPN Telegram support bot — long-polling entrypoint."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import sys
from pathlib import Path

# Allow `python -m src.main` and `python src/main.py` from project root
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeChat

from src.ai.client import AIClient
from src.config import Settings, load_settings
from src.control.audit import AuditLog
from src.control.registry import AgentRegistry
from src.control.service import ControlService
from src.conversation_analysis_job import run_conversation_analysis_job
from src.handlers.admin_control import setup_admin_control_router
from src.handlers.admin_settings import setup_admin_settings_router
from src.handlers.chat import setup_chat_router
from src.handlers.group import setup_group_router
from src.handlers.menu import setup_menu_router
from src.handlers.safety_confirm import setup_safety_router
from src.handlers.start import (
    BOT_COMMANDS,
    BOT_COMMANDS_ADMIN,
    BOT_COMMANDS_FA,
    BOT_COMMANDS_RU,
    BOT_COMMANDS_ZH,
    setup_start_router,
)
from src.knowledge.catalog_search import CatalogSiteSearch
from src.knowledge.intents import IntentMatcher
from src.knowledge.loader import KnowledgeLoader
from src.knowledge.product_catalogs import load_product_catalogs
from src.nightly_subscription_job import run_nightly_subscription_job
from src.safety.state import write_heartbeat
from src.social_news_job import run_social_news_job
from src.storage.bot_settings import BotSettingsStore
from src.storage.metrics import MetricsStore
from src.storage.users import UserStore


async def _heartbeat_loop() -> None:
    """Write a live heartbeat so the independent watchdog can detect a dead bot."""
    while True:
        try:
            write_heartbeat(pid=os.getpid(), status="ok")
        except Exception:  # noqa: BLE001
            logging.getLogger("smart-support-bot").exception("heartbeat write failed")
        await asyncio.sleep(10)


async def _register_bot_commands(bot: Bot, settings: Settings) -> None:
    """Public slash menu for everyone; admin commands only in admin private chats."""
    await bot.set_my_commands(BOT_COMMANDS)
    await bot.set_my_commands(BOT_COMMANDS_FA, language_code="fa")
    await bot.set_my_commands(BOT_COMMANDS_RU, language_code="ru")
    await bot.set_my_commands(BOT_COMMANDS_ZH, language_code="zh")
    public_plus_admin = BOT_COMMANDS + BOT_COMMANDS_ADMIN
    for admin_id in settings.bot_admin_ids:
        try:
            scope = BotCommandScopeChat(chat_id=admin_id)
            await bot.set_my_commands(public_plus_admin, scope=scope)
        except Exception:  # noqa: BLE001
            logging.getLogger("smart-support-bot").warning(
                "Could not set admin command scope for chat_id=%s", admin_id
            )


async def run() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    log = logging.getLogger("smart-support-bot")

    users = UserStore(settings.users_db_path)
    metrics = MetricsStore(settings.data_dir / "bot_metrics.json")

    # Control Plane — independent of the active LLM (encrypted agent registry)
    master_secret = settings.telegram_bot_token
    registry = AgentRegistry(
        settings.data_dir / "agent_registry.json",
        master_secret=master_secret,
    )
    if registry.bootstrap_from_settings(settings):
        log.info("Agent registry seeded from environment Primary agent")
    audit = AuditLog(settings.data_dir / "control_audit.jsonl")
    control = ControlService(settings, registry, audit)

    bot_settings = BotSettingsStore(
        settings.data_dir / "bot_settings.json",
        master_secret=master_secret,
    )
    if bot_settings.bootstrap_from_settings(settings):
        log.info("Bot settings seeded from environment (messages + panel)")

    from src.access import AdminAccess
    from src.ai.persona import apply_owner_info
    from src.health_job import run_health_report_job
    from src.runtime.gate import run_titil_gate

    run_titil_gate(
        project_root=settings.project_root,
        knowledge_root=settings.knowledge_root,
        data_dir=settings.data_dir,
    )
    apply_owner_info(await bot_settings.get_owner())
    ui_prefs = await bot_settings.get_ui_settings()
    from src.ui import admin_keyboards as ak

    ak.set_settings_columns(int(ui_prefs.get("settings_columns") or 2))
    customs = await bot_settings.list_custom_buttons(menu="settings")
    try:
        from src.generated.buttons import list_generated_buttons, preload_all

        generated = list_generated_buttons(menu="settings", refresh=True)
        loaded = preload_all()
        log.info("Generated admin buttons loaded: %s modules", loaded)
    except Exception as exc:  # noqa: BLE001
        log.warning("Generated buttons preload skipped: %s", exc)
        generated = []
    ak.refresh_custom_button_labels(list(customs) + list(generated))
    access = AdminAccess(settings, bot_settings)

    knowledge = KnowledgeLoader(settings)
    knowledge.load()

    if settings.source_catalog_sync_on_start:
        try:
            from src.knowledge.source_catalog.pipeline import run_sync

            payload = run_sync(
                settings.vps_to_vpn_source,
                settings.knowledge_root,
                settings.data_dir,
                force=False,
            )
            log.info(
                "source catalog sync: features=%s missing=%s",
                (payload.get("stats") or {}).get("features"),
                (payload.get("validation") or {}).get("missing"),
            )
        except Exception:  # noqa: BLE001
            log.exception("source catalog sync skipped")

    products = load_product_catalogs(settings.knowledge_root)
    log.info("Product catalogs ready: %s", [p.product_id for p in products])
    try:
        from src.knowledge.catalog_index import write_catalog_indexes

        write_catalog_indexes(settings.knowledge_root, settings.project_root)
        knowledge.load()
    except Exception:  # noqa: BLE001
        log.exception("catalog index markdown write skipped")

    intents = IntentMatcher(settings)
    intents.load()

    catalog = CatalogSiteSearch(settings)
    catalog.load()

    from src.knowledge.refresh import register_knowledge_reload

    def _reload_ai_knowledge() -> None:
        load_product_catalogs(settings.knowledge_root)
        try:
            from src.knowledge.catalog_index import write_catalog_indexes

            write_catalog_indexes(settings.knowledge_root, settings.project_root)
        except Exception:  # noqa: BLE001
            log.exception("catalog index refresh failed")
        knowledge.load()
        intents.load()
        catalog.load()
        log.info("AI knowledge reloaded after catalog/product change")

    register_knowledge_reload(_reload_ai_knowledge)

    ai = AIClient(settings, control=control)
    await ai.start()

    # Plain text: LLM replies may include characters that break HTML/Markdown parse modes
    bot = Bot(token=settings.telegram_bot_token)
    from src.branding import get_bot_display_name, sync_telegram_bot_name

    await sync_telegram_bot_name(bot, get_bot_display_name())
    await _register_bot_commands(bot, settings)
    nightly_task: asyncio.Task | None = None
    social_news_task: asyncio.Task | None = None
    convo_analysis_task: asyncio.Task | None = None
    health_task: asyncio.Task | None = None
    heartbeat_task: asyncio.Task | None = None

    dp = Dispatcher()
    dp.include_router(
        setup_start_router(users, settings=settings, metrics=metrics, access=access)
    )
    # Settings before agent control so message/panel wizards take priority
    dp.include_router(
        setup_admin_settings_router(
            users,
            settings=settings,
            bot_settings=bot_settings,
            audit=audit,
            control=control,
            ai=ai,
            access=access,
        )
    )
    dp.include_router(
        setup_admin_control_router(
            users,
            settings=settings,
            metrics=metrics,
            control=control,
            bot_settings=bot_settings,
            access=access,
        )
    )
    dp.include_router(setup_safety_router(users, settings=settings))
    dp.include_router(
        setup_menu_router(
            users,
            settings=settings,
            metrics=metrics,
            access=access,
            bot_settings=bot_settings,
            control=control,
        )
    )
    dp.include_router(setup_group_router(settings, users, ai, knowledge, catalog))
    dp.include_router(
        setup_chat_router(
            settings, users, ai, intents, knowledge, catalog, metrics, access=access
        )
    )

    active = await registry.get_active()
    log.info(
        "Starting long polling (env_model=%s env_base=%s active_agent=%s)",
        settings.ai_model,
        settings.ai_base_url,
        active.name if active else "(none)",
    )
    if settings.nightly_enabled:
        base, token, _inbound_ids = await bot_settings.effective_panel(settings)
        if not base or not token:
            log.error(
                "Nightly job enabled but panel settings are incomplete: PANEL_BASE_URL/PANEL_API_TOKEN"
            )
        else:
            nightly_task = asyncio.create_task(
                run_nightly_subscription_job(settings, bot, bot_settings),
                name="nightly-subscription-job",
            )
            chat_id = await bot_settings.effective_nightly_chat_id(settings)
            times = await bot_settings.effective_nightly_times(settings)
            log.info(
                "Nightly subscription job enabled for Iran time %s -> %s",
                times,
                chat_id,
            )
    if settings.social_news_enabled:
        social_news_task = asyncio.create_task(
            run_social_news_job(settings, bot, bot_settings),
            name="social-news-job",
        )
        social_chat = await bot_settings.effective_social_chat_id(settings)
        social_times = await bot_settings.effective_social_times(settings)
        log.info(
            "Social news job enabled (times=%s) -> %s",
            social_times,
            social_chat,
        )
    if settings.convo_analysis_enabled:
        convo_analysis_task = asyncio.create_task(
            run_conversation_analysis_job(settings, bot, bot_settings),
            name="conversation-analysis-job",
        )
        convo_chat = await bot_settings.effective_test_chat_id(settings)
        convo_times = await bot_settings.effective_test_times(settings)
        log.info(
            "Conversation analysis job enabled (times=%s) -> %s",
            convo_times,
            convo_chat,
        )
    heartbeat_task = asyncio.create_task(_heartbeat_loop(), name="safety-heartbeat")
    health_task = asyncio.create_task(
        run_health_report_job(settings, bot, bot_settings),
        name="health-report-job",
    )
    try:
        # Drop pending updates so restart does not replay a backlog
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if heartbeat_task:
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task
        if health_task:
            health_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await health_task
        if nightly_task:
            nightly_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await nightly_task
        if social_news_task:
            social_news_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await social_news_task
        if convo_analysis_task:
            convo_analysis_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await convo_analysis_task
        await ai.close()
        await bot.session.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
