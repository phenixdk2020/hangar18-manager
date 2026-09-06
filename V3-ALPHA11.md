# Visual Designer Manager V3 – 3.0.0-alpha.11

## Formål
Alpha.11 retter den resterende mobilparitetsfejl efter Alpha.10: når et problematisk grid-område skifter til naturligt vertikalt reflow, skal den visuelle rækkefølge fortsat følge Designerens gemte mobile geometri og ikke den rå DOM-rækkefølge.

## Reference
De godkendte mobilreferencer fra test2 viser blandt andet:
- Header med logo, foreningsnavn og mobilmenu.
- Hjem: hero-billede → faktabånd → Om foreningen → efterfølgende sektioner.
- Om foreningen: Bevaring → Formidling → Fællesskab som fuldbredde stablede mobilkort.
- Ingen vandret clipping, tekstoverlap eller ekstreme utilsigtede tomme grid-mellemrum.

## Ændring
- Alpha.10's overflow/overlap/gap-detektion bevares.
- Når `h18-vdm-mobile-flow-repair` aktiveres, får hvert direkte VDM-element en deterministisk CSS `order` baseret på den effektive mobile grid-position.
- Sortering er top-til-bund (`y`) og derefter venstre-til-højre (`x`).
- Samme-række desktop/tablet-kort, der stables på mobil, beholder derfor den naturlige visuelle rækkefølge.
- Mobil-runtimeasset versionsløftes til `v3-alpha11-mobile-reflow.js` for at undgå stale browsercache.

## Ikke ændret
- Gemte layoutdata omskrives ikke.
- Header/Footer fallback aktiveres ikke; deres responsive templategeometri fra Alpha.8 bevares.
- Alpha.9 detail/form/gallery/padding-rettelser bevares.
- V1 0.1.93-baseline og regressionsgates bevares.

## Acceptance
Alpha.11 må først publiceres når:
1. V1 regression gates er grønne.
2. Alpha.10 overflow/overlap/gap-sikkerheden stadig er grøn.
3. QA beviser at DOM-rækkefølge ikke kan overrule mobile `y/x` under reflow.
4. Installations-ZIP er valideret og SHA-256 verificeret.
5. Endelig visuel accept foretages på rigtig mobil mod de viste test2-referencebilleder.
