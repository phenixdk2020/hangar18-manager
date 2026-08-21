# LEGO test session — resultatskabelon

## Build

- Dato/tid:
- Tester:
- Staging URL:
- Commit SHA:
- Pluginversion:
- Browser + version:
- OS:
- Desktop viewport:
- Tablet viewport:
- Mobil viewport:

## Resultater

| Scenarie | Status | Evidence | Note |
|---|---|---|---|
| A — Elementbibliotek og Over/Under drop | PENDING |  |  |
| B — Kasse og nesting | PENDING |  |  |
| C — Side-by-side Venstre/Højre | PENDING |  |  |
| D — Desktop resize/span | PENDING |  |  |
| E — Tablet/Mobil overrides + Arv Desktop | PENDING |  |  |
| F — Design og spacing | PENDING |  |  |
| G — Foldbare paneler | PENDING |  |  |
| H — Undo/Redo | PENDING |  |  |
| I — Save/reload persistence | PENDING |  |  |
| J — Preview | PENDING |  |  |
| K — Backup/restore | PENDING |  |  |
| L — Vehicle/Event/Gallery regression | PENDING |  |  |

Tilladte statusværdier: `PASS`, `FAIL`, `BLOCKED`, `PENDING`.

## Konsolideret resultat

- Overall: PENDING
- Console-fejl observeret: Nej/Ja
- Datatab eller dubletter observeret: Nej/Ja
- Protected-domain regression: Nej/Ja
- Klar til næste I9-gate: Nej/Ja

## Fejl

For hver FAIL/BLOCKED registreres:

- scenarie;
- præcise trin til reproduktion;
- forventet resultat;
- faktisk resultat;
- screenshot/video/log-reference;
- om fejlen reproduceres efter hard reload;
- om Undo/Redo eller save/reload påvirkes.

## Acceptanceregel

Overall må kun sættes til `PASS`, når A–L er `PASS`, build-SHA er registreret, og der ikke er en kendt reproducerbar console-/datatabs-/protected-domain-fejl.
