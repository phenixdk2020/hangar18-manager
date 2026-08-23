# Hangar18 Manager — aktiv backlog v0.8.75

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.75**  
**Package SHA-256:** `f8acf40df3f6426a0ce23150ff6781ba9fa949fb2f8bdeca21f90a64999e1ba2`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md` er historiske snapshots.

## Verificeret fra brugerens v0.8.74-test

- Nested selection inde i layoutkassen fungerer nu stabilt.
- Diagnose viste `selection-runtime=0.8.74`, `mode=nested`, `matching=1`, `selectedMatching=1`, `selectedTotal=1`.
- Efter klik på et frit top-level element blev native WordPress-rækken skiftet, men LEGO-selection blev stående på den gamle nested key. Det gav to røde rammer samtidig.
- Screenshot viser at det ønskede drop-target er en **Række- og kolonne-kasse**, dvs. grid/flex-layout — ikke kun en almindelig `container`-Kasse.
- Tidligere `IND I KASSEN`-klassifikation accepterede kun almindelig container/Kasse. Det forklarer hvorfor inside-zonen aldrig blev vist på det testede grid/flex-target.

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-075 | Kritisk | 🟡 FIX-KANDIDAT | Skift fra nested child til top-level element efterlod gammel nested key aktiv, selv om native række var skiftet. | Top-level klik læser canonical key efter Inspector-handoff, skifter til `mode=top`, fjerner alle nested selection-klasser og efterlader præcis én rød ramme. |
| LEGO-INSIDE-075 | Kritisk | 🟡 FIX-KANDIDAT | `IND I KASSEN` blev kun tilbudt på almindelig container, men brugeren arbejder også med flex/grid-layoutkasser. | Almindeligt element-drag viser `IND I KASSEN` på container, flex og ikke-Auto grid. Slip dér sætter LayoutParentKey til layoutkassen. Auto-kasser bevarer særskilt semantik. |
| LEGO-NESTED-SELECTION-074 | Kritisk | ✅ VERIFICERET | Tidligere child-selection forsvandt efter render. | v0.8.74-diagnose viste stabil nested key og én markeret visible child-node. |
| LEGO-REPAINT-062 | Høj | 🔴 BACKLOG | Klik/resize kan stadig give unødige repaint-opdateringer. | Ingen flerblink efter selection/placement er stabile. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede/latest kan vise `JA`. | Korrekt version_compare-state. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Automatisk check kan sætte `JA` uden at opdatere vist latest-version. | Availability og vist versionsnummer kommer fra samme manifest-state. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel test v0.8.75

1. Klik et child-element inde i Række- og kolonne-kassen → kun child rød.
2. Klik derefter et frit top-level element → child-rammen skal forsvinde, kun top-level-elementet må være rødt.
3. Klik tilbage på child → selection skal igen flytte til child uden dobbelt markering.
4. Træk et frit Tekst/Billede-element hen over midten af Række- og kolonne-kassen → `IND I KASSEN` skal nu være synlig.
5. Slip på `IND I KASSEN` → elementet skal blive child i grid/flex-layoutet og ikke blot reorder over/under.
6. Regressionstest almindelig Kasse samt Over/Under og Auto-kasser.

Updater og repaint behandles fortsat som separate spor.
