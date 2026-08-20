# v0.8.17 Undo/Redo restore-latch hotfix

## Fejl reproduceret fra manuel v0.8.16-test

Efter en brugerændring kunne Undo kort gå fra historiktrin 4 til 3 og derefter straks tilbage til 4. Samtidig kunne Inspector/Direkte design blive genåbnet på et element, som ikke var en del af den handling, der blev fortrudt.

## Root cause

v0.8.16 markerer ægte brugerinput som history-eligible i et kort trusted-vindue. Hvis Undo/Redo startes mens dette vindue stadig er aktivt, kunne `guard.isSuppressed()` returnere false, selv om restore-transaktionen netop havde kaldt `suppress()`. Dermed kunne syntetiske restore/preview-events blive registreret som et nyt historiktrin.

Base-editorens history snapshot gemmer desuden `selectedKey` og genvælger dette element under restore. Selection/Inspector er UI-state og bør ikke skifte til et historisk element som bivirkning af en indholds-Undo.

## Hotfix

- Undo/Redo starter en eksplicit restore-latch, som nulstiller trusted-state fra handlingen før Undo.
- Restore-latch har højere prioritet end det tidligere trusted-vindue.
- Latch frigives først ved en ny ægte brugerændring eller kendt strukturhandling; syntetiske events kan derfor ikke genoprette trin 4 efter Undo.
- Ctrl/Cmd+Z og Ctrl/Cmd+Shift+Z går gennem samme latch som toolbar og kommandopalet.
- Det aktuelt valgte element huskes før Undo/Redo og genvælges efter restore, hvis elementet stadig findes. Dermed ændrer Undo ikke Inspector til et uvedkommende historisk element.
- Lokal kladde-restore bruger latch mod syntetiske captures, men bevarer sin egen draft-selection-adfærd.
- Der oprettes fortsat ingen ekstra history stack.

## QA-krav

Browser-QA skal specifikt dække:

1. rigtig brugerændring → Undo inden for trusted-vinduet → restore er stadig suppressed;
2. syntetiske input/change-events efter restore må ikke frigive latch;
3. ny rigtig brugerændring efter Undo frigiver latch og er history-eligible;
4. Ctrl/Cmd+Z bruger samme latch;
5. selection før Undo bevares efter at base-restore midlertidigt har valgt et andet historisk element;
6. eksisterende Kasse/Auto-kasser og protected Vehicle/Event/Gallery-kontrakter forbliver grønne.
