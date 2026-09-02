# Visual Designer Manager v0.1.85 – Editor/live-paritet, Eventfaktabånd og typografi

Status: release candidate – samlet QA bestået før release

## Leverance

- Editor, forhåndsvisning og live bruger samme kanoniske ydre geometri for Sektion/Kasse.
- Sektion/Kasse med eksplicit grid-geometri kan ikke længere auto-udvide editorens ydre boks ud over den gemte `h × 8 px`-geometri; den indre redigeringsflade holdes inde i samme border-box.
- Parent-højde afstemmes fortsat ud fra reelle børn samt padding og border, før DOM-geometrien låses, så gyldigt indhold ikke klippes.
- Nyt Designer-element: Eventfaktabånd.
- Dato, Tid, Sted, Adresse og Kontakt i fem responsive accentkort.
- Separat typografi for labels og værdier i faktabåndet.
- Nye kanoniske Event-felter: Adresse og Kontakt.
- Adresse og Kontakt er registreret i ModuleRegistry og persisteres gennem ModuleRecord.
- Eventfelt: separat overskrifts- og brødteksttypografi.
- Eventfelt: valgfri overskrift selv ved tomt felt.
- Sikker migration af den kendte v0.1.80 Eventdetalje med layoutbackup.
- Row-index-fix i Eventfelter-admin, så checkbox-flags virker ved første gem.

## QA

Den samlede v0.1.85-gate omfatter PHP/JS-syntaks, editor/live-box-paritet, Eventfaktabånd og typografi, Event-persistence/semantik samt regression for editor/frontend-paritet, canvas auto-height, responsive layouts, komponérbare moduler, v0.1.81-funktioner og v0.1.84 portable transfer.
