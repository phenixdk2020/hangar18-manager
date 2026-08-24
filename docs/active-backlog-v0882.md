# Hangar18 Manager — canonical backlog delta v0.8.82

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.82 publiceret som testkandidat  
**Release commit:** `ae88bd5e6370642025f06c72acd9130fb5bbc549`  
**Package SHA-256:** `cde6e0543507e96dd98ef53b64c69131c54b90635d5c8cfa42d57112bae83eee`  
**Package:** `dist/hangar18-manager.zip` · 839.902 bytes  
**Manifest:** schema `1.0`, channel `test`, version `0.8.82`  
**Verified build run:** `32708415315` · SUCCESS  
**Extends:** `docs/active-backlog-v0881.md`

Denne fil er den aktuelle canonical backlog. Den arver hele roadmapet via v0.8.81 og overskriver kun punkter ændret efter de nye Inspector/canvas/preview-regressioner blev identificeret.

## Batchstatus

Denne delta indeholder **9 nye/ændrede backlog-ID’er**: fem Inspector/canvas/preview-punkter og fire release-pipeline-punkter. De frosne `LEGO-SELECTION-075`, `LEGO-INSIDE-075` og `LEGO-REPAINT-062` ændres ikke. Vehicle/Event/Gallery frontend er uden for denne batch. Public cutover er fortsat ikke autoriseret.

v0.8.82 blev bygget gennem en isoleret PR-artifact-kørsel, fordi connector-baserede push-events ikke startede den normale push-workflow pålideligt. Buildet gennemførte source cleanup, updater-hardening, PHP/JS lint, versionsopdatering, frisk ZIP-build, SHA-256-kontrol, schema-1.0-kontrol og shim-denylist før den verificerede pakke blev publiceret til `main`.

# H. LEGO Inspector / canvas

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| INSPECTOR-DESIGN-081 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | `Luft, baggrund og placering` skal være læsbart i den smalle Inspector uanset browserbredde. Desktop og Mobil ligger lodret, felter er én kolonne og inputs må ikke udvide Inspector. Source-formular, canvas-data og frontend må ikke ændres. Source commit: `84cbc40884e9cf164c21fcf2064e670214732c96`. |
| LEGO-CANVAS-082 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | Et valgt top-level tekst/billede-element må ikke vise både en ydre source-row ramme og en indre elementramme. Editorens source-row er strukturel og skal være visuelt transparent; den faktiske `.h18-canvas-preview` ejer selection/design-kanten. Elementets synlige størrelse skal derfor følge den designede indholdsboks. Source commit: `d0355c7cc33281e96721ed4612fec1e264523883`. |
| INSPECTOR-IMAGE-083 | Normal | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | For `image` og `text_image` flyttes billedvælgeren foran overskrift/tekst i Inspector uden schemaændring. Rent `image` viser labels `Overskrift over billede (valgfri)` og `Billedtekst (valgfri)`. MediaId/URL/Title/Content gemmes i de eksisterende felter. Selection-owner ændres ikke. Source commit: `3863a22d2a88698e6f562f5b9517c8f289b92137`. |

# P. Preview fidelity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PREVIEW-FIDELITY-084 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.82 | `Forhåndsvis side` må ikke klone/sanitere admin-canvas. Den viser i stedet den rigtige senest gemte WordPress-side i iframe, så header, frontend CSS, typografi, kanter, elementbredder og responsive layout kommer fra samme publicerede renderer som siden selv. Desktop/Tablet/Mobil ændrer kun iframe-viewport. Preview er read-only. Source commits: `d2d88a8c91b64513bd14c30343e294f22c72abfb`, `d630599118ce02aa82e99d8f841669f0308cd451`, `2844abecb835cf45ca7aa8b8c48043c0b22a9dab`. |
| PREVIEW-LIVE-085 | Normal | ⬜ ÅBEN | Byg senere live preview af **ugemte** editorværdier gennem den canonical server-side frontend-normalisering/renderer og en read-only preview-kanal. Må ikke genindføre canvas-DOM-kloning og må ikke gemme post/option som sideeffekt. Indtil dette er implementeret, er PREVIEW-FIDELITY-084 eksplicit preview af senest gemte side. |

# Y. Release-pipeline

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| RELEASE-010 | Høj | ✅ IMPLEMENTERET v0.8.82 | Separat fallback test-release workflow kan køre som PR-build, så workflow-run, jobs, logs og verificeret binary artifact kan observeres direkte. Forkerte v0.8.82 asset-navne i den første fallback blev erstattet af de faktiske Inspector/Preview/Navigator assets. |
| RELEASE-011 | Kritisk | ✅ ROOT CAUSE RETTET I FALLBACK v0.8.82 | Release-ZIP skal altid oprettes fra nul. Før `zip` køres slettes eksisterende `dist/hangar18-manager.zip`, så fjernede filer ikke overlever som stale ZIP-entries. Denne fejl var årsag til den falske `NoWhatIf shim leaked into ZIP` efter source-filerne faktisk var slettet. |
| RELEASE-012 | Høj | ✅ IMPLEMENTERET v0.8.82 | En verificeret same-repo PR-build må efter fuld package-contract PASS publicere præcis ZIP, `update.json` og release-time rensede sourcefiler til `main`. v0.8.82 blev publiceret med denne sti; midlertidig PR #157 blev lukket uden merge efter publicering. |
| RELEASE-013 | Høj | ⬜ ÅBEN | Overfør RELEASE-011-reglen til den normale `.github/workflows/build-plugin-release.yml`: `dist/hangar18-manager.zip` skal slettes før hver normal build. Tilføj regression-check, så en fjernet fil ikke kan overleve fra en tidligere ZIP. Fallback-workflowet er allerede korrekt. |

# Manuel v0.8.82 testmatrix

1. Opdater fra v0.8.80 til v0.8.82 via Hangar18 Manager → Opdateringer; updater skal vise schema 1.0 og validere SHA `cde6e0543507e96dd98ef53b64c69131c54b90635d5c8cfa42d57112bae83eee`.
2. Åbn Design → `Luft, baggrund og placering`: ingen smalle side-by-side Desktop/Mobil-felter og ingen vandret overflow.
3. Vælg et top-level tekstelement: kun den faktiske tekstboks/preview har selection/design-kant; ingen ekstra stor ramme rundt om editor-rowen.
4. Vælg et rent Billede-element: `Vælg billede` ligger før overskrift/billedtekst i Inspector.
5. Gem en tydelig designændring, åbn `Forhåndsvis side`: preview skal ligne den offentlige side og må ikke vise editor-/LEGO-/design-controls.
6. Skift preview mellem Desktop, Tablet og Mobil: samme publicerede side, kun viewportbredden ændres.
7. Regression: selection/drop/repaint-sporene markeres ikke PASS som følge af denne batch; deres eksisterende status bevares.
