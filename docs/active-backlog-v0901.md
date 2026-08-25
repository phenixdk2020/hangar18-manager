# Hangar18 Manager v0.9.1 – Physical Canvas, History og Re-parenting

## Formål

v0.9.1 flytter editorens næste tre interaktionsansvar ind i den kanoniske 0.9.x-arkitektur: fysisk canvas-geometri, Undo/Redo og flytning af allerede deployede elementer mellem root og containere.

Målet er en editor, hvor elementets synlige kasse er en reel repræsentation af dets størrelse – ikke kun et administrativt kort. Et element skal kunne behandles som en Excel-celle: det kan gøres større eller mindre fra venstre, højre, top, bund og alle fire hjørner. Horisontal geometri snapper til et 120-unit layout-grid.

## Kanonisk geometri

- Horisontal canvas: **120 units**.
- Vertikal snap: **8 px** pr. unit.
- Geometri gemmes pr. SectionKey og pr. breakpoint.
- Desktop er første autoritative fysiske canvas; Tablet/Mobile kan arve Desktop og senere få egne overrides.
- En gemt geometri må ikke kun være CSS i editoren. Den skal kunne genindlæses og projiceres til den offentlige frontend.
- Fysisk geometri må ikke udledes fra visuelle proxy-kloner ved Save. Proxyer er rendering; source rows/canonical model er data.

## Backlog

### CANVAS-PHYSICAL-GEOMETRY-111 — IN PROGRESS
- Canvas bruger 120 horisontale layout-units.
- Elementets editorramme følger den faktiske bredde og højde.
- Elementet får 8 resize-zoner: N, NE, E, SE, S, SW, W, NW.
- Venstre/top resize flytter samtidig elementets origin, så modsatte kant forbliver forankret.
- Minimumsstørrelse og canvas-grænser håndhæves.
- Én resize-gesture er én historiktransaktion.

### CANVAS-REPARENT-112 — IN PROGRESS
- Et allerede eksisterende element kan trækkes ind i `container`, `grid` eller `flex`.
- Et element inde i en kasse kan trækkes ud til root igen.
- Drop på eget element eller en descendant afvises for at forhindre cycles.
- `LayoutParentKey` og `Order` opdateres kanonisk.
- Stack-relation nulstilles/valideres når parent ændres.
- Én drag/drop-gesture er én historiktransaktion.

### CANVAS-HISTORY-113 — IN PROGRESS
- Synlige knapper: **Fortryd** og **Gentag**.
- Tastatur: Ctrl/Cmd+Z = Undo, Ctrl/Cmd+Shift+Z og Ctrl+Y = Redo.
- Historik bruger snapshots af kanonisk layout + fysisk geometri.
- Ny ændring efter Undo rydder redo-stakken.
- Drag og resize må ikke generere hundredvis af historikpunkter under pointermove.
- History restore skal re-render canvas og opdatere Save-payload.

### FRONTEND-PHYSICAL-PARITY-114 — OPEN
- Gemte 120-unit bredder projiceres til frontend.
- Gemte eksplicitte højder respekteres uden at ændre Vehicle/Event/Gallery-runtime.
- Existing 12-column span-store forbliver kompatibilitetsfallback under migreringen.

### DIAG-INTERACTION-115 — OPEN
- Trace events for `RESIZE_BEGIN/COMMIT`, `REPARENT_BEGIN/COMMIT`, `UNDO`, `REDO`.
- Log må kun indeholde keys, type, parent/order og geometri – aldrig rå tekstindhold eller credentials.

## Interaktionskontrakt

1. **Resize**
   - Pointerdown på resize-handle tager et before-snapshot.
   - Pointermove opdaterer kun preview/current geometry.
   - Pointerup validerer, gemmer after-state og laver ét history-entry.

2. **Flyt eksisterende element**
   - Pointerdown på move-handle tager et before-snapshot.
   - Gyldige containere og root får tydelige drop-highlights.
   - Pointerup ændrer parent/order én gang og re-renderer fra canonical state.

3. **Undo/Redo**
   - Restore skriver canonical parent/order tilbage til source rows.
   - Geometry-state restores separat men ligger under samme layout-transaktion.
   - Base layout-engine reconciles efter restore.

## QA-gate

1. Opret to tekst-elementer og én Række-/kolonne-kasse.
2. Træk et allerede eksisterende tekst-element ind i kassen.
3. Gem + reload: elementet er stadig i kassen.
4. Træk samme element ud til root.
5. Gem + reload: elementet er stadig på root.
6. Resize et element fra E og W; modstående kant forbliver stabil.
7. Resize fra N og S; højde følger håndtaget fysisk.
8. Resize fra alle fire hjørner.
9. Kontrollér snap til 120-unit grid og 8-px vertikal unit.
10. Undo efter resize giver nøjagtig pre-resize geometri.
11. Redo giver nøjagtig post-resize geometri.
12. Undo efter re-parent flytter elementet tilbage til oprindelig parent/order.
13. Redo flytter det frem igen.
14. Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z og Ctrl+Y testes.
15. Save/reload bevarer parent/order/geometri.
16. Preview/frontend matcher gemt geometri.
17. Vehicle/Event/Gallery er visuelt og funktionelt uændrede.
18. Trace viser én COMMIT pr. færdig gesture, ikke pr. pointermove.

## Definition of Done

v0.9.1 kan først markeres PASS, når både re-parenting, 8-vejs resize, Undo/Redo og Save/Reload er verificeret på samme testside. En visuel resize uden persisted geometry tæller ikke som løst.
