# Visual Designer Manager V3 – Alpha.25

## Formål

Alpha.25 er en strukturel mobilrettelse baseret på de seneste V1/V3-mobilscreenshots. V1 på `test2.hangar18.dk` er fortsat facit.

## Hovedændringer

- V1-konverterede Section/Container-noder nulstiller på mobil desktop-grid, `grid-template-rows`, `grid-auto-rows`, faste højder og minimumshøjder med ID-specifikke regler.
- Mobilindhold bruger naturligt `flex-direction: column` flow; skjulte Spacer-noder er ikke længere en separat spacing-kilde.
- Headerens nested Section/Container-wrappers flades ud med `display: contents`, og Header-surface ejer én naturlig flex-række med vertikal centrering.
- Header beholder V1-referenceværdierne fra Alpha.24: 70 px logo, 17 px/750 titel og 44 px hamburger.
- Footerens Section/Container-ID’er nulstiller grid-rækker/kolonner og minimumshøjder endnu stærkere.
- `theme-color` sættes til `#30382a`, så browser-/statusområdet følger den mørkegrønne Hangar18-reference.
- Alpha.24’s 155 px hero, 30/15 px mobilsektion-padding, single-surface featurekort, responsive sideafstande og Alpha.22-menu bevares.

## Acceptance

Efter installation skal især 390×844 og 430×932 kontrolleres mod V1:

- ingen stort tomt grønt område under Headerens indhold
- logo ikke beskåret
- tydelig afstand Header → hero
- Bevaring/Formidling/Fællesskab har indholdstilpasset højde
- Events/Billedgalleri har 15 px sidepadding
- knapper holder sig inden for sektionens indholdsbredde
- luft mellem sektioner kommer fra Designerens spacing-indstillinger, ikke fra faste grid-højder
- Footer er indholdstilpasset

V1 0.1.93-kildebaselinen forbliver låst ved `dc3bad403c764f4ec123a526333a781d05dde491`.
