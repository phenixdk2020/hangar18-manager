# Visual Designer Manager – Design- og arkitekturmanual

Senest opdateret: 28. august 2026  
Gælder for: Visual Designer Manager 0.1.x og nyere  
Status: Autoritativ målarkitektur for Visual Designer

## 1. Formål

Denne manual beskriver den godkendte arkitektur og de visuelle regler for **Visual Designer Manager**. Den supplerer den eksisterende `DESIGN-MANUAL.md`, som fortsat dokumenterer den tidligere 0.4.x-løsning og de historiske designvalg for hjemmesiden.

Visual Designer-manualen skal bruges som teknisk og funktionel reference, når den nye Designer videreudvikles. Nye funktioner må ikke indføres på en måde, der bryder hierarkiet, versionsmodellen, frontend-renderingen eller adskillelsen mellem globalt design og sideindhold.

Hovedprincippet er, at Visual Designer skal fungere som en **LEGO-lignende, modeldrevet sidebygger**, hvor brugeren kan kombinere Sektioner, Kasser og indholdselementer visuelt uden at miste en entydig canonical model.

---

## 2. Overordnet arkitektur

Den godkendte struktur er:

```text
VISUAL DESIGNER
│
├── Globalt design
│   ├── Farvepalette
│   ├── Skrifttype
│   ├── Standard tekstfarve
│   ├── Standard overskriftsfarve
│   ├── Sidebaggrund
│   ├── Sidebredde
│   └── Standardafstande
│
├── Header Designer
│   ├── Logo
│   ├── Menu
│   ├── Tekst
│   ├── Knap
│   └── Kasser/layout
│
├── Side Designer
│   ├── Sektion
│   │   ├── Kasse
│   │   │   ├── Tekst
│   │   │   ├── Billede
│   │   │   └── øvrige elementer
│   │   ├── Tekst
│   │   └── Billede
│   └── flere Sektioner
│
└── Footer Designer
    ├── Tekst
    ├── Menu
    ├── Logo
    ├── Links
    └── Kasser/layout
```

Temaet skal på sigt fungere som **WordPress-shell/runtime**, mens Visual Designer Manager styrer det faktiske visuelle design.

Header og Footer er globale designs og skal **ikke** være almindelige elementer, der kopieres ind på hver side.

---

## 3. Sidehierarki

En almindelig Visual Designer-side skal følge dette hierarki:

```text
SIDE
│
├── SEKTION
│   ├── Tekst
│   ├── Billede
│   └── Kasse
│       ├── Tekst
│       ├── Billede
│       └── Kasse
│
├── SEKTION
│   ├── Kasse
│   ├── Kasse
│   └── Kasse
│
└── SEKTION
    └── Tekst
```

### Regler

- **Sektion** er sidens primære vandrette byggeblok.
- En Sektion skal som målarkitektur kun kunne ligge direkte på sidens root.
- En **Kasse** er en layout-/indholdscontainer inde i en Sektion eller anden Kasse.
- Tekst, Billede og øvrige indholdselementer kan ligge direkte i en Sektion eller i en Kasse.
- Kasser må kunne indeholde andre Kasser.
- Sektioner må ikke bruges som almindelige nested Kasser.

Den nuværende 0.1.x-model kan teknisk tillade flere kombinationer under udvikling. Når hierarkireglen låses i Visual Designer, skal ovenstående være den autoritative struktur.

---

## 4. Forskellen på Sektion og Kasse

| Egenskab | Sektion | Kasse |
|---|---|---|
| Formål | Hovedområde på en side | Lokal layout-/indholdskasse |
| Placering | Direkte på side/root | Inde i Sektion eller Kasse |
| Standardbredde | 120/120 | Valgfri |
| Side om side | Normalt nej | Ja |
| Kan indeholde Tekst/Billede | Ja | Ja |
| Kan indeholde Kasser | Ja | Ja |
| Kan ligge inde i Kasse | Nej i målarkitekturen | Ja |
| Baggrund | Ja | Ja |
| Border | Ja | Ja |
| Padding | Ja | Ja |
| Hjørneradius | Ja | Ja |
| Auto-grow | Ja | Ja |

### Sektion

Sektionen definerer et større logisk område på siden. Eksempler:

- Om foreningen
- Køretøjer og materiel
- Events
- Kontakt
- CTA-/handlingsområde

En Sektion kan have egen baggrund, afstand og indvendigt layout, men dens vigtigste rolle er at opdele siden i store, forståelige områder.

### Kasse

Kassen er den fleksible LEGO-klods til lokalt layout. Den bruges eksempelvis til:

- to eller tre kolonner;
- et kort med billede og tekst;
- en gruppe af elementer;
- nested layout;
- baggrundsfarve, border og afrundede hjørner omkring en gruppe.

Kassen skal automatisk vokse, når dens indhold kræver mere højde. En manuelt valgt højde fungerer som minimumshøjde.

---

## 5. Canonical layoutmodel

Visual Designer bruger en modeldrevet geometri med:

- 120 vandrette units;
- 8 px lodret grid/snap;
- `x`, `y`, `w`, `h` pr. element;
- `parentId` til hierarki;
- `order` til stabil rækkefølge;
- type-specifikke properties.

Fra Responsive Designer gemmes geometrien som samme element på flere breakpoints, bl.a. `geometry.desktop`, `geometry.laptop` og `geometry.mobile`. Elementets ID, indhold, parent og order er fælles.

Save, Undo, Redo, Preview og frontend skal alle arbejde ud fra samme canonical model.

Visuelle CSS-tricks må ikke være eneste kilde til en layoutændring. Hvis en egenskab påvirker layout, skal den kunne rekonstrueres efter Save/Reload.

---

## 6. Drag-and-drop og celle-split

Visual Designer skal understøtte fysisk drag-and-drop med tydelige drop-zoner.

### Almindelige elementer

Et element kan placeres:

- **Over**
- **Under**
- **Venstre**
- **Højre**

### Kasse og Sektion

En Kasse/Sektion har derudover:

- **Ind i**

### Celle-split

Over/Under må ikke automatisk betyde en ny fuldbredde række. Når man dropper på et konkret element, deles den valgte celle.

Eksempel:

```text
┌───────────────┬───────────────┐
│    Billede    │               │
├───────────────┤     Tekst     │
│     Tekst     │               │
└───────────────┴───────────────┘
```

Her spænder elementet til højre over to rækker. Det svarer konceptuelt til `row-span` i CSS Grid.

Venstre/Højre deler den valgte celle vandret. Over/Under deler den valgte celle lodret.

---

## 7. Editor-labels og fysisk geometri

Editor-labels som:

- `SEKTION · id`
- `KASSE · id`
- `TEKST · id`
- `BILLEDE · id`

må **aldrig tælle med i elementets fysiske højde eller bredde**.

Labelen er editor-chrome og skal ligge som overlay uden for canonical `x/y/w/h`.

Parent- og child-labels må ikke ligge oven i hinanden. Label-layoutet skal have sin egen visuelle lane/offset, som ikke påvirker frontend.

### Farver i editoren

- **Grøn** = valgt/aktivt element og resize-håndtag.
- **Blå** = hover/drop-kontekst.
- **Rød** = reel overlap/advarsel.
- **Sand/guld** = særskilt redigering af billedindhold inde i billedboksen.

Kasse/Sektion er layout-wrappers og må ikke få overlap-advarsel blot fordi deres børn ligger inde i dem.

---

## 8. Fælles styling-egenskaber

Alle relevante elementer skal kunne have grundlæggende styling uden specialkode pr. side.

### Fælles egenskaber

- Border thickness, standard `0 px`
- Border color
- Hjørneradius, standard `0 px`
- Afstand X til næste element
- Afstand Y til næste element
- Baggrundsfarve, hvor det giver mening
- Størrelse og placering

Hjørneradius er en fælles egenskab for **Sektion, Kasse, Tekst og Billede**. Afstand X/Y skal indgå i layoutberegningen og ikke kun være kosmetisk CSS.

---

## 9. Tekst-element

Tekst-elementet består af én fysisk boks med valgfri overskrift og brødtekst.

### Indhold

- Valgfri **Overskrift**
- Overskrifttype **H2-H6**
- Brødtekst
- Justering: venstre, center, højre

### Styling

Tekst-elementet skal kunne styre:

- Baggrundsfarve eller gennemsigtig
- Brødtekstfarve
- Overskriftsfarve
- Border og borderfarve
- Hjørneradius
- Padding
- Afstand X/Y
- Boksens bredde/højde

Overskriftsfarven arver som standard tekstfarven eller den globale overskriftsfarve, men skal kunne overskrives lokalt.

Tekst-elementets label er ikke en del af den fysiske højde.

---

## 10. Billede-element: boks og billede er to forskellige lag

Billede-elementet skal altid forstås som:

1. **Billedboksen**
2. **Selve billedet inde i boksen**

Boksens størrelse må ikke automatisk være identisk med billedets naturlige størrelse.

### Billedboksen

Boksen styrer:

- `x/y/w/h`
- Border og borderfarve
- Hjørneradius
- Baggrundsfarve
- Afstand X/Y
- Resize

De grønne resize-håndtag ændrer boksen, ikke billedets egen geometri.

### Billedet inde i boksen

Billedet kan vises som:

| Tilstand | Funktion |
|---|---|
| Vis hele billedet | Hele billedet vises uden beskæring; tom plads kan forekomme |
| Fyld boksen | Billedet fylder boksen og beskæres efter behov |
| Original størrelse | Billedet beholder sin naturlige størrelse inde i boksen |
| Stræk | Billedet følger boksens bredde/højde og kan deformeres |
| Manuel | Billedet har egen X/Y/bredde/højde inde i boksen |

Standard for nye billeder er **Vis hele billedet**, vandret center og lodret center.

I Manuel-tilstand kan selve billedet flyttes og skaleres uafhængigt af billedboksen. Den manuelle geometri gemmes separat, og ændring af billedboksens størrelse må ikke automatisk ændre billedets egen bredde/højde. Lås proportioner er standard slået til ved manuel skalering.

Hjørneradius på billedboksen skal klippe indholdet, så billedet ikke stikker uden for afrundede hjørner.

---

## 11. Auto-grow for Sektion og Kasse

Sektion og Kasse skal efter drop, reparent og resize genberegne nødvendig højde ud fra alle børn.

Reglen er:

```text
faktisk højde = max(valgt minimumshøjde, nødvendig indholdshøjde)
```

Når et barn flyttes eller slettes, må containeren krympe igen, men aldrig under den manuelt valgte minimumshøjde.

Border, padding og lodret afstand skal indgå i beregningen. Responsive layouts skal beregne nødvendig parent-højde ud fra det aktive breakpoint, så fx mobil-stacking ikke overlapper efterfølgende indhold.

---

## 12. Overlap

Overlap kan være nyttigt til avancerede designs, men må ikke ske usynligt ved en fejl.

Nuværende princip:

- reel overlap mellem leaf-elementer markeres med rød advarsel;
- container/barn-forhold tæller ikke som overlap;
- selected element beholder grøn selection, selv hvis overlap-advarslen samtidig vises.

Hvis fri overlap senere gøres til en officiel funktion, bør det implementeres som en tydelig **fri placering/layer-mode** med z-index og ikke blandes ind i standard LEGO/grid-layoutet.

---

## 13. Versionering af sider

Visual Designer skal være ikke-destruktiv.

Hver rigtig **Gem** opretter en ny Visual Designer-version og kræver en kort ændringsbeskrivelse.

Gemte versioner tilbyder **Forhåndsvis version**, **Gendan original** og **Opret kopi**.

Gendan original gemmer den valgte gamle model som en ny version, eksempelvis `v1 → v2 → v3 → Gendan v1 → v4`. Tidligere versioner bevares.

Opret kopi laver en ny WordPress-kladdeside, hvor den valgte historiske model bliver kopiens egen v1.

---

## 14. Forhåndsvisning og Save

Usavet Designer-state kan vises i den rigtige frontend/theme via en kortlivet brugerspecifik preview-model uden at ændre den offentlige side.

**Gem & vis** gemmer canonical model som ny version, verificerer at den gemte model matcher input og åbner den offentlige side efter gemning.

---

## 15. Globalt design

Globalt design skal samle værdier, der ikke bør sættes individuelt på hvert element.

Planlagte globale indstillinger:

- Primær skrifttype
- Standard brødtekstfarve
- Standard overskriftsfarve
- Standard sidebaggrund
- Godkendt Hangar18-farvepalette
- Desktop-sidebredde
- Laptop-sidebredde
- Mobil-sidebredde
- Standardafstande
- Standard border/radius-regler

Lokale elementindstillinger må kunne overskrive globale defaults.

---

## 16. Temaets rolle

Hangar18 Base Theme skal på sigt være et tyndt **runtime/shell-tema**.

Temaets opgaver er WordPress template lifecycle, hooks, nødvendige wrappers, menu-/WordPress-integration, indlæsning af Manager-renderet Header/Side/Footer og fallback hvis Manager ikke er tilgængelig.

Temaet bør ikke indeholde parallelle designregler, som konkurrerer med Visual Designer.

---

## 17. Header Designer

Header skal være et globalt design med sin egen model og versionshistorik og bruge samme LEGO-/grid-motor som Side Designer.

Planlagte elementer: Logo, Navigation/Menu, Tekst, Knap, Kasse og eventuelt Ikon.

Header-indstillinger omfatter bl.a. sticky/ikke sticky, højde, baggrund, tekst/menu-farve, mobilmenu, logo-størrelse og alignment. Headeren ligger uden for almindelige sider og kan ikke slettes fra en side.

---

## 18. Footer Designer

Footer skal være et globalt design med egen model og versionshistorik.

Planlagte elementer: Tekst, Logo, Menu, Links, Kasser/kolonner og eventuelt kontaktoplysninger/sociale links.

Footer følger global farvepalette, typografi og breddeprincip, men kan have egne lokale overrides og kan ikke slettes fra en almindelig side.

---

## 19. Flere elementtyper

Efter fundamentet planlægges bl.a.:

- Knap
- Skillelinje
- Spacer/Afstand
- Ikon
- **Tabel** – manuel og senere dynamisk datatabel
- Galleri
- Menu
- Hero/Topbanner
- Video
- Accordion/FAQ
- Tabs
- Formular
- Dynamisk Køretøj-element
- Dynamisk Event-element
- Dynamisk Billedgalleri-element

Nye elementer skal bruge samme canonical model, versionering og frontend-renderingsprincipper. Card/Kort bør som udgangspunkt undersøges som Kasse-preset/komponent frem for endnu en hårdkodet layouttype.

---

## 20. Responsivt design

Desktop, Laptop og Mobil er **tre visninger af samme side og samme elementer**, ikke tre uafhængige sider.

Den aktive arkitektur understøtter:

- `geometry.desktop`
- `geometry.laptop`
- `geometry.mobile`
- Laptop arver Desktop som standard
- Mobil arver det effektive Laptop/Desktop-layout som standard
- lokalt `x/y/w/h` override pr. breakpoint
- nulstilling til arv
- samme ID, indhold, parent og order på alle breakpoints

`geometry.tablet` beholdes reserveret i modellen, så en særskilt Tablet-visning kan tilføjes senere uden at ændre de eksisterende Laptop-data.

Frontend anvender Laptop-layout op til ca. 1180 px og Mobil-layout op til 782 px. Der må ikke opstå vandret rulning på hele siden som følge af elementgeometri.

Selve Designer-UI'et skal også være responsivt: **Elementer og Inspector kan foldes ind/ud**, canvas skal bruge den resterende skærmbredde, og almindelige laptopskærme skal kunne arbejde i en kompakt visning uden at ændre den canonical 120-unit model.

---

## 21. Tilgængelighed og kontrast

Farver skal følge Hangar18s godkendte palette, men redaktøren skal stadig kunne vælge lokale farver.

Følgende skal kontrolleres:

- tekst/baggrund har tilstrækkelig kontrast;
- links og knapper kan genkendes;
- fokusmarkering er synlig;
- billeder har alt-tekst;
- headings bruges semantisk korrekt;
- mobilvisning er læsbar.

---

## 22. Aktuel udviklingsrækkefølge

Versionsnumre er planlægningsmål og kan flyttes ved nødvendige hotfixes.

### Visual Designer 0.1.19 – sikkerhed og sporbarhed
- automatisk programbackup før update;
- synlig changelog;
- obligatorisk ændringsbeskrivelse i sideversioner.

### Visual Designer 0.1.20 – elementstyling og billedlag
- fælles hjørneradius;
- tekstbaggrund, tekst-/overskriftsfarve og padding;
- billedboks og billedindhold som uafhængige lag;
- manuel billedgeometri.

### Visual Designer 0.1.21 – Responsive Designer
- Desktop / Laptop / Mobil;
- canonical breakpoint-geometri og arv;
- responsive frontend;
- foldbare Elementer/Inspector-paneler og laptop-fit.

### Visual Designer 0.1.22 – hierarki og layout-QA
- Sektion kun på root;
- Kasse nesting;
- drop-regler;
- overlap-policy;
- auto-grow/celle-split regressionstest.

### Derefter
- Globalt design og theme-shell;
- Header/Footer Designer;
- flere generelle elementer inkl. Tabel;
- fælles dataarkitektur;
- Køretøjer, Events og Galleri;
- konvertering/paritetstest af eksisterende sider.

---

## 23. QA-regler for Visual Designer

Før en ny Visual Designer-version godkendes, skal følgende kontrolleres:

1. Save/Reload giver samme canonical layout.
2. Undo/Redo ændrer samme model, som bliver gemt.
3. Preview matcher frontend-renderingen.
4. Labels påvirker ikke fysisk elementgeometri.
5. Kasse/Sektion auto-grow følger børn korrekt.
6. Border, radius og Afstand X/Y er konsistente i editor og frontend.
7. Tekstoverskrift, brødtekst, farver og baggrund vises korrekt.
8. Billedboksen kan være større end selve billedet.
9. Manuel billedgeometri forbliver uafhængig af billedboksens størrelse.
10. Restore original bevarer historikken.
11. Restore som kopi ændrer ikke original-siden.
12. Plugin self-update efterlader Manager aktivt og har verificeret programbackup.
13. Desktop, Laptop og Mobil får ikke utilsigtet vandret overflow.
14. Responsive inheritance/override overlever Save/Reload.
15. Elementer/Inspector kan foldes uden at ændre canonical sidegeometri.
16. Header, side og footer må ikke overlappe hinanden.

---

## 24. Dokumentationsregel

Når et nyt Visual Designer-designvalg godkendes:

1. Opdatér den canonical Visual Designer-model eller relevante globale indstilling.
2. Opdatér denne design- og arkitekturmanual.
3. Opdatér `CLEAN-TECHNICAL-MANUAL.md`, når beslutningen påvirker en konkret UX-kontrakt, teknisk adfærd eller implementeringsregel.
4. Opdatér `CLEAN-USER-MANUAL.md`, når ændringen er synlig eller relevant for en redaktør/administrator.
5. Tilføj ændringen til release-notes/changelog.
6. Kør QA på editor, Save/Reload, Preview og frontend.
7. Byg først en verificeret GitHub-releasepakke, når den aftalte release skal publiceres.

### 24.1 Krav til brugermanualens grafiske dokumentation

Brugermanualen må ikke kun beskrive Visual Designer med tekst. Når et begreb, en arbejdsgang eller et layout forstås bedre visuelt, skal manualen suppleres med **grafiske eksempler og illustrationer**.

Som minimum skal følgende områder dokumenteres visuelt:

- en komplet websides anatomi med **Tema/Shell → Header → Side → Footer**;
- forskellen mellem **Header/Footer** og en sides **Hero/Topbanner**;
- LEGO-hierarkiet **Side → Sektion → Kasse → indholdselement**;
- typiske kolonne-, celle-split- og nested-Kasse-layouts;
- drag-and-drop med Over/Under/Venstre/Højre/Ind i;
- Desktop/Laptop/Mobil og responsive overrides;
- billedboks kontra selve billedet;
- normal kontra flydende Knap;
- Tabel, herunder cellemarkering og Excel-lignende rammevalg;
- Menu, Galleri, Formular og andre større elementtyper, når de frigives.

Grafiske eksempler skal følge disse regler:

- Illustrationer lagres som vedligeholdelige dokumentationsassets, fortrinsvis SVG til diagrammer og PNG/JPG til relevante screenshots.
- Hver illustration skal have en kort forklaring/caption og meningsfuld alt-tekst.
- Diagrammer skal vise det samme hierarki og de samme begreber som den canonical model; de må ikke introducere en alternativ layoutlogik.
- Screenshots og UI-illustrationer skal opdateres, hvis Designerens brugerflade ændres væsentligt.
- En illustration af en planlagt funktion skal tydeligt mærkes **Planlagt** og må ikke præsenteres som allerede frigivet funktionalitet.
- Før/efter-illustrationer anvendes, når de gør drag/drop, responsive ændringer, formattering eller migration lettere at forstå.
- Grafikken skal være læsbar både på almindelig desktop og ved nedskalering i dokumentation.
- Visuelle eksempler skal, hvor relevant, vise realistiske kombinationer af flere elementer frem for kun isolerede kontrolfelter.

Dokumentationen skal derfor forklare både **hvad et element er**, **hvor det kan ligge**, **hvordan det kombineres med andre elementer**, og **hvordan resultatet ser ud i en rigtig sideopbygning**.

### 24.2 Produktnavn og synlige filnavne

Det officielle produktnavn er **Visual Designer Manager**. Den tidligere udviklingsbetegnelse **Clean** må ikke bruges i nye brugersynlige navne.

Følgende er en FAST navngivningsregel:

- nye releasepakker navngives `visual-designer-manager-v<version>.zip`;
- automatiske programbackups navngives `visual-designer-manager-v<fra-version>-before-v<til-version>-YYYYMMDD-HHMMSS.zip`;
- nye brugersynlige eksport-, backup-, checkpoint-, dokument- og downloadnavne skal bruge **Visual Designer Manager** eller `visual-designer-manager`;
- `Clean`, `hangar18-manager-clean` og tilsvarende gamle produktbetegnelser må ikke introduceres i nye brugersynlige filnavne, UI-tekster eller dokumenttitler;
- historiske filer/releases omdøbes ikke automatisk;
- interne kompatibilitetsidentifikatorer som eksisterende PHP namespace, `h18_clean_*`, WordPress pluginmappe/slug og text-domain må bevares midlertidigt, når en ændring ellers kan bryde opdatering, data eller WordPress-kompatibilitet. De må ikke præsenteres som produktnavn for brugeren.

En senere intern namespace/slug-migration skal behandles som en særskilt kompatibilitetsændring og må ikke blandes sammen med den brugersynlige navngivning.

`CLEAN-DESIGN-MANUAL.md` er fremover den autoritative arkitekturbeskrivelse for den nye Visual Designer. Den ældre `DESIGN-MANUAL.md` bevares som reference for eksisterende designstandarder og legacy 0.4.x-adfærd, indtil de relevante regler er migreret til Visual Designer Manager.

## 0.1.23 – Global Header/Footer Designer

- Header og Footer er globale Visual Designer-modeller i separat storage og med separat ikke-destruktiv versionshistorik.
- De genbruger Side Designer-layoutmotoren; der må ikke opstå en parallel Header/Footer-layoutmotor.
- 0.1.23 overtager ikke endnu temaets runtime Header/Footer. Indstillingen kan klargøres, men frontend-aktivering venter på Theme-shell integration for at undgå dobbelt Header/Footer.
- Menu-data bevares separat. Visuelt Menu-element bygges først efter Header/Footer-canvas og indsættes derefter som et normalt globalt element.
- Manager-moduler viser modenhedsstatus; gul betyder ikke færdig.
- Versionsnote er valgfri og kan systemgenereres.

## 25. Ikonbibliotek

Visual Designer bruger et centralt SVG-ikonregister. Et Icon-element gemmer kun sin canonical kilde (`iconSet`) og sit ikon-ID (`icon`). SVG-geometrien ligger i biblioteket og må ikke kopieres ind i hver side.

Ikonbiblioteket har tre permanente niveauer:

1. **Core icons** – følger med Visual Designer Manager og organiseres i kategorier.
2. **Module icons** – moduler som Køretøjer, Events og Galleri kan registrere ekstra ikon-sæt uden at ændre core-biblioteket.
3. **Custom icons** – reserveret udvidelsesniveau, hvor administrator senere skal kunne uploade eller indsætte egne sanitiserede SVG-ikoner. Persistent Custom-upload er ikke aktiveret i v0.1.66.

Core-biblioteket skal være lokalt, SVG-baseret og uden eksterne font-/ikonafhængigheder. Designer og frontend skal bruge samme registry.

## 26. Tabel – kantdesign

Tabel er et struktureret Designer-element og skal understøtte Excel-lignende kantstyring. En eller flere celler kan markeres, og kantværktøjet kan anvende Yderramme, Indvendige, Alle, Vandret, Lodret, Top, Højre, Bund, Venstre eller Ingen. Stregens tykkelse, farve og stil (`solid`, `dashed`, `dotted`) er canonical data. Celle-overrides gemmes separat fra tabelstandarden og skal fungere med Copy/Paste, Undo/Redo, Save/Reload, Preview og frontend.

## Module/Data Foundation v0.1.67

Visual Designer Manager skelner nu mellem **statiske elementdata** og **genbrugelige moduldata**. Køretøjer, Events og Billedgalleri skal ikke gemmes som kopier inde i hver side. De får en fælles central datastore og kan senere vises gennem dynamiske Designer-elementer.

Et modulrecord har fælles titel/status/billede/sortering samt modul-specifikke standardfelter. Derudover findes ordnede, brugerdefinerede attributter. Det er især grundlaget for Køretøjer, hvor tekniske datafelter skal kunne tilføjes, skjules og sorteres uden at ændre datamodellen.

v0.1.67 indeholder **ikke** den endelige Køretøjer-Manager eller dynamisk frontendbinding. Den etablerer den datakontrakt, som næste version bygger UI og visninger oven på.

## 27. Canvas/Section-struktur

Den canonical sideanatomi er **Webside/Canvas → Sektion → Kasse eller indholdselement**. Kun Sektion må ligge direkte på Webside/Canvas. Kasser, Tekst, Billede, Knap, Menu, Tabel, Data List og andre leaf-elementer skal derfor altid have en Sektion som øverste layoutforælder. Kasser kan fortsat nestes i Sektion/Kasse.

Når et eksisterende legacy-layout har et element direkte på root, opretter normalizeren en neutral Sektion omkring elementet og flytter root-geometri og ekstern spacing til Sektionen. Elementets ID og synlige placering bevares. En historisk nested Sektion konverteres tabsfrit til Kasse.

Fra v0.1.68 bliver denne normalisering også persisteret automatisk for eksisterende Designer-sider. Hver berørt side får en rå pre-migration-backup og en ny Designer-version. Migreringen må kun committe, hvis alle oprindelige element-ID'er stadig findes og den nye model består canonical hierarchy-validering.

I editoren er lagløft under redigering en **ren UI-egenskab**: markeret element, drag og resize må midlertidigt ligge foran andre elementer og løfte nødvendige ancestor stacking contexts. Det må aldrig ændre elementets canonical `zIndex` eller frontendens lagrækkefølge.

## Canvas Auto Height

Websiden er den yderste Designer-ramme omkring alle Sektioner. Den skal automatisk udvide sig til mindst 32 px under den nederste root-Sektion og må tilsvarende krympe igen, når indhold flyttes op eller slettes. Kun Sektioner ligger direkte på Websiden; derfor beregnes Webside-højden ud fra disse og ikke ud fra hvert enkelt child-element.

## Køretøjsmodul – designprincip

Køretøjsdata og sidedesign holdes adskilt. Et køretøj oprettes én gang under **Manager → Køretøjer** og kan derefter vises mange steder. **Køretøjsliste** er et layout-element til oversigter; det styrer kolonner, afstand, kortfarver, billede, kategori og kort beskrivelse. **Køretøjsdetalje** er et layout-element til den fulde visning og styrer hero-billede, galleri, beskrivelse og tekniske data.

Standardmønstret er én oversigtsside plus én genbrugelig detaljeside. Køretøjslisten peger på detaljesiden, og hvert kort sender sit stabile record-ID som `?h18_vehicle=...`. Detalje-elementet står i **Fra URL**-tilstand og viser dermed det valgte record uden at der skal oprettes en separat WordPress-side for hvert køretøj.

Tekniske felter defineres centralt. En ændring af feltets synlige navn må ikke ændre det stabile felt-ID. Billeder bliver i WordPress Media Library; modulrecords gemmer kun attachment IDs.

## Eventmodul – designprincip

**VD-EVENT-MODULE-001** gør Events til dynamiske data i den fælles ModuleStore. Eventliste og Eventdetalje gemmer kun binding/design, ikke kopier af eventdata. Eventliste kan vise kommende, afholdte eller alle publicerede events, så historiske events bevares.
