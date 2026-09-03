# Visual Designer Manager — canonical backlog pointer

**Canonical arbejdsbacklog:** `docs/clean-backlog-v0100.md`  
**Aktuel vedligeholdelsesbaseline:** `v0.1.93`  
**Næste planlagte hovedmilepæl:** `v0.2.0`

Dette dokument er den entydige indgang til projektets aktuelle backlog og fortolker den historiske clean-backlog i forhold til den nuværende Visual Designer Manager-arkitektur.

## Aktuel status · 2026-09-03

- Visual Designer Manager er frigivet gennem v0.1.93.
- Konvertering og den gamle Eksport / import-menu er skjult; migrations- og recovery-motorerne bevares internt.
- Eksport har én normal indgang med **Eksporter alt**, komplet portable site-ZIP og to-lags SHA-256-verifikation.
- Siteindstillinger, farvevælger, formular-WYSIWYG og formulardesign er på den aktuelle regression-gate.
- Den centrale release-workflow skal bestå de aktuelle QA-gates før en ny updater-ZIP publiceres.
- Den kontrollerede navne-/plugin-basename-migration er fortsat reserveret til v0.2.0 og må ikke sniges ind i 0.1.x vedligeholdelsesversioner.

## Canonical regler

- `clean/hangar18-manager/` er fortsat den autoritative plugin-kilde indtil v0.2.0-migrationen gennemføres kontrolleret.
- Nye produkt-/runtime-navne skal bruge **Visual Designer Manager / VDM**. Historiske H18/Clean-identifikatorer må kun overleve som dokumenteret compatibility-, storage- eller migrationskontrakt.
- `docs/clean-backlog-v0100.md` er den detaljerede historiske/arkitektoniske arbejdsbacklog. Punkter, der allerede er implementeret i nyere releases, skal læses som historik og ikke som åbne opgaver.
- `docs/v01xx-status.md`, releasehistorik og grønne QA-gates er autoritativ dokumentation for gennemførte 0.1.x-opgaver.
- Gamle webpages/data må først destruktivt ændres, når en verificeret portable eksport og rollback-vej findes.
- Historiske backlogfiler ændres ikke for at omskrive fortiden; denne pointer angiver nutidig status.

## v0.2.0 — reserveret migrationsscope

Når den verificerede siteeksport er klar, omfatter v0.2.0 den planlagte kontrollerede oprydning af aktiv `clean`/`h18`/Hangar18-frameworknavngivning, pluginfolder/main-file identity, admin/AJAX/REST-identifikatorer og updater/activation-basename. Legacy storageværdier bevares kun gennem eksplicit compatibility/migration, indtil import og før/efter-QA er bestået.
