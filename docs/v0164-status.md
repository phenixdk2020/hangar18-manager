# Visual Designer Manager v0.1.64 status

- BUG-23 / VD-CLIPBOARD-002: Designer clipboard reliability.
- Copy/Duplicate recovers the visibly selected node if the internal selectedId is stale.
- Paste/Duplicate reveals the inserted copy and reports status instead of looking like a no-op.
- Ctrl/Cmd+V reports an empty clipboard explicitly.
- Client normalization preserves desktop/laptop/tablet/mobile geometry.
- The shared editor-v018-core runtime keeps the fix common to Page Designer and Header/Footer.
