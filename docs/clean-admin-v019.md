# Hangar18 Manager Clean 0.1.9 – admin-kontrakt

Status: implementeret 25. august 2026.

## Formål

Clean får igen ét samlet WordPress-adminområde som den gamle Manager, men adminlaget må ikke aktivere eller afhænge af 0.9.x/Ultimate Designer-runtime.

## Menustruktur

Topniveau: **Hangar18 Manager**.

Undermenuer:

1. Dashboard
2. Designer
3. Køretøjer
4. Køretøjsfelter
5. Events
6. Billedgalleri
7. Data
8. Sider
9. Menu
10. Header / Footer
11. Backup
12. Opdateringer
13. Log

Designer bruger fortsat `h18-clean-editor` og den eksisterende canonical Clean editor. Den tidligere separate top-level Designer-menu fjernes kun fra WordPress-navigationen; editorens Save/Restore/runtime ændres ikke af adminflytningen.

## Dashboard

Viser antal WordPress-sider, sider med Clean-state, samlet antal canonical nodes og antal gemte Clean-versioner. Hurtige genveje fører til Designer, Sider, Backup, Log, Opdateringer og Menu.

## Sider og indholdsoversigter

Sider viser side-ID, slug, Clean-version, nodeantal, seneste gemning samt links til Clean Designer, WordPress-editor og offentlig side.

Køretøjer, Events og Billedgalleri bruger eksisterende WordPress-hovedsider og undersider som read/manage-indgang. Der importeres eller aktiveres ingen gammel register-runtime.

Køretøjsfelter og custom Data har egne adminindgange, men den gamle dynamiske felt/data-runtime er bevidst ikke porteret implicit. De skal senere implementeres som selvstændige Clean-moduler.

## Menu og Header/Footer

Menu viser klassiske WordPress-menuer og registrerede theme locations og linker til WordPress' egen menu-editor.

Header/Footer viser aktivt tema og holder global shell adskilt fra sideversionerne. En fremtidig global Clean design-editor skal bo her og ikke i den enkelte sides canonical model.

## Backup

Fuld Clean-backup eksporterer JSON med:

- pluginversion, schema, units og rowPx,
- side-ID, titel og slug,
- aktuel Clean-version,
- canonical model,
- versionshistorik og digests.

Diagnostics, support-token, nonces og credentials eksporteres ikke.

## Log

Admin kan vælge en WordPress-side, se op til de seneste diagnostics, åbne sidens read-only support-link og rydde diagnostics for den valgte side. DiagnosticStore redakterer fortsat content, tokens, nonces, credentials og tilsvarende følsomme felter.

## Opdateringer

Clean bruger fortsat `clean-update.json`. Update-download valideres mod manifestets SHA-256 før installation.

## Arkitekturregel

Admin er et separat lag oven på Clean-modellen. DOM er ikke Save-kilde, og adminfunktioner må ikke omgå `LayoutModel`, versionshistorik eller `DiagnosticStore`.
