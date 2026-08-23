# Hangar18 Manager — aktiv backlog v0.8.61

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.61**  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. `active-backlog-v0840.md`, `active-backlog-v0841.md` og `active-backlog-v0842.md` er historiske snapshots.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO-editor / 2D Kasse-layout | 🟡 MANUEL TEST | Fortsæt manuel test af selection, klik, bredde/højde-resize og Under/Over på v0.8.61. |
| GitHub updater | 🔴 REGRESSION | Ret statusberegning så installeret version = GitHub-version altid giver `Opdatering tilgængelig: NEJ`. |
| WhatIf UI | ✅ Fjernet fra normal Hangar18-admin | Regressionstest ved senere updater/editor-ændringer. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Efter succesfuld opdatering til v0.8.61 viser updateren både `Installeret version: 0.8.61` og `Seneste GitHub-version: 0.8.61`, men feltet `Opdatering tilgængelig` står stadig til `JA`. | Når installeret version og manifestversion er identiske, skal status være `NEJ`; ingen opdateringshandling må tilbydes; manuel `Kontrollér GitHub nu`, refresh og nyligt gennemført opdatering skal give samme deterministiske resultat. |
| LEGO-SELECTION-061 | Høj | 🟡 MANUEL TEST | Selection/klik og resize har haft blink/rerender-regressioner gennem v0.8.58–0.8.61. | Valgt element beholder synlig rød ramme; klik mellem elementer giver ingen flerblink; bredde- og højderesize giver direkte preview og højst én nødvendig afsluttende synkronisering; Under/Over forbliver fungerende. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler fortsat. | Canonical browser-, screen-reader-, test2-, protected-domain- og rollback-evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Fortsæt først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## UPDATER-STATUS-001 — manuel evidence 2026-08-23

Observeret på WordPress-siden **Opdateringer** efter installation af v0.8.61:

- `Installeret version`: **0.8.61**
- `Seneste GitHub-version`: **0.8.61**
- `Opdatering tilgængelig`: **JA** — forkert
- GitHub adgangstilstand: `PUBLIC`

Det er en ren status-/state-reconciliation-fejl. Den skal behandles separat fra LEGO-editoren, så updater-fix ikke igen ændrer editor-runtime.

### Acceptkriterier

1. `installed < latest` → `Opdatering tilgængelig: JA`.
2. `installed == latest` → `Opdatering tilgængelig: NEJ`.
3. `installed > latest` → `Opdatering tilgængelig: NEJ` og eventuelt informativ downgrade-status, men aldrig almindelig update-knap.
4. Efter succesfuld pluginopdatering skal installeret version genlæses fra aktiv plugin-kode og sammenholdes med den senest hentede manifestversion.
5. Cache/transient må ikke efterlade `JA` fra den tidligere version efter opdatering.
6. Manuel `Kontrollér GitHub nu`, page refresh og automatisk check skal vise samme resultat.
7. Backup, SHA-256-verifikation, kodebackup og automatisk rollback må ikke ændres af dette fix.

## Arbejdsregel

Updateren og LEGO-editoren behandles som to separate fejlspor. Der må ikke lægges updater-fixes ind i editorens selection/drag/drop/runtime-kode, og editor-fixes må ikke ændre updaterens version-state eller backup/rollback-flow.
