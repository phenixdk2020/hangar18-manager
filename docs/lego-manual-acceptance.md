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

1. Træk et Tekst-element ind på tomt canvas.
2. Træk et Billede-element under teksten.
3. Træk et Knap-element over teksten.
4. Verificér at Over/Under-zonerne svarer visuelt til drop-resultatet.
5. Gem ikke endnu.

PASS når rækkefølgen efter hvert drop matcher den valgte zone og ingen ekstra wrapper/element bliver synligt som brugerindhold.

### B. Kasse og nesting

1. Opret en Kasse.
2. Træk Tekst ind i Kassen.
3. Træk Billede ind i samme Kasse.
4. Flyt Tekst ud af Kassen igen.
5. Flyt Tekst tilbage ind.

PASS når parent/child-adfærd er stabil, der ikke opstår dubletter, og canvas/navigator viser samme hierarchy.

### C. Side-by-side LEGO

1. Placer to almindelige elementer lodret.
2. Træk det nederste element til Højre for det øverste.
3. Verificér at de står side om side.
4. Flyt højre element til Venstre.
5. Tilføj et tredje element i samme række.

PASS når Auto-kasser/layoutmotoren bruges uden manuel wrapper-oprettelse, og elementerne kan omarrangeres Venstre/Højre.

### D. Desktop resize

1. Start med to side-by-side elementer.
2. Verificér initialt 6/6-layout.
3. Træk grænsen til ca. 8/4.
4. Træk mod minimum på højre element.
5. Verificér at minimum span aldrig går under 1.

PASS når resize er visuelt stabil, total span for rækken bevares, og ingen horisontal overflow introduceres.

### E. Tablet/Mobil overrides

1. Skift til Tablet.
2. Ændr span-fordelingen.
3. Skift tilbage til Desktop og verificér at Desktop-layoutet er uændret.
4. Skift til Mobil og lav et andet override.
5. Aktivér `Arv Desktop` på Tablet/Mobil og verificér at visningen følger Desktop igen.
6. Slå arv fra igen og kontrollér at det tidligere responsive snapshot kan gendannes, hvor UI understøtter dette.

PASS når Desktop, Tablet og Mobil kan afvige uden at overskrive hinandens state, og inheritance er reversibel.

### F. Design og spacing

For mindst ét Tekst-element og én Kasse:

1. ændr tekstfarve og baggrund;
2. ændr font/typografi;
3. ændr border/radius;
4. ændr X/Y padding/margin/gap;
5. skift mellem Desktop/Tablet/Mobil og verificér responsive design/spacing inheritance.

PASS når canvas og Inspector/Direkte design viser samme canonical værdier.

### G. Foldbare paneler

1. Genindlæs editoren.
2. Verificér at `Billede` og `Direkte design · LEGO` starter minimeret.
3. Åbn begge.
4. Luk kun det ene.
5. Genindlæs og kontrollér browser-lokal fold-state efter den gældende UX-regel.

PASS når fold/udfold ikke ændrer element-state eller opretter Undo/Redo-checkpoints.

### H. Undo/Redo

Udfør separat og kontrollér ét logisk checkpoint for hver:

- almindeligt drop;
- side-by-side drop;
- resize af to naboer;
- responsive resize;
- designændring;
- spacingændring.

For hver handling: udfør → Undo → Redo.

PASS når hele handlingen gendannes samlet, uden delvis wrapper/parent/span-state.

### I. Save/reload persistence

1. Gem testsiden.
2. Genindlæs browseren helt.
3. Verificér hierarchy, rækkefølge, spans, responsive overrides, design og spacing.
4. Foretag én ny ændring, gem igen og genindlæs.

PASS når den gemte editor-state er identisk efter reload.

### J. Preview

1. Åbn ugemt preview med en ændring der endnu ikke er gemt.
2. Verificér at editor-chrome ikke vises i preview.
3. Test Desktop/Tablet/Mobil preview.
4. Luk preview uden save og kontrollér at editorens state stadig er intakt.

PASS når preview viser sideindhold, ikke editor-kontroller, og ikke laver skjulte writes.

### K. Backup / restore

1. Gem en kendt baseline.
2. Lav en synlig LEGO-ændring og gem.
3. Verificér at versions-/backupflow registrerer den nye state.
4. Gendan baseline med eksisterende B1/B2-flow på testsiden.
5. Verificér hierarchy, spans, spacing/design og responsive state efter restore.

PASS når restore giver den forventede tidligere LEGO-state uden påvirkning af andre sider.

### L. Protected domains regression

Uden at redigere dem, åbn/vis:

- Vehicle;
- Event;
- Gallery.

PASS når de fortsat bruger deres legacy/specialiserede runtime og ser/fungerer som før.

## Evidence pr. scenarie

Registrér for A–L:

- status: PASS / FAIL / BLOCKED;
- browser + version;
- device/viewport;
- build commit SHA;
- screenshot/video/reference;
- kort note ved afvigelser.

## Stopregler

Stop testen og markér FAIL hvis:

- et element forsvinder eller duplikeres ved drag/drop;
- Undo/Redo genskaber kun dele af en handling;
- save/reload mister hierarchy/span/design-state;
- Tablet/Mobil ændrer Desktop-state utilsigtet;
- Vehicle/Event/Gallery ændres;
- browser console viser reproducerbar fatal/uncaught editorfejl.

## Acceptance

LEGO-034 er kun PASS når A–L er gennemført på den installerede staging-build og alle obligatoriske scenarier er PASS. Automatisk Playwright QA er støttebevis, ikke erstatning for denne manuelle acceptance.
