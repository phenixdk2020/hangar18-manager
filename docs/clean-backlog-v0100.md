# Hangar18 Manager Clean v0.1.0 – canonical clean backlog

**Statusdato:** 25. august 2026  
**Arkitekturgrænse:** `clean/hangar18-manager/`  
**Legacy-reference:** eksisterende root-plugin v0.9.x må bruges som specifikation/migrationskilde, men ingen gammel editor-runtime må kopieres ind i clean-pluginet.

## Formål

Denne backlog er arbejdsplanen for den nye WordPress-installation på et rent subdomæne. Clean-pluginet starter med en ny datamodel og ny editor. Gamle Hangar18-sider konverteres først, når clean-editorens Save/Reload/Restore og frontend-paritet er QA-godkendt.

## Implementeret – manuel QA mangler

### CLEAN-ARCH-001 — IMPLEMENTERET / MANUEL QA
- Én canonical JSON-model pr. WordPress-side i `_h18_clean_layout_v1`.
- Elementer har `id`, `type`, `parentId`, `order`, `geometry` og `props`.
- Serveren normaliserer IDs, typer, parents, cycles, geometry og props før persistens.
- Ingen DOM/proxy bruges som Save-kilde.

### CLEAN-CANVAS-002 — IMPLEMENTERET / MANUEL QA
- 120 horisontale layout-units.
- 8 px lodret snap.
- Fysisk editorboks bruger samme `x/y/w/h` som modellen.
- 8 resize-håndtag: N, NE, E, SE, S, SW, W, NW.
- Venstre/top-resize flytter origin, så modsatte kant forbliver forankret.

### CLEAN-HISTORY-003 — IMPLEMENTERET / MANUEL QA
- Fortryd/Gentag knapper.
- Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z og Ctrl+Y.
- Én resize/re-parent/Inspector-ændring bliver én history-transaktion.
- Ny ændring efter Undo rydder redo-stakken.

### CLEAN-REPARENT-004 — IMPLEMENTERET / MANUEL QA
- Et allerede deployet element kan trækkes ind i `Sektion` eller `Kasse`.
- Elementet kan trækkes ud til root igen.
- Self/descendant-drop afvises for at forhindre cycles.
- Re-parent ændrer modellen først og renderer derefter canvas fra modellen.

### CLEAN-IMAGE-005 — IMPLEMENTERET / MANUEL QA
- Billede vælges via WordPress Media Library.
- Standard `Cover`: proportioner bevares, og billedet beskæres automatisk til den fysiske elementkasse.
- `Contain`: hele billedet vises uden deformation.
- `Stretch`: bredde/højde må afvige, så billedet kan deformeres frit.
- Focal X/Y styrer crop-position.
- Editor-preview og frontend bruger samme fit/focal-værdier.

### CLEAN-SAVE-RESTORE-006 — IMPLEMENTERET / MANUEL QA
- Gem opretter en ny clean-version med normalized model og strukturel SHA-256 digest.
- Op til 50 clean-versioner bevares pr. side.
- Restore af en tidligere version gemmer den valgte model som en ny version; den nuværende version forbliver i historikken som sikkerhed.
- Save/Restore bruger nonce og `edit_pages` capability.

### CLEAN-DIAG-007 — IMPLEMENTERET / MANUEL QA
- Strukturelle klientevents: boot, add, delete, resize begin/commit, re-parent begin/commit, Undo/Redo, Inspector, image select, Save-intent og Restore-intent.
- Serverevents: Save begin/result/error og Restore begin/result/error.
- Logs indeholder IDs/type/parent/order/geometry/image-fit, men ikke rå tekstindhold, credentials, nonce eller tokens.
- Privat 256-bit read-only support-link via REST for den valgte side.

### CLEAN-FRONTEND-008 — IMPLEMENTERET / MANUEL QA
- Sider med clean-model renderes direkte fra samme model på frontend.
- Hver surface bruger 120-unit CSS Grid.
- Text, Image, Section og Container renderes rekursivt.
- Fysisk width/height og image fit/focal følger modellen.
- Sider uden clean-model røres ikke.

## Næste backlog

### CLEAN-RESPONSIVE-009 — ÅBEN / NÆSTE
- Desktop, Tablet og Mobil får hver fysisk `x/y/w/h` override med tydelig `Arv fra Desktop`.
- Editor-toolbar skifter fysisk canvas-breakpoint uden at mutere de andre breakpoints.
- Mobil må som standard arve Desktop men kan sættes til 120/120 og egen højde/position.
- Undo/Redo omfatter breakpointændringer.

### CLEAN-THEME-010 — ÅBEN
- Installer Hangar18 Base Theme 1.2.0 som visuel baseline.
- Lav eksport/import af site-specifik Custom CSS og relevante theme settings fra den gamle installation.
- Importen må kun indeholde theme/frontend-konfiguration; ingen gammel editor-state eller editor-JavaScript.
- Header, footer, banner, menu, farver, typografi og 90%-desktopbredde regressionskontrolleres.

### CLEAN-ELEMENTS-011 — ÅBEN
- Button, Spacer, Heading, Divider og Gallery som native clean-elementer.
- Elementdefinitioner registreres centralt og får schema/Inspector/Renderer i samme kontrakt.

### CLEAN-ORDERING-012 — ÅBEN
- Drop før/efter eksisterende sibling, ikke kun append til parent.
- Visuel insertion-line.
- `order` normaliseres deterministisk uden DOM som canonical state.

### CLEAN-PREVIEW-013 — ÅBEN
- Live preview af ugemte canonical state gennem samme renderer-kontrakt.
- Må ikke klone admin-DOM.
- Desktop/Tablet/Mobil viewport.

### CLEAN-MIGRATOR-014 — BLOKERET INDTIL CLEAN-QA PASS
- Læs gamle Hangar18-sider read-only.
- Konverter til clean-model som kladde/kopi.
- Vis gammel side ↔ clean konvertering side om side.
- Ingen gammel side overskrives automatisk.
- Vehicle/Event/Gallery migreres først efter de generelle sider.

## QA-gate for v0.1.0

1. Opret en tom WordPress-side og åbn Hangar18 Designer.
2. Tilføj Sektion, Kasse, to Tekst-elementer og ét Billede.
3. Resize alle elementtyper fra E/W/N/S og mindst to hjørner.
4. Træk eksisterende Tekst ind i Kasse og ud til root igen.
5. Træk Billede ind i Kasse.
6. Test Cover, Contain og Stretch samt focal X/Y.
7. Undo/Redo både resize, re-parent, image-fit og Inspectorændring.
8. Gem som v1, reload editor og verificér identisk model/geometri.
9. Lav ændringer og gem som v2/v3.
10. Restore v1; resultatet skal blive en ny version og v3 skal stadig ligge i historikken.
11. Åbn offentlig side og sammenlign Text/Image/Container-geometri med editor.
12. Kopiér diagnose-link og verificér Save/Restore/re-parent/resize events uden rå tekst eller secrets.
13. Side uden clean-model skal fortsat vises fra normal WordPress content.

## Definition of Done

v0.1.0 må først markeres PASS efter QA-gaten på det nye rene subdomæne. Først derefter implementeres responsive overrides og senere migratoren til de gamle webpages.
