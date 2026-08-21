# Ultimate Designer — hurtig reference

**DOC-2** · aktuel editorbaseline **Hangar18 Manager v0.8.41** · 21. august 2026

Denne side er den korte daglige huskeseddel. Se `ultimate-designer-user-manual.md` for den fulde forklaring, `ud-v0841-manual-retest.md` for den aktuelle testprocedure og `DESIGN-MANUAL.md` for de godkendte visuelle værdier.

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
- **v0.8.41:** palette → Venstre/Højre bruger nu den synlige side-zones koordinater, så native HTML5 drop-target ikke må falde tilbage til lodret placement.

Ved manuel test: prøv først **Tekst og billede → nyt Tekst fra palette → Venstre**. Resultatet skal være side-by-side, ikke lodret.

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

## Slet side — PAGE-DELETE-001

**Gælder først i en QA-grøn release, der eksplicit indeholder PAGE-DELETE-001; funktionen er ikke del af den allerede frigivne v0.8.41-pakke.**

Sikker flow:

```text
Slet side
   ↓
skriv aktuel sidetitel præcist
   ↓
ekstra bekræftelse
   ↓
B1-kompatibel safety backup
   ↓
WordPress Papirkurv
```

Regler:

- kræver `delete_pages` + objektspecifik `delete_post` + nonce;
- forkert titel eller Cancel = ingen mutation;
- bruger WordPress Trash, aldrig permanent delete;
- audit binder side-ID, titel, bruger, tid og safety-backup;
- restore genbruger eksisterende B1-motor;
- `Hjem`, `Køretøjer og materiel`, `Events` og `Billedgalleri` er låst mod funktionen.

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

## Aktuel acceptance

Canonical PENDING-record for v0.8.41:

`docs/lego-v0841-manual-acceptance.json`

Ingen scenario-PASS uden konkret evidence. Et samlet LEGO A–L PASS er stadig kun input til I9 og autoriserer ikke I10.

## Public cutover

```text
Automatiseret QA PASS
        ↓
I9 manual/live evidence PASS
        ↓
I10 kontrolleret conversion
```

I10-rækkefølge: comparison → Hjem → Om → Kontakt → Bliv medlem → protected domains efter særskilt proof → legacy removal sidst.
