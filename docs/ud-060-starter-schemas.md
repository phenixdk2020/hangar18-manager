# UD-060 – Vehicle / Event / Gallery starter schemas

## Goal

UD-060 provides three starter schemas as presets for the existing generic Dynamic CMS motor. The presets are definitions only in this phase: they do not install data types, migrate legacy pages or replace Vehicle/Event/Gallery rendering.

## Design requirement

The product design requires three domain schemas – Vehicle, Event and Gallery – to be creatable through presets rather than separate special engines.

The generic schema payload targets the already implemented UD-051/UD-054 data shape:

- `Key`
- `SingularLabel`
- `PluralLabel`
- `SchemaVersion = 2`
- `Fields[]`

Supported field types used by the presets are limited to the current generic motor: `text`, `number`, `bool`, `date`, `media`, `relation`, `group`, and `repeater`.

## Entry title

The existing generic data editor stores an entry title separately from `Fields[]` and requires it for every data entry. Therefore the design-level required `title` property is represented by `EntryTitle.Required = true` in preset metadata instead of creating a duplicate `title` field.

## Vehicle

The design specification explicitly describes the core Vehicle model: title, description, image, manufacturer, model, year, engine, weight, optional color and active.

The preset also carries current Hangar18 fields needed for lossless future compatibility: type, crew, service period, restoration status, history, Aalborg service, restoration text and technical source URL.

Because the current generic v2 data motor has no dedicated rich-text or URL field, those compatibility values use generic `text` fields for now. This is a storage/schema compatibility choice, not a statement that the future editor should expose only single-line text controls.

## Event

The design document names Event as a required domain schema but does not prescribe its complete field list. The starter preset therefore maps the current v0.5.30 Event contract:

- required event date;
- short description;
- start/end time;
- venue and address;
- contact;
- description, program and practical information;
- main image;
- relation to Gallery.

The legacy `GalleryAlbumPageId` cannot be copied directly into a generic relation because the new relation must reference the migrated Gallery data entry. The preset explicitly marks `gallery_album` as requiring relation ID remapping during a future migration.

## Gallery

The design document requires Gallery as a custom-data domain but does not prescribe its complete field list. The preset maps current v0.5.30 Gallery behavior:

- album type;
- description;
- cover image;
- ordered image list.

The ordered image list uses the generic `repeater` field with nested `media`, title and description fields. The current generic engine limits a repeater to 20 rows, so the preset uses that existing limit. No existing gallery album is changed by this phase.

## Legacy compatibility metadata

Each preset records:

- legacy parent slug;
- legacy marker;
- legacy source fields;
- transformation/remapping notes where required.

This metadata is not part of the installable generic schema. It exists so a later dry-run migration service can prove what will map before any mutation occurs.

## Safety rule

Until explicit old/new state and markup audits pass, Vehicle, Event and Gallery remain protected by `CompatibilityPolicy` and continue using the v0.5.30 persistence/render paths.

## Definition of Done for this phase

- exactly three presets exist: Vehicle, Event, Gallery;
- presets validate against the existing generic data field capabilities;
- Vehicle contains the design-specified core data model;
- Event/Gallery cover all currently required legacy data;
- Event → Gallery is represented as a generic relation;
- Gallery images are represented as a generic repeater;
- no WordPress writes occur;
- no legacy runtime file changes;
- QA passes on PHP 8.0, 8.2 and 8.3.
