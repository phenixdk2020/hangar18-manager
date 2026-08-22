#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bridge="$root/assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js"
guard="$root/assets/ultimate-designer-lego-parent-key-guard-v0845.js"
history="$root/assets/ultimate-designer-history-atomic-v0840.js"
inspector="$root/assets/ultimate-designer-lego-inspector-only-v0847.js"
inspector_css="$root/assets/ultimate-designer-lego-inspector-only-v0847.css"
controller="$root/src/Admin/EditorLegoDropZonesAdminController.php"

node --check "$bridge"
node --check "$guard"
node --check "$history"
node --check "$inspector"

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

# LEGO-047 makes Inspector the only settings editor. Canvas may still own layout
# gestures such as drag/drop and resize, but not inline text/media/image settings.
grep -Fq "INLINE_EDIT_SELECTOR" "$inspector"
grep -Fq "DIRECT_SETTING_SELECTOR" "$inspector"
grep -Fq "selectInspectorForNode" "$inspector"
grep -Fq "armCompositionReconcile" "$inspector"
grep -Fq "__h18LegoParentKeyGuardV0845" "$inspector"
grep -Fq "data-h18-lego-inspector-only" "$inspector"
grep -Fq "__h18LegoInspectorOnlyV0847" "$inspector"
grep -Fq ".h18-canvas-image-tools" "$inspector_css"
grep -Fq ".h18-canvas-focal-dot" "$inspector_css"

# The existing canonical spacing/design fields already model the requested LEGO
# controls. LEGO-047 exposes them with user-facing Inspector wording without
# inventing another persistence schema.
grep -Fq "Afstand og spacing" "$inspector"
grep -Fq "Lodret afstand omkring element" "$inspector"
grep -Fq "Mellem elementer vandret" "$inspector"
grep -Fq "Mellem rækker lodret" "$inspector"
grep -Fq "Elementfarve / baggrund" "$inspector"
grep -Fq "Kanttykkelse" "$inspector"
grep -Fq "0 px = ingen synlig kant" "$inspector"
grep -Fq "Hjørner / runding" "$inspector"
grep -Fq "0 px = helt lige hjørner" "$inspector"

grep -Fq "ultimate-designer-lego-palette-side-drop-bridge-v0843.js" "$controller"
grep -Fq "ultimate-designer-lego-parent-key-guard-v0845.js" "$controller"
grep -Fq "ultimate-designer-lego-inspector-only-v0847.js" "$controller"
grep -Fq "ultimate-designer-lego-inspector-only-v0847.css" "$controller"
grep -Fq "hangar18-ultimate-designer-lego-inspector-only-v0847" "$controller"
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

# LEGO-047 is an interaction-policy adapter only. It may select an existing row
# and request the existing read-only visual reconcile, but it may not write
# hierarchy/order/persistence or create an independent history/placement model.
if grep -Eq 'setParent\s*\(|createAutoFor|placeRowBeside|LayoutParentKey\s*=|insertBefore\s*\(|insertAfter\s*\(|appendTo\s*\(|wp_update_post|update_option|localStorage|sessionStorage|undo\s*\(|redo\s*\(' "$inspector"; then
  echo 'LEGO-047 contract FAILED: Inspector-only adapter contains forbidden placement/persistence/history ownership.' >&2
  exit 1
fi

echo 'LEGO-041/042/046/047 palette + Inspector-only interaction contract: PASS'
