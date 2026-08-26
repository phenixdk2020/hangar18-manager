# Visual Designer Manager – Brugermanual

Senest opdateret: 25. august 2026  
Gælder fra: Visual Designer Manager 0.1.18  
Målgruppe: Redaktører og administratorer, der bygger og vedligeholder sider i WordPress

> Denne manual beskriver **hvordan Visual Designer Manager bruges i praksis**. Den tekniske arkitektur er beskrevet separat i `CLEAN-DESIGN-MANUAL.md`.

---

## 1. Hvad er Visual Designer Manager?

Visual Designer Manager er en visuel sidebygger til WordPress. Ideen er, at en side bygges som LEGO-klodser:

- **Sektioner** opdeler siden i større områder.
- **Kasser** bruges til lokale grupper og kolonner.
- **Tekst** bruges til overskrift og brødtekst.
- **Billede** bruges til billeder med en selvstændig billedboks.

Elementer kan flyttes med drag-and-drop, placeres over/under/venstre/højre for hinanden og lægges ind i Kasser og Sektioner.

Visual Designer gemmer siden i sin egen model og ændrer først den offentlige Visual Designer-side, når du vælger **Gem som ny version**.

---

## 2. Hvor findes funktionerne?

Når pluginet **Visual Designer Manager** er aktivt, findes hovedmenuen:

**WordPress → Visual Designer Manager**

Her findes bl.a.:

| Menupunkt | Formål |
|---|---|
| Dashboard | Samlet status for Visual Designer-sider og Manager |
| Designer | Åbn den visuelle sidebygger |
| Køretøjer | Administration af køretøjsindhold |
| Køretøjsfelter | Feltopsætning for køretøjsdata |
| Events | Administration af events |
| Billedgalleri | Administration af galleri/album |
| Data | Datafunktioner og fremtidige datamoduler |
| Sider | Oversigt over WordPress-sider og Visual Designer-status |
| Menu | WordPress-menuer og menuplaceringer |
| Header / Footer | Global header/footer-administration |
| Backup | Backup af Visual Designer-layouts og versionshistorik |
| Opdateringer | Tjek og installer nye Manager-versioner |
| Log | Diagnose- og fejllog |

Nogle af de specialiserede adminområder udbygges fortsat i Visual Designer-serien.

---

## 3. Åbn en side i Designer

1. Gå til **Visual Designer Manager → Designer**.
2. Find den WordPress-side, du vil redigere.
3. Klik **Åbn designer**.

Designerens skærm består af tre hovedområder:

```text
┌──────────────┬─────────────────────────────┬──────────────────┐
│ ELEMENTER    │           CANVAS            │    INSPECTOR     │
│              │                             │                  │
│ Sektion      │   Den side du bygger        │ Indstillinger    │
│ Kasse        │                             │ for valgt        │
│ Tekst        │                             │ element          │
│ Billede      │                             │                  │
└──────────────┴─────────────────────────────┴──────────────────┘
```

### Venstre: Elementer

Herfra kan du tilføje nye elementer.

### Midten: Canvas

Her bygges siden visuelt.

### Højre: Inspector

Her ændres egenskaberne for det valgte element.

---

## 4. Forstå Sektion og Kasse

### Sektion

En **Sektion** er et stort hovedområde på siden.

Eksempel:

```text
SIDE
├── SEKTION: Om foreningen
├── SEKTION: Køretøjer
├── SEKTION: Events
└── SEKTION: Kontakt
```

En Sektion bruges normalt i fuld sidebredde og fungerer som den overordnede ramme for et område.

### Kasse

En **Kasse** er en mindre layoutcontainer inde i en Sektion eller en anden Kasse.

Eksempel:

```text
SEKTION
├── KASSE
│   ├── Billede
│   └── Tekst
└── KASSE
    └── Tekst
```

Kasser er især nyttige til:

- to eller tre kolonner;
- kort med billede og tekst;
- farvede felter;
- grupper af elementer;
- nested layout.

### Praktisk huskeregel

**Sektion = stort område på siden.**  
**Kasse = lokal LEGO-klods inde i området.**

---

## 5. Tilføj et element

Et element kan tilføjes på to måder.

### Klik

Klik på fx **+ Tekst**. Elementet lægges på root/canvas.

### Drag-and-drop

Træk elementet fra venstre palette til den ønskede position.

Det anbefales at bruge drag-and-drop, når du vil placere elementet direkte i en Kasse eller ved siden af et andet element.

---

## 6. Flyt elementer

Eksisterende elementer flyttes ved at trække i elementets **✥ flyttehåndtag**.

Når du trækker over et andet element, vises drop-zoner.

### Drop-zoner

- **↑ OVER** – del den valgte celle over elementet.
- **↓ UNDER** – del den valgte celle under elementet.
- **← VENSTRE** – del cellen og placer det nye element til venstre.
- **HØJRE →** – del cellen og placer det nye element til højre.
- **IND I** – vises på Kasse/Sektion og lægger elementet ind i containeren.

### Eksempel: to elementer side om side

```text
┌───────────────┬───────────────┐
│    Billede    │     Tekst     │
└───────────────┴───────────────┘
```

### Eksempel: del kun venstre celle lodret

```text
┌───────────────┬───────────────┐
│    Billede    │               │
├───────────────┤     Tekst     │
│     Tekst     │               │
└───────────────┴───────────────┘
```

Elementet til højre kan altså spænde over begge rækker.

---

## 7. Farverne i Designer

Designer bruger farver til at vise status.

| Farve | Betydning |
|---|---|
| **Grøn** | Elementet er valgt/aktivt |
| **Blå** | Hover, drop-zone eller element under markøren |
| **Rød** | Reel overlap-advarsel |

En Kasse eller Sektion tæller ikke som overlap blot fordi dens egne børn ligger inde i den.

---

## 8. Labels over elementerne

Elementer kan have labels som:

- `SEKTION · id`
- `KASSE · id`
- `TEKST · id`
- `BILLEDE · id`

Labelen er kun en del af editoren.

Den tæller **ikke** med i:

- elementets fysiske højde;
- elementets bredde;
- frontend-layoutet;
- Kasse/Sektions auto-grow.

Det betyder, at den offentlige side ikke får ekstra højde på grund af editor-labels.

---

## 9. Ændr størrelse på et element

Når et element er valgt, vises grønne resize-punkter.

Du kan trække i sider eller hjørner for at ændre:

- bredde;
- højde;
- placering i forhold til gridet.

Visual Designer bruger:

- **120 vandrette units**;
- **8 px lodret snap/grid**.

Inspector viser de tilsvarende værdier for X, Y, bredde og højde.

---

## 10. Kasse og Sektion vokser med indholdet

Kasse og Sektion har **auto-grow**.

Hvis du lægger elementer under hinanden inde i en Kasse, skal Kassen vokse, så alt indhold kan være inde i den.

Hvis du selv gør Kassen højere end nødvendigt, behandles den valgte højde som en **minimumshøjde**.

Eksempel:

```text
KASSE
├── Tekst
├── Billede
└── Tekst
```

Kassen skal automatisk være høj nok til alle tre elementer.

---

## 11. Tekst-element

Et Tekst-element kan indeholde både overskrift og brødtekst.

### Inspector

For Tekst kan du bl.a. vælge:

- **Overskrift** – valgfri;
- **Overskrifttype** – H2, H3, H4, H5 eller H6;
- **Tekst** – brødtekst;
- **Justering** – venstre, center eller højre;
- ramme/border;
- afstand X/Y.

Hvis Overskrift er tom, vises kun brødteksten.

### På vej i næste stylingtrin

Tekst-elementet skal desuden kunne styre:

- baggrundsfarve eller gennemsigtig;
- brødtekstfarve;
- separat overskriftsfarve.

Disse stylingfelter er godkendt som næste Visual Designer-udvidelse.

---

## 12. Billede-element

I Visual Designer 0.1.18 er **billedboksen** og **selve billedet** adskilt.

Det betyder, at boksen godt kan være større end selve billedet.

### Billedboksen

Boksen styrer:

- X/Y;
- bredde/højde;
- border;
- afstand X/Y;
- baggrundsfarve.

### Billedet inde i boksen

I Inspector kan du vælge, hvordan billedet skal opføre sig.

#### Vis hele billedet

Hele billedet vises med bevarede proportioner. Der kan være tom plads rundt om billedet.

Dette er standard for nye billeder.

#### Fyld boksen / beskær

Billedet fylder hele boksen. Noget af billedet kan blive beskåret.

#### Original størrelse

Billedet beholder sin naturlige størrelse inde i boksen.

#### Stræk

Billedet fylder boksens bredde og højde, også hvis proportionerne ændres.

### Placering

Billedet kan placeres:

- vandret: venstre / center / højre;
- lodret: top / center / bund.

Ved beskæring kan fokus desuden styres med Fokus X/Y.

---

## 13. Border / ramme

Alle relevante elementer kan have en ramme.

### Indstillinger

- **Ramme px** – standard `0`;
- **Rammefarve**.

`0 px` betyder ingen synlig ramme.

Rammen følger selve elementets fysiske boks og vises også på frontend.

---

## 14. Afstand X og Afstand Y

Elementer kan have individuel afstand til næste element.

### Afstand X

Vandret luft mod næste element til højre.

### Afstand Y

Lodret luft mod næste element nedenunder.

Standard er `0`.

Afstanden er en del af Visual Designer-layoutet og indgår derfor også i auto-grow og Save/Reload.

---

## 15. Overlap

Hvis to indholdselementer fysisk ligger oven i hinanden, viser Designer en rød **OVERLAP**-advarsel.

Overlap bruges foreløbig som en advarsel og er ikke en normal layoutmetode.

Hvis overlap senere skal bruges bevidst til fx lag, badges eller grafiske overlays, bør det ske gennem en særskilt fri/layer-funktion i stedet for almindeligt grid-layout.

---

## 16. Fortryd og Gentag

Designer har:

- **↶ Fortryd**
- **↷ Gentag**

De arbejder på den aktuelle usavede Designer-session.

Fortryd/Gentag erstatter ikke de gemte versionshistorikker. Når siden gemmes, bruges versionsstyringen beskrevet senere i manualen.

---

## 17. Forhåndsvis uden at gemme

Klik **Forhåndsvis** for at se den aktuelle usavede Designer-model i den rigtige frontend med tema/header/footer.

Denne forhåndsvisning:

- gemmer ikke siden;
- er midlertidig;
- er knyttet til den aktuelle bruger;
- viser en markering om, at det er en ikke-gemt forhåndsvisning.

Brug den, før du gemmer større ændringer.

---

## 18. Gem som ny version

Når du er tilfreds med layoutet, klik:

**Gem som ny version**

Visual Designer:

1. normaliserer layoutmodellen;
2. gemmer en ny versionspost;
3. læser modellen tilbage;
4. verificerer at den gemte model matcher det indsendte layout;
5. beholder tidligere versioner i historikken.

Den offentlige Visual Designer-side bruger den senest gemte version.

---

## 19. Gem & vis

**Gem & vis** gør to ting:

1. gemmer siden som ny Visual Designer-version;
2. åbner den rigtige offentlige side.

Brug denne funktion, når du både vil gemme og straks kontrollere frontend-resultatet.

---

## 20. Gemte versioner

Nederst i Designer findes området **Gemte versioner**.

Fra Visual Designer 0.1.18 kan en tidligere version bruges på tre måder.

### Forhåndsvis version

Åbner den valgte historiske version uden at ændre den aktuelle side.

### Gendan original

Gør den valgte gamle version til den aktive model på originalsiden.

Det er **ikke destruktivt**:

- den gamle historik slettes ikke;
- restore oprettes som en ny version;
- du kan derfor altid gå tilbage igen.

### Opret kopi

Opretter en ny WordPress-side som kladde ud fra den valgte version.

Kopien:

- ændrer ikke originalsiden;
- får sin egen Visual Designer-model;
- starter sin egen Visual Designer-historik ved v1;
- kan åbnes separat i Designer.

Dette er nyttigt, hvis du vil eksperimentere med et gammelt layout uden risiko for den aktive side.

---

## 21. Opdater Visual Designer Manager

Gå til:

**Visual Designer Manager → Opdateringer**

Her kan du:

1. klikke **Tjek for opdatering**;
2. se om en nyere Visual Designer-version findes;
3. vælge **Opdater nu**.

Updateren verificerer den versionerede pakke og SHA-256-kontrolsummen.

Fra 0.1.16 er updateren desuden ændret, så pluginets aktive WordPress-status skal bevares under self-update.

---

## 22. Backup

Under:

**Visual Designer Manager → Backup**

kan Visual Designer-layouts og versionshistorik eksporteres som backup.

Backup bør bruges før større ændringer af:

- tema;
- globale designindstillinger;
- Header/Footer;
- større konverteringer af eksisterende sider.

---

## 23. Diagnose og Log

Hvis noget opfører sig forkert, kan Designerens diagnosefunktion bruges.

### Kopiér diagnose-link

I Designer findes knappen:

**Kopiér diagnose-link**

Loggen kan bl.a. indeholde hændelser som:

- palette drag/drop;
- reparent/flytning;
- resize;
- Undo/Redo;
- Save;
- Preview;
- restore;
- billedevalg.

Under **Visual Designer Manager → Log** kan diagnoseoplysninger ses og ryddes.

Ved fejl er det nyttigt at notere:

1. hvad du gjorde;
2. hvad du forventede;
3. hvad der skete;
4. screenshot;
5. diagnose-link.

---

## 24. Globalt design – planlagt næste lag

Visual Designer skal have et globalt designområde, så de samme grundværdier ikke skal sættes manuelt på hver side.

Planlagte globale indstillinger omfatter:

- farvepalette;
- skrifttype;
- standard tekstfarve;
- standard overskriftsfarve;
- sidebaggrund;
- desktopbredde;
- mobilbredde;
- standardafstande.

Et element kan senere enten **arve global stil** eller **overskrive den lokalt**.

---

## 25. Header og Footer – planlagt Designer

Header og Footer skal ikke være almindelige elementer på hver side.

De skal have egne globale Designer-modeller.

### Header Designer

Skal kunne arbejde med fx:

- Logo;
- Menu;
- Tekst;
- Knap;
- Kasser/layout.

### Footer Designer

Skal kunne arbejde med fx:

- Tekst;
- Menu;
- Logo;
- Links;
- Kasser/layout.

Header/Footer får deres egen versionshistorik og skal bruge samme grundlæggende drag-and-drop-motor som Side Designer.

---

## 26. Temaets rolle

På sigt skal **Hangar18 Base Theme** primært fungere som WordPress-shell/runtime.

Det betyder:

- WordPress står fortsat for sider, URL'er, templates og frontend-hook;
- Manageren står for det visuelle design;
- Header/Footer og globale designvalg styres fra Manager;
- almindelige sider bygges i Visual Designer.

Header og Footer ligger uden for en almindelig sides model og kan derfor ikke slettes ved at redigere en side.

---

## 27. Kommende elementtyper

Når det nuværende layout-, styling- og tema-fundament er låst, kan Designer udvides med flere LEGO-klodser.

Mulige næste elementer:

- Knap;
- Divider/skillelinje;
- Spacer/afstand;
- Ikon;
- Logo;
- Menu;
- Galleri;
- video;
- kort/map;
- formular;
- dynamiske Køretøj-, Event- og Galleri-elementer.

Målet er, at alle nye elementer bruger de samme grundprincipper for:

- placering;
- resize;
- border;
- afstand;
- baggrund;
- responsive regler;
- Save/Preview/versionering.

---

## 28. Anbefalet arbejdsgang

Ved almindelig sideredigering anbefales:

1. Åbn siden i Designer.
2. Brug **Forhåndsvis** hvis du vil se den aktuelle gemte eller usavede retning.
3. Tilføj eller flyt Sektion/Kasse/elementer.
4. Rediger indhold og styling i Inspector.
5. Kontrollér for røde overlap-advarsler.
6. Brug **Forhåndsvis** uden at gemme.
7. Ret eventuelle fejl.
8. Klik **Gem som ny version**.
9. Brug **Gem & vis** eller åbn den offentlige side.
10. Kontrollér desktop og mobil.

Ved større ændringer anbefales desuden at tage en Backup først.

---

## 29. Hurtigt eksempel – byg en sektion med billede og tekst

### Målet

```text
SEKTION
└── KASSE
    ┌───────────────┬───────────────┐
    │    Billede    │     Tekst     │
    └───────────────┴───────────────┘
```

### Fremgangsmåde

1. Træk **Sektion** ind på siden.
2. Træk **Kasse** ind i Sektionen.
3. Træk **Billede** ind i Kassen.
4. Vælg billedet i Inspector.
5. Træk **Tekst** over Billede-elementet og slip i **HØJRE**-zonen.
6. Vælg Tekst-elementet.
7. Indtast valgfri overskrift og brødtekst.
8. Tilpas bredde, border og afstand.
9. Klik **Forhåndsvis**.
10. Klik **Gem som ny version**, når resultatet er korrekt.

---

## 30. Hurtigt eksempel – to rækker til venstre og ét højt element til højre

Start med:

```text
┌───────────────┬───────────────┐
│    Billede    │     Tekst     │
└───────────────┴───────────────┘
```

Træk et nyt Tekst-element ind og slip det **UNDER Billede**.

Resultatet kan blive:

```text
┌───────────────┬───────────────┐
│    Billede    │               │
├───────────────┤     Tekst     │
│     Tekst     │               │
└───────────────┴───────────────┘
```

Her deles kun venstre celle. Højre Tekst-element fortsætter over begge rækker.

---

## 31. Hvis noget ser forkert ud

Kontrollér først:

- Er det rigtige element valgt? Grøn markering betyder valgt.
- Er der en rød **OVERLAP**-advarsel?
- Ligger elementet inde i den rigtige Kasse/Sektion?
- Har elementet stor Afstand X/Y?
- Har Kassen en manuelt valgt minimumshøjde?
- Er billedets visning sat til `Vis hele`, `Fyld`, `Original` eller `Stræk` som ønsket?
- Er du i en usavet Preview eller på den rigtige gemte frontend?

Hvis problemet fortsætter, brug **Kopiér diagnose-link** og tag et screenshot af Designer.

---

## 32. Versionshistorik for denne manual

| Manualversion | Ændring |
|---|---|
| 1.0 | Første Visual Designer-brugermanual baseret på funktionerne gennem 0.1.18 og den godkendte målarkitektur. |

---

## 33. Relaterede dokumenter

- `CLEAN-DESIGN-MANUAL.md` – teknisk design- og arkitekturmanual for Clean.
- `DESIGN-MANUAL.md` – historisk/visuel manual fra den tidligere 0.4.x Manager-serie.
- `README.md` – overordnet repository-/projektinformation.

Når nye brugerfunktioner bliver frigivet, skal denne brugermanual opdateres sammen med den relevante Visual Designer-version.
