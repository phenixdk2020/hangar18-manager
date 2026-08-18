=== Hangar18 Manager ===
Version: 0.5.30

Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.


== Version 0.5.25 – E5 Query Builder v1 ==

Nyt:
- UD-055: generisk Query Builder v1 for custom data med datatype, ét typevalideret filter, sortering, retning og limit
- text understøtter eq/neq/contains; number eq/neq/gt/gte/lt/lte; date eq/before/after; bool og media sikre equality-filtre
- sortering kan ske efter titel, oprettet, ændret eller kompatibelt schemafelt
- limit håndhæves server-side til 1–100 resultater
- admin-preview og frontend-shortcode bruger præcis samme run_custom_data_query()-motor
- frontend-shortcode [hangar18_data_query ...] viser kun publicerede data-entry-titler; drafts/private eksponeres ikke
- Query Builder bygger udelukkende WP_Query/get_posts-argumenter og query-klare _h18_field_<key> meta fra v0.5.23; ingen rå SQL
- generated shortcode vises efter preview, så samme query kan reproduceres på frontend
- page-editor schema forbliver 1.19
- advanced AND/OR, relation og pagination er fortsat UD-056; template-repeat pr. resultat er UD-057

== Version 0.5.24 – E5 Dynamic binding ==

Nyt:
- UD-053: hver Hangar18-side kan vælge en current data context som datatype + konkret entry
- elementegenskaber kan bindes til current context: Title, Content, MediaId og begge knappers tekst/link
- bindinger er typevaliderede: media kan kun drive billeder, links kun text fields, mens text/number/bool/date kan drive sikre tekstegenskaber
- static elementværdier ændres ikke og bruges som fallback, hvis context eller felt ikke længere findes
- runtime validerer altid datatype, entry og field-type igen; admin-UI er ikke sikkerhedsgrænsen
- canvas-preview bruger samme current context og viser også dynamiske WordPress-medier
- Bindings serialiseres med Patterns, linked component definitions og Page Templates uden at introducere ny delt identitet
- page-editor schema løftes bagudkompatibelt til 1.19
- foundation er klar til UD-057 Repeater/Query list, der senere kan skifte current context pr. resultat

== Version 0.5.23 – E5 Dynamic CMS foundation ==

Nyt:
- UD-051: generisk custom datatype schema builder under Hangar18 Manager → Data
- schemas understøtter text, number, bool, date og media fields med stabile keys, labels, required-flag og validering
- schema-struktur kræver manage_options; entry CRUD kræver edit_pages
- datatype-key er immutable efter oprettelse, og datatype-delete blokeres når entries stadig findes
- UD-052: generisk admin entry editor med create/read/update/delete for alle custom datatyper
- entries gemmes som privat Hangar18 custom post type med datatype-meta, samlet values-map og query-klare _h18_field_<key> meta-felter
- number/date/media valideres server-side; media skal pege på et rigtigt WordPress attachment
- media-felter bruger WordPress Media Library direkte i Data-editoren
- datamotoren er foundation for UD-053 dynamic binding og UD-055 Query Builder; Vehicle/Event/Gallery migreres senere via UD-060 presets, ikke via endnu en specialmotor
- page-editor schema forbliver 1.18; denne release ændrer ikke eksisterende side-JSON

== Version 0.5.22 – E4 Components completion ==

Nyt:
- UD-047: linked component variants deler base-definition og gemmer kun kontrollerede værdier for allerede frigivne component inputs
- variant anvendes før lokale instance-overrides, så lokale overrides fortsat har højeste prioritet
- variants oprettes/opdateres direkte fra en component-instance; variant med usage kan ikke slettes
- component revision stiger ved variantændringer, og global definition-update bevarer eksisterende variants
- UD-048: eksisterende presets er nu eksplicit Patterns og kan gemme/indsætte et helt nested subtree med friske keys og bevaret intern parent-struktur
- gamle én-sektions presets migreres transparent til subtree Pattern-format ved læsning
- Patterns forbliver ikke-linked og indeholder aldrig linked component-instanser eller legacy
- UD-049: Page Templates gemmer hele selvstændige sider og kan oprette nye draft WordPress/Hangar18-sider med friske section keys
- template-oprettede sider markeres som Hangar18-managed og bliver automatisk tilgængelige i sideeditorens sidevælger
- Page Template usage spores som origin-metadata til audit, men siden er en fri kopi; senere template-ændringer påvirker den ikke
- Page Templates afviser legacy og linked component-instanser for at garantere ingen skjulte shared-instance side effects
- page-editor schema løftes bagudkompatibelt til 1.18

== Version 0.5.21 – E4 linked component engine foundation ==

Nyt:
- UD-043: Navigator tree får separat lagnavn, rename, hide/show, lock/unlock og realtime reorder-beskyttelse
- låste lag kan ikke trækkes, skjules eller duplikeres ved et uheld i editoren
- UD-044: et valgt layout-subtree kan gemmes som en rigtig linked component med intern nesting bevaret
- linked components gemmes i separat versioneret WordPress-option; eksisterende presets bevares som ikke-linked Patterns
- UD-045: component-instanser gemmer kun ComponentId + lokale overrides og resolver altid den aktuelle globale definition ved render, så én atomisk option-opdatering propagere til alle instanser
- global definition har monotont Revision-nummer; instans-editor viser aktuel revision og usage
- UD-046: ved oprettelse/opdatering vælger designeren eksplicit hvilke Title/Content/Image/Button inputs der frigives; layout/design er ikke overridable lokalt
- risky Content inputs for CSS/HTML/Shortcode/Embed frigives ikke
- linked component kan ikke indeholde legacy eller andre linked components, så recursive component cycles er blokeret i foundation
- UD-050: usage inspector scanner alle gemte Hangar18-sider og viser side + section key; komponent med usage kan ikke slettes
- component-instanser har eget canvas-kort og indgår i responsive visibility/layout som én node
- page-editor schema løftes bagudkompatibelt til 1.17

== Version 0.5.20 – E3 Design System completion ==

Nyt:
- globale redigerbare builder-breakpoints med standard 782 px mobil og 1199 px tablet, så eksisterende sider bevarer nuværende responsive adfærd
- globale motion-tokens: Fast, Normal og Slow samt global focus-ring farve og bredde
- elementer kan vælge Transition: Global, Fast, Normal, Slow eller eksisterende Custom hover-transition
- Focus-state med global, tilpasset eller ingen focus ring samt farve, bredde og offset
- Active-state med Ingen, Tryk 1 px eller Scale 97% for interaktive descendants
- Disabled-state med justerbar opacity for disabled/aria-disabled kontroller
- live canvas og kommandopalette kan nu vise Normal, Hover, Focus, Aktiv og Disabled
- page-editor media queries bruger de globale breakpoints uden at ændre headerens eksisterende responsive legacy-regler
- prefers-reduced-motion bevares; motion-tokens ændrer ikke brugerens reducerede motion-præference
- DesignerSchemaVersion løftes kompatibelt til 1.1 og page-editor schema til 1.16

== Version 0.5.19 – Section/Container/Flex/Grid layout foundation ==

Nyt:
- UD-021–023 layoutfundament: Container, Flex container og Grid container som native builder-elementer
- elementer kan placeres inde i en layout-parent via LayoutParentKey, mens storage fortsat er en flad revisionsvenlig sektionsliste
- frontend omdanner den flade model til et ægte DOM-træ med op til tre niveauer
- server-side validering af parent-type, manglende parent, selvreference, cykler og maksimal dybde
- Flex: row/column, wrap, justify, align, desktop/mobile gap og valgfri mobil-stack
- Grid: 1-6 desktopkolonner, 1-3 mobilkolonner, align og separate gaps
- Canvas og Navigator indrykker children og viser antal under-elementer i layout-containere
- responsive section styling, hover, visibility og typografi virker også for nested children
- retter samtidig checkbox-semantik for Carousel loop/pile/prikker samt nye layout-checkboxes
- page-editor schema løftes bagudkompatibelt til 1.15

== Version 0.5.18 – Carousel / Slider ==

Nyt:
- UD-031: Carousel/Slider som native sideeditor-element og med den eksisterende Cards-model som slides
- autoplay er FRA som standard og kan aktiveres med justerbart interval 2-20 sekunder
- loop, forrige/næste-pile og priknavigation kan slås til/fra separat
- keyboard-navigation med venstre/højre pil samt Home/End på priknavigationen
- touch swipe på mobil og tablet; swipe kræver mindst ca. 45 px bevægelse
- autoplay pauser ved hover og keyboard-fokus og genstarter først, når brugeren forlader carousellen
- prefers-reduced-motion deaktiverer autoplay og transitions automatisk
- slides bruger role=group/aria-roledescription=slide, live status og skjuler inaktive slides fra fokus/assistive tech
- hvert slide bevarer Card-baggrund, teksttone, kant, padding, radius og responsive indstillinger
- page-editor schema løftes bagudkompatibelt til 1.14 for carousel-adfærd

== Version 0.5.17 – Tabs og Accordion ==

Nyt:
- UD-030: nye Faner/Tabs og Accordion-elementer direkte i sidebyggeren
- begge elementer genbruger den eksisterende Cards/panel-model, så komponenter, Undo/Redo, autosave og copy/paste fortsætter uden parallel datamodel
- Tabs har semantisk tablist/tab/tabpanel-markup, roving tabindex og tastaturstyring med pile, Home og End
- Accordion bruger native details/summary for robust keyboard- og skærmlæserunderstøttelse
- paneler kan flyttes, aktiveres/deaktiveres og beholder eksisterende baggrund, teksttone, kant, padding, radius og responsive Card-indstillinger
- nye Tabs/Accordion oprettes med to startpaneler og kan have op til 12 paneler
- live canvas viser den første fane eller det første accordion-panel uden at ændre frontend-state
- page-editor schema forbliver 1.13; ingen ekstra paneldatamigrering er nødvendig

== Version 0.5.16 – E2 element primitives og sikre embeds ==

Nyt:
- UD-028: sikkert Icon/SVG-element med indbygget allowlist-baseret ikonbibliotek uden rå bruger-SVG
- UD-029: nye semantiske elementer for skillelinje, liste, badge og citat
- Divider-varianter: hel, stiplet, prikket og dobbelt; List-varianter: punkter, numre og flueben
- Badge kan være fyldt/outline, og Quote kan være standard/stort citat
- UD-032: separat Embed-element via WordPress oEmbed og separat avanceret Shortcode-element
- Shortcode autoriseres kun ved gemning af brugere med unfiltered_html/manage_options; lavere roller kan ikke ændre eller indsætte ny eksekverbar shortcode
- eksisterende autoriseret shortcode kan bevares af lavere roller, når selve shortcode-indholdet er uændret
- importerede Gutenberg lister/citater/separatorer konverteres til de nye semantiske elementer
- HTML-elementet udfører ikke længere nye shortcodes implicit; eksplicit Shortcode-element er sikkerhedsgrænsen
- page-editor schema løftes bagudkompatibelt til 1.13

== Version 0.5.15 – Multi-select, canvas workspace og context menu ==

Nyt:
- UD-017: Ctrl/Cmd/Shift+klik kan vælge flere sideelementer samtidig i canvas og Navigator
- fælles kompatible egenskaber kan batch-redigeres: baggrund, placering, padding, radius, opacity og synlighed
- Inspector viser tydeligt antal valgte elementer og skjuler batchfelter, som ikke understøttes af alle valgte elementer
- UD-018: canvas zoom 50-150%, 100%-reset, Outline mode og 16 px Guides-grid
- workspace-indstillinger gemmes lokalt i browseren og ændrer aldrig frontend-output
- UD-019: højreklik eller Shift+F10 åbner en keyboard-tilgængelig context menu på canvas/Navigator
- context menu indeholder redigér, multivalg, duplikér, design copy/paste, komponent, vis/skjul, flyt og fjern
- context menu understøtter piletaster, Home/End, Enter/Space, Tab-loop og Escape
- page-editor schema forbliver 1.12; alle funktioner er editor-only

== Version 0.5.14 – Kommandopalette og hurtignavigation ==

Nyt:
- Ctrl/Cmd+K åbner en søgbar kommandopalette uden for aktive tekstfelter
- dynamiske Gå til element-kommandoer bygges fra sidens aktuelle sektioner, overskrifter og elementnøgler
- tilføj alle centrale elementtyper direkte fra paletten
- skift Desktop/Tablet/Mobil og Normal/Hover fra tastaturet
- Fortryd/Gendan, Kopiér/Indsæt design og Gem som komponent er tilgængelige som kommandoer
- Gem-kommandoen navigerer kun til ændringsbeskrivelsen og udfører aldrig en rigtig Gem automatisk
- Alt+Pil op/ned skifter mellem sideelementer uden at overtage genveje inde i tekstfelter
- Escape lukker, piletaster vælger, Enter udfører og Tab holdes inde i dialogen
- page-editor schema forbliver 1.12; funktionen er editor-only og ændrer ikke frontend-data

== Version 0.5.13 – Lokal autosave og crash recovery ==

Nyt:
- lokal browser-autosave af sideeditorens aktuelle recovery-state
- kladden gemmes pr. side og indeholder sideopbygning, Card Grid, design og aktuelle feltværdier
- Gendan kladde / Kassér kladde vises kun, når der faktisk findes en relevant recovery-state
- ældre kladder markeres tydeligt, hvis WordPress-siden er ændret siden kladden blev oprettet
- ingen kladde gendannes automatisk; restore kræver altid et aktivt klik
- autosave flusher ved skjult fane/pagehide og før browserens ugemte-ændringer-advarsel
- permanent Gem, WhatIf, WordPress-revisioner og JSON-backups er uændrede
- page-editor schema forbliver 1.12; ingen datamigrering er nødvendig

== Version 0.5.12 – Undo / Redo og sikker redigeringshistorik ==

Nyt:
- lokal Undo/Redo-historik med op til 50 trin
- Fortryd/Gendan-knapper og Ctrl/Cmd+Z samt Ctrl/Cmd+Shift+Z uden at overtage normal tekst-undo i inputfelter
- historikken dækker live canvas, sektioner, Card Grid og rækkefølge
- status for ugemte ændringer og browseradvarsel ved navigation
- hurtige ændringer flusher før Undo/Redo, og Card Grid i Inspector indgår i historikken
- page-editor schema forbliver 1.12; permanente revisioner og backups er uændrede


== Version 0.5.11 – Elementstørrelse og design-clipboard ==

Nyt:
- elementbredde kan styres separat for desktop, tablet og mobil
- tablet/mobil kan arve desktopbredde med -1
- max-bredde og minimumshøjde kan styres pr. element
- bredde og minimumshøjde kan justeres direkte fra live canvas
- image/text_image får separat billedbredde på desktop/tablet og mobil samt max-bredde
- valgt billedformat kan låses eller frigives; låst format styrer højden når formatet ikke er Auto
- Inspector får Kopiér design / Indsæt design uden at kopiere tekst, links, billeder eller elementnøgle
- design-clipboard gemmes lokalt i browseren og kan bruges mellem elementer/sider i editoren
- page-editor schema 1.12 med bagudkompatible standarder

== Version 0.5.10 – Billeder og box-model i live canvas ==

Nyt:
- klik på image/text_image direkte i canvas for billedkontroller; dobbeltklik åbner WordPress Media Library
- focal point kan trækkes direkte på billedet og gemmes som X/Y-procenter
- billedformat: Auto, 1:1, 4:3, 3:2 og 16:9
- object-fit kan vælges som Fyld/beskær eller Vis hele billedet
- separat billedhøjde for desktop/tablet og mobil; 0 bevarer automatisk højde
- margin top/bund får egne drag-handles, mens eksisterende padding-handles bevares
- valgt element viser en kompakt box-model overlay med margin- og padding-værdier
- page-editor schema 1.11 med bagudkompatible standarder: Auto, Cover, fokus 50/50 og 0 px højde

== Version 0.5.9 – Direkte Card Grid-redigering ==

Nyt:
- hvert kort i Card Grid kan vælges direkte i canvas
- kort kan omarrangeres direkte i canvas med drag-and-drop
- kortets overskrift og rich-text indhold kan redigeres med dobbeltklik
- valgt kort får egne hurtigkontroller for baggrund, teksttone, placering, padding, radius, kant og aktiv-status
- kortdesign følger desktop/mobil-felterne, som allerede fandtes i editorens datamodel
- Card Grid får direkte kontrol over antal kolonner og mellemrum, så kortbredden kan justeres visuelt
- valgt kort fremhæves samtidig i Inspector
- page-editor schema forbliver 1.10; ingen datamigrering er nødvendig


== Version 0.5.8 – Direkte canvas-kontroller ==

Nyt:
- brødtekst kan redigeres direkte som rich text i canvas med dobbeltklik
- Escape annullerer inline-redigering af overskrift/knaptekst
- valgt element får hurtigkontroller for padding, vandret padding, top/bundafstand, radius og opacity
- baggrund, tekst og overskriftsfarve kan vælges direkte fra canvas
- fire drag-handles ændrer indvendig lodret/vandret luft direkte på elementet
- kontrollerne følger Desktop/Tablet/Mobil og Normal/Hover
- page-editor schema forbliver 1.10; ingen eksisterende sidedata migreres


== Version 0.5.7 – Live visuel canvas ==

Nyt:
- midterfeltet i sideeditoren viser nu en live visuel gengivelse af sektionerne
- klik direkte på et element i canvas for at vælge det i Inspector
- Desktop, Tablet og Mobil bruger de faktiske responsive værdier i live preview
- Normal/Hover kan simuleres direkte i editorens toolbar
- designændringer i Inspector opdaterer canvas uden at siden først skal gemmes
- overskrifter og knaptekster kan redigeres direkte med dobbeltklik i canvas
- skjulte elementer forbliver synlige som redigerbare, nedtonede placeholders på det valgte device
- hero, tekst/billede, kort, formularer, afstemninger, spacer, HTML og øvrige sektionstyper har egne visuelle previews
- page-editor schema forbliver 1.10; v0.5.7 ændrer kun editorens visuelle arbejdslag og er derfor bagudkompatibel


== Version 0.5.6 – Normal/Hover states ==

Nyt:
- hover-state kan arve Normal eller have egne farver
- egen hover-baggrund, tekst, overskrift, kant og opacity
- tilpasset hover-baggrund er en solid state og erstatter gradient/billede under hover
- hover state kombineres med v0.5.4-bevægelse/skygge og v0.5.5-device transforms
- page-editor schema 1.10; standarden Arv Normal bevarer eksisterende design


== Version 0.5.5 – Responsiv elementstyring ==

Nyt:
- vis/skjul hvert element separat på desktop, tablet og mobil
- særskilt tablet-placering, luft og indvendig luft
- tablet kan arve desktop med Inherit/-1
- translate X/Y, scale og rotate separat for desktop, tablet og mobil
- eksisterende hover-effekter komponeres med de responsive transforms
- reduced-motion fjerner kun hover-bevægelsen og bevarer statiske transforms
- page-editor schema 1.9 med neutrale bagudkompatible standarder


== Version 0.5.4 – Avanceret visuelt elementdesign ==

Nyt i sideeditoren:
- opacity pr. sektion
- gradientbaggrund med start/slutfarve og vinkel
- baggrundsbillede fra WordPress Media Library eller URL
- baggrundsbilledets placering og skalering
- individuel radius for alle fire hjørner
- hover-effekter: løft, let zoom eller ekstra skygge
- justerbar hover-transition
- schema 1.8 med bagudkompatible standardværdier

Eksisterende sektioner beholder 100% opacity, ingen ekstra baggrundseffekt, deres eksisterende radius og ingen hover-effekt.

== Installation / opdatering ==

1. Tag gerne en WordPress-backup.
2. WordPress -> Plugins -> Tilføj plugin -> Upload plugin.
3. Upload den nyeste hangar18-manager.zip.
4. Hvis v0.1.0 allerede er installeret, vælg at erstatte den eksisterende version.
5. Aktivér Hangar18 Manager.
6. Åbn Hangar18 Manager i venstre wp-admin-menu.

== Sikkerhedsmodel ==

WhatIf / Sikker tilstand er FRA som standard i v0.3.2. Brugeren kan markere WhatIf manuelt for at simulere en write-operation.
Når WhatIf er markeret:
- ingen side oprettes
- ingen side opdateres
- ingen registerside genbygges

Ved rigtig skrivning oprettes automatiske JSON-backups og WordPress-revisioner, hvor det er muligt.

== Køretøjer ==

Hangar18 Manager -> Køretøjer

Funktioner:
- Nyt / eksisterende køretøj
- HANGAR18-VEHICLE-DATA
- hovedbillede
- tekniske data
- historik
- tjeneste ved Aalborg
- restaureringsstatus
- draft / publiceret
- Placering i køretøjsregister: Venstre / Midt, separat på desktop og mobil
- Indholdsjustering på køretøjssiden: Venstre / Midt, separat på desktop og mobil
- automatisk genbygning af Køretøjer og materiel

== Events ==

Hangar18 Manager -> Events

Funktioner:
- HANGAR18-EVENT-DATA
- dato, tid, sted, adresse, kontakt
- hovedbillede
- om arrangementet
- program
- praktiske oplysninger
- draft / publiceret
- Billedalbum-dropdown med publicerede gallerialbums
- eventet linker til albummet i stedet for at have eget galleri
- automatisk genbygning af Events-siden

== Billedgalleri ==

Hangar18 Manager -> Billedgalleri

Struktur:
Billedgalleri -> album -> billeder

Albumtyper:
- Køretøj
- Event
- Restaurering
- Foreningen
- Andet

Funktioner:
- HANGAR18-GALLERY-ALBUM-DATA
- vælg flere billeder fra Media Library
- drag-and-drop rækkefølge
- første billede bliver featured image / album-cover
- automatisk genbygning af Billedgalleri-indekset

== Sider ==

Hangar18 Manager -> Sider

Egen sektionseditor til Hjem, Om foreningen, Bliv medlem og Kontakt:
- nuværende Gutenberg- og HTML-indhold opdeles automatisk i redigerbare sektionskladder
- den offentlige side ændres først, når redaktøren vælger Gem siden
- vis, skjul, duplikér, fjern og drag-and-drop-sortér sektioner
- visuel sidebygger med elementpalette, sideopbygning og særskilt indstillingspanel
- topbanner/hero, tekst, tekst og billede, stort billede, handlingsknapper, indholdskort, kort-rækker, fremhævet tekst, afstand og importeret HTML
- kort-rækker med 1-4 desktopkolonner, 1-2 mobilkolonner og drag-and-drop-sortering af kasser
- individuel baggrund, automatisk tekstkontrast, kant, luft, afrunding og placering for hver kasse
- sikker opdeling af importerede WordPress-kolonner til redigerbare kasser
- separat placering, luft og indvendig luft på desktop og mobil
- editorvisning i desktop-, tablet- og mobilbredde
- billeder vælges fra WordPress Media Library
- header og footer ligger uden for editoren og kan ikke slettes her

Funktionsmoduler:
- Mailformular med modtager, bekræftelse, valgfri samtykketekst, spambegrænsning og testmail
- valgfri lagring af de seneste 200 henvendelser og CSV-eksport
- Afstemning med 2-20 svarmuligheder, enkelt/flere svar, start/slut, resultatvisning, nulstilling og CSV-eksport
- dobbeltstemmer begrænses uden lagring af rå IP-adresser
- dynamisk frontend-rendering, så modulrettelser gælder alle forekomster
- WhatIf-simulering, automatisk backup og WordPress-revision


== Menu ==

Hangar18 Manager -> Menu

Menu-manageren arbejder med WordPress' rigtige nav-menu-system og opdaterer
samtidig den statiske menu-HTML i Hangar18-headeren.

Funktioner:
- vælg eksisterende WordPress-menu
- opret "Hangar18 Hovedmenu", hvis ingen menu findes
- drag-and-drop rækkefølge
- redigér vist menunavn uden at ændre sidetitlen
- vælg "Undermenu under"
- fjern menupunkt
- tilføj publiceret WordPress-side
- dubletbeskyttelse ved tilføjelse
- status for Hjem og dubletter
- "Sikr standardmenu":
  Hjem
  Om foreningen
  Køretøjer og materiel
  Events
  Billedgalleri
  Bliv medlem
  Kontakt
- standardmenu-reparation tilføjer manglende standardsider
- dubletter af samme WordPress-side fjernes
- ukendte/manuelle menupunkter bevares
- valg af temaets menu-location
- aktiv Hangar18-menu gemmes centralt
- menuen anvendes automatisk på alle styrede Hangar18-sider
- desktop-undermenuer vises som dropdown
- mobil-undermenuer vises indrykket

Sikkerhed:
- WhatIf er markeret som standard
- menu-backup før ændringer
- samlet sidebackup før headeren opdateres
- checkpoints i web-loggen

== Header / Footer ==

Hangar18 Manager -> Header / Footer

Designstyring:
- Sticky header
- maksimal hjemmesidebredde
- header top/bund luft
- logo størrelse
- foreningsnavn størrelse
- menutekst størrelse
- placering af logo/navn: venstre/midt/højre
- placering af menu: venstre/midt/højre

"Gem og anvend design":
- gemmer centrale webmanager-indstillinger
- lægger et separat HANGAR18-WEB-OVERRIDE på alle styrede sider
- ændrer ikke den eksisterende Additional CSS

"Synkroniser header/footer":
- bruger Hjem som primær shell-kilde
- kopierer HANGAR18-HEADER, HANGAR18-SHELL-CSS og HANGAR18-FOOTER
- anvender dem på alle styrede hoved- og undersider
- laver samlet backup først

== Backup ==

Hangar18 Manager -> Backup

- automatisk backup før writes
- manuel samlet backup
- backupfiler:
  wp-content/uploads/hangar18-manager-backups/

== Log ==

Hangar18 Manager -> Log

Checkpoints for WhatIf, saves, registeropdateringer, shell/design og fejl.

== Intern lagring og kompatibilitet ==

v0.2.0 bruger fortsat:
HANGAR18-VEHICLE-DATA
HANGAR18-EVENT-DATA
HANGAR18-GALLERY-ALBUM-DATA

Web-manageren bruger fortsat de samme datamarkører på eksisterende sider.
Indstillinger gemmes centralt i WordPress, og JSON anvendes kun internt til konfiguration og backup.
Den tidligere automatiske PowerShell-import og baseline-genindlæsning er fjernet fra den aktive arbejdsgang i v0.4.15.

Bemærk: Versionsafsnittene nedenfor beskriver også historisk funktionalitet i ældre udgaver.


== Version 0.3.0 ==

Nyt:
- fuldt Menu-modul
- aktiv WordPress nav-menu
- drag-and-drop
- ændring af vist navn
- undermenu-parent
- fjern menupunkt
- tilføj side
- Hjem-kontrol
- dubletkontrol og reparation
- standardmenu-reparation
- theme location
- menu-backup
- automatisk Hangar18-header-synkronisering
- desktop/mobile submenu CSS

Alle funktioner fra v0.2.0 er bevaret.


== Version 0.3.1 – 1:1 Configuration Sync ==

Denne version fjerner de selvstændige web-defaults som autoritativ
designkilde.

Ved første wp-admin-load efter opgraderingen forsøger pluginet automatisk
at læse den private WordPress-side:

hangar18-configuration-store

Den er den samme centrale store som PowerShell Manager v2.0.39 bruger.

Følgende filer importeres og SHA-256-valideres:
- Hangar18-HeaderDesign.json
- Hangar18-MenuOrder.json
- Hangar18-VehicleRegister.json

HeaderDesign:
- fuld schema 2.5
- alle felter er med i web-GUI
- samme valideringsgrænser og effektive normaliseringsregler som
  PowerShell v2.0.39
- Identity 100% bruger samme 0.70 identity-base
- VisualBaseScalePercent er med
- responsive fluid font/logo/menu sizing er porteret
- StickyOnScroll er separat fra PositionMode
- den aktuelle v2.0.39 site-width-runtime bevares præcist:
  min(100vw,calc(50vw + 700px))

VehicleRegister:
- schema 1.2
- CardAlignment er global Left/Center
- DetailAlignment er global Left/Center/Auto
- dette erstatter v0.3.0's fejlagtige per-køretøj-layoutmodel

MenuOrder:
- schema 2.0
- Menu-reparation bruger den importerede centrale rækkefølge og Included
- ændringer i WordPress-menuen publiceres tilbage som Hangar18-MenuOrder.json

To-vejs config sync:
Når web-manageren laver en RIGTIG ændring i HeaderDesign,
VehicleRegister eller MenuOrder:
1. lokal WordPress web-option opdateres
2. central hangar18-configuration-store opdateres
3. Base64 manifest schema 1.0 bevares
4. ContentBase64, SHA-256 og Length genereres
5. konfigurationsfilbytes gemmes med UTF-8 BOM for kompatibilitet med
   Windows PowerShell 5.1
6. PowerShell Manager kan hente ændringen igen via sin eksisterende
   CONFIG_SYNC-funktion

Manuel knap:
Header / Footer -> Genindlæs alle settings 1:1 fra central
PowerShell-konfiguration.

Installation af v0.3.1 ændrer ikke frontend automatisk.
Importen ændrer kun web-managerens indlæste settings.
Frontend ændres først, når en write-funktion køres med WhatIf slået FRA.


== Version 0.3.2 ==

Rettet efter test af v0.3.1:

1. Manglende hangar18-configuration-store er ikke længere en fejl.
   Hvis den private Configuration Store ikke findes:
   - web-manageren læser den eksisterende Hangar18 live-header/shell
   - udleder de settings der kan læses direkte fra headerens classes/style/runtime
   - bruger projektets kendte v2.0.39 baseline for de settings der ikke kan
     reverseres entydigt fra genereret CSS
   - læser eksisterende WordPress-menu til Hangar18-MenuOrder.json
   - bruger det globale PowerShell VehicleRegister schema 1.2
   - opretter automatisk den private WordPress-side:
     hangar18-configuration-store
   - skriver alle tre configfiler i manifest schema 1.0 med Base64, SHA-256,
     længde og UTF-8 BOM
   - fremtidig web/PowerShell config sync kan derefter bruge samme store

2. WhatIf er FRA som standard.
   Alle WhatIf-checkboxes er umarkerede ved åbning.
   WhatIf-funktionen er stadig fuldt bevaret og kan slås til manuelt.

3. Frontend ændres IKKE alene fordi Configuration Store bootstrapper.
   Bootstrap opretter/synkroniserer kun central konfiguration.
   Frontend ændres fortsat kun ved de konkrete save/apply-handlinger.

Ny log:
CONFIG_STORE_BOOTSTRAP_SUCCESS


== Version 0.4.0 – GitHub Updater ==

Nyt modul:
Hangar18 Manager -> Opdateringer

Standard repository:
phenixdk2020/hangar18-manager

Standard branch:
main

Standard manifest:
update.json

Standard package:
dist/hangar18-manager.zip

Updater flow:
1. hent update.json fra GitHub Contents API
2. valider schema/version/plugin-id
3. sammenlign version med installeret version
4. kontroller minimum WordPress/PHP
5. ved manuel update:
   - samlet Hangar18 data-backup
   - ZIP-backup af den installerede plugin-kode
   - download update-ZIP fra GitHub Contents API
   - SHA-256 kontrol
   - WordPress Plugin_Upgrader overwrite
   - genaktivering
   - verifikation af versionsnummer i installeret hovedfil
6. ved fejl:
   - log UPDATE_FAILED
   - automatisk rollback fra plugin-kodebackup
   - log rollback-resultat

Privat GitHub repository:
Token gemmes IKKE i WordPress-databasen.
Sæt i wp-config.php:

define('HANGAR18_GITHUB_TOKEN', 'github_pat_...');

Token behøver Contents: Read til repository.

Automatisk versionscheck:
- standard hver 6. time
- kan slås fra
- installation er fortsat manuel i v0.4.0

Update manifest eksempel:

{
  "schema_version": "1.0",
  "plugin": "hangar18-manager",
  "version": "0.4.1",
  "min_wp": "6.4",
  "min_php": "8.0",
  "published_utc": "2026-08-13T20:00:00Z",
  "package_path": "dist/hangar18-manager.zip",
  "package_sha256": "<64 hex characters>",
  "changelog": [
    "Rettelse 1",
    "Ny funktion 2"
  ]
}

Checkpoints:
UPDATE_CHECK_SUCCESS
UPDATE_CHECK_FAILED
UPDATE_SETTINGS_SAVED
UPDATE_START
UPDATE_CODE_BACKUP_SUCCESS
UPDATE_PACKAGE_VERIFIED
UPDATE_SUCCESS
UPDATE_FAILED
UPDATE_ROLLBACK_START
UPDATE_ROLLBACK_SUCCESS
UPDATE_ROLLBACK_FAILED

GitHub repository skal indeholde:
hangar18-manager.php
assets/admin.js
assets/admin.css
readme.txt
update.json
dist/hangar18-manager.zip


== Version 0.4.1 – Authoritative uploaded configuration baseline ==

Denne version korrigerer tidligere antagelser om konfigurationsschemaerne.

Autoritative filer er de tre JSON-filer leveret 2026-08-13:

Hangar18-HeaderDesign.json
- Version 2.3
- VisualBaseScalePercent 90
- MenuAlignment Right
- PositionMode Normal
- StickyOnScroll false
- BackgroundMode None
- WidthMode Contained
- ShowBrand true
- IdentityAlignment Center
- BrandFontSize 22
- BrandSizePercent 100
- ShowLogo false
- LogoWidthPx 52
- LogoSizePercent 100
- MobileStyle Dark
- MenuFontSize 15
- MenuSizePercent 100
- MenuFontFamily Segoe UI
- MenuFontWeight Semibold
- ResponsiveLargeWidthPx 2560
- ResponsiveLaptopWidthPx 1920
- ResponsiveLaptopScalePercent 90
- ResponsiveMinimumScalePercent 90
- DesktopContentWidthPercent 80
- LaptopContentWidthPercent 90
- MaximumDesktopContentWidthPercent 90
- ContentMaxWidth None
- FooterWidthPercent 100

Hangar18-MenuOrder.json
- Version 1.0
- Order:
  1. hjem
  2. koeretoejer-og-materiel
  3. events
  4. billedgalleri
  5. bliv-medlem
  6. kontakt
  7. om-foreningen

Hangar18-VehicleRegister.json
- Version 1.2
- CardAlignment Center
- DetailAlignment Auto

Migration:
På første wp-admin-load efter opgradering til 0.4.1 anvendes denne
autoritative baseline én gang på plugin-options og den centrale
Configuration Store.

Migrationen ændrer IKKE frontend automatisk.
Frontend ændres først ved en konkret Save/Apply/Sync-handling.

Tidligere web-schema MenuOrder 2.0/Items understøttes som input og
konverteres tilbage til det autoritative schema 1.0/Order.

Tidligere HeaderDesign-opgraderinger til schema 2.5 udføres ikke længere.
Web-manageren bevarer schema 2.3 som autoritativt schema.

Checkpoint:
AUTHORITATIVE_BASELINE_APPLIED
AUTHORITATIVE_BASELINE_FAILED


== Version 0.4.2 – GitHub updater diagnostics ==

- Forbedret 404-diagnostik.
- Public repository fungerer uden GitHub-token.
- Privat repository kan fortsat bruge HANGAR18_GITHUB_TOKEN i wp-config.php.
- Opdateringssiden viser adgangstilstand: PUBLIC eller TOKEN.
- Den autoritative PowerShell-konfigurationsbaseline fra v0.4.1 er uændret.
- WhatIf er fortsat FRA som standard.


== Version 0.4.3 – Event/galleri-placering og menu-pinning ==

- Events har nu global placering: Venstre eller Midtstillet.
- Eventplaceringen anvendes på både eventoversigt og eventdetaljer.
- Billedgalleri har nu global placering: Venstre eller Midtstillet.
- Galleriplaceringen anvendes på både albumoversigt og albumsider.
- Ny central Hangar18-ContentLayout.json schema 1.0.
- Menu-siden har nu en tydelig "Pin menu/header ved scroll"-funktion.
- Pinning synkroniserer StickyOnScroll i Hangar18-HeaderDesign.json.
- Web-override indeholder sticky CSS-fallback med korrekt WordPress admin-bar offset.
- Layoutændringer tager fuld backup før eksisterende sider genbygges.
- WhatIf er fortsat FRA som standard.


== Version 0.4.4 – Separate oversigts- og detaljeplaceringer ==

- Køretøjer har nu to uafhængige valg: Køretøjer og materiel-oversigten samt de enkelte køretøjssider.
- Events har nu to uafhængige valg: eventoversigten samt de enkelte eventsider.
- Billedgalleri har nu to uafhængige valg: gallerioversigten samt de enkelte albumsider.
- Alle seks valg er Venstre eller Midtstillet.
- Hangar18-VehicleRegister.json er opgraderet til schema 1.3 og bevarer CardAlignment som legacy-alias.
- Hangar18-ContentLayout.json er opgraderet til schema 1.1.
- Eksisterende v0.4.3 EventAlignment/GalleryAlignment migreres automatisk til begge nye valg.
- Eksisterende Vehicle DetailAlignment=Auto migreres til Center for at bevare desktop-udseendet.
- WhatIf er fortsat FRA som standard.


== Version 0.4.5 – Frontend layoutfix ==

- Fjerner Astra/WordPress' native sidetitel og reserverede topafstand på Hangar18-styrede sider.
- Retter det blå/lilla titel-felt over Hangar18-headeren på Køretøjer, Events og Billedgalleri.
- Events detaljesider respekterer nu reelt Venstre/Midtstillet for hele indholdscontaineren.
- Billedgalleri-albums respekterer nu reelt Venstre/Midtstillet for selve billedgrid'et.
- Køretøjsdetaljer respekterer nu reelt Venstre/Midtstillet for hele detaljeindholdet.
- Eventbilleder er gendannet på Events-oversigten.
- Eventdetaljer bruger featured image som fallback, hvis ældre marker-data mangler MainMediaId.
- Header-knapper omdøbt til tydeligere funktioner.


== Version 0.4.6 – køretøj/galleri frontend-fix ==

- Events er bevidst ikke ændret i denne version.
- Astra/WordPress' native blå/lilla sidetitelbjælke fjernes via wp_head på Hangar18-styrede sider.
- Native entry-title/page-header/advanced-header wrappers får nul højde og ingen margin/padding.
- Køretøjsdetaljer bruger eksplicit h18-align-left/h18-align-center og fuld genbygning ved layoutændring.
- Gutenberg-klassen has-text-align-center fjernes fra køretøjernes leadtekst.
- Gallerialbums bruger eksplicit h18-align-left/h18-align-center på selve billedgrid'et.
- Første wp-admin-side efter opdatering genbygger automatisk køretøjer, køretøjsoversigt, gallerialbums og gallerioversigt.


== Version 0.4.7 – Astra Banner Area ==

- Den resterende lilla/blå bjælke er identificeret som Astra 4.x Banner Area.
- Hangar18 bruger nu Astra's egne frontend-filtre til at deaktivere banner/title-området.
- astra_apply_hero_header_banner sættes false på Hangar18-styrede sider.
- astra_remove_entry_header_content sættes true.
- astra_single_layout_one_banner_visibility sættes false.
- astra_the_title_enabled og astra_advanced_header_title deaktiveres.
- Astra-meta site-post-title, ast-title-bar-display og ast-banner-title-visibility sættes til disabled på styrede sider én gang efter opdatering.
- Ekstra CSS fallback dækker .ast-single-entry-banner og relaterede Astra 4 selectors.
- Events, køretøjer, billedgalleri og deres layoutdata ændres ikke.
- Oversigtssiderne får egne Hangar18-overskrifter: Køretøjer og materiel, Events og Billedgalleri.
- Overskrifterne følger oversigtssidens Venstre/Midtstillet-indstilling.


== Version 0.4.8 – Dynamiske køretøjsfelter ==

- Ny undermenu: Hangar18 Manager -> Køretøjsfelter.
- Tekniske køretøjsfelter kan aktiveres/deaktiveres, omdøbes, flyttes og fjernes fra opsætningen.
- Hvert felt har separat valg for visning på køretøjsoversigten og på den enkelte køretøjsside.
- Nye felter kan tilføjes uden kodeændring.
- Felttyper: kort tekst, lang tekst, tal, ja/nej, dropdown, dato, URL og farvevælger.
- Standardfeltet Farve er oprettet som inaktivt felt og kan aktiveres med ét klik.
- Eksisterende feltværdier slettes ikke, når et felt deaktiveres eller fjernes.
- Eksisterende legacy-felter migreres logisk til CustomFields og spejles fortsat til de gamle nøgler for bagudkompatibilitet.
- Ny central konfigurationsfil: Hangar18-VehicleFields.json schema 1.0.
- Gem af feltopsætning tager backup og genbygger alle køretøjssider samt køretøjsoversigten.


== Version 0.4.9 – Køretøjets billede og tekniske data ==

- Køretøjets detaljeside bruger nu sit eget eksplicitte layout og er ikke afhængig af Astra eller WordPress' blok-CSS.
- På computer står hovedbilledet fast i venstre kolonne og Tekniske data i højre kolonne.
- På mobil stables billedet øverst og Tekniske data nedenunder.
- Venstre/Midtstillet-indstillingen styrer fortsat placeringen af det samlede detaljeindhold.
- Alle eksisterende køretøjssider genbygges automatisk én gang efter opdateringen.


== Version 0.4.10 – Korrekt sidebredde og topplacering ==

- Header, sideindhold og footer bruger nu de gemte Desktop/Laptop-bredder i stedet for den gamle faste v2.0.39-formel.
- MaximumDesktopContentWidthPercent kan ikke længere gøre desktopbredden mindre end DesktopContentWidthPercent.
- Med DesktopContentWidthPercent 90 og MaximumDesktopContentWidthPercent 88 bliver den effektive maksimumsbredde derfor 90 procent.
- På mobil bruges fortsat 100 procent bredde.
- Headeren nulstilles målrettet til 0 topmargin og 0 toppadding på Hangar18 Base Theme og Astra.


== Version 0.4.11 – Sektionsafstand og galleri-skabelonfix ==

- Nye HeaderDesign-felter styrer afstanden mellem sidens hovedsektioner separat på desktop og mobil.
- Astra-lignende standardafstand er 32 px på desktop og 24 px på mobil.
- Første synlige sektion får ingen ekstra topafstand, så headerens placering helt oppe bevares.
- Gamle Astra-sideskabeloner fjernes automatisk fra alle Hangar18-styrede sider og den private Configuration Store én gang efter opdateringen.
- Gallerialbums og Billedgalleri-oversigten gemmes eksplicit med Hangar18 Base Themes standardskabelon.
- Fejlen "Ugyldig sideskabelon" ved gemning af billedgalleri er dermed rettet.
- HeaderDesign kan igen publiceres til Configuration Store uden fejlen "Ugyldig sideskabelon".


== Version 0.4.12 – Header starter ved 0 px for indloggede brugere ==

- Fjerner WordPress' resterende 32 px desktopafstand og 46 px mobilafstand, når admin-baren er skjult.
- En afsluttende CSS-regel i footeren sikrer, at senere WordPress- eller blok-CSS ikke kan flytte headeren ned.
- Headerens top, margin-top og sticky-position fastholdes på 0 px.
- Indstillingen for sektionsafstand påvirker fortsat kun sektionerne inde i indholdsrammen.


== Version 0.4.13 – Styrbar luft omkring sideindholdet ==

- Fire nye HeaderDesign-felter styrer luften fra header til indhold og fra indhold til footer separat på desktop og mobil.
- Standardafstanden er 32 px på desktop og 24 px på mobil.
- Afstanden oprettes som indvendig luft i indholdsrammen, så headeren fortsat starter ved 0 px.
- Den eksisterende sektionsafstand styrer fortsat afstanden mellem indholdets hovedsektioner.


== Version 0.4.14 – Mobilplacering for Events og Billedgalleri ==

- Events har nu separate indstillinger for placering af oversigt og detaljesider på desktop og mobil.
- Billedgalleri har nu separate indstillinger for placering af albumoversigt og billeder i albums på desktop og mobil.
- Mobilstandard er Midtstillet for alle fire visninger; desktopindstillingerne bevares uændret.
- Eksisterende events, albumsider og oversigter genbygges automatisk én gang efter opdateringen.
- Hangar18-ContentLayout.json er opgraderet fra schema 1.1 til 1.2.


== Version 0.4.15 – Oprydning og mobilplacering for køretøjer ==

- Fjerner den gamle PowerShell-import, baseline-genindlæsning, importstatus og importknap fra den aktive web-manager.
- Bevarer den private centrale WordPress-konfiguration og JSON-backups, fordi de bruges til sikker lagring og gendannelse.
- Forenkler administrationssiderne, så tekniske JSON-filnavne og schemanumre ikke vises i den normale arbejdsgang.
- Køretøjsoversigten og de enkelte køretøjssider får separate placeringer på desktop og mobil.
- Mobilstandard er Midtstillet, og eksisterende køretøjssider genbygges automatisk én gang efter opdateringen.
- Den interne køretøjslayout-konfiguration er opgraderet fra schema 1.3 til 1.4.


== Version 0.4.16 – Ensartede layouts og knapforklaringer ==

- Samler layoutindstillinger for Køretøjer, Events og Billedgalleri i ens kort med tydelige Desktop- og Mobil-sektioner.
- Holder relaterede felter i faste kolonner og tilpasser dem automatisk til tablet og mobil.
- Giver layout-, gemme- og reparationsknapper synlige forklaringer om hvad de gør, og hvornår de skal bruges.
- Forklarer WhatIf som en frivillig simulering, der ikke gemmer eller ændrer sider.
- Gør handlingslinjerne ens på Køretøjer, Køretøjsfelter, Events, Billedgalleri, Menu, Header/Footer, Opdateringer og Backup.


== Version 0.4.17 – Sideindhold og designmanual ==

- Tilføjer modulet Sideindhold til styring af indholdssektioner på Om foreningen.
- Sektioner kan vises, skjules, tilføjes, sorteres med musen eller fjernes permanent.
- Luft før første indholdskasse, mellem kasser og inde i kasser kan styres separat på desktop og mobil.
- Hjørneafrunding kan indstilles, og det godkendte kortdesign bruges som standard.
- WhatIf simulerer ændringen uden skrivning, og en rigtig gemning tager automatisk backup først.
- Tilføjer DESIGN-MANUAL.md med de godkendte valg for farver, bredde, typografi, afstande, kort og mobilvisning.


== Version 0.4.18 – Egen sideeditor og funktionsmoduler ==

- Udvider Sideindhold til Sider med en samlet editor til Hjem, Om foreningen, Bliv medlem og Kontakt.
- Bevarer eksisterende ukendt sideindhold som en sikker legacy-sektion, indtil redaktøren selv vælger at fjerne det.
- Tilføjer genbrugelige sektionstyper til tekst, billeder, knapper, kort, fremhævelser og afstand.
- Tilføjer mailformular med servervalidering, nonce, spambegrænsning, testmail, valgfri lagring og CSV-eksport.
- Tilføjer afstemning med svarmuligheder, enkelt/flere svar, tidsrum, resultater, nulstilling og CSV-eksport.
- Begrænser dobbeltstemmer med cookie og saltet hash uden at gemme rå IP-adresser.
- Tilføjer responsive desktop-, tablet- og mobilvisninger samt separat luft og placering.
- Gemmer sider som dynamiske Hangar18-moduler, så en kodeopdatering gælder alle forekomster.
- Opdaterer designmanualen med regler for sideeditor, mailformularer og afstemninger.


== Version 0.4.19 – Redigering af nuværende sider ==

- Retter 0.4.18-fejlen, hvor eksisterende sideindhold kun blev vist som én låst legacy-sektion.
- Indlæser nuværende Gutenberg- og HTML-indhold som en ikke-gemt, redigerbar sektionskladde.
- Genkender overskrifter, tekst, billeder, knapper, afstande, to-kolonneindhold og topbanner/hero.
- Tilføjer en redigerbar Importeret blok / HTML-type til ukendte blokke, så intet indhold kasseres.
- Bevarer den offentlige side uændret, indtil redaktøren aktivt vælger Gem siden.
- Opretter fortsat fuld backup og WordPress-revision før den første konverterede gemning.


== Version 0.4.20 – Bevaring af eksisterende layout ==

- Retter fejlen, hvor importeret side-CSS blev vist som almindelig tekst øverst på siden.
- Genkender og renderer eksisterende side-CSS som CSS i stedet for indhold.
- Bevarer designgrupper med egne Gutenberg-klasser som samlede redigerbare HTML-sektioner ved nye importer.
- Gendanner kolonnelayout for eksisterende kort, Events og Billedgalleri på desktop og stabler dem på mobil.
- Samler tekst og tilhørende handlingsknap i samme luftsektion på allerede konverterede sider.
- Gendanner topbilledets efterfølgende tagline og de oprindelige responsive afstandsregler.
- Reparerer den allerede gemte 0.4.19-forside ved visning uden at kræve en ny konvertering eller automatisk dataskrivning.


== Version 0.4.21 – Ét korrekt hero-billede ==

- Fjerner det gamle Gutenberg Cover-billede fra heroens indhold, når samme billede allerede bruges som hero-baggrund.
- Bevarer heroens godkendte højde, beskæring og responsive baggrundsvisning.
- Genkender også ældre CSS, der blev gemt som en tekstsektion, og renderer den som side-CSS i stedet for synlig tekst.
- Sikrer, at Venstre/Midtstillet for desktop og mobil styrer både overskrifter, tekst og handlingsknapper uden at blive tilsidesat af importerede Gutenberg-klasser.


== Version 0.4.22 – Sammenligningskladde fra backup ==

- Backupoversigten viser nu backupgrund og om filen indeholder den oprindelige Hjem-side eller en nyere sideeditor-version.
- En oprindelig Hjem-backup kan oprettes som en separat WordPress-kladde direkte fra backuplisten.
- Kladden bliver ikke aktiv forside, tilføjes ikke til menuen og kan ikke overskrive Hjem-side ID 9.
- En allerede oprettet sammenligningskladde genbruges, så samme backup ikke opretter dubletter.
- Sidespecifik CSS tilpasses kladdens nye side-ID, så den gamle side kan forhåndsvises retvisende.


== Version 0.4.23 – Gendannet Hjem-design i sideeditoren ==

- Gendanner Hjem-sidens oprindelige sektionsfarver: knækket hvid, hvid, olivengrøn og sandfarvet.
- Gendanner 32 px luft mellem hovedsektionerne på desktop og 24 px på mobil.
- Tilføjer særskilt styring af lodret og vandret indvendig luft på desktop og mobil.
- Gendanner 24 px vandret indvendig luft på desktop samt 18 px på mobil.
- Gendanner de oprindelige runde knapper og deres farver i importerede Hjem-sektioner.
- Sætter mobilbanneret til 180 px og sikrer fortsat, at bannerbilledet kun vises én gang.
- Bevarer venstrestilling på desktop og midterstilling på mobil efter de valgte indstillinger.
- Tager automatisk fuld backup før engangsreparationen af den aktive Hjem-side.


== Version 0.4.24 – Sikre konverteringstests af sider ==

- Tilføjer Opret konverteringstest på ukonverterede sider i Hangar18 sideeditor.
- Opretter Om foreningen, Kontakt eller Bliv medlem som en separat offentlig testkopi uden at ændre originalsiden.
- Genbruger og opdaterer samme testside, så der ikke oprettes dubletter ved gentagne tests.
- Lader testkopien læse sin egen indlejrede sektionskladde i stedet for originalsiden eller den centrale editoropsætning.
- Tilpasser sidespecifik CSS fra originalens side-ID til testkopiens side-ID.
- Føjer ikke testkopier til Hangar18-menuen og udelader dem fra menuens sidevælger.
- Markerer testkopier med noindex, nofollow og noarchive, så de ikke skal optages af søgemaskiner.


== Version 0.4.25 – Fortryd sidekonvertering ==

- Tilføjer Gendan siden fra før editoren på sider, der allerede er gemt i Hangar18 sideeditor.
- Finder først den nyeste WordPress-revision uden sideeditor-data og bruger JSON-backup som sikker reserve.
- Tager både fuld backup og sidebackup af den konverterede version, før gendannelsen udføres.
- Gendanner kun den valgte sides titel, indhold, uddrag og eventuelle fremhævede billede.
- Rydder den valgte side fra editorens centrale lager, så den ikke genindlæses som konverteret ved næste besøg.
- Ændrer ikke menu, header, footer, testkopier eller andre sider.


== Version 0.4.26 – Sideversionering og ændringsbeskrivelser ==

- Kræver en kort ændringsbeskrivelse ved hver rigtig gemning i Hangar18 sideeditor.
- Tildeler hver side sit eget fortløbende versionsnummer.
- Tager automatisk en fuld før-backup og en separat sidekopi af den nye gemte version.
- Gemmer tidspunkt, WordPress-bruger, ændringsbeskrivelse, antal aktive sektioner, backupfiler og indholdshash i versionshistorikken.
- Viser de seneste versioner nederst på den valgte sides editorside.
- WhatIf viser næste versionsnummer, men opretter ingen version, backup eller historikpost.
- Medtager versionshistorikken i fremtidige fulde Hangar18-backups.


== Version 0.4.27 – Visuel sidebygger og redigerbare kasser ==

- Ombygger sideeditoren til en visuel arbejdsflade med elementer til venstre, sideopbygning i midten og indstillinger til højre.
- Elementer og funktionsmoduler kan klikkes eller trækkes ind i sideopbygningen.
- Tilføjer Kort-række / kolonner med 1-4 kolonner på desktop og 1-2 kolonner på mobil.
- Gør hver kasse selvstændigt redigerbar og flytbar med farve, tekstkontrast, kant, luft, afrunding og placering.
- Tilføjer stålgrå til den godkendte farvepalette.
- Tilføjer Opdel importerede kasser, som udskiller WordPress-kolonner uden at ændre den resterende importerede sektion.
- Bevarer den offentlige side, indtil redaktøren gemmer som en ny version med ændringsbeskrivelse og automatisk backup.


== Version 0.5.0 – Designsystem og menueffekter ==

Version 0.5.0 bygger direkte videre på v0.4.27. Den eksisterende visuelle sidebygger, datamodeller, WhatIf, backup og versionshistorik er bevaret.

Nyt i første 0.5.0-fundament:
- Nyt Designer schema 1.0 med globale design tokens, indlejret bagudkompatibelt i HeaderDesign schema 2.3.
- Centrale farver: primær, sekundær, accent, lys flade, baggrund, tekst, lys tekst og action/link.
- Global brødtekst- og overskriftstypografi med H1/H2/H3-størrelser.
- Afstandstokens XS/S/M/L/XL og tre niveauer af hjørneafrunding.
- Sidebyggerens eksisterende farveklasser kobles til de globale farver.
- Menupræsentation: Klassisk, Flydende pill eller Indrammet.
- Hover-effekter: Ingen, animeret understregning, løft eller pill-baggrund.
- Aktiv side: Ingen, understregning, pill eller punkt.
- Undermenu-animation: Ingen, Fade, Fade + slide eller Scale.
- Animationshastighed kan styres centralt.

Kompatibilitet og sikkerhed:
- Standardfarverne er identiske med v0.4.27.
- Alle nye menueffekter er slået fra som standard.
- HeaderDesign forbliver schema 2.3, så den eksisterende centrale konfiguration og ældre PowerShell-klienter fortsat kan læse de kendte felter.
- Ingen sidekonvertering eller datamigration køres automatisk.


== Version 0.5.1 – Navigator, avanceret Inspector og genbrugelige komponenter ==

- Sidebuilderens venstre panel har faner til Elementer, Lag og Komponenter.
- Navigator/Lag viser alle aktive sektioner, synlighedsstatus og understøtter drag-and-drop rækkefølge.
- Inspector er opdelt i Indhold, Design og Avanceret.
- Avanceret Inspector viser elementtype og elementnøgle samt genveje til duplikering og komponentlagring.
- Fem indbyggede komponentpresets: Hero + handling, Tekst + billede, 3 informationskort, CTA-bånd og Kontaktblok.
- Enhver ikke-legacy sektion kan gemmes som egen genbrugelig komponent. Egne komponenter gemmes centralt i WordPress og kan indsættes på alle redigerbare sider.
- Egne komponenter kan slettes direkte fra komponentbiblioteket.
- Eksisterende v0.5.0 sider, HeaderDesign schema 2.3 og Designer schema 1.0 bevares uændret.


== Version 0.5.2 – Individuelt elementdesign ==

- Hver editorsektion kan følge Globalt design eller bruge Tilpasset farvetilstand.
- Tilpasset tilstand giver egne farver for baggrund, tekst og overskrifter.
- Hvert element kan få egen kantbredde, kantfarve og skygge.
- Globalt design er fortsat standard, så eksisterende sider beholder deres udseende efter opdatering.
- Page-editor dataformatet er kompatibelt løftet fra schema 1.5 til 1.6.


== Version 0.5.3 – Typografi pr. element ==

- Hver editorsektion kan vælge egen brødtekstfont og overskriftsfont eller arve de globale fonte.
- Brødtekst samt H1, H2 og H3 kan få egne størrelser pr. element.
- Værdien 0 betyder global størrelse og giver fuld bagudkompatibilitet.
- Typografifelterne gemmes også i genbrugelige komponenter fra v0.5.1.
- Page-editor dataformatet er kompatibelt løftet fra schema 1.6 til 1.7.


== 0.5.12 ==
* Lokal Undo/Redo-historik med op til 50 redigeringstrin i den visuelle editor.
* Fortryd/Gendan-knapper samt Ctrl/Cmd+Z og Ctrl/Cmd+Shift+Z uden at overtage tekstfelters native undo.
* Historikken dækker feltændringer, live-canvas, sektioner, kort og rækkefølge.
* Status viser ugemte ændringer, og browseren advarer ved navigation væk fra en ændret side.
* Ingen page-editor schemaændring; permanente WordPress-revisioner/backups er uændrede.


## v0.5.26 – E5 UD-057 Repeater / Query list
- Nyt `Repeater / Query list`-element i den visuelle sidebygger.
- Genbruger Query Builder v1 til datatype, filter, sortering og limit.
- En linked component fungerer som template og renderes én gang pr. query-resultat.
- Hvert resultat bliver current data context under render, så eksisterende dynamic bindings virker uden en særskilt template-motor.
- Understøtter component variant, desktop/mobil-kolonner, gap og tom-resultattekst.
- Query List-komponentreferencer indgår i Usage Inspector og blokerer sikker sletning af komponent/variant.
- Runtime beskytter mod rekursive Query List/component-loops og gendanner altid det tidligere data context.
- Page-editor schema: 1.20.


## v0.5.27 – E5 UD-058 Conditional Visibility
- Alle page-builder elementer får generiske Conditions med AND/OR mode.
- Data conditions: empty/not-empty/equality/comparison mod current data context.
- User conditions: logged in/out, rolle og capability.
- Date/time conditions: før, efter og mellem i WordPress-site timezone.
- Conditions evalueres server-side før dynamic binding og virker derfor også pr. resultat inde i Query Lists.
- Editor-preview evaluerer samme condition-model og markerer skjulte elementer uden at fjerne dem fra canvas.
- Conditions er præsentationslogik og er eksplicit ikke en authorization/security boundary.
- Maks. 8 conditions pr. element; ukendte typer/operatorer droppes under normalisering.
- Page-editor schema: 1.21.


## v0.5.28 – E5 UD-054 Relation / Group / Repeater fields
- Datatype schema builder understøtter nu Relation, Group og Repeater ud over de fem primitive felttyper.
- Relation kræver en eksisterende mål-datatype og gemmer et valideret entry-ID; mål-datatyper kan ikke slettes mens relationer peger på dem.
- Group og Repeater bruger op til 12 typed underfelter af text/number/bool/date/media.
- Repeater er bounded til 1–20 rækker pr. schemafelt og har add/remove UI i entry-editoren.
- Nested værdier bruger samme server-side sanitizer som primitive felter og Required-validering.
- Query Builder v1 skjuler/rejecter strukturerede felter; relation/advanced query udvides separat i UD-056.
- Data SchemaVersion løftes til 2; page-editor schema forbliver 1.21.


## v0.5.29 – E5 UD-056 Advanced Query
- Advanced Query understøtter op til 4 AND/OR-grupper med op til 6 filtre pr. gruppe.
- Filtre kan blande primitive datafelter, Relation-felter og Data Tags taxonomy.
- Data entries får en privat `h18_data_tag` taxonomy med kommasepareret tag-editor.
- Relation-filter valideres mod relation-feltets scalar target-ID; Group/Repeater kan ikke bruges som direkte query-filter.
- Advanced preview og frontend-shortcode bruger samme normalized evaluator uden rå SQL.
- Pagination: 1–50 resultater pr. side, stabil sortering og separate query-string page keys pr. query.
- Kandidatsættet er bounded til 2000 publicerede entries og markerer `Truncated`, hvis grænsen nås.
- Page-editor schema forbliver 1.21; Data SchemaVersion forbliver 2.


## v0.5.30 – E5 UD-059 Field formatters + fallback
- Dynamic bindings får et separat, bagudkompatibelt `BindingOptions`-lag; den eksisterende `Bindings[property]=field` model ændres ikke.
- Formatters: Auto/Text, upper/lower, tal med 0/1/2 decimaler, kort/ISO/lang dato samt Ja/Nej.
- Fallback modes: behold statisk elementværdi, custom fallback eller tom værdi.
- `FallbackWhenEmpty` er opt-in og default false, så eksisterende bindinger beholder tidligere empty-value adfærd.
- Prefix/suffix kan anvendes på tekstoutput; URL/media springer prefix/suffix over og saniteres fortsat typespecifikt.
- Runtime og canvas-preview anvender samme formatter/fallback-model.
- BindingOptions følger med i Patterns, linked component definitions og Page Templates.
- Page-editor schema løftes bagudkompatibelt til 1.22.
