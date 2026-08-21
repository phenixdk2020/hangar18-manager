<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestorePreflightService;
use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestoreService;
use Hangar18\UltimateDesigner\Backup\ManagedPageTrashService;
use RuntimeException;

require_once dirname(__DIR__) . '/Backup/ManagedPageTrashService.php';

/** Admin UI for B1 managed page backup restore/copy and safe page Trash. */
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
        add_action('admin_post_h18_ud_trash_page', [self::class, 'trashPage']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueuePageDelete']);
        add_action('admin_notices', [self::class, 'renderPageDeleteNotice']);
    }

    public static function enqueuePageDelete(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('delete_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-page-delete-v0844.js';
        wp_enqueue_script(
            'hangar18-ultimate-designer-page-delete-v0844',
            $pluginUrl . 'assets/ultimate-designer-page-delete-v0844.js',
            [],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.44',
            true
        );
        wp_localize_script(
            'hangar18-ultimate-designer-page-delete-v0844',
            'H18PageDeleteV0844',
            [
                'actionUrl' => admin_url('admin-post.php'),
                'nonce' => wp_create_nonce('h18_ud_trash_page'),
                'action' => 'h18_ud_trash_page',
                'buttonLabel' => 'Slet side',
            ]
        );
    }

    public static function renderPageDeleteNotice(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages') {
            return;
        }
        $status = isset($_GET['h18_page_delete_status']) ? sanitize_key((string) wp_unslash($_GET['h18_page_delete_status'])) : '';
        $message = isset($_GET['h18_page_delete_message']) ? sanitize_text_field((string) wp_unslash($_GET['h18_page_delete_message'])) : '';
        if ($status === '' || $message === '') {
            return;
        }
        $class = $status === 'error' ? 'notice notice-error is-dismissible' : 'notice notice-success is-dismissible';
        echo '<div class="' . esc_attr($class) . '"><p>' . esc_html($message) . '</p></div>';
    }

    public static function renderPanel(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $service = new ManagedPageBackupRestoreService();
        $preflight = new ManagedPageBackupRestorePreflightService();
        $backups = $service->listBackups(30);
        $audit = $service->audit(20);

        echo '<section class="h18-ud-panel"><h2>B1 · Gendan sidebackup</h2>';
        echo '<p class="description">Bruger de eksisterende Hangar18 JSON-backups. <strong>Erstat original</strong> tager altid en ny sikkerhedsbackup før første write. <strong>Opret som kopi</strong> laver kun en ny draft og ændrer ikke originalens URL eller menu.</p>';
        echo '<div class="notice notice-warning inline"><p><strong>Restore er en eksplicit mutation:</strong> kontrollér backup, side og restore-mode før du fortsætter. Page Editor-sider kan kun erstatte originalen, når backupfilen også indeholder den centrale editor-state; ellers er kun sikker kopi-mode tilgængelig.</p></div>';

        if (!$backups) {
            echo '<p>Ingen læsbare managed backups blev fundet i <code>uploads/hangar18-manager-backups</code>.</p></section>';
            return;
        }

        echo '<div style="overflow:auto"><table class="widefat striped"><thead><tr><th>Backup</th><th>Side</th><th>Editor-data</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($backups as $backup) {
            $filename = (string) ($backup['Filename'] ?? '');
            $created = (string) ($backup['CreatedUtc'] ?? '');
            $reason = (string) ($backup['Reason'] ?? '');
            foreach ((array) ($backup['Pages'] ?? []) as $page) {
                if (!is_array($page)) {
                    continue;
                }
                $sourceKey = (string) ((int) ($page['ID'] ?? 0) > 0 ? (int) $page['ID'] : ($page['Slug'] ?? ''));
                $replaceAllowed = false;
                $replaceReason = 'Restore preflight kunne ikke køres.';
                $editorSource = 'ukendt';
                try {
                    $check = $preflight->analyzeReplace($filename, $sourceKey);
                    $replaceAllowed = !empty($check['Allowed']);
                    $replaceReason = (string) ($check['Reason'] ?? '');
                    $editorSource = (string) ($check['EditorDataSource'] ?? 'ukendt');
                } catch (\Throwable $error) {
                    $replaceReason = 'Preflight-fejl: ' . $error->getMessage();
                }

                echo '<tr><td><code>' . esc_html($filename) . '</code><br><small>' . esc_html($created) . '</small>';
                if ($reason !== '') {
                    echo '<br><small>' . esc_html($reason) . '</small>';
                }
                echo '</td><td><strong>' . esc_html((string) ($page['Title'] ?? '')) . '</strong><br><code>' . esc_html((string) ($page['Slug'] ?? '')) . '</code><br><small>ID ' . esc_html((string) ($page['ID'] ?? 0)) . ' · ' . esc_html((string) ($page['Status'] ?? '')) . '</small></td>';
                echo '<td><code>' . esc_html($editorSource) . '</code><br><small>' . esc_html($replaceReason) . '</small></td><td>';
                if ($replaceAllowed) {
                    self::renderActionForm('h18_ud_restore_backup_original', $filename, $sourceKey, 'Erstat original', true);
                } else {
                    echo '<button type="button" class="button" disabled title="' . esc_attr($replaceReason) . '">Erstat original · låst</button> ';
                }
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
            $filename = sanitize_file_name((string) wp_unslash($_POST['backup_file'] ?? ''));
            $sourceKey = sanitize_text_field((string) wp_unslash($_POST['source_key'] ?? ''));
            $check = (new ManagedPageBackupRestorePreflightService())->analyzeReplace($filename, $sourceKey);
            if (empty($check['Allowed'])) {
                throw new RuntimeException((string) ($check['Reason'] ?? 'Restore preflight afviste backup-kilden.'));
            }
            $result = (new ManagedPageBackupRestoreService())->restoreOriginal($filename, $sourceKey);
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

    public static function trashPage(): void
    {
        if (!current_user_can('delete_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til at slette sider.', 'hangar18-manager'));
        }
        check_admin_referer('h18_ud_trash_page');

        try {
            $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));
            if ($slug === '') {
                throw new RuntimeException('Der blev ikke angivet en gyldig side.');
            }
            $post = get_page_by_path($slug, OBJECT, 'page');
            if (!$post instanceof \WP_Post || $post->post_type !== 'page') {
                throw new RuntimeException('Siden kunne ikke findes.');
            }
            if (!current_user_can('delete_post', (int) $post->ID)) {
                throw new RuntimeException('Du har ikke delete-rettighed til denne side.');
            }

            $confirmation = trim((string) wp_unslash($_POST['confirm_title'] ?? ''));
            $result = (new ManagedPageTrashService())->trashBySlug($slug, $confirmation, get_current_user_id());
            self::redirectPageEditor('success', sprintf(
                'Siden "%s" blev flyttet til WordPress Papirkurv. Sikkerhedsbackup: %s. Den kan gendannes fra B1-backup-panelet.',
                (string) ($result['Title'] ?? ''),
                (string) ($result['SafetyBackup'] ?? '')
            ));
        } catch (\Throwable $error) {
            self::redirectPageEditor('error', 'Slet side fejlede: ' . $error->getMessage());
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

    private static function redirectPageEditor(string $status, string $message): void
    {
        $url = add_query_arg([
            'page' => 'hangar18-pages',
            'h18_page_delete_status' => $status === 'error' ? 'error' : 'success',
            'h18_page_delete_message' => $message,
        ], admin_url('admin.php'));
        wp_safe_redirect($url);
        exit;
    }
}
