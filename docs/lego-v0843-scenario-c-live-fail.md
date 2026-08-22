# Hangar18 Manager v0.8.43 — Scenario C live FAIL

## Status

**FAIL** på `https://test2.hangar18.dk` efter installation af den officielle v0.8.43-pakke.

Den synlige fejl er, at palette-side-drop til Venstre/Højre opretter en Grid container / Auto-kasse, men den bliver stående med `0 stk.`. De to indholdselementer forbliver lodrette topniveau-søskende i stedet for at blive børn af den nye Auto-kasse.

## Diagnose

v0.8.43 rettede parent-select → `LayoutParentKey`-synkroniseringen, men den automatiske regression modellerede ikke hele den virkelige Inspector-DOM-kontrakt.

Når Ultimate Designer vælger den nyoprettede Grid-række, flyttes dens komplette `.h18-page-section-body` fysisk fra rækken til `#h18-page-inspector-target`.

Der var to separate Inspector-blinde opslag:

1. Nesting-motorens `rowKey()` slog kun `.h18-page-section-key` op inde i selve rækken. Den valgte Grid-række kunne derfor midlertidigt se ud til at have en tom key, så `findNewRow()` kunne miste den nyoprettede Grid. `syncFlatOrder()` havde samme blinde vinkel for `.h18-page-section-order`.
2. v0.8.43 ParentKey-guarden fandt også en parent via en key, der kun blev læst inde i rækken. Når den nye Grid var valgt og dens key lå i Inspector, kunne guarden derfor ikke genkende Grid'en som gyldig parent og tilføjede ikke den nye `auto-*` option til børnenes parent-select. Den normale WordPress select → hidden-synkronisering kunne derefter nulstille den allerede korrekte `LayoutParentKey` tilbage til tom.

Det sidste forklarer den reproducerede tilstand præcist: Grid/Auto-kassen findes, men begge børn ender igen med tom parent og Grid'en viser `0 stk.`.

## LEGO-044 rettelse

PR #144 gør alle nødvendige strukturelle opslag Inspector-aware via samme kontrolmodel:

- nesting `rowKey()` læser `.h18-page-section-key` gennem `controls()`.
- `syncFlatOrder()` skriver `.h18-page-section-order` gennem `controls()`.
- ParentKey-guarden finder den valgte Inspector-hosted parent-key og parent-label gennem en Inspector-aware `controls()` helper.
- ParentKey-guarden sikrer parent-optionen på både almindelige og Inspector-hosted selects gennem samme helper.
- Scenario C-browserregressionen flytter den nyoprettede Grids komplette section body ind i Inspector under selve placement-handoffet og inkluderer den reelle select → hidden-synkronisering.
- Regressionen kræver samme Auto-kasse parent-key/select på begge elementer, 2 synlige børn, korrekt Grid-order og 0 orphan Grid-containere.

Placement-authority er fortsat den eksisterende nesting-motor og `LayoutParentKey`; der er ikke tilføjet en parallel placement-motor.

## Gate

v0.8.43 må ikke markeres PASS. I9/I10 og public cutover forbliver låst, indtil en ny build med LEGO-044 er testet manuelt på test2.
