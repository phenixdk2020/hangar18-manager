# Visual Designer Manager 0.1.31 – status

- [x] Arbejdspakke oprettet.
- [x] Scope fastlagt.
- [x] QA/testplan oprettet.
- [x] Header/Footer/Theme migrationsprincip dokumenteret.
- [x] Floating Button overlay-interaktion rettet: separat parent-relativt flytteflow uden normal celle-split drag/drop.
- [x] Rich-text selection preservation rettet for Fed/Kursiv og fælles toolbar-mekanisme.
- [x] Eksisterende globale Header/Footer-template-modeller koblet til Theme Shell-resolution som migrationsfundament.
- [x] Theme Shell-fundament implementeret med cutover slået fra som standard.
- [x] PHP/JavaScript + model/hierarchy QA bestået.
- [x] Release manifest/package bygget og verificeret som 0.1.31.

## Bevidst ikke aktiveret i 0.1.31

Den visuelle 1:1 Header/Footer-cutover er ikke aktiveret endnu. Hangar18 Base Theme 1.2.0 forbliver fallback/reference, indtil den eksisterende Header/Footer fra `/koeretoejer-og-materiel/` er kortlagt og parity-testet på Desktop/Laptop/Mobil. Dette undgår dobbelt Header/Footer eller en ufuldstændig frontend-konvertering.
