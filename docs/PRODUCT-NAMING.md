# Hangar18 Visual Designer – navnestandard

**Statusdato:** 25. august 2026  
**Status:** Godkendt navnestandard fra og med planlagt release 0.1.22

## Officielle synlige navne

### Hangar18 Visual Designer
Navnet på selve den visuelle Designer, hvor sider, Header og Footer bygges med elementer, grid, responsive layouts og Inspector.

Eksempler på UI-tekst:
- `Hangar18 Visual Designer`
- `Åbn Visual Designer`
- `Visual Designer · Desktop / Laptop / Mobil`

### Hangar18 Visual Designer Manager
Navnet på hele WordPress-administrationspakken/pluginet omkring Visual Designer.

Visual Designer Manager omfatter på sigt bl.a.:
- Visual Designer;
- Globalt design;
- Header/Footer;
- Køretøjer og køretøjsfelter;
- Events og datostyring;
- Galleri/album;
- Sider og navigation;
- Komponenter/presets;
- Backup/rollback;
- Opdateringer;
- Diagnose/log.

## Versionsnavn

Synlige versionsreferencer skal fremover skrives som fx:

`Hangar18 Visual Designer Manager 0.1.22`

Når konteksten kun handler om editoren, kan der stå:

`Hangar18 Visual Designer 0.1.22`

## Clean er kun intern teknisk generationsbetegnelse

`Clean` var udviklingsnavnet for den nye arkitektur og skal ikke længere være det primære produktnavn i brugerfladen.

Eksisterende interne identifiers beholdes foreløbig for kompatibilitet og sikker migration, bl.a.:
- `clean/hangar18-manager/`;
- `H18_CLEAN_*`;
- `_h18_clean_layout_v1` og øvrige `_h18_clean_*` metadata;
- eksisterende action-/nonce-/CSS-/JS-identifiers;
- eksisterende releasefilnavne, indtil en særskilt kontrolleret migrering godkendes.

De interne identifiers må ikke omdøbes mekanisk alene for kosmetikkens skyld, da det kan bryde updater, eksisterende layouts, historik, preview, metadata eller integrationer.

En intern teknisk rename kan vurderes omkring 1.0.0 eller som en særskilt migrationsopgave med backwards compatibility.

## Dokumentationsregel

Fra 0.1.22 skal nye eller opdaterede brugerrettede dokumenter anvende **Hangar18 Visual Designer** / **Hangar18 Visual Designer Manager** som primære navne.

Historiske dokumenter og filnavne med `Clean` må bevares, når de fungerer som tekniske referencer, men de skal ved næste relevante revision forklare, at `Clean` er den interne generationsbetegnelse.

## Kildehierarki

Hvis navngivning er uklar, er denne fil autoritativ for produktnavnet. Den tekniske arkitektur er fortsat beskrevet i `CLEAN-DESIGN-MANUAL.md`, den operative plan i `docs/clean-backlog-v0120.md`, og projektstatus/overdragelse i `docs/CLEAN-HANDOVER.md`.
