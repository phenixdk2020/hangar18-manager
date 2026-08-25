# Visual Designer – navnestandard

**Statusdato:** 25. august 2026  
**Status:** Godkendt navnestandard fra og med planlagt release 0.1.22

## Officielle synlige navne

### Visual Designer
Navnet på selve den visuelle Designer, hvor sider, Header og Footer bygges med elementer, grid, responsive layouts og Inspector.

Eksempler på UI-tekst:
- `Visual Designer`
- `Åbn Visual Designer`
- `Visual Designer · Desktop / Laptop / Mobil`

### Visual Designer Manager
Navnet på hele WordPress-administrationspakken/pluginet omkring Visual Designer.

Den generiske kerne omfatter på sigt bl.a.:
- Visual Designer;
- Globalt design;
- Header/Footer;
- Sider og navigation;
- Komponenter/presets;
- Backup/rollback;
- Export/Import;
- Opdateringer;
- Diagnose/log.

Website-specifikke datamoduler, fx Køretøjer, Events og specialgallerier, må ligge som konfigurerbare moduler oven på den generiske kerne og må ikke være en forudsætning for at bruge Visual Designer Manager på andre websites.

## Site-branding

Produktnavnet skal være uafhængigt af det website, det installeres på.

Site-branding skal være konfiguration og kan fx indeholde:
- Website-/organisationsnavn;
- logo;
- farvepalette;
- standardtypografi;
- site-specifikke datamoduler;
- eventuelle speciallabels.

Som standard kan Visual Designer Manager bruge WordPress' site title som website-navn, men det ændrer ikke pluginets produktnavn.

## Versionsnavn

Synlige versionsreferencer skal fremover skrives som fx:

`Visual Designer Manager 0.1.22`

Når konteksten kun handler om editoren, kan der stå:

`Visual Designer 0.1.22`

## Hangar18 er site/projekt – ikke produktnavn

Hangar18 er det første website/projekt, som Visual Designer Manager udvikles og testes imod. Hangar18-navnet må derfor bruges i site-specifik konfiguration, datamoduler, migreringsnoter og parity-test, men ikke som permanent produktprefix.

## Clean er kun intern teknisk generationsbetegnelse

`Clean` var udviklingsnavnet for den nye arkitektur og skal ikke længere være det primære produktnavn i brugerfladen.

Eksisterende interne identifiers beholdes foreløbig for kompatibilitet og sikker migration, bl.a.:
- `clean/hangar18-manager/`;
- `H18_CLEAN_*`;
- `_h18_clean_layout_v1` og øvrige `_h18_clean_*` metadata;
- eksisterende action-/nonce-/CSS-/JS-identifiers;
- eksisterende releasefilnavne og repository-navn, indtil en særskilt kontrolleret migration godkendes.

De interne identifiers må ikke omdøbes mekanisk alene for kosmetikkens skyld, da det kan bryde updater, eksisterende layouts, historik, preview, metadata eller integrationer.

En intern teknisk rename kan vurderes omkring 1.0.0 eller som en særskilt migrationsopgave med backwards compatibility.

## Modulprincip

Den generiske kerne må ikke hardcode Hangar18 som nødvendig runtime-forudsætning.

Eksempel:

```text
VISUAL DESIGNER MANAGER
├── Core
│   ├── Visual Designer
│   ├── Global Design
│   ├── Header/Footer
│   ├── Components
│   ├── Backup / Export / Import
│   └── Updates / Diagnostics
│
└── Site modules
    ├── Vehicles (valgfri)
    ├── Events (valgfri)
    ├── Gallery data (valgfri)
    └── øvrige site-specifikke moduler
```

## Dokumentationsregel

Fra 0.1.22 skal nye eller opdaterede brugerrettede dokumenter anvende **Visual Designer** / **Visual Designer Manager** som primære navne.

Historiske dokumenter og filnavne med `Hangar18` eller `Clean` må bevares, når de fungerer som tekniske/historiske referencer, men de skal ved næste relevante revision forklare, at Hangar18 er site/projekt og Clean er intern generationsbetegnelse.

## Kildehierarki

Hvis navngivning er uklar, er denne fil autoritativ for produktnavnet. Den tekniske arkitektur er fortsat beskrevet i `CLEAN-DESIGN-MANUAL.md`, den operative plan i `docs/clean-backlog-v0120.md`, og projektstatus/overdragelse i `docs/CLEAN-HANDOVER.md`.
