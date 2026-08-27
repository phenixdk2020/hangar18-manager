# 0.1.31 – Header/Footer/Theme migration notes

Reference for visuel parity: den eksisterende Hangar18 frontend, herunder siden `/koeretoejer-og-materiel/`.

## Princip
- Header og Footer bliver globale Visual Designer-modeller med egen historik.
- De skal bruge samme canonical layout engine som pages.
- Hangar18 Base Theme reduceres gradvist til shell/runtime.
- Ingen gammel editor-runtime må genintroduceres.
- Theme 1.2.0 forbliver rollback/parity baseline.

## Flyt fra theme til Visual Designer
- Header/footer geometri og layout.
- Logo- og menuplacering.
- Header/footer baggrunde, farver og spacing.
- Typografi og visuelle standarder, hvor de hører til Global Design.

## Behold i theme shell
- WordPress lifecycle og templates.
- wp_head/wp_footer og hooks.
- body_class og nødvendig markup.
- WordPress menu/data integration.
- fallback når Visual Designer-model ikke findes eller ikke er aktiv.

Cutover er eksplicit ikke en del af første migrationscommit; det sker først efter parity-QA.
