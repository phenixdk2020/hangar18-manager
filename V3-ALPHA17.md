# Visual Designer Manager V3 — 3.0.0-alpha.17

## Scope

Alpha.17 retter størrelsen på Eventliste-kortene på desktop/tablet med V1 som visuel reference, uden at ændre den aktuelle V3-menu eller eventindholdet.

V1 brugte kompakte eventkort i et interval omkring 280–360 px, mens V3 hidtil brugte `repeat(..., minmax(0,1fr))`, så få kort kunne blive strakt meget store over hele Eventlistens bredde.

## Ændringer

- Eventkort bruger som standard **280 px minimum** og **360 px maksimum**.
- **Maks. kolonner** bestemmer højst hvor mange kort der kan ligge i en række.
- Eventlistens maksimale bredde beregnes ud fra maks. kortbredde + gap, så et enkelt kommende event ikke bliver strakt ud.
- Designer → **Eventliste** får direkte styring af:
  - Min. kortbredde
  - Maks. kortbredde
  - Maks. kolonner
  - Kortjustering: venstre / centreret / højre
  - Kortafstand
  - Kortpadding
  - Billedformat
  - Fast billedhøjde
  - Hjørner
- Billedformat har **16:10 · V1** som standard samt 16:9, 4:3 og Fast højde.
- Nye Eventlister bruger V1-lignende standarder: 18 px gap, 20 px padding, 8 px hjørner og lys kortbaggrund.
- Eksisterende eksplicit gemte værdier for padding, radius og farver bevares.
- Mobilreglerne fra Alpha.15/16 bevares: Eventliste bliver fortsat én kolonne på telefon.

## Acceptance

På test4 skal Events-siden visuelt vise kompakte kort som V1: et enkelt kommende event må ikke blive bredere end den valgte maks. kortbredde, og flere tidligere events må lægge sig i kompakte rækker. Ændringer i Designerens bredde-/formatfelter skal kunne ses både i preview og live.
