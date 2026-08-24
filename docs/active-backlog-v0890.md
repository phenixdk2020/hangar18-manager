# Hangar18 Manager — canonical backlog delta v0.8.90

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.89 generic Grid/Flex reload rebuild  
**Extends:** `docs/active-backlog-v0889.md`

Denne delta bygger på den rene v0.8.89-reproduktion, hvor alle gamle sektioner først blev slettet og siden gemt tom. Dermed er stale legacy-state udelukket som forklaring.

# S. Save/reload canvas parity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| SAVE-RELOAD-GRID-104 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.90 | En generisk `grid`/`flex` skal efter reload bygge en verificeret proxy fra de gemte `LayoutParentKey`-relationer. Source-rækker må først skjules EFTER proxyen faktisk er indsat i parent-preview. CSS må matche attribut-kontrakten uanset parent-key-værdi. Renderer må ikke eje `dragstart`, `dragover`, `drop` eller `dragend`. Den skal eksponere `proxyCount`, `hiddenSourceCount`, parent/root keys og effektive spans til Trace som `DIAG_LAYOUT_REBUILD_V0890`. |
| SIDE-SPAN-PERSIST-105 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.90 | Når en generisk Grid/Flex-komposition har mindst to root-kolonner og ALLE root-kolonner stadig har Desktop `Span=0`, materialiseres den allerede viste implicitte ligedeling gennem den eksisterende v0.8.41 `writeStateForKey()`-API. To roots bliver 6/6, tre 4/4/4 osv. Eksisterende eksplicitte spans må aldrig overskrives. Canonicalisering skal være på plads før v0.8.41 genererer `h18_lego_layout_span` ved Gem. |

# Dokumenteret v0.8.89 clean-test evidence

1. Siden blev først gemt med alle tidligere sektioner markeret `remove=true`; næste reload havde `sectionCount=0`.
2. Derefter blev der oprettet præcis fire friske sektioner: én `grid`, to `text` og ét `image`.
3. Umiddelbart før Gem havde begge tekster og billedet samme `LayoutParentKey` = den nye grid-key.
4. Billedet havde `StackRootKey` = den højre tekst og `StackOrder=10`; vertical stack-state var altså korrekt.
5. `DIAG_CLIENT_GENERATED_SAVE_PAYLOAD_V0889` viste fire `h18_lego_layout_span` entries, men ALLE havde Desktop `Span=0`. Stack-payloaden bevarede billedets relation til højre tekst.
6. `SERVER_BEFORE_SAVE` bevarede alle tre child `parentKey`-værdier.
7. Efter reload bevarede canonical state fortsat parent/stack-relationerne, men de tre child source-rækker blev tegnet som separate fuldbredde rækker under grid-parenten.

# Ny konkret root cause i v0.8.89

v0.8.89 JavaScript skrev source-markøren som:

`data-h18-v0889-generic-child-source="<parent-key>"`

mens CSS kun skjulte:

`[data-h18-v0889-generic-child-source="1"]`

Kontrakten kunne derfor aldrig matche. v0.8.90 bruger i stedet en attribut-tilstedeværelsesselector og sætter først attributten efter en verificeret proxy-append. Dermed er fail-safe retningen korrekt: hvis rebuild fejler, forbliver canonical source-rækker synlige i stedet for at data ser ud til at forsvinde.

# Manuel v0.8.90 testmatrix

1. Start gerne igen på tom `testside-ny` og opret Række- og kolonne-kasse med to root-elementer samt et tredje element under højre root.
2. Før Gem skal to implicitte root-kolonner vise 6/12 + 6/12, medmindre brugeren selv har lavet eksplicit resize; i så fald bevares den eksplicitte fordeling.
3. Gem. `DIAG_CLIENT_GENERATED_SAVE_PAYLOAD_V0889.spanPayload` skal nu have ikke-nul Desktop spans for root-kolonnerne.
4. Efter reload skal kun parent-kassen være top-level synlig; child source-rækkerne må ikke ligge som fuldbredde rækker nedenunder.
5. Trace skal indeholde `DIAG_LAYOUT_REBUILD_V0890` med `ready=true`, `proxyCount>=1` og `hiddenSourceCount` svarende til de canonical børn i den generiske parent.
6. Et stack-member, fx Billede under højre Tekst, skal fortsat ligge i samme kolonne efter reload.
7. Klik på proxy-elementerne og verificér korrekt Inspector-selection.
8. Regression: eksisterende højre/venstre/over/under, image insert, almindelig Kasse og Auto-kasser må være uændrede.
