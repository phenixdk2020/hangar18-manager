# Hangar18 Manager Clean 0.1.8 – celle/grid-kontrakt

Status: godkendt designregel, 25. august 2026.

## Formål

0.1.8 erstatter 0.1.7-reglen om, at `Over` og `Under` altid opretter en fuldbredde-række. Layoutet behandles i stedet som fysiske celler i den eksisterende canonical 120-unit / 8-px geometri.

Der indføres ikke en separat DOM-baseret layoutkilde. `geometry.desktop.x/y/w/h`, `parentId` og `order` forbliver canonical state.

## Fysisk celle

En celle beskrives af:

- `x` – startkolonne i 120-unit grid.
- `w` – bredde i 120-unit grid.
- `y` – startposition i 8-px rækker.
- `h` – højde i 8-px rækker.

Når en gammel node med `h=0` første gang indgår i en fysisk split-operation, materialiseres dens aktuelle visuelle højde til et eksplicit antal 8-px rækker. Dette gør row-span deterministisk uden at migrere gamle layouts unødigt.

## Drop på almindeligt element

### Venstre / Højre

Drop deler kun målelementets eksisterende celle vandret.

Eksempel: en 60-unit celle deles i 30/30. Andre celler uden for målcellen beholder deres geometri.

### Over / Under

Drop deler kun målelementets eksisterende celle lodret.

Hvis målcellen ligger ved siden af en anden celle i samme visuelle bånd, materialiseres båndets fælles højde først. Den anden celle beholder hele højden og fungerer dermed som fysisk row-span over begge nye under-rækker.

Eksempel:

```text
┌───────────────┬───────────────┐
│    Billede    │               │
├───────────────┤     Tekst     │
│     Tekst     │               │
└───────────────┴───────────────┘
```

Den højre Tekst-celle har samme samlede `h` som de to venstre celler tilsammen.

## Drop på Kasse/Sektion

Kasse og Sektion har fortsat fem zoner:

- Over
- Under
- Venstre
- Højre
- Ind i Kassen

Centerzonen ændrer `parentId` og lægger elementet ind i parenten. Kantzonerne splitter parentens egen celle i forhold til dens siblings; de betyder ikke `Ind i`.

## Fjern/flyt fra celle

Editoren må ikke længere omfordele en hel række automatisk, fordi det kan ødelægge row-span-layouts. Ved flytning forsøges kun en lokal, sikker heal:

- præcis én direkte vandret nabo med samme højde kan udvides ind i den ledige celle, eller
- præcis én direkte lodret nabo med samme bredde kan udvides ind i den ledige celle.

Hvis layoutet er tvetydigt, efterlades geometrien uændret i stedet for at gætte.

## Rendering

Editor og frontend bruger den samme canonical geometri.

Når `h > 0` renderes elementet med:

- `grid-column: x+1 / span w`
- `grid-row: y+1 / span h`
- grid auto-row = 8 px

Gamle `h=0`-elementer beholder kompatibilitetsadfærd, indtil de indgår i en celle-split eller får eksplicit højde.

## Label/editor-chrome

Elementlabel, type, kort ID, drag-håndtag og resize-håndtag er editor-chrome og må aldrig tælle med i canonical `x/y/w/h`.

## Parent auto-grow

Kasse/Sektion bruger fortsat valgt højde som minimum. Parentens synlige højde skal kunne vokse til den faktiske bundkant af børn, inklusive eksplicitte row-span-celler, og falde tilbage mod minimum når indhold fjernes.

## Diagnostics

En celle-drop-transaktion logges som `cell_drop_commit` med mindst:

- element-ID og type
- add/move
- fra/til-parent ved flytning
- `dropZone`
- `targetId`
- placement-geometri/båndinformation
- strukturel modelsummary efter transaktionen

Rå tekstindhold, credentials, nonces og tokens må ikke logges.
