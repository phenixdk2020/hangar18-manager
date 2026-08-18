# E8 Workflow core — UD-081 to UD-088

## Scope

This slice establishes the new Ultimate Designer workflow model without converting existing pages or replacing the current Hangar18 legacy page/version runtime.

## Implemented

- UD-081: autosave snapshots are stored separately from permanent revisions.
- UD-082: manual saves create immutable revision entries with user, UTC time, note and state hash.
- UD-083: restore appends a new revision and records `RestoreOf`; history is never overwritten.
- UD-084: structured diff reports added, removed, moved and changed Sections/properties.
- UD-085: read-only preview resolves unpublished working state for desktop/tablet/mobile claims.
- UD-086: preview tokens are HMAC-signed, expiring and revocable.
- UD-087: working and published state are independent.
- UD-088: publish runs through a repository transaction and takes a permanent pre-publish backup before replacing an existing public state.

## Editor UX

The current legacy editor now also exposes its already-existing permanent save operation prominently in the top toolbar. `Ctrl/Cmd+S` invokes the same form submission, save-state feedback is visible, and leaving with unsaved changes triggers a browser warning. The old bottom `Gem som ny version` control remains as a secondary save entry point.

## Compatibility boundary

- No existing page is converted to the new staging/revision repositories in this slice.
- Vehicle/Event/Gallery remain on the protected legacy runtime.
- Existing WordPress page data, URLs and frontend markup are unchanged.
- Runtime activation of the E8 repositories will happen only after adapters and migration/rollback QA are in place.
