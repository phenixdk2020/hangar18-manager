from pathlib import Path
import json

ROOT = Path('.')


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Version + migration bootstrap
# -----------------------------------------------------------------------------
plugin_path = 'clean/hangar18-manager/hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.81', ' * Version: 0.1.82', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.81');", "define('H18_CLEAN_VERSION', '0.1.82');", 'runtime version')

require_anchor = "require_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';\n"
require_line = "require_once H18_CLEAN_DIR . 'src/Migration/ConvertedButtonOverlayMigration.php';\n"
if require_line not in plugin:
    plugin = replace_once(plugin, require_anchor, require_anchor + require_line, 'converted button migration require')

register_anchor = "    \\VisualDesignerManager\\Migration\\HybridModulePageMigration::register();\n"
register_line = "    \\VisualDesignerManager\\Migration\\ConvertedButtonOverlayMigration::register();\n"
if register_line not in plugin:
    plugin = replace_once(plugin, register_anchor, register_anchor + register_line, 'converted button migration register')
write(plugin_path, plugin)


# -----------------------------------------------------------------------------
# Future conversions: converted CTA/buttons use the same floating contract as a
# Button inserted directly in Visual Designer.
# -----------------------------------------------------------------------------
converter_path = 'clean/hangar18-manager/src/Migration/VisualBlockConversionService.php'
converter = read(converter_path)
converter = replace_once(
    converter,
    "                'placementMode' => 'normal', 'zIndex' => 20,",
    "                'placementMode' => 'overlay', 'zIndex' => 20,",
    'converted button placement mode'
)
write(converter_path, converter)


# -----------------------------------------------------------------------------
# Existing conversions: migrate only buttons whose immutable generated ID
# belongs to the exact stored external source snapshot for that page.
# -----------------------------------------------------------------------------
migration_path = 'clean/hangar18-manager/src/Migration/ConvertedButtonOverlayMigration.php'
migration = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

/**
 * v0.1.82 one-time repair for buttons created by VisualBlockConversionService.
 *
 * Converted button IDs contain an 8-character source suffix derived from the
 * page ID plus the immutable external source snapshot. That provenance lets us
 * repair only converter-owned buttons and leave ordinary Designer buttons
 * untouched.
 */
final class ConvertedButtonOverlayMigration
{
    public const MARKER_META = '_h18_vd_converted_button_overlay_v0182';
    public const BACKUP_META = '_h18_vd_converted_button_overlay_backup_v0182';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'migrateAll'], 20);
    }

    public static function migrateAll(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $ids = get_posts([
            'post_type' => 'page',
            'post_status' => 'any',
            'numberposts' => -1,
            'fields' => 'ids',
            'orderby' => 'ID',
            'order' => 'ASC',
            'meta_key' => PageConversionService::STATE_META,
        ]);
        if (!is_array($ids)) {
            return;
        }

        foreach ($ids as $id) {
            self::migratePage(absint($id));
        }
    }

    private static function migratePage(int $postId): void
    {
        if ($postId <= 0 || metadata_exists('post', $postId, self::MARKER_META)) {
            return;
        }

        $source = get_post_meta($postId, PageConversionService::SOURCE_META, true);
        $source = is_array($source) ? $source : [];
        $sourceType = sanitize_key((string) ($source['sourceType'] ?? ''));
        $sourceHtml = isset($source['sourceHtml']) && is_string($source['sourceHtml']) ? $source['sourceHtml'] : '';
        if ($sourceType !== 'external' || $sourceHtml === '') {
            self::mark($postId, 'not-applicable', 0, 0);
            return;
        }

        $suffix = substr(hash('sha256', (string) $postId . '|' . $sourceHtml), 0, 8);
        $activeChanged = 0;
        $candidateChanged = 0;

        if (metadata_exists('post', $postId, LayoutModel::META)) {
            $raw = get_post_meta($postId, LayoutModel::META, true);
            if (is_array($raw)) {
                $current = LayoutModel::normalize($raw);
                [$next, $activeChanged] = self::upgradeModelForConverter($current, $suffix);
                if ($activeChanged > 0) {
                    if (!metadata_exists('post', $postId, self::BACKUP_META)) {
                        update_post_meta($postId, self::BACKUP_META, $raw);
                    }
                    LayoutModel::saveVersion(
                        $postId,
                        $next,
                        max(0, get_current_user_id()),
                        'v0.1.82: konverterede knapper ændret til flydende Designer-knapper'
                    );
                }
            }
        }

        $candidate = get_post_meta($postId, PageConversionService::CANDIDATE_META, true);
        if (is_array($candidate)) {
            [$candidateNext, $candidateChanged] = self::upgradeModelForConverter(LayoutModel::normalize($candidate), $suffix);
            if ($candidateChanged > 0) {
                update_post_meta($postId, PageConversionService::CANDIDATE_META, LayoutModel::normalize($candidateNext));
            }
        }

        self::mark(
            $postId,
            ($activeChanged + $candidateChanged) > 0 ? 'migrated' : 'checked',
            $activeChanged,
            $candidateChanged
        );
    }

    /**
     * Pure migration kernel used by release QA as well as the WordPress pass.
     *
     * @param array<string,mixed> $model
     * @return array{0:array<string,mixed>,1:int}
     */
    public static function upgradeModelForConverter(array $model, string $suffix): array
    {
        if (!preg_match('/^[a-f0-9]{8}$/', $suffix)) {
            return [$model, 0];
        }
        if (!isset($model['nodes']) || !is_array($model['nodes'])) {
            return [$model, 0];
        }

        $prefix = 'button-' . $suffix . '-';
        $changed = 0;
        foreach ($model['nodes'] as &$node) {
            if (!is_array($node)
                || (string) ($node['type'] ?? '') !== 'button'
                || !str_starts_with((string) ($node['id'] ?? ''), $prefix)
                || !isset($node['props'])
                || !is_array($node['props'])
                || (string) ($node['props']['placementMode'] ?? 'normal') !== 'normal') {
                continue;
            }
            $node['props']['placementMode'] = 'overlay';
            $changed++;
        }
        unset($node);

        return [$model, $changed];
    }

    private static function mark(int $postId, string $status, int $activeChanged, int $candidateChanged): void
    {
        update_post_meta($postId, self::MARKER_META, [
            'version' => '0.1.82',
            'status' => sanitize_key($status),
            'activeChanged' => max(0, $activeChanged),
            'candidateChanged' => max(0, $candidateChanged),
            'migratedUtc' => gmdate('c'),
        ]);
    }

    private function __construct()
    {
    }
}
'''
write(migration_path, migration)


# -----------------------------------------------------------------------------
# Make the v0.1.81 historical gate forward-compatible now that v0.1.81 is a
# verified published baseline.
# -----------------------------------------------------------------------------
qa81_path = '.github/scripts/v0181_complete_qa.py'
qa81 = read(qa81_path)
old81 = """# Pre-release contract: updater stays on last verified release until central packaging runs.\nreq(str(manifest.get('version', '')) == '0.1.80', 'pre-release updater manifest remains on verified v0.1.80')\nreq((ROOT / 'dist/visual-designer-manager-v0.1.80.zip').is_file(), 'verified v0.1.80 ZIP remains present before v0.1.81 release')\n"""
new81 = """# Historical gate: v0.1.81 is now a verified published baseline.\nreq(tuple(map(int, str(manifest.get('version', '0.0.0')).split('.'))) >= (0, 1, 81), 'updater manifest is v0.1.81 or newer')\nreq((ROOT / 'dist/visual-designer-manager-v0.1.81.zip').is_file(), 'verified v0.1.81 ZIP remains present')\n"""
if old81 in qa81:
    qa81 = qa81.replace(old81, new81, 1)
elif 'updater manifest is v0.1.81 or newer' not in qa81:
    raise SystemExit('v0.1.81 QA forward-compatibility anchor not found')
write(qa81_path, qa81)


# -----------------------------------------------------------------------------
# Release metadata and documentation
# -----------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
if not isinstance(versions, list):
    raise SystemExit('release history versions is not a list')
if not any(isinstance(row, dict) and row.get('version') == '0.1.82' for row in versions):
    versions.insert(0, {
        'version': '0.1.82',
        'date': '2026-09-02',
        'items': [
            'VD-CONVERTED-BUTTON-FLOATING-001: knapper oprettet af sidekonverteringen bruger nu samme flydende overlay-kontrakt som nye Designer-knapper.',
            'Eksisterende eksternt konverterede sider migreres selektivt via deres deterministiske converter-ID; almindelige Designer-knapper ændres ikke.',
            'Aktive layouts får rå backup og ny LayoutModel-version før ændring; eksisterende konverteringskandidater repareres uden at godkende dem automatisk.',
            'Migrationen er idempotent og markerer hver konverteret side efter kontrol.'
        ]
    })
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes_path = 'clean-release-notes.html'
notes = read(notes_path)
section = '<section data-version="0.1.82"><h2>0.1.82</h2><ul><li>Konverterede knapper bliver nu flydende på samme måde som knapper, der indsættes direkte i Visual Designer.</li><li>Allerede konverterede sider repareres selektivt uden at ændre almindelige Designer-knapper.</li><li>Aktive layouts sikkerhedskopieres og versionsgemmes før migration.</li><li>Eksisterende konverteringskandidater repareres også, men godkendes ikke automatisk.</li></ul></section>\n'
if 'data-version="0.1.82"' not in notes:
    notes = section + notes
write(notes_path, notes)

backlog_path = 'docs/clean-backlog-v0100.md'
backlog = read(backlog_path)
backlog = backlog.replace('**Aktuel release:** v0.1.80', '**Aktuel release:** v0.1.82', 1)
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.79', '## Aktuel milepælsstatus · v0.1.82', 1)
marker = '- **VD-COMPOSABLE-MODULE-PAGES-002 — IMPLEMENTERET I v0.1.80:** collection-overskrifter og Eventdetaljens kernefelter er selvstændige Designer-elementer; Data-menuen er skjult.\n'
if 'VD-CONVERTED-BUTTON-FLOATING-001 — IMPLEMENTERET I v0.1.82' not in backlog:
    if marker in backlog:
        backlog = backlog.replace(marker, marker + '- **VD-CONVERTED-BUTTON-FLOATING-001 — IMPLEMENTERET I v0.1.82:** konverterede CTA-knapper følger samme flydende overlay-kontrakt som nye Designer-knapper, med selektiv migration og backup.\n', 1)
    roadmap = '12. **v0.1.80 – VD-COMPOSABLE-MODULE-PAGES-002 — FÆRDIG:** collection-overskrifter og Eventdetaljens kernefelter er selvstændige Designer-elementer; Data-menuen er skjult.\n'
    if roadmap in backlog:
        backlog = backlog.replace(roadmap, roadmap + '13. **v0.1.81 – Farvevælger + formularparitet — FÆRDIG:** fælles farvevælger, formular-preview og udvidet dokumentation.\n14. **v0.1.82 – VD-CONVERTED-BUTTON-FLOATING-001 — FÆRDIG:** konverterede knapper er flydende og eksisterende konverteringer migreres selektivt.\n', 1)
write(backlog_path, backlog)

status = '''# Visual Designer Manager v0.1.82 – status\n\n## Scope\n\n- `VisualBlockConversionService` opretter knapper med `placementMode = overlay`.\n- Ny selektiv migration reparerer allerede konverterede knapper, herunder sider som **Bliv medlem – kopi (ID 228)** når plugin-opdateringen kører på sitet.\n- Kun knapper med converterens deterministiske `button-<source-suffix>-...` ID ændres.\n- Almindelige Designer-knapper og allerede flydende knapper ændres ikke.\n- Aktive layouts får backup og en ny Designer-version før ændringen.\n- Pending konverteringskandidater repareres uden automatisk godkendelse.\n\n## Release gate\n\nRelease candidate; central ZIP/manifest-build kræves efter grøn QA.\n'''
write('docs/v0182-status.md', status)

print('Applied Visual Designer Manager v0.1.82 converted button overlay candidate.')
