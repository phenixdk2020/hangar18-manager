# Hangar18 backlog — canonical pointer

**Canonical backlog:** `docs/clean-backlog-v0100.md`

Dette dokument er den entydige indgang til projektets aktuelle backlog.

## Regel

- `docs/clean-backlog-v0100.md` er nu den aktive arbejdsbacklog for den nye rene Hangar18 Designer/Manager-kodebase.
- `clean/hangar18-manager/` er den autoritative clean-plugin-kilde.
- Det eksisterende root-plugin og alle `docs/active-backlog-v*.md` betragtes herefter som legacy/reference/migrationskilder, medmindre clean-backloggen eksplicit henviser til dem.
- Legacy editor-JavaScript, save guards, proxy-renderere eller gamle persistence-runtimes må ikke kopieres ind i clean-pluginet.
- Historiske backlogfiler må ikke redigeres for at ændre nutidig status.
- Gamle webpages konverteres først efter clean QA PASS og kun gennem en særskilt migrator.

Hvis denne pointer og et historisk dokument modsiger hinanden om hvad der er aktuelt, vinder denne pointer og clean-backloggen.
