# Hangar18 Manager — canonical backlog delta v0.8.91

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.90 generic Grid/Flex reload rebuild  
**Extends:** `docs/active-backlog-v0890.md`

Denne delta isolerer en kritisk Gem-regression, dokumenteret af live-diagnostikken på `testside-ny`: et korrekt gemt layout kan være intakt umiddelbart efter reload, men ved næste Gem kan alle eksisterende sektioner blive markeret som fjernet på klienten, før serverens save-normalisering modtager dataene.

# S. Save integrity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| SAVE-INTEGRITY-106 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.91 | Gem må aldrig forvandle et layout, der havde aktive sektioner ved brugerens Gem-aktivering, til `activeCount=0`/alle `Remove=1` under samme submit-transaktion. En pre-submit guard skal snapshotte aktive rækker ved pointer/keyboard Save-aktivering og må KUN intervenere ved den dokumenterede katastrofe-signatur: snapshot havde mindst én aktiv række, submit-capture har nul aktive rækker, og de samme rækker findes stadig i DOM. Ved recovery gendannes kun de rækker, der var aktive ved Gem-aktiveringen, deres `Remove=0` og deres snapshot-tagne `LayoutParentKey`. Bevidst slettede rækker må ikke genoplives. Ingen drag/drop-events eller placement-state må overtages. Trace skal registrere `DIAG_SAVE_GUARD_CAPTURE_V0891` og ved intervention `DIAG_SAVE_GUARD_RECOVER_V0891`. |

# Dokumenteret v0.8.90 evidence

1. En tidligere Gem omkring 18:44 lokal tid sendte fire sektioner korrekt: én grid-parent, to text-children og ét image-child. Alle tre børn havde samme `LayoutParentKey` som grid-parenten, og serveren modtog `remove=false`.
2. Efter en senere reload var de samme fire rækker fortsat aktive, og resize/stack-runtime kunne læse deres canonical state.
3. Ved den reproducerede fejl omkring 19:34 lokal tid viste submit-capture stadig fire legacy-rækker i DOM, men den genererede save-payload havde `sectionCount=0`, `spanPayload=[]` og `stackPayload=[]`.
4. Serverens efterfølgende `SERVER_BEFORE_SAVE` modtog de fire poster som `remove=true` med tomme parent-relationer. Fejlen er derfor opstået klient-side før server-normalisering.
5. v0.8.90 generic saved-layout rebuild rapporterede samtidig `ready=false`, `proxyCount=0` og `hiddenSourceCount=0`; rebuild-rendereren var dermed ikke aktiv ejer af den destruktive overgang.
6. `admin.js` har en legitim Fjern-handler, som toggler `.h18-page-section-removed` og skriver `Remove=1/0`. v0.8.91 ændrer ikke den handler; guard-laget beskytter kun selve Gem-transaktionen mod den observerede all-removed overgang.

# v0.8.91 teknisk kontrakt

- `assets/ultimate-designer-save-integrity-guard-v0891.js` må ikke registrere `dragstart`, `dragover`, `drop` eller `dragend`.
- Snapshot tages ved faktisk Save-aktivering, ikke ved page load, så brugerens seneste reordering/parent-ændringer bevares.
- `window` capture-phase på `submit` kører før formens normale capture/serialization.
- Recovery må kun ske, hvis alle aktive snapshot-rækker fortsat findes i DOM, men submit-state viser nul aktive rækker.
- Recovery gendanner kun remove-state og `LayoutParentKey`; span/stack-felter ejes fortsat af de eksisterende v0.8.41/v0.8.51 runtimes.
- Hvis brugeren selv har slettet alle rækker før Gem, er snapshot `activeCount=0`, og guard-laget må ikke gøre noget.

# Manuel v0.8.91 testmatrix

1. Åbn et allerede gemt layout med én Række- og kolonne-kasse, to Tekst-elementer og ét Billede-element i kassen.
2. Kontrollér før Gem, at alle fire rækker er aktive og at de tre børn peger på grid-parentens key.
3. Klik Gem uden at ændre layoutet. Siden må efter reload stadig have fire sektioner med samme parent-hierarki.
4. Gentag Gem mindst tre gange uden ændringer. Ingen Gem må give `sectionCount=0` eller `remove=true` på de fire aktive sektioner.
5. Hvis den gamle regression forsøger at opstå, skal Trace vise `DIAG_SAVE_GUARD_RECOVER_V0891` med `recovered=true`, `intentActiveCount=4` og efterfølgende aktivt layout.
6. Slet bevidst ét child-element og Gem. Det slettede element må forblive slettet; guard må ikke genoplive det.
7. Slet bevidst alle sektioner og Gem. Tom side skal fortsat kunne gemmes; guard må ikke intervenere.
8. Regression: højre/venstre/over/under, stack, resize, almindelig Kasse og Auto-kasser må være uændrede.
