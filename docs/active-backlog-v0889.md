# Hangar18 Manager — canonical backlog delta v0.8.89

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.88 live diagnostics  
**Extends:** `docs/active-backlog-v0888.md`

Denne delta bygger på den første komplette site-diagnose fra `testside-ny`. Evidensen viser, at Gem-requesten bevarer det kanoniske parent/child-hierarki. Den synlige regression efter reload ligger derfor i den ældre canvas-komposition, som kun genopbygger `Kasse` (`container`) og `Auto-kasser` (labelled `grid`) og ikke en almindelig `grid`/`flex` parent.

# S. Save/reload canvas parity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| SAVE-RELOAD-GRID-102 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.89 | En gemt almindelig `grid`/`flex` med gyldige `LayoutParentKey`-børn skal efter reload igen vises som én komposition i parent-kassen. Runtime er read/render-only: den må ikke registrere `dragstart`, `dragover`, `drop` eller `dragend`, ændre `LayoutParentKey`, span eller stack-state. For testcasen skal venstre Tekst forblive 4/12, højre Tekst 8/12 og Billede med `StackRootKey` = højre Tekst vises under denne i samme 8/12-kolonne. Source-rækker skjules kun med den nye v0.8.89-proxy-attribut og må ikke overtage legacy Kasse/Auto-kasser. Proxyen skal kunne vælges via eksisterende Inspector-selection og refreshes efter Inspector/resize-ændringer. |

# D. Diagnostics efter reload

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| DIAG-RELOAD-103 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.89 | Site-diagnosen sender et direkte `DIAG_CLIENT_RELOAD_DIRECT_V0889` snapshot uden den gamle Trace-depth-begrænsning. Ved Gem registreres desuden `DIAG_CLIENT_GENERATED_SAVE_PAYLOAD_V0889` efter v0.8.41 submit-serialisering med de genererede `h18_lego_layout_span`- og `h18_lego_stack_v0851`-entries. Det gør før Gem → genereret payload → `SERVER_BEFORE_SAVE` → reload sammenlignelig uden `[depth]`. |

# Dokumenteret root-cause evidence fra v0.8.88

På `testside-ny` viste `DIAG_CLIENT_BEFORE_SAVE` fire sektioner:

- Grid `sektion-mt7gtak9-nm15aqr` som top-level parent.
- Tekst `sektion-mt7gtahl-bqsm1qb` med `LayoutParentKey=sektion-mt7gtak9-nm15aqr` og Desktop span 4.
- Tekst `sektion-mt7gt8nb-r9rxemt` med samme parent og Desktop span 8.
- Billede `sektion-mt7gtfgk-xmxmyts` med samme parent og `StackRootKey=sektion-mt7gt8nb-r9rxemt`, `StackOrder=10`.

`SERVER_BEFORE_SAVE` modtog fortsat alle tre børn med samme grid som `parentKey`. Dermed er browserens canonical hierarchy og serverens pre-save request korrekte. Det tidligere `hasSpanState=false` i v0.8.88-diagnosen er ikke autoritativt: resize-controlleren bruger POST-feltet `h18_lego_layout_span`, mens det gamle diagnoseflag kontrollerede et andet navn.

Legacy `ultimate-designer-nesting-tools.js` klassificerer kun parent som synlig nesting-komposition når `isBox(parent) || isAuto(parent)`. `isAuto` kræver `grid` + label `Auto-kasser`; almindelig Række- og kolonne-kasse falder derfor udenfor canvas-rebuild efter reload.

# Manuel v0.8.89 testmatrix

1. Opdater og åbn den allerede gemte `testside-ny` uden først at ændre siden. Række- og kolonne-kassen skal straks vise sine gemte børn inde i kassen i stedet for tre separate top-level source-rækker.
2. Kontroller layout: Tekst 4/12 til venstre; Tekst 8/12 til højre; Billede under højre Tekst i samme 8/12-kolonne.
3. Klik på venstre Tekst, højre Tekst og Billede inde i den genopbyggede komposition. Eksisterende Inspector-selection skal åbne det korrekte canonical element.
4. Ændr en kolonnebredde eller en billed-/højdeindstilling. Proxyen skal refreshes uden reload og uden at ændre parent-relationer.
5. Gem siden og lad den reloade. Samme komposition og spans/stack skal fortsat vises.
6. Skriv `se loggen`: site-loggen skal indeholde `DIAG_CLIENT_GENERATED_SAVE_PAYLOAD_V0889` med span/stack entries og et fuldt `DIAG_CLIENT_RELOAD_DIRECT_V0889` uden `[depth]` i `sections`.
7. Regression: Tekst/Billede højre/venstre/over/under samt image insert må fortsat fungere; v0.8.89 må ikke eje nogen drag/drop-events.
8. Regression: almindelig `Kasse` og `Auto-kasser` skal fortsat ejes af legacy nesting-runtime og må ikke få v0.8.89-proxy.

# Fortsat separat

Problemet med at flytte et **allerede eksisterende** element direkte IND I en kasse (i stedet for over/under kassen) er fortsat separat og tages senere med live-log. Det er ikke en del af `SAVE-RELOAD-GRID-102`.
