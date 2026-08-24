# Hangar18 backlog — canonical pointer

**Canonical backlog:** `docs/active-backlog-v0882.md`

Dette dokument er den entydige indgang til projektets aktuelle backlog.

## Regel

- Kun filen angivet som **Canonical backlog** ovenfor er den aktuelle arbejdsbacklog.
- Alle andre filer der matcher `docs/active-backlog-v*.md` er **historiske snapshots** fra det tidspunkt hvor den pågældende version var aktiv — også hvis gammel tekst inde i filen siger “current”, “aktuel” eller “canonical”.
- Historiske snapshots må ikke redigeres for at ændre nutidig status; nye statusændringer skrives i den aktuelle canonical delta/extends-kæde.
- `tools/backlog-snapshot-guard.py` verificerer at pointeren peger på den højeste backlogversion og klassificerer hver backlogfil maskinelt som `canonical` eller `historical_snapshot`.
- `tools/backlog-governance.py` merger den aktuelle `Extends`-kæde og producerer det operative `docs/backlog-index.json`.

Hvis denne pointer og et historisk dokument modsiger hinanden om hvad der er aktuelt, vinder denne pointer og den aktuelle extends-kæde.
