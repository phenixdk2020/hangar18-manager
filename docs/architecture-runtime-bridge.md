# Ultimate Designer runtime bridge – phase 2

## Goal

Phase 2 introduces a passive bridge between the existing Hangar18 Manager v0.5.30 runtime and the extracted Ultimate Designer architecture.

The phase is deliberately non-destructive. The bridge may expose architecture services for tests and future extraction work, but it must not replace existing WordPress handlers or frontend renderers yet.

## Baseline

- Base branch: `agent/architecture-foundation`
- Legacy runtime: Hangar18 Manager v0.5.30
- Page schema: 1.22
- Protected domains: Vehicle, Event, Gallery

## Shadow mode

`RuntimeBridge` boots in `shadow` mode.

In shadow mode:

1. Vehicle, Event and Gallery route to `legacy`.
2. Other domains may be inspected through `architecture-shadow`.
3. `mayReplaceLegacyHandler()` always returns `false`.
4. Construction of the bridge registers no WordPress hooks.
5. No legacy save, rebuild, shortcode or frontend-render path is replaced.

## WordPress factory

`WordPressRuntimeBridgeFactory` composes the bridge from adapters that preserve the existing v0.5.30 contracts:

- `LegacyOptionPageRepository` → `hangar18_manager_pages_v1`, keyed by page slug.
- `WordPressSecurityGate` → WordPress capabilities/nonces; current admin capability remains `edit_pages`.
- `LegacyOptionLogger` → `hangar18_manager_log` and the existing log entry shape/retention.
- `PageSchemaValidator` → existing normalized page schema 1.22.
- `Architecture` → element/property registries.

## Protected runtime rule

The following are explicitly out of scope for this phase:

- changing Vehicle/Event/Gallery HTML or CSS hooks;
- changing their marker payloads;
- changing their WordPress admin actions;
- changing existing URLs, IDs or media references;
- moving their save/rebuild/render handlers to new classes;
- changing page-editor persistence format;
- enabling a new renderer on public requests.

## Activation plan

The final bootstrap connection into the large legacy plugin file should be a minimal, reviewable change only after the shadow bridge tests are green. Activation must still leave all legacy handlers authoritative.

The preferred first live connection is therefore:

1. load `src/Autoload.php`;
2. register the autoloader;
3. create a `WordPressRuntimeBridgeFactory::create()` instance;
4. expose it only as a passive service reference;
5. register no replacement hooks.

A later extraction phase can then route one non-protected responsibility at a time through the bridge, with old/new comparison tests and a rollback path.

## QA gates

Phase 2 must pass on PHP 8.0, 8.2 and 8.3:

- foundation isolation guard;
- protected Vehicle/Event/Gallery contract test;
- PHP syntax validation;
- foundation registry/migration smoke tests;
- page schema 1.22 compatibility test;
- runtime bridge shadow-mode test;
- WordPress bridge factory composition test.
