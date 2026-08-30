# Visual Designer Manager 0.1.59 status

- BUG-21 / VD-TEXT-BG-INHERIT-001 implementeret.
- Text normaliseres canonical med `backgroundTransparent=true`.
- Synlig baggrund følger Text → nærmeste Kasse → Sektion.
- Legacy `backgroundTransparent=false` på Text kan ikke længere male en hvid leaf-flade.
- Menu, Billede, Knap, geometri og hierarchy-normalisering er ikke ændret.
- Release bygges gennem den eksisterende Visual Designer Manager release-workflow med versionslåst ZIP og SHA-256-manifest.
