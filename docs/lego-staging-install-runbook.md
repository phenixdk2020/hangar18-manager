# LEGO-036 — Staging installation og rollback

Formål: installere en konkret LEGO staging-build på test2, gennemføre manuel acceptance og kunne rulle sikkert tilbage uden at gøre builden til officiel release.

## Før installation

1. Bekræft at målmiljøet er staging/test2 og ikke production.
2. Notér aktuel pluginversion og tag screenshot af Plugins-siden.
3. Tag eksisterende B2/site-backup efter gældende runbook.
4. Hent artifact fra `LEGO Staging Test Build`.
5. Verificér `SHA256SUMS.txt` mod `hangar18-manager-lego-staging.zip`.
6. Åbn artifactets `TEST-BUILD.txt` og notér commit-SHA og pluginversion i `docs/lego-test-session-template.md` eller en kopi heraf.
7. Bekræft at `lego-staging-manifest.json` har:
   - `officialRelease=false`;
   - `publicCutoverAuthorized=false`;
   - samme commit-SHA som `TEST-BUILD.txt`.

## Installation på test2

1. Sørg for at ingen anden editor-session gemmer samtidig.
2. Installer/erstat Hangar18 Manager med staging-ZIP'en via den eksisterende sikre plugin-opdateringsmetode på test2.
3. Genindlæs wp-admin.
4. Bekræft at plugin stadig er aktivt.
5. Hvis filadgang er tilgængelig, verificér `wp-content/plugins/hangar18-manager/TEST-BUILD.txt` og sammenhold commit-SHA med artifactet.
6. Tøm relevante browser-/sidecaches uden at ændre WordPress-indhold.
7. Åbn en almindelig testsides editor og verificér at editoren indlæses uden fatal/uncaught fejl.

## Smoke før fuld LEGO-test

Før A–L acceptance køres, verificér:

- Elementbibliotek vises;
- canvas vises;
- Inspector vises;
- `Billede` og `Direkte design · LEGO` starter minimeret;
- eksisterende testsides indhold er intakt;
- Vehicle/Event/Gallery kan åbnes uden ændret runtime.

Ved fejl stoppes testen og rollback udføres før yderligere redigering.

## Manuel LEGO acceptance

Kør `docs/lego-manual-acceptance.md` og registrér resultater i `docs/lego-test-session-template.md` eller en kopi med build-SHA/evidence.

## Rollback

Rollback udføres hvis:

- wp-admin/editor ikke kan indlæses;
- der opstår reproducerbart datatab/dubletter;
- save/reload mister LEGO-state;
- Undo/Redo korrumperer hierarchy;
- Vehicle/Event/Gallery regresserer;
- en kritisk PHP/JS-fejl blokerer testen.

### Plugin rollback

1. Stop redigering og gem ikke yderligere ændringer.
2. Geninstaller den tidligere kendte gode officielle/plugin-ZIP på test2.
3. Bekræft at staging-fil `TEST-BUILD.txt` ikke længere findes i den installerede pluginmappe.
4. Genindlæs wp-admin og verificér den tidligere pluginversion.

### Data rollback

Hvis staging-testen nåede at gemme ændringer på testsiden:

1. brug eksisterende B1/B2 restore på den berørte testsides baseline;
2. verificér hierarchy, design, spacing og public preview;
3. verificér Vehicle/Event/Gallery igen read-only.

## Efter rollback eller afsluttet test

Registrér:

- staging commit-SHA;
- installeret pluginversion;
- artifact SHA-256;
- start/slut-tid;
- om plugin rollback blev udført;
- om data restore blev udført;
- slutstatus PASS/FAIL/BLOCKED;
- links/referencer til screenshots/logs.

## Sikkerhedsgrænse

Staging-builden er kun til LEGO/manual acceptance. Den er ikke en officiel release, giver ikke public cutover-autorisation og ændrer ikke I9/I10-status automatisk.
