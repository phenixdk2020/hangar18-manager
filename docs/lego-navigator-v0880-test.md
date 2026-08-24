# Ultimate Designer v0.8.80 — Navigator / Flyt til test

Dette er den manuelle acceptance-plan for Navigator/Move-laget. Testen må køres uden at ændre de frosne canvas drag/drop-fejl.

## Forudsætninger

- Installer v0.8.80 på test2.
- Åbn Hangar18 Manager → Sider på en side med mindst to top-level elementer og én Kasse/Grid/Flex med child-elementer.
- Gem ikke permanent før de strukturelle ændringer ser korrekte ud.

## Navigator

1. Navigator viser alle aktive editor-rækker i samme hierarki som `LayoutParentKey`.
2. Child-elementer vises under deres parent; top-level elementer ligger i roden.
3. Klik på top-level element i Navigator åbner samme element i Inspector/canvas.
4. Klik på nested child i Navigator åbner samme nested element.
5. Klik i canvas/Inspector flytter Navigator-highlight til samme key.
6. Fold/udfold en Kasse; state skal overleve refresh i samme browser.
7. Søg på navn, type og key; kun relevante grene vises.
8. Inaktive/skjulte elementer vises dæmpet i stedet for at forsvinde.
9. Breadcrumb viser `Side › ... › valgt element`; klik på ancestor vælger ancestor.
10. Toggle `Vis kontur...` viser/fjerner outline på container/grid/flex uden at ændre side-data.

## Deterministisk Flyt til

11. Vælg et top-level Tekst/Billede og vælg en almindelig Kasse under `Flyt til`; elementets `LayoutParentKey` skal blive Kasse-key.
12. Gentag til Flex/Grid, hvor target er gyldigt.
13. `Flyt ud` flytter ét niveau op og fjerner/ændrer ParentKey korrekt.
14. `Til top` / `Til bund` ændrer rækkefølgen blandt siblings i samme parent.
15. Vælg en sibling og brug `Før` / `Efter`; kun sibling order ændres.
16. Parent-picker må ikke vise valgt element selv eller descendants som target.
17. En operation der ville skabe parent-cycle må ikke kunne udføres.
18. Auto-kasser må kun tilbydes som parent for almindelig Kasse, ikke et vilkårligt Tekst/Billede.
19. Efter hver flytning skal eksisterende Kasse-preview opdatere via nesting refresh.
20. Undo/Redo skal efter smoke-test verificeres separat; Navigator introducerer ikke egen history stack.

## Regression

- Canvas Over/Under/Ind-i logikken må ikke ændres af Navigator-laget.
- Vehicle/Event/Gallery røres ikke.
- Save/reload af en Navigator-flyttet struktur testes først efter ovenstående 1–19 er PASS.

## Evidence

Ved fejl: slå TRACE master TIL, Start test, udfør kun den fejlede Navigator/Move-handling, Stop log og eksportér support bundle.
