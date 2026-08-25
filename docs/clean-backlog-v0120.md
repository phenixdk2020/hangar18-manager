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

## CLEAN-ELEMENT-TABLE-032 – Tabel
**Prioritet: P1**

Tabel skal være et generelt element med to datatilstande:

### Manuel tabel
- Brugeren opretter selv kolonner og rækker.
- Valgfri overskriftsrække og første kolonne som rækkeoverskrift.
- Tilføj/slet/flyt rækker og kolonner.
- Celleindhold: tekst og simple links i første version.
- Senere evt. billede/ikon/knap i celler via kontrollerede celletyper.

### Dynamisk tabel
- Datakilde kan vælges, fx Køretøjer eller Events.
- Hver kolonne bindes til et datafelt.
- Eksempel Køretøjer: `Navn | Årgang | Vægt | Motor | Status`.
- Eksempel Events: `Dato | Event | Sted | Status`.
- Sortering, filtrering og maksimum antal rækker.
- Senere pagination/søgning for større datasæt.
- Dynamic table gemmer kun binding/filter/design i sideversionen, ikke en kopi af alle poster.

### Styling
- Header-baggrund og header-tekstfarve.
- Cellebaggrund/tekstfarve.
- Zebra-striber valgfrit.
- Border-tykkelse/farve.
- Radius på ydre tabelboks.
- Celle-padding.
- Kolonnebredder og alignment.
- Typografi fra Globalt design med lokale overrides.

### Responsive tabel
På Mobil kan brugeren vælge mellem:
1. **Vandret scroll** – tabelstrukturen bevares.
2. **Skjul kolonner** – udvalgte sekundære kolonner skjules på Laptop/Mobil.
3. **Stak som kort** – hver datarække vises lodret som et label/value-kort.

Tabel skal rendere semantisk HTML med `<table>`, `<thead>`, `<tbody>`, `<th>` og korrekte `scope`-relationer, når tabelformat anvendes.

## CLEAN-ELEMENT-GALLERY-033
- Flere billeder.
- Grid/kolonner.
- Responsive kolonner.
- Lightbox senere hvis nødvendigt.

## CLEAN-ELEMENT-HERO-034
- Hero/topbanner.
- Billede/baggrund.
- Overlay.
- Tekst/overskrift/knap.
- Responsive højde og position.

## CLEAN-ELEMENT-MENU-035
- Menu som element, især til Header/Footer.
- WordPress menu source.
- Desktop og mobil præsentation.

## CLEAN-ELEMENT-FORM-036
- Kontaktformular som native Clean-element/modul.
- Spam-/nonce-beskyttelse.
- Feltdefinition og mailrouting.

### Senere generelle elementer / komponenter
- Video.
- Liste.
- Citat.
- Badge/Label.
- Accordion/FAQ.
- Tabs.
- Slider/Carousel.
- Embed.
- Breadcrumbs.
- Anker.
- Sociale links.
- Knaprække.
- Card/Kort bør primært undersøges som Kasse-preset/komponent fremfor endnu en hårdkodet datatype.

---

# F. P1/P2 – Manager administration

## CLEAN-PAGES-037
- Udvid Sider-oversigten med version, ændringer og responsive status.
- Hurtig Preview af seneste version.
- Duplicate side via Manager.
- Eventuel arkiv/status-styring.

## CLEAN-MENU-038
- Nuværende menupunkt viser WordPress-menuer.
- Tilføj reel Manager-redigering af navigation.
- Versionering/backup af menuændringer.
- Preview før publicering hvis muligt.

## CLEAN-PROGRAM-BACKUP-039
- Vis alle programbackups i Manager.
- Version, dato, størrelse og SHA-256.
- Download backup.
- Sikker `Rollback til denne programversion`.
- Automatisk ny backup før rollback.
- Rollback må bevare plugin aktivt.

## CLEAN-SITE-BACKUP-040
- Eksisterende JSON Clean-backup beholdes.
- Tilføj Restore/import af Clean-backup.
- Dry-run før restore.
- Side-ID/slug konflikthåndtering.
- Global design/Header/Footer inkluderes når de findes.

## CLEAN-DIAGNOSTICS-041
- Gør diagnostics lettere at læse for administrator.
- Filtrering på Save, update, layout, frontend osv.
- Bevar redaction: ingen secrets/nonces/rå følsomme felter.

---

# G. P2 – Fælles dataarkitektur før dynamiske Hangar18-elementer

## CLEAN-DATA-ARCH-042 – Adskil data og design
**Prioritet: P2 · fundament for Køretøjer/Events/Galleri**

Hovedregel:

- Designer-modellen gemmer **reference, filter, feltbinding og præsentation**.
- Køretøjs-/Event-/Galleri-data gemmes i deres egne datamodeller.
- Sideversionen må ikke indeholde kopier af dynamiske dataposter.
- Rettes en datapost centralt, opdateres alle dynamiske visninger automatisk.
- Dataobjekter får på sigt egen revisionshistorik adskilt fra sidedesign-versioner.

Eksempel:

```text
Sideversion v8
└── Køretøjsliste
    ├── kilde = vehicles
    ├── filter = kategori:bæltekøretøj
    ├── sortering = navn
    └── felter = billede, navn, årgang
```

Siden gemmer ikke hele M113-/Centurion-posten.

## CLEAN-DATA-RELATIONS-043 – Relationer mellem data

- Køretøj ↔ Event er many-to-many.
- Event kan vælge deltagende køretøjer.
- Køretøj kan automatisk vise kommende/tidligere events, hvor køretøjet deltager.
- Event ↔ Album/Galleri relation.
- Køretøj ↔ Album/Galleri relation.
- Relationer skal være stabile ID-referencer, ikke navnetekst.
- Sletning/inaktivering skal håndtere relationer sikkert uden orphan-fejl.

---

# H. P2 – Køretøjsdata

## CLEAN-VEHICLES-044
**Prioritet: P2**

Rigtig Clean datamodel for køretøjer.

### Faste basisfelter
- Navn.
- Undertitel.
- Aktiv/inaktiv.
- Status, fx restaureret / under restaurering / opmagasineret.
- Kategori.
- Fabrikant.
- Model.
- Årgang.
- Land.
- Primært billede.
- Galleri/albumrelation.
- Beskrivelse.
- Manuel sortering.

### Dynamiske køretøjsfelter
Eksempler:
- Motor.
- Effekt.
- Vægt.
- Længde.
- Bredde.
- Højde.
- Topfart.
- Besætning.
- Brændstofkapacitet.
- Bevæbning.

Hvert felt skal kunne definere:
- label;
- datatype: tekst, lang tekst, tal, tal+enhed, ja/nej, dato, valg mv.;
- enhed;
- aktiv/inaktiv;
- sorteringsrækkefølge;
- vis på kort;
- vis på detalje;
- eventuel formattering.

## CLEAN-VEHICLE-FIELDS-045
- Portér den ønskede funktionalitet fra den gamle Manager som en ny Clean-model.
- Ingen legacy runtime må genaktiveres.
- Ændring af feltdefinition må ikke kræve ny plugin-version.
- Felt-ID skal være stabilt, selv hvis label omdøbes.

## Dynamiske Designer-elementer for køretøjer
Planlagte:
- **Køretøjsoversigt** – filtreret liste/grid/kort.
- **Køretøj** – et bestemt eller aktuelt køretøj.
- **Køretøjsfelt** – et bestemt felt fra aktuelt/valgt køretøj.
- **Tabel** med `Datakilde = Køretøjer` som alternativ præsentation.

---

# I. P2 – Events og datostyring

## CLEAN-EVENTS-046
**Prioritet: P2**

### Event-basisfelter
- Titel.
- Startdato.
- Starttid, valgfri.
- Slutdato, valgfri.
- Sluttid, valgfri.
- Heldagsevent.
- Tidszone, normalt WordPress site timezone / `Europe/Copenhagen`.
- Lokation/sted.
- Adresse.
- Beskrivelse.
- Primært billede.
- Galleri/albumrelation.
- Tilmeldingsfrist.
- Tilmeldingslink.
- Fremhævet ja/nej.
- Publicér fra, valgfri.
- Skjul efter, valgfri.
- Aktiv/inaktiv.
- Relation til deltagende køretøjer.

### Automatisk eventstatus
Status må ikke kræve manuel ændring:

```text
NU < start                         => Kommende
start <= NU <= slut                => I gang
NU > slut                          => Afsluttet
```

Hvis sluttid mangler, bruges en dokumenteret fallback, normalt slutningen af slutdatoen. Heldagsevents beregnes efter lokal site-tidszone.

Status beregnes ved dataforespørgsel/rendering og må **ikke være afhængig af WordPress Cron** for at skifte korrekt tidspunkt.

### Dato-/synlighedsregler
- Kommende events: start >= nu.
- Tidligere events: slut < nu.
- I gang: nu i start/slut-interval.
- Filter på dato-interval, fx kalenderår.
- Tilmeldingsfrist kan vises og bruges som status.
- `Publicér fra` kan styre frontend-synlighed.
- `Skjul efter` kan fjerne event fra standardlister uden at slette data.
- Historiske events bevares som data og kan vises i arkiv.

### Dynamiske Event-elementer
- **Eventliste** – fx kommende 6 events.
- **Eventkort** – card-visning.
- **Event** – et bestemt/aktuelt event.
- **Eventfelt** – et bestemt felt.
- **Tabel** med `Datakilde = Events`.

Eventliste-Inspector skal mindst kunne styre:
- kommende / i gang / tidligere / alle;
- fra/til dato;
- maksimum antal;
- sortering;
- kun fremhævede;
- eventuelle kategorier senere;
- synlige felter;
- datovisningsformat.

---

# J. P2 – Galleri-data

## CLEAN-GALLERY-DATA-047
- Album/galleri-datamodel.
- Albumoversigt.
- Dynamisk galleri-element.
- Responsive billeder og lightbox.
- Relation til Køretøj og Event.
- Et album kan genbruges flere steder uden at kopiere billederne til sideversionen.

---

# K. P2 – Migration af eksisterende site

## CLEAN-MIGRATOR-048
**Blokeret indtil responsive + theme + QA er PASS**

- Læs gamle sider read-only.
- Konverter til Clean som kladde/kopi.
- Sammenlign gammel side og Clean-side side om side.
- Ingen automatisk overskrivning.
- Start med Hjem, Om, Kontakt og Bliv medlem.
- Derefter Køretøjer, Events og Galleri.

## CLEAN-VISUAL-PARITY-049
- Screenshot-/målebaseret sammenligning gammel ↔ Clean.
- Desktop, Laptop og Mobil.
- Header/banner/menu/content/footer.
- Accepterede tolerancer dokumenteres.

---

# L. P2/P3 – Avancerede funktioner

## CLEAN-LAYERS-050
- Frivillig Fri placering/Layer-mode.
- z-index.
- Bring forward/send backward.
- Bevidst overlap uden fejlstatus.
- Skal være tydeligt adskilt fra standard grid-mode.

## CLEAN-STYLES-051
- Gradienter.
- Baggrundsbilleder på Sektion/Kasse/Tekst.
- Skygger.
- Mere avancerede hover-effekter.
- Gemte style presets.

## CLEAN-COMPONENTS-052 – Komponenter / presets
- Gem en Kasse med børn som genbrugelig komponent.
- Fx Køretøjskort, Eventkort, CTA, medlemskort og kontaktblok.
- **Lokal kopi:** uafhængig efter indsættelse.
- **Global komponent:** valgfri synkronisering til alle instanser.
- Versionering af globale komponenter.
- Beskyttelse mod rekursive komponentreferencer.

## CLEAN-TEMPLATES-053
- Side-skabeloner.
- Sektion-skabeloner.
- Gem eksisterende layout som skabelon.

---

# M. Tværgående QA før første egentlige Clean-live

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
17. Manuel tabel bevarer rækker/kolonner/cellestyles efter Save/Reload.
18. Dynamisk tabel viser aktuelle data uden at kopiere dataposter ind i sideversionen.
19. Mobil tabelstrategi giver ingen utilsigtet side-overflow.
20. Eventstatus skifter korrekt omkring start/slut uden cron-afhængighed.
21. Køretøj↔Event-relationer virker begge veje.

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
- Knap, Divider, Spacer, Ikon og **Tabel**.
- Tabel starter med manuel data + responsive visning; dynamiske datakilder kobles på efter dataarkitekturen.

## 0.1.28 – Backup/rollback/import
- Programbackup-oversigt + rollback.
- Clean JSON restore/import.

## 0.1.29 – Gallery/Hero/Menu
- Galleri, Hero og Menu-element.

## 0.1.30 – General Clean QA / MVP gate
- Samlet QA af editor, responsive, versionsstyring, theme, Header/Footer og frontend.
- Kandidat til første generelle Clean-sidekonvertering.

## 0.2.0 – Fælles dataarkitektur
- Data/design-adskillelse.
- Datakilde-kontrakt for dynamiske Designer-elementer.
- Relationer.
- Revisionsprincip for dataposter.

## 0.2.1 – Køretøjer + dynamiske felter
- Køretøjsdatamodel.
- Køretøjsfelter.
- Køretøjsoversigt/Køretøj/Køretøjsfelt.
- Dynamisk Tabel-kilde: Køretøjer.

## 0.2.2 – Events + datostyring
- Eventdatamodel.
- Automatisk Kommende/I gang/Afsluttet.
- Dato-/synlighedsregler.
- Eventliste/Event/Eventfelt.
- Køretøj↔Event relationer.
- Dynamisk Tabel-kilde: Events.

## 0.2.3 – Billedgalleri-data
- Albumdata.
- Relationer til Køretøjer/Events.
- Dynamiske galleri-visninger.

## 0.2.4+ – Migrator og visuel parity
- Migrator.
- Visuel parity.
- Side-for-side konvertering af det eksisterende site.

---

# Næste konkrete arbejde

1. Færdiggør og frigiv **0.1.21 Responsive**.
2. Test 0.1.20 → 0.1.21 self-update med automatisk programbackup.
3. Kør responsive QA på en side med Sektion + nested Kasse + Tekst + Billede.
4. Fortsæt derefter med **0.1.22 Hierarki/layout QA**.
5. Implementér Tabel som del af 0.1.27, først manuel og derefter dynamisk datakilde efter 0.2.0.
6. Byg Køretøjer/Events mod den fælles dataarkitektur i stedet for at hardkode dataposter i sideelementerne.

Denne fil er den operative backlog fra Clean 0.1.20 og frem. `clean-backlog-v0100.md` bevares som historik over den oprindelige Clean-opbygning.