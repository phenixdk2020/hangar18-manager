# Visual Designer Manager V3 — 3.0.0-alpha.13

## V1 Mobile Geometry Recovery

Alpha.13 retter den persistente mobilfejl på datalaget i stedet for at tilføje endnu en responsive workaround.

- Bevarer Alpha.12/Alpha.9 responsive renderer uændret.
- Læser den bevarede V1-sidegeometri fra `_h18_clean_layout_v1`.
- Matcher V1 og V3 på node-ID + type.
- Kopierer kun `geometry.mobile` 1:1 til `_vdm_layout_v1`.
- Bevarer desktop/laptop/tablet, props, hierarki og V3-only nodes.
- Laver backup af den eksisterende V3-model før ændring.
- Gemmer recovery som en normal Designer-version.
- Udfører samme mobile recovery på Header/Footer templates, når bevaret V1-template/global-layout findes.
- Kører én gang pr. side/template.

Alpha.12 eventrettelser bevares: almindelig eventbilledvisning og linjeskift i Program/øvrige eventfelter.
