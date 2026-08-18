# E10 Permissions core — UD-094 to UD-097

## UD-094 Named capability matrix

Ultimate Designer actions map to explicit least-privilege capabilities instead of one broad editor permission. The catalog covers settings, design, components, templates, data schemas, content, assets, publish, custom code, events and galleries.

Role recipes are defined for Administrator, Designer, Editor, Eventansvarlig and Gallery Manager. `WordPressRoleInstaller` can install these roles/capabilities explicitly, but this passive slice does not run the installer automatically.

## UD-095 Design lock

`DesignLockGuard` prevents structure and/or design properties from being changed while still permitting explicitly released content fields. Structure changes include key/type/order/parent changes; design changes cover the shared design/layout/typography/state property families.

## UD-096 Component editable inputs

`ComponentEditableInputPolicy` derives the allow-list from the existing linked-component `Inputs` definition. Content-only overrides not explicitly released by the designer are discarded/rejected by policy.

## UD-097 Domain-scoped roles

`DomainScopePolicy` restricts roles to Dynamic CMS datatype keys. Eventansvarlig is scoped to `event`, Gallery Manager to `gallery`, while Designer/Admin recipes can use wildcard scope.

## Activation boundary

Existing Hangar18 admin handlers continue to use the current legacy permission gate until migration/rollback/security QA is complete. The new role installer is callable but is not wired into plugin activation or current page/domain handlers in this slice.
