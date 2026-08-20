# v0.8.16 Undo/Redo all-paths hotfix

## Problem fundet ved re-audit af v0.8.15

v0.8.15 starter restore-transactionen fra toolbar Undo/Redo og Ctrl/Cmd+Z. Den samme interne history restore kan imidlertid også kaldes fra kommandopaletten og lokal kladde-gendannelse. Disse veje var ikke dækket af capture-phase guard'en.

Desuden blev alle history-captures i den korte restore-settle-periode droppet. Det beskytter mod syntetiske Kasse/runtime-events, men kan også skjule en ægte brugerændring, hvis brugeren redigerer eller starter et drag umiddelbart efter Undo.

## Hotfix

- genbruger den eksisterende `window.__h18HistoryTransactionV0814` — der oprettes ikke en anden history stack;
- starter samme restore-transaction for toolbar, keyboard, kommandopalet og lokal kladde-restore;
- bruger `Event.isTrusted` til at skelne ægte browserinput fra programmatisk `.trigger('input/change')` under restore-settle;
- ægte input/change og kendte strukturhandlinger (drag handles, palette, delete/duplicate osv.) kan derfor igen oprette et nyt history-trin straks efter Undo;
- syntetiske restore-events forbliver undertrykt;
- ingen side-save, option/meta-write, menuændring, frontend hook eller public cutover tilføjes.

## QA

- eksisterende v0.8.15 Kasse/Undo kontrakt er udvidet med alle restore-entry-points og trusted-edit checks;
- ny Playwright spec tester toolbar/kommandopalet/keyboard/lokal kladde, syntetisk input versus ægte input og hurtig drag-handle-interaktion;
- browserpakken køres fortsat i Chromium, Firefox og WebKit.
