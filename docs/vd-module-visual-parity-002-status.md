# VD-MODULE-VISUAL-PARITY-002 – status

**Dato:** 1. september 2026  
**Status:** Implementeret i source efter v0.1.75; afventer næste eksplicit bestilte release.

## Scope
- Events, Billedgalleri og Køretøjer og materiel.
- `_old` er visuel reference.
- Frontend beholder dynamisk flow-rendering og eksisterende søgning/sortering.
- Kortlayout er justeret mod `_old` med 90% frame, 3/2/1 grid, fuldbredde 16:9-billeder, beige kortkrop og kompakt spacing.
- Designer bruger den faktiske offentlige CollectionPageRenderer i en same-origin iframe i stedet for en separat JS-approximation.
- WordPress admin-bar skjules kun i iframe-previewet for redaktører, så preview-geometrien svarer til offentlig visning.

## Releasegrænse
- Plugin header/runtime forbliver `0.1.75`.
- `clean-update.json` forbliver `0.1.75`.
- Ingen ZIP, manifest eller release-trigger ændres af denne opgave.
