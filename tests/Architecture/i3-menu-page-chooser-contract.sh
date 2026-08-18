#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/MenuPageChooserAdminController.php'
js='assets/ultimate-designer-menu-pages.js'

grep -F "post_type'=>'page'" "$controller" >/dev/null
grep -F "post_status'=>['publish','draft','private']" "$controller" >/dev/null
grep -F 'Tilgængelige sider' "$js" >/dev/null
grep -F 'En side behøver ikke være i menuen' "$js" >/dev/null
grep -F "setValue(row,'Type','page')" "$js" >/dev/null
grep -F "setValue(row,'Target',page.Id)" "$js" >/dev/null
grep -F "button.click()" "$js" >/dev/null

# Page chooser is discovery/UI only: it must not register write endpoints or mutate WP page posts.
for forbidden in 'admin_post_' 'wp_ajax_' 'wp_insert_post' 'wp_update_post' 'wp_delete_post' 'update_post_meta' 'delete_post_meta'; do
  if grep -F "$forbidden" "$controller" >/dev/null; then echo "FAIL: page chooser may not mutate pages: $forbidden"; exit 1; fi
done

echo 'I3.1 menu page opt-in/out contract: PASS'
