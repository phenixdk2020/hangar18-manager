# UD-061–UD-073 Site Builder core

This slice builds the generic Site Builder engine without converting existing pages or replacing the legacy Hangar18 header/footer/menu runtime.

Implemented in the passive architecture layer:

- UD-061 Header templates use the same `Sections` tree and Page Schema 1.22 as the page editor, with revisioned storage and global assignment metadata.
- UD-062 Footer templates use the same engine and assignment model.
- UD-063 Menus have a versioned tree model with stable IDs, parent/order, cycle detection, max depth, icons, badges and descriptions.
- UD-064 Classic menu renderer outputs semantic navigation, active state, submenu controls, mobile progressive enhancement and keyboard/Escape handling via passive runtime assets.
- UD-065 Transparent → solid header preset includes reduced-motion behavior.
- UD-066 Sticky shrink preset reserves initial height to avoid content jump.
- UD-067 Floating pill preset shares the same menu data source.
- UD-068 Mega menu preset is declared for component-backed panels; full visual mega-panel editing remains a later UI integration step.
- UD-069 Off-canvas mobile preset declares focus trap, Escape close, overlay and scroll lock requirements.
- UD-070 Fullscreen overlay preset declares focus/animation/reduced-motion behavior.
- UD-071 Side rail and bottom-mobile presets reuse the same menu data source.
- UD-072 Hover/active motion presets are declarative and require no layout shift.
- UD-073 Single/archive/system template assignments resolve by context and priority.

## Compatibility rule

None of these services are wired to replace the current frontend runtime. Existing Vehicle/Event/Gallery, current pages, legacy header/footer and current menu stay untouched until the approved final conversion/cutover phase.

## QA

`tests/Architecture/e6-site-builder-smoke.php` verifies shared header/footer element trees, global assignment metadata, nested menu validation, accessible classic rendering, cycle rejection, assignment priority and preset coverage. `assets/site-builder-runtime.js` is syntax-checked but not enqueued yet.
