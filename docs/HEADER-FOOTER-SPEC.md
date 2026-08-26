# Visual Designer – Header, Footer, Menu og Theme

**Statusdato:** 26. august 2026  
**Status:** Godkendt målarkitektur under implementation  
**Produkt:** Visual Designer / Visual Designer Manager

## 1. Grundprincip

Header, Footer, Menu og Theme hænger sammen, men deres ansvar skal være klart adskilt.

Den ønskede arkitektur er:

```text
WORDPRESS / THEME SHELL
│
├── Valgt Header-template fra Visual Designer
│   ├── Logo
│   ├── Menu-element → Navigation-data
│   ├── Tekst / Knap / Ikon / Kasser
│   └── Responsive Desktop / Laptop / Mobil
│
├── Side-model fra Visual Designer
│
└── Valgt Footer-template fra Visual Designer
    ├── Menu-element → Navigation-data
    ├── Logo / Tekst / Links / Kasser
    └── Responsive Desktop / Laptop / Mobil
```

Temaet må ikke være den primære kilde til menuens visuelle design, når Visual Designer er aktiv.

---

## 2. Ansvarsfordeling

### Theme / WordPress shell

Temaet skal på sigt være en tynd runtime-shell og skal primært håndtere:

- WordPress template lifecycle;
- `wp_head()`, `wp_body_open()`, `wp_footer()`;
- hooks og nødvendige wrappers;
- side-/post-template routing;
- integration til WordPress' menu/navigation-system;
- fallback Header/Menu/Footer hvis Visual Designer Manager ikke er aktiv eller ingen gyldig template kan vælges;
- nødvendige accessibility/runtime-funktioner;
- indlæsning af Visual Designer Manager-renderet Header, Side og Footer.

Temaet må ikke have et parallelt sæt CSS-regler, der konkurrerer med Visual Designerens Header/Menu/Footer-design.

### Navigation / Menu-data

Menu-data beskriver **hvad navigationen indeholder**:

- menupunkter;
- hierarchy / parent-child;
- rækkefølge;
- URL eller WordPress-object reference;
- label;
- target;
- evt. relation til side/post/custom object.

Menu-data må ikke være bundet til et bestemt Header-layout.

Den samme menu kan derfor bruges både i Header, Footer og andre Menu-elementer.

### Visual Designer Menu-element

Menu-elementet beskriver **hvordan navigationen vises**:

- valgt menu/navigation source;
- vandret eller lodret præsentation;
- alignment;
- gap mellem menupunkter;
- font, størrelse og vægt;
- normal tekstfarve;
- hover-farve;
- aktiv side-farve;
- baggrund;
- border/radius/padding hvor relevant;
- submenu-design;
- Desktop/Laptop/Mobil-præsentation;
- hamburger/drawer/dropdown på Mobil.

Det betyder:

> Menu-data = struktur og links.  
> Visual Designer = udseende og responsive opførsel.  
> Theme = WordPress runtime og fallback.

---

## 3. Header og Footer er navngivne globale templates

Visual Designer skal understøtte **flere forskellige Header-templates og flere forskellige Footer-templates på samme website**.

De må ikke kopieres ind i hver side. Hver template er sin egen globale canonical model med egen versionshistorik.

Eksempel:

```text
Headers
├── Header – Standard
├── Header – Forside
├── Header – Undersider
└── Header – Kampagne / Landingpage

Footers
├── Footer – Standard
├── Footer – Enkel
└── Footer – Kontakt / Forening
```

Header og Footer vælges **uafhængigt**. En side kan derfor fx bruge:

```text
Header = Header – Forside
Footer = Footer – Standard
```

mens en anden side bruger:

```text
Header = Header – Undersider
Footer = Footer – Standard
```

Ændring af en Header-/Footer-template må ikke oprette nye versioner af de sider, der bruger den.

### Template-egenskaber

Hver Header/Footer-template skal mindst have:

- stabilt internt template-ID;
- navn;
- type: Header eller Footer;
- canonical Designer-model;
- egne settings;
- egen versionshistorik;
- aktiv/inaktiv som tilgængelig template;
- information om hvor den bruges;
- mulighed for at duplikere template;
- mulighed for at omdøbe uden at bryde referencer.

Referencer skal bruge stabile ID'er og ikke templatenavnet.

---

## 4. Hvilken Header/Footer er aktiv? – Assignment Resolver

Der skal være én entydig resolver for Header og én for Footer. Der må aldrig rendere to Headers eller to Footers ved en konflikt.

Prioriteten er:

```text
1. Eksplicit valg på den konkrete side
2. Mest specifikke matchende assignment-regel
3. Website-standard Header/Footer
4. Theme fallback
```

Et eksplicit valg af **Ingen Header** eller **Ingen Footer** stopper kæden og må ikke falde tilbage til standard/template fra temaet.

### A. Website-standard

I Header/Footer Manager vælges præcis én standard Header og én standard Footer, fx:

```text
Standard Header = Header – Standard
Standard Footer = Footer – Standard
```

De bruges på alle sider, hvor intet mere specifikt valg findes.

### B. Valg på den enkelte side

På hver side skal der være en enkel indstilling:

**Header**
- Arv / automatisk
- Header – Standard
- Header – Forside
- Header – Undersider
- …
- Ingen Header

**Footer**
- Arv / automatisk
- Footer – Standard
- Footer – Enkel
- …
- Ingen Footer

`Arv / automatisk` betyder, at resolveren fortsætter til assignment-regler og derefter website-standard.

### C. Assignment-regler

Senere skal en template kunne tildeles flere sider uden at vælge den manuelt på hver enkelt side.

Eksempler:

```text
Header – Forside
→ Side = Hjem

Header – Undersider
→ Alle almindelige sider undtagen Hjem

Header – Kampagne
→ Sider med valgt template/type = Landingpage

Footer – Enkel
→ Udvalgte kampagnesider
```

Første implementation behøver kun understøtte simple regler. Senere kan resolveren udvides med fx:

- specifik side;
- sidetype/post type;
- side-template;
- parent/children;
- kategori/taksonomi hvor relevant;
- logged-in/logged-out hvis der senere er et reelt behov.

Regler skal have eksplicit prioritet og UI'et skal advare om konflikter.

### D. Manager-overblik

Header/Footer Manager skal vise en oversigt som fx:

| Template | Type | Status | Bruges som | Antal anvendelser |
|---|---|---|---|---:|
| Header – Standard | Header | Aktiv | Standard | 8 |
| Header – Forside | Header | Aktiv | Regel: Hjem | 1 |
| Header – Kampagne | Header | Aktiv | Manuelt valg | 2 |
| Footer – Standard | Footer | Aktiv | Standard | 10 |
| Footer – Enkel | Footer | Aktiv | Manuelt valg | 1 |

Der skal være tydelig forskel på:

- **Aktiv template** = kan vælges/anvendes;
- **Standard** = fallback for websitet;
- **Tildelt** = bruges via sidevalg eller regel;
- **Kladde/inaktiv** = findes, men resolveren må ikke vælge den automatisk.

---

## 5. Header Designer

Header bruger samme 120-unit layoutmotor og 8 px lodrette grid som Side Designer.

Elementer bør mindst omfatte:

- Kasse
- Logo/Billede
- Menu
- Tekst
- Knap
- Ikon
- Divider
- Spacer

Header skal have Desktop, Laptop og Mobil-layout med samme element-ID og fælles indhold, men mulighed for breakpoint-specifik geometri og præsentation.

### Header-egenskaber

- aktiv/inaktiv;
- baggrund / transparent;
- full-width baggrund;
- indre content-width;
- minimumshøjde / auto-grow;
- padding;
- border/bundlinje;
- skygge;
- normal eller sticky;
- kontrolleret z-index;
- evt. eksplicit `Overlay første sektion`;
- responsive overrides.

`Fixed`/overlay må ikke opstå implicit. Hvis Header skal ligge over et Hero-element, skal det være en tydelig valgt tilstand.

---

## 6. Menu-element og mobilmenu

Menu-elementets Inspector skal mindst kunne vælge:

- Menu source;
- orientation;
- alignment;
- spacing;
- typografi;
- normal/hover/active farver;
- submenu style;
- responsive behavior.

På Mobil bør Menu-elementet kunne skifte til mindst:

- Hamburger + drawer venstre;
- Hamburger + drawer højre;
- Dropdown under Header.

Fuldskærmsmenu kan tilføjes senere.

Mobilmenuen bruger samme navigation-data; den er ikke en separat kopi af menuen.

Keyboard-navigation, focus trap hvor relevant, Escape-lukning og ARIA-attributter skal indgå i QA.

---

## 7. Footer Designer

Footer bruger samme globale templateprincip og layoutmotor.

Elementer bør mindst omfatte:

- Kasse
- Tekst
- Logo/Billede
- Menu
- Links/Knap
- Ikon
- Divider
- Spacer
- Sociale links

Footer kan bygges som flere rækker/kolonner med Kasser og skal have Desktop/Laptop/Mobil-layout.

Footer er som standard almindeligt dokumentflow efter sideindholdet og ikke fixed/sticky.

---

## 8. Globalt Design

Header, Footer og Menu skal arve defaults fra Globalt Design, fx:

- primær font;
- tekstfarver;
- farvepalette;
- content width;
- standard spacing;
- border/radius defaults.

Lokale Header/Footer/Menu-indstillinger kan overskrive disse defaults.

Global Design kopieres ikke ind i hver Header/Footer-version; modellerne refererer til/arver den aktive globale designkonfiguration.

---

## 9. Theme fallback

Hvis Visual Designer Manager er deaktiveret, eller resolveren ikke kan finde en gyldig aktiv template og ingen eksplicit `Ingen Header/Footer` er valgt, skal temaet kunne vise en sikker minimal fallback.

Fallback kan fx bruge:

- WordPress site logo/site title;
- en valgt WordPress-menu;
- standard semantisk `<header>`, `<nav>` og `<footer>`.

Fallback er driftssikkerhed, ikke en alternativ designmotor.

Når Visual Designer er aktiv og resolveren finder en template, skal dens output være den visuelle sandhed.

---

## 10. Semantik og tilgængelighed

Frontend skal bruge semantiske wrappers:

- `<header>`;
- `<nav>` omkring navigation;
- `<main>` omkring sideindhold;
- `<footer>`.

Menu-elementet skal markere aktiv side korrekt og være fuldt keyboard-brugbart.

---

## 11. Versionering og Preview

Hver Header- og Footer-template får sin egen ikke-destruktive versionshistorik.

Ændringsbeskrivelse ved Gem er valgfri; hvis brugeren ikke skriver en note, genererer Visual Designer automatisk en beskrivelse.

Funktioner:

- Forhåndsvis usavet Header/Footer-template;
- Forhåndsvis historisk version;
- Gendan som ny version;
- duplikér template;
- omdøb template uden at ændre ID;
- se hvilke sider/regler der bruger templaten.

Preview skal kunne vise den valgte Header/Footer sammen med en rigtig side og kunne skifte Desktop/Laptop/Mobil.

Hvis en template har assignment-regler, skal Preview kunne vælge en testsides kontekst, så man kan se den reelle resolver-kombination.

---

## 12. Export / Import

Visual Designer Manager-menuen skal senere have et selvstændigt `Export`-område.

Header/Footer/Menu/Theme-konfiguration skal kunne eksporteres sammen med:

- Plugin;
- Theme;
- Webpages;
- uploadede billeder;
- dokumenter;
- video;
- Global Design;
- alle Header/Footer-templates;
- standardvalg og assignment-regler;
- Navigation/Menu-data;
- komponenter/presets;
- relevante site-specifikke moduler.

Eksportpakker skal have manifest, schema/version og SHA-256-verifikation.

En samlet website-export skal kunne genskabe sammenhængen mellem Theme shell, Menu-data, Header/Footer-templates, assignments, sider og medier uden at hardcode et bestemt website-brand.

---

## 13. Implementationsrækkefølge

Før Header/Footer implementeres produktionsklart, skal den fælles Side Designer-layoutmotor være stabil.

Anbefalet rækkefølge:

1. 0.1.22 – hierarki og layout-QA;
2. 0.1.23 – første globale Header/Footer-model og fælles Designer-canvas;
3. migrér fase-1 single Header/Footer til **navngivne templates** med stabile template-ID'er;
4. implementér Standard Header/Footer + side-level `Arv / konkret template / Ingen`;
5. Header/Footer layout-QA med Sektion/Kasse/Tekst/Billede;
6. Global Design-model og Theme-shell-kontrakt;
7. simple assignment-regler og resolver-QA;
8. Menu-element oven på eksisterende Menu-data;
9. mobilmenu og accessibility-QA;
10. parity-test mod eksisterende site;
11. Export/Import integration.

### Migrationsregel fra 0.1.23 fase 1

Den eksisterende ene Header og ene Footer i `GlobalLayoutModel` er kun fase-1 storage. Før Theme-shell aktiveres offentligt, migreres de uden datatab til:

```text
Header – Standard
Footer – Standard
```

med nye stabile template-ID'er. De gamle option-navne må kun bruges som migrationskilde og kompatibilitetslag; de må ikke blive den permanente multi-template-arkitektur.

---

## 14. Definition of Done for multi-template Header/Footer

Funktionen er ikke grøn/Klar før følgende er opfyldt:

- mindst to Header-templates kan eksistere samtidigt;
- mindst to Footer-templates kan eksistere samtidigt;
- hver template har egen versionering;
- én Header og én Footer kan vælges som website-standard;
- en konkret side kan override Header og Footer uafhængigt;
- `Ingen Header` og `Ingen Footer` virker eksplicit;
- resolverens prioritet er deterministisk og QA-testet;
- en inaktiv template kan ikke vælges automatisk;
- frontend viser aldrig to Headers eller to Footers ved konflikt;
- Preview viser samme templatevalg som frontend;
- eksisterende fase-1 Header/Footer migreres uden datatab.

Denne fil er den autoritative detaljespecifikation for grænsen mellem Header, Footer, Menu og Theme.