# I9 Manual Evidence — Gate Index

Dette er operatorindgangen til de **otte faktiske I9 acceptance-gates**. Skabelonerne er støtte til test/evidence; de ændrer ikke manifest, WordPress eller cutover-state.

| Canonical gate | Skabelon | Krævet human/live bevis |
|---|---|---|
| `chrome` | `docs/i9-evidence-gate-chrome.md` | Google Chrome brand/editor flow |
| `edge` | `docs/i9-evidence-gate-edge.md` | Microsoft Edge brand/editor flow |
| `firefox` | `docs/i9-evidence-gate-firefox.md` | Firefox brand/editor flow |
| `safari` | `docs/i9-evidence-gate-safari.md` | Safari brand/editor flow |
| `screenReader` | `docs/i9-evidence-gate-screen-reader.md` | Reel screen-reader core-flow |
| `test2LiveE2E` | `docs/i9-evidence-gate-test2-live-e2e.md` | Authenticated editor/session på staging/test2 |
| `protectedDomains` | `docs/i9-evidence-gate-protected-domains.md` | Vehicle/Event/Gallery visual/function regression |
| `rollback` | `docs/i9-evidence-gate-rollback.md` | Kontrolleret rollback rehearsal på staging/live kopi |

## Anbefalet rækkefølge

1. Lås buildidentitet: commit SHA, pluginversion og target.
2. Opret/valider I9-manifestet.
3. Kør Chrome, Edge, Firefox og Safari.
4. Kør screen-reader core-flow.
5. Kør authenticated `test2LiveE2E` med registreret restore point.
6. Kør `protectedDomains` mod de fastlagte baselines.
7. Kør `rollback` rehearsal.
8. Registrer hver gate via stdout-only recorderen og valider manifestet efter hver ændring.
9. Kør integrity + readiness rapport.
10. Kør `--require-pass` først når alle otte gates har reelt evidence.

## Stopregler

- En `FAIL` skal behandles som fejl, ikke omdøbes til `BLOCKED` for at komme videre.
- `BLOCKED` bruges kun når testen reelt ikke kan gennemføres endnu.
- `PASS` kræver konkret evidence-reference.
- Automated Playwright/PHP QA kan støtte en gate, men erstatter ikke de krævede brand-/human-/live-tests.
- `readyForI10=true` er kun en readiness-indikator; I10-mutations/cutover-koden forbliver separat låst.
- Ingen eksisterende public side konverteres som led i I9 evidence-indsamlingen.
