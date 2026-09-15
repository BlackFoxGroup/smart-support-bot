# Catalog feature teaching copy

Smart Support Bot product-hub feature buttons use a fixed writing structure.

## Required shape

Persian (`howto.fa`):

```text
هدف طراحی: …
عملکرد: …
```

English (`howto.en`):

```text
Design goal: …
Behavior: …
```

## Rules

1. Exactly two labeled blocks, in that order.
2. Each block: 1–2 short sentences.
3. Persian sentences start with a Persian word (RTL).
4. Prefer clear user wording; avoid internal paths unless needed.
5. Do not rename official product names.
6. Keep facts grounded in the product catalog / MD guides.

Code prefers `howto` over `summary` when answering a feature key (`feature_body`).
An Ask AI footer may be appended by the UI layer — do not duplicate it inside `howto`.

See also Cursor rule: `telegram-bot-feature-howto-writing.mdc`.
