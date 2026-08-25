# Hangar18 Manager v0.9.2 – Save/Restore Diagnostics

**Statusdato:** 25. august 2026  
**Extends:** `docs/active-backlog-v0901.md`

## Formål

v0.9.2 gør fejlretning af den nye 0.9.x-editor observerbar gennem hele persistence-kæden. Interaction-log fra resize, re-parenting, Undo og Redo er ikke nok alene: vi skal kunne afgøre præcis om en fejl opstår i browserens canonical state, i serverens Save-projektion, i den faktiske persistens, under Restore eller først ved efterfølgende reload.

Loglaget er **read/observe only**. Det må ikke ændre sektioner, parent/order, geometri, backupkilder, restore-beslutninger eller frontend-output.

## Status fra v0.9.1

### FRONTEND-PHYSICAL-PARITY-114 — IMPLEMENTERET / MANUEL QA
- `PhysicalCanvasFrontendRuntime` projicerer gemt 120-unit geometri til offentlig frontend.
- 12-column span-store er fortsat kompatibilitetsfallback for elementer uden fysisk geometry-state.
- Punktet kan først markeres PASS efter Save/Reload/Frontend-test på det nye rene subdomæne.

### DIAG-INTERACTION-115 — IMPLEMENTERET / MANUEL QA
- Der findes strukturelle events for resize begin/commit, re-parent begin/commit, Undo og Redo.
- Eventdata er keys, parent/order, geometri og historikdybde; rå tekstindhold og credentials logges ikke.

## Nye backlogpunkter

### SAVE-DIAG-116 — FIX-CANDIDATE
- `SERVER_SAVE_INTENT_V0902` gemmer strukturel før-tilstand: WordPress content-hash, seneste sideversion og canonical layout digest.
- `SERVER_SAVE_PROJECTED_V0902` kører efter v0.9.0 canonical projection og v0.9.1 geometry merge, men før legacy content-saver.
- Eventet verificerer de rigtige payload-kontrakter: `h18_lego_layout_span`, `h18_lego_stack_v0851` og `h18_layout_geometry_v0901`.
- Shutdown logger `SERVER_SAVE_RESULT_V0902`, så resultatet kan aflæses selv når WordPress redirecter/exit'er efter Save.
- Resultatet sammenligner version før/efter, WordPress hash og canonical layout digest.
- Fatal PHP-fejl logges kun som type, filnavn, linje og kort sanitiseret fejltekst.

### RESTORE-DIAG-117 — FIX-CANDIDATE
- Både **Erstat original** og **Restore som kopi** får `SERVER_RESTORE_BEGIN_V0902`.
- Restore-loggen gemmer mode, target-version, sikker strukturel før-tilstand og kun det sanitiserede backup-filnavn som audit-kontekst.
- Restore-controllerens mutation ændres ikke; debuglaget observerer requesten ved priority 1 og resultatet via shutdown.
- `wp_redirect` observeres kun for HTTP-status, restore-status, slug og beskedlængde; beskedens indhold kopieres ikke til loggen.
- `SERVER_RESTORE_RESULT_V0902` sammenligner originalens WordPress-hash og canonical layout digest før/efter og medtager fatal-state hvis relevant.

### SAVE-RESTORE-CORRELATION-118 — FIX-CANDIDATE
- Browseren logger `DIAG_CLIENT_SAVE_INTENT_V0902`, `DIAG_CLIENT_RESTORE_INTENT_V0902` og `DIAG_CLIENT_RESTORE_RETURN_V0902` med samme strukturelle SectionKey/parent/order/span/stack/geometry-model.
- Den aktuelle diagnostic session kopieres ind i Restore-formen, så klient- og serverevents ender i samme private site-log.
- Hvis session-felt mangler, serveren finder seneste diagnostics-session for samme bruger og side; Restore kan som sidste fallback starte en ny server-session.
- Restore-return correlation ligger i `sessionStorage` i højst 10 minutter og indeholder kun mode, version, slug og timestamp.

### IMAGE-PHYSICAL-BOX-119 — OPEN / NÆSTE FUNKTIONELLE BATCH
- Rent billede skal følge den fysiske elementkasses størrelse.
- Standard: behold billedets proportioner uden deformation.
- Valg: `Contain`, `Cover/beskær`, eller fri deformation hvor bredde/højde må afvige.
- `Cover` beskærer automatisk til kassens fysiske dimensioner og bruger focal X/Y som `object-position`.
- Editor og frontend skal bruge samme fit-regel og samme fysiske geometry-state.
- Resize af selve elementkassen må ikke oprette et konkurrerende legacy image-height resize-ansvar.

## Save/Restore eventkæde

Ved en normal Save forventes rækkefølgen:

1. `DIAG_CLIENT_SAVE_INTENT_V0902`
2. eksisterende `DIAG_CLIENT_BEFORE_SAVE`
3. eksisterende `SERVER_BEFORE_SAVE`
4. `SERVER_SAVE_INTENT_V0902`
5. v0.9.0 canonical projection
6. v0.9.1 geometry merge
7. `SERVER_SAVE_PROJECTED_V0902`
8. legacy Page Editor save + versionshistorik/backup
9. `SERVER_SAVE_RESULT_V0902` fra PHP shutdown
10. næste editor-load/reload diagnostics

Ved Restore forventes:

1. `DIAG_CLIENT_RESTORE_INTENT_V0902`
2. `SERVER_RESTORE_BEGIN_V0902`
3. eksisterende B1 restore/preflight service
4. redirect-status observeres uden at tage ejerskab
5. `SERVER_RESTORE_RESULT_V0902` fra shutdown
6. `DIAG_CLIENT_RESTORE_RETURN_V0902` efter redirect

## QA-gate

1. Lav én resize og én re-parent, derefter Save.
2. Verificér at Save-loggen har samme keys/parent/order/geometri i client intent, projected state og shutdown-resultat.
3. Verificér at ny sideversion øges præcis én gang.
4. Reload og kontrollér at canonical digest svarer til Save-resultatet.
5. Lav en ny ændring og Save igen.
6. Restore den foregående version med **Erstat original**.
7. Verificér `RESTORE_BEGIN` → restore-status success → `RESTORE_RESULT` → client return.
8. Kontrollér at originalens hash/layout ændres til forventet state og at sikkerhedsbackup fortsat oprettes af eksisterende restore-service.
9. Kør **Restore som kopi** og verificér at originalsiden ikke ændres.
10. Slå Trace/logging fra og verificér at debuglaget ikke påvirker Save/Restore-funktionalitet.
11. Kontrollér support-loggen for passwords, nonces, tokens, cookies og rå tekstindhold; ingen må forekomme.
12. Vehicle/Event/Gallery regressionskontrolleres og må være uændrede.

## Definition of Done

v0.9.2 kan markeres PASS når én komplet Save + reload + Restore-original + Restore-kopi kan følges deterministisk i samme diagnostic flow, uden at diagnosticlaget selv ændrer state. Dette bliver QA-infrastrukturen for de næste 0.9.x-batches, herunder billedets fysiske kasseadfærd.
