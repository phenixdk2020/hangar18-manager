# Visual Designer Manager v0.1.69

Status: release candidate

- VD-CANVAS-AUTOHEIGHT-001 implementeret som delt Page/Header/Footer runtime.
- Root canvas følger nederste direkte Sektion med 32 px bundluft og minimum 650 px.
- Højden kan både vokse og krympe.
- Viewport-stage følger eksisterende ResizeObserver.
- Ingen modelmutation i auto-height runtime.
