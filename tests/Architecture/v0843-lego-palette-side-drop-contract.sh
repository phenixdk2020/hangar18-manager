#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bridge="$root/assets/ultimate-designer-lego-palette-side-drop-bridge-v0843.js"
guard="$root/assets/ultimate-designer-lego-parent-key-guard-v0845.js"
history="$root/assets/ultimate-designer-history-atomic-v0840.js"
inspector="$root/assets/ultimate-designer-lego-inspector-only-v0847.js"
inspector_css="$root/assets/ultimate-designer-lego-inspector-only-v0847.css"
fixes="$root/assets/ultimate-designer-lego-fixes-v0851.js"
fixes_css="$root/assets/ultimate-designer-lego-fixes-v0851.css"
controller="$root/src/Admin/EditorLegoDropZonesAdminController.php"

node --check "$bridge"
node --check "$guard"
node --check "$history"
node --check "$inspector"
node --check "$fixes"
php -l "$controller" >/dev/null

# LEGO-041 side-drop targeting contract remains intact.
grep -Fq "window.addEventListener('dragover'" "$bridge"
grep -Fq "window.addEventListener('drop'" "$bridge"
grep -Fq ".h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)" "$bridge"
grep -Fq "target.dispatchEvent(redirected)" "$bridge"
grep -Fq "event.stopPropagation()" "$bridge"
grep -Fq "data-h18-lego-palette-side-drop-bridge" "$bridge"
grep -Fq "__h18LegoPaletteSideDropBridgeV0843" "$bridge"

# LEGO-046/051 use the same event-target bridge for vertical semantics. The
# bridge may resolve a nested target but delegates parent/stack ownership to the
# dedicated LEGO-051 runtime; it still does not persist data itself.
grep -Fq 'data-h18-v0838-position="under"' "$bridge"
grep -Fq 'data-h18-v0838-position="over"' "$bridge"
grep -Fq "canonicalUnderTarget" "$bridge"
grep -Fq "canonicalOverTarget" "$bridge"
grep -Fq "nextTopLevelRow" "$bridge"
grep -Fq "adoptNestedDrop" "$bridge"
grep -Fq "data-h18-lego-palette-vertical-drop-bridge" "$bridge"
grep -Fq "capabilityVersion: '0.8.51'" "$bridge"

grep -Fq "change.h18V0845ParentKeyGuard" "$guard"
grep -Fq ".h18-layout-parent-key" "$guard"
grep -Fq ".h18-layout-parent-select" "$guard"
grep -Fq "PARENT_TYPES" "$guard"
grep -Fq "data-h18-lego-parent-key-guard" "$guard"
grep -Fq "__h18LegoParentKeyGuardV0845" "$guard"

# LEGO-046 history boundary remains one trusted palette gesture per checkpoint.
grep -Fq "paletteGestureSerial" "$history"
grep -Fq "activePaletteGestureSerial" "$history"
grep -Fq "end(true, true)" "$history"
grep -Fq "data-h18-v0846-history-gesture-boundary" "$history"
grep -Fq "capabilityVersion: '0.8.46'" "$history"

# LEGO-047 keeps Inspector as the only settings editor.
grep -Fq "INLINE_EDIT_SELECTOR" "$inspector"
grep -Fq "DIRECT_SETTING_SELECTOR" "$inspector"
grep -Fq "selectInspectorForNode" "$inspector"
grep -Fq "armCompositionReconcile" "$inspector"
grep -Fq "__h18LegoParentKeyGuardV0845" "$inspector"
grep -Fq "data-h18-lego-inspector-only" "$inspector"
grep -Fq "__h18LegoInspectorOnlyV0847" "$inspector"
grep -Fq ".h18-canvas-image-tools" "$inspector_css"
grep -Fq ".h18-canvas-focal-dot" "$inspector_css"

# Existing canonical spacing/design fields remain visible with LEGO wording.
grep -Fq "Afstand og spacing" "$inspector"
grep -Fq "Lodret afstand omkring element" "$inspector"
grep -Fq "Mellem elementer vandret" "$inspector"
grep -Fq "Mellem rækker lodret" "$inspector"
grep -Fq "Elementfarve / baggrund" "$inspector"
grep -Fq "Kanttykkelse" "$inspector"
grep -Fq "0 px = ingen synlig kant" "$inspector"
grep -Fq "Hjørner / runding" "$inspector"
grep -Fq "0 px = helt lige hjørner" "$inspector"

# LEGO-051 manual acceptance follow-up: state is additive and editor-only.
grep -Fq "STACK_FIELD_CLASS" "$fixes"
grep -Fq "StackRootKey" "$fixes"
grep -Fq "stackUnder" "$fixes"
grep -Fq "stackOver" "$fixes"
grep -Fq "h18-v0851-stack-resize-handle" "$fixes"
grep -Fq "h18-v0851-selection-overlay" "$fixes"
grep -Fq "Træk en Kasse ind i Auto-kasser." "$fixes"
grep -Fq "Custom…" "$fixes"
grep -Fq "luft, baggrund og placering" "$fixes"
grep -Fq "h18-v0851-selection-overlay" "$fixes_css"
grep -Fq "h18-v0851-device-tabs" "$fixes_css"
grep -Fq "STACK_OPTION_V0851" "$controller"
grep -Fq "h18_lego_stack_v0851" "$controller"
grep -Fq "ultimate-designer-lego-fixes-v0851.js" "$controller"
grep -Fq "ultimate-designer-lego-fixes-v0851.css" "$controller"

grep -Fq "ultimate-designer-lego-palette-side-drop-bridge-v0843.js" "$controller"
grep -Fq "ultimate-designer-lego-parent-key-guard-v0845.js" "$controller"
grep -Fq "ultimate-designer-lego-inspector-only-v0847.js" "$controller"
grep -Fq "ultimate-designer-lego-inspector-only-v0847.css" "$controller"
grep -Fq "hangar18-ultimate-designer-lego-inspector-only-v0847" "$controller"
grep -Fq "hangar18-ultimate-designer-lego-parent-key-guard-v0845" "$controller"
grep -Fq "hangar18-ultimate-designer-lego-drop-zones-v0838" "$controller"

# The bridge remains an event-target adapter; actual hierarchy/stack writes live
# in the dedicated LEGO-051 runtime and server-side additive option bridge.
if grep -Eq 'setParent\s*\(|createAutoFor|placeRowBeside|LayoutParentKey\s*=|insertBefore\s*\(|insertAfter\s*\(|appendTo\s*\(|\.before\s*\(|\.after\s*\(|wp_update_post|update_option|localStorage|sessionStorage|undo\s*\(|redo\s*\(' "$bridge"; then
  echo 'LEGO-041/046/051 bridge contract FAILED: palette bridge contains forbidden direct placement/persistence/history ownership.' >&2
  exit 1
fi

if grep -Eq 'setParent\s*\(|createAutoFor|placeRowBeside|insertBefore\s*\(|insertAfter\s*\(|appendTo\s*\(|wp_update_post|update_option|localStorage|sessionStorage|undo\s*\(|redo\s*\(' "$guard"; then
  echo 'LEGO-042 contract FAILED: parent-key guard contains forbidden placement/persistence/history ownership.' >&2
  exit 1
fi

if grep -Eq 'setParent\s*\(|createAutoFor|placeRowBeside|LayoutParentKey\s*=|insertBefore\s*\(|insertAfter\s*\(|appendTo\s*\(|wp_update_post|update_option|localStorage|sessionStorage|undo\s*\(|redo\s*\(' "$inspector"; then
  echo 'LEGO-047 contract FAILED: Inspector-only adapter contains forbidden placement/persistence/history ownership.' >&2
  exit 1
fi

echo 'LEGO-041/042/046/047/051 palette + Inspector interaction contract: PASS'
