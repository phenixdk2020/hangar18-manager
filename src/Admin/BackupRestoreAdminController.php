<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestoreService;

/** Admin UI for B1 managed page backup restore/copy. */
final class BackupRestoreAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_post_h18_ud_restore_backup_original', [self::class, 'restoreOriginal']);
        add_action('admin_post_h18_ud_restore_backup_copy', [self::class, 'createCopy']);
    }

    public static function renderPanel(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $service = new ManagedPageBackupRestoreService();
        $backups = $service->listBackups(30);
        $audit = $service->audit(20);

        echo '<section class="h18-ud-panel"><h2>B1 · Gendan sidebackup</h2>';
        echo '<p class="description">Bruger de eksisterende Hangar18 JSON-backups. <strong>Erstat original</strong> tager altid en ny sikkerhedsbackup før første write. <strong>Opret som kopi</strong> laver kun en ny draft og ændrer ikke originalens URL eller menu.</p>';
        echo '<div class="notice notice-warning inline"><p><strong>Restore er en eksplicit mutation:</strong> kontrollér backup, side og restore-mode før du fortsætter. Full-backups kan også gendanne den tilhørende Page Editor store-entry; ældre enkelt-side backups kan mangle denne del.</p></div>';

        if (!$backups) {
            echo '<p>Ingen læsbare managed backups blev fundet i <code>uploads/hangar18-manager-backups</code>.</p></section>';
            return;
        }

        echo '<div style="overflow:auto"><table class="widefat striped"><thead><tr><th>Backup</th><th>Side</th><th>Editor-data</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($backups as $backup) {
            $filename = (string) ($backup['Filename'] ?? '');
            $created = (string) ($backup['CreatedUtc'] ?? '');
            $reason = (string) ($backup['Reason'] ?? '');
            $hasStore = !empty($backup['HasPageEditorStore']);
            foreach ((array) ($backup['Pages'] ?? []) as $page) {
                if (!is_array($page)) {
                    continue;
                }
                $sourceKey = (string) ((int) ($page['ID'] ?? 0) > 0 ? (int) $page['ID'] : ($page['Slug'] ?? ''));
                echo '<tr><td><code>' . esc_html($filename) . '</code><br><small>' . esc_html($created) . '</small>';
                if ($reason !== '') {
                    echo '<br><small>' . esc_html($reason) . '</small>';
                }
                echo '</td><td><strong>' . esc_html((string) ($page['Title'] ?? '')) . '</strong><br><code>' . esc_html((string) ($page['Slug'] ?? '')) . '</code><br><small>ID ' . esc_html((string) ($page['ID'] ?? 0)) . ' · ' . esc_html((string) ($page['Status'] ?? '')) . '</small></td>';
                echo '<td>' . ($hasStore ? '<span class="h18-health-ok">Tilgængelig</span>' : '<span class="h18-health-bad">Ikke i denne fil</span>') . '</td><td>';
                self::renderActionForm('h18_ud_restore_backup_original', $filename, $sourceKey, 'Erstat original', true);
                self::renderActionForm('h18_ud_restore_backup_copy', $filename, $sourceKey, 'Opret som kopi', false);
                echo '</td></tr>';
            }
        }
        echo '</tbody></table></div>';

        echo '<h3>Seneste restore-audit</h3>';
        if (!$audit) {
            echo '<p class="description">Ingen B1 restore-handlinger er registreret endnu.</p>';
        } else {
            echo '<div style="overflow:auto"><table class="widefat striped"><thead><tr><th>Tid</th><th>Mode</th><th>Kilde</th><th>Mål</th><th>Sikkerhedsbackup</th></tr></thead><tbody>';
            foreach ($audit as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                echo '<tr><td>' . esc_html((string) ($entry['Utc'] ?? '')) . '</td><td><code>' . esc_html((string) ($entry['Mode'] ?? '')) . '</code></td><td>' . esc_html((string) ($entry['SourceBackup'] ?? '')) . '<br><code>' . esc_html((string) ($entry['SourceSlug'] ?? '')) . '</code></td><td>ID ' . esc_html((string) ($entry['TargetPageId'] ?? 0)) . '<br><code>' . esc_html((string) ($entry['TargetSlug'] ?? '')) . '</code></td><td><code>' . esc_html((string) ($entry['SafetyBackup'] ?? '')) . '</code></td></tr>';
            }
            echo '</tbody></table></div>';
        }
        echo '</section>';
    }

    public static function restoreOriginal(): void
    {
        self::authorize();
        try {
            $result = (new ManagedPageBackupRestoreService())->restoreOriginal(
                sanitize_file_name((string) wp_unslash($_POST['backup_file'] ?? '')),
                sanitize_text_field((string) wp_unslash($_POST['source_key'] ?? ''))
            );
            self::redirect('success', sprintf(
                'Side ID %d blev gendannet. Sikkerhedsbackup: %s',
                (int) ($result['TargetPageId'] ?? 0),
                (string) ($result['SafetyBackup'] ?? '')
            ));
        } catch (\Throwable $error) {
            self::redirect('error', 'Restore fejlede: ' . $error->getMessage());
        }
    }

    public static function createCopy(): void
    {
        self::authorize();
        try {
            $result = (new ManagedPageBackupRestoreService())->createCopy(
                sanitize_file_name((string) wp_unslash($_POST['backup_file'] ?? '')),
                sanitize_text_field((string) wp_unslash($_POST['source_key'] ?? ''))
            );
            self::redirect('success', sprintf(
                'Backup-siden blev oprettet som draft-kopi: %s (ID %d).',
                (string) ($result['TargetSlug'] ?? ''),
                (int) ($result['TargetPageId'] ?? 0)
            ));
        } catch (\Throwable $error) {
            self::redirect('error', 'Kopi kunne ikke oprettes: ' . $error->getMessage());
        }
    }

    private static function renderActionForm(string $action, string $filename, string $sourceKey, string $label, bool $destructive): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline-block;margin:0 8px 6px 0">';
        wp_nonce_field('h18_ud_backup_restore');
        echo '<input type="hidden" name="action" value="' . esc_attr($action) . '">';
        echo '<input type="hidden" name="backup_file" value="' . esc_attr($filename) . '">';
        echo '<input type="hidden" name="source_key" value="' . esc_attr($sourceKey) . '">';
        $confirm = $destructive ? ' onclick="return confirm(\'Erstat originalsiden med denne backup? Der oprettes først en ny sikkerhedsbackup af den nuværende original.\');"' : '';
        echo '<button type="submit" class="button' . ($destructive ? ' button-secondary' : '') . '"' . $confirm . '>' . esc_html($label) . '</button>';
        echo '</form>';
    }

    private static function authorize(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne handling.', 'hangar18-manager'));
        }
        check_admin_referer('h18_ud_backup_restore');
    }

    private static function redirect(string $status, string $message): void
    {
        $url = add_query_arg([
            'page' => IntegrationAdminBootstrap::PAGE_SLUG,
            'ud_status' => $status === 'error' ? 'error' : 'success',
            'ud_message' => $message,
        ], admin_url('admin.php'));
        wp_safe_redirect($url);
        exit;
    }
}
