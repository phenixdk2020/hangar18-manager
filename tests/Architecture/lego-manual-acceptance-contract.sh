#!/usr/bin/env bash
set -euo pipefail

DOC='docs/lego-manual-acceptance.md'
TPL='docs/lego-test-session-template.md'

for file in "$DOC" "$TPL"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

# Core LEGO behavior that must remain manually testable.
require_contains "$DOC" 'Elementbibliotek og drop' 'element library/drop scenario missing'
require_contains "$DOC" 'Kasse og nesting' 'nesting scenario missing'
require_contains "$DOC" 'Side-by-side LEGO' 'side-by-side scenario missing'
require_contains "$DOC" 'Desktop resize' 'Desktop resize scenario missing'
require_contains "$DOC" 'Tablet/Mobil overrides' 'responsive span scenario missing'
require_contains "$DOC" 'Design og spacing' 'design/spacing scenario missing'
require_contains "$DOC" 'Foldbare paneler' 'collapsed-panel scenario missing'
require_contains "$DOC" 'Undo/Redo' 'history scenario missing'
require_contains "$DOC" 'Save/reload persistence' 'persistence scenario missing'
require_contains "$DOC" 'Preview' 'preview scenario missing'
require_contains "$DOC" 'Backup / restore' 'backup/restore scenario missing'
require_contains "$DOC" 'Protected domains regression' 'protected-domain regression missing'

# Key architecture/UX acceptance guards.
require_contains "$DOC" 'Auto-kasser/layoutmotor' 'existing Auto-kasser motor must be tested'
require_contains "$DOC" 'minimum er 1' 'minimum column span acceptance missing'
require_contains "$DOC" 'Arv Desktop' 'responsive inheritance acceptance missing'
require_contains "$DOC" 'starter minimeret' 'default-collapsed panel acceptance missing'
require_contains "$DOC" 'ét logisk checkpoint' 'single history checkpoint acceptance missing'
require_contains "$DOC" 'Vehicle, Event og Gallery' 'protected domain names missing'
require_contains "$DOC" 'Automatisk Playwright QA er støttebevis' 'manual acceptance ownership missing'

# Session template must bind the result to a concrete build and all A-L scenarios.
require_contains "$TPL" 'Commit SHA:' 'build SHA field missing'
require_contains "$TPL" 'Pluginversion:' 'plugin version field missing'
for id in A B C D E F G H I J K L; do
  require_contains "$TPL" "| $id —" "session row $id missing"
done
require_contains "$TPL" 'Overall må kun sættes til `PASS`' 'overall PASS rule missing'
require_contains "$TPL" 'Protected-domain regression: Nej/Ja' 'protected regression result field missing'

# These files are documentation/contracts only; they must never imply public cutover.
if grep -Ei 'activate public|execute cutover|public mutation available: yes' "$DOC" "$TPL" >/dev/null; then
  echo 'FAIL: LEGO manual acceptance pack implies public cutover'
  exit 1
fi

echo 'LEGO-034 manual acceptance contract: PASS'
