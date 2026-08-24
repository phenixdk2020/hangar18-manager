# Hangar18 Manager — canonical backlog delta v0.8.82

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.80 installeret; v0.8.81 release-diagnostic fejlede før package; v0.8.82 source-delta under manuel QA  
**Extends:** `docs/active-backlog-v0881.md`

Denne fil er den aktuelle canonical backlog. Den arver hele roadmapet via v0.8.81 og overskriver kun punkter ændret efter de nye Inspector/canvas/preview-regressioner blev identificeret.

## Batchstatus

Denne delta tilføjer **5 backlog-ID’er**. De frosne `LEGO-SELECTION-075`, `LEGO-INSIDE-075` og `LEGO-REPAINT-062` ændres ikke. Vehicle/Event/Gallery frontend er uden for denne batch. Public cutover er fortsat ikke autoriseret.

# H. LEGO Inspector / canvas

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| INSPECTOR-DESIGN-081 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST | `Luft, baggrund og placering` skal være læsbart i den smalle Inspector uanset browserbredde. Desktop og Mobil ligger lodret, felter er én kolonne og inputs må ikke udvide Inspector. Source-formular, canvas-data og frontend må ikke ændres. Source commit: `84cbc40884e9cf164c21fcf2064e670214732c96`. |
| LEGO-CANVAS-082 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST | Et valgt top-level tekst/billede-element må ikke vise både en ydre source-row ramme og en indre elementramme. Editorens source-row er strukturel og skal være visuelt transparent; den faktiske `.h18-canvas-preview` ejer selection/design-kanten. Elementets synlige størrelse skal derfor følge den designede indholdsboks. Source commit: `d0355c7cc33281e96721ed4612fec1e264523883`. |
| INSPECTOR-IMAGE-083 | Normal | 🟡 FIX-KANDIDAT / MANUEL TEST | For `image` og `text_image` flyttes billedvælgeren foran overskrift/tekst i Inspector uden schemaændring. Rent `image` viser labels `Overskrift over billede (valgfri)` og `Billedtekst (valgfri)`. MediaId/URL/Title/Content gemmes i de eksisterende felter. Selection-owner ændres ikke. Source commit: `3863a22d2a88698e6f562f5b9517c8f289b92137`. |

# P. Preview fidelity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PREVIEW-FIDELITY-084 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST | `Forhåndsvis side` må ikke klone/sanitere admin-canvas. Den viser i stedet den rigtige senest gemte WordPress-side i iframe, så header, frontend CSS, typografi, kanter, elementbredder og responsive layout kommer fra samme publicerede renderer som siden selv. Desktop/Tablet/Mobil ændrer kun iframe-viewport. Preview er read-only. Source commits: `d2d88a8c91b64513bd14c30343e294f22c72abfb`, `d630599118ce02aa82e99d8f841669f0308cd451`, `2844abecb835cf45ca7aa8b8c48043c0b22a9dab`. |
| PREVIEW-LIVE-085 | Normal | ⬜ ÅBEN | Byg senere live preview af **ugemte** editorværdier gennem den canonical server-side frontend-normalisering/renderer og en read-only preview-kanal. Må ikke genindføre canvas-DOM-kloning og må ikke gemme post/option som sideeffekt. Indtil dette er implementeret, er PREVIEW-FIDELITY-084 eksplicit preview af senest gemte side. |

# Manuel v0.8.82 testmatrix

1. Åbn Design → `Luft, baggrund og placering`: ingen smalle side-by-side Desktop/Mobil-felter og ingen vandret overflow.
2. Vælg et top-level tekstelement: kun den faktiske tekstboks/preview har selection/design-kant; ingen ekstra stor ramme rundt om editor-rowen.
3. Vælg et rent Billede-element: `Vælg billede` ligger før overskrift/billedtekst i Inspector.
4. Gem en tydelig designændring, åbn `Forhåndsvis side`: preview skal ligne den offentlige side og må ikke vise editor-/LEGO-/design-controls.
5. Skift preview mellem Desktop, Tablet og Mobil: samme publicerede side, kun viewportbredden ændres.
6. Regression: selection/drop/repaint-sporene markeres ikke PASS som følge af denne batch; deres eksisterende status bevares.
