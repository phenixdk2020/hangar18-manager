# VD-MODULE-VISUAL-PARITY-002 – status

**Dato:** 1. september 2026  
**Status:** Inkluderet i Visual Designer Manager v0.1.76.

## Scope
- Events, Billedgalleri og Køretøjer og materiel.
- `_old` er visuel reference.
- Frontend beholder dynamisk flow-rendering og eksisterende søgning/sortering.
- Kortlayout er justeret mod `_old` med 90% frame, 3/2/1 grid, fuldbredde 16:9-billeder, beige kortkrop og kompakt spacing.
- Designer bruger den faktiske offentlige CollectionPageRenderer i en same-origin iframe i stedet for en separat JS-approximation.
- WordPress admin-bar skjules kun i iframe-previewet for redaktører, så preview-geometrien svarer til offentlig visning.

## Release
- Plugin header/runtime er `0.1.76` efter releaseforberedelsen.
- ZIP og `clean-update.json` genereres kun af den centrale release-workflow.
- Historiske v0.1.75-funktioner er fortsat regression-gates.
