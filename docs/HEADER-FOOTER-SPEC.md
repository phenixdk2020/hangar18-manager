# Visual Designer – Header, Footer, Menu og Theme

**Statusdato:** 26. august 2026  
**Status:** Godkendt målarkitektur før implementation  
**Produkt:** Visual Designer / Visual Designer Manager

## 1. Grundprincip

Header, Footer, Menu og Theme hænger sammen, men deres ansvar skal være klart adskilt.

Den ønskede arkitektur er:

```text
WORDPRESS / THEME SHELL
│
├── Global Header-model fra Visual Designer
│   ├── Logo
│   ├── Menu-element → Navigation-data
│   ├── Tekst / Knap / Ikon / Kasser
│   └── Responsive Desktop / Laptop / Mobil
│
├── Side-model fra Visual Designer
│
└── Global Footer-model fra Visual Designer
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
- fallback Header/Menu/Footer hvis Visual Designer Manager ikke er aktiv eller ingen global model findes;
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

## 3. Header og Footer er globale Visual Designer-modeller

Header og Footer skal ikke kopieres ind i hver side.

Der oprettes globale canonical modeller med egen versionshistorik:

- Header
- Footer

En side gemmer kun reference/anvendelse, fx:

```text
Header = Global
Footer = Global
```

Senere kan en side vælge:

- Global Header
- Ingen Header
- alternativ navngivet Header-template
- Global Footer
- Ingen Footer
- alternativ navngivet Footer-template

Ændring af global Header/Footer må ikke oprette ny version af alle sider.

---

## 4. Header Designer

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

## 5. Menu-element og mobilmenu

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

## 6. Footer Designer

Footer bruger samme globale modelprincip og layoutmotor.

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

## 7. Globalt Design

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

## 8. Theme fallback

Hvis Visual Designer Manager er deaktiveret eller den globale Header/Footer-model mangler, skal temaet kunne vise en sikker minimal fallback.

Fallback kan fx bruge:

- WordPress site logo/site title;
- en valgt WordPress-menu;
- standard semantisk `<header>`, `<nav>` og `<footer>`.

Fallback er driftssikkerhed, ikke en alternativ designmotor.

Når Visual Designer er aktiv, skal dens output være den visuelle sandhed.

---

## 9. Semantik og tilgængelighed

Frontend skal bruge semantiske wrappers:

- `<header>`;
- `<nav>` omkring navigation;
- `<main>` omkring sideindhold;
- `<footer>`.

Menu-elementet skal markere aktiv side korrekt og være fuldt keyboard-brugbart.

---

## 10. Versionering og Preview

Header og Footer får hver deres ikke-destruktive versionshistorik.

Hver Gem kræver ændringsbeskrivelse.

Funktioner:

- Forhåndsvis usavet Header/Footer;
- Forhåndsvis historisk version;
- Gendan som ny version;
- senere kopier/skabeloner.

Preview skal kunne vise Header/Footer sammen med en rigtig side og kunne skifte Desktop/Laptop/Mobil.

---

## 11. Export / Import

Visual Designer Manager-menuen skal senere have et selvstændigt `Export`-område.

Header/Footer/Menu/Theme-konfiguration skal kunne eksporteres sammen med:

- Plugin;
- Theme;
- Webpages;
- uploadede billeder;
- dokumenter;
- video;
- Global Design;
- Header/Footer;
- Navigation/Menu-data;
- komponenter/presets;
- relevante site-specifikke moduler.

Eksportpakker skal have manifest, schema/version og SHA-256-verifikation.

En samlet website-export skal kunne genskabe sammenhængen mellem Theme shell, Menu-data, Header/Footer, sider og medier uden at hardcode et bestemt website-brand.

---

## 12. Implementationsrækkefølge

Før Header/Footer implementeres produktionsklart, skal den fælles Side Designer-layoutmotor være stabil.

Anbefalet rækkefølge:

1. 0.1.22 – hierarki og layout-QA;
2. 0.1.23 – global Header/Footer-model og fælles Designer-canvas;
3. Header/Footer layout-QA med Sektion/Kasse/Tekst/Billede;
4. Global Design-model og Theme-shell-kontrakt;
5. Menu-element oven på eksisterende Menu-data;
6. mobilmenu og accessibility-QA;
7. parity-test mod eksisterende site;
8. Export/Import integration.

Denne fil er den autoritative detaljespecifikation for grænsen mellem Header, Footer, Menu og Theme.