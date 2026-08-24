# Hangar18 Manager — canonical backlog delta v0.8.84

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.83 installeret og manuelt testet  
**Extends:** `docs/active-backlog-v0883.md`

Denne delta registrerer regressionen i v0.8.83 placement-sikkerhedslaget samt den præciserede Inspector-rækkefølge. v0.8.84 skal bevare den eksisterende `INSPECTOR-IMAGE-086`, `TRACE-SAFETY-088` og `TRACE-UI-087` leverance fra v0.8.83-kæden uden at redefinere deres backlog-ID’er.

## Manuel evidens fra v0.8.83

- Rent `Billede` fryser **ikke længere** editorens JavaScript-tråd: **PASS**.
- Den tidligere fungerende placement-kontrakt `højre / venstre / over / under` virker ikke længere efter v0.8.83: **REGRESSION**.
- Før image-fixet virkede `Tekst → tekst til højre → tekst under`: **PASS**.
- Konklusion: image-freeze-fix og placement-motor skal være isolerede; den nye generelle drag-cleanup/watchdog må ikke eje drop-afslutning.

# H. LEGO Inspector

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| INSPECTOR-ORDER-090 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.84 | Inspectorens avancerede hale er fast: almindelige/type-specifikke felter først; når elementet har medie, placeres hele **Billede/Mediebibliotek**-modulet umiddelbart før de avancerede sektioner; **Dynamic data binding** er næstsidst og **Conditions / synlighed** er altid sidst. Dynamic data binding og Conditions / synlighed er foldet sammen som standard på hver ny Inspector-render og kan åbnes med klik/Enter/Space. Rækkefølge-runtime skal være idempotent og må ikke skabe MutationObserver-loop. |

# P. Placement regression

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| PLACEMENT-ROLLBACK-089 | Kritisk | 🟡 ROLLBACK-KANDIDAT / MANUEL TEST v0.8.84 | Fjern v0.8.83 runtime-sikkerhedens dragstart/dragover/drop/dragend listeners, watchdog, syntetiske dragend og overlay-cleanup. Den dokumenteret fungerende v0.8.82-kæde `v0838/v0843/v0851/v0862` skal igen være eneste placement-authority for højre/venstre/over/under/inside. Image- og trace-sikkerhed må ikke ændre placement-state. |

# Videreførte v0.8.83 gates

- `INSPECTOR-IMAGE-086`: image-freeze skal fortsat være løst uden placement ownership.
- `TRACE-SAFETY-088`: trace må ikke selvforstærke editorbelastning.
- `TRACE-UI-087`: trace Start/Stop-panelet skal forblive synligt over viewportens bund.

# Manuel v0.8.84 testmatrix

1. `Tekst → tekst til højre`: højre-placement skal virke.
2. Flyt/indsæt tilsvarende til **venstre**, **over** og **under**: alle fire zoner skal virke som før v0.8.83.
3. `Tekst → Billede til højre`: placement virker, editor fryser ikke, og efterfølgende klik/drag virker.
4. `To tekster side om side → Billede under den ene`: placement virker og editor fryser ikke.
5. Vælg et Billede-element og kontrollér Inspector-halen: **Billede/Mediebibliotek → Dynamic data binding → Conditions / synlighed**.
6. Kontrollér at **Dynamic data binding** og **Conditions / synlighed** begge er foldet ind som standard; åbn/luk begge og verificér at felterne fortsat fungerer.
7. Vælg et element uden medie: Dynamic data binding skal være næstsidst og Conditions / synlighed sidst.
8. Gentag placement med trace både TIL og FRA; resultatet skal være identisk.
