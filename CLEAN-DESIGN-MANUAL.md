# Hangar18 Manager Clean – Design- og arkitekturmanual

Senest opdateret: 25. august 2026  
Gælder for: Hangar18 Manager Clean 0.1.x og nyere  
Status: Autoritativ målarkitektur for Clean Designer

## 1. Formål

Denne manual beskriver den godkendte arkitektur og de visuelle regler for **Hangar18 Manager Clean**. Den supplerer den eksisterende `DESIGN-MANUAL.md`, som fortsat dokumenterer den tidligere 0.4.x-løsning og de historiske designvalg for hjemmesiden.

Clean-manualen skal bruges som teknisk og funktionel reference, når den nye Designer videreudvikles. Nye funktioner må ikke indføres på en måde, der bryder hierarkiet, versionsmodellen, frontend-renderingen eller adskillelsen mellem globalt design og sideindhold.

Hovedprincippet er, at Clean Designer skal fungere som en **LEGO-lignende, modeldrevet sidebygger**, hvor brugeren kan kombinere Sektioner, Kasser og indholdselementer visuelt uden at miste en entydig canonical model.

---

## 2. Overordnet arkitektur

Den godkendte struktur er:

```text
HANGAR18 DESIGN
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

Temaet skal på sigt fungere som **WordPress-shell/runtime**, mens Hangar18 Manager styrer det faktiske visuelle design.

Header og Footer er globale designs og skal **ikke** være almindelige elementer, der kopieres ind på hver side.

---

## 3. Sidehierarki

En almindelig Clean-side skal følge dette hierarki:

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

Den nuværende 0.1.x-model kan teknisk tillade flere kombinationer under udvikling. Når hierarkireglen låses i Clean, skal ovenstående være den autoritative struktur.

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
| Hjørneradius | Muligt | Ja |
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

Clean Designer bruger en modeldrevet geometri med:

- 120 vandrette units;
- 8 px lodret grid/snap;
- `x`, `y`, `w`, `h` pr. element;
- `parentId` til hierarki;
- `order` til stabil rækkefølge;
- type-specifikke properties.

Save, Undo, Redo, Preview og frontend skal alle arbejde ud fra samme canonical model.

Visuelle CSS-tricks må ikke være eneste kilde til en layoutændring. Hvis en egenskab påvirker layout, skal den kunne rekonstrueres efter Save/Reload.

---

## 6. Drag-and-drop og celle-split

Clean Designer skal understøtte fysisk drag-and-drop med tydelige drop-zoner.

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

Kasse/Sektion er layout-wrappers og må ikke få overlap-advarsel blot fordi deres børn ligger inde i dem.

---

## 8. Fælles styling-egenskaber

Alle relevante elementer skal kunne have grundlæggende styling uden specialkode pr. side.

### Fælles egenskaber

- Border thickness, standard `0 px`
- Border color
- Afstand X til næste element
- Afstand Y til næste element
- Baggrundsfarve, hvor det giver mening
- Størrelse og placering

Afstand X/Y skal indgå i layoutberegningen og ikke kun være kosmetisk CSS.

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
- Border
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
- Border
- Borderfarve
- Baggrundsfarve
- Afstand X/Y
- Resize

De grønne resize-håndtag ændrer boksen, ikke billedfilens naturlige proportioner.

### Billedet inde i boksen

Billedet skal kunne vises som:

| Tilstand | Funktion |
|---|---|
| Vis hele billedet | Hele billedet vises uden beskæring; tom plads kan forekomme |
| Fyld boksen | Billedet fylder boksen og beskæres efter behov |
| Original størrelse | Billedet beholder sin naturlige størrelse inde i boksen |
| Stræk | Billedet følger boksens bredde/højde og kan deformeres |

Standard for nye billeder er:

- **Vis hele billedet**
- vandret center
- lodret center

### Placering i boksen

- Vandret: venstre / center / højre
- Lodret: top / center / bund
- Fokus X/Y bruges især ved beskæring i **Fyld boksen**.

Eksempel:

```text
┌──────────────────────────────┐
│                              │
│       ┌──────────────┐       │
│       │    BILLEDE   │       │
│       └──────────────┘       │
│                              │
└──────────────────────────────┘
         BILLEDBOKS
```

---

## 11. Auto-grow for Sektion og Kasse

Sektion og Kasse skal efter drop, reparent og resize genberegne nødvendig højde ud fra alle børn.

Reglen er:

```text
faktisk højde = max(valgt minimumshøjde, nødvendig indholdshøjde)
```

Når et barn flyttes eller slettes, må containeren krympe igen, men aldrig under den manuelt valgte minimumshøjde.

Border, padding og lodret afstand skal indgå i beregningen.

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

Clean Designer skal være ikke-destruktiv.

Hver rigtig **Gem** opretter en ny Clean-version.

### Gemte versioner skal tilbyde

- **Forhåndsvis version**
- **Gendan original**
- **Opret kopi**

### Gendan original

Gendannelse til original-siden må ikke overskrive historikken destruktivt.

En valgt gammel version gemmes som en **ny version** på den originale side.

Eksempel:

```text
v1 → v2 → v3 → Gendan v1 → v4
```

v2 og v3 findes stadig i historikken.

### Opret kopi

En historisk version kan oprettes som en ny WordPress-side:

- status: kladde;
- original side ændres ikke;
- kopien får sin egen Clean-historik;
- den valgte model bliver kopiens `v1`.

---

## 14. Forhåndsvisning og Save

Der findes to forskellige preview-behov:

### Usavet forhåndsvisning

Den aktuelle Designer-model kan vises i den rigtige frontend/theme uden at gemme.

Dette skal bruge en kortlivet, brugerspecifik preview-model og må ikke ændre den offentlige side.

### Gem & vis

- gemmer canonical model som ny version;
- verificerer at den gemte model matcher input;
- åbner den rigtige offentlige side efter gemning.

---

## 15. Globalt design

Globalt design skal samle værdier, der ikke bør sættes individuelt på hvert element.

Planlagte globale indstillinger:

- Primær skrifttype
- Standard brødtekstfarve
- Standard overskriftsfarve
- Standard sidebaggrund
- Godkendt Hangar18-farvepalette
- Desktop-sidebredde, aktuelt designprincip 90 %
- Mobil-sidebredde, aktuelt designprincip 100 %
- Standardafstande
- Standard border/radius-regler

Lokale elementindstillinger må kunne overskrive globale defaults.

---

## 16. Temaets rolle

Hangar18 Base Theme skal på sigt være et tyndt **runtime/shell-tema**.

Temaets opgaver:

- WordPress template lifecycle
- hooks
- nødvendige wrappers
- menu- og WordPress-integration
- indlæsning af Manager-renderet Header, Side og Footer
- fallback hvis Manager ikke er tilgængelig

Temaet bør ikke indeholde parallelle designregler, som konkurrerer med Clean Designer.

Den tekniske sandhed for visuelt design skal gradvist flyttes til Managerens globale designmodel og de gemte Designer-modeller.

---

## 17. Header Designer

Header skal være et globalt design med sin egen model og versionshistorik.

Den skal kunne bruge samme LEGO-/grid-motor som Side Designer, men med header-specifikke elementer.

Planlagte elementer:

- Logo
- Navigation/Menu
- Tekst
- Knap
- Kasse
- eventuelt ikon

Header-indstillinger kan eksempelvis omfatte:

- sticky / ikke sticky
- højde
- baggrund
- tekst/menu-farve
- mobilmenu
- logo-størrelse
- alignment

Headeren ligger uden for almindelige sider og kan ikke slettes fra en side.

---

## 18. Footer Designer

Footer skal ligeledes være et globalt design med egen model og versionshistorik.

Planlagte elementer:

- Tekst
- Logo
- Menu
- Links
- Kasser/kolonner
- eventuelt kontaktoplysninger/sociale links

Footer følger global farvepalette, typografi og breddeprincip, men kan have egne lokale overrides.

Footer kan ikke slettes fra en almindelig side.

---

## 19. Flere elementtyper

Flere elementtyper skal først bygges, når hierarki, styling, globalt design og Header/Footer-arkitektur er stabile.

Planlagte elementer efter fundamentet:

- Knap
- Skillelinje
- Spacer/Afstand
- Ikon
- Galleri
- Menu
- Hero/Topbanner
- Kort-række
- Fremhævet tekst
- Dynamisk Køretøj-element
- Dynamisk Event-element
- Dynamisk Billedgalleri-element
- Formular
- øvrige funktionsmoduler

Nye elementer skal bruge samme canonical model, versionering og frontend-renderingsprincipper.

---

## 20. Responsivt design

Desktop og mobil skal ses som to visninger af samme model, ikke som to uafhængige sider.

Målarkitekturen skal understøtte:

- Desktop-layout
- Tablet-layout
- Mobil-layout
- arv fra desktop som standard
- lokale overrides hvor nødvendigt

Mobilbreakpoint fra den eksisterende designmanual er 782 px.

Der må ikke opstå vandret rulning på hele siden som følge af elementgeometri.

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

## 22. Godkendt udviklingsrækkefølge

Følgende rækkefølge er godkendt som den anbefalede fortsættelse efter Clean 0.1.18:

### Clean 0.1.19

- lås forskellen mellem Sektion og Kasse;
- Sektion kun på root i målarkitekturen;
- baggrundsfarve/gennemsigtig baggrund på relevante elementer;
- brødtekstfarve;
- separat overskriftsfarve;
- færdiggør grundlæggende element-styling.

### Clean 0.1.20

- Globalt design;
- forbindelse mellem Clean Manager og Hangar18 Base Theme;
- globale defaults for farver, typografi, sidebaggrund og bredde.

### Clean 0.1.21

- Header Designer;
- Footer Designer;
- samme grid-/LEGO-motor;
- separat global versionering.

### Derefter

- flere indholdselementer;
- specialelementer;
- dynamiske moduler;
- avanceret responsive controls;
- eventuel fri overlap/layer-mode.

Versionsnumrene er planlægningsmål og kan ændres, hvis en nødvendig fejlrettelse eller QA-version indsættes.

---

## 23. QA-regler for Clean Designer

Før en ny Clean-version godkendes, skal følgende kontrolleres:

1. Save/Reload giver samme canonical layout.
2. Undo/Redo ændrer samme model, som bliver gemt.
3. Preview matcher frontend-renderingen.
4. Labels påvirker ikke fysisk elementgeometri.
5. Kasse/Sektion auto-grow følger børn korrekt.
6. Border og Afstand X/Y er konsistente i editor og frontend.
7. Tekstoverskrift og brødtekst vises korrekt.
8. Billedboksen kan være større end selve billedet.
9. Billedets fit/placering matcher Inspector-valget.
10. Restore original bevarer historikken.
11. Restore som kopi ændrer ikke original-siden.
12. Plugin self-update efterlader Manager aktivt.
13. Desktop og mobil får ikke utilsigtet vandret overflow.
14. Header, side og footer må ikke overlappe hinanden.

---

## 24. Dokumentationsregel

Når et nyt Clean-designvalg godkendes:

1. Opdatér den canonical Clean-model eller relevante globale indstilling.
2. Opdatér denne manual.
3. Tilføj ændringen til release-notes/changelog.
4. Kør QA på editor, Save/Reload, Preview og frontend.
5. Byg en verificeret GitHub-releasepakke.

`CLEAN-DESIGN-MANUAL.md` er fremover den autoritative arkitekturbeskrivelse for den nye Clean Designer. Den ældre `DESIGN-MANUAL.md` bevares som reference for eksisterende designstandarder og legacy 0.4.x-adfærd, indtil de relevante regler er migreret til Clean.
