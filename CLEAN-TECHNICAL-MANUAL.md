# Visual Designer Manager – Teknisk manual og beslutningsregister

Senest opdateret: 28. august 2026  
Gælder for: Visual Designer Manager 0.1.x og nyere  
Status: **Autoritativ reference for tekniske adfærdsregler, UX-kontrakter og godkendte implementeringsvalg**

> Denne manual supplerer `CLEAN-DESIGN-MANUAL.md`. Designmanualen beskriver målarkitekturen og de overordnede visuelle principper. Denne tekniske manual beskriver de **konkrete adfærdsregler og beslutninger**, som implementeringen og QA skal overholde.

---

## 1. Formål

Manualen har fire formål:

1. Fastholde konkrete tekniske og brugeroplevelsesmæssige beslutninger, så de ikke ændres utilsigtet senere.
2. Gøre det muligt at opdage, når et nyt ønske er i konflikt med en tidligere godkendt regel.
3. Give udvikling og QA præcise **interaction contracts** – altså hvad der skal ske før, under og efter en brugerhandling.
4. Være grundlag for løbende teknisk review, hvor nye forbedringsforslag kan vurderes uden at blande dem sammen med allerede godkendte krav.

### Konfliktregel

Hvis et nyt ønske strider mod en regel i denne manual, må implementeringen **ikke stille og roligt ændre den eksisterende adfærd**.

I stedet skal konflikten gøres tydelig:

- Hvilken eksisterende beslutning kolliderer det nye ønske med?
- Hvad er fordelen ved det nye forslag?
- Hvilke eksisterende funktioner, data eller workflows påvirkes?
- Skal den gamle regel bevares, ændres eller erstattes?

Først når ændringen er accepteret, opdateres denne manual og derefter kode, QA og bruger-/designmanualer efter behov.

---

## 2. Dokumenthierarki

Dokumenterne har forskellige roller:

| Dokument | Autoritet |
|---|---|
| Aktuel kode + `clean-update.json` | Hvad der faktisk er frigivet/implementeret |
| `CLEAN-DESIGN-MANUAL.md` | Godkendt målarkitektur og overordnet designmodel |
| **`CLEAN-TECHNICAL-MANUAL.md`** | Godkendte konkrete adfærdsregler, UX-kontrakter og tekniske valg |
| Backlog / handover | Kommende arbejde og rækkefølge |
| `CLEAN-USER-MANUAL.md` | Hvordan brugeren anvender systemet |
| `DESIGN-MANUAL.md` | Legacy/reference |

Ved konflikt mellem designmanualen og denne manual skal forskellen afklares, før der implementeres. De to dokumenter skal normalt være konsistente.

---

## 3. Grundlæggende systemkontrakter

### 3.1 Canonical model er sandheden

- DOM er aldrig Save-kilde.
- Hvert element har stabilt `id`, `type`, `parentId`, `order`, `geometry` og `props`.
- Layoutændringer skal kunne rekonstrueres efter Save/Reload.
- CSS må visualisere modellen, men må ikke være eneste lagringssted for en layoutbeslutning.
- Save, Preview, Undo/Redo, Restore og frontend skal arbejde ud fra samme model.

### 3.2 Ét element må ikke skifte type ved en UI-genvej

Når brugeren vælger en elementtype i paletten, skal der oprettes den valgte canonical type.

Eksempel:

- `+ Tekst` → `type = text`
- `+ Billede` → `type = image`
- `+ Knap` → `type = button`

En Knap må **ikke** oprettes som Tekst og derefter forsøges gjort knap-lignende via properties eller CSS.

Type-label, Inspector, renderer, drag/drop og Save-model skal alle være enige om elementets type.

### 3.3 Editor-chrome må ikke ændre frontend-geometri

Labels, type/id-visning, drag handles, resize handles, selectionrammer og drop-guides er editor-chrome.

De må ikke:

- ændre canonical `x/y/w/h`;
- skabe ekstra fysisk højde eller bredde;
- påvirke parent auto-grow;
- dukke op på frontend.

---

## 4. Rich-text interaction contracts

### 4.1 Selection skal bevares ved formattering

Dette er en fast UX-regel.

Når brugeren markerer tekst og anvender en formatteringskommando, skal den markerede tekst **forblive markeret efter kommandoen**.

Gælder mindst:

- Fed;
- Kursiv;
- Understregning;
- øvrige rich-text toolbar-kommandoer, hvor det teknisk giver mening.

Godkendt flow:

```text
1. Markér teksten "direkte"
2. Klik Fed
3. "direkte" bliver fed
4. "direkte" er STADIG markeret
5. Klik Kursiv
6. Samme tekst bliver også kursiv
7. Selection er STADIG aktiv
8. Klik Understregning
9. Samme selection får også understregning
```

Brugeren skal altså kunne kæde flere formatteringer uden at markere teksten igen.

### 4.2 Fokus må ikke være lig med tab af selection

Toolbaren må gerne modtage pointer-/keyboard-interaktion, men implementeringen skal bevare den relevante editor-Range.

Teknisk princip:

- gem selection/range før toolbar-handlingen kan flytte fokus;
- udfør kommandoen mod den gemte range;
- rekonstruer/gendan selection efter DOM-opdatering;
- re-render må ikke unødigt ødelægge selection.

Hvis native `Selection`/`Range` ikke overlever DOM-normalisering, gemmes logiske tekst-offsets og gendannes mod den nye DOM.

### 4.3 Toolbar-kommandoer skal dele selection-mekanisme

Fed, Kursiv og Understregning må ikke have tre forskellige selection-løsninger.

Der skal være én fælles mekanisme til:

1. capture;
2. validate;
3. apply;
4. restore.

Det reducerer regressioner, hvor én knap virker anderledes end de andre.

### 4.4 Re-render skal minimeres under aktiv tekstredigering

Hvis en formatteringsændring kan opdateres lokalt uden fuld Inspector/canvas re-render, foretrækkes dette. Fuld re-render må kun bruges, hvis modellen kræver det, og selection/fokus skal derefter gendannes.

---

## 5. Drag/drop og layoutkontrakter

### 5.1 Over/Under splitter den valgte celle

Over/Under betyder ikke automatisk en ny fuldbredde række.

Når et element droppes Over eller Under et konkret element, deles **den valgte celle** lodret.

Eksempel:

```text
┌───────────────┬───────────────┐
│    Billede    │               │
├───────────────┤     Tekst     │
│     Tekst     │               │
└───────────────┴───────────────┘
```

Højre element kan dermed konceptuelt spænde over to rækker.

### 5.2 Venstre/Højre splitter cellen vandret

Venstre/Højre deler den valgte celle og placerer elementerne side om side.

Drop-guides skal visuelt gøre det tydeligt, hvilken celle der deles.

### 5.3 Ind i bruges kun til containere

`Ind i` giver mening på Sektion og Kasse, ikke på almindelige leaf-elementer.

### 5.4 Hierarkiet skal håndhæves

- Sektion: kun direkte på Side/root.
- Kasse: i Sektion eller Kasse.
- Normale leaf-elementer: i Sektion eller Kasse.
- **Flydende Knap er den eksplicitte leaf-undtagelse** og må placeres på Side/root, i Sektion eller Kasse.
- Kasse må indeholde Kasse.
- Sektion må ikke nestes som almindelig Kasse.

---

## 6. Knap-kontrakter

### 6.1 Knap er en selvstændig elementtype

Knap har egen canonical type, egen label og eget Inspector-panel.

Editor-label skal vise fx:

`KNAP · <id>`

og aldrig `TEKST · <id>`.

### 6.2 Normal Knap

En normal Knap deltager i almindeligt LEGO/grid-layout og kan placeres via Over/Under/Venstre/Højre. Normal er en bevidst tilstand, som kan vælges i Inspector.

Når **Knap trækkes fra paletten**, er den godkendte standard derimod **Flydende**, så indsættelsen ikke først går gennem almindelig celle-split.

### 6.3 Flydende Knap

En Flydende Knap er et **parent-relativt overlay**, ikke et normalt grid-element.

Den skal:

- kunne bruges på Side-root, Sektion eller Kasse;
- have fri X/Y-position inden for parent;
- flytte med parent;
- aldrig være `position: fixed` mod browserens viewport;
- ikke reservere almindelig grid-celle eller række;
- ikke skubbe søskende;
- ikke udløse parent auto-grow alene på grund af sin floating-position;
- kunne overlappe almindeligt indhold med vilje uden normal overlap-fejl;
- have breakpoint-specifik geometri for Desktop/Laptop/Mobil.

**Editor-stacking:** En Flydende Knap skal altid være visuelt over normale editor-elementer, også når et andet element vælges. Selection-chrome må ikke skabe et stacking-context, der skjuler floating. Canonical `zIndex` bevares til rækkefølge mellem flere floating-elementer og frontend; editorens top-lag er separat chrome-adfærd.

### 6.4 Floating må ikke skjules som CSS-only hack

Floating-status skal være en model-egenskab/layouttilstand, som kan Save/Reloades og gengives ens i editor, Preview og frontend.

---

## 7. Linkmodel

Knap, Billede og Icon skal så vidt muligt bruge **samme fælles linkmodel**.

Godkendte linktyper:

- Ingen;
- Intern side;
- Ekstern URL;
- Anker;
- E-mail;
- Telefon.

Hvor relevant:

- Åbn i ny fane;
- senere eventuelt `nofollow`/andre relationer.

Det skal undgås, at hvert element udvikler sit eget inkompatible URL-format.

---

## 8. Billede-kontrakter

### 8.1 Billedboks og billedindhold er separate lag

Ydre billedboks styrer canonical elementgeometri.

Selve billedet inde i boksen kan have egen visning/geometri.

### 8.2 Resize handles ændrer billedboksen

De almindelige grønne resize handles ændrer den ydre boks, ikke automatisk det indre billedes manuelle størrelse.

### 8.3 Manuel billedtilstand er uafhængig

Ved Manuel:

- inner X/Y/W/H gemmes separat;
- resizing af boksen må ikke automatisk ændre billedets manuelle W/H;
- lås proportioner er standard slået til;
- radius på boksen klipper billedindholdet.

### 8.4 Billede som link

Hele billedets fysiske klikområde skal følge billedboksen, når Billede bruges som link. Linket må ikke ændre canonical geometri.

Status: godkendt krav til kommende implementering.

---

## 9. Container- og auto-grow-kontrakter

### 9.1 Auto-grow

For Sektion og Kasse gælder:

```text
faktisk højde = max(manuel minimumshøjde, nødvendig indholdshøjde)
```

### 9.2 Container må krympe igen

Når børn flyttes eller slettes, skal parent kunne krympe igen, men aldrig under manuel minimumshøjde.

### 9.3 Følgende indgår i nødvendig højde

- child geometry;
- padding;
- border;
- lodret spacing;
- aktiv breakpoint-geometri.

Editor-labels indgår ikke.

---

## 10. Inspector-kontrakter

### 10.1 Inspector har egen scroll

På desktop skal Inspector kunne rulles uafhængigt af browservinduet, så nederste felter altid kan nås.

### 10.2 Ekstra scroll-buffer nederst

Der må være kunstig tom plads nederst i Inspectorens scroll-indhold for at sikre, at de sidste kontroller kan rulles komfortabelt op fra browserkanten.

Denne plads er kun editor-UI og må ikke påvirke canonical model eller frontend.

Aktuelt aftalt mål: ca. **360 px scroll-buffer**; værdien kan finjusteres som UI-konstant uden modelmigration.

---

## 11. Tabel-kontrakter

Status: godkendt mål for kommende native Tabel-element.

### 11.1 Grundfunktioner

Tabel skal kunne håndtere:

- tilføj/fjern rækker;
- tilføj/fjern kolonner;
- rækkefølge;
- valgfri header-række;
- celleindhold;
- kolonnebredder;
- alignment;
- tekst-/baggrundsfarver;
- padding;
- responsive strategier.

### 11.2 Flere celler skal kunne markeres

Tabel skal understøtte selection af én eller flere celler, så styling kan anvendes på et område.

### 11.3 Excel-lignende border control

For markerede celler skal brugeren kunne vælge:

- Ydre;
- Indre;
- Alle;
- Vandret;
- Lodret;
- Top;
- Bund;
- Venstre;
- Højre;
- Ingen.

For border-selection styres mindst:

- tykkelse;
- farve;
- solid/dashed/dotted.

### 11.4 Mobilstrategier

Tabel skal kunne tilbyde relevante mobile strategier, fx:

- vandret scroll;
- skjul valgte kolonner;
- stablet label/værdi-kort.

Strategien skal være et bevidst responsive valg og ikke tilfældig browser-overflow.

---

## 12. Divider, Spacer og Icon

Status: godkendte kommende elementtyper.

### Divider

Visuel skillelinje med bredde, tykkelse, farve, alignment, spacing og senere stregtype.

### Spacer

Selvstændig tom layoutblok. Skal ikke bruges som erstatning for normal Afstand X/Y.

### Icon

Grafisk element til fx telefon, mail, sociale medier, pil, info og download. Skal kunne bruge fælles linkmodel.

---

## 13. Hero / Topbanner

Hero/Topbanner skal **ikke** være en separat layoutmotor.

Det skal implementeres som Sektion-preset/specialisering, så samme hierarchy, canonical model og responsive motor genbruges.

Godkendte mål-egenskaber:

- background image;
- Cover/Contain/manuel placering;
- focal point;
- overlay-farve/gennemsigtighed;
- min/fast højde;
- responsive højde;
- normale child-elementer som Tekst, Knap, Icon og Kasse.

Hero/Topbanner er sideindhold og må ikke forveksles med global Header.

---

## 14. Menu

Menu skal være et visuelt element, mens menuens data/struktur forbliver separat WordPress-/Manager-data.

Det betyder:

- Menu-elementet vælger datakilde/menu;
- Visual Designer styrer visning og responsive layout;
- Header/Footer må ikke hardcode en parallel menustruktur.

Planlagte visuelle indstillinger:

- typografi;
- farver;
- afstand;
- hover;
- aktiv side;
- alignment;
- mobil/hamburger-adfærd.

---

## 15. Header, Footer og Tema/Shell

### 15.1 Header/Footer er globale modeller

Header og Footer har egne modeller og egen ikke-destruktiv versionshistorik.

De bruger samme layoutmotor som Side Designer; der må ikke opstå en separat Header/Footer-layoutmotor.

### 15.2 Konvertering skal være 1:1 før cutover

Den eksisterende Header/Footer på Hangar18-testmiljøet bruges som visuel baseline.

Cutover må først ske efter parity-QA på:

- Desktop;
- Laptop;
- Mobil;
- højde/bredde;
- logo;
- menu;
- spacing;
- baggrunde;
- typografi;
- mobilmenu;
- overgang Header → Side → Footer.

### 15.3 Temaet skal være en tynd shell

Temaet beholder WordPress-ansvar som lifecycle, hooks, wrappers og fallback, men må ikke have parallelle designregler, som konkurrerer med Visual Designer.

---

## 16. Responsive kontrakter

Desktop, Laptop og Mobil er views af **samme elementer**, ikke kopier af siden.

- samme ID;
- samme type;
- samme parent/order;
- samme indhold;
- breakpoint-specifik geometri.

Arv:

- Laptop arver Desktop;
- Mobil arver effektiv Laptop/Desktop;
- bruger kan lave lokal override;
- override kan nulstilles til arv.

Responsive ændringer skal overleve Save/Reload og må ikke skabes alene via midlertidig CSS.

---

## 17. Versionering og ikke-destruktiv adfærd

- Hver rigtig Save opretter ny Visual Designer-version.
- Historiske versioner slettes ikke ved restore.
- Restore bliver en ny version.
- Create copy laver ny WordPress-kladdeside med egen historie.
- Preview af usavet state ændrer ikke offentlig side.

Global Header/Footer har tilsvarende separat historik.

---

## 18. Dokumentationskontrakt

Brugerrettede funktioner skal dokumenteres i `CLEAN-USER-MANUAL.md`.

Komplekse begreber skal, hvor det hjælper forståelsen, have:

- grafiske illustrationer;
- layoutdiagrammer;
- screenshots;
- før/efter-eksempler;
- tydelig markering af **Planlagt** kontra **Frigivet**.

Illustrationer skal afspejle canonical model og må ikke vise en alternativ arkitektur.

---

## 19. QA som kontrakttest

QA skal ikke kun teste, om funktionen "ser rigtig ud". Den skal teste kontrakten.

Eksempler:

### Rich text

- markér tekst;
- klik Fed;
- kontrollér format;
- kontrollér at samme tekst stadig er selected;
- klik Kursiv;
- kontrollér kombination og selection;
- klik Understregning;
- kontrollér kombination og selection.

### Knaptype

- drag Knap fra palette;
- canonical type skal være `button`;
- label skal være KNAP;
- Inspector skal være Knap-Inspector;
- Save/Reload må ikke konvertere den til Tekst.

### Floating

- skift Knap til Floating;
- flyt over Tekst/Billede;
- sibling geometry må ikke ændres;
- parent må ikke vokse alene pga. floating-position;
- Save/Reload/Preview/frontend skal matche.

### Inspector

- vælg element med mange Inspector-felter;
- rul helt til sidste felt;
- sidste felt skal kunne flyttes komfortabelt op fra viewport-bunden ved hjælp af scroll-buffer.

---

## 20. Beslutningsstatus

Hver teknisk beslutning kan have én af disse statustyper:

| Status | Betydning |
|---|---|
| **FAST** | Godkendt kontrakt; må ikke ændres uden eksplicit beslutning |
| **GODKENDT MÅL** | Godkendt funktion/retning, endnu ikke nødvendigvis implementeret |
| **IMPLEMENTERET** | Findes i aktuel kode/release; verificér mod `clean-update.json` |
| **BUG** | Implementeringen bryder en FAST/GODKENDT kontrakt |
| **FORSLAG** | Teknisk forbedringsidé, endnu ikke godkendt |

Denne manual beskriver primært FAST og GODKENDT MÅL. Implementationsstatus må altid verificeres mod aktuel kode og release-manifest.

---

## 21. Kontraktstatus for 0.1.38

### VD-FLOAT-001 – Flydende Knap

**IMPLEMENTERET / stacking rettet i 0.1.34.** Palette-Knap starter fortsat som Flydende før drop-zonen beregnes. 0.1.34 fjerner normal-elementers editor stacking-context og giver Flydende Knap et separat top-lag, så den ikke forsvinder, når et andet element markeres. Canonical `zIndex` bevares og bruges til rækkefølge mellem flere floating-elementer og på frontend.

### VD-TEXT-SEL-001 – Rich-text selection

**PASS i bruger-QA på 0.1.38 / regressionsbeskyttet i 0.1.39.** Cold-start selection-sessionen etableres ved afsluttet tekstmarkering, før første toolbar-klik. `v0125` er eneste autoritative selection-ejer, og legacy-lag må ikke aktivere egne restore-loops. Bruger-QA bekræftede, at Fed/Kursiv/Understregning nu bevarer markeringen som krævet.

**FAST owner-regel:** Legacy rich-text-filer må aldrig afgøre delegation ud fra et konkret release-nummer. Hvis `H18RichTextV0125.selectionOwner` er sat, er v0125 den eneste selection-ejer.

### VD-PAGES-001 – Opret side fra Manager

**IMPLEMENTERET i 0.1.39.** Sider kan oprettes direkte fra Managerens Sider-modul med titel, valgfri slug, overordnet side og status. Efter oprettelse åbnes siden direkte i Visual Designer. Oprettelse af en side opretter ikke automatisk en Visual Designer-version; første rigtige Gem opretter v1.

### VD-MENU-001 – WordPress-menu som visuelt element

**IMPLEMENTERET i 0.1.39 for Header/Footer Designer.** Canonical `type=menu` gemmer reference til en eksisterende WordPress-menu og designindstillinger, men ikke en kopi af menupunkterne. Menu Inspector styrer retning, alignment, mobilstrategi, farver, typografi, afstand, padding og baggrund. Mobilstrategier er Hamburger, Lodret og Ombryd. Theme Shell-cutover er fortsat separat og OFF, indtil parity er godkendt.

### VD-BUTTON-TYPE-001 – Knap er Knap

**IMPLEMENTERET / uændret.** Palette-Knap er canonical `type=button` og starter med `placementMode=overlay`. Normal kan fortsat vælges i Inspector.

### VD-FLOAT-STACK-001 – Floating altid over normale editor-elementer

**IMPLEMENTERET i 0.1.34.** Floating får et særskilt editor-toplag. Valg/selection af Tekst, Billede, Kasse eller Sektion må ikke skjule den flydende Knap. Dette editorlag ændrer ikke den canonical lagværdi.

### VD-COLOR-001 – Inspector farvevælger

**IMPLEMENTERET i 0.1.35 – afventer bruger-QA.** Inspector bruger sin egen farvevælger og må ikke afhænge af operativsystemets native `type=color`-dialog. UI har saturation/brightness-felt, hue-slider, HEX-input, preview og farvechips. Canonical værdi er fortsat `#RRGGBB`.

Godkendelsestest: vælg en tydelig grøn farve, klik **Anvend**, og verificér samme HEX i Inspector, canvas og efter Save/Reload uden at tidligere sort/lav luminans hænger ved.


### VD-COLOR-POPOVER-001 – Global farvevælgerplacering

**BUGFIX i 0.1.36 – afventer bruger-QA.** Farvevælgeren er én fælles Inspector-popover for alle elementtyper og alle `type=color`-felter. Mens den er åben, flyttes panelet til `document.body`, positioneres som viewport-relativ editor-chrome og clamped til den synlige viewport. Den forsøger først at holde hele panelet inden for Inspectorens vandrette område og vælger derefter en viewport-fallback. Inspector `overflow` må aldrig klippe farvevælgeren. Scroll og resize genberegner placeringen.

### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer

**PASS i bruger-QA på 0.1.32 / uændret i 0.1.35.** Inspectorens ca. 360 px editor-only bund-buffer fungerer som aftalt og påvirker ikke canonical model, Preview eller frontend.

---

## 22. Teknisk review – forslag til forbedringer

Følgende er **FORSLAG**, ikke godkendte ændringer. De er med for at gøre manualen nyttig som reviewværktøj.

### FORSLAG-A – Central capability registry

Opret ét centralt register pr. elementtype med fx:

```text
type
allowedParents
canContainChildren
supportsLink
supportsFloating
supportsBorder
supportsBackground
supportsRadius
supportsRichText
supportsResponsiveGeometry
```

Fordel: Palette, Inspector, drag/drop, renderer og QA kan bruge samme kontrakt og dermed mindske fejl som "Knap bliver Tekst".

### FORSLAG-B – Fælles LinkValue-model

Indfør én serialiserbar linkstruktur for Knap/Billede/Icon/Menu-relaterede actions.

Fordel: færre særregler og enklere migration/QA.

### FORSLAG-C – Interaction contract tests

Lav automatiske browser-/DOM-tests omkring handlinger, ikke kun model-unit-tests.

Eksempel: selection → Bold → samme Range selected.

Fordel: regressionsfejl i fokus, selection og drag/drop opdages før release.

### FORSLAG-D – Inspector sections som collapsible grupper

Opdel lange Inspector-paneler i fx:

- Indhold;
- Layout;
- Typografi;
- Baggrund;
- Ramme;
- Link;
- Responsive;
- Avanceret.

Fordel: mindre scrollbehov og lettere navigation. Scroll-bufferen beholdes stadig som sikkerhed.

### FORSLAG-E – Design tokens frem for gentagne rå værdier

Global spacing, radius, font sizes og farver kan få navngivne tokens med lokal override.

Fordel: mere konsistent design og lettere global ændring.

### FORSLAG-F – Explicit edit transaction

Handlinger som drag, resize og rich-text formattering bør have tydelig begin/update/commit-model.

Fordel: bedre Undo/Redo, selection-preservation og automatiske versionsnoter.

### FORSLAG-G – Contract IDs i kode og QA

Vigtige regler kan få stabile ID'er, fx:

- `VD-TEXT-SEL-001`
- `VD-BUTTON-TYPE-001`
- `VD-FLOAT-001`
- `VD-IMG-INNER-001`

QA-fejl kan så direkte pege på kontrakten.

---

## 23. Procedure ved nyt ønske

Når et nyt krav kommer ind:

1. Find berørte kontrakter i denne manual.
2. Afgør om ønsket er:
   - kompatibelt;
   - en udvidelse;
   - eller en konflikt.
3. Ved konflikt: forklar konsekvensen og få beslutning før implementering.
4. Opdatér denne manual, hvis den godkendte adfærd ændres.
5. Opdatér designmanual/backlog/bruger manual efter relevans.
6. Implementér.
7. Tilføj kontraktbaseret QA.
8. Release først, når den aftalte pakke skal bygges.

---

## 24. Procedure ved teknisk review

Ved et periodisk review gennemgås manualen for:

- duplikerede mekanismer;
- special cases der bør samles i fælles model;
- UX-regler som ikke har automatiske tests;
- properties der kun findes i CSS/DOM og ikke canonical model;
- forskelle mellem editor, Preview og frontend;
- planlagte funktioner, som påvirker eksisterende contracts;
- muligheder for simplere Inspector og bedre responsiv adfærd;
- dokumentation der er blevet forældet.

Reviewet må gerne producere FORSLAG, men må ikke ændre FAST-regler uden eksplicit beslutning.

---

## 25. Kort huskeregel

Når Visual Designer udvikles, skal vi kunne svare **ja** til tre spørgsmål:

1. **Er adfærden entydigt beskrevet?**
2. **Kan den gemmes og rekonstrueres fra canonical model?**
3. **Kan QA bevise, at brugerens handling giver samme resultat hver gang?**

Hvis ikke, er funktionen ikke teknisk låst endnu.


## 22. WYSIWYG viewport- og containerkontrakt · 0.1.44

### VD-CONTAINER-PAINT-001 · IMPLEMENTERET 0.1.44
Sektion og Kasse ejer hele deres fysiske canonical geometri. Baggrund, ramme og radius må ikke afhænge af, om child-elementer fylder højden. Den indre child-surface er transparent og fylder hele parentens geometri. Manuel højde er et minimum; required child height kan autogrow parenten. Editor-labels/handles er chrome og tæller ikke i layoutgeometrien.

### VD-WYSIWYG-VIEWPORT-001 · IMPLEMENTERET 0.1.44
Designerens layoutbredde må aldrig være den tilfældige restbredde mellem WordPress-adminmenu, Elementer og Inspector. Layout beregnes ved en virtuel frontend-viewport: Desktop 1920 px, Laptop 1180 px og Mobil 390 px. Editorens tilgængelige plads styrer kun Fit-zoom.

### VD-WYSIWYG-FIT-001 · IMPLEMENTERET 0.1.44
Fit-zoom genberegnes dynamisk ved ResizeObserver på canvas-kolonnen samt ved breakpointskift, Mere canvas og foldning af Elementer/Inspector. Ændret Fit må aldrig mutere canonical x/y/w/h eller responsive inheritance. Drag/resize og pixelbaserede editorfunktioner skal omsætte fysiske pointer-deltaer tilbage til virtuelle pixels/8px-rækker.


---

## 22. Kontraktstatus for 0.1.45

### VD-TEXT-VALIGN-001 – IMPLEMENTERET, afventer bruger-QA

- Tekst har en canonical `verticalAlign` med værdierne `top`, `center`, `bottom`.
- Eksisterende Tekst uden property skal normaliseres til `top`, så gamle layouts ikke flytter sig.
- Inspector viser særskilt vandret og lodret justering.
- Designer, Preview og frontend skal bruge samme property.

### VD-IMAGE-MIME-001 – IMPLEMENTERET, afventer bruger-QA

- Billede-elementets medievælger filtrerer på WordPress `image/*`, ikke på en hårdkodet filendelse.
- PNG, inkl. alpha/transparens, må ikke konverteres eller flades ud af Visual Designer.
- JPG/JPEG, WebP, GIF og andre image-formater følger WordPress-installationens tilladte MIME-typer.
- SVG er kun tilgængelig hvis WordPress-installationen selv tillader SVG-upload.

### VD-FOOTER-LEGACY-SOURCE-001 – IMPLEMENTERET, afventer bruger-QA

Kildeprioritet ved gammel Footer-konvertering:

1. global Footer-assignment i den gamle Visual Header/Footer Builder;
2. præcis én gammel Footer-template hvis ingen global assignment findes;
3. gammel `HANGAR18-FOOTER-START/END` shell på Hjem eller anden side;
4. gammel Manager-standard som eksplicit fallback.

Hvis flere gamle Footer-templates findes uden entydig assignment, må systemet ikke gætte hvilken af dem der var aktiv. En standardfallback skal mærkes som fallback og må ikke beskrives som 1:1-konvertering.

### VD-CANVAS-ZOOM-001 – IMPLEMENTERET, afventer bruger-QA

- Virtuel viewport fra VD-WYSIWYG-VIEWPORT-001 ændres aldrig af zoom.
- Musehjul over canvas zoomer designet 25-200% i 10 procentpoint-trin.
- Zoom forankres omkring musemarkørens virtuelle punkt.
- Ved overflow viser canvas-host vandret/lodret scrollbar; Elementer, Inspector og toolbar zoomes ikke.
- `Fit` genberegnes ved ændret editorbredde, Mere canvas og panel-foldning.
- Manuel zoom forbliver fast ved de samme ændringer.
- Skift mellem Desktop/Laptop/Mobil går tilbage til `Fit` for den nye virtuelle viewport.
- Alle pointerbaserede layoutoperationer bruger fortsat den aktuelle viewport-scale til at oversætte skærmpixels til virtuelle layoutkoordinater.


## 0.1.46 – Footer/preview/Fit/rich-text parity

### VD-GLOBAL-PREVIEW-001
Header/Footer lokal preview må ikke kræve browser-popup-tilladelse. Preview vises i en intern overlay/modal og må ikke bruge popup som normalmekanisme.

### VD-FOOTER-REFERENCE-001
Hvis hverken gammel Visual Header/Footer Builder-kilde eller HANGAR18-FOOTER-shell findes, bruges den godkendte Desktop-reference fra 29-08-2026 som eksplicit visuel fallback. Den må ikke beskrives som 1:1-kildekonvertering.

### VD-CANVAS-START-FIT-001
Designer starter altid i Fit ved ny editor-entry, reload/pageshow og breakpointskift. 100% og anden manuel zoom er kun sessionens manuelle visningsvalg.

### VD-RICHTEXT-SPACING-001
Temaets globale CSS må ikke ændre Visual Designer Tekst-elementets paragraph-, liste- eller link-spacing. Designer og frontend ejer disse baselines deterministisk.


## 0.1.47 – stabilisering før Menu-UX

- **VD-TEXT-SEL-001:** BUG-02 er permanent release-gate. `v0125-authoritative` + `prearmed-v0138` må ikke fjernes; første og kædede Fed/Kursiv/Understregning skal bevare native selection.
- **VD-TEXT-FLEX-001:** lodret Tekst-justering arbejder på én samlet content-wrapper. Inline `EM`, `STRONG`, `U` og `A` må aldrig blive selvstændige flex-items.
- **VD-VIEWPORT-EDGE-001:** X=0/Y=0/W=120 refererer til den faktiske virtuelle side. Editor-padding/border er chrome uden for canonical sidegeometri.
- **VD-SAVE-NOOP-001:** brugerens Gem må ikke oprette ny Side/Header/Footer-version, hvis canonical model og relevante settings/valg er identiske med seneste gemte state. En ændringsnote alene er ikke en ændring. Restore/konvertering kan fortsat være eksplicit non-destruktive versionshandlinger.
- **VD-LANDING-PREVIEW-001:** en separat Visual Designer Hjem-kladdeside kan bruges til Header + Side + Footer parity uden at ændre gammel Hjem eller `page_on_front`. Samlet preview bruger canonical modeller og Theme Shell forbliver OFF.
- **VD-MENU-UX-NEXT:** næste hovedarbejdsspor er en mere brugervenlig Menu-oplevelse; WordPress-menu-ID forbliver canonical datakilde.


## 0.1.48 – Lag, parity og legacy-oprydning

- Venstre Designer-panel har `Elementer | Lag`; Lag-træet er editor-chrome og ændrer aldrig canonical modellen.
- Klik på et Lag vælger den tilsvarende canvas-node, også når den er fysisk dækket af en anden node.
- Button border/background/radius skal males på samme synlige surface i Designer, lokal Preview og frontend.
- Legacy Header/Footer converter UI og automatisk runtime er retired; historiske klasser må kun eksistere dormant for QA/data-kompatibilitet.
- Editor entry og breakpointskift starter i Fit.
- Theme Shell er fortsat OFF.
- Synligt theme-navn er AKVPK; intern `hangar18-base` slug/Text Domain bevares.


## 0.1.49 – Aktiv Theme Shell og Hjemmeside

### VD-SHELL-LIVE-001
Når Theme Shell er aktiv på en side med canonical Visual Designer-model, er live-rendering: valgt/Auto Header → sidens canonical model → valgt/Auto Footer. Alle tre dele bruger samme `Renderer::renderModel()` som preview.

### VD-SHELL-FALLBACK-001
Theme Shell må ikke overtage legacy/non-Visual-Designer sider under overgang. Hvis en resolved Header/Footer mangler, er inaktiv, tom eller fejler, udelades kun den del; sideindholdet skal fortsat rendres.

### VD-HOME-001
Visual Designer Manager → Sider er autoritativ UX for at vælge hjemmesiden. Handlingen må kun vælge en Visual Designer-side, publicerer den ved behov efter capability-check og skriver WordPress-standarderne `show_on_front=page` + `page_on_front=<ID>`. Den gamle forside slettes ikke.

### VD-CUTOVER-0149
0.1.49 er det eksplicit godkendte Header/Footer cutover. Cutover aktiveres én gang ved runtime og markerer `h18_visual_designer_theme_shell_cutover_v1=1`. Menu-redesign er ikke en del af denne kontrakt.


## 0.1.50 – Sidekonvertering og AKVPK teknisk theme-identitet

### VD-CONVERSION-STAGE-001
Konvertering af en eksisterende WordPress-side skal være staging-only indtil eksplicit godkendelse. Original `post_content` overskrives ikke. Batch-konvertering må oprette kandidater, men må ikke aktivere dem.

### VD-CONVERSION-SHELL-001
Legacy Header/Footer-markører fjernes fra kandidatens body, fordi Visual Designer Header/Footer allerede leveres af den aktive globale shell. Kandidat-preview skal bruge samme canonical Renderer.

### VD-THEME-AKVPK-001
Det officielle WordPress-theme hedder og installeres teknisk som `akvpk`. Migration fra historisk `hangar18-base` skal bevare theme_mods/menu-locations og Custom CSS før theme-switch. Theme URI er `https://akvpk.dk/`.

## 0.1.54 – Menu UX og sidestatus

### VD-MENU-UX-002
- WordPress `nav_menu`/`nav_menu_item` er fortsat canonical datakilde for navigation. VDM må ikke oprette en parallel menustruktur i Header/Footer.
- Manager → Menu er den primære brugervenlige redigering: rækkefølge kan ændres med drag-and-drop og tastaturvenlige pile; undermenu vælges eksplicit via parent.
- Menu-elementet gemmer kun menu-reference og design/responsive egenskaber.
- Desktop/Laptop/Mobil bruger samme menupunkter. Breakpointet ændrer præsentationen, ikke datasættet.
- Hamburger understøtter Dropdown, Panel fra højre og Panel fra venstre. `aria-expanded`, `aria-controls`, Esc, klik udenfor og valgfri luk-efter-valg er faste accessibility/UX-kontrakter.

### VD-PAGE-STATUS-001
- Side-Designer viser og ændrer WordPress' rigtige `post_status`; der oprettes ingen separat Visual Designer-publiceringsstatus.
- Kladde kan publiceres fra Designer, hvis brugeren har `publish_pages`.
- En publiceret side kan gøres til kladde med eksplicit bekræftelse.
- Statusændringen går gennem samme Save-submit som canonical layoutet, så aktuelle Designer-ændringer ikke tabes ved publicering/afpublicering.
- Header/Footer templates har ikke denne kontrol; den gælder almindelige WordPress-sider.

## 0.1.55 – Sidehandlinger

### VD-PAGES-ACTIONS-001
- Manager → Sider viser publiceringsstatus og sidehandlinger uden at sammenblande publicering og hjemmesidevalg.
- `Publicér` ændrer kun WordPress `post_status` til `publish`.
- `Gør til kladde` ændrer kun WordPress `post_status` til `draft` og kræver en tydelig bekræftelse i UI.
- `Sæt som Hjem` kræver, at siden allerede er publiceret, og ændrer kun `show_on_front=page` + `page_on_front=<ID>`; handlingen må ikke auto-publicere.
- `Slet` er en recoverable handling og bruger WordPress-papirkurven (`wp_trash_post`) efter bekræftelse. Permanent sletning er ikke en normal VDM-sidehandling.
- Den aktive hjemmeside må ikke gøres til kladde eller flyttes til papirkurven. Brugeren skal først vælge en anden publiceret Visual Designer-side som Hjem.
- `Designer`, `WordPress` og `Vis` forbliver separate navigationshandlinger.
- Denne kontrakt superseder auto-publiceringsdelen af `VD-HOME-001` fra 0.1.49; hjemmesidevalget er fra 0.1.55 selection-only.

## 0.1.56 – Forenklet visuel Menu-administration

### VD-MENU-UX-003
- Manager → Menu viser som standard den valgte menus faktiske menupunkter; WordPress-tekniske felter, theme-locations, flere menuer og historik ligger under **Avancerede indstillinger**.
- Menupunkter kan flyttes visuelt med drag-and-drop samt tastaturvenlige op/ned-knapper. `↳` gør et punkt til undermenu under forrige punkt, og `←` flytter ét niveau ud. Backend validerer fortsat parent-grafen mod cycles og ugyldige parents.
- **+ Tilføj menupunkt** åbner en dialog med tre enkle valg: publicerede WordPress-sider, eksternt link eller overskrift/gruppe. Kladder vises ikke som valgbare sider, og en side der allerede er i menuen kan ikke tilføjes igen via standarddialogen.
- Menutekst kan ændres uden at ændre WordPress-sidens titel. **Fjern fra menu** sletter kun `nav_menu_item`; destinationssiden slettes aldrig.
- Struktur-preview opdateres i browseren ved ændret rækkefølge, nesting eller menutekst. Preview viser kun informationsarkitektur; typografi/farver/layout styres fortsat af Visual Designer Menu-elementet.
- WordPress `nav_menu` / `nav_menu_item` er fortsat den eneste canonical datakilde. Versionssnapshots og restore-kontrakten fra VD-MENU-UX-002 bevares.



## 0.1.57 – Menu-save og runtime-identitet

### VD-MENU-CLASS-SERIALIZATION-001
- Alle kald til WordPress `wp_update_nav_menu_item()` skal sende `menu-item-classes` som en whitespace-separeret streng, aldrig som PHP-array.
- Eksisterende CSS-klasser normaliseres med `sanitize_html_class`, dubletter fjernes, og tomme værdier udelades.
- Reglen gælder både almindelig Gem menu, oprettelse af overskrift/gruppe og gendannelse fra navigation-snapshot.
- En eksisterende menu med én eller flere CSS-klasser må ikke kunne udløse PHP `TypeError` i WordPress `nav-menu.php`.

### VD-RUNTIME-IDENTITY-001
- Aktiv PHP-runtime bruger namespace-roden `VisualDesignerManager\\...`; nye stacktraces må ikke vise `Hangar18\\Clean\\...`.
- WordPress Text Domain er `visual-designer-manager`.
- Persistente kompatibilitets-ID'er som eksisterende option/meta/action/page-slugs med `h18_clean` / `h18-clean` ændres ikke i denne migration. De er data-/URL-kompatibilitet og må ikke masseomdøbes uden en særskilt migrationskontrakt.
- Den historiske `Hangar18_Manager` compatibility marker bevares, så eksisterende theme-integration ikke brydes.


## 0.1.58 – Side Designer Gem → frontend synkronisering

### VD-PAGE-SAVE-CACHE-001
- Side Designerens canonical model gemmes fortsat i `_h18_clean_layout_v1`/versionshistorikken; WordPress `post_content` bliver ikke Designer-datakilde.
- Efter en verificerbar Designer-gemning skal den tilhørende WordPress-side touches med `wp_update_post()` og derefter `clean_post_cache()`.
- Touch udføres **efter** Designer-meta og Header/Footer-valg er skrevet, så `post_updated`/`save_post`-baserede host-, plugin- og full-page caches invaliderer den gamle offentlige render og efterfølgende læser den nye canonical model.
- En canonical no-op Gem må også invaliderer frontend-cache. Det gør det muligt at reparere en allerede stale offentlig side uden at oprette en kunstig Designer-version.
- `Gem & vis` skal åbne permalinket med `h18_vd_saved=<version>` som cache-buster for den umiddelbare efterkontrol.
- Restore af en Designer-version skal bruge samme frontend-invalideringsvej.
- Menu-save og navigationens datamodel er uden for denne kontrakt og må ikke ændres af 0.1.58.


## 0.1.59 – Tekstbaggrund arver Kasse/Sektion

### VD-TEXT-BG-INHERIT-001
- Tekst-elementer har ikke en selvstændig synlig baggrundskontrakt i den aktuelle Inspector og normaliseres derfor canonical med `backgroundTransparent=true`.
- Paint-kæden er **Tekst → nærmeste Kasse → Sektion**.
- Ligger Tekst direkte under en Sektion, er Sektionens baggrund den synlige baggrund bag teksten.
- Ligger Tekst under en Kasse, er Kassens baggrund den synlige baggrund; er Kassen transparent, fortsætter paint-kæden til Sektionen.
- Ældre persisted Text-state med `backgroundTransparent=false` må ikke genindføre en hvid leaf-baggrund.
- Menu, Billede og Knap beholder deres egne eksisterende background-kontrakter.


## 0.1.60 – Button Designer/frontend parity

### VD-BUTTON-PARITY-001
- Knap-elementets typografi er canonical data: skrifttype, størrelse, tykkelse, linjeafstand og bogstavafstand.
- Designer-preview og PHP Renderer bruger de samme Button-properties og samme system-font fallback.
- `autoSize=true` betyder, at knapteksten holdes på én linje (`nowrap`) og Designerens målte tekst/padding materialiserer elementets grid-geometri.
- `autoSize=false` bevarer manuel bredde/højde og tillader normal tekstombrydning.
- Temaets link-/button-typografi må ikke ændre den synlige størrelse på et Visual Designer Button-element.
- Sektion/Kasse-geometri, Menu, Billede og Tekst ændres ikke af denne kontrakt.

## 0.1.61 – Keyboard, Clipboard og Header/Footer baseline

### VD-KEYBOARD-001
- Et markeret Designer-element kan finjusteres visuelt uden at ændre 120-unit-gridpositionen.
- `Pil` ændrer canonical `offsetX`/`offsetY` med 1 px; `Shift + pil` ændrer med 10 px.
- Offset er begrænset til ±2000 px og renderes identisk i Designer og frontend via `transform: translate(...)`.
- Gentagne piletastetryk indtil keyup grupperes som én Undo/Redo-transaktion.
- Tastaturgenveje må ikke overtage piletaster/Ctrl-genveje når fokus står i input, textarea, select eller contenteditable.

### VD-CLIPBOARD-001
- `Ctrl/Cmd+C` kopierer valgt element; `Ctrl/Cmd+V` indsætter; `Ctrl/Cmd+D` duplikerer uden at overskrive clipboard.
- Kasse/Sektion kopieres som komplet subtree med alle descendants.
- Ved indsættelse oprettes nye unikke element-ID'er, og interne `parentId`-referencer remappes til de nye IDs.
- Clipboard lagres bruger-specifikt i browserens localStorage og overlever navigation mellem Visual Designer-sider på samme website; der findes in-memory fallback.
- Root for en indsættelse placeres på næste frie Y-position i mål-parenten, mens subtree-intern geometri, props, billeder, links og styling bevares.
- Indsæt/Duplikér er én Undo/Redo-transaktion.

### VD-HEADER-FOOTER-COMPLETE-001
- Multi-template Header/Footer baseline er FÆRDIG fra v0.1.61.
- `TemplateLayoutModel::resolveChoiceId()` er fælles resolverkontrakt for frontend og composite Preview.
- Inaktiv stored default ignoreres; resolveren falder deterministisk tilbage til første aktive template eller tom fallback.
- `Ingen Header/Footer` stopper resolveren eksplicit.
- `.github/scripts/v0161_header_footer_qa.php` er permanent Definition-of-Done regression gate.

## 0.1.62 – Kopiér side

### VD-PAGE-DUPLICATE-001
- Funktionen ligger under `Visual Designer Manager → Sider` og ikke i den generelle Designer-toolbar.
- Brugeren vælger `Kopiér`, angiver et nyt sidenavn og får en ny WordPress-side med nyt side-ID og unik slug.
- Kopien oprettes altid som `draft`; hjemmeside-status kopieres aldrig.
- WordPress-indhold, parent, menu-order, side-template og featured image kopieres som sikre sideattributter.
- Hvis kildesiden er en Visual Designer-side, kopieres den aktuelle canonical model til kopien og gemmes som kopiens egen version 1. Kildens versionshistorik kopieres ikke.
- Header- og Footer-sidevalg kopieres eksplicit med `TemplateLayoutModel::pageChoice()` / `setPageChoice()`.
- Den nye Designer-model SHA/digest verificeres mod kilden. Hvis kopieringen fejler efter oprettelsen, rulles den nye side tilbage til papirkurven.
- Original side og original versionshistorik ændres ikke.

## 0.1.64 – Designer clipboard reliability

### BUG-23 / VD-CLIPBOARD-002
- Kopiér/Duplikér må ikke afhænge af kun én intern selection-variabel. Hvis core-selection mangler, må den synligt markerede `.is-selected` node bruges som sikker fallback.
- `Ctrl/Cmd+C`, `Ctrl/Cmd+V`, `Ctrl/Cmd+D` og toolbar-knapperne skal kalde samme produktionsfunktioner.
- Efter Indsæt/Duplikér skal den nye root-node være markeret og automatisk scrolles ind i canvas-view, så en korrekt indsættelse ikke kan ligne en no-op.
- Clipboard-status skal give synlig feedback ved Kopiér, Indsæt, Duplikér og tomt clipboard.
- Clientens canonical model skal bevare `desktop`, `laptop`, `tablet` og `mobile` geometry ved normalisering og clipboard roundtrip.
- `window.H18VDProductivity` eksponerer de samme produktionsfunktioner til live QA/diagnostik; den er ikke en separat implementering.
- Side Designer og Header/Footer skal fortsat bruge den samme `editor-v018-core.js`, så Designer-rettelser gælder begge steder.



## VD-ELEMENTS-001 · General Designer Elements v0.1.65

Visual Designer har canonical leaf-typerne `spacer`, `divider`, `icon`, `badge`, `link`, `datalist` og `table`. De skal fungere i samme layout-/clipboard-/historikmotor som eksisterende elementer og i både Side Designer og Header/Footer Designer. `datalist` og `table` er i v0.1.65 statiske; dynamisk datasource/binding er et separat efterfølgende kontraktlag.

## 27. v0.1.66 – ikonregister, tabelkanter og Menu-preview

### VD-ICON-LIBRARY-001

- Core icons er lokal SVG og kategoriseret i det centrale `IconRegistry`.
- Module icons registreres via den dokumenterede module-filterkontrakt.
- Custom icons er reserveret som tredje niveau; upload/indsæt-UI kommer senere.
- Side Designer og Header/Footer bruger samme ikonregister og samme SVG-rendering som frontend.

### VD-TABLE-BORDERS-001

- Klik markerer én tabelcelle. Ctrl/Cmd+klik tilføjer/fjerner celler. Shift+klik markerer et rektangulært område.
- Markeret område understøtter Yderramme, Indvendige, Alle, Vandret, Lodret, Top, Højre, Bund, Venstre og Ingen.
- Border-pen styrer tykkelse, farve og `solid/dashed/dotted`.
- Cellekanter er canonical `cellBorders`; tabelstandard er `borderMode`, `cellBorderWidth`, `cellBorderColor`, `cellBorderStyle`.
- Samme data bruges i Designer-preview og frontend.

### VD-MENU-PREVIEW-001

- Struktur-preview er bredere på store skærme og holder Desktop-menuens root-punkter på én vandret række.
- Hvis strukturen stadig er bredere end previewet, bruges vandret scroll i previewet i stedet for kunstig line-wrap.
- På smallere adminskærme flyttes previewet fortsat under menu-editoren.

### VD-ADMIN-STATUS-002

- `Log` og `Konvertering` vises som `Klar` i Visual Designer Manager-menuen.

## VD-MODULE-DATA-001 – Fælles modul- og dataarkitektur (v0.1.67)

- `ModuleRegistry` er den eneste registry for modulnøglerne `vehicles`, `events` og `galleries`.
- `ModuleRecord` schema 1 normaliserer den fælles record-envelope: stabilt ID, titel, slug, status, sortering, featured media, summary, module-specifikke standardfelter, dynamiske attributter samt created/updated timestamps.
- Dynamiske attributter er ordnede key/label/type/value-records. De er bevidst generiske, så Køretøjer kan få brugerdefinerede tekniske felter uden et nyt databaseformat.
- `ModuleStore` bruger det private WordPress post type `h18_module_item`. Canonical record gemmes som JSON i `_h18_module_record_v1`; modul, status og sortering har egne meta-indekser.
- Storage er `public=false`, `show_ui=false` og `show_in_rest=false`. Manager-UI skal altid gå gennem modulets egne kontrollerede actions/services.
- `ModuleBinding` schema 1 beskriver `static|module`, `list|detail`, record-ID, query og field-map. Kontrakten er foundation i v0.1.67; eksisterende statiske Designer-elementer skifter ikke datasource automatisk.
- Records har canonical SHA-256 digest, så senere import/migration og QA kan verificere strukturel identitet.
- Modulrækkefølge: Køretøjer først, derefter Events og Billedgalleri.

## VD-CANVAS-SECTION-001 – Canonical Canvas/Section hierarchy

- Root på en almindelig Designer-side må kun indeholde `section`.
- `container` og alle leaf-typer skal have ancestry, der ender i en root-`section`.
- `HierarchyNormalizer::normalize()` wrapper legacy root-noder i en neutral Sektion og konverterer nested Sektion til Kasse.
- `HierarchyNormalizer::isCanonical()` er den fælles verifieringskontrakt for migration/QA.
- `CanvasSectionMigration` kører én gang i Admin for sider med `_h18_clean_layout_v1`, gemmer `_h18_clean_layout_pre_section_v0168`, bevarer alle oprindelige node-ID'er og gemmer migrationen som en ny Designer-version.
- Ved validerings- eller save-fejl gendannes current model, history og version-meta til før migreringen.
- Editorens JavaScript-normalizer håndhæver samme root-kontrakt ved runtime, så add/paste/re-parent ikke kan efterlade løse root-elementer.

## VD-SELECTION-LAYER-001 – Editor-only active layer

Markeret element og element under drag/resize skal ligge øverst i Designerens stacking context. Ancestor wrappers løftes samtidig, så et markeret child ikke kan skjules bag en sibling-Kasse/Sektion. Lagløftet implementeres kun i editor-CSS og må ikke persistére eller ændre frontendens canonical `zIndex`.
