# Hangar18 Manager — canonical backlog delta v0.8.82

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.82 publiceret som korrigeret testkandidat  
**Release commit:** `a906fd4a8497d41e6afe3f83826a316899b306ee`  
**Package SHA-256:** `68a629eab9e115b6c24c16b985e7933e511c5b9e62fc7285747719e4fa1941aa`  
**Package:** `dist/hangar18-manager.zip` · 839.916 bytes  
**Manifest:** schema `1.0`, channel `test`, version `0.8.82`  
**Verified build run:** `32712612412` · SUCCESS  
**Extends:** `docs/active-backlog-v0881.md`

Denne fil er den aktuelle canonical backlog. Den arver hele roadmapet via v0.8.81 og overskriver kun punkter ændret efter de nye Inspector/canvas/preview/updater-regressioner blev identificeret.

## Batchstatus

Denne delta indeholder **13 nye/ændrede backlog-ID’er**: fem Inspector/canvas/preview-punkter, updater-button-fix og syv release-pipeline-punkter. De frosne `LEGO-SELECTION-075`, `LEGO-INSIDE-075` og `LEGO-REPAINT-062` ændres ikke. Vehicle/Event/Gallery frontend er uden for denne batch. Public cutover er fortsat ikke autoriseret.

# H. LEGO Inspector / canvas

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| INSPECTOR-DESIGN-081 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | `Luft, baggrund og placering` skal være læsbart i den smalle Inspector uanset browserbredde. Desktop og Mobil ligger lodret, felter er én kolonne og inputs må ikke udvide Inspector. Source-formular, canvas-data og frontend må ikke ændres. Source commit: `84cbc40884e9cf164c21fcf2064e670214732c96`. |
| LEGO-CANVAS-082 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | Et valgt top-level tekst/billede-element må ikke vise både en ydre source-row ramme og en indre elementramme. Editorens source-row er strukturel og skal være visuelt transparent; den faktiske `.h18-canvas-preview` ejer selection/design-kanten. Elementets synlige størrelse skal derfor følge den designede indholdsboks. Source commit: `d0355c7cc33281e96721ed4612fec1e264523883`. |
| INSPECTOR-IMAGE-083 | Normal | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | For `image` og `text_image` flyttes billedvælgeren foran overskrift/tekst i Inspector uden schemaændring. Rent `image` viser labels `Overskrift over billede (valgfri)` og `Billedtekst (valgfri)`. MediaId/URL/Title/Content gemmes i de eksisterende felter. Selection-owner ændres ikke. Source commit: `3863a22d2a88698e6f562f5b9517c8f289b92137`. |

# P. Preview fidelity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PREVIEW-FIDELITY-084 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | `Forhåndsvis side` må ikke klone/sanitere admin-canvas. Den viser i stedet den rigtige senest gemte WordPress-side i iframe, så header, frontend CSS, typografi, kanter, elementbredder og responsive layout kommer fra samme publicerede renderer som siden selv. Desktop/Tablet/Mobil ændrer kun iframe-viewport. Preview er read-only. |
| PREVIEW-LIVE-085 | Normal | ⬜ ÅBEN | Byg senere live preview af **ugemte** editorværdier gennem canonical frontend-normalisering/renderer uden canvas-DOM-kloning eller write-sideeffekt. |

# C. Updater

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| UPDATER-BUTTON-082 | Kritisk | ✅ ROOT CAUSE RETTET I v0.8.82 / BOOTSTRAP FRA 0.8.80 KRÆVER ÉNGANGS-UNLOCK | `updater-support-v0879.js` må ikke eje enabled/disabled-state for install-formen. PHP `render_updates()` er eneste autoritet: den renderer kun install-formen ved nyere kompatibel version. Root cause var strict JS-check `cfg.updateAvailable === true`, mens WordPress localization kunne levere scalar state som tekst (`"1"`), så en gyldig opdatering blev disabled. Den korrigerede v0.8.82-pakke indeholder ikke denne JS-disable-owner. Source commit: `93f14bee6a05181ae228001217b3f45a62f283fb`. |

# Y. Release-pipeline

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| RELEASE-010 | Høj | ✅ IMPLEMENTERET v0.8.82 | Separat fallback test-release workflow kan køre som PR-build med observerbare jobs/logs/artifacts. |
| RELEASE-011 | Kritisk | ✅ IMPLEMENTERET v0.8.82 | Release-ZIP oprettes altid fra nul; eksisterende `dist/hangar18-manager.zip` slettes før `zip`, så fjernede filer ikke overlever som stale entries. |
| RELEASE-012 | Høj | ✅ IMPLEMENTERET v0.8.82 | Verificeret PR-build kan efter package-contract PASS publicere ZIP, manifest og release-time source til `main`. |
| RELEASE-013 | Høj | ✅ IMPLEMENTERET | Normal `build-plugin-release.yml` sletter nu eksisterende ZIP før build og bruger member-name denylist. |
| RELEASE-014 | Normal | ✅ IMPLEMENTERET | Fallback publisher accepterer kontrollerede `release-v*` PR-buildbranches i stedet for én hardcoded branch. |
| RELEASE-015 | Normal | ✅ IMPLEMENTERET | Fallback publisher bruger idempotent `git add` og må ikke fejle på pathspecs for shim-filer, der allerede er slettet. |

# Manuel v0.8.82 testmatrix

1. Fra installeret v0.8.80: oplås install-knappen én gang i browseren, fordi netop v0.8.80 indeholder den defekte JS-disable-owner. Backend nonce/version/compatibility/SHA-checks forbliver aktive.
2. Installer v0.8.82; updater skal validere schema `1.0` og package SHA `68a629eab9e115b6c24c16b985e7933e511c5b9e62fc7285747719e4fa1941aa`.
3. Efter installation: Tjek opdatering skal vise installeret=latest og NEJ; updater-support må ikke disable en server-renderet install-form via localized JS-state.
4. Åbn Design → `Luft, baggrund og placering`: ingen smalle side-by-side Desktop/Mobil-felter og ingen vandret overflow.
5. Vælg et top-level tekstelement: kun den faktiske tekstboks/preview har selection/design-kant.
6. Vælg et rent Billede-element: `Vælg billede` ligger før overskrift/billedtekst i Inspector.
7. Gem en tydelig designændring, åbn `Forhåndsvis side`: preview skal ligne den offentlige side og må ikke vise editor-/LEGO-/design-controls.
8. Skift preview mellem Desktop, Tablet og Mobil: samme publicerede side, kun viewportbredden ændres.
9. Regression: selection/drop/repaint-sporene markeres ikke PASS som følge af denne batch; deres eksisterende status bevares.
