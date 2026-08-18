# Vehicle / Event / Gallery compatibility contract — v0.5.30

This document characterizes the existing Hangar18 Manager v0.5.30 runtime that must remain visually and functionally compatible while Ultimate Designer is refactored.

## Shared protected contract

The current plugin identifies the three managed domains with stable parent slugs and content markers:

- Vehicle parent: `koeretoejer-og-materiel`
- Event parent: `events`
- Gallery parent: `billedgalleri`
- Vehicle marker: `HANGAR18-VEHICLE-DATA`
- Event marker: `HANGAR18-EVENT-DATA`
- Gallery marker: `HANGAR18-GALLERY-ALBUM-DATA`

The foundation phase must preserve these values and the existing WordPress page IDs/data.

## Vehicle

### Existing write/admin actions

- `h18_save_vehicle`
- `h18_save_vehicle_register_settings`
- `h18_save_vehicle_fields`
- `h18_rebuild_vehicle_register`

Saving a vehicle currently rebuilds the vehicle register. Vehicle-field changes also rebuild affected detail pages/register output. These behaviours are part of the compatibility contract.

### Existing frontend hooks

Overview/card output relies on, among others:

- `.h18-overview-title`
- `.h18-vehicle-register`
- `.h18-register-align-left`
- `.h18-register-align-center`
- `.h18-vehicle-card`
- `.h18-vehicle-card-image`
- `.h18-vehicle-card-body`

Detail output relies on, among others:

- `.h18-vehicle-hero`
- `.h18-vehicle-content`
- `.h18-vehicle-inner`
- `.h18-vehicle-main-layout`
- `.h18-vehicle-table`
- `.h18-color-value`
- `.h18-color-swatch`
- `.h18-vehicle-section`

Current layout characteristics that must not change accidentally include the card grid, 16:10 card image crop, detail alignment controls, the approximately 55/45 desktop detail layout, and one-column mobile detail layout.

## Event

### Existing write/admin actions

- `h18_save_event`
- `h18_save_event_layout`
- `h18_rebuild_event_register`

### Existing frontend hooks

Overview output relies on, among others:

- `.h18-overview-heading`
- `.h18-event-section-heading`
- `.h18-event-register`
- `.h18-event-card`
- `.h18-event-card-image`
- `.h18-event-card-body`

Detail output relies on, among others:

- `.h18-event-hero`
- `.h18-event-main`
- `.h18-event-meta`
- `.h18-event-section`
- `.h18-event-image`
- `.h18-event-gallery-link`

Current behaviour includes separate upcoming/past sections, existing alignment settings, event images, metadata layout, gallery link behaviour and responsive alignment overrides.

## Gallery

### Existing write/admin actions

- `h18_save_gallery_album`
- `h18_save_gallery_layout`
- `h18_rebuild_gallery_index`

### Existing frontend hooks

Album/detail output relies on, among others:

- `.h18-gallery-hero`
- `.h18-gallery-grid`
- `.h18-gallery-item`
- `.h18-align-left`
- `.h18-align-center`

Current behaviour includes the existing album image grid, image crop/object-fit, captions, left/center alignment and separate mobile alignment behaviour.

## Responsive contract

The current protected domain CSS has important mobile behaviour at approximately the WordPress 782px breakpoint. A replacement renderer must preserve equivalent desktop/tablet/mobile presentation before a protected domain is allowed to leave the legacy runtime.

## Migration acceptance rule

A new implementation is not considered compatible merely because it contains equivalent data. It must also preserve all CSS/JavaScript-relevant hooks and user-visible behaviour, or deliberately provide a compatibility layer that makes the rendered result equivalent.

Before switching any protected domain:

1. Compare persisted values for an existing record before/after edit.
2. Compare overview item count, order and links.
3. Compare detail markup and all CSS/JS-relevant class hooks.
4. Compare image selection/cropping and alignment.
5. Compare desktop and mobile presentation.
6. Verify the existing v0.5.30 data requires no manual recreation.
7. Keep the legacy renderer available as rollback until the new path has passed QA.
