# Visual Designer Manager 0.1.38 – status

Dato: 28. august 2026

## Scope
- VD-TEXT-SEL-001 / BUG-02 cold-start only.
- Ingen Billede-rettelse i denne release.

## Observation fra 0.1.37
Bruger-QA i både Firefox/Chrome viste tidligere samme grundfejl, og 0.1.37 forbedrede adfærden: de første 2–3 forsøg kunne fortsat miste selection, mens formattering derefter blev stabil i samme editor-session.

## Fix
- selection-sessionen pre-armes ved afsluttet markering (`mouseup`/`keyup`);
- boundary-markører installeres før brugeren går til toolbaren;
- toolbar pointerdown bruger eksisterende marker-session og initialiserer kun som fallback;
- v0125 forbliver eneste autoritative selection-ejer;
- v0131/v0132 legacy restore-loops forbliver deaktiveret via versionsuafhængig delegation.

## Acceptance
Cold start efter frisk reload: første klik på Fed, Kursiv og Understregning skal bevare samme selection. Derefter 20/20 gentagelser og chaining. Minimum Firefox + Chrome før lukning af BUG-02.
