# Visual Designer Manager v0.1.77 – Moduldesign

**Dato:** 1. september 2026  
**Status:** Release candidate; central ZIP/manifest-build kræves efter grøn QA.

## Scope
- Events, Billedgalleri og Køretøjer får et redigerbart **Moduldesign** i Visual Designer.
- Samme canonical `CollectionPageRenderer` bruges fortsat i Designer-preview og frontend.
- Live preview bruger kun en autoriseret same-origin preview-override; den publicerede side læser gemt post-meta.
- Designparametre: sidebredde, Desktop/Tablet/Mobil-kolonner, kortafstand, maks. kortbredde, kortbaggrund, tekstfarve, padding, radius, kortbilledformat, H1/H2/H3, brødtekst, accentfarve og sektionsafstand.
- `_old`-paritet er standardprofilen: 90% sidebredde, 3/2/1 kolonner, 22px gap, beige #eee8dc og 16:9 kortbilleder.
- Moduldesign gemmes sammen med en Designer-version og kan gendannes ved versions-restore.

## Releasegrænse
- Source bumpes til `0.1.77` efter QA.
- `clean-update.json` og ZIP må først ændres af central `visual-designer-release.yml`.
