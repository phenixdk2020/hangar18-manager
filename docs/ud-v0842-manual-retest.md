# Ultimate Designer v0.8.42 — manuel test på test2

**Status:** PENDING — testprocedure, ikke PASS-evidence.  
**Kandidat:** Hangar18 Manager **v0.8.42**  
**Release commit:** `55625c67f61d78bc83a2546acac77a08e7879b09`  
**Package SHA-256:** `6c57740f1a3fda1348850bdede7d0303bee523da58aeec91d58d27be482b39e8`  
**Target:** `https://test2.hangar18.dk`

## 1. Preflight

- Bekræft i WordPress, at **Hangar18 Manager 0.8.42** er installeret og aktiv.
- Bekræft at testen foregår på `test2`, ikke production.
- Tag eller identificér rollback-point før første permanent gem/write-test.
- Notér browser, OS og Desktop/Tablet/Mobil-viewports.
- Brug `docs/lego-v0842-manual-acceptance.json` som canonical record.

## 2. Første test — den tidligere v0.8.40-fejl

1. Opret/brug en almindelig testside.
2. Indsæt **Tekst og billede**.
3. Tag et nyt **Tekst** fra venstre **Elementer/Funktioner**.
4. Træk det ind i den synlige **Venstre**-dropzone på `Tekst og billede`.
5. Slip.

**PASS:**

- `Tekst` står til venstre for `Tekst og billede`;
- begge ligger i samme Auto-kasser-layout;
- de må ikke ende lodret;
- ingen dublet/console fatal;
- ét Undo gendanner hele side-drop-handlingen.

Ved fejl: stop og registrér FAIL/evidence; fortsæt ikke som om den kendte regression er løst.

## 3. A–L

### A — Elementbibliotek og drop

- Indsæt mindst Tekst, Billede og Kasse.
- Test Over/Under og Venstre/Højre.
- Visuel dropzone skal matche faktisk placement.
- Ingen dubletter.

### B — Kasse og nesting

- Drop element Into Kasse.
- Tilføj flere børn.
- Flyt barn ud igen.
- Parent/child skal overleve save/reload.

### C — Side-by-side / Auto-kasser

- To elementer side-by-side, normalt cirka 6/6.
- Tilføj evt. tredje barn.
- Test venstre/højre rækkefølge.
- Auto-kasser må være layoutmekanisme, ikke manuel wrapper-administration.

### D — Desktop resize

- Resize mellem naboer, fx 6/6 → 8/4.
- Minimum span = 1.
- Nabospans kompenserer inden for 12 kolonner.
- Ét pointerforløb = ét Undo-trin.

### E — Tablet/Mobil + Arv Desktop

- Lav Tablet-override og kontrollér at Desktop er uændret.
- `Arv Desktop` til → Desktop-værdi vises.
- `Arv Desktop` fra → tidligere override-snapshot vender tilbage.
- Gentag sanity på Mobil.

### F — Design og spacing

På almindeligt element og Kasse:

- tekst/baggrund;
- border/radius;
- X/Y spacing;
- responsive designoverride;
- Direkte Design og Inspector skal afspejle samme state.

### G — Foldbare paneler

- Fold Direkte Design, Billede og relevante rails ind/ud.
- Foldestatus må ikke ændre page-data eller history.

### H — Undo/Redo

Test mindst:

- side-drop;
- resize;
- design/spacing;
- indholdsændring.

Én logisk handling skal være ét forventet history-trin.

### I — Save/reload persistence

- Lav kendt nesting + side-by-side + spans + design.
- Gem permanent version med ændringsnote.
- Reload.
- Placement, parent, spans, responsive overrides og indhold skal være identiske.

### J — Preview

- Desktop, Tablet og Mobil.
- Ingen horisontal overflow.
- Ingen editor-chrome i preview.
- Preview må ikke udføre public cutover.

### K — Backup/restore + PAGE-DELETE sanity

Først almindelig B1/B2 sanity. Derefter på en **ny midlertidig almindelig side**:

1. Klik **Slet side** → Cancel: ingen mutation.
2. Forkert titel: ingen mutation.
3. Korrekt titel → sidste Cancel: ingen mutation.
4. Korrekt titel + bekræft: siden skal flyttes til WordPress Papirkurv.
5. Success notice skal oplyse safety-backup.
6. Gendan via eksisterende **B1 · Gendan sidebackup**.
7. Bekræft titel, status, content og Page Editor-state.

**Må ikke testes destruktivt på:** Hjem, Køretøjer og materiel, Events eller Billedgalleri. De skal være låst mod PAGE-DELETE-001.

### L — Vehicle/Event/Gallery

Read-only regression:

- Køretøjer og materiel fungerer som før.
- Events fungerer som før.
- Billedgalleri fungerer som før.
- Ingen generel LEGO-konvertering/public renderer har overtaget domænerne.

## 4. Evidence-regel

Et scenarie må kun sættes `PASS`, når der er konkret evidence, fx screenshot, kort timestamped observation, browserlog eller backup/recovery-reference.

Critical flags bruges ved:

- console/fatal error;
- datatab/dubletter;
- protected-domain regression.

`overallStatus=PASS` for A–L er kun LEGO acceptance. Det er ikke samlet I9 PASS og autoriserer ikke I10/public cutover.

## 5. Efter A–L

Hvis alle A–L er PASS med evidence, fortsæt de resterende I9 manual/live gates. I10 forbliver låst, indtil samtlige canonical I9 gates er PASS.
