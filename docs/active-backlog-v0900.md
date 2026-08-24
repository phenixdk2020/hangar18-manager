# Hangar18 Manager v0.9.0 – Editor Architecture Consolidation

## Formål

v0.9.0 stopper patch-kæden i editorens layoutfundament. Versionen introducerer én canonical layout-model for hierarki, rækkefølge, responsive kolonne-spans og stack-relationer. De eksisterende section/span/stack stores bruges i v0.9.x kun som kompatibilitetsprojektioner, indtil migreringen kan afsluttes uden at ændre frontend.

## Backlog

### ARCH-CANONICAL-MODEL-107 — FIX-CANDIDATE
- Én browsermodel ejer `parent`, `order`, `removed`, responsive spans og stack-state.
- Modellen bygges fra canonical source rows og må aldrig udledes af visuelle proxy-kloner.
- Hierarki valideres for manglende parents, ugyldige parent-typer og cycles.

### ARCH-SAVE-PROJECTION-108 — FIX-CANDIDATE
- Gem tager et canonical snapshot ved brugerens Save-intent.
- Snapshot projiceres server-side til `sections`, `h18_lego_layout_span` og `h18_lego_stack_v0851` før de eksisterende persistence-handlers kører.
- En manglende eller ufuldstændig model skal fail-open til eksisterende POST-data; den må aldrig slette indhold.
- v0.8.91 save-integrity guard erstattes af den canonical save-kontrakt.

### ARCH-RENDER-OWNER-109 — FIX-CANDIDATE
- Én v0.9.0 renderer genopbygger generic Grid/Flex-layout fra canonical modellen.
- v0.8.90 generic saved-layout rebuild kobles ud af aktiv enqueue.
- Kasse/Auto-kasser bevarer eksisterende adaptere under første migrationstrin.

### ARCH-LEGACY-ADAPTERS-110 — OPEN
- Drag/drop, resize, stack og Inspector fra v0.8.x fungerer midlertidigt som input-adaptere til canonical modellen.
- Efter v0.9.0 QA migreres hvert adapteransvar ind i layout-engine ét ad gangen.
- Ingen nye editorfunktioner før stabilitetsgaten er bestået.

## Regression / QA gate

1. Opret Tekst + Billede og placer dem venstre/højre.
2. Flyt et eksisterende element over/under et andet.
3. Opret Række- og kolonne-kasse med 4/12 + 8/12.
4. Stack Billede under Tekst i samme kolonne.
5. Resize kolonnebredde og elementhøjde.
6. Gem som ny version.
7. Reload editoren og verificér samme parent/order/span/stack.
8. Gem igen uden layoutændring og verificér identisk struktur.
9. Preview og offentlig frontend skal være visuelt uændrede.
10. Slet ét element, Gem og reload.
11. Slet alle elementer bevidst på en testside, Gem og verificér at handlingen respekteres.
12. Verificér at en Gem aldrig kan konvertere et ellers aktivt layout til alle `Remove=1`.
13. Trace skal vise canonical model ved boot, reconcile og save uden rå tekst-/credential-data.

## Status for tidligere fejl

- `SAVE-INTEGRITY-106`: superseded af `ARCH-SAVE-PROJECTION-108` når v0.9.0-gaten består.
- `SAVE-RELOAD-GRID-104`: dækkes af `ARCH-RENDER-OWNER-109`.
- `SIDE-SPAN-PERSIST-105`: dækkes af canonical span-projektionen.
- `DIAG-RELOAD-103` og `DIAG-LIVE-101`: beholdes som QA-infrastruktur.
- `IMAGE-FIT-PARITY-100`, `VERTICAL-ELEMENT-RESIZE-099`, `FRONTEND-STACK-096`, `CANVAS-STACK-AUTOHEIGHT-097`: regressionskontrolleres, men ændres ikke funktionelt i v0.9.0.
