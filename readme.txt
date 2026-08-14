=== Hangar18 Manager ===
Version: 0.4.9

Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.

== Installation / opdatering ==

1. Tag gerne en WordPress-backup.
2. WordPress -> Plugins -> Tilføj plugin -> Upload plugin.
3. Upload hangar18-manager-v0.4.1.zip.
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
- Placering i køretøjsregister: Venstre / Midt
- Indholdsjustering på køretøjssiden: Auto / Venstre / Midt
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

== Kompatibilitet ==

v0.2.0 bruger fortsat:
HANGAR18-VEHICLE-DATA
HANGAR18-EVENT-DATA
HANGAR18-GALLERY-ALBUM-DATA

PowerShell- og webmanageren kan derfor fortsat læse de samme datamarkører.


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
