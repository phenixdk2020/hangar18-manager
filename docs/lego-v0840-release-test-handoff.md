# LEGO v0.8.40 — officiel release test handoff

## Formål

Denne testfase bruger den officielle Hangar18 Manager **v0.8.40** releasepakke som testkandidat på `test2.hangar18.dk`.

Releaseidentitet:

- version: `0.8.40`
- release package commit: `b35b3809500f7de90ab7a3df0249fd84194edb51`
- package: `dist/hangar18-manager.zip`
- SHA-256: `1497d3f0bd784aa10dcb8b14ee91a74b21fda99c78071ddedb2dcf0f2b988a66`
- public cutover authorized: **NO**

## Testregel

Den officielle ZIP må installeres på `test2`, men eksisterende sider må ikke public-konverteres som del af LEGO-testen. Vehicle/Event/Gallery forbliver protected domains.

## Manuel A–L acceptance

Kør scenarierne i `docs/lego-manual-acceptance.md` mod den installerede v0.8.40-build:

A. Elementbibliotek og drop
B. Kasse og nesting
C. Side-by-side
D. Desktop resize
E. Tablet/Mobil overrides
F. Design og spacing
G. Foldbare paneler
H. Undo/Redo
I. Save/reload persistence
J. Preview
K. Backup/restore
L. Vehicle/Event/Gallery regression

PASS kræver evidence pr. scenarie. Console-fejl, datatab/duplikering eller regression i protected domains tvinger samlet FAIL.

## Stopregler

Stop testen og rollback pluginet hvis:

- WordPress/PHP fatal error opstår;
- editoren mister eller dublerer data;
- Undo/Redo ændrer mere end den forventede brugerhandling;
- Vehicle/Event/Gallery ændrer adfærd eller layout;
- save/reload ikke reproducerer den gemte state.

## Efter PASS

Et fuldt A–L PASS er kun LEGO/manual acceptance evidence. Det erstatter ikke de øvrige I9-gates som Safari/Edge/screen-reader/live rollback evidence, og det autoriserer ikke I10 public cutover.
