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
- senere eventuelt solid/dashed/dotted.

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

## 21. Kontraktstatus for 0.1.36

### VD-FLOAT-001 – Flydende Knap

**IMPLEMENTERET / stacking rettet i 0.1.34.** Palette-Knap starter fortsat som Flydende før drop-zonen beregnes. 0.1.34 fjerner normal-elementers editor stacking-context og giver Flydende Knap et separat top-lag, så den ikke forsvinder, når et andet element markeres. Canonical `zIndex` bevares og bruges til rækkefølge mellem flere floating-elementer og på frontend.

### VD-TEXT-SEL-001 – Rich-text selection

**BUGFIX i 0.1.36 – afventer bruger-QA.** Bruger-QA af 0.1.35 viste fortsat, at Understregning bevarer selection, mens Fed/Kursiv kan miste den. 0.1.36 gør derfor selection uafhængig af Firefox' genopbygning af `STRONG`/`EM`: to vedvarende, tomme editor-boundary-markører placeres omkring den valgte tekst ved toolbar-pointerdown. Fed, Kursiv og Understregning formatterer mellem de samme markører, og Range rekonstrueres fra markørerne efter hver kommando. Logiske tekst-offsets er kun fallback.

Godkendelsestest: 20/20 gentagelser for Fed, Kursiv og Understregning samt kæderne Fed → Kursiv → Understregning og Kursiv → Fed → Understregning uden ny markering.

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
