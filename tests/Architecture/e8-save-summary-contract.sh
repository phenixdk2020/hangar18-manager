#!/usr/bin/env bash
set -euo pipefail

fail=0

require_text() {
  local file="$1" text="$2" label="$3"
  if ! grep -F "$text" "$file" >/dev/null; then
    echo "SAVE SUMMARY CONTRACT FAIL: missing $label"
    fail=1
  fi
}

forbid_text() {
  local file="$1" text="$2" label="$3"
  if grep -F "$text" "$file" >/dev/null; then
    echo "SAVE SUMMARY CONTRACT FAIL: old behavior still present: $label"
    fail=1
  fi
}

require_text hangar18-manager.php 'Egen kommentar (valgfri)' 'optional user-note label'
require_text hangar18-manager.php 'page_auto_change_summary' 'automatic summary request field'
require_text hangar18-manager.php 'summarize_page_editor_changes_v071' 'server-side summary fallback'
require_text hangar18-manager.php "'AutoChangeSummary'" 'separate automatic history field'
require_text hangar18-manager.php "'UserChangeNote'" 'separate optional user history field'
require_text assets/admin.js 'h18BuildAutomaticSummaryV071' 'client deterministic summary builder'
require_text assets/admin.js 'h18AutoSummaryBaselineV071' 'saved-state comparison baseline'
require_text assets/admin.js 'h18RefreshAutomaticSummaryV071();' 'summary refresh on submit'

forbid_text hangar18-manager.php 'Skriv kort, hvad du har ændret, før siden gemmes som en ny version.' 'mandatory server note block'
forbid_text assets/admin.js 'Beskriv ændringen før Gem' 'mandatory client note block'

if [[ "$fail" -ne 0 ]]; then exit 1; fi

echo 'E8 optional save summary UX contract: PASS'
