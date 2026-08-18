# Ultimate Designer — administrator/designer onboarding

## 1. Build safely

1. Open **Hangar18 Manager → Sider**.
2. Create a blank page or create from a Page Template.
3. Build with the element library and Navigator; use Containers/Flex/Grid for hierarchy.
4. Select an element and use **Indhold**, **Typografi**, **Design** and **Avanceret** in Inspector.
5. Use Desktop/Tablet/Mobil preview and only add breakpoint overrides where values differ from base.
6. Use the top **Gem** button or Ctrl/Cmd+S. A manual save is a permanent version; autosave is only crash recovery.
7. Add a meaningful change note before permanent save.

## 2. Reuse instead of copy/paste

- Save reusable visual subtrees as linked Components when changes should propagate.
- Use released Component Inputs for fields an Editor may change without touching design.
- Use Patterns when you want a disconnected copy.
- Use Page Templates for new-page starting points.

## 3. Dynamic CMS

- Create generic datatypes through schema presets/builders.
- Bind Text/Image/Link properties to the current data context.
- Use Query/Repeater List for repeated content.
- Vehicle/Event/Gallery are presets on the generic datatype model in the new architecture; the current production-like legacy registers are not converted until final migration.

## 4. Site Builder

- Build Header and Footer templates with the same element tree.
- Build menu data separately and bind it to Menu elements.
- Use template assignment priority for single/archive/system contexts.
- Keep existing legacy header/footer/menu active until the final live QA gate passes.

## 5. Interaction

- Forms require server validation even when client validation is enabled.
- Mail/save/redirect/webhook actions run as an ordered action chain.
- Modal/popup/menu behavior must remain keyboard operable.
- Webhook/redirect targets must pass the safe URL policy.

## 6. Assets

- Collections/folders/tags are metadata over WordPress Media IDs; do not renumber native IDs.
- Check Usage before deleting an asset.
- Set focal points for responsive crops.
- WebP/AVIF are derivatives; preserve the original.
- Duplicate detection reports SHA-256 matches and does not delete automatically.

## 7. Side Health

Review the five areas before publish:

- Design
- Mobile
- Accessibility
- Performance
- SEO

Fix **HardFailures** before relying on the numeric score. Side Health is advisory/read-only and does not silently rewrite the page.

## 8. AI suggestions

AI is suggestion-only:

- text suggestions require explicit Accept
- layout proposals must validate against the normal page schema
- design/accessibility proposals are tied to concrete element/property references
- accepted changes carry Undo data

Do not enable a provider until credentials/policy have been configured explicitly.

## 9. Export/import

1. Export page/global styles or selected artifacts.
2. Run import as **dry-run** first.
3. Review ID conflicts, remaps and broken asset references.
4. Do not confirm while the plan has blocking conflicts.
5. On confirmed import, verify the automatic pre-import backup exists.
6. Test restore before removing the source or legacy version.

## 10. Publish/revisions

- Working and Public versions are separate.
- Preview uses unpublished Working state.
- Publish promotes Working atomically.
- Replacing an existing Public state creates a pre-publish backup.
- Restore creates another revision; it does not erase history.

## 11. Final Hangar18 migration order

Do **not** bulk-convert the current site first.

1. Finish automated E14 QA.
2. Run manual Chrome/Edge/Firefox/Safari checks.
3. Run a real screen-reader core flow.
4. Clone/backup current page data.
5. Convert one non-critical comparison page.
6. Compare old/new markup, visuals, responsive behavior and forms.
7. Test rollback.
8. Convert Hjem/Om/Kontakt/Bliv medlem one at a time.
9. Convert Vehicle/Event/Gallery only after their current legacy output has passed side-by-side regression checks.
10. Keep rollback available throughout.
11. Remove legacy code only after every converted page/domain has been accepted.

This order preserves the current site while the new runtime is proven rather than assuming compatibility.
