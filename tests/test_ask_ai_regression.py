from src.ai.persona import excerpt_teaching_for_query, looks_like_prompt_dump
from src.ai.safety import ResponseBudget, is_transient_ai_error, prepare_user_reply
from src.knowledge.ai_memory import append_catalog_training, replace_catalog_training
from src.knowledge.catalog_index import wants_send_media


def test_prompt_dump_never_user_facing() -> None:
    raw = "### Operator AI memory for product_id=x ONLY\n<!-- BEGIN CATALOG -->\nnever invent steps"
    assert looks_like_prompt_dump(raw)
    assert prepare_user_reply(raw) == ""


def test_excerpt_shorter_than_full() -> None:
    teach = "1. AAA\n" + ("الف " * 80) + "\n\n2. اسکریپت CLI\n" + ("ب " * 40)
    out = excerpt_teaching_for_query(teach, "اسکریپت چه جوری کار میکنه؟", limit=200)
    assert out
    assert "<!--" not in out
    assert len(out) <= 200


def test_media_followup_hint() -> None:
    assert wants_send_media("عکسش را بفرست") is True
    assert wants_send_media("اسکریپت چه جوری کار میکنه؟") is False


def test_validate_media_same_product_and_ref(tmp_path) -> None:
    from src.knowledge.response_bundle import MediaRef, existing_media_paths, validate_media_for_response

    img = tmp_path / "script.png"
    img.write_bytes(b"x")
    ok = MediaRef(
        path=str(img),
        product_id="project-agent-hub",
        unit_id="media:project-agent-hub:script",
        feature_ids=["script_cli"],
        score=14.0,
    )
    weak = MediaRef(
        path=str(img),
        product_id="project-agent-hub",
        unit_id="media:project-agent-hub:script",
        score=3.0,
    )
    bad = MediaRef(
        path=str(img),
        product_id="vpn-installer",
        unit_id="media:vpn-installer:x",
        score=99.0,
    )
    assert validate_media_for_response(
        ok,
        product_id="project-agent-hub",
        knowledge_refs=["feature:project-agent-hub:script_cli"],
        project_root=tmp_path,
    )
    # Media unit ids in knowledge_refs alone must not auto-pass low scores.
    assert not validate_media_for_response(
        weak,
        product_id="project-agent-hub",
        knowledge_refs=["media:project-agent-hub:script"],
        project_root=tmp_path,
    )
    assert not validate_media_for_response(
        bad,
        product_id="project-agent-hub",
        knowledge_refs=["feature:project-agent-hub:script_cli"],
        project_root=tmp_path,
    )
    paths = existing_media_paths(
        [ok, bad],
        product_id="project-agent-hub",
        knowledge_refs=["feature:project-agent-hub:script_cli"],
        project_root=tmp_path,
    )
    assert paths == [img]


def test_ambiguous_backup_no_media() -> None:
    from pathlib import Path

    from src.knowledge.catalog_rag import retrieve_catalog_context
    from src.knowledge.product_catalogs import load_product_catalogs

    root = Path(__file__).resolve().parents[1]
    load_product_catalogs(root / "knowledge")
    r = retrieve_catalog_context(
        "برنامه سیستم backup هم داره؟",
        lang="fa",
        project_root=root,
        product_id="vpn-installer",
    )
    assert r.needs_clarification is True
    assert r.attach_media is False
    assert r.media_paths == []
    assert r.clarifying_question


def test_append_and_replace(tmp_path) -> None:
    root = tmp_path / "knowledge"
    pid = "demo-prod"
    cat = root / "product_catalogs"
    cat.mkdir(parents=True)
    (cat / f"{pid}.json").write_text(
        '{"product_id":"%s","enabled":true,"title":{"fa":"د"},"ai_training_text":"OLD"}'
        % pid,
        encoding="utf-8",
    )
    (root / "product_guides").mkdir(parents=True)
    assert append_catalog_training(root, pid, "NEW") == "OLD\n\nNEW"
    assert replace_catalog_training(root, pid, "ONLY") == "ONLY"


def test_budget_skips_retry() -> None:
    budget = ResponseBudget(10)
    budget.started -= 9
    assert budget.can_retry(14) is False
    assert is_transient_ai_error(TimeoutError("timed out")) is True
    assert is_transient_ai_error(RuntimeError("invalid api key")) is False
