# Hangar18 Manager v0.8.43 — Scenario C live FAIL

## Status

**FAIL** på `https://test2.hangar18.dk` efter installation af den officielle v0.8.43-pakke.

Den synlige fejl er, at palette-side-drop til Venstre/Højre opretter en Grid container / Auto-kasse, men den bliver stående med `0 stk.`. De to indholdselementer forbliver lodrette topniveau-søskende i stedet for at blive børn af den nye Auto-kasse.

## Diagnose

v0.8.43 rettede parent-select → `LayoutParentKey`-synkroniseringen, men den automatiske regression modellerede ikke hele den virkelige Inspector-DOM-kontrakt.

Når Ultimate Designer vælger den nyoprettede Grid-række, flyttes dens komplette `.h18-page-section-body` fysisk fra rækken til `#h18-page-inspector-target`. Nesting-motorens `rowKey()` slog fortsat kun `.h18-page-section-key` op inde i selve rækken. Den valgte Grid-række så derfor midlertidigt ud til at have en tom key, så `findNewRow()` ikke fandt den nyoprettede Grid og placement-flowet stoppede før `configureAuto()` og `setParent()`.

`syncFlatOrder()` havde samme blinde vinkel for `.h18-page-section-order` på en valgt Inspector-hosted række.

## LEGO-044 rettelse

PR #144 gør de to strukturelle opslag Inspector-aware via den allerede eksisterende `controls()`-abstraktion:

- `rowKey()` læser `.h18-page-section-key` gennem `controls()`.
- `syncFlatOrder()` skriver `.h18-page-section-order` gennem `controls()`.
- Scenario C-browserregressionen flytter nu den nyoprettede Grids komplette section body ind i Inspector under selve placement-handoffet.
- Regressionen kræver samme Auto-kasse parent-key på begge elementer, 2 synlige børn, korrekt Grid-order og 0 orphan Grid-containere.

Den eksisterende v0.8.43 ParentKey-guard bevares, fordi den løser en separat select-synkroniseringsfejl.

## Gate

v0.8.43 må ikke markeres PASS. I9/I10 og public cutover forbliver låst, indtil en ny build med LEGO-044 er testet manuelt på test2.
