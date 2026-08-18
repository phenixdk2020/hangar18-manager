#!/usr/bin/env bash
set -euo pipefail

fail(){ echo "v0.7.2 contract FAILED: $1"; exit 1; }

# Save note is visibly and programmatically optional.
grep -F 'Egen kommentar (valgfri)' hangar18-manager.php >/dev/null || fail 'optional comment label missing'
grep -F 'aria-required="false"' hangar18-manager.php >/dev/null || fail 'optional textarea aria state missing'
if grep -F 'Skriv kort, hvad du har ændret' hangar18-manager.php >/dev/null; then fail 'legacy mandatory server message still present'; fi
if grep -F 'Beskriv ændringen før Gem' assets/admin.js >/dev/null; then fail 'legacy mandatory client validation still present'; fi
grep -F 'function h18MakeChangeNoteOptionalV072()' assets/admin.js >/dev/null || fail 'defensive optional-note guard missing'
grep -F ".prop('required', false).removeAttr('required')" assets/admin.js >/dev/null || fail 'required attribute is not actively cleared'

# Admin assets must be cache-busted with file timestamp as well as plugin version.
grep -F '$admin_css_version = self::VERSION' hangar18-manager.php >/dev/null || fail 'admin CSS cache bust missing'
grep -F '$admin_js_version = self::VERSION' hangar18-manager.php >/dev/null || fail 'admin JS cache bust missing'

# Typography controls exist and the nesting-aware CSS exposes them.
for field in SectionBodyFontFamily SectionHeadingFontFamily BodyFontSizePx H1FontSizePx H2FontSizePx H3FontSizePx; do
  grep -F "[$field]" hangar18-manager.php >/dev/null || fail "typography field missing: $field"
done
grep -F '.h18-element-design-box>.h18-element-typography-box{display:block!important' assets/admin.css >/dev/null || fail 'nested typography box visibility fix missing'
grep -F '.h18-element-typography-box .h18-field{display:block!important' assets/admin.css >/dev/null || fail 'typography field visibility rule missing'

# A visible editor version makes it obvious which build the site is running.
grep -F 'class="h18-editor-version"' hangar18-manager.php >/dev/null || fail 'visible editor version marker missing'

echo 'v0.7.2 save/typography contract: PASS'
