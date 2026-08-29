# Visual Designer Manager 0.1.47 – status

Dato: 2026-08-29

## Implementeret
- BUG-02 regression-gate: v0125 er eneste selection-owner; prearmed v0138 bevares og restore-burst er styrket.
- BUG-17: rich-text frontend wrapper beskytter inline EM/STRONG/U mod flex-split.
- BUG-18: root virtual page har 0 intern padding/border; editor-chrome ligger udenfor siden.
- Footer parity iteration og Fit i lokal Header/Footer preview.
- No-op Save på Side/Header/Footer.
- Separat Hjem – Visual Designer-kladdeside, uden ændring af gammel Hjem eller WordPress page_on_front.
- Samlet canonical Header + Side + Footer preview mens Theme Shell er OFF.
- Menu er næste UX-arbejdsspor; ingen menu-data ændres i 0.1.47.

## QA
PHP/JS syntax, hierarchy/model QA og 0.1.47 kontrakt-gates skal være grønne før release. Bruger-QA af selection, Footer parity og samlet landingsside-preview følger efter installation.
