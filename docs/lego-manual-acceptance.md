# LEGO-034 — Manual acceptance test pack

Formål: give en fast, gentagelig manuel test af LEGO-editoren på staging/test2 uden public cutover.

Denne test må udføres på en shadow-/testside. Vehicle/Event/Gallery må ikke ændres som del af testen.

## Forudsætninger

- Installeret build svarer til den commit der testes.
- Testside er en almindelig side, ikke Vehicle/Event/Gallery.
- Browserens console er åben under testen.
- Der tages et screenshot før første ændring.
- Undo/Redo-historik starter fra en kendt state.

## Acceptance-scenarier

### A. Elementbibliotek og drop
1. Træk Tekst ind på tomt canvas.
2. Træk Billede under teksten.
3. Træk Knap over teksten.
4. Verificér at Over/Under-zonerne svarer til drop-resultatet.
PASS når rækkefølgen matcher valgt zone uden ekstra bruger-synlige wrappers.

### B. Kasse og nesting
1. Opret Kasse.
2. Træk Tekst og Billede ind.
3. Flyt Tekst ud og ind igen.
PASS når hierarchy er stabilt uden dubletter og canvas/navigator er enige.

### C. Side-by-side LEGO
1. Placer to almindelige elementer lodret.
2. Træk nederste til Højre for øverste.
3. Flyt højre element til Venstre.
4. Tilføj et tredje element i rækken.
PASS når eksisterende Auto-kasser/layoutmotor bruges og Venstre/Højre kan omarrangeres.

### D. Desktop resize
1. Start med to side-by-side elementer.
2. Verificér 6/6.
3. Resize til ca. 8/4.
4. Træk mod minimum.
PASS når total span bevares, minimum er 1 og der ikke kommer horisontal overflow.

### E. Tablet/Mobil overrides
1. Skift til Tablet og ændr span.
2. Gå tilbage til Desktop og verificér uændret Desktop.
3. Skift til Mobil og lav et andet override.
4. Brug `Arv Desktop` og verificér inheritance.
5. Slå arv fra igen og verificér bevaret snapshot hvor UI understøtter det.
PASS når device-state ikke overskriver hinanden og inheritance er reversibel.

### F. Design og spacing
For Tekst og Kasse: ændr farver, font, border/radius, X/Y padding/margin/gap og responsive inheritance.
PASS når canvas og Inspector/Direkte design viser samme canonical værdier.

### G. Foldbare paneler
1. Genindlæs editoren.
2. Verificér at `Billede` og `Direkte design · LEGO` starter minimeret.
3. Åbn/luk uafhængigt og genindlæs.
PASS når fold-state følger UX-reglen uden element-state/history-event.

### H. Undo/Redo
Test separat: almindeligt drop, side-drop, Desktop resize, responsive resize, design og spacing. For hver: udfør → Undo → Redo.
PASS når hver brugerhandling er ét logisk checkpoint.

### I. Save/reload persistence
Gem, hard reload, verificér hierarchy/order/spans/responsive/design/spacing. Lav én ny ændring, gem og reload igen.
PASS når state er identisk efter reload.

### J. Preview
Test ugemt preview og Desktop/Tablet/Mobil. Verificér at editor-chrome ikke vises og at preview ikke laver skjulte writes.

### K. Backup / restore
Gem baseline, lav LEGO-ændring, gem, gendan baseline via eksisterende B1/B2 på testsiden og verificér LEGO-state.

### L. Protected domains regression
Uden at redigere dem, verificér Vehicle, Event og Gallery.
PASS når specialiseret legacy-runtime og funktionalitet er uændret.

## Evidence pr. scenarie
Registrér A–L med status PASS/FAIL/BLOCKED, browser/version, device/viewport, build SHA, screenshot/video/reference og kort note.

## Stopregler
Stop og markér FAIL ved elementtab/dubletter, delvis Undo/Redo, tab af state efter save/reload, responsive writes til forkert device, protected-domain regression eller reproducerbar fatal/uncaught editorfejl.

## Acceptance
LEGO-034 er kun PASS når A–L er gennemført på den installerede staging-build og alle obligatoriske scenarier er PASS. Automatisk Playwright QA er støttebevis, ikke erstatning for manuel acceptance.
