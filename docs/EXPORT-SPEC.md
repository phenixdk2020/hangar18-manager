# Visual Designer Manager – Export-specifikation

**Statusdato:** 25. august 2026  
**Status:** Godkendt backlog/specifikation  
**Produktnavn:** Visual Designer Manager

## Formål

Visual Designer Manager skal have et selvstændigt hovedmenupunkt i WordPress med navnet **Export**.

Export skal gøre det muligt at tage kontrollerede, verificerbare eksportpakker af program, tema, sider og uploadede mediefiler uden at være afhængig af hostingens filmanager.

Export er adskilt fra den automatiske programbackup før update. Backup beskytter en ændring; Export bruges til bevidst download, arkivering, flytning og senere import/restore.

## Manager-menu

```text
Visual Designer Manager
├── Visual Designer
├── Globalt design
├── Header / Footer
├── Sider
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
4. **Export Medier**
5. **Export hele sitet** – senere samlet pakke

Hver eksport skal vise hvad der inkluderes, forventet størrelse hvis muligt, dato/tid og resultat af verifikation.

---

## 1. Export Plugin

Eksporter den installerede Visual Designer Manager-pluginmappe som ZIP.

Pakken skal indeholde:
- pluginfiler;
- versionsnummer;
- filmanifest;
- SHA-256 for ZIP-pakken;
- eksportdato/-tid;
- WordPress/PHP compatibility metadata hvor relevant.

Må ikke eksportere:
- credentials;
- nonces;
- auth cookies;
- server-secrets;
- midlertidige cachefiler.

Standard filnavn, eksempel:

`visual-designer-manager-plugin-v0.1.22-20260825-223000.zip`

---

## 2. Export Tema

Eksporter det aktive tema eller et valgt installeret tema som ZIP.

Pakken skal indeholde:
- temafiler;
- theme-version;
- manifest;
- SHA-256;
- eksportdato/-tid.

Hvis Visual Designer Manager senere styrer globale theme-/shell-indstillinger, skal disse kunne vælges som separat JSON ved siden af selve temafilerne.

Standard filnavn, eksempel:

`visual-designer-theme-1.2.0-20260825-223000.zip`

---

## 3. Export Webpages

Webpages skal eksporteres som strukturerede data, ikke kun som rendered HTML.

Valgmuligheder:
- alle sider;
- udvalgte sider;
- kun publicerede;
- kladder;
- evt. historiske Designer-versioner.

En sideexport skal kunne indeholde:
- WordPress page ID som kilde-reference;
- titel;
- slug;
- status;
- parent/menu-relationer hvor relevant;
- canonical Visual Designer-model;
- Designer-versionshistorik hvis valgt;
- ændringsbeskrivelser;
- references til medier;
- references til globale komponenter/datamoduler;
- strukturel digest/checksum.

Eksportformat bør være JSON i en ZIP med manifest, så senere Import kan lave dry-run, ID-remapping og konfliktkontrol.

Rendered HTML kan eventuelt tilbydes som ekstra eksportformat, men må ikke erstatte den canonical model.

---

## 4. Export Medier

Medieexport omfatter WordPress Media Library-filer, herunder:
- billeder;
- dokumenter, fx PDF/DOCX;
- video;
- øvrige uploadede filer.

Valgmuligheder bør mindst omfatte:
- alle medier;
- kun billeder;
- kun dokumenter;
- kun video;
- udvalgte filer;
- medier brugt af udvalgte sider;
- medier brugt af et bestemt datamodul/event/køretøj når relationerne findes.

ZIP-pakken skal bevare nok metadata til senere import:
- originalt filnavn;
- relativ uploads-path;
- MIME type;
- WordPress attachment ID som kilde-reference;
- titel/caption/alt-tekst hvor relevant;
- filstørrelse;
- SHA-256 pr. fil;
- references fra Designer/dataobjekter hvis valgt.

Export må ikke antage, at kun billeder findes i Media Library.

---

## 5. Samlet site-export

Senere skal Export kunne lave én transportabel pakke med valgbare dele:

```text
SITE EXPORT
├── Visual Designer Manager plugin
├── Tema
├── Globalt design
├── Header / Footer
├── Webpages + versionshistorik
├── Komponenter / presets
├── Data-moduler
│   ├── Køretøjer (hvis modulet findes)
│   ├── Events (hvis modulet findes)
│   └── Galleri-data (hvis modulet findes)
├── Navigation/menuer
└── Medier
```

Dette skal være modulært, så et website uden Hangar18-specifikke moduler stadig kan eksporteres fuldt.

---

## Manifest og integritet

Alle ZIP-exports skal have et maskinlæsbart manifest, fx `visual-designer-export.json`, med:
- export schema version;
- export type;
- produktversion;
- WordPress version;
- PHP version hvor relevant;
- source site URL/identifier uden secrets;
- created UTC/local timestamp;
- included modules;
- filer og checksums;
- package checksum.

SHA-256 skal bruges til integritetskontrol.

---

## Sikkerhed

- Kun autoriserede administratorer må eksportere plugin/tema/hele sitet.
- Side-/medieexport skal følge relevante WordPress capabilities.
- Export må aldrig inkludere `wp-config.php`, databasecredentials, API-secrets, auth keys, nonces, sessioncookies eller andre credentials.
- Store exports skal fejle kontrolleret med tydelig status og må ikke efterlade halvfærdige offentligt tilgængelige ZIP-filer.
- Midlertidige exportfiler skal ligge i et beskyttet område og slettes efter download/udløb.

---

## Forhold til Import/Restore

Export-formatet skal designes, så en senere **Import** kan bruge samme schema.

Import skal senere have:
- dry-run;
- checksum-verifikation;
- versions/schema-check;
- ID-remapping;
- slug-konflikter;
- media deduplication via checksum;
- reference-rewrite mellem sider, medier, komponenter og dataobjekter;
- mulighed for at importere enkelte dele af en samlet export.

Export udvikles først; Import må ikke improvisere et inkompatibelt format senere.

---

## QA

Før Export markeres PASS:

1. Plugin-export kan pakkes ud og matcher manifestet.
2. Tema-export kan pakkes ud og matcher manifestet.
3. Sideexport kan round-trip gennem en test-import uden tab af canonical Designer-model.
4. Medieexport indeholder billeder, dokumenter og video med korrekte checksums.
5. References mellem sider og medier kan rekonstrueres.
6. Ingen secrets findes i exportpakken.
7. SHA-256-verifikation opdager en ændret/korrupt fil.
8. Store eksportjob giver kontrolleret fejl/status.
9. Export fungerer også på et site uden Hangar18-specifikke moduler.

---

## Produktarkitektur

Export er en del af den generiske **Visual Designer Manager Core** og må ikke være Hangar18-specifik.

Hangar18 er et website/projekt og kan have ekstra export-adapters til site-specifikke datamoduler, men Core Export skal fungere på ethvert kompatibelt WordPress-site.
