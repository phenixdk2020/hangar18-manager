# Hangar18 Manager — aktiv backlog v0.8.72

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.72**  
**Release commit:** `98b2ef652f3127f3ff39786067e720a67423a7ea`  
**Package SHA-256:** `37fd014a92bf3333f0d200f8d2b5621e3ccefbfd86b190b9e26f9ba9803aac68`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.71

- `IND I KASSEN` blev fortsat ikke synlig i brugerens faktiske drag-scenarie.
- Child-selection viste fortsat kun rød kant et splitsekund.

## Nye root causes i v0.8.72

- Nested selection blev korrekt sat ved child-click, men det efterfølgende syntetiske canonical `.h18-page-section-edit`-klik kunne nedgradere samme key fra nested til top-level. v0.8.72 bevarer nested-mode for identisk handoff-key.
- Kasse-overlay og child-overlays kunne overlappe. Child-overlays kunne visuelt/hit-testmæssigt vinde med Over/Under. v0.8.72 giver Kasse-overlay højere lagprioritet og prioriterer `is-inside` i hit-testen.
- Asset-cache er verificeret som ikke-root-cause: relevante editor assets enqueue'es med `filemtime()`.

## Status

| Område | Status | Næste handling |
|---|---|---|
| LEGO child-selection | 🟡 FIX-KANDIDAT v0.8.72 | Klik child i Kassen og verificér at rød ramme bliver stående gennem Inspector-handoff. |
| LEGO IND I KASSEN | 🟡 FIX-KANDIDAT v0.8.72 | Træk almindeligt top-level element over Kasse med eksisterende children og verificér at central IND I KASSEN-zone er synlig og vinder overlap. |
| LEGO Over/Under stack | 🟡 BEVARET v0.8.51 | Regressionstest; skal fortsat fungere. |
| LEGO repaint/resize | 🔴 BACKLOG | `LEGO-REPAINT-062` forbliver åben. |
| GitHub updater status | 🔴 REGRESSION | `UPDATER-STATUS-001` forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | `UPDATER-VERSION-002` forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres. |
| Public cutover | 🔒 LÅST | Ingen cutover før samlet manuel QA. |

## Manuel test v0.8.72

- [ ] Klik child-element i Kassen → child får rød ramme.
- [ ] Vent mindst 5 sekunder → rammen bliver stående.
- [ ] Klik et andet child → rammen flytter én gang til det nye child.
- [ ] Træk et top-level Tekst/Billede over en Kasse med eksisterende child-indhold → `IND I KASSEN` er synlig i midten, også hvor child-overlays findes.
- [ ] Slip på `IND I KASSEN` → `LayoutParentKey` bliver Kasse-key og elementet bliver child.
- [ ] Slip på Over/Under udenfor centerzonen → v0.8.51 placement fungerer fortsat.

## Arbejdsregel

Selection må have én semantisk ejer. Programmatisk Inspector-handoff for samme nested key må ikke ændre selection-mode. Kasse `IND I` er en Kasse-level semantik og skal visuelt/hit-testmæssigt have prioritet over child-overlays i centerområdet.
