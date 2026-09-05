from pathlib import Path
import hashlib
import shutil

VERSION = '3.0.0-alpha.3'
SOURCE = Path('clean/hangar18-manager')
DEST = Path('build/visual-designer-manager')

TOKEN_MAP = {
    'H18_CLEAN_VERSION': 'VDM_VERSION',
    'H18_CLEAN_FILE': 'VDM_FILE',
    'H18_CLEAN_DIR': 'VDM_DIR',
    'H18_CLEAN_URL': 'VDM_URL',
}

# Only active V1 content/design storage is canonicalized in Alpha.3.
# Operational action/nonces, diagnostics, update caches and historical migration
# markers deliberately remain untouched until the imported site is accepted.
STORAGE_MAP = {
    'h18_clean_navigation_history_v1': 'vdm_navigation_history_v1',
    'h18_vehicle_fields_v1': 'vdm_vehicle_fields_v1',
    'h18_event_fields_v1': 'vdm_event_fields_v1',
    'h18_clean_global_template_registry_v1': 'vdm_global_template_registry_v1',
    'h18_clean_global_template_defaults_v1': 'vdm_global_template_defaults_v1',
    'h18_clean_global_template_migrated_v1': 'vdm_global_template_migrated_v1',
    'h18_clean_tpl_': 'vdm_tpl_',
    '_h18_clean_header_template_v1': '_vdm_header_template_v1',
    '_h18_clean_footer_template_v1': '_vdm_footer_template_v1',
    '_h18_clean_layout_v1': '_vdm_layout_v1',
    '_h18_clean_layout_version_v1': '_vdm_layout_version_v1',
    '_h18_clean_layout_history_v1': '_vdm_layout_history_v1',
    '_h18_vd_module_design_v1': '_vdm_module_design_v1',
    '_h18_vd_module_design_history_v1': '_vdm_module_design_history_v1',
    'h18_module_item': 'vdm_module_item',
    '_h18_module_key': '_vdm_module_key',
    '_h18_module_record_v1': '_vdm_module_record_v1',
    '_h18_module_record_id': '_vdm_module_record_id',
    '_h18_module_digest': '_vdm_module_digest',
    '_h18_module_status': '_vdm_module_status',
    '_h18_module_sort_order': '_vdm_module_sort_order',
}

UPDATER_REPLACEMENTS = {
    "private const MANIFEST_URL = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/main/clean-update.json';":
        "private const MANIFEST_URL = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json';",
    "private const SLUG = 'hangar18-manager';":
        "private const SLUG = 'visual-designer-manager';",
    "private const PLUGIN_FILE = 'hangar18-manager/hangar18-manager.php';":
        "private const PLUGIN_FILE = 'visual-designer-manager/visual-designer-manager.php';",
    "'User-Agent' => 'Hangar18-Manager-Clean/' . VDM_VERSION,":
        "'User-Agent' => 'Visual-Designer-Manager-V3/' . VDM_VERSION,",
    "'hangar18-manager/' . str_replace('\\\\', '/', $relative)":
        "'visual-designer-manager/' . str_replace('\\\\', '/', $relative)",
}

MIGRATION_PHP = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

/**
 * V3 Alpha.3 copy-and-verify migration for active V1 content/design storage.
 *
 * Safety rules:
 * - legacy values are never deleted or overwritten;
 * - canonical values are written only when absent;
 * - pre-existing canonical values must be byte-equivalent after serialization;
 * - module posts are duplicated, never converted in place;
 * - the migration is idempotent and records a verification report.
 */
final class V3StorageMigration
{
    private const VERSION = '3.0.0-alpha.3';
    private const STATE_OPTION = 'vdm_v3_storage_migration_v1';
    private const BACKUP_OPTION = 'vdm_v3_storage_backup_manifest_v1';
    private const LEGACY_MODULE_POST_TYPE = 'h18_module_item';
    private const CANONICAL_MODULE_POST_TYPE = 'vdm_module_item';

    /** @var array<string,string> */
    private const OPTION_MAP = [
        'h18_clean_navigation_history_v1' => 'vdm_navigation_history_v1',
        'h18_vehicle_fields_v1' => 'vdm_vehicle_fields_v1',
        'h18_event_fields_v1' => 'vdm_event_fields_v1',
        'h18_clean_global_template_registry_v1' => 'vdm_global_template_registry_v1',
        'h18_clean_global_template_defaults_v1' => 'vdm_global_template_defaults_v1',
        'h18_clean_global_template_migrated_v1' => 'vdm_global_template_migrated_v1',
    ];

    /** @var array<string,string> */
    private const META_MAP = [
        '_h18_clean_header_template_v1' => '_vdm_header_template_v1',
        '_h18_clean_footer_template_v1' => '_vdm_footer_template_v1',
        '_h18_clean_layout_v1' => '_vdm_layout_v1',
        '_h18_clean_layout_version_v1' => '_vdm_layout_version_v1',
        '_h18_clean_layout_history_v1' => '_vdm_layout_history_v1',
        '_h18_vd_module_design_v1' => '_vdm_module_design_v1',
        '_h18_vd_module_design_history_v1' => '_vdm_module_design_history_v1',
        '_h18_module_key' => '_vdm_module_key',
        '_h18_module_record_v1' => '_vdm_module_record_v1',
        '_h18_module_record_id' => '_vdm_module_record_id',
        '_h18_module_digest' => '_vdm_module_digest',
        '_h18_module_status' => '_vdm_module_status',
        '_h18_module_sort_order' => '_vdm_module_sort_order',
    ];

    public static function register(): void
    {
        // Core option/post-meta storage must exist before the retained V1 migrations run.
        add_action('init', [self::class, 'migratePrimaryStorage'], 1);
        // ModuleStore registers the canonical post type at init priority 10.
        add_action('init', [self::class, 'migrateModulePosts'], 20);
    }

    public static function migratePrimaryStorage(): void
    {
        $state = self::state();
        if (($state['status'] ?? '') === 'complete' && ($state['version'] ?? '') === self::VERSION) {
            return;
        }

        if (!self::optionExists(self::BACKUP_OPTION)) {
            update_option(self::BACKUP_OPTION, self::backupManifest(), false);
        }

        $state = self::freshState($state);
        foreach (self::OPTION_MAP as $legacy => $canonical) {
            self::copyOption($legacy, $canonical, $state);
        }
        self::copyDynamicTemplateOptions($state);
        foreach (self::META_MAP as $legacy => $canonical) {
            self::copyPostMeta($legacy, $canonical, $state);
        }

        $state['status'] = 'primary-complete';
        $state['primaryCompletedUtc'] = gmdate('c');
        $state['verification']['primary'] = self::verifyPrimaryStorage();
        update_option(self::STATE_OPTION, $state, false);
    }

    public static function migrateModulePosts(): void
    {
        $state = self::state();
        if (($state['status'] ?? '') === 'complete' && ($state['version'] ?? '') === self::VERSION) {
            return;
        }
        if (($state['status'] ?? '') !== 'primary-complete') {
            self::migratePrimaryStorage();
            $state = self::state();
        }

        self::copyModulePosts($state);
        $state['verification']['primary'] = self::verifyPrimaryStorage();
        $state['verification']['modules'] = self::verifyModulePosts();
        $state['completedUtc'] = gmdate('c');
        $state['status'] = empty($state['conflicts'])
            && !empty($state['verification']['primary']['ok'])
            && !empty($state['verification']['modules']['ok'])
            ? 'complete'
            : 'attention';
        update_option(self::STATE_OPTION, $state, false);
    }

    /** @return array<string,mixed> */
    public static function report(): array
    {
        return self::state();
    }

    /** @param array<string,mixed> $existing @return array<string,mixed> */
    private static function freshState(array $existing): array
    {
        return [
            'version' => self::VERSION,
            'sourceVersion' => '0.1.93',
            'startedUtc' => (string) ($existing['startedUtc'] ?? gmdate('c')),
            'status' => 'running',
            'copiedOptions' => (int) ($existing['copiedOptions'] ?? 0),
            'reusedOptions' => (int) ($existing['reusedOptions'] ?? 0),
            'copiedMetaRows' => (int) ($existing['copiedMetaRows'] ?? 0),
            'reusedMetaRows' => (int) ($existing['reusedMetaRows'] ?? 0),
            'copiedModulePosts' => (int) ($existing['copiedModulePosts'] ?? 0),
            'reusedModulePosts' => (int) ($existing['reusedModulePosts'] ?? 0),
            'modulePostMap' => is_array($existing['modulePostMap'] ?? null) ? $existing['modulePostMap'] : [],
            'conflicts' => is_array($existing['conflicts'] ?? null) ? $existing['conflicts'] : [],
            'verification' => is_array($existing['verification'] ?? null) ? $existing['verification'] : [],
            'legacyDataRetained' => true,
        ];
    }

    /** @param array<string,mixed> $state */
    private static function copyOption(string $legacy, string $canonical, array &$state): void
    {
        if (!self::optionExists($legacy)) {
            return;
        }
        $legacyValue = get_option($legacy);
        if (!self::optionExists($canonical)) {
            update_option($canonical, $legacyValue, false);
            $state['copiedOptions']++;
            return;
        }
        if (self::digest(get_option($canonical)) === self::digest($legacyValue)) {
            $state['reusedOptions']++;
            return;
        }
        self::conflict($state, 'option', $legacy, $canonical);
    }

    /** @param array<string,mixed> $state */
    private static function copyDynamicTemplateOptions(array &$state): void
    {
        global $wpdb;
        $prefix = 'h18_clean_tpl_';
        $like = $wpdb->esc_like($prefix) . '%';
        $names = $wpdb->get_col($wpdb->prepare(
            "SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_name",
            $like
        ));
        foreach ((array) $names as $legacy) {
            $legacy = (string) $legacy;
            if (!str_starts_with($legacy, $prefix)) {
                continue;
            }
            $canonical = 'vdm_tpl_' . substr($legacy, strlen($prefix));
            self::copyOption($legacy, $canonical, $state);
        }
    }

    /** @param array<string,mixed> $state */
    private static function copyPostMeta(string $legacy, string $canonical, array &$state): void
    {
        global $wpdb;
        $postIds = $wpdb->get_col($wpdb->prepare(
            "SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s ORDER BY post_id",
            $legacy
        ));
        foreach ((array) $postIds as $postIdRaw) {
            $postId = (int) $postIdRaw;
            if ($postId <= 0) {
                continue;
            }
            $legacyValue = get_post_meta($postId, $legacy, true);
            if (!metadata_exists('post', $postId, $canonical)) {
                update_post_meta($postId, $canonical, $legacyValue);
                $state['copiedMetaRows']++;
                continue;
            }
            if (self::digest(get_post_meta($postId, $canonical, true)) === self::digest($legacyValue)) {
                $state['reusedMetaRows']++;
                continue;
            }
            self::conflict($state, 'post-meta:' . $postId, $legacy, $canonical);
        }
    }

    /** @param array<string,mixed> $state */
    private static function copyModulePosts(array &$state): void
    {
        global $wpdb;
        $legacyIds = $wpdb->get_col($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE post_type = %s AND post_status <> 'trash' ORDER BY ID",
            self::LEGACY_MODULE_POST_TYPE
        ));

        foreach ((array) $legacyIds as $legacyIdRaw) {
            $legacyId = (int) $legacyIdRaw;
            $source = get_post($legacyId);
            if (!$source instanceof \WP_Post) {
                continue;
            }
            $recordId = trim((string) get_post_meta($legacyId, '_h18_module_record_id', true));
            if ($recordId === '') {
                $raw = (string) get_post_meta($legacyId, '_h18_module_record_v1', true);
                $decoded = $raw !== '' ? json_decode($raw, true) : null;
                $recordId = is_array($decoded) ? trim((string) ($decoded['id'] ?? '')) : '';
            }
            if ($recordId === '') {
                self::conflict($state, 'module-post:' . $legacyId, 'missing-record-id', 'not-copied');
                continue;
            }

            $existingIds = get_posts([
                'post_type' => self::CANONICAL_MODULE_POST_TYPE,
                'post_status' => 'publish',
                'fields' => 'ids',
                'posts_per_page' => 1,
                'no_found_rows' => true,
                'suppress_filters' => true,
                'meta_query' => [[
                    'key' => '_vdm_module_record_id',
                    'value' => $recordId,
                    'compare' => '=',
                ]],
            ]);
            if (is_array($existingIds) && $existingIds) {
                $targetId = (int) $existingIds[0];
                if (self::modulePostEquivalent($legacyId, $targetId)) {
                    $state['reusedModulePosts']++;
                    $state['modulePostMap'][(string) $legacyId] = $targetId;
                } else {
                    self::conflict($state, 'module-post:' . $legacyId, $recordId, 'canonical-record-differs');
                }
                continue;
            }

            $targetId = wp_insert_post([
                'post_type' => self::CANONICAL_MODULE_POST_TYPE,
                'post_status' => 'publish',
                'post_author' => (int) $source->post_author,
                'post_date' => (string) $source->post_date,
                'post_date_gmt' => (string) $source->post_date_gmt,
                'post_content' => (string) $source->post_content,
                'post_title' => (string) $source->post_title,
                'post_excerpt' => (string) $source->post_excerpt,
                'post_name' => (string) $source->post_name,
                'menu_order' => (int) $source->menu_order,
            ], true);
            if (is_wp_error($targetId)) {
                self::conflict($state, 'module-post:' . $legacyId, $recordId, $targetId->get_error_message());
                continue;
            }
            $targetId = (int) $targetId;
            foreach (self::META_MAP as $legacyMeta => $canonicalMeta) {
                if (!metadata_exists('post', $legacyId, $legacyMeta)) {
                    continue;
                }
                update_post_meta($targetId, $canonicalMeta, get_post_meta($legacyId, $legacyMeta, true));
            }
            $state['copiedModulePosts']++;
            $state['modulePostMap'][(string) $legacyId] = $targetId;
        }
    }

    private static function modulePostEquivalent(int $legacyId, int $canonicalId): bool
    {
        foreach (self::META_MAP as $legacyMeta => $canonicalMeta) {
            if (!str_starts_with($legacyMeta, '_h18_module_')) {
                continue;
            }
            $legacyExists = metadata_exists('post', $legacyId, $legacyMeta);
            $canonicalExists = metadata_exists('post', $canonicalId, $canonicalMeta);
            if ($legacyExists !== $canonicalExists) {
                return false;
            }
            if ($legacyExists && self::digest(get_post_meta($legacyId, $legacyMeta, true)) !== self::digest(get_post_meta($canonicalId, $canonicalMeta, true))) {
                return false;
            }
        }
        return true;
    }

    /** @return array<string,mixed> */
    private static function backupManifest(): array
    {
        global $wpdb;
        $options = [];
        foreach (self::OPTION_MAP as $legacy => $canonical) {
            if (self::optionExists($legacy)) {
                $options[$legacy] = ['target' => $canonical, 'digest' => self::digest(get_option($legacy))];
            }
        }
        $prefix = 'h18_clean_tpl_';
        $like = $wpdb->esc_like($prefix) . '%';
        foreach ((array) $wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_name", $like)) as $name) {
            $name = (string) $name;
            $options[$name] = ['target' => 'vdm_tpl_' . substr($name, strlen($prefix)), 'digest' => self::digest(get_option($name))];
        }

        $meta = [];
        foreach (self::META_MAP as $legacy => $canonical) {
            $ids = array_map('intval', (array) $wpdb->get_col($wpdb->prepare("SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s ORDER BY post_id", $legacy)));
            $parts = [];
            foreach ($ids as $id) {
                $parts[] = $id . ':' . self::digest(get_post_meta($id, $legacy, true));
            }
            $meta[$legacy] = [
                'target' => $canonical,
                'count' => count($ids),
                'digest' => hash('sha256', implode('|', $parts)),
            ];
        }

        $moduleIds = array_map('intval', (array) $wpdb->get_col($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE post_type = %s AND post_status <> 'trash' ORDER BY ID",
            self::LEGACY_MODULE_POST_TYPE
        )));

        return [
            'createdUtc' => gmdate('c'),
            'sourceVersion' => '0.1.93',
            'targetVersion' => self::VERSION,
            'strategy' => 'copy-and-verify; legacy data retained in place',
            'options' => $options,
            'postMeta' => $meta,
            'legacyModulePostIds' => $moduleIds,
            'legacyModulePostCount' => count($moduleIds),
        ];
    }

    /** @return array{ok:bool,checked:int,failed:array<int,string>} */
    private static function verifyPrimaryStorage(): array
    {
        global $wpdb;
        $checked = 0;
        $failed = [];
        foreach (self::OPTION_MAP as $legacy => $canonical) {
            if (!self::optionExists($legacy)) {
                continue;
            }
            $checked++;
            if (!self::optionExists($canonical) || self::digest(get_option($legacy)) !== self::digest(get_option($canonical))) {
                $failed[] = 'option:' . $legacy;
            }
        }
        $prefix = 'h18_clean_tpl_';
        $like = $wpdb->esc_like($prefix) . '%';
        foreach ((array) $wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_name", $like)) as $legacy) {
            $legacy = (string) $legacy;
            $canonical = 'vdm_tpl_' . substr($legacy, strlen($prefix));
            $checked++;
            if (!self::optionExists($canonical) || self::digest(get_option($legacy)) !== self::digest(get_option($canonical))) {
                $failed[] = 'option:' . $legacy;
            }
        }
        foreach (self::META_MAP as $legacy => $canonical) {
            $ids = $wpdb->get_col($wpdb->prepare("SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s ORDER BY post_id", $legacy));
            foreach ((array) $ids as $idRaw) {
                $id = (int) $idRaw;
                $checked++;
                if (!metadata_exists('post', $id, $canonical) || self::digest(get_post_meta($id, $legacy, true)) !== self::digest(get_post_meta($id, $canonical, true))) {
                    $failed[] = 'post-meta:' . $id . ':' . $legacy;
                }
            }
        }
        return ['ok' => !$failed, 'checked' => $checked, 'failed' => $failed];
    }

    /** @return array{ok:bool,legacy:int,matched:int,failed:array<int,string>} */
    private static function verifyModulePosts(): array
    {
        global $wpdb;
        $legacyIds = array_map('intval', (array) $wpdb->get_col($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE post_type = %s AND post_status <> 'trash' ORDER BY ID",
            self::LEGACY_MODULE_POST_TYPE
        )));
        $matched = 0;
        $failed = [];
        foreach ($legacyIds as $legacyId) {
            $recordId = trim((string) get_post_meta($legacyId, '_h18_module_record_id', true));
            if ($recordId === '') {
                $raw = (string) get_post_meta($legacyId, '_h18_module_record_v1', true);
                $decoded = $raw !== '' ? json_decode($raw, true) : null;
                $recordId = is_array($decoded) ? trim((string) ($decoded['id'] ?? '')) : '';
            }
            if ($recordId === '') {
                $failed[] = 'missing-record-id:' . $legacyId;
                continue;
            }
            $ids = get_posts([
                'post_type' => self::CANONICAL_MODULE_POST_TYPE,
                'post_status' => 'publish',
                'fields' => 'ids',
                'posts_per_page' => 1,
                'no_found_rows' => true,
                'suppress_filters' => true,
                'meta_query' => [[
                    'key' => '_vdm_module_record_id',
                    'value' => $recordId,
                    'compare' => '=',
                ]],
            ]);
            if (!is_array($ids) || !$ids || !self::modulePostEquivalent($legacyId, (int) $ids[0])) {
                $failed[] = 'module-record:' . $legacyId . ':' . $recordId;
                continue;
            }
            $matched++;
        }
        return ['ok' => !$failed, 'legacy' => count($legacyIds), 'matched' => $matched, 'failed' => $failed];
    }

    private static function optionExists(string $name): bool
    {
        global $wpdb;
        return (int) $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name = %s", $name)) > 0;
    }

    private static function digest(mixed $value): string
    {
        return hash('sha256', serialize($value));
    }

    /** @param array<string,mixed> $state */
    private static function conflict(array &$state, string $scope, string $legacy, string $canonical): void
    {
        $key = $scope . '|' . $legacy . '|' . $canonical;
        $state['conflicts'][$key] = [
            'scope' => $scope,
            'legacy' => $legacy,
            'canonical' => $canonical,
        ];
    }

    /** @return array<string,mixed> */
    private static function state(): array
    {
        $raw = get_option(self::STATE_OPTION, []);
        return is_array($raw) ? $raw : [];
    }

    private function __construct() {}
}
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_php(text: str) -> str:
    for old, new in TOKEN_MAP.items():
        text = text.replace(old, new)
    for old, new in STORAGE_MAP.items():
        text = text.replace(old, new)
    return text


if DEST.parent.exists():
    shutil.rmtree(DEST.parent)
DEST.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(SOURCE, DEST)

old_main = DEST / 'hangar18-manager.php'
main = DEST / 'visual-designer-manager.php'
old_main.rename(main)

main_text = main.read_text(encoding='utf-8')
main_replacements = {
    ' * Version: 0.1.93': f' * Version: {VERSION}',
    "define('VDM_VERSION', '0.1.93');": f"define('VDM_VERSION', '{VERSION}');",
    "define('H18_CLEAN_VERSION', '0.1.93');": f"define('H18_CLEAN_VERSION', '{VERSION}');",
}
for old, new in main_replacements.items():
    if main_text.count(old) != 1:
        raise SystemExit(f'Main bootstrap token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)

require_anchor = "require_once VDM_DIR . 'src/Compatibility/LegacyStorageBridge.php';"
if main_text.count(require_anchor) != 1:
    raise SystemExit('V3 storage migration bootstrap require anchor mismatch')
main_text = main_text.replace(
    require_anchor,
    require_anchor + "\nrequire_once VDM_DIR . 'src/Migration/V3StorageMigration.php';",
)
register_anchor = "    \\VisualDesignerManager\\Modules\\ModuleStore::register();"
if main_text.count(register_anchor) != 1:
    raise SystemExit('V3 storage migration register anchor mismatch')
main_text = main_text.replace(
    register_anchor,
    "    \\VisualDesignerManager\\Migration\\V3StorageMigration::register();\n" + register_anchor,
)
main.write_text(main_text, encoding='utf-8')

for path in sorted(DEST.rglob('*.php')):
    if path == main:
        continue
    text = path.read_text(encoding='utf-8')
    transformed = transform_php(text)
    if path.relative_to(DEST).as_posix() == 'src/Update/GitHubUpdater.php':
        for old, new in UPDATER_REPLACEMENTS.items():
            if transformed.count(old) != 1:
                raise SystemExit(f'Updater token mismatch: {old!r} count={transformed.count(old)}')
            transformed = transformed.replace(old, new)
    path.write_text(transformed, encoding='utf-8')

migration_path = DEST / 'src/Migration/V3StorageMigration.php'
migration_path.write_text(MIGRATION_PHP, encoding='utf-8')

# Prove all retained runtime changes are deterministic: Alpha.2 constant normalization,
# the explicit Alpha.3 storage map, updater identity, bootstrap registration, and the one
# new migration class. No JS/CSS/renderer behavioral code may change.
failures = []
for src in sorted(p for p in SOURCE.rglob('*') if p.is_file()):
    rel = src.relative_to(SOURCE).as_posix()
    if rel == 'hangar18-manager.php':
        continue
    dst = DEST / rel
    if not dst.is_file():
        failures.append(f'missing: {rel}')
        continue
    if src.suffix.lower() == '.php':
        expected = transform_php(src.read_text(encoding='utf-8'))
        if rel == 'src/Update/GitHubUpdater.php':
            for old, new in UPDATER_REPLACEMENTS.items():
                expected = expected.replace(old, new)
        actual = dst.read_text(encoding='utf-8')
        if actual != expected:
            failures.append(f'non-approved PHP mutation: {rel}')
    elif sha(src) != sha(dst):
        failures.append(f'non-PHP runtime changed: {rel}')

source_files = {
    p.relative_to(SOURCE).as_posix()
    for p in SOURCE.rglob('*') if p.is_file() and p.relative_to(SOURCE).as_posix() != 'hangar18-manager.php'
}
dest_files = {
    p.relative_to(DEST).as_posix()
    for p in DEST.rglob('*') if p.is_file() and p.relative_to(DEST).as_posix() not in {'visual-designer-manager.php', 'src/Migration/V3StorageMigration.php'}
}
for rel in sorted(source_files - dest_files):
    failures.append(f'missing expected runtime file: {rel}')
for rel in sorted(dest_files - source_files):
    failures.append(f'extra runtime file: {rel}')

if failures:
    print('V3 Alpha.3 deterministic transform: FAIL')
    for failure in failures:
        print(' -', failure)
    raise SystemExit(1)

# Active content models must point only at canonical storage after the transform.
required_canonical = {
    'src/Model/LayoutModel.php': ['_vdm_layout_v1', '_vdm_layout_version_v1', '_vdm_layout_history_v1'],
    'src/Model/TemplateLayoutModel.php': ['vdm_global_template_registry_v1', 'vdm_global_template_defaults_v1', 'vdm_tpl_', '_vdm_header_template_v1', '_vdm_footer_template_v1'],
    'src/Model/ModuleDesignModel.php': ['_vdm_module_design_v1', '_vdm_module_design_history_v1'],
    'src/Modules/ModuleStore.php': ['vdm_module_item', '_vdm_module_record_v1', '_vdm_module_record_id'],
    'src/Modules/VehicleFieldRegistry.php': ['vdm_vehicle_fields_v1'],
    'src/Modules/EventFieldRegistry.php': ['vdm_event_fields_v1'],
    'src/Admin/NavigationController.php': ['vdm_navigation_history_v1'],
    'src/Compatibility/LegacyStorageBridge.php': ['vdm_global_template_registry_v1', 'vdm_global_template_defaults_v1', 'vdm_tpl_'],
}
for rel, needles in required_canonical.items():
    text = (DEST / rel).read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'Canonical storage token missing: {rel}: {needle}')

# The only intentional references to the migrated legacy storage names are the
# copy source keys in V3StorageMigration.php itself.
for rel in required_canonical:
    text = (DEST / rel).read_text(encoding='utf-8')
    for legacy in STORAGE_MAP:
        if legacy in text:
            raise SystemExit(f'Legacy active storage token remains after transform: {rel}: {legacy}')

if "copy-and-verify" not in MIGRATION_PHP or "legacyDataRetained" not in MIGRATION_PHP:
    raise SystemExit('Migration safety contract missing')
if "add_action('init', [self::class, 'migratePrimaryStorage'], 1);" not in MIGRATION_PHP:
    raise SystemExit('Early primary migration hook missing')
if "add_action('init', [self::class, 'migrateModulePosts'], 20);" not in MIGRATION_PHP:
    raise SystemExit('Module migration hook missing')
if 'delete_option(' in MIGRATION_PHP or 'delete_post_meta(' in MIGRATION_PHP or 'wp_delete_post(' in MIGRATION_PHP:
    raise SystemExit('Destructive operation found in V3 storage migration')

print('V3 Alpha.3 deterministic transform: PASS')
print('Canonical active content/design storage: PASS')
print('Copy-and-verify migration with retained V1 data: PASS')
print('Designer/JS/CSS/non-storage runtime preservation: PASS')
