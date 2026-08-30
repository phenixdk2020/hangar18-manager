# Visual Designer Manager 0.1.61 status

## Keyboard / pixel-finjustering
- Pil = 1 px via canonical offsetX/offsetY.
- Shift + pil = 10 px.
- Offset kan redigeres/nulstilles i Inspector.
- Grid x/y/w/h ændres ikke af pixel-finjustering.
- Piletastsekvens grupperes til én Undo/Redo-transaktion.

## Clipboard
- Ctrl/Cmd+C = Kopiér.
- Ctrl/Cmd+V = Indsæt.
- Ctrl/Cmd+D = Duplikér.
- Kasse/Sektion kopierer hele subtree.
- Nye IDs genereres, parentId remappes, og indsætning virker mellem Designer-sider via bruger-specifikt browser-clipboard.

## Header/Footer
- Status: FÆRDIG baseline.
- Definition of Done verificeres af `.github/scripts/v0161_header_footer_qa.php`.
- Shared `resolveChoiceId()` bruges til frontend og composite Preview.
- Inaktive defaults/templates vælges ikke automatisk.
- `Ingen Header/Footer`, side override, standardvalg, multi-template og fase-1 migration er regressionsgates.

## Uden for denne afsluttede baseline
- Assignment-regler, Export/Import og nye generelle elementtyper er separate fremtidige udvidelser.
