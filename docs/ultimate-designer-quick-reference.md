# Ultimate Designer — hurtig reference

**DOC-2** · editorarkitektur gennem LEGO-033

Denne side er den korte daglige huskeseddel. Se `ultimate-designer-user-manual.md` for den fulde forklaring og `DESIGN-MANUAL.md` for de godkendte visuelle værdier.

## Byg

```text
Elementer/Funktioner → Canvas → vælg element → Direkte Design / Inspector
```

- Klik eller drag et element ind.
- Brug Kasse til logiske grupper.
- `LayoutParentKey` er hierarchy-authority.
- Vehicle/Event/Gallery må ikke generelt public-konverteres endnu.

## Flyt

```text
             OVER
              ↑
   VENSTRE ← MÅL → HØJRE
              ↓
             UNDER
```

- Over/Under = lodret rækkefølge.
- Venstre/Højre = side-by-side via eksisterende Auto-kasser.
- Ét side-drop = ét Undo-trin.

## Resize

12-kolonne grid:

```text
2 børn: 6 / 6
3 børn: 4 / 4 / 4
4 børn: 3 / 3 / 3 / 3
```

Træk grænsen mellem to naboer.

- min. span = 1;
- naboen kompenserer;
- række-budget ≤ 12;
- ét pointerforløb = ét Undo-trin.

## Responsive

```text
Desktop = base
Tablet  = arver Desktop, indtil override
Mobil   = arver Desktop, indtil override
```

Eksempel:

```text
Desktop 7 / 5
Tablet  8 / 4  ← override
Mobil   7 / 5  ← arv
```

`Arv Desktop`:

- til = vis Desktop-værdi;
- fra = tidligere override-snapshot kommer tilbage.

## Spacing

- X = vandret.
- Y = lodret.
- Brug responsive override kun når værdien faktisk skal afvige.

## Design

Direkte Design og Inspector viser samme canonical state.

Kontrollér især:

- typografi;
- tekst/baggrund;
- border/radius;
- opacity/shadow;
- Hover/Focus/Active/Disabled;
- Desktop/Tablet/Mobil.

## Undo / Redo

Forvent ét logisk trin pr. brugerhandling:

| Handling | Ét Undo skal gendanne |
|---|---|
| side-drop | placement + wrappers + order samlet |
| resize | begge nabo-spans samlet |
| responsive resize | kun aktiv device-state |
| designændring | tidligere designstate |
| indholdsændring | tidligere indhold |

## Før Gem

- [ ] Desktop kontrolleret
- [ ] Tablet kontrolleret
- [ ] Mobil kontrolleret
- [ ] ingen horisontal overflow
- [ ] fokus synligt
- [ ] kontrast OK
- [ ] billeder responsive / alt-tekst
- [ ] Undo/Redo sanity
- [ ] Vehicle/Event/Gallery upåvirket
- [ ] ændringsnote skrevet

## Public cutover

```text
Automatiseret QA PASS
        ↓
I9 manual/live evidence PASS
        ↓
I10 kontrolleret conversion
```

I10-rækkefølge: comparison → Hjem → Om → Kontakt → Bliv medlem → protected domains efter særskilt proof → legacy removal sidst.
