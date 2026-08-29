# Visual Designer Manager 0.1.44 status

## Scope

- BUG-13: Section/Box physical painted geometry.
- BUG-14: virtual viewport + dynamic Fit zoom.
- Preserve 0.1.43 Header/Footer conversion and keep Theme Shell cutover OFF.

## Fixed contract

- Desktop virtual viewport: 1920 px.
- Laptop virtual viewport: 1180 px.
- Mobile virtual viewport: 390 px.
- The model is laid out at the virtual viewport width; available admin/editor width only changes Fit zoom.
- Fit is recalculated when canvas-column width changes, including More canvas and Elementer/Inspector collapse/expand.
- Pointer deltas are converted from physical screen pixels back to virtual pixels/8px rows.
- Section/Box owns background, border and radius over the full physical geometry.
- Inner child surface is transparent and fills the Section/Box; editor chrome is not physical geometry.
- Manual height remains a minimum and children may auto-grow the parent.

## QA gate

- PHP syntax.
- JavaScript syntax.
- hierarchy normalizer QA.
- canonical model QA.
- source contract checks for virtual widths, ResizeObserver Fit, scale-aware geometry and parent painted box.
- Theme Shell cutover remains explicit OFF.
