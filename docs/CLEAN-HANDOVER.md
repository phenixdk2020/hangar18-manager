# Hangar18 Manager Clean – Projekt-overdragelse

**Statusdato:** 25. august 2026  
**Aktuel frigivet version:** 0.1.21  
**Formål:** Denne fil er startpunktet for en ny ChatGPT-session eller udvikler, der skal overtage Hangar18 Manager Clean uden at kende den tidligere samtale.

---

## 1. Læs disse filer i denne rækkefølge

1. `docs/CLEAN-HANDOVER.md` – denne fil; aktuel status, aftaler, næste opgave og ikke-forhandlingsbare regler.
2. `CLEAN-DESIGN-MANUAL.md` – autoritativ design- og arkitekturmålmodel.
3. `docs/clean-backlog-v0120.md` – operativ backlog. Filnavnet siger v0.1.20, men den indeholder også senere godkendte forslag og skal læses sammen med denne handover.
4. `clean-update.json` – sandheden om senest frigivne version, package, SHA-256 og seneste changelog.
5. `clean-release-notes.html` – release-noter for den version, der er under opbygning/frigivelse.
6. `CLEAN-USER-MANUAL.md` – brugermanual/arbejdsbeskrivelse. Den er nyttig, men implementationsstatus i den kan være ældre end den aktuelle release. Brug ikke denne fil alene til at afgøre, hvad der er implementeret.
7. `DESIGN-MANUAL.md` – legacy/reference for historisk Hangar18-udseende og gamle designstandarder. Den gamle editor-runtime må ikke genindføres.

### Kildehierarki ved konflikt

1. Aktuel kode + `clean-update.json` afgør hvad der faktisk er implementeret.
2. `CLEAN-DESIGN-MANUAL.md` afgør godkendt målarkitektur.
3. `docs/clean-backlog-v0120.md` + denne handover afgør godkendte kommende funktioner og rækkefølge.
4. `CLEAN-USER-MANUAL.md` beskriver brugerflow, men kan være versionsmæssigt bagefter.
5. `DESIGN-MANUAL.md` er legacy/reference, ikke Clean canonical runtime.

---

## 2. Projektets hovedmål

Hangar18 Manager Clean skal være en modeldrevet, LEGO-lignende WordPress Designer, hvor sider bygges visuelt af sektioner, kasser og indholdselementer.

Målet er, at de eksisterende Hangar18-sider på sigt kan bygges 100 % med Clean Designer uden at indsætte gammel editor-HTML eller aktivere legacy runtime.

De gamle sider bruges derfor som en konkret **paritetstest**:

- Hvis en gammel side kan bygges korrekt med native Clean-elementer, er den del af Designerens kapacitet god nok.
- Hvis en gammel side kræver noget Clean ikke kan udtrykke, oprettes den manglende funktion/element i backloggen.
- Gamle live-sider må ikke overskrives automatisk. Konvertering skal først ske som kladde/kopi og sammenlignes visuelt.

---

## 3. Ikke-forhandlingsbare arkitekturregler

### Canonical model

- Én canonical JSON-model pr. WordPress-side.
- DOM er aldrig Save-kilde.
- Layoutmotoren bruger 120 vandrette units og 8 px lodret grid/snap.
- Elementer har `id`, `type`, `parentId`, `order`, `geometry` og `props`.
- Save, Preview, Undo/Redo, Restore og frontend skal rekonstruere samme model.

### Hierarki

Godkendt målarkitektur:

```text
SIDE
└── SEKTION
    ├── KASSE
    │   ├── TEKST
    │   ├── BILLEDE
    │   └── KASSE
    ├── TEKST
    └── BILLEDE
```

- Sektion skal kun ligge på root.
- Kasse må ligge i Sektion eller Kasse.
- Leaf-elementer må ligge i Sektion eller Kasse.
- Kasse må nestes.
- Sektion må ikke bruges som nested Kasse.
- Denne regel skal håndhæves endeligt i 0.1.22.

### Editor-chrome

- Labels/type/id/drag handles er editor-chrome og må aldrig tælle med i fysisk x/y/w/h.
- Grøn = selected/aktive resize-handles.
- Blå = hover/drop-kontekst.
- Rød = reel overlap-advarsel.
- Kasse/Sektion er wrappers og er ikke overlap mod egne børn.

### Styling

Fælles styling skal kunne rekonstrueres canonical:

- border width, default 0 px;
- border color;
- hjørneradius;
- baggrund hvor relevant;
- padding hvor relevant;
- Afstand X/Y;
- lokal størrelse/placering.

Hjørneradius er en fælles egenskab på Sektion, Kasse, Tekst og Billede.

---

## 4. Implementeret gennem 0.1.21

### Grundeditor

- Sektion, Kasse, Tekst og Billede.
- Drag-and-drop med Over / Under / Venstre / Højre / Ind i.
- Celle-split med row-span-lignende layouts.
- 8 resize-handles.
- Auto-grow for Kasse/Sektion.
- Undo/Redo som modeltransaktioner.
- Overlap-advarsel.
- Labels uden fysisk geometri.

### Tekst

- valgfri overskrift;
- H2–H6;
- brødtekst;
- alignment;
- baggrund/gennemsigtig;
- brødtekstfarve;
- separat overskriftsfarve;
- padding;
- border/radius/Afstand X/Y.

### Billede

Billede består af to forskellige lag:

1. ydre billedboks;
2. selve billedindholdet.

Implementeret:

- Media Library;
- contain / cover / original / stretch;
- vandret/lodret alignment;
- focal X/Y;
- boksbaggrund;
- border/radius;
- manuel billedtilstand;
- selve billedet kan flyttes og skaleres uafhængigt af boksen;
- manuel X/Y/bredde/højde gemmes i pixels, så billedet ikke automatisk vokser, når boksen gøres større;
- Lås proportioner er standard i manuel tilstand.

### Preview, Save og sideversioner

- usavet theme-accurate Preview;
- Gem & vis;
- Save-verifikation med digest;
- hver rigtig Gem opretter ny version;
- ændringsbeskrivelse er obligatorisk;
- historikken viser ændringen pr. version;
- Forhåndsvis historisk version;
- Gendan original opretter en ny version og sletter ikke historik;
- Opret kopi laver en ny WordPress-kladdeside med egen Clean-historik.

### Programupdate og backup

- GitHub update-manifest;
- SHA-256-verifikation;
- self-update;
- plugin skal forblive aktivt efter update;
- automatisk ZIP-programbackup før opdatering;
- update stoppes hvis backup ikke kan oprettes/verificeres;
- changelog/releaseændringer vises før update;
- næste backup-trin er UI med liste/download/rollback.

### Responsive 0.1.21

Designer og frontend har tre aktive visninger:

- Desktop;
- Laptop;
- Mobil.

Principper:

- element-ID, type, parent, order og indhold er fælles;
- geometri kan være forskellig pr. breakpoint;
- Laptop arver Desktop som standard;
- Mobil arver effektiv Laptop/Desktop som standard;
- lokal responsive geometri kan nulstilles til arv;
- Laptop frontend-breakpoint: op til 1180 px;
- Mobil frontend-breakpoint: op til 782 px;
- `tablet` er fortsat reserveret i modellen til en mulig senere særskilt Tablet-visning;
- responsive parent-højder følger børnene.

### Designer på mindre skærme

- Elementer-panelet kan foldes ind/ud;
- Inspector kan foldes ind/ud;
- `⇔ Mere canvas` folder begge sidepaneler;
- paneltilstand gemmes lokalt i browseren;
- arbejdsfladen er kompakteret på laptop;
- canonical 120-unit model ændres ikke af den visuelle fit-to-screen-opførsel.

Aktuel release skal verificeres i `clean-update.json` før videre arbejde.

---

## 5. Aftalt elementbibliotek

### Implementeret nu

- Sektion
- Kasse
- Tekst
- Billede

### Høj prioritet

- Knap
- Skillelinje / Divider
- Spacer / Afstand
- Ikon
- Tabel

### Derefter

- Galleri
- Hero / Topbanner
- Menu
- Formular
- Video
- Liste
- Citat
- Badge / Label
- Accordion / FAQ
- Tabs
- Slider / Carousel
- Embed
- Breadcrumbs
- Anker
- Sociale links
- Knaprække

### Card/Kort

Card/Kort bør først undersøges som **Kasse-preset/komponent**, ikke nødvendigvis som endnu en hårdkodet datatype.

---

## 6. Tabel-element – godkendt retning

Tabel er et rigtigt Designer-element og skal have to datatilstande.

### Manuel tabel

- opret/slet/flyt rækker og kolonner;
- valgfri header-række;
- valgfri første kolonne som row header;
- tekst/simple links i første version;
- senere kontrollerede celletyper som billede, ikon og knap.

### Dynamisk tabel

- datakilde kan fx være Køretøjer eller Events;
- hver kolonne bindes til et datafelt;
- filter, sortering og max antal poster;
- sideversion gemmer kun binding/filter/design, aldrig en kopi af alle dynamiske poster;
- formattering pr. kolonne bør understøtte fx dato, tal+enhed, pris, status-badge, link og thumbnail.

### Responsive tabel

Mobiltilstande:

1. vandret scroll;
2. skjul valgte kolonner;
3. stak hver række som label/value-kort.

Semantisk tabel skal bruge korrekt `table/thead/tbody/th` og `scope`.

---

## 7. Komponenter og presets – godkendt idé

Designer skal senere kunne gemme en bygget struktur som genbrugelig komponent/preset.

Eksempel:

```text
KASSE
├── BILLEDE
├── TEKST
└── KNAP
```

kan gemmes som fx `Køretøjskort`.

Planlagte modes:

- **Lokal kopi**: ny uafhængig kopi, der kan redigeres frit.
- **Global komponent**: instanser kan valgfrit være bundet til en central komponent, så ændring ét sted kan synkroniseres.

Dette må ikke forveksles med dynamiske data. En komponent er layout/design; Køretøj/Event er data.

---

## 8. Dataarkitektur – hovedregel

Data og design skal være adskilt.

Designer-modellen gemmer:

- reference til datakilde/post;
- filtre;
- sortering;
- feltbinding;
- præsentationsindstillinger.

Designer-modellen gemmer ikke en kopi af hele Køretøj/Event/Album-posten.

Hvis et køretøj eller event ændres centralt, skal alle dynamiske visninger automatisk vise de nye data uden at sidedesignet får en ny version.

Dynamiske dataobjekter bør senere få deres egen revisionshistorik, adskilt fra sidedesign-versioner.

---

## 9. Køretøjsdata – aftalt retning

### Faste basisfelter

- Navn
- Undertitel
- Aktiv/inaktiv
- Status
- Kategori
- Fabrikant
- Model
- Årgang
- Land
- Primært billede
- Galleri/albumrelation
- Beskrivelse
- Manuel sortering

### Dynamiske felter

Eksempler:

- Motor
- Effekt
- Vægt
- Længde
- Bredde
- Højde
- Topfart
- Besætning
- Brændstofkapacitet
- Bevæbning

Hvert dynamisk felt bør kunne definere:

- label;
- datatype;
- enhed;
- aktiv/inaktiv;
- sortering;
- vis på kort;
- vis på detaljeside;
- formattering.

Nye køretøjsfelter skal kunne oprettes uden at kode en ny plugin-version.

### Designer-visninger

Planlagte dynamiske elementer:

- Køretøjsoversigt / Køretøjsliste;
- Ét Køretøj;
- Køretøjsfelt / feltbinding;
- dynamisk Tabel kan også bruge køretøjsdata.

---

## 10. Events og datostyring – aftalt retning

Event skal mindst kunne have:

- Titel
- Startdato
- Starttid valgfri
- Slutdato valgfri
- Sluttid valgfri
- Heldagsevent
- Tidszone, normalt `Europe/Copenhagen`
- Lokation
- Adresse
- Beskrivelse
- Forsidebillede
- Galleri/albumrelation
- Tilmeldingsfrist valgfri
- Tilmeldingslink valgfri
- Fremhævet Ja/Nej
- Publicér fra valgfri
- Skjul efter valgfri
- Aktiv Ja/Nej

### Automatisk status

Status skal beregnes ved rendering ud fra aktuel tid, ikke kræve manuel ændring og ikke være afhængig af WP-Cron som eneste mekanisme.

Princip:

```text
Nu < start                   => Kommende
start <= Nu <= slut          => I gang
Nu > slut                    => Afsluttet
```

Hvis en sluttid mangler, skal en entydig regel defineres, fx slutningen af slutdatoen.

WP-Cron kan bruges til cache, mail/notifikation og oprydning, men eventstatus må ikke kun afhænge af et cron-job.

### Dynamiske eventvisninger

Planlagte elementer:

- Eventliste
- Eventkort
- Ét Event
- dynamisk Tabel med Events

Filtre bør kunne understøtte:

- kommende;
- i gang;
- tidligere;
- alle;
- periode/dato-interval;
- fremhævede;
- max antal;
- sortering stigende/faldende efter dato.

Et afsluttet event skal automatisk kunne forsvinde fra `Kommende` og dukke op i `Tidligere` uden manuel redigering.

---

## 11. Relationer mellem data

Aftalt many-to-many/relationsmodel:

- Køretøj ↔ Event;
- Event ↔ Galleri/Album;
- Køretøj ↔ Galleri/Album.

Eksempel:

Et Event kan markere hvilke køretøjer der deltager. Event-siden kan derefter vise `Køretøjer du kan opleve`, og et Køretøj kan vise kommende/tidligere events hvor det deltager.

Relationer skal bruge stabile ID-referencer, ikke navnetekst.

Sletning/inaktivering skal håndteres uden orphan-fejl.

---

## 12. Globalt design – planlagt

Globalt design skal have sin egen model og versionshistorik og senere være den primære kilde til:

- primær skrifttype;
- standard body color;
- standard heading color;
- sidebaggrund;
- Hangar18 palette;
- Desktop/Laptop/Mobil sidebredder;
- standard spacing;
- standard border/radius.

Lokale elementindstillinger må overskrive globale defaults.

---

## 13. Header og Footer – planlagt

Header og Footer er globale designs, ikke almindelige elementer på hver side.

De skal bruge samme grundlæggende LEGO/grid-motor og responsive model.

### Header

Planlagte elementer/funktioner:

- Logo
- Menu
- Tekst
- Knap
- Kasse
- Ikon
- sticky / ikke sticky
- baggrund
- højde
- menu-/tekstfarver
- logo size/alignment
- mobilmenu/hamburger

### Footer

Planlagte elementer/funktioner:

- Tekst
- Logo
- Menu
- Links
- Kasser/kolonner
- kontaktoplysninger
- sociale links

Header og Footer skal have separat global versionshistorik.

---

## 14. Theme-rollen

Hangar18 Base Theme skal gradvist blive en tynd WordPress runtime/shell.

Temaet skal primært håndtere:

- WordPress lifecycle/templates;
- hooks/wrappers;
- menuintegration;
- rendering/fallback omkring Managerens Header/Side/Footer.

Tema og Manager må ikke have to konkurrerende sæt visuelle sandheder.

---

## 15. Backups og rollback – aftalt retning

Programbackup før update er implementeret.

Mangler som UI/backlog:

- oversigt over programbackups;
- version;
- dato/tid;
- størrelse;
- SHA-256;
- download;
- `Rollback til denne version`;
- automatisk ny backup før rollback;
- rollback skal efterlade plugin aktivt.

Clean/site-backup skal senere understøtte Restore/import med dry-run og konflikthåndtering.

---

## 16. Konvertering af de gamle sider

Strategien er ændret fra kun at vente til alt er færdigt til også at bruge de gamle sider løbende som en **Designer capability audit**.

### Arbejdsform

1. Gør den aktuelle Designer-milepæl færdig.
2. Tag en gammel side read-only.
3. Forsøg at beskrive/rebygge den med native Clean-elementer.
4. Hvis noget ikke kan bygges, registreres det som et konkret hul i Designer/backlog.
5. Byg manglende generelle funktioner fremfor side-specifik hacks.
6. Lav Clean-versionen som kopi/kladde.
7. Sammenlign visuelt Desktop/Laptop/Mobil.
8. Overskriv aldrig den gamle live-side automatisk.

Første generelle kandidater er Hjem, Om, Kontakt og Bliv medlem. Køretøjer, Events og Galleri konverteres først rigtigt, når deres datamoduler er på plads.

### Forbudt migrationsgenvej

- Ingen gammel editor-runtime.
- Ingen stor `Imported HTML`-blok som permanent løsning, hvis siden burde kunne bygges af native Clean-elementer.
- Ingen side-specifik CSS som skjuler et hul i den generelle Designer, medmindre det eksplicit klassificeres som midlertidig migrationsteknik.

---

## 17. Næste konkrete opgave

Efter release 0.1.21 er næste hovedmilepæl:

### 0.1.22 – Hierarki + layout-QA

- håndhæv Sektion root-only;
- Kasse nesting;
- afvis ulovlige drops med tydelig feedback;
- QA celle-split i komplekse layouts;
- QA nested Kasser;
- QA auto-grow med border/padding/gap;
- QA labels;
- endelig standard-overlap-policy;
- regressionskontrol af Desktop/Laptop/Mobil.

Samtidig kan en gammel almindelig side bruges read-only som capability audit for at opdage manglende generelle elementer.

Efter 0.1.22 fortsætter den planlagte rækkefølge med Globalt design, theme-shell, Header/Footer og flere generelle elementer, med mulighed for at justere versionsnumre hvis nødvendige QA/fix-builds indsættes.

---

## 18. Release-procedure

- Bump pluginversion i Clean source.
- Opdatér release-notes/changelog.
- Brug eksisterende releaseworkflow/trigger (`clean-release-now.txt`).
- Workflow skal bestå `Verify clean source`.
- Workflow bygger versioneret ZIP.
- `clean-update.json` skal efter release vise korrekt version, package, source commit og SHA-256.
- En version må ikke omtales som frigivet før workflow er `success` og manifestet er verificeret.
- Self-update skal testes med den automatiske programbackup.

---

## 19. Ting en ny chat ikke må gøre

- Genaktivér ikke legacy 0.4.x/0.9.x editor-runtime.
- Brug ikke DOM som canonical Save-kilde.
- Lad ikke editor-labels ændre fysisk layout.
- Kopiér ikke dynamiske Køretøj/Event-data ind i sidedesign-versionen.
- Lav ikke destruktiv Restore der sletter historik.
- Omgå ikke update SHA-256 eller programbackup.
- Antag ikke at en version er frigivet uden at kontrollere `clean-update.json` og workflow.
- Konverter ikke gamle live-sider direkte uden kopi/preview/paritetstest.
- Løs ikke et generelt Designer-hul med en permanent side-specifik hack, hvis en generel funktion er den rigtige løsning.

---

## 20. Kendte dokumentationsforhold

- `CLEAN-USER-MANUAL.md` er en brugermanual, men står stadig med ældre versionsstatus og skal opdateres efter de seneste 0.1.20/0.1.21-funktioner.
- En Word-brugermanual med tabeller/illustrationer er tidligere genereret i samtalen. Den er ikke den tekniske source of truth og bør regenereres/opdateres fra Markdown-dokumentationen, når næste manualrevision laves.
- `docs/clean-backlog-v0120.md` er den operative backlog, selv om filnavnet indeholder 0.1.20.
- Denne handover skal opdateres, når en større arkitektur-, data- eller procesbeslutning godkendes.

---

## 21. Hurtig takeover-checkliste

En ny chat skal kunne starte med følgende:

1. Læs denne fil.
2. Læs `CLEAN-DESIGN-MANUAL.md`.
3. Læs `docs/clean-backlog-v0120.md`.
4. Læs `clean-update.json` og bekræft seneste release.
5. Fetch de aktuelle sourcefiler før enhver ændring.
6. Fortsæt fra `Næste konkrete opgave` ovenfor.
7. Opdatér dokumentation + release-notes sammen med kodeændringer.

Hvis disse trin følges, skal en ny chat ikke være afhængig af den tidligere samtale for at forstå projektets retning.