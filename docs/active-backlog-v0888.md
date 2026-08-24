# Hangar18 Manager — canonical backlog delta v0.8.88

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.87 source/release  
**Extends:** `docs/active-backlog-v0887.md`

Denne delta tilføjer en privat, server-side diagnosekanal til Ultimate Designer, så manuelle fejltests ikke længere er afhængige af download/copy af trace-bundles efter hver reproduktion.

# D. Live diagnostics

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| DIAG-LIVE-101 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.88 | Når Udvidet fejllogning er TIL, streamer browserens eksisterende Trace events i små batches til WordPress. Data gemmes privat i bounded, non-autoload options (maks. 20 sessioner / 3000 entries pr. session). Browser og server redigerer password/token/nonce/cookie/authorization/credential og rå UI-value/text/content. Gem-side registrerer en nonce-valideret `SERVER_BEFORE_SAVE` med `Key`, `Type`, `LayoutParentKey`, order, element-/billedstørrelser samt om span/stack-state var med i requesten. Client registrerer strukturelle snapshots ved page-load, preview og før Gem. En 256-bit tilfældig read-only support-URL under WP REST returnerer kun den sanitiserede seneste session med `no-store` og `noindex`. Trace support viser `Site-log klar` samt `Kopiér diagnose-link`. |

# Manuel v0.8.88 testmatrix

1. Slå **Udvidet fejllogning TIL** og åbn Sider-editoren.
2. Trace support skal vise **Site-log klar** og knappen **Kopiér diagnose-link**.
3. Start en Trace-test, flyt/resize mindst tre elementer og åbn Forhåndsvis side.
4. Åbn den kopierede diagnose-URL i en privat browserfane. Den skal returnere JSON med session, metadata og events, men ingen nonce/token/password/cookie eller rå tekstindhold.
5. Lav Række- og kolonne-kasse → 2×Tekst + 1×Billede, og tryk Gem. Diagnose-URLen skal efterfølgende indeholde både `DIAG_CLIENT_BEFORE_SAVE` og `SERVER_BEFORE_SAVE` for samme session.
6. `SERVER_BEFORE_SAVE.detail.sections` skal vise elementernes `key`, `type`, `parentKey`, order og sizing-felter uden Title/Content-værdier.
7. Efter reload skal en `DIAG_CLIENT_RELOAD_SNAPSHOT` være til stede, så før/efter-hierarkiet kan sammenlignes direkte.
8. Stop Trace. Normal editoradfærd, højre/venstre/over/under, Billede-insert, preview og Gem må ikke være afhængige af at diagnose-streaming lykkes.
9. Regression: v0.8.87 image-fit og lodret resize skal være uændret.

# Fortsat åbent

- `SAVE-RELOAD-HIERARCHY-098` skal herefter diagnosticeres med den nye live-log i stedet for manuelle bundle-exports.
- Direkte GitHub-sync er ikke standard i v0.8.88, fordi det kræver en write-credential på WordPress. Site-endpointet er read-only og token-beskyttet. GitHub-arkiv kan tilføjes senere som opt-in server-side sink.
