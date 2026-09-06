# Visual Designer Manager V3 — 3.0.0-alpha.15

## Scope

Alpha.15 er en målrettet **V1 Mobile Page Flow Parity**-rettelse.

Alpha.13 viste, at det ikke er nok at kopiere V1's `geometry.mobile`: V3 fortsatte bagefter med at fortolke mobilgeometrien som et 120-kolonne grid. Den fungerende V1-side gør noget andet på telefon: indholdet går over i naturligt én-kolonne flow, brede sektioner fylder skærmen, sammensatte kolonner stables, og mobile mellemrum/padding er mindre.

Alpha.15 retter derfor selve mobil-flowsemantikken i V3 i stedet for at lave endnu en målebaseret JavaScript-workaround.

## Ændringer

- Konverterede V1-sider skifter på `<=782px` fra 120-kolonne sidegrid til naturligt vertikalt flow.
- Header og Footer er ikke en del af denne ændring og beholder deres separate responsive template-geometri.
- Direkte sideelementer bliver fuld bredde og sorteres deterministisk efter deres gemte mobile `y`, derefter `x` og til sidst `order`.
- Desktop-offset/transform og grid-koordinater kan ikke længere skubbe mobilindhold sidelæns eller lade to kolonner blive stående.
- Store geometriske tomrum reduceres til højst 24 px mellem normale mobile elementer.
- Sektion/container-padding begrænses på mobil til højst 18 px vandret og 38 px lodret, svarende til V1's fungerende mobilprincip.
- Eventfaktabånd, eventoversigter og gallerier bliver én kolonne på telefon.
- Galleri-detailbilleder bruger V1's 4:3-proportion, mens oversigtskort bruger 16:10.
- Den fungerende Alpha.14 hamburger/dropdown-menu bevares uændret.
- Der genindføres ikke Alpha.10/11's DOM-måling eller reflow-JavaScript, og gemte V3-data omskrives ikke.

## Test4 acceptance

Versionen er først visuelt godkendt, når følgende på test4 matcher V1-princippet:

1. almindeligt sideindhold fylder mobilbredden uden falske to-kolonne layouts;
2. tekst/billede-sektioner ligger i korrekt top-til-bund rækkefølge;
3. "Om foreningen" er én læsbar kolonne uden overdreven luft;
4. Events/kalender følger én-kolonne mobilrækkefølge;
5. Billedgalleri bruger mobilbredden uden store side-/sektionsgab;
6. Alpha.14-menuen fungerer fortsat.

Grøn automatiseret QA er en release-gate, men test4 er fortsat den visuelle acceptance-gate.
