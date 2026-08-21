# Hangar18 Manager — aktiv backlog v0.8.42

**Statusdato:** 21. august 2026  
**Aktuel officiel pluginbaseline:** **v0.8.42**  
**Officiel release package commit:** `55625c67f61d78bc83a2546acac77a08e7879b09`  
**Package SHA-256:** `6c57740f1a3fda1348850bdede7d0303bee523da58aeec91d58d27be482b39e8`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den korte canonical aktive backlog. Ældre `active-backlog-v0840.md` og `active-backlog-v0841.md` er historiske snapshots. `integration-backlog-after-ud120.md` er den detaljerede arkitektur-/implementeringshistorik.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO-editor runtime | ✅ Implementeret + automatiseret QA PASS | Manuel v0.8.42 A–L acceptance på `test2`. |
| Palette → Venstre/Højre | ✅ Rettet siden v0.8.41 + browser-regression PASS | Genprøv den oprindelige v0.8.40-fejl først. |
| PAGE-DELETE-001 | ✅ Implementeret + QA PASS + frigivet i v0.8.42 | Manuel UI/restore-sanity på en midlertidig side. |
| Officiel v0.8.42 release | ✅ Bygget + checksum-verificeret | Installer/bekræft v0.8.42 på `test2`. |
| LEGO manual acceptance | 🟡 PENDING | Brug `docs/lego-v0842-manual-acceptance.json`; ingen manuel PASS registreret. |
| Dokumentation | ✅ v0.8.42 testpakke opdateret | Brug retest- og page-delete-manualerne. |
| I9 manual/live evidence | 🟡 PENDING | Brand browsers + screen reader + test2 editor/live E2E + protected domains + rollback. |
| I10 controlled conversion | 🔒 LÅST | Må først fortsætte efter fuldt I9 PASS. |
| Public page conversion | 🔒 LÅST | Ingen public mutation/cutover. |

## Hvad blev afsluttet inden næste manuelle session

### Side-drop-fix

Den manuelle v0.8.40-session fandt, at et palette-element visuelt kunne ramme Venstre/Højre-zonen men stadig ende lodret. Rettelsen kom i v0.8.41 og er med i v0.8.42. Den ændrer ikke placement-authority: eksisterende `nesting-tools`, Auto-kasser og `LayoutParentKey` er fortsat ejere.

### PAGE-DELETE-001

PAGE-DELETE-001 er merged og frigivet i v0.8.42:

- tydelig **Slet side** på almindelige sider;
- `delete_pages` + objektspecifik `delete_post` + nonce;
- eksakt titelbekræftelse + afsluttende bekræftelse;
- B1-kompatibel safety backup **før** Trash;
- WordPress `wp_trash_post`, ikke permanent/raw delete;
- audit med tid, side-ID/slug/titel, tidligere status, bruger og backup;
- eksisterende B1 restore genbruges;
- Hjem, Køretøjer og materiel, Events og Billedgalleri er låst.

Automatiseret PAGE-DELETE-test er PASS på PHP 8.0/8.2/8.3, inkl. fysisk backup og efterfølgende B1 restore. Det erstatter ikke den manuelle UI-sanity.

## Aktive backlogpunkter

| ID | Status | Definition of done |
|---|---|---|
| MANUAL-ACCEPT-v0842 | 🟡 PENDING | A–L gennemført med konkret evidence og deterministisk record. |
| PAGE-DELETE-MANUAL | 🟡 PENDING | Cancel/mismatch/success/Trash/B1 restore på midlertidig almindelig side. |
| I9-EVIDENCE | 🟡 PENDING | Alle otte canonical manual/live gates med evidence. |
| I10-CUTOVER | 🔒 LÅST | Comparison → Hjem → Om → Kontakt → Bliv medlem → protected domains efter særskilt proof → legacy removal sidst. |

**Der er pr. denne baseline ikke en kendt åben implementeringsbacklog, som må gennemføres før den manuelle acceptance uden at opfinde nyt scope.** Nye fejl fundet i acceptance bliver nye konkrete backlogpunkter.

## Morgendagens anbefalede rækkefølge

1. Installer/bekræft **Hangar18 Manager 0.8.42** på `test2`.
2. Bekræft rollback-point.
3. Genprøv først: **Tekst og billede → nyt Tekst fra palette → Venstre**.
4. Hvis korrekt: fortsæt A–L efter `docs/ud-v0842-manual-retest.md`.
5. Test PAGE-DELETE på en ny midlertidig almindelig side.
6. Registrér konkret evidence i `docs/lego-v0842-manual-acceptance.json`.
7. Ved fejl: stop relevant scenario, registrér FAIL/evidence og opret konkret backlogpunkt.
8. Ved A–L PASS: fortsæt de resterende I9 manual/live gates. A–L alene er ikke I9 PASS.

## A–L acceptance v0.8.42

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
- [ ] K — Backup/restore, inkl. PAGE-DELETE restore sanity
- [ ] L — Vehicle/Event/Gallery regression

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
