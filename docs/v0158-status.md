# Visual Designer Manager 0.1.58 status

- BUG-20 / VD-PAGE-SAVE-CACHE-001 implementeret i Side Designerens server-side save-lifecycle.
- Canonical Designer-model gemmes og verificeres før WordPress-siden touches.
- `wp_update_post()` udløser standard `post_updated` / `save_post` integrationspunkter efter den nye Designer-state findes.
- `clean_post_cache()` køres eksplicit bagefter.
- Canonical no-op Gem invaliderer også frontend-cache.
- `Gem & vis` bruger `h18_vd_saved=<version>` som cache-buster.
- Restore invaliderer samme frontend-cachevej.
- Menu-kode er ikke ændret.
