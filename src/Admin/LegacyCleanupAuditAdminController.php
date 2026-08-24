<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/** Read-only installed-runtime audit for legacy bootstrap and retired simulation artifacts. */
final class LegacyCleanupAuditAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_notices', [self::class, 'render'], 80);
    }

    public static function render(): void
    {
        if (!current_user_can('manage_options')) {
            return;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-updates') {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $uploads = wp_upload_dir();
        $uploadDir = empty($uploads['error']) && !empty($uploads['basedir']) ? (string) $uploads['basedir'] : '';
        $sourceAudit = self::scanSource($pluginDir);
        $runtimeArtifacts = self::findArtifacts([$pluginDir, $uploadDir]);
        $options = self::optionAudit();

        echo '<div class="notice notice-info" style="padding:14px 16px;margin-top:16px">';
        echo '<h2 style="margin:0 0 8px">Cleanup-audit · read-only</h2>';
        echo '<p>Denne kontrol sletter eller ændrer <strong>intet</strong>. Den viser aktive legacy-runtime-referencer og installationsartefakter. Cleanup-panelets egne diagnostiktekster tælles ikke som aktiv runtime.</p>';
        echo '<table class="widefat striped" style="max-width:1150px"><tbody>';
        self::row('Aktive WhatIf runtime-referencer', (string) $sourceAudit['whatif_matches'], $sourceAudit['whatif_files'] . ' runtime-fil(er). For en fuldt migreret installation skal værdien være 0.');
        self::row('PowerShell .ps1', (string) count($runtimeArtifacts['powershell']), count($runtimeArtifacts['powershell']) ? implode(', ', array_slice($runtimeArtifacts['powershell'], 0, 5)) : 'Ingen fundet.');
        self::row('VehicleRegister/bootstrap JSON', (string) count($runtimeArtifacts['bootstrap']), count($runtimeArtifacts['bootstrap']) ? implode(', ', array_slice($runtimeArtifacts['bootstrap'], 0, 5)) : 'Ingen fil-artifacts fundet.');
        self::row('NoWhatIf kompatibilitetsshim', $sourceAudit['shim_present'] ? 'TIL STEDE' : 'FJERNET', $sourceAudit['shim_present'] ? 'Legacy shim findes stadig og skal fjernes sammen med den permanente source-migration.' : 'Controller og shim-assets er væk.');
        echo '</tbody></table>';

        echo '<h3>Legacy WordPress-options</h3><div style="overflow:auto"><table class="widefat striped" style="max-width:1150px"><thead><tr><th>Option</th><th>Status</th><th>Klassifikation</th></tr></thead><tbody>';
        foreach ($options as $item) {
            echo '<tr><td><code>' . esc_html($item['name']) . '</code></td><td>' . esc_html($item['exists'] ? 'Findes' : 'Findes ikke') . '</td><td>' . esc_html($item['classification']) . '</td></tr>';
        }
        echo '</tbody></table></div>';
        echo '<p><small>Audit-version 0.8.81 · ' . esc_html(gmdate('c')) . '</small></p></div>';
    }

    /** @return array<string,mixed> */
    private static function scanSource(string $root): array
    {
        $matches = 0;
        $files = 0;
        $shimPresent = false;
        $diagnosticPaths = [
            'src/Admin/LegacyCleanupAuditAdminController.php',
        ];
        $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($root, \FilesystemIterator::SKIP_DOTS));
        foreach ($iterator as $file) {
            if (!$file instanceof \SplFileInfo || !$file->isFile()) {
                continue;
            }
            $path = $file->getPathname();
            $relative = ltrim(str_replace('\\', '/', substr($path, strlen($root))), '/');
            if (preg_match('~^(?:dist|build|\.git)/~', $relative)) {
                continue;
            }
            if (str_contains($relative, 'NoWhatIfAdminController') || str_contains($relative, 'hangar18-no-whatif')) {
                $shimPresent = true;
            }
            $ext = strtolower($file->getExtension());
            if (!in_array($ext, ['php', 'js', 'css'], true) || in_array($relative, $diagnosticPaths, true)) {
                continue;
            }
            $content = @file_get_contents($path);
            if (!is_string($content)) {
                continue;
            }
            $count = preg_match_all('/whatif/i', $content, $unused);
            if ($count > 0) {
                $matches += $count;
                $files++;
            }
        }
        return ['whatif_matches' => $matches, 'whatif_files' => $files, 'shim_present' => $shimPresent];
    }

    /** @param array<int,string> $roots @return array<string,array<int,string>> */
    private static function findArtifacts(array $roots): array
    {
        $result = ['powershell' => [], 'bootstrap' => []];
        foreach ($roots as $root) {
            if ($root === '' || !is_dir($root)) {
                continue;
            }
            try {
                $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($root, \FilesystemIterator::SKIP_DOTS));
                foreach ($iterator as $file) {
                    if (!$file instanceof \SplFileInfo || !$file->isFile()) {
                        continue;
                    }
                    $name = $file->getFilename();
                    $path = $file->getPathname();
                    if (strtolower($file->getExtension()) === 'ps1') {
                        $result['powershell'][] = $path;
                    }
                    if (preg_match('/(?:VehicleRegister|vehicle[-_ ]?register|bootstrap).*\.json$/i', $name)) {
                        $result['bootstrap'][] = $path;
                    }
                    if (count($result['powershell']) >= 50 && count($result['bootstrap']) >= 50) {
                        break;
                    }
                }
            } catch (\Throwable $ignore) {
                // Read-only diagnostics must never break the Updates page.
            }
        }
        return $result;
    }

    /** @return array<int,array{name:string,exists:bool,classification:string}> */
    private static function optionAudit(): array
    {
        $definitions = [
            ['hangar18_manager_vehicle_register_v12', 'AKTIV DATA · behold'],
            ['hangar18_manager_config_import_meta', 'MIGRATION/IMPORT · behold indtil migration er afsluttet'],
            ['hangar18_manager_config_bootstrap_v032', 'LEGACY BOOTSTRAP · review efter backup/QA'],
            ['hangar18_manager_authoritative_baseline_20260813', 'BASELINE/AUDIT · behold indtil migration er afsluttet'],
            ['hangar18_manager_frontend_repair_046', 'ONE-TIME REPAIR FLAG · cleanup-kandidat efter live QA'],
            ['hangar18_manager_astra_banner_repair_047', 'ONE-TIME REPAIR FLAG · cleanup-kandidat efter live QA'],
            ['hangar18_manager_vehicle_layout_repair_049', 'ONE-TIME REPAIR FLAG · cleanup-kandidat efter live QA'],
            ['hangar18_manager_legacy_page_template_repair_0411', 'ONE-TIME REPAIR FLAG · cleanup-kandidat efter live QA'],
            ['hangar18_manager_mobile_content_layout_repair_0414', 'ONE-TIME REPAIR FLAG · cleanup-kandidat efter live QA'],
            ['hangar18_manager_legacy_startup_cleanup_0415', 'ONE-TIME CLEANUP FLAG · cleanup-kandidat efter live QA'],
            ['hangar18_manager_home_editor_design_repair_0423', 'ONE-TIME REPAIR FLAG · cleanup-kandidat efter live QA'],
        ];
        $result = [];
        foreach ($definitions as $definition) {
            $sentinel = new \stdClass();
            $value = get_option($definition[0], $sentinel);
            $result[] = [
                'name' => $definition[0],
                'exists' => $value !== $sentinel,
                'classification' => $definition[1],
            ];
        }
        return $result;
    }

    private static function row(string $label, string $value, string $note): void
    {
        echo '<tr><th style="width:240px">' . esc_html($label) . '</th><td style="width:120px"><strong>' . esc_html($value) . '</strong></td><td>' . esc_html($note) . '</td></tr>';
    }
}
