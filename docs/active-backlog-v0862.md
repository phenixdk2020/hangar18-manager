# Hangar18 Manager — aktiv backlog v0.8.62

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.62**  
**Release commit:** `e82f5b048c22ad2c6473375e235401566f04cb6c`  
**Package SHA-256:** `b34e0715d28206087ef3f8a2e22a569a25897f32985c828947fadb73d7ba1e62`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. `active-backlog-v0840.md`, `active-backlog-v0841.md`, `active-backlog-v0842.md` og `active-backlog-v0861.md` er historiske snapshots.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO eksisterende element-placement | 🟡 FIX-KANDIDAT v0.8.62 | Manuel test: Tekst + Billede, flyt Venstre/Højre til samme Auto-kasse og test Over/Under i eksisterende Grid. |
| LEGO selection/repaint | 🟡 FIX-KANDIDAT v0.8.62 | Manuel test: klik mellem elementer, kontroller permanent rød ramme og ingen flerblink; gentag efter bredde/højde-resize. |
| GitHub updater | 🔴 REGRESSION | UPDATER-STATUS-001: installeret version = GitHub-version skal give `Opdatering tilgængelig: NEJ`. |
| WhatIf UI | ✅ Fjernet | Regressionstest ved senere editor/updater-ændringer. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-DROP-062 | Høj | 🟡 FIX-KANDIDAT | Ved drag af et eksisterende element mod et andet kunne LEGO-zonen miste autoriteten ved sortstop, så jQuery Sortable kun ændrede flad rækkefølge og elementerne skiftede plads. | Venstre/Højre mellem to eksisterende elementer samler dem deterministisk i samme Auto-kasse; eksisterende Auto-kasse genbruges; der oprettes højst én ny Auto-kasse; Over/Under i Grid bruger stack-modellen; almindelig fri reorder virker fortsat uden LEGO-zone. |
| LEGO-REPAINT-062 | Høj | 🟡 FIX-KANDIDAT | Selection og resize kunne udløse gentagne komplette canvas-renders. En valid lodret stack blev desuden fejltalt som et manglende Grid-child og kunne starte seks reconcile-forsøg. | Klik mellem elementer giver ingen canvas-flerblink; rød selection-ramme bliver stående; en valid stack giver `expected == visual`; bredde/højde-resize har direkte preview og højst nødvendig afsluttende synkronisering. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Efter succesfuld opdatering kan updateren vise samme installerede og seneste GitHub-version, men stadig vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ; samme resultat efter opdatering, refresh og manuel GitHub-kontrol; backup/SHA/rollback uændret. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler fortsat. | Canonical browser-, screen-reader-, test2-, protected-domain- og rollback-evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Fortsæt først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## v0.8.62 — teknisk rettelse til manuel acceptance

### LEGO-DROP-062

- LEGO-zonen gemmes som eksplicit placement-intention under eksisterende Sortable-drag.
- Ved sortstop køres placement efter de gamle Sortable-handlere, så en valgt Venstre/Højre/Over/Under-zone ikke tabes til almindelig reorder.
- Venstre/Højre genbruger mål-elementets eksisterende Auto-kasse eller opretter én ny Auto-kasse for parret.
- Over/Under i et Grid bruger den eksisterende v0.8.51 stack-API.
- Hvis ingen LEGO-zone er valgt, griber v0.8.62 ikke ind i almindelig reorder.

### LEGO-REPAINT-062

- nesting-tools' gamle komplette refresh ved almindeligt valg af sektionsheader/Rediger kobles fra; selection er ikke en strukturel layoutændring.
- Nested Rediger bevarer delegation til den kanoniske række uden den efterfølgende unødige refresh.
- Parent-key guard tæller unikke kanoniske child-keys i både normale `.h18-v0811-auto-box` tiles og `.h18-v0851-stack-segment` segmenter.
- En sund 2-element lodret stack bliver derfor ikke længere fejltolket som `2 expected / 1 visual` og skal ikke udløse seks reconcile-renders.
- Den røde CSS-selection-ramme og den persistente selection-key fra v0.8.61 bevares.

## Manuel test v0.8.62

- [ ] Opret Tekst og derefter Billede som separate elementer.
- [ ] Træk Billede til Venstre/Højre på Tekst → begge ligger i samme Auto-kasse, ikke blot byttet i rækkefølgen.
- [ ] Træk igen mellem Venstre/Højre → samme Auto-kasse genbruges; ingen ekstra Auto-kasse.
- [ ] Test Over/Under mellem elementer i Auto-kassen → lodret stack i den valgte kolonne.
- [ ] Klik hurtigt mellem Tekst og Billede → ingen flerblink; rød ramme bliver stående på valgt element.
- [ ] Træk i kolonnebredde → direkte preview, ingen flerblink efter slip.
- [ ] Træk i højdefordeling → direkte preview, ingen serie af efterfølgende refreshes.
- [ ] Bekræft at fri reorder uden at ramme LEGO-zone stadig virker.
- [ ] Bekræft at Vehicle/Event/Gallery ikke er påvirket.

## Arbejdsregel

Updateren og LEGO-editoren behandles fortsat som separate fejlspor. UPDATER-STATUS-001 må ikke løses ved at ændre editor-runtime, og editor-fixes må ikke ændre updaterens version-state, backup, SHA-verifikation eller rollback-flow.
