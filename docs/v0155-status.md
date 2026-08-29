# Visual Designer Manager 0.1.55 – status

## Scope
- Separate sidehandlinger i Manager → Sider.
- Publicér og Gør til kladde ændrer kun WordPress post_status.
- Sæt som Hjem er selection-only og kræver publiceret side.
- Slet flytter siden til WordPress-papirkurven.
- Aktiv hjemmeside er beskyttet mod draft/trash.

## QA
- PHP syntax på hele pluginet.
- Eksisterende HierarchyNormalizer/LayoutModel regression-QA.
- Kontrakt-gates for separate action/nonces, wp_trash_post, capability-checks og fravær af “Publicér og sæt som Hjem”.
