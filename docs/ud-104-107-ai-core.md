# E12 AI core — UD-104 to UD-107

## Provider boundary

AI is provider-neutral behind `AiProvider`. Providers receive structured read-only requests and return data; they never receive repository, WordPress write or publish access.

A dedicated `hangar18_use_ai` capability gates future UI/runtime activation. It is explicit in Administrator/Designer/Editor role recipes and is not implicitly granted to domain-scoped Event/Gallery roles.

## UD-104 AI text assistant

Text assistance returns a `pending` proposal containing Before/After/Reason. Content is not changed by the assistant. `SuggestionGuard` requires explicit confirmation before producing an Apply operation and also emits the inverse Undo operation.

## UD-105 Prompt-to-layout

AI output is treated as an untrusted candidate page state. `PromptLayoutService` passes it through the normal `SchemaValidator`; preview/insert are allowed only when the complete candidate validates successfully.

## UD-106 AI design review

Design review starts from the deterministic Design Consistency analyzer and accepts AI suggestions only when they reference an existing element key and existing property. Suggestions remain pending until approval.

## UD-107 AI accessibility suggestions

Accessibility AI is restricted to suggestion text for concrete missing alt/label findings. Empty/unknown element/property suggestions are discarded. Suggestions may be accepted or rejected individually.

## Safety/compatibility

- AI output never writes directly.
- Every accepted proposal contains reversible Before/After data for undo/revision integration.
- Invalid layout output cannot preview/insert.
- Existing pages and Vehicle/Event/Gallery remain unchanged.
- No provider/API credentials are configured by this architecture slice.
