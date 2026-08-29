# Visual Designer Manager 0.1.45 – status

Dato: 2026-08-29

## Implementeret

- VD-TEXT-VALIGN-001: Tekst har canonical `verticalAlign = top|center|bottom`; eksisterende modeller defaultes til `top`.
- VD-IMAGE-MIME-001: WordPress-mediavælgeren bruger `library.type = image`; PNG/JPG/WebP/GIF følger WordPress' billed-MIME-regler uden JPG-hardcoding.
- VD-FOOTER-LEGACY-SOURCE-001: Footer-kilder prioriteres old Visual Builder assignment/template → legacy shell → eksplicit standardfallback.
- VD-CANVAS-ZOOM-001: manuel 25-200% wheel-zoom, pointer-anchor, overflow-scrollbars og Fit/100%/−/+.
- Fit-mode følger editorbredden; manuel zoom ændres ikke af Inspector/Elementer/Mere canvas.
- Theme Shell cutover er fortsat OFF.

## QA-status

Kode-/modelkontrakter er dækket af release-gates. Bruger-QA af interaktion, Footer-kilde på testsite og browseradfærd afventer.
