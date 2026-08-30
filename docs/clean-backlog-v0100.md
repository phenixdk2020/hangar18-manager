# Hangar18 Manager Clean v0.1.x – canonical clean backlog

**Statusdato:** 30. august 2026  
**Arkitekturgrænse:** `clean/hangar18-manager/`  
**Legacy-reference:** eksisterende root-plugin v0.9.x må bruges som specifikation/migrationskilde, men ingen gammel editor-runtime må kopieres ind i clean-pluginet.

## Aktuel milepælsstatus · v0.1.62

- **HEADER/FOOTER — FÆRDIG:** multi-template baseline, side-overrides, `Ingen`, standardvalg, migration, versionshistorik og delt Preview/frontend-resolver er lukket som regression-gate.
- **VD-KEYBOARD-001 — IMPLEMENTERET:** markeret element kan finjusteres 1 px med piletaster og 10 px med `Shift + pil`; offset X/Y er canonical og kan nulstilles i Inspector.
- **VD-CLIPBOARD-001 — IMPLEMENTERET:** `Ctrl/Cmd+C`, `Ctrl/Cmd+V` og `Ctrl/Cmd+D`, subtree-kopi af Kasse/Sektion, nye IDs/parentId-remap og clipboard mellem Designer-sider.
- **VD-PAGE-DUPLICATE-001 — IMPLEMENTERET:** Sider kan kopieres med nyt navn som selvstændig kladde, nyt WordPress-ID, unik slug og egen Designer-v1-historik.
- **Næste generelle elementpakke:** Spacer, Divider, Ikon og Tabel/Dataliste. Dynamiske Køretøjer/Events/Billedgalleri følger derefter den separate modularkitektur.

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
- Fra v0.1.1 kan nye palette-elementer trækkes direkte til root, Sektion eller Kasse.

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
- Strukturelle klientevents: boot, add, delete, resize begin/commit, re-parent begin/commit, palette drag/drop, Undo/Redo, Inspector, image select, Save-intent og Restore-intent.
- Serverevents: Save begin/result/error og Restore begin/result/error.
- Logs indeholder IDs/type/parent/order/geometry/image-fit, men ikke rå tekstindhold, credentials, nonce eller tokens.
- Privat 256-bit read-only support-link via REST for den valgte side.

### CLEAN-FRONTEND-008 — IMPLEMENTERET / MANUEL QA
- Sider med clean-model renderes direkte fra samme model på frontend.
- Hver surface bruger 120-unit CSS Grid.
- Text, Image, Section og Container renderes rekursivt.
- Fysisk width/height og image fit/focal følger modellen.
- Sider uden clean-model røres ikke.

### CLEAN-UPDATE-015 — IMPLEMENTERET / MANUEL QA
- Fra v0.1.2 anvendes GitHub som update-kilde via `clean-update.json`.
- WordPress' normale plugin-update-system viser nyere clean-versioner og bruger `Opdater nu`.
- Hangar18 Designer har `Tjek GitHub-opdatering`, som rydder update-cache og laver et nyt check med det samme.
- GitHub-manifestet peger på en versionslåst ZIP i `dist/`.
- Update-pakken SHA-256-verificeres mod manifestet før WordPress får lov at installere den.
- Plugin-headeren bruger `Update URI`, så clean-pluginet ikke kan kollidere med en eventuel WordPress.org-plugin med samme slug.

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

## QA-gate for clean v0.1.x

1. Opret en tom WordPress-side og åbn Hangar18 Designer.
2. Tilføj Sektion, Kasse, to Tekst-elementer og ét Billede.
3. Træk mindst ét nyt palette-element direkte ind i Kasse uden først at oprette det på root.
4. Resize alle elementtyper fra E/W/N/S og mindst to hjørner.
5. Træk eksisterende Tekst ind i Kasse og ud til root igen.
6. Træk Billede ind i Kasse.
7. Test Cover, Contain og Stretch samt focal X/Y.
8. Undo/Redo både resize, re-parent, palette-drop, image-fit og Inspectorændring.
9. Gem som v1, reload editor og verificér identisk model/geometri.
10. Lav ændringer og gem som v2/v3.
11. Restore v1; resultatet skal blive en ny version og v3 skal stadig ligge i historikken.
12. Åbn offentlig side og sammenlign Text/Image/Container-geometri med editor.
13. Kopiér diagnose-link og verificér Save/Restore/re-parent/resize/palette events uden rå tekst eller secrets.
14. Tryk `Tjek GitHub-opdatering`; v0.1.2 skal rapportere at den er aktuel. Når en nyere testversion publiceres, skal WordPress vise `Opdater nu`, hente GitHub-ZIP'en og bestå SHA-256-kontrollen.
15. Side uden clean-model skal fortsat vises fra normal WordPress content.

## Definition of Done

Clean v0.1.x må først markeres PASS efter QA-gaten på det nye rene subdomæne. Først derefter implementeres responsive overrides og senere migratoren til de gamle webpages.
