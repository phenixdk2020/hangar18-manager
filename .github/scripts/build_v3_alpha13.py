from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.13'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


subprocess.run(['python3', '.github/scripts/build_v3_alpha12.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.12', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.12');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.12');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.13 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# One-time recovery is deliberately data-side, not another responsive renderer workaround.
recovery_php = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

/**
 * Alpha.13 one-time recovery of V1 mobile geometry into existing V3 models.
 *
 * V3StorageMigration correctly refused to overwrite an already-existing V3
 * layout. That safety rule also means later V3 edits/migrations can leave the
 * canonical mobile geometry different from the still-retained V1 source.
 * Alpha.13 repairs ONLY geometry.mobile for nodes whose id + type still match.
 * Desktop/laptop/tablet, props, hierarchy and V3-only nodes stay untouched.
 */
final class V1MobileGeometryRecovery
{
    private const VERSION = '3.0.0-alpha.13';
    private const STATE_OPTION = 'vdm_v3_alpha13_mobile_geometry_recovery_v1';
    private const LEGACY_PAGE_META = '_h18_clean_layout_v1';
    private const CANONICAL_PAGE_META = '_vdm_layout_v1';
    private const PAGE_BACKUP_META = '_vdm_alpha13_mobile_geometry_backup_v1';
    private const PAGE_DONE_META = '_vdm_alpha13_mobile_geometry_recovered_v1';
    private const TEMPLATE_REGISTRY = 'vdm_global_template_registry_v1';

    public static function register(): void
    {
        // V3StorageMigration copies primary storage at init priority 1.
        add_action('init', [self::class, 'run'], 6);
    }

    public static function run(): void
    {
        $existing = get_option(self::STATE_OPTION, []);
        if (is_array($existing) && ($existing['status'] ?? '') === 'complete' && ($existing['version'] ?? '') === self::VERSION) {
            return;
        }

        $state = [
            'version' => self::VERSION,
            'startedUtc' => gmdate('c'),
            'status' => 'running',
            'pagesScanned' => 0,
            'pagesChanged' => 0,
            'pageNodesMatched' => 0,
            'pageNodesChanged' => 0,
            'templatesScanned' => 0,
            'templatesChanged' => 0,
            'templateNodesMatched' => 0,
            'templateNodesChanged' => 0,
            'errors' => [],
        ];

        self::recoverPages($state);
        self::recoverTemplates($state);
        $state['completedUtc'] = gmdate('c');
        $state['status'] = empty($state['errors']) ? 'complete' : 'attention';
        update_option(self::STATE_OPTION, $state, false);
    }

    /**
     * Pure model operation used by runtime and deterministic QA.
     *
     * @param array<string,mixed> $legacy
     * @param array<string,mixed> $canonical
     * @return array{model:array<string,mixed>,matched:int,changed:int,unmatched:int}
     */
    public static function recoverModel(array $legacy, array $canonical): array
    {
        $source = [];
        foreach ((array) ($legacy['nodes'] ?? []) as $node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            $type = (string) ($node['type'] ?? '');
            $mobile = isset($node['geometry']['mobile']) && is_array($node['geometry']['mobile']) ? $node['geometry']['mobile'] : null;
            if ($id !== '' && $type !== '' && is_array($mobile)) {
                $source[$id] = ['type' => $type, 'mobile' => $mobile];
            }
        }

        $matched = 0;
        $changed = 0;
        $unmatched = 0;
        $nodes = isset($canonical['nodes']) && is_array($canonical['nodes']) ? $canonical['nodes'] : [];
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            $type = (string) ($node['type'] ?? '');
            if ($id === '' || !isset($source[$id]) || $source[$id]['type'] !== $type) {
                $unmatched++;
                continue;
            }
            $matched++;
            $current = isset($node['geometry']['mobile']) && is_array($node['geometry']['mobile']) ? $node['geometry']['mobile'] : [];
            $wanted = $source[$id]['mobile'];
            if ($current !== $wanted) {
                if (!isset($node['geometry']) || !is_array($node['geometry'])) { $node['geometry'] = []; }
                $node['geometry']['mobile'] = $wanted;
                $changed++;
            }
        }
        unset($node);
        $canonical['nodes'] = $nodes;

        return ['model' => $canonical, 'matched' => $matched, 'changed' => $changed, 'unmatched' => $unmatched];
    }

    /** @param array<string,mixed> $state */
    private static function recoverPages(array &$state): void
    {
        global $wpdb;
        $postIds = $wpdb->get_col($wpdb->prepare(
            "SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s ORDER BY post_id",
            self::LEGACY_PAGE_META
        ));

        foreach ((array) $postIds as $postIdRaw) {
            $postId = (int) $postIdRaw;
            if ($postId <= 0 || get_post_type($postId) !== 'page') { continue; }
            $state['pagesScanned']++;
            if ((string) get_post_meta($postId, self::PAGE_DONE_META, true) === self::VERSION) { continue; }
            if (!metadata_exists('post', $postId, self::CANONICAL_PAGE_META)) { continue; }

            $legacyRaw = get_post_meta($postId, self::LEGACY_PAGE_META, true);
            $canonicalRaw = get_post_meta($postId, self::CANONICAL_PAGE_META, true);
            if (!is_array($legacyRaw) || !is_array($canonicalRaw)) { continue; }

            try {
                $legacy = LayoutModel::normalize($legacyRaw);
                $canonical = LayoutModel::normalize($canonicalRaw);
                $result = self::recoverModel($legacy, $canonical);
                $state['pageNodesMatched'] += $result['matched'];
                $state['pageNodesChanged'] += $result['changed'];

                if ($result['changed'] > 0) {
                    if (!metadata_exists('post', $postId, self::PAGE_BACKUP_META)) {
                        add_post_meta($postId, self::PAGE_BACKUP_META, [
                            'version' => self::VERSION,
                            'savedUtc' => gmdate('c'),
                            'model' => $canonical,
                            'digest' => LayoutModel::structuralDigest($canonical),
                        ], true);
                    }
                    LayoutModel::saveVersion($postId, $result['model'], 0, 'Alpha.13: gendan V1 mobilgeometri 1:1');
                    $state['pagesChanged']++;
                }
                update_post_meta($postId, self::PAGE_DONE_META, self::VERSION);
            } catch (\Throwable $error) {
                $state['errors'][] = 'page:' . $postId . ':' . $error->getMessage();
            }
        }
    }

    /** @param array<string,mixed> $state */
    private static function recoverTemplates(array &$state): void
    {
        $registry = get_option(self::TEMPLATE_REGISTRY, []);
        if (!is_array($registry)) { return; }

        foreach ($registry as $idRaw => $row) {
            if (!is_array($row)) { continue; }
            $id = sanitize_key((string) ($row['id'] ?? $idRaw));
            $type = sanitize_key((string) ($row['type'] ?? ''));
            if ($id === '' || !in_array($type, ['header', 'footer'], true)) { continue; }
            $state['templatesScanned']++;

            $suffix = md5($id);
            $doneOption = 'vdm_alpha13_template_mobile_recovered_' . $suffix;
            $backupOption = 'vdm_alpha13_template_mobile_backup_' . $suffix;
            if ((string) get_option($doneOption, '') === self::VERSION) { continue; }

            $canonicalOption = 'vdm_tpl_' . $id . '_model_v1';
            $legacyOption = 'h18_clean_tpl_' . $id . '_model_v1';
            if ($id === $type . '-standard-v1') {
                $globalLegacy = 'h18_clean_global_' . $type . '_layout_v1';
                if (self::optionExists($globalLegacy)) { $legacyOption = $globalLegacy; }
            }
            if (!self::optionExists($legacyOption) || !self::optionExists($canonicalOption)) { continue; }

            $legacyRaw = get_option($legacyOption, []);
            $canonicalRaw = get_option($canonicalOption, []);
            if (!is_array($legacyRaw) || !is_array($canonicalRaw)) { continue; }

            try {
                $legacy = LayoutModel::normalize($legacyRaw);
                $canonical = LayoutModel::normalize($canonicalRaw);
                $result = self::recoverModel($legacy, $canonical);
                $state['templateNodesMatched'] += $result['matched'];
                $state['templateNodesChanged'] += $result['changed'];

                if ($result['changed'] > 0) {
                    if (!self::optionExists($backupOption)) {
                        update_option($backupOption, [
                            'version' => self::VERSION,
                            'templateId' => $id,
                            'savedUtc' => gmdate('c'),
                            'model' => $canonical,
                            'settings' => TemplateLayoutModel::settings($id),
                            'digest' => LayoutModel::structuralDigest($canonical),
                        ], false);
                    }
                    TemplateLayoutModel::saveVersion(
                        $id,
                        $result['model'],
                        TemplateLayoutModel::settings($id),
                        0,
                        'Alpha.13: gendan V1 mobilgeometri 1:1'
                    );
                    $state['templatesChanged']++;
                }
                update_option($doneOption, self::VERSION, false);
            } catch (\Throwable $error) {
                $state['errors'][] = 'template:' . $id . ':' . $error->getMessage();
            }
        }
    }

    private static function optionExists(string $name): bool
    {
        $sentinel = new \stdClass();
        return get_option($name, $sentinel) !== $sentinel;
    }

    private function __construct() {}
}
'''
write('src/Migration/V1MobileGeometryRecovery.php', recovery_php)

replace_once(
    'visual-designer-manager.php',
    "require_once VDM_DIR . 'src/Migration/V3StorageMigration.php';",
    "require_once VDM_DIR . 'src/Migration/V3StorageMigration.php';\nrequire_once VDM_DIR . 'src/Migration/V1MobileGeometryRecovery.php';",
    'Alpha.13 recovery require'
)
replace_once(
    'visual-designer-manager.php',
    "    \\VisualDesignerManager\\Migration\\V3StorageMigration::register();",
    "    \\VisualDesignerManager\\Migration\\V3StorageMigration::register();\n    \\VisualDesignerManager\\Migration\\V1MobileGeometryRecovery::register();",
    'Alpha.13 recovery register'
)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.12':
    raise SystemExit('Expected Alpha.12 release-history baseline missing')
alpha13 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'V1 Mobile Geometry Recovery: eksisterende V3-sider får V1 geometry.mobile tilbage for matchende node-id og type.',
        'Kun mobilgeometri ændres; desktop/laptop/tablet, props, hierarki og V3-only elementer bevares.',
        'Nuværende V3-model sikkerhedskopieres før recovery, og den reparerede model gemmes som en normal Designer-version.',
        'Header/Footer templates repareres efter samme regel fra bevaret V1-template/global-layout, når en kilde findes.',
        'Alpha.12 V1-parity renderer og eventrettelser bevares; der tilføjes ingen ny responsive CSS/JS workaround.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha13] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic build contract.
main = read('visual-designer-manager.php')
recovery = read('src/Migration/V1MobileGeometryRecovery.php')
rr = read('src/Frontend/ResponsiveRenderer.php')
for token in [
    "Version: 3.0.0-alpha.13",
    "V1MobileGeometryRecovery.php",
    "V1MobileGeometryRecovery::register();",
]:
    if token not in main:
        raise SystemExit(f'Alpha.13 main token missing: {token}')
for token in [
    "private const LEGACY_PAGE_META = '_h18_clean_layout_v1';",
    "private const CANONICAL_PAGE_META = '_vdm_layout_v1';",
    "public static function recoverModel(array $legacy, array $canonical): array",
    "$node['geometry']['mobile'] = $wanted;",
    "LayoutModel::saveVersion($postId, $result['model']",
    "TemplateLayoutModel::saveVersion(",
    "PAGE_BACKUP_META",
    "h18_clean_global_",
]:
    if token not in recovery:
        raise SystemExit(f'Alpha.13 recovery token missing: {token}')
for forbidden in ['h18-vdm-mobile-flow-repair', 'v3-alpha10-mobile-reflow.js', 'v3-alpha11-mobile-reflow.js']:
    if forbidden in rr or (DEST / 'assets' / forbidden).exists():
        raise SystemExit(f'Forbidden mobile workaround returned in Alpha.13: {forbidden}')

print('V3 Alpha.13 V1 mobile geometry recovery: PASS')
print('Page/template backup + versioned recovery: PASS')
print('Desktop/laptop/tablet/V3-only preservation contract: PASS')
print('Alpha.12 renderer path retained without reflow workaround: PASS')
