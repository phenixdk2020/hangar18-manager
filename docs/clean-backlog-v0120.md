# Hangar18 Manager Clean – Backlog fra v0.1.20

**Statusdato:** 25. august 2026  
**Aktuel frigivet version:** 0.1.20  
**Arkitekturgrænse:** `clean/hangar18-manager/`  
**Autoritativ designreference:** `CLEAN-DESIGN-MANUAL.md`  
**Brugerreference:** `CLEAN-USER-MANUAL.md` / Word-brugermanual  

## Formål

Denne backlog erstatter den praktiske plan i `clean-backlog-v0100.md` som arbejdsplan fra Clean 0.1.20 og frem. Den gamle backlog bevares som historik.

Målet er først at gøre den generelle Clean Designer komplet, responsiv, sikker og theme-integreret. Derefter bygges Header/Footer, flere elementtyper, dynamiske datamoduler og migrering af eksisterende sider.

---

# A. Allerede implementeret gennem 0.1.20

## A1. Canonical editor og layout
- Canonical JSON-model pr. WordPress-side.
- 120 vandrette units og 8 px lodret grid.
- x/y/w/h, parentId og order.
- 8-vejs resize.
- Drag-and-drop med Over / Under / Venstre / Højre / Ind i.
- Celle-split med row-span-lignende layout.
- Undo/Redo som modeltransaktioner.
- Labels er editor-overlay og påvirker ikke fysisk geometri.
- Grøn selection, blå hover/drop, rød overlap-advarsel.

## A2. Sektion/Kasse
- Sektion og Kasse kan indeholde elementer.
- Kasse/Sektion auto-grow ud fra børn.
- Manuel højde fungerer som minimum.
- Border, padding, baggrund og hjørner findes.
- Container/barn-forhold tæller ikke som overlap.

## A3. Tekst
- Valgfri overskrift.
- H2–H6.
- Brødtekst.
- Justering.
- Baggrund/gennemsigtig.
- Brødtekstfarve.
- Overskriftsfarve.
- Padding.
- Border, radius og Afstand X/Y.

## A4. Billede
- WordPress Media Library.
- Billedboks og billede er separate lag.
- Vis hele / Fyld-beskær / Original / Stræk.
- Vandret/lodret placering og focal X/Y.
- Boksbaggrund.
- Manuel billedtilstand med selvstændig X/Y/bredde/højde.
- Selve billedet kan flyttes/skaleres uafhængigt af billedboksen.
- Lås proportioner.
- Border og radius på billedboksen.

## A5. Preview, Save og versioner
- Usavet theme-accurate Preview.
- Gem & vis.
- Save-verifikation via digest.
- Hver Gem opretter ny version.
- Obligatorisk ændringsbeskrivelse.
- Forhåndsvis historisk version.
- Gendan original som ny ikke-destruktiv version.
- Opret kopi som ny WordPress-kladdeside med egen historik.

## A6. Update og sikkerhed
- GitHub update-manifest.
- SHA-256-verifikation af releasepakke.
- Direkte update fra Hangar18 Manager.
- Aktiv plugin-status bevares gennem self-update.
- Automatisk ZIP-backup af programmet før update.
- Update afbrydes hvis backup ikke kan verificeres.
- Releaseændringer/changelog vises før opdatering.

---

# B. P0 – Kritisk fundament før bred sidebygning

## CLEAN-RESPONSIVE-021 – Desktop / Laptop / Mobil
**Prioritet: P0 · Næste build**

- Designer-toolbar med tre aktive arbejdsvisninger: Desktop, Laptop og Mobil.
- Canonical `geometry.desktop`, `geometry.laptop` og `geometry.mobile`.
- Laptop arver Desktop som standard.
- Mobil arver Desktop/Laptop som standard, indtil override oprettes.
- Tydelig `Arver` / `Egen layout` status pr. element og breakpoint.
- Mulighed for at nulstille Laptop/Mobil til arv.
- Resize og flytning ændrer kun aktivt breakpoint.
- Undo/Redo skal kende breakpointet.
- Frontend breakpoints skal rendere korrekt geometri.
- Ingen vandret overflow på Laptop/Mobil.
- Preview skal kunne åbnes i Desktop/Laptop/Mobil viewport.

**Definition of Done:** Samme side kan være 2 kolonner på Desktop/Laptop og 1 kolonne på Mobil uden at duplikerer siden eller elementerne.

## CLEAN-HIERARCHY-022 – Lås Sektion/Kasse-regler
**Prioritet: P0**

- Sektion må kun ligge direkte på root.
- Kasse må ligge i Sektion eller Kasse.
- Tekst/Billede/andre leaf-elementer må ligge i Sektion eller Kasse.
- Reparent/drop må ikke kunne skabe Sektion inde i Kasse.
- Eksisterende ulovlige modeller normaliseres sikkert uden datatab.
- Palette/drop-guides skal forklare hvorfor et drop ikke er tilladt.

## CLEAN-LAYOUT-QA-023 – Stabiliser layoutmotor
**Prioritet: P0**

- QA celle-split på komplekse layouts.
- QA auto-grow med padding, border, radius og Afstand Y.
- QA nested Kasser.
- QA labels ved flere nested niveauer.
- Beslut endelig overlap-policy.
- Standard-layout skal forhindre utilsigtet overlap.
- Eventuel bevidst overlap flyttes senere til særskilt Layer/Fri placering-mode.

---

# C. P1 – Globalt design og theme integration

## CLEAN-GLOBAL-DESIGN-024
**Prioritet: P1**

Global designmodel med egen versionshistorik:

- Primær skrifttype.
- Standard brødtekstfarve.
- Standard overskriftsfarve.
- Sidebaggrund.
- Hangar18 farvepalette.
- Desktop sidebredde.
- Laptop sidebredde.
- Mobil sidebredde.
- Standard padding/afstande.
- Standard border/radius.
- Mulighed for lokale overrides på elementer.

## CLEAN-THEME-SHELL-025
**Prioritet: P1**

- Hangar18 Base Theme gøres til tynd runtime/shell.
- Manager bliver visuel sandhed for Header/Side/Footer.
- Theme fallback hvis Manager er deaktiveret.
- Undgå parallel CSS mellem tema og Manager.
- Regressionstest mod eksisterende Hangar18-udseende.
- Header, side og footer må ikke overlappe fysisk.

---

# D. P1 – Header og Footer Designer

## CLEAN-HEADER-026
**Prioritet: P1**

- Global Header-model og versionshistorik.
- Samme LEGO/grid-motor som Side Designer.
- Responsive Desktop/Laptop/Mobil-varianter.
- Elementer: Logo, Menu, Tekst, Knap, Kasse, evt. Ikon.
- Sticky / ikke sticky.
- Headerhøjde og baggrund.
- Logo-størrelse/placering.
- Menu-farver og alignment.
- Mobilmenu/hamburger.

## CLEAN-FOOTER-027
**Prioritet: P1**

- Global Footer-model og versionshistorik.
- Responsive Desktop/Laptop/Mobil-varianter.
- Tekst, Logo, Menu, Links og Kasser/kolonner.
- Kontaktoplysninger/sociale links.
- Global designarv + lokale overrides.

---

# E. P1/P2 – Flere generelle elementer

## CLEAN-ELEMENT-BUTTON-028
- Knap med tekst/link.
- Baggrund, tekstfarve, border, radius, padding.
- Hover/focus styling.
- Intern/ekstern URL.

## CLEAN-ELEMENT-DIVIDER-029
- Skillelinje.
- Tykkelse, farve, bredde, alignment og afstand.

## CLEAN-ELEMENT-SPACER-030
- Kontrolleret tom afstand.
- Primært lodret, evt. responsiv størrelse.

## CLEAN-ELEMENT-ICON-031
- Ikon med størrelse/farve/link.
- Ingen afhængighed af tilfældige eksterne icon-CDN'er.

## CLEAN-ELEMENT-GALLERY-032
- Flere billeder.
- Grid/kolonner.
- Responsive kolonner.
- Lightbox senere hvis nødvendigt.

## CLEAN-ELEMENT-HERO-033
- Hero/topbanner.
- Billede/baggrund.
- Overlay.
- Tekst/overskrift/knap.
- Responsive højde og position.

## CLEAN-ELEMENT-MENU-034
- Menu som element, især til Header/Footer.
- WordPress menu source.
- Desktop og mobil præsentation.

## CLEAN-ELEMENT-FORM-035
- Kontaktformular som native Clean-element/modul.
- Spam-/nonce-beskyttelse.
- Feltdefinition og mailrouting.

---

# F. P1/P2 – Manager administration

## CLEAN-PAGES-036
- Udvid Sider-oversigten med version, ændringer og responsive status.
- Hurtig Preview af seneste version.
- Duplicate side via Manager.
- Eventuel arkiv/status-styring.

## CLEAN-MENU-037
- Nuværende menupunkt viser WordPress-menuer.
- Tilføj reel Manager-redigering af navigation.
- Versionering/backup af menuændringer.
- Preview før publicering hvis muligt.

## CLEAN-PROGRAM-BACKUP-038
- Vis alle programbackups i Manager.
- Version, dato, størrelse og SHA-256.
- Download backup.
- Sikker `Rollback til denne programversion`.
- Automatisk ny backup før rollback.
- Rollback må bevare plugin aktivt.

## CLEAN-SITE-BACKUP-039
- Eksisterende JSON Clean-backup beholdes.
- Tilføj Restore/import af Clean-backup.
- Dry-run før restore.
- Side-ID/slug konflikthåndtering.
- Global design/Header/Footer inkluderes når de findes.

## CLEAN-DIAGNOSTICS-040
- Gør diagnostics lettere at læse for administrator.
- Filtrering på Save, update, layout, frontend osv.
- Bevar redaction: ingen secrets/nonces/rå følsomme felter.

---

# G. P2 – Dynamiske Hangar18-moduler

## CLEAN-VEHICLES-041
- Rigtig Clean datamodel for køretøjer.
- Dynamiske køretøjsfelter.
- Aktiv/inaktiv feltstyring.
- Sortering af felter.
- Køretøjselement til Designer.
- Liste-/kortvisning.

## CLEAN-EVENTS-042
- Event-datamodel.
- Dato/tid/sted/billede/beskrivelse.
- Eventliste og eventkort som Designer-elementer.
- Arkiv/tidligere events.

## CLEAN-GALLERY-DATA-043
- Album/galleri-datamodel.
- Albumoversigt.
- Dynamisk galleri-element.
- Responsive billeder og lightbox.

## CLEAN-VEHICLE-FIELDS-044
- Portér funktionaliteten fra den gamle Manager som en ny Clean-model.
- Ingen legacy runtime må genaktiveres.

---

# H. P2 – Migration af eksisterende site

## CLEAN-MIGRATOR-045
**Blokeret indtil responsive + theme + QA er PASS**

- Læs gamle sider read-only.
- Konverter til Clean som kladde/kopi.
- Sammenlign gammel side og Clean-side side om side.
- Ingen automatisk overskrivning.
- Start med Hjem, Om, Kontakt og Bliv medlem.
- Derefter Køretøjer, Events og Galleri.

## CLEAN-VISUAL-PARITY-046
- Screenshot-/målebaseret sammenligning gammel ↔ Clean.
- Desktop, Laptop og Mobil.
- Header/banner/menu/content/footer.
- Accepterede tolerancer dokumenteres.

---

# I. P2/P3 – Avancerede funktioner

## CLEAN-LAYERS-047
- Frivillig Fri placering/Layer-mode.
- z-index.
- Bring forward/send backward.
- Bevidst overlap uden fejlstatus.
- Skal være tydeligt adskilt fra standard grid-mode.

## CLEAN-STYLES-048
- Gradienter.
- Baggrundsbilleder på Sektion/Kasse/Tekst.
- Skygger.
- Mere avancerede hover-effekter.
- Gemte style presets.

## CLEAN-COMPONENTS-049
- Genbrugelige globale komponenter.
- Fx CTA, medlemskort, kontaktblok.
- Opdater én komponent → valgfrit synkroniser instanser.

## CLEAN-TEMPLATES-050
- Side-skabeloner.
- Sektion-skabeloner.
- Gem eksisterende layout som skabelon.

---

# J. Tværgående QA før første egentlige Clean-live

Følgende skal være PASS før Clean bruges som primær sidebygger på det rigtige site:

1. Save/Reload giver samme canonical model.
2. Undo/Redo virker for Desktop, Laptop og Mobil.
3. Preview matcher frontend på alle tre breakpoints.
4. Sektion/Kasse-hierarki er låst og valideret.
5. Nested Kasser og auto-grow er stabile.
6. Tekstfarver, baggrund, border, radius og padding matcher frontend.
7. Billedboks og manuelt billedindhold er reelt uafhængige.
8. Ingen labels påvirker fysisk geometri.
9. Ingen utilsigtet vandret overflow.
10. Versioner viser ændringsbeskrivelser og Restore er ikke-destruktiv.
11. Programupdate tager verificeret backup og efterlader Manager aktivt.
12. Rollback testes, når rollback-UI er implementeret.
13. Global design og tema-shell giver samme visuelle resultat efter reload.
14. Header/side/footer overlapper ikke.
15. Keyboard/focus/kontrast/alt-tekst kontrolleres.
16. Side uden Clean-model fungerer fortsat via WordPress fallback.

---

# Anbefalet releaseplan

## 0.1.21 – Responsive fundament
- Desktop / Laptop / Mobil Designer.
- Canonical breakpoint-geometri og arv.
- Frontend breakpoints.
- Responsive Preview.

## 0.1.22 – Hierarki + layout QA
- Sektion kun root.
- Kasse nesting.
- Drop-regler.
- Overlap-policy.
- Auto-grow/celle-split regressionsfix.

## 0.1.23 – Globalt design
- Farver, typografi, sidebaggrund, bredder og defaults.
- Global design-versionering.

## 0.1.24 – Theme shell integration
- Hangar18 Base Theme kobles til globale Clean-designværdier.
- Desktop/Laptop/Mobil frontend-paritet.

## 0.1.25 – Header Designer
- Global Header + responsive layout + menu/logo/knap.

## 0.1.26 – Footer Designer
- Global Footer + responsive layout + links/kontakt/menu.

## 0.1.27 – Basale nye elementer
- Knap, Divider, Spacer og Ikon.

## 0.1.28 – Backup/rollback/import
- Programbackup-oversigt + rollback.
- Clean JSON restore/import.

## 0.1.29 – Gallery/Hero/Menu
- Galleri, Hero og Menu-element.

## 0.1.30 – General Clean QA / MVP gate
- Samlet QA af editor, responsive, versionsstyring, theme, Header/Footer og frontend.
- Kandidat til første generelle Clean-sidekonvertering.

## 0.2.x – Hangar18 datamoduler og migration
- Køretøjer.
- Køretøjsfelter.
- Events.
- Billedgalleri.
- Migrator.
- Visuel parity og side-for-side konvertering.

---

# Næste konkrete arbejde

1. Færdiggør og frigiv **0.1.21 Responsive**.
2. Test 0.1.20 → 0.1.21 self-update med automatisk programbackup.
3. Kør responsive QA på en side med Sektion + nested Kasse + Tekst + Billede.
4. Fortsæt derefter med **0.1.22 Hierarki/layout QA**.

Denne fil er den operative backlog fra Clean 0.1.20 og frem. `clean-backlog-v0100.md` bevares som historik over den oprindelige Clean-opbygning.