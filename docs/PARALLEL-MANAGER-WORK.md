# Visual Designer Manager – parallelle arbejdsområder

**Statusdato:** 26. august 2026  
**Aktuel offentlig release:** 0.1.21  
**Status:** Godkendt udviklingsprincip og forward-development på `main`

## Formål

Ikke alle dele af Visual Designer Manager behøver vente på den visuelle Designer/layoutmotor. Funktioner med en stabil, selvstændig WordPress-kontrakt må udvikles parallelt, så længe de ikke ændrer eller duplikerer Designerens canonical ansvar.

## Må udvikles uafhængigt af Designer-canvas

### Export
- selvstændigt Manager-menupunkt `Export`;
- Export Plugin;
- Export Tema;
- Export Webpages inkl. canonical Visual Designer-model/versioner;
- Export billeder;
- Export dokumenter;
- Export video;
- Export alle medier;
- manifest og SHA-256;
- senere samlet site-export og Import.

Forward-development findes i `src/Admin/ExportController.php`.

### Menu / Navigation-data
- liste/opret WordPress-menuer;
- tilføj sider og custom links;
- titel, parent/hierarki og rækkefølge;
- slet menupunkt;
- tildel theme-locations;
- strukturelt snapshot før Manager-ændringer.

Forward-development findes i `src/Admin/NavigationController.php`.

Menu-data er **ikke** menu-design. Farver, typografi, spacing, dropdown/hamburger/drawer og fysisk placering tilhører senere Visual Designer Menu-element + Header/Footer Designer.

### Tema / Shell-status
- aktivt tema og version;
- parent-theme status;
- theme supports;
- menu-locations;
- adgang til Theme-export;
- dokumenteret ansvarsgrænse mellem Theme og Visual Designer.

Forward-development findes i `src/Admin/ThemeController.php`.

Denne side ændrer endnu ikke den offentlige theme-runtime.

## Skal fortsat vente på Designer/global model

Følgende må ikke implementeres som parallel specialkode:
- visuel Header-layout;
- visuel Footer-layout;
- Menu-elementets styling og responsive præsentation;
- global palette/typografi/sidebredde som frontend-sandhed;
- theme-shell overtagelse af Header/Footer-rendering;
- per-side valg af global/alternativ/ingen Header/Footer.

Disse dele skal genbruge Visual Designerens canonical 120-unit/8-px motor, responsive Desktop/Laptop/Mobil-model og versionsprincipper.

## Ansvarsgrænse

| Område | Source of truth |
|---|---|
| WordPress templates/hooks/fallback | Tema |
| Menupunkter, hierarki, rækkefølge og links | Navigation-data |
| Menuens visuelle design/adfærd | Visual Designer Menu-element |
| Header/Footer placering og layout | Global Header/Footer Designer |
| Global palette, typografi og bredder | Globalt design |
| Sider og elementgeometri | Visual Designer canonical model |

## QA-status

Dev artifact workflow blev udvidet til at linte alle PHP-filer og syntax-checke alle JavaScript-filer under den aktive plugin-source.

Efter rettelse af en parsefejl i NavigationController blev workflow run `32938048743` kørt mod commit `450bd65ed8eb6899fbc3df033c79d9c239fbf2f3` og afsluttet med `success`:
- Verify clean source: PASS
- Build installable ZIP: PASS
- Upload development artifact: PASS

Dette er udviklings-QA og **ikke** en offentlig release. `clean-update.json` afgør fortsat seneste frigivne version.

## Release-regel

De parallelle Manager-funktioner må samles i en kommende release, når deres runtime-QA og dokumentation er gennemført. De må ikke alene få den eksisterende 0.1.21-release til at blive omtalt som ændret eller genudgivet.
