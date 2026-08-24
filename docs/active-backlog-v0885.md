# Hangar18 Manager — canonical backlog delta v0.8.85

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.84 installeret og manuelt testet  
**Extends:** `docs/active-backlog-v0884.md`

Denne delta registrerer tre konkrete fidelity-regressioner fundet i v0.8.84: frontend-forhåndsvisning viser ikke den aktuelle editor-state, LEGO-kolonnebredderne er kun autoritative i editoren og tomme kolonner afspejler ikke deres faktiske footprint/højde tydeligt nok. Derudover præciseres Inspector-halen med Layout-hierarki mellem Mediebibliotek og de avancerede sektioner.

## Manuel evidens fra v0.8.84

- Frontend-forhåndsvisning viser header og footer men kan vise blankt sideindhold, mens editoren indeholder en Række-/kolonne-kasse med et Billede-element.
- Samme layout viser forskellig kolonnefordeling i editor og rigtig frontend; editoren kan vise omtrent 4/12 + 8/12, mens frontend viser den modsatte/ældre fordeling.
- Et tomt element er fortsat et layout-element og skal derfor reservere sin tildelte bredde og rækkens højde i editoren, selv uden tekst/billede.
- `hangar18_ultimate_designer_lego_layout_span_v1` har hidtil været renderer-neutral og er derfor ikke anvendt af public frontend-rendering.

# H. Inspector-rækkefølge

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| INSPECTOR-ORDER-095 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.85 | Inspectorens faste hale er **Billede/Mediebibliotek → Layout-hierarki → Dynamic data binding → Conditions / synlighed** for medie-typer. For elementer uden medie er halen **Layout-hierarki → Dynamic data binding → Conditions / synlighed**. Dynamic og Conditions starter foldet ind. Kun v0.8.85 order-runtime må eje denne rækkefølge; ældre Selection Inspector må ikke flytte blokkene tilbage eller genoprette en konkurrerende Avanceret-heading. |

# L. Frontend / canvas layout parity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| FRONTEND-SPAN-094 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.85 | Den gemte 12-kolonne LEGO span-state skal være fælles autoritet for editor, live preview og public frontend. Grid/Flex-børn skal bruge samme effektive Desktop/Tablet/Mobile spans som resize-runtime. Public renderer må ikke længere falde tilbage til en separat lige-fordeling, når eksplicitte spans findes. |
| CANVAS-FIDELITY-093 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.85 | En tom grid-kolonne skal stadig optage sin fulde tildelte span-bredde og strække sig til rækkens højde i editoren. Tomt indhold må ikke få kolonnen til visuelt at kollapse eller give et falsk billede af frontend-geometrien. Rettelsen er CSS-only og må ikke ændre resize/drag/drop JavaScript. |

# V. Frontend-forhåndsvisning

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PREVIEW-LIVE-092 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.85 | **Forhåndsvis side** skal vise den aktuelle, også ugemte editor-state gennem den rigtige public PHP-renderer. Klik må ikke gemme WordPress-siden eller canonical page-option. Editor-form og aktuelle LEGO spans lægges i en kortlivet, brugerbeskyttet preview-transient; iframe renderer via read-only token og no-cache/noindex. |

# Manuel v0.8.85 testmatrix

1. Opret en Række-/kolonne-kasse med en tom venstre kolonne og et Billede i højre kolonne; sæt fx 4/12 + 8/12.
2. Bekræft i editoren at den tomme 4/12-kolonne stadig er tydeligt 4/12 bred og strækker sig til samme rækkehøjde som billedkolonnen.
3. Tryk **Forhåndsvis side uden at gemme**. Preview skal vise det aktuelle billede og samme 4/12 + 8/12-geometri; siden må ikke være blevet gemt.
4. Gem siden og åbn den rigtige frontend. Editor, preview og frontend skal have samme kolonnebredder.
5. Gentag med en anden fordeling, fx 8/12 + 4/12, samt Tablet/Mobil hvor egne spans er sat.
6. Vælg Billede i Inspector: rækkefølgen nederst skal være **Billede/Mediebibliotek → Layout-hierarki → Dynamic data binding → Conditions / synlighed**.
7. Vælg et element uden medie: **Layout-hierarki → Dynamic data binding → Conditions / synlighed** skal være de sidste tre relevante blokke.
8. Dynamic data binding og Conditions / synlighed skal starte foldet ind og kunne åbnes/lukkes uden repaint-loop.
9. Regression: højre/venstre/over/under placement og Billede-insert skal stadig fungere uden freeze.
