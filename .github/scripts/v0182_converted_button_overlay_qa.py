from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit('FAIL missing ' + rel)
    return p.read_text(encoding='utf-8')


def req(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit('FAIL: ' + message)
    print('PASS:', message)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
converter = text('clean/hangar18-manager/src/Migration/VisualBlockConversionService.php')
migration = text('clean/hangar18-manager/src/Migration/ConvertedButtonOverlayMigration.php')
editor = text('clean/hangar18-manager/assets/editor-v018-core.js')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
manifest = json.loads(text('clean-update.json'))
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
req(header is not None and const is not None and header.group(1) == const.group(1) == '0.1.82', 'runtime/header version is exactly v0.1.82')

req("require_once H18_CLEAN_DIR . 'src/Migration/ConvertedButtonOverlayMigration.php';" in plugin, 'converted button migration is bootstrapped')
req('\\VisualDesignerManager\\Migration\\ConvertedButtonOverlayMigration::register();' in plugin, 'converted button migration is registered')

button_factory = converter.split('private static function buttonNode', 1)[1].split('private static function geometry', 1)[0]
req("'placementMode' => 'overlay'" in button_factory, 'future converted buttons are created as overlay')
req("'placementMode' => 'normal'" not in button_factory, 'converter no longer emits normal-flow buttons')
req(re.search(r"node\.props\.placementMode\s*===\s*['\"]overlay['\"]", editor) is not None, 'Designer floating-button contract still uses overlay placement')

req("MARKER_META = '_h18_vd_converted_button_overlay_v0182'" in migration, 'one-time migration marker exists')
req("BACKUP_META = '_h18_vd_converted_button_overlay_backup_v0182'" in migration, 'pre-migration backup marker exists')
req("$sourceType !== 'external'" in migration and "$sourceHtml === ''" in migration, 'migration requires an external immutable source snapshot')
req("substr(hash('sha256', (string) $postId . '|' . $sourceHtml), 0, 8)" in migration, 'migration derives the exact converter source suffix')
req("$prefix = 'button-' . $suffix . '-'" in migration, 'migration scopes changes to converter generated button IDs')
req("(string) ($node['type'] ?? '') !== 'button'" in migration, 'migration requires button node type')
req("(string) ($node['props']['placementMode'] ?? 'normal') !== 'normal'" in migration, 'migration changes only still-normal converter buttons')
req("$node['props']['placementMode'] = 'overlay';" in migration, 'migration converts matching buttons to overlay')
req('LayoutModel::saveVersion(' in migration, 'active layout migration creates a Designer version')
req('update_post_meta($postId, self::BACKUP_META, $raw);' in migration, 'raw active layout is backed up before migration')
req('PageConversionService::CANDIDATE_META' in migration and '$candidateChanged' in migration, 'pending conversion candidates are repaired too')
req("metadata_exists('post', $postId, self::MARKER_META)" in migration, 'migration is guarded by a per-page one-time marker')

versions = history.get('versions', []) if isinstance(history, dict) else []
req(bool(versions) and isinstance(versions[0], dict) and str(versions[0].get('version', '')) == '0.1.82', 'release history starts with v0.1.82')
req('VD-CONVERTED-BUTTON-FLOATING-001' in json.dumps(history, ensure_ascii=False), 'release history records converted button repair')
req('data-version="0.1.82"' in notes and 'Konverterede knapper' in notes, 'release notes document v0.1.82 button migration')
req('**Aktuel release:** v0.1.82' in backlog and 'VD-CONVERTED-BUTTON-FLOATING-001' in backlog, 'canonical backlog records v0.1.82')
req((ROOT / 'docs/v0182-status.md').is_file(), 'v0.1.82 status document exists')

# Pre-release boundary: current updater stays on last verified package until the
# central release workflow publishes v0.1.82.
req(str(manifest.get('version', '')) == '0.1.81', 'pre-release updater manifest remains on verified v0.1.81')
req((ROOT / 'dist/visual-designer-manager-v0.1.81.zip').is_file(), 'verified v0.1.81 ZIP remains present before v0.1.82 release')

print('Visual Designer Manager v0.1.82 converted button static QA: PASS')
