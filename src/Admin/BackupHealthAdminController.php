<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupIntegrityService;
use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestoreService;
use Hangar18\UltimateDesigner\Backup\SiteBackupPackageService;
use Hangar18\UltimateDesigner\Backup\SiteBackupRestoreService;

/** Read-only backup health and restore-audit support layer. */
final class BackupHealthAdminController
{
    private const HEALTH_OPTION = 'hangar18_manager_backup_health_v1';
    private const CHECK_INTERVAL = 21600; // 6 hours.
    private const PAGE_UPDATES = 'hangar18-updates';
    private const PAGE_DESIGNER = 'hangar18-ultimate-designer';
    private const NONCE = 'h18_backup_health_v1';

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_init', [self::class, 'maybeCheck'], 65);
        add_action('admin_notices', [self::class, 'render'], 32);
        add_action('admin_post_h18_backup_health_refresh', [self::class, 'handleRefresh']);
        add_action('admin_post_h18_backup_audit_export', [self::class, 'handleExport']);
    }

    public static function maybeCheck(): void
    {
        if (!is_admin() || !current_user_can('manage_options')) {
            return;
        }
        $page = self::page();
        if (!in_array($page, [self::PAGE_UPDATES, self::PAGE_DESIGNER], true)) {
            return;
        }
        $previous = get_option(self::HEALTH_OPTION, []);
        $previous = is_array($previous) ? $previous : [];
        $checked = strtotime((string) ($previous['CheckedUtc'] ?? ''));
        if ($checked !== false && (time() - $checked) < self::CHECK_INTERVAL) {
            return;
        }
        self::runCheck();
    }

    public static function handleRefresh(): void
    {
        self::authorize();
        self::runCheck();
        self::redirect('Backup health-check er opdateret.');
    }

    public static function render(): void
    {
        if (!is_admin() || !current_user_can('manage_options')) {
            return;
        }
        if (!in_array(self::page(), [self::PAGE_UPDATES, self::PAGE_DESIGNER], true)) {
            return;
        }

        $health = get_option(self::HEALTH_OPTION, []);
        $health = is_array($health) ? $health : [];
        $errors = is_array($health['Errors'] ?? null) ? $health['Errors'] : [];
        $checked = (string) ($health['CheckedUtc'] ?? 'ikke kørt');
        $b1 = is_array($health['B1'] ?? null) ? $health['B1'] : [];
        $b2 = is_array($health['B2'] ?? null) ? $health['B2'] : [];
        $class = $errors ? 'notice notice-warning' : 'notice notice-info';

        echo '<div class="' . esc_attr($class) . '" style="padding:12px 16px;margin-top:14px">';
        echo '<h2 style="margin:0 0 8px">Backup health · read-only</h2>';
        echo '<p><strong>Sidst kontrolleret:</strong> ' . esc_html($checked) .
            ' · B1: ' . esc_html((string) ($b1['Valid'] ?? 0)) . '/' . esc_html((string) ($b1['Checked'] ?? 0)) . ' valide' .
            ' · B2: ' . esc_html((string) ($b2['Valid'] ?? 0)) . '/' . esc_html((string) ($b2['Checked'] ?? 0)) . ' valide.</p>';
        if ($errors) {
            echo '<details><summary><strong>' . esc_html((string) count($errors)) . ' backup health-fejl</strong></summary><ul style="list-style:disc;padding-left:22px">';
            foreach ($errors as $error) {
                echo '<li>' . esc_html((string) $error) . '</li>';
            }
            echo '</ul></details>';
        }

        echo '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">';
        self::postButton('h18_backup_health_refresh', [], 'Kør health-check nu');
        self::postButton('h18_backup_audit_export', ['format'=>'json'], 'Eksportér restore-audit JSON');
        self::postButton('h18_backup_audit_export', ['format'=>'csv'], 'Eksportér restore-audit CSV');
        echo '</div></div>';
    }

    public static function handleExport(): void
    {
        self::authorize();
        $format = sanitize_key((string) wp_unslash($_POST['format'] ?? 'json'));
        if (!in_array($format, ['json', 'csv'], true)) {
            wp_die(esc_html__('Ukendt eksportformat.', 'hangar18-manager'));
        }

        $records = self::auditRecords();
        $stamp = gmdate('Ymd-His');
        while (ob_get_level() > 0) {
            ob_end_clean();
        }
        nocache_headers();

        if ($format === 'json') {
            header('Content-Type: application/json; charset=utf-8');
            header('Content-Disposition: attachment; filename="Hangar18-Restore-Audit-' . $stamp . '.json"');
            echo wp_json_encode([
                'SchemaVersion'=>'1.0',
                'ExportedUtc'=>gmdate('c'),
                'RecordCount'=>count($records),
                'Records'=>$records,
            ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
            exit;
        }

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="Hangar18-Restore-Audit-' . $stamp . '.csv"');
        $out = fopen('php://output', 'wb');
        if ($out === false) {
            wp_die(esc_html__('CSV-output kunne ikke åbnes.', 'hangar18-manager'));
        }
        // Excel-friendly UTF-8 BOM and semicolon delimiter, matching Hangar18 admin conventions.
        fwrite($out, "\xEF\xBB\xBF");
        fputcsv($out, ['Source','Utc','Mode','Backup','PageSlug','TargetPageId','SafetyBackup','UserId','Error'], ';');
        foreach ($records as $row) {
            fputcsv($out, [
                (string) ($row['Source'] ?? ''),
                (string) ($row['Utc'] ?? ''),
                (string) ($row['Mode'] ?? ''),
                (string) ($row['Backup'] ?? ''),
                (string) ($row['PageSlug'] ?? ''),
                (string) ($row['TargetPageId'] ?? ''),
                (string) ($row['SafetyBackup'] ?? ''),
                (string) ($row['UserId'] ?? ''),
                (string) ($row['Error'] ?? ''),
            ], ';');
        }
        fclose($out);
        exit;
    }

    /** @return array<string,mixed> */
    private static function runCheck(): array
    {
        $errors = [];
        $b1Checked = 0;
        $b1Valid = 0;
        $b2Checked = 0;
        $b2Valid = 0;

        try {
            $b1Service = new ManagedPageBackupRestoreService();
            $integrity = new ManagedPageBackupIntegrityService();
            foreach (array_slice($b1Service->listBackups(10), 0, 10) as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                $filename = (string) ($entry['Filename'] ?? '');
                if ($filename === '') {
                    continue;
                }
                $b1Checked++;
                try {
                    $report = $integrity->inspect($filename);
                    if (!empty($report['Valid'])) {
                        $b1Valid++;
                    }
                } catch (\Throwable $error) {
                    $errors[] = 'B1 ' . $filename . ': ' . $error->getMessage();
                }
            }
        } catch (\Throwable $error) {
            $errors[] = 'B1 health-check: ' . $error->getMessage();
        }

        try {
            $packages = new SiteBackupPackageService();
            foreach (array_slice($packages->listBackups(), 0, 5) as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                $id = (string) ($entry['BackupId'] ?? '');
                if ($id === '') {
                    continue;
                }
                $b2Checked++;
                $report = $packages->validate($id);
                if (!empty($report['Valid'])) {
                    $b2Valid++;
                } else {
                    $messages = is_array($report['Errors'] ?? null) ? $report['Errors'] : [];
                    $errors[] = 'B2 ' . $id . ': ' . ($messages ? implode(' | ', array_map('strval', $messages)) : 'ukendt integritetsfejl');
                }
            }
        } catch (\Throwable $error) {
            $errors[] = 'B2 health-check: ' . $error->getMessage();
        }

        $report = [
            'SchemaVersion'=>'1.0',
            'CheckedUtc'=>gmdate('c'),
            'ReadOnly'=>true,
            'B1'=>['Checked'=>$b1Checked,'Valid'=>$b1Valid],
            'B2'=>['Checked'=>$b2Checked,'Valid'=>$b2Valid],
            'Errors'=>array_slice(array_values(array_unique($errors)), 0, 50),
        ];
        update_option(self::HEALTH_OPTION, $report, false);
        return $report;
    }

    /** @return array<int,array<string,mixed>> */
    private static function auditRecords(): array
    {
        $out = [];
        $b1 = get_option(ManagedPageBackupRestoreService::AUDIT_OPTION, []);
        foreach (is_array($b1) ? $b1 : [] as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $out[] = [
                'Source'=>'B1',
                'Utc'=>(string) ($entry['Utc'] ?? ''),
                'Mode'=>(string) ($entry['Mode'] ?? ''),
                'Backup'=>(string) ($entry['SourceBackup'] ?? ''),
                'PageSlug'=>(string) ($entry['SourceSlug'] ?? ''),
                'TargetPageId'=>(int) ($entry['TargetPageId'] ?? 0),
                'SafetyBackup'=>(string) ($entry['SafetyBackup'] ?? ''),
                'UserId'=>(int) ($entry['UserId'] ?? 0),
                'Error'=>(string) ($entry['Error'] ?? ''),
            ];
        }
        $b2 = get_option(SiteBackupRestoreService::AUDIT_OPTION, []);
        foreach (is_array($b2) ? $b2 : [] as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $out[] = [
                'Source'=>'B2',
                'Utc'=>(string) ($entry['Utc'] ?? ''),
                'Mode'=>(string) ($entry['Mode'] ?? ''),
                'Backup'=>(string) ($entry['BackupId'] ?? ''),
                'PageSlug'=>(string) ($entry['PageSlug'] ?? ''),
                'TargetPageId'=>0,
                'SafetyBackup'=>(string) ($entry['SafetyBackupId'] ?? ''),
                'UserId'=>(int) ($entry['UserId'] ?? 0),
                'Error'=>(string) ($entry['Error'] ?? ''),
            ];
        }
        usort($out, static fn(array $a, array $b): int => strcmp((string) ($b['Utc'] ?? ''), (string) ($a['Utc'] ?? '')));
        return array_slice($out, 0, 500);
    }

    /** @param array<string,string> $fields */
    private static function postButton(string $action, array $fields, string $label): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline-block">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr($action) . '">';
        foreach ($fields as $name=>$value) {
            echo '<input type="hidden" name="' . esc_attr($name) . '" value="' . esc_attr($value) . '">';
        }
        echo '<button type="submit" class="button">' . esc_html($label) . '</button></form>';
    }

    private static function authorize(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Kun administratorer kan bruge backup health/audit-support.', 'hangar18-manager'));
        }
        check_admin_referer(self::NONCE);
    }

    private static function page(): string
    {
        return isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
    }

    private static function redirect(string $message): void
    {
        $page = self::page();
        if (!in_array($page, [self::PAGE_UPDATES, self::PAGE_DESIGNER], true)) {
            $page = self::PAGE_UPDATES;
        }
        wp_safe_redirect(add_query_arg(['page'=>$page,'h18_backup_health_message'=>$message], admin_url('admin.php')));
        exit;
    }
}
