# Visual Designer Manager 3.0.0-alpha.9

Alpha.9 samler de aftalte rettelser til test4:

- Eventdetalje: billede → faktabånd → eventfelter.
- Separat padding top/højre/bund/venstre på sektioner og kasser, også efter gem/genindlæsning.
- Formular-preview: feltbredder, afstand og mobiltilpasning.
- Fjernelse af den ekstra gallerioverskrift og teksten “← Tilbage til album”.
- Albumhøjde baseret på billedantal og breakpoint samt styrbar bundluft før Footer.
- Alpha.8's responsive Header/side/Footer-scopes bevares.

## Rettelser før publicering

Bootstrap-referencen i build-scriptet er rettet. QA-kørsel 34024126098 bestod på commit b687c45b9a84c1d405e92c9ce40d93fb515b3a38.

Efterfølgende kodegennemgang fandt, at PHP LayoutModel fjernede de nye paddingfelter ved normalisering. Alpha.9-buildet bevarer nu eksplicitte sideværdier i intervallet 0–240, inklusive nul. Manglende værdier forbliver manglende, så den eksisterende fælles padding og migrationens standarder fortsat virker.

`.github/scripts/v3_alpha9_padding_qa.php` kontrollerer den faktiske PHP-model gennem saveVersion/get/history med WordPress-metadata i hukommelsen. Testen dækker sektioner, kasser, gentagen lagring, gamle layouts og grænseværdier. Den køres i både QA- og releaseworkflowet. Den oprindelige V1-kilde er uændret.

## Release og installation

QA skal være grøn efter den sidste koderettelse. Opret PR til `v3-clean-refactor`, merge det testede head og start det eksisterende releaseworkflow med `v3-alpha9-release-now.txt`. Workflowet gentager gates og gemmer den versionerede installations-ZIP og `v3-update.json` på V3-branchen.

Før udlevering skal den publicerede ZIP's SHA-256 svare til manifestet. Pakken installeres som opdatering af Visual Designer Manager på test4; nyt tema eller ny import er ikke nødvendigt for en eksisterende V3-installation.

Automatiseret QA er ikke manuel visuel accept af test4. Versionen forbliver alpha; V3-BASELINE.md's krav før 3.0.0 gælder fortsat.
