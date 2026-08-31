# Visual Designer Manager v0.1.x – canonical backlog

**Statusdato:** 31. august 2026  
**Aktuel release:** v0.1.70  
**Arkitekturgrænse:** `clean/hangar18-manager/`  
**Legacy-reference:** gammel Manager må bruges som read-only specifikation/migrationskilde; legacy editor-runtime må ikke blandes ind i Visual Designer Manager.

## Aktuel milepælsstatus · v0.1.70

- **HEADER/FOOTER — FÆRDIG:** multi-template, website-standarder, side-overrides, `Ingen`, migration, historik og fælles Preview/frontend-resolver er permanent regression-gate.
- **DESIGNER PRODUKTIVITET — IMPLEMENTERET:** keyboard nudge, clipboard/copy/paste/duplicate, sidekopi, Undo/Redo, versionshistorik og restore/kopi.
- **GENERELLE ELEMENTER — IMPLEMENTERET:** Tekst, Billede, Knap, Menu, Link, Mellemrum, Skillelinje, Ikon, Badge, Data List og Tabel inkl. tabelkanter.
- **VD-MODULE-DATA-001 — IMPLEMENTERET:** fælles ModuleRegistry, ModuleRecord, ModuleBinding og privat ModuleStore.
- **VD-CANVAS-SECTION-001 — IMPLEMENTERET:** Webside-root indeholder kun Sektioner; eksisterende Designer-sider migreres sikkert.
- **VD-SELECTION-LAYER-001 — IMPLEMENTERET:** selected/drag/resize løftes kun visuelt i editoren.
- **VD-CANVAS-AUTOHEIGHT-001 — IMPLEMENTERET I v0.1.69:** Webside/canvas vokser og krymper automatisk efter nederste root-Sektion.
- **VD-VEHICLE-MODULE-001 — IMPLEMENTERET I v0.1.70:** Køretøjer har Manager-CRUD, fleksible tekniske felter, billeder, sortering og Designer-list/detail-binding.

## Roadmap

1. **v0.1.69 – Canvas Auto Height — FÆRDIG.**
2. **v0.1.70 – Køretøjsmodul — FÆRDIG.**
3. **v0.1.71 – Events — NÆSTE:** CRUD på fælles ModuleStore, dato/tid, sted, status, automatisk kommende/afholdte visninger og Designer list/detail-elementer.
4. **v0.1.72 – Billedgalleri — PLANLAGT:** album, Media Library-referencer, sortering, cover og genbrugeligt Designer galleri/album-element.
5. **Efter modulerne:** samlet data-/module-migrering fra legacy, med side-by-side QA før cutover.

## Åben backlog

### VD-EVENT-MODULE-001 — NÆSTE
- Manager-CRUD på `events`-modulet.
- Start/slut, sted, kort/længere beskrivelse, status og billeder.
- Sortering samt kommende/afholdte regler uden at slette historiske events.
- Canonical Designer-elementer til Eventliste og Eventdetalje.
- Frontend må kun vise records efter den valgte status-/datoregel.

### VD-GALLERY-MODULE-001 — PLANLAGT
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

## Global release-gate

- PHP/JavaScript syntax QA skal være grøn.
- Historiske regression-gates fra Header/Footer, clipboard, generelle elementer, Module Foundation, Canvas/Section og Canvas Auto Height skal forblive grønne.
- Release-ZIP bygges kun af central `visual-designer-release.yml`, SHA-256 skrives til `clean-update.json`, og versionen anses først for frigivet efter successful workflow + manifestkontrol.
