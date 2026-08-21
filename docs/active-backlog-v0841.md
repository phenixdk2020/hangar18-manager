# Hangar18 Manager — aktiv backlog v0.8.41

**Statusdato:** 21. august 2026  
**Aktuel officiel pluginbaseline:** **v0.8.41**  
**Officiel release package commit:** `1ccfa6b51a4fb1e716e565ba96e2f9d8cf0746ff`  
**Package SHA-256:** `000f01eb9c8ca25881c7b969057175882d25ef1b2eff1fcdef3fed725acae433`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den korte aktive styringsbacklog. `integration-backlog-after-ud120.md` bevares som den detaljerede historiske arkitektur-/implementeringslog.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO-editor runtime | ✅ Implementeret + automatiseret QA PASS | Manuel v0.8.41 A–L retest på `test2`. |
| Palette → Venstre/Højre | ✅ Rettet i v0.8.41 + browser-regression PASS | Genprøv præcis den manuelle v0.8.40-fejl først. |
| Officiel v0.8.41 release | ✅ Bygget + checksum-verificeret | Installer/bekræft v0.8.41 på `test2`. |
| LEGO manual acceptance | 🟡 PENDING | Brug `docs/lego-v0841-manual-acceptance.json`; ingen manuel PASS er registreret. |
| PAGE-DELETE-001 | 🟡 IMPLEMENTERING/QA | Sikker Slet side → WordPress Trash + safety backup + B1 restore + audit. |
| Dokumentation | 🟡 SYNC | Opdater manual/quick reference/retest-guide til v0.8.41 + sikker sidesletning. |
| I9 manual/live evidence | 🟡 PENDING | Brand browsers + screen reader + test2 editor/live E2E + protected domains + rollback. |
| I10 controlled conversion | 🔒 LÅST | Må først fortsætte efter fuldt I9 PASS. |
| Public page conversion | 🔒 LÅST | Ingen public mutation/cutover. |

## Resultat fra v0.8.40-manualtesten

Den første manuelle acceptance fandt en reel fejl: et nyt **Tekst**-element fra venstre palette kunne visuelt slippes i **Venstre**-zonen på **Tekst og billede**, men ende lodret over målelementet. Derfor er v0.8.40 ikke længere den aktive acceptance-kandidat.

Fejlen er rettet i v0.8.41 med en snæver HTML5 drop-target bridge, som kun retargeter drop-eventet til den eksisterende side-zone. Den eksisterende `nesting-tools`-motor ejer fortsat Auto-kasser, `LayoutParentKey`, rækkefølge og placement. Browser-regressionen dækker den præcise v0.8.40-reproduktion.

## Aktive backlogpunkter

| ID | Status | Leverance / definition of done |
|---|---|---|
| SIDEDROP-FIX-v0841 | ✅ QA PASS / manuel retest pending | Palette-element til Venstre/Højre skal bruge eksisterende Auto-kasser-motor og ende side-by-side. |
| PAGE-DELETE-001 | 🟡 Implementering/QA | Slet side-knap, capability + nonce, eksakt titelbekræftelse, safety backup før mutation, WordPress Trash, audit og B1 restore. |
| DOC-SYNC-v0841 | 🟡 Aktiv | Brugermanual, quick reference og retest-guide skal pege på v0.8.41. |
| MANUAL-ACCEPT-v0841 | 🟡 PENDING | A–L med konkret evidence; `overallStatus=PASS` må kun komme fra faktisk manuel test. |
| I9-EVIDENCE | 🟡 PENDING | Alle otte canonical manual/live gates med evidence. |
| I10-CUTOVER | 🔒 LÅST | Comparison → Hjem → Om → Kontakt → Bliv medlem → protected domains efter særskilt proof → legacy removal sidst. |

> **Nummernote:** ældre dokumentation brugte LEGO-041..043 til acceptance-værktøjer, mens den senere side-drop bugfix-PR også fik arbejdstitlen LEGO-041. For at undgå yderligere ID-kollision bruger den aktive backlog navnet `SIDEDROP-FIX-v0841` om bugfixen.

## Morgendagens manuelle rækkefølge

1. Installer/bekræft **Hangar18 Manager 0.8.41** på `test2`.
2. Etabler/identificér rollback-point.
3. Genprøv først den kendte v0.8.40-fejl: **Tekst og billede → træk nyt Tekst fra palette → Venstre**.
4. Hvis side-drop er korrekt, fortsæt A–L i `docs/ud-v0841-manual-retest.md`.
5. Registrér evidence i `docs/lego-v0841-manual-acceptance.json`; ingen scenario-PASS uden konkret evidence.
6. PAGE-DELETE-001 testes særskilt, når den QA-grønne build/release indeholder funktionen.

## A–L acceptance v0.8.41

- [ ] A — Elementbibliotek og drop, inkl. palette → Venstre/Højre regression
- [ ] B — Kasse og nesting
- [ ] C — Side-by-side / Auto-kasser
- [ ] D — Desktop resize
- [ ] E — Tablet/Mobil overrides + `Arv Desktop`
- [ ] F — Design og spacing
- [ ] G — Foldbare paneler
- [ ] H — Undo/Redo, ét logisk checkpoint pr. handling
- [ ] I — Save/reload persistence
- [ ] J — Preview Desktop/Tablet/Mobil
- [ ] K — Backup/restore
- [ ] L — Vehicle/Event/Gallery regression

### Kritiske stopregler

Stop og markér relevant test FAIL ved:

- PHP/WordPress fatal error eller kritisk console error;
- datatab eller dubletter;
- side-drop der visuelt viser Venstre/Højre men gemmer lodret placement;
- Undo/Redo der ændrer mere end den forventede logiske handling;
- save/reload der ikke reproducerer gemt state;
- regression i Vehicle/Event/Gallery.

## PAGE-DELETE-001 — sikkerhedsregler

Den nye funktion må kun flytte en almindelig side til **WordPress Papirkurv**. Den må aldrig permanent slette via `wp_delete_post`, direkte SQL eller rå database-sletning.

Før Trash skal der eksistere en B1-kompatibel safety backup. Serveren kræver både:

- `delete_pages`;
- objektspecifik `delete_post`-rettighed;
- nonce;
- den aktuelle sidetitel skrevet præcist.

`Hjem`, `Køretøjer og materiel`, `Events` og `Billedgalleri` er eksplicit låst mod denne funktion. Gendannelse sker via den eksisterende B1-restore-motor; der oprettes ikke en konkurrerende restore-stack.

## I9 — stadig krævet efter LEGO A–L

1. Chrome brand test.
2. Edge brand test.
3. Firefox brand test.
4. Safari brand test.
5. Screen-reader core flow.
6. Authenticated `test2` editor/live E2E.
7. Vehicle/Event/Gallery visual/function regression.
8. Migration/rollback rehearsal på live kopi.

A–L PASS kan levere evidence til I9, men kan ikke alene sætte I9 til PASS og kan ikke autorisere I10/public cutover.
