# WordPress Ultimate Designer — Design- og kravspecifikation v01.02.00

**Dato:** 19. august 2026  
**Implementeringsbaseline:** Hangar18 Manager **v0.8.6**  
**GitHub main:** `39d713e4f64cc0c1540f85d8f3bc686a3579820d`

Den formelle design-/kravspecifikation ligger i:

`docs/WordPress_Ultimate_Designer_Designspecifikation_v01.02.00.docx`

## Hvad v01.02.00 korrigerer/opdaterer

- dokumentkontrol, cover-version og footer er synkroniseret til v01.02.00;
- dato er opdateret til 19.08.2026;
- den tidligere 23.3-tekst, som sagde at ingen backlogopgaver var udført, er korrigeret;
- den faktiske implementeringsstatus gennem v0.8.6 er dokumenteret;
- I1–I8 er markeret som implementeret;
- I9 er markeret som teknisk færdig med manuel evidens udestående;
- I10 planner/shadow/acceptance/source-drift/signed preflight er dokumenteret som implementeret, mens public cutover fortsat er låst;
- Auto-kasser, visuelt Tabel-værktøj og sammenklappet Side Health er indarbejdet som designkrav;
- den fastlåste konverteringsrækkefølge og Vehicle/Event/Gallery-beskyttelsen er fastholdt;
- GitHub-baseline commit og v0.8.6 er registreret.

## Relaterede dokumenter

- `docs/ultimate-designer-implementation-status-v086.md` — kort, repo-læsbar statusliste.
- `docs/integration-backlog-after-ud120.md` — I1–I10 integrationsbacklog og aktuelle gates.
- `docs/architecture-migration.md` — migrationsprincipper og v0.8.6 cutover-preflight.
- `docs/architecture-legacy-domain-contract-v0530.md` — beskyttet Vehicle/Event/Gallery baseline.

## Vigtig status

Der findes fortsat **ingen public Activate/Cutover/Publish-handler** i I10-preflightfasen. Eksisterende sider konverteres først efter manual QA, shadow acceptance og dokumenteret rollback. Vehicle/Event/Gallery konverteres sidst.
