# Visual Designer Manager V3 — Alpha.38

Version: `3.0.0-alpha.38`

## Scope

Alpha.38 fixes two responsive Designer-preview defects observed in the screen recording from 2026-09-13.

## 1. No Header/Footer flash in Designer

Laptop, Tablet and Mobil use the canonical frontend renderer inside the Designer, but that embedded iframe is page-only. Alpha.37 hid the global Header/Footer after the iframe load event, which could allow one browser paint with the shell still visible.

Alpha.38 keeps the iframe invisible while it navigates and reveals it only after the page-only bridge CSS has been inserted. Header/Footer should therefore no longer appear briefly and then disappear.

## 2. “Vis med Header + Footer” follows selected device

The composite Header/Footer preview previously filled the available dialog width, causing every device to behave like a Desktop viewport.

Alpha.38 assigns the iframe the exact selected CSS viewport before loading its document:

- Desktop: 1920 px
- Laptop: 1100 px
- Tablet: 850 px
- Mobil: 390 px

The iframe may be visually scaled to fit the dialog, but CSS media queries and responsive layout are evaluated at the real selected pixel width.

The preview bar shows device, CSS viewport width and visual scale percentage.

## Preserved behavior

- Normal responsive Designer remains page-only.
- “Vis med Header + Footer” remains the explicit full-shell preview.
- Alpha.37 Laptop/Tablet CTA button parity remains active.
- Alpha.36 selected-device ordinary “Forhåndsvis” behavior remains active.
- Desktop master editing remains unchanged.

## Acceptance

1. Select Laptop, Tablet or Mobil in Designer.
2. Verify Header/Footer do not flash briefly during responsive preview load or refresh.
3. Click “Vis med Header + Footer”.
4. Verify the preview bar reports the selected device and correct width.
5. Verify Mobil renders the mobile Header at 390 px.
6. Verify Tablet renders at 850 px and Laptop at 1100 px rather than Desktop width.
7. Switch devices and repeat without reloading the Designer page.
