# -*- coding: utf-8 -*-
"""Regenerate FA/RU/ZH FAQ with ID-aligned question translations."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "_faq_en_parsed.json").read_text(encoding="utf-8"))

# Complete question translations — must match EN Q IDs exactly.
Q = {
"Q001": {"fa": "نصب‌کننده Black Fox VPN چیست؟", "ru": "Что такое Black Fox VPN Installer?", "zh": "Black Fox VPN Installer 是什么？"},
"Q002": {"fa": "آیا Black Fox فورک رابط کاربری پنل 3X-UI است؟", "ru": "Black Fox — это форк UI панели 3X-UI?", "zh": "Black Fox 是 3X-UI 面板界面的分支吗？"},
"Q003": {"fa": "محصول از چه پلتفرم‌هایی پشتیبانی می‌کند؟", "ru": "Какие платформы поддерживает продукт?", "zh": "产品支持哪些平台？"},
"Q004": {"fa": "Installer رسمی را از کجا دانلود کنم؟", "ru": "Где скачать официальный Installer?", "zh": "官方 Installer 从哪里下载？"},
"Q005": {"fa": "تب‌های اصلی برنامه کدام‌اند؟", "ru": "Какие основные вкладки в приложении?", "zh": "应用有哪些主标签页？"},
"Q006": {"fa": "تب View برای چیست؟", "ru": "Для чего вкладка View?", "zh": "View 标签页有什么用？"},
"Q007": {"fa": "حالت Basic چیست؟", "ru": "Что такое режим Basic?", "zh": "什么是 Basic 模式？"},
"Q008": {"fa": "حالت Pro چیست؟", "ru": "Что такое режим Pro?", "zh": "什么是 Pro 模式？"},
"Q009": {"fa": "AI Assistant Pro چیست؟", "ru": "Что такое AI Assistant Pro?", "zh": "什么是 AI Assistant Pro？"},
"Q010": {"fa": "بعد از فعال‌سازی می‌توانم حالت را عوض کنم؟", "ru": "Можно ли сменить режим после активации?", "zh": "激活后还能切换模式吗？"},
"Q011": {"fa": "کدام عملیات در Basic رایگان است؟", "ru": "Какие операции бесплатны в Basic?", "zh": "Basic 里哪些操作免费？"},
"Q012": {"fa": "آیا در Basic سرور Central باید در کشورهای خاصی باشد؟", "ru": "В Basic Central должен быть в определённых странах?", "zh": "Basic 的 Central 必须位于特定国家吗？"},
"Q013": {"fa": "در Basic چند Exit Server می‌توانم داشته باشم؟", "ru": "Сколько Exit Server можно в Basic?", "zh": "Basic 最多可用多少 Exit Server？"},
"Q014": {"fa": "آیا در Pro تعداد Exit نامحدود است؟", "ru": "Неограничены ли Exit в Pro?", "zh": "Pro 的 Exit 是无限的吗？"},
"Q015": {"fa": "Full Deploy چیست؟", "ru": "Что такое Full Deploy?", "zh": "什么是 Full Deploy？"},
"Q016": {"fa": "قبل از Full Deploy چه باید کرد؟", "ru": "Что сделать перед Full Deploy?", "zh": "Full Deploy 之前要做什么？"},
"Q017": {"fa": "Connect SSH چیست؟", "ru": "Что такое Connect SSH?", "zh": "什么是 Connect SSH？"},
"Q018": {"fa": "برنامه چه اطلاعات SSH را می‌پذیرد؟", "ru": "Какие SSH-данные принимает приложение?", "zh": "应用接受哪些 SSH 凭据？"},
"Q019": {"fa": "Panel Login Info چیست؟", "ru": "Что такое Panel Login Info?", "zh": "什么是 Panel Login Info？"},
"Q020": {"fa": "Configure Panel چیست؟", "ru": "Что такое Configure Panel?", "zh": "什么是 Configure Panel？"},
"Q021": {"fa": "Test Client / WireGuard چیست؟", "ru": "Что такое Test Client / WireGuard?", "zh": "什么是 Test Client / WireGuard？"},
"Q022": {"fa": "Add Exit Server چیست؟", "ru": "Что такое Add Exit Server?", "zh": "什么是 Add Exit Server？"},
"Q023": {"fa": "Add Tunnel Server چیست؟", "ru": "Что такое Add Tunnel Server?", "zh": "什么是 Add Tunnel Server？"},
"Q024": {"fa": "Add Node چیست؟", "ru": "Что такое Add Node?", "zh": "什么是 Add Node？"},
"Q025": {"fa": "تفاوت Exit و Node چیست؟", "ru": "Чем Exit отличается от Node?", "zh": "Exit 和 Node 有什么区别？"},
"Q026": {"fa": "Add Domain چیست؟", "ru": "Что такое Add Domain?", "zh": "什么是 Add Domain？"},
"Q027": {"fa": "Configure CDN چیست؟", "ru": "Что такое Configure CDN?", "zh": "什么是 Configure CDN？"},
"Q028": {"fa": "Add Subscription چیست؟", "ru": "Что такое Add Subscription?", "zh": "什么是 Add Subscription？"},
"Q029": {"fa": "Proxy Settings چیست؟", "ru": "Что такое Proxy Settings?", "zh": "什么是 Proxy Settings？"},
"Q030": {"fa": "چه زمانی به Proxy نیاز دارم؟", "ru": "Когда нужен Proxy?", "zh": "什么时候需要 Proxy？"},
"Q031": {"fa": "چگونه License را فعال کنم؟", "ru": "Как активировать License?", "zh": "如何激活 License？"},
"Q032": {"fa": "کد claim چیست؟", "ru": "Что такое claim-код?", "zh": "什么是 claim 码？"},
"Q033": {"fa": "کد وابسته به دستگاه (machine-bound) چیست؟", "ru": "Что такое machine-bound код?", "zh": "什么是设备绑定码？"},
"Q034": {"fa": "Reactivation چیست؟", "ru": "Что такое Reactivation?", "zh": "什么是 Reactivation？"},
"Q035": {"fa": "Device ID / License ID چیست؟", "ru": "Что такое Device ID / License ID?", "zh": "什么是 Device ID / License ID？"},
"Q036": {"fa": "چرا My Code هنوز موجود نیست؟", "ru": "Почему My Code ещё недоступен?", "zh": "为什么 My Code 还不可用？"},
"Q037": {"fa": "پرداخت روی چه شبکه‌ای است؟", "ru": "Какая платёжная сеть используется?", "zh": "使用什么支付网络？"},
"Q038": {"fa": "قیمت Basic چقدر است؟", "ru": "Сколько стоит Basic?", "zh": "Basic 多少钱？"},
"Q039": {"fa": "قیمت Pro چقدر است؟", "ru": "Сколько стоит Pro?", "zh": "Pro 多少钱？"},
"Q040": {"fa": "قیمت AI Assistant Pro چقدر است؟", "ru": "Сколько стоит AI Assistant Pro?", "zh": "AI Assistant Pro 多少钱？"},
"Q041": {"fa": "شارژ سهمیه AI با BFXQ چیست؟", "ru": "Что такое пополнение AI quota (BFXQ)?", "zh": "AI quota 充值（BFXQ）是什么？"},
"Q042": {"fa": "مدت License چقدر است؟", "ru": "На сколько выдаётся License?", "zh": "License 有效期多久？"},
"Q043": {"fa": "آیا یک خرید چند دستگاه را پوشش می‌دهد؟", "ru": "Можно ли одной покупкой закрыть несколько устройств?", "zh": "一次购买能否覆盖多台设备？"},
"Q044": {"fa": "اگر TX HASH را دوباره استفاده کنم چه می‌شود؟", "ru": "Что будет, если повторно использовать TX HASH?", "zh": "重复使用 TX HASH 会怎样？"},
"Q045": {"fa": "معنی «claim already bound» چیست؟", "ru": "Что значит «claim already bound»?", "zh": "“claim already bound” 是什么意思？"},
"Q046": {"fa": "کد فعال‌سازی نامعتبر است — چه کار کنم؟", "ru": "Invalid activation code — что делать?", "zh": "激活码无效——怎么办？"},
"Q047": {"fa": "TX پیدا نشد / در انتظار / مبلغ اشتباه؟", "ru": "TX not found / pending / wrong amount?", "zh": "TX 未找到 / 待确认 / 金额错误？"},
"Q048": {"fa": "پیام «ابتدا از تب Registration فعال کنید» یعنی چه؟", "ru": "Что значит «Please activate via Registration tab first»?", "zh": "“Please activate via Registration tab first” 是什么意思？"},
"Q049": {"fa": "پیام «این قابلیت نیاز به فعال‌سازی Pro دارد» یعنی چه؟", "ru": "Что значит «This feature requires Pro activation»?", "zh": "“This feature requires Pro activation” 是什么意思？"},
"Q050": {"fa": "اگر License منقضی شود هنوز می‌توانم از برنامه استفاده کنم؟", "ru": "License истёк — можно ли ещё пользоваться приложением?", "zh": "License 过期后还能用应用吗？"},
}

# Continue Q051-Q200 in compact form
MORE = r'''
Q051|قیمت زنده سایت کجا تعریف می‌شود؟|Где задаются live-цены сайта?|网站实时价格在哪里定义？
Q052|Initial Server Setup / Central Server Setup چیست؟|Что такое Initial / Central Server Setup?|什么是 Initial / Central Server Setup？
Q053|چرا هنگام ذخیره نمی‌توانم Host/IP را عوض کنم؟|Почему нельзя менять Host/IP при сохранении?|保存时为什么不能改 Host/IP？
Q054|Full Deploy تمام شد ولی پنل باز نمی‌شود — بعد چه کنم؟|Full Deploy завершён, панель недоступна — что дальше?|Full Deploy 完成但面板打不开——下一步？
Q055|Install WireGuard / Install 3X-UI جداگانه چیست؟|Что такое отдельная установка WireGuard / 3X-UI?|单独的 Install WireGuard / Install 3X-UI 是什么？
Q056|Diagnostic Center چیست؟|Что такое Diagnostic Center?|什么是 Diagnostic Center？
Q057|Link Test چیست؟|Что такое Link Test?|什么是 Link Test？
Q058|GRE fallback چیست؟|Что такое GRE fallback?|什么是 GRE fallback？
Q059|Reverse Tunnel (Stealth-WSS) چیست؟|Что такое Reverse Tunnel (Stealth-WSS)?|什么是 Reverse Tunnel (Stealth-WSS)？
Q060|Mesh / Link Monitor Agent چیست؟|Что такое Mesh / Link Monitor Agent?|什么是 Mesh / Link Monitor Agent？
Q061|آیا ایجنت‌های Mesh نیاز دارند برنامه Windows باز باشد؟|Нужно ли держать Windows-приложение открытым для mesh-агентов?|Mesh 代理是否需要 Windows 应用一直打开？
Q062|ایجنت Mesh غایب/متوقف است — چه کنم؟|Mesh-агенты missing/stopped — что делать?|Mesh 代理显示 missing/stopped——怎么办？
Q063|Mirza Bot چیست؟|Что такое Mirza Bot?|什么是 Mirza Bot？
Q064|می‌توانم Mirza را به سرور دیگری منتقل کنم؟|Можно ли перенести Mirza на другой сервер?|可以把 Mirza 迁到另一台服务器吗？
Q065|برنامه از چه زبان‌هایی پشتیبانی می‌کند؟|Какие языки поддерживает приложение?|应用支持哪些语言？
Q066|تفاوت Setup.exe و Portable exe چیست؟|Чем Setup.exe отличается от Portable exe?|Setup.exe 与 Portable exe 有何区别？
Q067|Delete History چه می‌کند؟|Что делает Delete History?|Delete History 做什么？
Q068|Delete Exit Servers & Node چه می‌کند؟|Что делает Delete Exit Servers & Node?|Delete Exit Servers & Node 做什么？
Q069|Delete Tunnel Servers چه می‌کند؟|Что делает Delete Tunnel Servers?|Delete Tunnel Servers 做什么？
Q070|DELETE — Reset All Servers چه می‌کند؟|Что делает DELETE — Reset All Servers?|DELETE — Reset All Servers 做什么？
Q071|Factory Reset Server چیست؟|Что такое Factory Reset Server?|什么是 Factory Reset Server？
Q072|آیا Delete History لایسنس را پاک می‌کند؟|Удаляет ли Delete History лицензию?|Delete History 会删除 License 吗？
Q073|به‌روزرسانی برنامه چگونه کار می‌کند؟|Как работают обновления приложения?|应用 Update 如何工作？
Q074|Check Update 3X-UI چیست؟|Что такое Check Update 3X-UI?|什么是 Check Update 3X-UI？
Q075|تفاوت Android و Windows چیست؟|Чем Android отличается от Windows?|Android 与 Windows 有何不同？
Q076|چگونه با پشتیبانی تماس بگیرم؟|Как связаться с поддержкой?|如何联系支持？
Q077|در پیام پشتیبانی چه چیزهایی بفرستم؟|Что указать в сообщении поддержке?|给支持发消息应包含什么？
Q078|BlackFox MCP چیست؟|Что такое BlackFox MCP?|什么是 BlackFox MCP？
Q079|چت AI می‌گوید فعال‌سازی AI Assistant Pro لازم است|AI пишет, что нужна активация AI Assistant Pro|AI 提示需要激活 AI Assistant Pro
Q080|سهمیه AI تمام شده — چه کنم؟|AI quota исчерпан — что делать?|AI quota 用尽——怎么办？
Q081|محدودیت پیوست در چت AI چیست؟|Какие лимиты вложений в AI-чате?|AI 聊天附件有哪些限制？
Q082|آیا AI بدون تأیید عملیات را اجرا می‌کند؟|AI выполняет операции без подтверждения?|AI 会在未确认时执行操作吗？
Q083|AI گفت عملیات شروع شد — چقدر صبر کنم؟|AI сказал, что операция началась — сколько ждать?|AI 说操作已开始——要等多久？
Q084|آیا AI می‌تواند outbound سفارشی v2ray اضافه کند؟|Может ли AI добавить кастомные v2ray outbounds?|AI 能否添加自定义 v2ray outbound？
Q085|راهنمای پیش‌فرض پورت inbound در Configure Panel چیست؟|Какие inbound-порты по умолчанию в Configure Panel?|Configure Panel 默认 inbound 端口指引是什么？
Q086|اعتبارنامه پنل Central پیدا نشد؟|Не найдены credentials центральной панели?|找不到 Central 面板凭据？
Q087|SSH host key عوض شده — امن است؟|SSH host key изменился — это безопасно?|SSH host key 变更——安全吗？
Q088|احراز هویت SSH شکست خورد (کلید و رمز)؟|SSH authentication failed (ключ и пароль)?|SSH 认证失败（密钥与密码）？
Q089|رمز لینوکس هنگام SSH منقضی شده؟|Linux password expired во время SSH?|SSH 时 Linux 密码过期？
Q090|علل SSH timeout چیست؟|Каковы причины SSH timeout?|SSH timeout 的原因？
Q091|نمای topology چیست؟|Что такое topology view?|什么是 topology 视图？
Q092|Add OutBounds چیست؟|Что такое Add OutBounds?|什么是 Add OutBounds？
Q093|آیا Basic همه‌جا می‌تواند از Cloudflare CDN استفاده کند؟|Может ли Basic везде использовать Cloudflare CDN?|Basic 能否到处使用 Cloudflare CDN？
Q094|کدام ارائه‌دهندگان DNS در برنامه پشتیبانی می‌شوند؟|Какие DNS-провайдеры поддерживаются в приложении?|应用内支持哪些 DNS 提供商？
Q095|تفاوت DNS وبهوک بات و دامنه پنل؟|Bot webhook DNS vs домен панели?|Bot webhook DNS 与面板域名有何不同？
Q096|Diagnose & Repair چیست؟|Что такое Diagnose & Repair?|什么是 Diagnose & Repair？
Q097|اسپینر busy نوار وضعیت یعنی چه؟|Что значит busy-спиннер в status bar?|状态栏 busy 转圈是什么意思？
Q098|می‌توانم عملیات در حال اجرای terminal را متوقف کنم؟|Можно ли остановить текущую terminal-операцию?|可以停止正在运行的 terminal 操作吗？
Q099|فایل‌های محلی نصب‌شده کجا ذخیره می‌شوند؟|Где хранятся локальные файлы (installed)?|已安装模式下本地文件存在哪里？
Q100|چگونه Device ID / wallet / TX / کد فعال‌سازی را کپی کنم؟|Как скопировать Device ID / wallet / TX / код?|如何复制 Device ID / wallet / TX / 激活码？
Q101|مسیر فعال‌سازی Offline / record-offline چیست؟|Что такое offline / record-offline активация?|离线 / record-offline 激活路径是什么？
Q102|معنی پیشوندهای BFXB / BFXP / BFXA / BFXQ؟|Что значат префиксы BFXB / BFXP / BFXA / BFXQ?|BFXB / BFXP / BFXA / BFXQ 前缀含义？
Q103|آیا AI Pro امکانات دستی Pro را هم دارد؟|Включает ли AI Pro ручные функции Pro?|AI Pro 是否包含 Pro 的手动功能？
Q104|آیا باز کردن Pro، AI Assistant Pro را هم می‌دهد؟|Даёт ли unlock Pro доступ к AI Assistant Pro?|解锁 Pro 能获得 AI Assistant Pro 吗？
Q105|تفاوت Activation سایت و تأیید TX داخل برنامه؟|Website Activation vs проверка TX в приложении?|网站 Activation 与应用内 TX 验证有何不同？
Q106|PAS Generator چیست؟|Что такое PAS Generator?|什么是 PAS Generator？
Q107|برای Add Exit چه پیش‌نیازهایی لازم است؟|Какие prerequisites для Add Exit?|Add Exit 需要哪些前提？
Q108|چرا قبل از بعضی حذف‌های Tunnel باید Exitها پاک شوند؟|Почему exits нужно удалить до некоторых tunnel deletes?|为何部分 Tunnel 删除前必须先删 Exit？
Q109|شماره chain در Pro چیست؟|Что такое chain number в Pro?|Pro 中的 chain number 是什么？
Q110|نقش Microsocks روی Exitها؟|Роль Microsocks на exits?|Exit 上 Microsocks 的作用？
Q111|نکتهٔ import کلاینت WireGuard؟|Совет по импорту WireGuard-клиента?|WireGuard 客户端导入提示？
Q112|ارجاع پورت پیش‌فرض پنل؟|Ссылки на порт панели по умолчанию?|面板默认端口相关说明？
Q113|رابطه External Proxy و proxy پنل؟|External Proxy и proxy панели?|External Proxy 与面板 proxy 的关系？
Q114|آموزش Registration — پیدا کردن TX HASH؟|Туториал Registration — как найти TX HASH?|Registration 教程——如何找 TX HASH？
Q115|کپی System info در Windows؟|Копирование System info на Windows?|Windows 上如何复制 System info？
Q116|اگر قیمت هاب دریافت نشود چه می‌شود؟|Что если не удаётся получить цены с хаба?|无法获取 Hub 价格时怎么办？
Q117|آیا blackfoxupdate.ir مرتبط است؟|Связан ли blackfoxupdate.ir?|blackfoxupdate.ir 相关吗？
Q118|دیالوگ Limited Access چیست؟|Что такое диалог Limited Access?|什么是 Limited Access 对话框？
Q119|می‌توانم Full Deploy را از چت AI اجرا کنم؟|Можно ли запустить Full Deploy из AI-чата?|能否从 AI 聊天执行 Full Deploy？
Q120|آیا AI چت قبلی را ادامه می‌دهد؟|AI продолжает предыдущий чат?|AI 会恢复之前的聊天吗？
Q121|Move Central چیست؟|Что такое Move Central?|什么是 Move Central？
Q122|تفاوت Subscription URL و لینک VLESS؟|Subscription URL vs ссылка VLESS?|Subscription URL 与 VLESS 链接有何不同？
Q123|چرا بعد از Deploy توپولوژی خالی است؟|Почему topology пустая после deploy?|部署后 topology 为什么是空的？
Q124|ابزارهای ایجنت Mesh از کجا دانلود می‌شوند؟|Откуда качаются agent tools при mesh install?|Mesh 安装时 agent 工具从哪里下载？
Q125|Other CDN چیست؟|Что такое Other CDN?|什么是 Other CDN？
Q126|Hysteria / پورت‌های خاص؟|Hysteria / особые порты?|Hysteria / 特殊端口？
Q127|می‌توانم کاربر SSH غیر root استفاده کنم؟|Можно ли SSH не от root?|可以使用非 root 的 SSH 用户吗？
Q128|رمز یا کلید — کدام ترجیح دارد؟|Пароль или ключ — что предпочтительнее?|密码与密钥更推荐哪个？
Q129|معنی server draft saved چیست؟|Что значит server draft saved?|server draft saved 是什么意思？
Q130|عملیات در جریان است — باز هم ببندم؟|Операция идёт — всё равно закрыть?|操作进行中——仍要关闭吗？
Q131|بعد از نصب چگونه زبان برنامه را عوض کنم؟|Как сменить язык после установки?|安装后如何更改应用语言？
Q132|تب Contact چه کانال‌هایی نشان می‌دهد؟|Какие каналы показывает вкладка Contact?|Contact 标签显示哪些渠道？
Q133|آیا ایمیل مسیر اصلی پشتیبانی است؟|Email — основной канал поддержки?|邮件是主要支持渠道吗？
Q134|«Update BlackFox & Wallet Address» چیست؟|Что такое «Update BlackFox & Wallet Address»?|“Update BlackFox & Wallet Address” 是什么？
Q135|حداقل نسخه اجباری برنامه را قفل کرده — چه کنم؟|Force min version блокирует приложение — что делать?|强制最低版本挡住应用——怎么办？
Q136|خطای timeout / شبکه سرویس AI؟|Таймаут / сетевая ошибка AI-сервиса?|AI 服务超时 / 网络错误？
Q137|AI موقتاً در دسترس نیست؟|AI временно недоступен?|AI 暂时不可用？
Q138|برای License سهمیه پیدا نشد؟|Quota not found for license?|License 找不到 quota？
Q139|آیا Delete All رمزهای SSH را از دیسک پاک می‌کند؟|Delete All удаляет SSH-пароли с диска?|Delete All 会从磁盘删除 SSH 密码吗？
Q140|آیا Factory Reset دادهٔ پنل را نگه می‌دارد؟|Factory Reset сохраняет данные панели?|Factory Reset 会保留面板数据吗？
Q141|چگونه failover مش را سریع چک کنم؟|Как быстро проверить mesh failover?|如何快速验证 mesh 故障切换？
Q142|دامنهٔ «Install always-on Link Monitor Agents» چیست؟|Каков scope «Install always-on Link Monitor Agents»?|“Install always-on Link Monitor Agents” 范围是什么？
Q143|می‌توانم برنامه را فقط به‌عنوان مدیر بوکمارک پنل استفاده کنم؟|Можно ли использовать приложение только как менеджер закладок панели?|能否只把应用当面板书签管理器用？
Q144|وضعیت مشترک بین Basic / Pro / AI Pro؟|Общее состояние Basic / Pro / AI Pro?|Basic / Pro / AI Pro 是否共享状态？
Q145|تفاوت Check System و Diagnose & Repair؟|Check System vs Diagnose & Repair?|Check System 与 Diagnose & Repair 有何不同？
Q146|بعد از افزودن Exit تست کلاینت شکست خورد؟|Client test failed после add exit?|添加 Exit 后客户端测试失败？
Q147|Add Node در ورود به پنل Central شکست می‌خورد؟|Add Node fails central login?|Add Node 登录 Central 失败？
Q148|ریسک از دست رفتن داده در حالت Portable؟|Риск потери данных в portable mode?|Portable 模式有数据丢失风险吗？
Q149|صفحات چندزبانه سایت چه ربطی به برنامه دارند؟|Как мультиязычные страницы сайта связаны с приложением?|网站多语言页面与应用有何关系？
Q150|زیرعنوان «Multi-Location VPN Manager» یعنی چه؟|Что значит подзаголовок «Multi-Location VPN Manager»?|副标题 “Multi-Location VPN Manager” 是什么意思？
Q151|آیا در Factory Reset رمزها ذخیره می‌شوند؟|Сохраняются ли пароли при Factory Reset?|Factory Reset 时会保存密码吗？
Q152|معنی «SSH connected but probe output unexpected»؟|Что значит «SSH connected but probe output unexpected»?|“SSH connected but probe output unexpected” 是什么意思？
Q153|می‌توانم اسکرین‌شات پنل سرور را به چت AI بچسبانم؟|Можно ли прикреплять скриншоты панелей к AI-чату?|能否把服务器面板截图附加到 AI 聊天？
Q154|AI اشتباه Exit را به‌جای Node تشخیص داد؟|AI перепутал Exit и Node?|AI 把 Exit 和 Node 认错了？
Q155|وضعیت Apply Actions در چت AI چیست؟|Что значит статус Apply Actions в AI-чате?|AI 聊天中的 Apply Actions 状态是什么？
Q156|آیا مبلغ USDT همیشه ۱۹/۳۳/۴۰ است؟|Сумма USDT всегда 19/33/40?|USDT 金额永远是 19/33/40 吗？
Q157|اگر Reactivation بگوید tier mismatch؟|Reactivation пишет tier mismatch?|Reactivation 提示 tier mismatch 怎么办？
Q158|بعد از claim می‌توانم کدها را از TX قدیمی بازیابی کنم؟|Можно ли восстановить коды со старого TX после claim?|claim 之后还能从旧 TX 找回代码吗？
Q159|مسیر پیشنهادی اولین اجرا برای کاربر جدید؟|Рекомендуемый first-run путь для новичка?|新用户推荐的首次运行路径？
Q160|پشتیبان برای متن دقیق UI به کجا نگاه کند؟|Куда смотреть агенту поддержки за точными UI-строками?|客服应到哪里核对精确 UI 文案？
Q161|تعویض حالت View سرورها را پاک می‌کند؟|Смена режима View стирает серверы?|切换 View 模式会清空服务器吗？
Q162|تفاوت Configure Panel و Full Deploy؟|Configure Panel vs Full Deploy?|Configure Panel 与 Full Deploy 有何不同？
Q163|چند Node می‌توانم اضافه کنم؟|Сколько Node можно добавить?|最多可以添加多少 Node？
Q164|Full Deploy / Add Node از چه منابع XUI استفاده می‌کنند؟|Какие XUI-источники у Full Deploy / Add Node?|Full Deploy / Add Node 可用哪些 XUI 来源？
Q165|Delete History چه چیزهایی را نگه می‌دارد؟|Что сохраняет Delete History?|Delete History 会保留什么？
Q166|DELETE — Reset All Servers چه می‌کند؟|Что делает DELETE — Reset All Servers?|DELETE — Reset All Servers 做什么？
Q167|می‌توانم فقط hopهای Tunnel را حذف کنم؟|Можно ли удалить только tunnel hops?|可以只删除 tunnel hops 吗？
Q168|چه پروفایل‌های Proxy وجود دارد؟|Какие профили Proxy есть?|有哪些 Proxy 配置？
Q169|بعد از Deploy آدرس پنل را کجا ببینم؟|Где смотреть URL панели после deploy?|部署后在哪里查看面板 URL？
Q170|Test Client / WG برای چیست؟|Для чего Test Client / WG?|Test Client / WG 做什么用？
Q171|Add Domain چیست؟|Что такое Add Domain?|什么是 Add Domain？
Q172|کدام ارائه‌دهندگان CDN در UI هستند؟|Какие CDN-провайдеры в UI?|UI 里有哪些 CDN 提供商？
Q173|Mesh Servers چیست؟|Что такое Mesh Servers?|什么是 Mesh Servers？
Q174|Add Telegram Bot (Mirza) چیست؟|Что такое Add Telegram Bot (Mirza)?|什么是 Add Telegram Bot (Mirza)？
Q175|Move Central Server چیست؟|Что такое Move Central Server?|什么是 Move Central Server？
Q176|BlackFox MCP در Tasks هوش مصنوعی چیست؟|Что такое BlackFox MCP в AI tasks?|AI 任务中的 BlackFox MCP 是什么？
Q177|تفاوت Diagnose & Repair و Check System؟|Diagnose & Repair vs Check System?|Diagnose & Repair 与 Check System 有何不同？
Q178|Link Test (AI) چیست؟|Что такое Link Test (AI)?|什么是 Link Test（AI）？
Q179|Add OutBounds (AI) چیست؟|Что такое Add OutBounds (AI)?|什么是 Add OutBounds（AI）？
Q180|آیا Factory Reset رمزی که تایپ می‌کنم را ذخیره می‌کند؟|Factory Reset сохраняет введённый пароль?|Factory Reset 会保存我输入的密码吗？
Q181|زبان برنامه کجا عوض می‌شود؟|Где меняется язык?|在哪里更改语言？
Q182|مدیر بسته 3X-UI در Settings چیست؟|Что такое менеджер пакетов 3X-UI в Settings?|Settings 里的 3X-UI 包管理器是什么？
Q183|چه چیزی باعث force update می‌شود؟|Что вызывает force update?|什么会触发强制更新？
Q184|PAS Generator چیست؟|Что такое PAS Generator?|什么是 PAS Generator？
Q185|Config Builder چیست؟|Что такое Config Builder?|什么是 Config Builder？
Q186|کشورهای رایگان Central در Basic کدام‌اند؟|Какие бесплатные страны Central в Basic?|Basic 免费 Central 国家有哪些？
Q187|آیا License پرو چت AI را باز می‌کند؟|Открывает ли Pro license AI-чат?|Pro License 能打开 AI 聊天吗？
Q188|چه پیشوندهای کدی وجود دارد؟|Какие префиксы кодов есть?|有哪些代码前缀？
Q189|My Code در Registration چیست؟|Что такое My Code на Registration?|Registration 上的 My Code 是什么？
Q190|System ID / Device ID چیست؟|Что такое System ID / Device ID?|什么是 System ID / Device ID？
Q191|اگر ماه‌ها مشخص نباشد مدت پیش‌فرض License؟|Срок License по умолчанию, если месяцы не указаны?|未指定月数时默认 License 时长？
Q192|برنامه از چه هاب‌هایی استفاده می‌کند؟|Какие хабы использует приложение?|应用使用哪些 Hub？
Q193|راه‌های پشتیبانی از کانفیگ محصول؟|Контакты поддержки из product config?|产品配置中的支持联系方式？
Q194|املای GitHub عمومی عمدی است؟|Намеренное написание public GitHub?|公开 GitHub 拼写是故意的吗？
Q195|برای Full Deploy اندروید بهتر است یا Windows؟|Android или Windows для Full Deploy?|Full Deploy 用 Android 还是 Windows？
Q196|دو کپی Portable می‌توانند یک inventory را ایمن شریک شوند؟|Безопасно ли двум portable копиям делить inventory?|两个 Portable 副本能安全共享同一套库存吗？
Q197|AI هرگز چه چیزهایی را نباید اختراع کند؟|Что AI никогда не должен выдумывать?|AI 绝不应该编造什么？
Q198|اسکرین‌شات‌های آموزش کجا هستند؟|Где скриншоты для обучения?|教学截图在哪里？
Q199|چت‌بات برای Deploy گیرکرده چه ترتیبی پیشنهاد دهد؟|Как chatbot вести застрявший deploy?|聊天机器人应如何引导卡住的部署？
Q200|فایل اصلی ورود RAG کدام است؟|Какой единый RAG entry-файл?|唯一的 RAG 入口文件是什么？
'''

for line in MORE.strip().splitlines():
    if not line.strip():
        continue
    qid, fa, ru, zh = line.split("|", 3)
    Q[qid] = {"fa": fa, "ru": ru, "zh": zh}

assert len(Q) == 200, len(Q)

# High-quality native answers for key IDs (fact-checked against EN).
ANS = {
"Q001": {
 "fa": "Black Fox یک Installer ویندوزی است که با SSH روی VPS شما WireGuard و پنل 3X-UI (Sanaei) را برای زیرساخت VPN چندمکانه خودکار می‌کند؛ کلاینت مصرف‌کنندهٔ وب‌گردی نیست.",
 "ru": "Black Fox — Windows Installer, который по SSH автоматизирует WireGuard и панель 3X-UI (Sanaei) на вашем VPS для multi-location VPN. Это не потребительский VPN-клиент.",
 "zh": "Black Fox 是 Windows Installer，通过 SSH 在您的 VPS 上自动部署 WireGuard 与 3X-UI (Sanaei) Panel，用于多地域 VPN 基建，不是消费级 VPN 客户端。",
},
"Q005": {
 "fa": "تب‌ها: Operations، Check System، View، Settings، Registration، Contact. Add Domain و Mesh پوشش جدا هستند؛ تب سطح‌بالای Add وجود ندارد.",
 "ru": "Вкладки: Operations, Check System, View, Settings, Registration, Contact. Add Domain и Mesh — оверлеи; отдельной вкладки Add нет.",
 "zh": "标签页：Operations、Check System、View、Settings、Registration、Contact。Add Domain 与 Mesh 为叠加页；没有独立顶层 Add 标签。",
},
"Q011": {
 "fa": "بدون License در Basic فقط Setup Central، Connect SSH و Full Deploy رایگان‌اند.",
 "ru": "Без License в Basic бесплатны только Setup Central, Connect SSH и Full Deploy.",
 "zh": "Basic 无 License 时仅 Setup Central、Connect SSH、Full Deploy 免费。",
},
"Q014": {
 "fa": "خیر. سقف Exit برابر ۶ اسلات است (`MaxExitServers`).",
 "ru": "Нет. Лимит Exit — 6 слотов (`MaxExitServers`).",
 "zh": "不是。Exit 上限为 6 个槽位（`MaxExitServers`）。",
},
"Q015": {
 "fa": "Full Deploy نصب یک‌مرحله‌ای WireGuard و پنل 3X-UI روی سرور Central است.",
 "ru": "Full Deploy — одношаговая установка WireGuard и панели 3X-UI на Central.",
 "zh": "Full Deploy 是在 Central 上一键安装 WireGuard 与 3X-UI Panel。",
},
"Q020": {
 "fa": "Configure Panel مسیریابی inbound/outbound/SOCKS را برای Exit یا Node موجود تعمیر می‌کند؛ نصب پنل روی Central نیست.",
 "ru": "Configure Panel чинит inbound/outbound/SOCKS для существующего Exit/Node; это не установка панели на Central.",
 "zh": "Configure Panel 修复已有 Exit/Node 的 inbound/outbound/SOCKS，不是在 Central 安装面板。",
},
"Q031": {
 "fa": "تب Registration → Device ID را کپی کنید → کد/claim را وارد و Activate کنید (یا مسیر پرداخت TX در foxnext.net).",
 "ru": "Registration → скопируйте Device ID → вставьте код/claim и Activate (или TX-оплата на foxnext.net).",
 "zh": "打开 Registration → 复制 Device ID → 粘贴代码/claim 并 Activate（或走 foxnext.net 的 TX 支付流程）。",
},
"Q104": {
 "fa": "خیر. AI Assistant Pro جداست و به `BFXA` به‌علاوه quota نیاز دارد.",
 "ru": "Нет. AI Assistant Pro отдельно: нужен `BFXA` и quota.",
 "zh": "不能。AI Assistant Pro 需单独 `BFXA` 解锁并具备 quota。",
},
"Q187": {
 "fa": "خیر. چت AI فقط با فعال‌سازی AI Pro و سهمیه باز می‌شود.",
 "ru": "Нет. AI-чат открывается только с AI Pro unlock и quota.",
 "zh": "不能。只有 AI Pro 解锁且具备 quota 才能打开 AI 聊天。",
},
}

ERR = {
"fa": "خطاهای رایج: need activate/Pro، SSH fail، شکست Full Deploy، AI quota، Proxy، host key. وضعیت/terminal را ببینید؛ در صورت نیاز Device ID + اسکرین به @HiBlackFoxVpn.",
"ru": "Частые ошибки: need activate/Pro, SSH fail, Full Deploy fail, AI quota, Proxy, host key. Смотрите status/terminal; при необходимости Device ID + скрин в @HiBlackFoxVpn.",
"zh": "常见错误：need activate/Pro、SSH 失败、Full Deploy 失败、AI quota、Proxy、host key。查看 status/terminal；必要时将 Device ID + 截图发给 @HiBlackFoxVpn。",
}

HEADERS = {
"fa": """# Black Fox VPN — پرسش‌های متداول (فارسی)

> برای AI / ربات تلگرام / پشتیبانی. شناسهٔ Q با انگلیسی یکی است.
> دقت: حداکثر ۶ Exit؛ رایگان Basic = Setup Central + Connect SSH + Full Deploy؛ Pro ≠ AI Pro؛ تب‌ها = Operations, Check System, View, Settings, Registration, Contact.

""",
"ru": """# Black Fox VPN — FAQ (русский)

> Для AI / Telegram Bot / поддержки. ID вопросов совпадают с EN.
> Точность: макс. 6 Exit; бесплатно в Basic = Setup Central + Connect SSH + Full Deploy; Pro ≠ AI Pro; вкладки = Operations, Check System, View, Settings, Registration, Contact.

""",
"zh": """# Black Fox VPN — 常见问题（简体中文）

> 供 AI / Telegram Bot / 客服。问题编号与英文对齐。
> 准确性：Exit 最多 6；Basic 免费 = Setup Central + Connect SSH + Full Deploy；Pro ≠ AI Pro；标签 = Operations, Check System, View, Settings, Registration, Contact.

""",
}

LABELS = {
"fa": ("سؤال", "پاسخ", "راه‌حل قدم‌به‌قدم", "خطاهای احتمالی"),
"ru": ("Question", "Answer", "Step by step solution", "Possible errors"),
"zh": ("Question", "Answer", "Step by step solution", "Possible errors"),
}


def answer(lang: str, qid: str, en_a: str) -> str:
    if qid in ANS:
        return ANS[qid][lang]
    core = en_a.strip()
    if lang == "fa":
        return f"بر اساس رفتار فعلی Black Fox: {core} قیمت و نسخه را اختراع نکنید؛ UI را معیار بگیرید."
    if lang == "ru":
        return f"По текущему поведению Black Fox: {core} Не выдумывайте цены и версии; ориентируйтесь на UI."
    return f"根据当前 Black Fox 行为：{core} 不要编造价格或版本；以应用 UI 为准。"


def steps(lang: str, en_steps: str) -> str:
    lines = [re.sub(r"^\d+\.\s*", "", ln.strip()) for ln in en_steps.splitlines() if ln.strip()]
    out = [f"{i}. {ln}" for i, ln in enumerate(lines, 1)]
    if lang == "fa":
        out.append(f"{len(out)+1}. اگر حل نشد Device ID را به @HiBlackFoxVpn بفرستید.")
    elif lang == "ru":
        out.append(f"{len(out)+1}. Если не помогло — Device ID в @HiBlackFoxVpn.")
    else:
        out.append(f"{len(out)+1}. 若仍未解决，将 Device ID 发给 @HiBlackFoxVpn。")
    return "\n".join(out)


def render(lang: str) -> str:
    qL, aL, sL, eL = LABELS[lang]
    parts = [HEADERS[lang]]
    for item in DATA:
        qid = item["id"]
        parts.append(
            f"### {qid}\n"
            f"**{qL}:** {Q[qid][lang]}\n"
            f"**{aL}:** {answer(lang, qid, item['a'])}\n"
            f"**{sL}:**\n{steps(lang, item['steps'])}\n"
            f"**{eL}:** {ERR[lang]}\n"
        )
    return "\n".join(parts)


def main() -> None:
    paths = {
        "fa": ROOT / "Persian" / "FAQ_FA.md",
        "ru": ROOT / "Russian" / "FAQ_RU.md",
        "zh": ROOT / "Chinese" / "FAQ_ZH.md",
    }
    for lang, path in paths.items():
        text = render(lang)
        path.write_text(text, encoding="utf-8")
        n = len(re.findall(r"^### Q\d+", text, re.M))
        print(lang, n, path.stat().st_size)


if __name__ == "__main__":
    main()
