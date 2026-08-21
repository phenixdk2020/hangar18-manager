# I9 evidence integrity

`tools/i9-evidence-integrity.cjs` er et read-only hjælpeværktøj til at kontrollere, at lokale evidence-referencer faktisk findes og kan bindes kryptografisk til det manifest, der indgår i I9.

Værktøjet ændrer ingen filer, logger ikke ind i WordPress og udfører ingen public mutation.

## Formål

Evidence-manifestet kan referere til både:

- lokale filer, f.eks. `evidence/chrome-desktop.md`;
- eksterne referencer, f.eks. en Actions-artifact eller en URL.

Integrity-værktøjet skelner eksplicit mellem disse typer. En ekstern reference markeres som **external / ikke lokalt verificeret**; den får aldrig en opdigtet hash eller falsk `verified=true`.

Lokale filer får:

- SHA-256;
- filstørrelse i bytes;
- gate-navn;
- original evidence-reference.

Selve manifestet får også SHA-256 og størrelse i integritetsrapporten.

## Kørsel

```bash
node tools/i9-evidence-integrity.cjs evidence/i9/manifest.json \
  --root . \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/
```

Standard-output er JSON.

Markdown:

```bash
node tools/i9-evidence-integrity.cjs evidence/i9/manifest.json \
  --root . \
  --markdown
```

## Sikkerhedsregler

For lokale evidence-referencer gælder:

- absolutte stier afvises;
- `..` path traversal afvises;
- filen skal forblive inden for `--root`;
- filen skal eksistere;
- referencen skal pege på en regulær fil;
- SHA-256 beregnes kun på den fundne lokale fil.

Manglende eller ugyldige lokale evidence-filer giver FAIL.

## Eksterne referencer

Referencer med URI-/scheme-format behandles som eksterne. De kan være legitime evidence-pointere, men dette lokale værktøj kan ikke bevise deres indhold.

Hvis en evidence-pakke skal være fuldt selvbærende og lokalt hashbar, bruges:

```bash
node tools/i9-evidence-integrity.cjs evidence/i9/manifest.json \
  --root . \
  --require-all-local
```

I denne mode giver enhver ekstern reference FAIL.

## Sammen med I9 PASS

Integrity-værktøjet kan kræve både korrekt build/environment binding og fuld I9-status:

```bash
node tools/i9-evidence-integrity.cjs evidence/i9/manifest.json \
  --root . \
  --expected-sha 0123456789abcdef0123456789abcdef01234567 \
  --expected-version 0.8.39 \
  --expected-target https://test2.hangar18.dk/ \
  --require-pass
```

`--require-pass` betyder stadig ikke, at værktøjet udfører de manuelle tests. Det betyder kun, at det underliggende manifest allerede skal være konsistent med alle otte evidenced PASS-gates.

## QA-kontrakt

`tests/Architecture/i9-evidence-integrity-contract.sh` verificerer bl.a.:

- korrekt SHA-256 for lokale evidence-filer;
- ekstern reference klassificeres som ekstern og ikke verificeret;
- `--require-all-local` blokerer eksterne refs;
- manglende lokal fil blokerer;
- absolute/path-traversal refs blokerer;
- forkert build-SHA eller staging-target blokerer;
- integritetsværktøjet indeholder ingen direkte fil-write primitives.

Kontrakten køres transitivt gennem den canonical I9 evidence QA-kæde og dermed både I9 Prep QA og Architecture QA.
