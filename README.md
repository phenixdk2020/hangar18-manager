# Hangar18 Manager

Webbaseret WordPress-administrationsværktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.

Repositoryet bruges som versionskilde for Hangar18 Managers indbyggede GitHub-updater.

Den aktuelle officielle testbaseline er **Hangar18 Manager v0.8.42**. Ultimate Designer/LEGO-editorens automatiserede QA er grøn; den manuelle test2/I9 acceptance er fortsat PENDING, og public I10 cutover er låst.

## Dokumentation

- [Aktiv backlog v0.8.42](docs/active-backlog-v0842.md) — canonical status og hvad der reelt mangler.
- [Manuel v0.8.42 testprocedure](docs/ud-v0842-manual-retest.md) — A–L, kendt side-drop regression og PAGE-DELETE sanity.
- [Slet side sikkert](docs/ud-page-delete-user-guide.md) — safety backup, WordPress Trash og B1 restore.
- [Ultimate Designer hurtig reference](docs/ultimate-designer-quick-reference.md) — daglig editor-huskeseddel.
- [Ultimate Designer brugermanual](docs/ultimate-designer-user-manual.md) — grundlæggende editorarkitektur og arbejdsgange.
- [Designmanual](DESIGN-MANUAL.md) — godkendte valg for farver, bredde, luft, kort og mobilvisning.

## Release / testgrænse

Automatiseret QA kan dokumentere kode- og browserregressioner, men kan ikke sætte de manuelle/live gates til PASS. Den aktive acceptance-record er `docs/lego-v0842-manual-acceptance.json`. I10/public konvertering må først fortsætte, når I9 er fuldt dokumenteret PASS.
