# Visual Designer Manager – parallelle arbejdsområder

**Statusdato:** 26. august 2026  
**Aktuel offentlig release:** 0.1.21  
**Status:** Godkendt udviklingsprincip og forward-development på `main`

## Formål

Ikke alle dele af Visual Designer Manager behøver vente på den visuelle Designer/layoutmotor. Funktioner med en stabil, selvstændig WordPress-kontrakt må udvikles parallelt, så længe de ikke ændrer eller duplikerer Designerens canonical ansvar.

## Må udvikles uafhængigt af Designer-canvas

### Export

Forward-development findes i `clean/hangar18-manager/src/Admin/ExportController.php`.

Aktuelt bygget i source:
- selvstændigt Manager-menupunkt `Export`;
- Export Plugin;
- Export Tema;
- child-theme export inkluderer parent-theme når det findes;
- Export Webpages inkl. canonical Visual Designer-model og versionshistorik;
- Webpages indeholder kendte mediereferencer til featured image, Visual Designer-billeder og kendte WordPress-gallerier/billeder;
- Export Navigation med menuer, menupunkter, parent-hierarki og theme-locations;
- Export billeder;
- Export dokumenter;
- Export video;
- Export alle medier;
- Media-export gemmer attachment-metadata og hvilke filer der hører til attachmentet;
- `visual-designer-export.json` med filmanifest, SHA-256 pr. fil og samlet content-digest;
- den færdige ZIPs SHA-256 sendes som `X-Visual-Designer-SHA256` ved download;
- filesystem-export afviser kendte secret-filer og symlink/realpath-filer uden for den tilladte plugin/theme-root.

Fortsat planlagt:
- valg af enkelte sider/medier;
- størrelses-estimat før export;
- samlet site-export;
- Import/dry-run/ID-remapping/deduplication.

### Menu / Navigation-data

Forward-development findes i `clean/hangar18-manager/src/Admin/NavigationController.php`.

Aktuelt bygget i source:
- liste/opret WordPress-menuer;
- tilføj sider og custom links;
- titel, parent/hierarki og rækkefølge;
- slet menupunkt;
- tildel theme-locations;
- parent-cirkelbeskyttelse;
- komplet strukturelt snapshot før Manager-ændringer;
- op til 30 snapshots;
- versionsoversigt med dato, årsag, menu-/punktantal og bruger;
- detaljevisning af et snapshot;
- stabil snapshot-fingerprint;
- sikker `Gendan dette snapshot`;
- før restore gemmes den aktuelle navigation automatisk som nyt sikkerhedssnapshot;
- restore rekonstruerer menuer, items, parent-relationer og theme-locations;
- manglende ikke-custom objekter kan falde tilbage til custom link med den gemte URL;
- snapshot-restore er global navigation restore og bringer menu-sættet tilbage til snapshot-tilstanden.

Menu-data er **ikke** menu-design. Farver, typografi, spacing, dropdown/hamburger/drawer og fysisk placering tilhører senere Visual Designer Menu-element + Header/Footer Designer.

### Tema / Shell-status

Forward-development findes i `clean/hangar18-manager/src/Admin/ThemeController.php`.

Aktuelt bygget i source:
- aktivt tema og version;
- parent-theme status;
- theme supports;
- menu-locations;
- adgang til Theme-export;
- dokumenteret ansvarsgrænse mellem Theme og Visual Designer.

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
| Transportpakker og integritetsmanifest | Export |

## QA-status

Dev artifact workflow linter alle PHP-filer og syntax-checker alle JavaScript-filer under den aktive plugin-source, bygger derefter en installérbar udviklings-ZIP.

Seneste QA efter Menu restore/history og udvidet Export:

- workflow run `32938880719`;
- head `60d7fef0ff6d679f4ce0cb78e50ca1c05af973e4`;
- Verify Visual Designer source: **PASS**;
- Build installable ZIP: **PASS**;
- Upload development artifact: **PASS**.

Tidligere QA fandt en PHP-parsefejl i NavigationController. Fejlen blev rettet før ovenstående PASS. Dette er et eksempel på, at dev-artifact-gaten skal køres efter hver parallel kodeændring.

Dette er udviklings-QA og **ikke** en offentlig release. `Visual Designer-update.json` afgør fortsat seneste frigivne version.

## Runtime-QA der stadig mangler før offentlig release

Syntax/build PASS erstatter ikke WordPress-runtime-test. Før funktionerne frigives skal mindst følgende testes på testsite:

1. opret/rediger menu og parent-relationer;
2. snapshot oprettes før ændring;
3. snapshot-detaljer viser korrekt struktur;
4. restore genskaber menuer og locations og efterlader sikkerhedssnapshot;
5. Plugin-export kan downloades og pakkes ud;
6. Theme-export indeholder både child og parent når relevant;
7. Webpages-export indeholder canonical layouts/history;
8. Navigation-export indeholder korrekt parent/location-data;
9. Media-export indeholder forventede filer og checksums;
10. ingen kendte secrets eller filer uden for de tilladte roots kommer med.

## Release-regel

De parallelle Manager-funktioner må samles i en kommende release, når runtime-QA og dokumentation er gennemført. De må ikke alene få den eksisterende 0.1.21-release til at blive omtalt som ændret eller genudgivet.
