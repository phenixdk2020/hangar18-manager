# Hangar18 Manager v0.8.81 — permanent fjernelse af WhatIf

## Formål

WhatIf var oprindeligt en simuleringsmekanisme i den gamle Hangar18 Manager. Fra v0.8.58 blev den skjult med `NoWhatIfAdminController`, men de reelle HTML-felter, request branches og Page Editor-JavaScript fandtes stadig i legacy-kilden.

v0.8.81 ændrer dette fra **UI-skjulning** til **source-removal**.

## Autoritativ kontrakt efter migration

De primære runtime-filer må ikke længere indeholde ordet `WhatIf`/`whatif`:

- `hangar18-manager.php`
- `assets/admin.js`
- `assets/admin.css`
- `src/Admin/IntegrationAdminBootstrap.php`

Følgende kompatibilitetsfiler skal være slettet:

- `src/Admin/NoWhatIfAdminController.php`
- `assets/hangar18-no-whatif-v0858.js`
- `assets/hangar18-no-whatif-v0858.css`

Dokumentation, backlog og cleanup-diagnostik må fortsat nævne ordet historisk; de er ikke runtime paths.

## Fjernede domæner

Den guardede migration fjerner de kendte legacy simulation paths for:

1. Vehicle save, layout, register/rebuild og field settings.
2. Event save, layout og register/rebuild.
3. Gallery save, layout og rebuild.
4. Page Editor save-status/request-state.
5. Static/legacy page content paths hvor de bruger samme request-form.
6. Menu create/save/add/repair simulation controls og backend branches.
7. Design/Header/Footer/shell-relaterede legacy simulation branches.
8. Dashboard/help/log-tekster der kun beskriver WhatIf runtime.
9. WhatIf-specifik CSS og JavaScript.
10. Den v0.8.58 UI-only shim.

## Guardrails

`tools/whatif-source-cleanup.py` er fail-closed:

- den fjerner kun kendte markup/branch-former;
- balancerede PHP/HTML blocks skal kunne identificeres;
- første migration skal faktisk finde både UI og backend branches;
- efter migration må der være 0 `whatif` hits i de primære runtime-filer;
- PHP og JavaScript lintes efter mutation;
- release ZIP må ikke indeholde en fil med `whatif` i filnavnet;
- cleaner er idempotent, så senere releases blot verificerer den rene baseline.

Hvis én efterkontrol fejler, skal release-buildet stoppe. Der må ikke pakkes en delvist renset version.

## Funktionel konsekvens

Efter v0.8.81 er almindelige admin-handlinger altid reelle handlinger, når brugeren trykker Gem/Opdater/Rebuild. Sikkerhed skal derfor komme fra de etablerede mekanismer: nonce/capability checks, side-/site-backup, versionering, preflight hvor relevant, updater code backup og rollback — ikke fra et skjult simulationsflag.

## QA

Minimum acceptance på test2:

1. Ingen WhatIf-kontrol vises på Vehicle, Event, Gallery, Menu, Design eller Sider.
2. Save/Rebuild-handlinger fungerer normalt uden et `whatif` POST-felt.
3. Page Editor viser `Gemmer…`, aldrig `Simulerer…`.
4. Vehicle/Event/Gallery public output er uændret efter almindelig gem/rebuild.
5. Opdateringer/cleanup-audit må gerne omtale den historiske migration, men må ikke rapportere aktive runtime paths.
6. Repository/release QA skal fortsat blokere genintroduktion af aktive WhatIf-referencer.
