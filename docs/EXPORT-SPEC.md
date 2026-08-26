# Visual Designer Manager – Export-specifikation

**Statusdato:** 26. august 2026  
**Status:** Godkendt specifikation + delvist implementeret som forward-development  
**Produktnavn:** Visual Designer Manager

## Formål

Visual Designer Manager skal have et selvstændigt menupunkt i WordPress med navnet **Export**.

Export skal gøre det muligt at tage kontrollerede, verificerbare eksportpakker af program, tema, sider, navigation og uploadede mediefiler uden at være afhængig af hostingens filmanager.

Export er adskilt fra den automatiske programbackup før update. Backup beskytter en ændring; Export bruges til bevidst download, arkivering, flytning og senere Import/Restore.

## Aktuel implementationsstatus

Forward-development findes i `clean/hangar18-manager/src/Admin/ExportController.php`.

Allerede implementeret i source:

- **Export Plugin**;
- **Export Tema**;
- **Export Webpages**;
- **Export Navigation**;
- **Export Billeder**;
- **Export Dokumenter**;
- **Export Video**;
- **Export Alle medier**;
- manifest med SHA-256 pr. fil og samlet content-digest;
- ZIP-download med package SHA-256 i HTTP-header;
- sikkerhedsfilter mod kendte secret-filer og filer uden for tilladt root;
- child-theme export inkluderer parent-theme når det findes;
- Webpages inkluderer canonical Visual Designer-model/versioner og kendte media source IDs.

Dette er endnu ikke en offentlig release. Seneste offentlige version afgøres altid af `clean-update.json`.

## Manager-menu

```text
Visual Designer Manager
├── Visual Designer
├── Globalt design
├── Header / Footer
├── Sider
├── Menu / Navigation
├── Data / site-moduler
├── Backup
├── Export
├── Opdateringer
└── Log / Diagnose
```

## Export-forside

Export-siden skal som minimum have disse handlinger:

1. **Export Plugin**
2. **Export Tema**
3. **Export Webpages**
4. **Export Navigation**
5. **Export Billeder**
6. **Export Dokumenter**
7. **Export Video**
8. **Export Alle medier**
9. **Export hele sitet** – senere samlet pakke

---

## 1. Export Plugin

Eksporter den installerede Visual Designer Manager-pluginmappe som ZIP.

Pakken indeholder:
- pluginfiler;
- produkt-/intern versionsmetadata;
- filmanifest;
- SHA-256 pr. fil;
- samlet content-digest;
- eksportdato/-tid og miljømetadata i manifestet.

Eksporten må ikke følge symlinks eller realpaths uden for pluginroden og skal springe kendte secret-/udviklingsfiler over.

---

## 2. Export Tema

Eksporter det aktive tema som transportabel ZIP.

Hvis det aktive tema er et child-theme, inkluderes også parent-theme, fordi child-theme ellers ikke nødvendigvis kan installeres/fungere på et nyt site.

Pakken skal indeholde:
- aktive temafiler;
- parent-theme filer når relevant;
- theme-navn/version/stylesheet/template;
- theme mods;
- aktuelle menu-location references;
- manifest/checksums.

Theme-export må ikke være den visuelle source of truth for fremtidigt Global Design/Header/Footer. Den transporterer theme-shell og eksisterende theme-indstillinger.

---

## 3. Export Webpages

Webpages eksporteres som strukturerede data, ikke kun rendered HTML.

Aktuel export indeholder for hver side:
- WordPress page ID som `sourceId`;
- parent source ID;
- titel;
- slug;
- status;
- dato/ændringsdato;
- WordPress content/excerpt;
- menu order;
- template;
- featured image source ID;
- kendte media source IDs;
- canonical Visual Designer-model når den findes;
- aktuel Designer-version;
- strukturel digest;
- Designer-versionshistorik.

Kendte mediereferencer omfatter aktuelt:
- featured image;
- Visual Designer image-nodes;
- `wp-image-ID` references i WordPress-content;
- kendte WordPress gallery IDs.

Sidepakken indeholder også source IDs for WordPress front page/posts page, så en senere Import kan remappe dem.

Fremtidige valgmuligheder:
- alle sider;
- udvalgte sider;
- kun publicerede;
- kladder;
- med/uden historiske Designer-versioner.

---

## 4. Export Navigation

Navigation eksporteres separat fra det visuelle Menu-element.

Pakken indeholder:
- alle WordPress-menuer;
- menu source ID/navn/slug;
- menupunkter;
- titel/URL/type/object/objectId;
- parent source ID;
- rækkefølge;
- target/classes/attr title/description/XFN;
- registrerede theme-locations;
- aktuelle location → menu source ID relationer.

Dette format skal kunne bruges af senere Import til at oprette menuer med nye WordPress IDs og remappe parent/location-relationer.

---

## 5. Export Medier

Medieexport omfatter WordPress Media Library-filer, herunder:
- billeder;
- dokumenter, fx PDF/DOCX/XLSX/TXT/CSV;
- video;
- øvrige uploadede filer.

Aktuelle separate exports:
- kun billeder;
- kun dokumenter;
- kun video;
- alle medier.

Hver attachment-record indeholder bl.a.:
- source attachment ID;
- titel/slug;
- MIME type;
- dato/ændringsdato;
- caption/description/alt;
- `_wp_attached_file`;
- WordPress attachment metadata;
- liste over de konkrete archive-filer, der hører til attachmentet.

For billeder inkluderes også registrerede WordPress size-filer/original-image, når de findes under uploads-roden.

Fremtidige valgmuligheder:
- udvalgte filer;
- medier brugt af udvalgte sider;
- medier brugt af et bestemt datamodul/event/køretøj.

---

## 6. Samlet site-export

Senere skal Export kunne lave én transportabel pakke med valgbare dele:

```text
SITE EXPORT
├── Visual Designer Manager plugin
├── Tema
├── Globalt design
├── Header / Footer
├── Webpages + versionshistorik
├── Komponenter / presets
├── Navigation/menuer
├── Data-moduler
│   ├── Køretøjer (hvis modulet findes)
│   ├── Events (hvis modulet findes)
│   └── Galleri-data (hvis modulet findes)
└── Medier
```

Dette skal være modulært, så et website uden Hangar18-specifikke moduler stadig kan eksporteres fuldt.

---

## Manifest og integritet

Alle ZIP-exports indeholder `visual-designer-export.json` med mindst:
- export schema version;
- export type/label;
- produktversion;
- WordPress/PHP-version;
- source site navn/URL uden secrets;
- created UTC;
- record count;
- filantal;
- hver fil med path, størrelse og SHA-256;
- samlet `contentSha256` beregnet over det sorterede filmanifest.

### Package SHA-256

Den færdige ZIPs SHA-256 kan ikke ligge inde i selve ZIP-manifestet uden at skabe en cirkulær checksum-afhængighed. Derfor sendes package SHA-256 ved download som:

`X-Visual-Designer-SHA256`

En senere download-log/UI kan gemme og vise denne værdi sammen med eksporttidspunkt og filnavn.

---

## Sikkerhed

- Kun administratorer med `manage_options` må køre de aktuelle exports.
- Midlertidige ZIP-filer oprettes via WordPress temp-mekanisme og slettes efter download/failure.
- Export må ikke inkludere `wp-config.php`, databasecredentials, auth cookies eller andre secrets.
- Plugin/theme filesystem-export kontrollerer realpath mod tilladt root, så eksterne symlink-targets ikke eksporteres.
- Kendte secret-filer som `.env*`, `auth.json`, `credentials.json`, `secrets.json`, private key-navne m.fl. springes over.
- Store exports skal senere få tydelig size/progress/error-håndtering frem for ukontrolleret timeout.

---

## Forhold til Import/Restore

Export-formatet designes med Import for øje.

Import skal senere have:
- dry-run;
- checksum-verifikation;
- schema/version-check;
- ID-remapping;
- slug-konflikter;
- media deduplication via checksum;
- reference-rewrite mellem sider, medier, navigation, komponenter og dataobjekter;
- mulighed for at importere enkelte dele af en samlet export.

Export udvikles først; Import må ikke improvisere et inkompatibelt format senere.

---

## QA-gate

Før Export markeres produktionsklar/PASS:

1. Plugin-export kan downloades, pakkes ud og matcher manifestet.
2. Tema-export kan downloades og inkluderer parent-theme korrekt ved child-theme.
3. Webpages-export indeholder canonical Designer-model og historik uden tab.
4. Navigation-export indeholder korrekt menu-/parent-/location-data.
5. Medieexport indeholder billeder, dokumenter og video med korrekte checksums.
6. References mellem sider og medier kan rekonstrueres.
7. Ingen kendte secrets eller realpath-filer uden for tilladte roots findes i pakkerne.
8. Content-digest opdager ændringer i filmanifestet.
9. Package SHA-256 kan verificeres efter download.
10. Store eksportjob giver kontrolleret status/fejl.
11. Export fungerer på et site uden Hangar18-specifikke moduler.
12. Senere test-import kan round-trip canonical layouts og navigation med ID-remapping.

## Produktarkitektur

Export er en del af den generiske **Visual Designer Manager Core** og må ikke være Hangar18-specifik.

Site-specifikke datamoduler kan senere registrere egne export-adapters, men Core Export skal fungere på ethvert kompatibelt WordPress-site.
