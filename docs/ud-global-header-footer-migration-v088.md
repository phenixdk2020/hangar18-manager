# Ultimate Designer – Header/Footer migration plan (v0.8.8 backlog)

## Status

Planned architecture work only. This document does **not** activate a new Header/Footer renderer and does not change the current public appearance.

## Goal

Header and Footer should eventually be edited through the same visual Designer model as normal page content, while preserving the current Hangar18 frontend 1:1 during migration.

Header/Footer are global templates, not ordinary page-local sections. They should therefore appear in the Designer as global design areas, for example:

- Globaler → Header
- Globaler → Footer

The Designer may expose normal composition primitives inside these areas, such as Container, Grid/Flex, Logo/brand, Menu, Text, Image, Button, links and spacing.

## Existing source of truth

Until cutover is explicitly approved, the existing runtime remains authoritative:

- `HEADER_DESIGN_OPTION` continues to hold current Header design settings.
- Existing `HEADER_START` / `HEADER_END` shell markers remain unchanged.
- Existing `FOOTER_START` / `FOOTER_END` shell markers remain unchanged.
- Existing shell/header/footer generation remains the public renderer.
- Vehicle/Event/Gallery stay on the protected legacy runtime.

## Migration phases

### HF-1 – Inventory and immutable baseline

Capture the current Header/Footer structure, settings, generated HTML/CSS, desktop/tablet/mobile screenshots and relevant WordPress state. Generate hashes for the accepted baseline so later comparisons can detect drift.

No writes to public Header/Footer.

### HF-2 – Shadow adapter

Build an admin-only adapter that maps the existing Header/Footer configuration into a Designer-compatible element tree. The shadow tree is for editing/preview only and must not become a second public source of truth.

No frontend hook or renderer switch.

### HF-3 – Visual Designer editing

Expose Header and Footer as global Designer workspaces. Reuse existing Designer primitives and Inspector controls where possible. Changes are stored only in shadow/design workspace state until accepted.

Required initial behavior: importing the current Header/Footer and saving without intentional design changes must produce a visually identical result.

### HF-4 – Compatibility comparison

Compare legacy output and Designer candidate for:

- desktop
- tablet
- mobile
- menu open/closed states
- sticky/static behavior
- logo/brand placement
- colors, typography, spacing, widths and heights
- responsive menu behavior
- footer columns/links/text

Any material difference blocks cutover.

### HF-5 – Save/rollback rehearsal

Run save, preview, revision and rollback against a non-public copy. Verify that the accepted legacy state can be restored exactly.

No public mutation during rehearsal.

### HF-6 – Controlled cutover

Only after manual QA PASS may a future version switch Header/Footer to a Designer-backed renderer. Cutover must be reversible and preserve the legacy baseline for immediate rollback.

This phase must be implemented separately and is not part of v0.8.8.

## Non-regression rules

1. Current Header/Footer appearance is the baseline and must not change unintentionally.
2. No direct migration of Vehicle/Event/Gallery as a side effect.
3. No automatic public cutover.
4. No deletion of existing Header/Footer configuration until rollback has been proven on the live test copy.
5. A Designer import followed by save-without-changes must be visually equivalent to the current frontend.
6. Header/Footer remain global templates and are not duplicated independently into every page.

## Recommended backlog sequence

- HF-1 baseline capture and comparer
- HF-2 legacy → Designer shadow adapter
- HF-3 global Header Designer workspace
- HF-4 global Footer Designer workspace
- HF-5 responsive/interaction compatibility QA
- HF-6 migration + rollback rehearsal
- HF-7 signed cutover preflight
- HF-8 public cutover only after explicit approval
