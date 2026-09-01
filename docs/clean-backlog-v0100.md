# Visual Designer Manager v0.1.x – canonical backlog

**Statusdato:** 1. september 2026  
**Aktuel release:** v0.1.72  
**Arkitekturgrænse:** `clean/hangar18-manager/`  
**Legacy-reference:** gammel Manager må bruges som read-only specifikation/migrationskilde; legacy editor-runtime må ikke blandes ind i Visual Designer Manager.

## Aktuel milepælsstatus · v0.1.72

- **HEADER/FOOTER — FÆRDIG:** multi-template, website-standarder, side-overrides, `Ingen`, migration, historik og fælles Preview/frontend-resolver er permanent regression-gate.
- **DESIGNER PRODUKTIVITET — IMPLEMENTERET:** keyboard nudge, clipboard/copy/paste/duplicate, sidekopi, Undo/Redo, versionshistorik og restore/kopi.
- **GENERELLE ELEMENTER — IMPLEMENTERET:** Tekst, Billede, Knap, Menu, Link, Mellemrum, Skillelinje, Ikon, Badge, Data List og Tabel inkl. tabelkanter.
- **VD-MODULE-DATA-001 — IMPLEMENTERET:** fælles ModuleRegistry, ModuleRecord, ModuleBinding og privat ModuleStore.
- **VD-CANVAS-SECTION-001 — IMPLEMENTERET:** Webside-root indeholder kun Sektioner; eksisterende Designer-sider migreres sikkert.
- **VD-SELECTION-LAYER-001 — IMPLEMENTERET:** selected/drag/resize løftes kun visuelt i editoren.
- **VD-CANVAS-AUTOHEIGHT-001 — IMPLEMENTERET I v0.1.69:** Webside/canvas vokser og krymper automatisk efter nederste root-Sektion.
- **VD-VEHICLE-MODULE-001 — IMPLEMENTERET I v0.1.70:** Køretøjer har Manager-CRUD, fleksible tekniske felter, billeder, sortering og Designer-list/detail-binding.
- **VD-EVENT-MODULE-001 — IMPLEMENTERET I v0.1.71:** Events har Manager-CRUD, dato/tid, sted, billede, kommende/afholdte regler og Designer list/detail-binding.
- **VD-GALLERY-MODULE-001 — IMPLEMENTERET I v0.1.72:** Album har CRUD, cover, Media Library-liste og Designer oversigt/detail.
- **VD-SITE-DESIGN-HARMONY-001 — IMPLEMENTERET I v0.1.72:** de seks øvrige hovedsider harmoniseres sikkert med Hjem med backup og versionering.
- **VD-EVENT-MODULE-001 — IMPLEMENTERET I v0.1.71:** Events har Manager-CRUD, dato/tid, sted, billede, kommende/afholdte regler og Designer list/detail-binding.
- **VD-GALLERY-MODULE-001 — IMPLEMENTERET I v0.1.72:** Album har CRUD, cover, Media Library-liste og Designer oversigt/detail.
- **VD-SITE-DESIGN-HARMONY-001 — IMPLEMENTERET I v0.1.72:** de seks øvrige hovedsider harmoniseres sikkert med Hjem med backup og versionering.

## Roadmap

1. **v0.1.69 – Canvas Auto Height — FÆRDIG.**
2. **v0.1.70 – Køretøjsmodul — FÆRDIG.**
3. **v0.1.71 – Events — FÆRDIG:** CRUD på fælles ModuleStore, dato/tid, sted, status, automatisk kommende/afholdte visninger og Designer list/detail-elementer.
4. **v0.1.72 – Billedgalleri + site-design — FÆRDIG:** album, Media Library-referencer, sortering, cover, Designer oversigt/detail og sikker Hjem-baseret designharmonisering.
5. **v0.1.73 – Modul-cutover/migrering — NÆSTE:** samlet legacy data-/module-migrering med side-by-side QA før cutover.

## Åben backlog

### VD-EVENT-MODULE-001 — FÆRDIG I v0.1.71
- Manager-CRUD på `events`-modulet.
- Start/slut, sted, kort/længere beskrivelse, status og billeder.
- Sortering samt kommende/afholdte regler uden at slette historiske events.
- Canonical Designer-elementer til Eventliste og Eventdetalje.
- Frontend må kun vise records efter den valgte status-/datoregel.

### VD-GALLERY-MODULE-001 — FÆRDIG I v0.1.72
- Album-CRUD på `galleries`.
- Cover, beskrivelse og sorteret Media Library-liste.
- Designer-element til albumoversigt og albumvisning.
- Ingen billedbytes i layout-JSON eller module JSON; kun attachment IDs.

### CLEAN-RESPONSIVE-009 — DELVIST / MANUEL QA
- Canonical model har Desktop/Laptop/Tablet/Mobil geometri og arv.
- Desktop/Laptop/Mobil kan previewes i den nuværende viewport-runtime.
- Tablet skal have samme fulde, eksplicitte toolbar/preview-flow som de øvrige, før punktet lukkes.
- Breakpointændringer skal fortsat være Undo/Redo-sikre og må ikke mutere andre breakpoints.

### CLEAN-THEME-010 — IMPLEMENTERET BASELINE / REGRESSION FORTSÆTTER
- Theme shell og Header/Footer bruges på Visual Designer-sider.
- Banner, menu, farver, typografi og sitebredde skal fortsat regressionskontrolleres ved ændringer i fælles Designer/CSS.

### CLEAN-PREVIEW-013 — IMPLEMENTERET
- Ugemt canonical state kan previewes gennem samme PHP Renderer-kontrakt.
- Samlet preview kan vise Header + side + Footer uden at publicere.
- Admin-DOM klones ikke som frontend-kilde.

### CLEAN-MIGRATOR-014 — DELVIST / BLOKERET FOR MODULE-CUTOVER
- Eksisterende sidekonvertering er implementeret som ikke-destruktiv kandidat/QA-flow.
- Køretøjer, Events og Galleri migreres først, når de respektive nye moduler er færdige.
- Legacy-data læses read-only og originalen må ikke overskrives automatisk.

## v0.1.70 Køretøjsmodul – QA-gate

1. Opret et nyt køretøj som Kladde med primært billede, galleri og mindst tre tekniske felter.
2. Reload Manager og verificér identisk record, stabile field IDs og korrekt Media-ID-reference.
3. Redigér felt-navnet i Køretøjsfelter og verificér at recordets værdi stadig ligger under samme interne felt-ID.
4. Sæt record til Publiceret og opret mindst to yderligere publicerede records med forskellige sorteringsværdier.
5. Tilføj Køretøjsliste i Designer; test kolonner, sortering, vis/skjul billede/kategori/beskrivelse og kortdesign.
6. Opret en detaljeside med Køretøjsdetalje i “Fra URL”-tilstand og vælg den som detaljeside i listen.
7. Klik hvert listekort på frontend og verificér at `?h18_vehicle=<record-id>` viser korrekt record, billeder og tekniske data.
8. Sæt et record tilbage til Kladde/Arkiveret; det må ikke længere kunne vises offentligt via en direkte detail-URL.
9. Test et fast record-ID i Køretøjsdetalje Inspector.
10. Gem/reload/Undo/Redo Designer-sider med begge køretøjselementer og verificér canonical modelparitet.

## v0.1.71 Eventmodul – QA-gate

1. Opret Kladde med start/slut, sted, beskrivelse og billede; reload og verificér stabilt record-ID.
2. Publicér events før og efter aktuel dato og test Kommende, Afholdte og Alle publicerede.
3. Test startdato-sortering, Eventliste-design og genbrugelig Eventdetalje via `?h18_event=<record-id>`.
4. Kladde/Arkiveret må ikke kunne vises offentligt via direkte detail-URL.
5. Gem/reload/Undo/Redo begge eventelementer; historiske events må ikke slettes automatisk.

## Global release-gate

- PHP/JavaScript syntax QA skal være grøn.
- Historiske regression-gates fra Header/Footer, clipboard, generelle elementer, Module Foundation, Canvas/Section og Canvas Auto Height skal forblive grønne.
- Release-ZIP bygges kun af central `visual-designer-release.yml`, SHA-256 skrives til `clean-update.json`, og versionen anses først for frigivet efter successful workflow + manifestkontrol.


### VD-SITE-DESIGN-HARMONY-001 — FÆRDIG I v0.1.72
- Hjem er visuel reference; seks navngivne hovedsider er mål.
- Kun designprops ændres; indhold, hierarchy og geometri bevares byte-/fingerprint-logisk.
- Backup-meta + ny Designer-version fører til reversibel migration.

## v0.1.72 Billedgalleri/design – QA-gate
1. Opret et album som Kladde med cover, mindst 5 billeder og beskrivelse; reload og verificér stabile attachment-IDer.
2. Publicér mindst tre album og test sortering samt Gallerioversigt.
3. Test Albumvisning via `?h18_gallery=<record-id>`; Kladde/Arkiveret må ikke vises offentligt.
4. Verificér at albumdata kun indeholder attachment-IDer, ikke billedbytes.
5. Efter opdatering: verificér backup + ny Designer-version for hver målside der blev harmoniseret.
6. Sammenlign node-ID, hierarchy og Desktop/Laptop/Tablet/Mobil-geometri før/efter; de skal være identiske.
7. Vis alle seks sider og kontrollér visuelt samme farver, typografi, sektion/kasse-stil og knapper som Hjem.
