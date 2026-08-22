#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bridge="$root/assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js"
guard="$root/assets/ultimate-designer-lego-parent-key-guard-v0845.js"
history="$root/assets/ultimate-designer-history-atomic-v0840.js"
controller="$root/src/Admin/EditorLegoDropZonesAdminController.php"

node --check "$bridge"
node --check "$guard"
node --check "$history"

# LEGO-041 side-drop targeting contract remains intact.
grep -Fq "window.addEventListener('dragover'" "$bridge"
grep -Fq "window.addEventListener('drop'" "$bridge"
grep -Fq ".h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)" "$bridge"
grep -Fq "target.dispatchEvent(redirected)" "$bridge"
grep -Fq "event.stopPropagation()" "$bridge"
grep -Fq "data-h18-lego-palette-side-drop-bridge" "$bridge"
grep -Fq "__h18LegoPaletteSideDropBridgeV0843" "$bridge"

# LEGO-046 extends the same event-target bridge to vertical Under semantics.
# It may translate which existing row/root receives the base drop event, but it
# still must not create/move sections or write hierarchy/persistence itself.
grep -Fq 'data-h18-v0838-position="under"' "$bridge"
grep -Fq "canonicalUnderTarget" "$bridge"
grep -Fq "nextTopLevelRow" "$bridge"
grep -Fq "data-h18-lego-palette-vertical-drop-bridge" "$bridge"
grep -Fq "capabilityVersion: '0.8.46'" "$bridge"

grep -Fq "change.h18V0845ParentKeyGuard" "$guard"
grep -Fq ".h18-layout-parent-key" "$guard"
grep -Fq ".h18-layout-parent-select" "$guard"
grep -Fq "PARENT_TYPES" "$guard"
grep -Fq "data-h18-lego-parent-key-guard" "$guard"
grep -Fq "__h18LegoParentKeyGuardV0845" "$guard"

# LEGO-046 history boundary: a genuinely new trusted palette gesture must close
# an older pending atomic gesture before the new DOM mutation, while synthetic
# re-dispatches from the same gesture remain inside the current transaction.
grep -Fq "paletteGestureSerial" "$history"
grep -Fq "activePaletteGestureSerial" "$history"
grep -Fq "end(true, true)" "$history"
grep -Fq "data-h18-v0846-history-gesture-boundary" "$history"
grep -Fq "capabilityVersion: '0.8.46'" "$history"

grep -Fq "ultimate-designer-lego-palette-side-drop-bridge-v0843.js" "$controller"
grep -Fq "ultimate-designer-lego-parent-key-guard-v0845.js" "$controller"
grep -Fq "hangar18-ultimate-designer-lego-parent-key-guard-v0845" "$controller"
grep -Fq "hangar18-ultimate-designer-lego-drop-zones-v0838" "$controller"

# The bridge may only correct HTML5 event targeting. It must never become a
# second section creator, hierarchy writer, persistence layer or Undo/Redo stack.
if grep -Eq 'setParent\s*\(|createAutoFor|placeRowBeside|LayoutParentKey\s*=|insertBefore\s*\(|insertAfter\s*\(|appendTo\s*\(|\.before\s*\(|\.after\s*\(|wp_update_post|update_option|localStorage|sessionStorage|undo\s*\(|redo\s*\(' "$bridge"; then
  echo 'LEGO-041/046 contract FAILED: palette drop bridge contains forbidden placement/persistence/history ownership.' >&2
  exit 1
fi

# LEGO-042 may only protect the existing hidden/select control handoff. It may
# not choose a target, move DOM rows, create Auto-kasser or own history/save.
if grep -Eq 'setParent\s*\(|createAutoFor|placeRowBeside|insertBefore\s*\(|insertAfter\s*\(|appendTo\s*\(|wp_update_post|update_option|localStorage|sessionStorage|undo\s*\(|redo\s*\(' "$guard"; then
  echo 'LEGO-042 contract FAILED: parent-key guard contains forbidden placement/persistence/history ownership.' >&2
  exit 1
fi

echo 'LEGO-041/042/046 palette drop + parent-key + gesture-boundary contract: PASS'
