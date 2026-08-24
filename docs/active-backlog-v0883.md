# Hangar18 Manager — canonical backlog delta v0.8.83

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.82 installeret og under manuel test  
**Extends:** `docs/active-backlog-v0882.md`

Denne delta registrerer den reproducerede v0.8.82 hard-freeze ved indsættelse af et rent Billede-element samt de nødvendige trace/runtime-sikkerhedsrettelser. Tekst/stacking-sporet er eksplicit regressionstestet separat og er ikke årsagen.

## Manuel evidens før fix

- `Tekst → tekst til højre → tekst under`: **PASS**.
- `Tekst → billede til højre`: **HARD FREEZE**; siden kan compositor-scrolle, men JavaScript/click/drag og DevTools Console svarer ikke.
- `Tekst → tekst til højre → billede under`: **HARD FREEZE**.
- Fælles faktor er derfor rent `image`-element, ikke generel side-by-side eller vertical stacking.

# H. LEGO Inspector / image runtime

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| INSPECTOR-IMAGE-086 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.83 | Rent `image` må kunne oprettes top-level, til højre/venstre for et eksisterende element og over/under et nested/stacked element uden main-thread freeze. Root cause-kandidaten er v0.8.82 `polishImageInspector()`: Inspectorens globale MutationObserver kan observere de DOM-flytninger som samme callback selv udfører (`insertBefore`/`insertAfter` og label/picker-polish), så image-selection kan skabe en selvforstærkende observer-loop. v0.8.83 lægger en dedikeret observer guard ind **før** Inspector-runtime: callbacks med `clarifyInspectorControls` + `refreshSelectedCanvasMarker` debounces og undertrykker egne mutations i et kort settle-window. Tekst/stacking-adfærd må ikke ændres. |

# T. Trace / diagnostik

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| TRACE-SAFETY-088 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.83 | Udvidet trace må ikke kunne forstærke en editor-fejl. Trace MutationObserver ignorerer egne UI-områder, eventpanelets repaint throttles, højfrekvente drag/sort events throttles hårdere, og DOM-tekst omskrives kun når værdien reelt ændres. Trace til/fra må ikke ændre editorens funktionelle resultat. |
| TRACE-UI-087 | Normal | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.83 | Start/Stop/Markér/Eksport-panelet skal være `position:fixed`, tydeligt over viewportens nederste kant, have sikker max-height/overflow og forblive klikbart ved lang Designer-side. Det må ikke næsten forsvinde under bunden som observeret i v0.8.82. |

# Manuel v0.8.83 testmatrix

1. Slå udvidet log **TIL**, åbn Designer og bekræft at Start/Stop-panelet er fuldt synligt over bunden.
2. Opret ét Tekst-element. Drag et nyt **Billede** til højre for teksten. Editor skal fortsat reagere på klik, drag, Inspector og Console.
3. Opret to Tekst-elementer side om side. Drag et nyt **Billede** under det ene. Ingen hard-freeze.
4. Gentag punkt 2 og 3 med trace **FRA**. Resultatet skal være identisk.
5. Vælg det nye Billede-element: billedvælgeren skal fortsat ligge før de valgfrie tekstfelter, og Inspector må ikke begynde at repaint/flicker kontinuerligt.
6. Regression: `Tekst → tekst til højre → tekst under` skal fortsat virke.
7. Efter hver drop: lav endnu et klik og endnu et drag for at verificere at drag/drop state er ryddet.
