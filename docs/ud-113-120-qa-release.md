# E14 QA & Release — UD-113 to UD-120

## Status model

E14 separates **automated evidence** from **manual/live evidence**. CI success is necessary but does not make the final release/conversion ready by itself. `ReleaseReadiness` keeps `Ready=false` until every required manual item is explicitly recorded as passed.

## UD-113 Cross-browser matrix

### Automated engine matrix

| Engine | Represents | Automated core flows |
|---|---|---|
| Chromium | Chrome/Edge rendering/JS engine family | menu toggle/arrows/submenu/Escape, modal, form, reduced motion |
| Firefox | Firefox | same |
| WebKit | Safari/WebKit engine family | same |

Playwright runs the passive public runtimes against all three engines. This is not claimed as brand-identical evidence for desktop Chrome/Edge/Safari.

### Required manual brand evidence before final conversion

- latest stable Chrome
- latest stable Edge
- latest stable Firefox
- latest stable Safari

Core manual flows: open/edit/save page, responsive switch, drag/reorder, rich text Bold/Italic, typography, preview, revision restore, menu keyboard, form validation, modal keyboard, publish/rollback.

## UD-114 Accessibility QA

Automated browser tests cover keyboard focus movement, Escape, menu arrow keys, submenu controls, modal focus trap/restore, form invalid-focus and reduced-motion behavior. Static analyzers cover heading/alt/label/focus/contrast findings.

A real screen-reader core-flow remains mandatory manual evidence (NVDA/JAWS/VoiceOver as appropriate). Automated DOM/ARIA checks are not treated as a screen-reader substitute.

## UD-115 Security review

`tests/Architecture/e14-security-audit.sh` applies a high-risk static policy to the new architecture:

- rejects eval/shell execution/unserialize primitives in `src/`
- rejects raw request globals in service/domain code
- verifies dedicated custom-code and AI capabilities
- verifies HMAC + `hash_equals` preview token boundary
- verifies explicit import confirmation and safe URL boundaries

Existing legacy monolith remains subject to final live security regression before legacy removal. No critical/high finding in the new architecture may be open when E14 is promoted.

## UD-116 Performance budget

CI budgets:

- `site-builder-runtime.js` <= 50 KiB
- `interaction-runtime.js` <= 50 KiB
- 1,000 artifact export/import/dry-run plan < 5 seconds in CI
- portability memory delta < 128 MiB
- Side Health analysis of 120 elements < 2 seconds in CI

Final live budgets (manual/field measurement) should additionally capture LCP/CLS/INP, page transfer size and editor responsiveness on test2.

## UD-117 Migration/rollback

Automated migration fixture:

1. capture checksum-protected pre-migration backup
2. migrate through a registered multi-step schema path
3. verify target transformations
4. restore exact original state
5. verify unknown migration targets fail rather than guessing

E13 separately tests failed-import transaction rollback and pre-import recovery backups. A live-copy migration/rollback remains required before converting current pages.

## UD-118 MVP E2E

Automated flow covers page schema -> autosave -> permanent save -> unpublished mobile preview -> atomic publish -> Side Health -> page/global-styles export/import -> revision restore.

## UD-119 v1 E2E

Automated flow adds global Header/Footer templates, accessible classic menu and accessible form rendering to the workflow/quality/portability stack.

Final live acceptance on test2 is still required because the current pages intentionally remain on the legacy runtime until the end.

## UD-120 Documentation/onboarding

See `docs/ultimate-designer-onboarding.md` for the administrator/designer workflow and the final migration order.

## Manual release evidence still required

The release gate intentionally starts these as pending:

- latest Chrome brand test
- latest Edge brand test
- latest Firefox brand test
- latest Safari brand test
- screen-reader core flow
- test2 live-site E2E
- Vehicle/Event/Gallery visual/function regression
- migration/rollback on a live copy

These are the final gates before enabling new runtime assignments on existing pages and before removing legacy code.
