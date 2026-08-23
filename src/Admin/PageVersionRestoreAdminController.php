<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestorePreflightService;
use Hangar18\UltimateDesigner\Backup\ManagedPageBackupRestoreService;
use RuntimeException;

/**
 * Makes the legacy Page Editor version history actionable without introducing
 * a second restore engine. Mutation is delegated to the existing B1 service.
 */
final class PageVersionRestoreAdminController
{
    private const HISTORY_OPTION = 'hangar18_manager_page_versions_v1';
    private const PAGE_SLUG = 'hangar18-pages';
    private const NONCE_ACTION = 'h18_ud_page_version_restore';
    private const MAX_VISIBLE = 30;

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        add_action('admin_notices', [self::class, 'renderNotice']);
        add_action('admin_notices', [self::class, 'renderPanel'], 30);
        add_action('admin_post_h18_ud_restore_page_version_original', [self::class, 'restoreOriginal']);
        add_action('admin_post_h18_ud_restore_page_version_copy', [self::class, 'restoreCopy']);
    }

    public static function renderNotice(): void
    {
        if (!self::isPageEditorRequest()) {
            return;
        }
        $status = isset($_GET['h18_version_restore_status'])
            ? sanitize_key((string) wp_unslash($_GET['h18_version_restore_status']))
            : '';
        $message = isset($_GET['h18_version_restore_message'])
            ? sanitize_text_field((string) wp_unslash($_GET['h18_version_restore_message']))
            : '';
        if ($status === '' || $message === '') {
            return;
        }
        $class = $status === 'error' ? 'notice notice-error is-dismissible' : 'notice notice-success is-dismissible';
        echo '<div class="' . esc_attr($class) . '"><p>' . esc_html($message) . '</p></div>';
    }

    public static function renderPanel(): void
    {
        if (!self::isPageEditorRequest() || !current_user_can('edit_pages')) {
            return;
        }

        $slug = self::requestedSlug();
        if ($slug === '') {
            return;
        }
        $history = self::history($slug);
        if (!$history) {
            return;
        }

        $currentPage = get_page_by_path($slug, OBJECT, 'page');
        $currentTitle = $currentPage instanceof \WP_Post ? (string) $currentPage->post_title : $slug;
        $currentHash = $currentPage instanceof \WP_Post ? hash('sha256', (string) $currentPage->post_content) : '';

        echo '<div class="notice notice-info" style="padding:14px 16px;margin-top:12px">';
        echo '<h2 style="margin-top:0">Sideversioner · ' . esc_html($currentTitle) . '</h2>';
        echo '<p>Vælg altid restore-mode eksplicit. <strong>Erstat original</strong> opretter først en B1-sikkerhedsbackup. <strong>Restore som kopi</strong> ændrer ikke originalsiden og opretter en ny draft med unik slug.</p>';
        echo '<div style="overflow:auto"><table class="widefat striped"><thead><tr>';
        echo '<th>Version</th><th>Gemt</th><th>Ændring</th><th>Kontrol</th><th>Restore</th>';
        echo '</tr></thead><tbody>';

        foreach (array_slice($history, 0, self::MAX_VISIBLE) as $entry) {
            $version = (int) ($entry['Version'] ?? 0);
            if ($version <= 0) {
                continue;
            }
            $source = self::resolveSource($slug, $version, $history);
            $replaceFile = (string) ($source['replace_file'] ?? '');
            $copyFile = (string) ($source['copy_file'] ?? '');
            $replaceAllowed = false;
            $replaceReason = 'Der findes ikke en komplet restore-kilde med Page Editor-state for denne version.';

            if ($replaceFile !== '') {
                try {
                    $check = (new ManagedPageBackupRestorePreflightService())->analyzeReplace($replaceFile, $slug);
                    $replaceAllowed = !empty($check['Allowed']);
                    $replaceReason = (string) ($check['Reason'] ?? $replaceReason);
                } catch (\Throwable $error) {
                    $replaceReason = $error->getMessage();
                }
            }

            $saved = (string) ($entry['SavedUtc'] ?? '');
            $savedDisplay = $saved !== '' ? $saved : 'ukendt';
            $note = trim((string) ($entry['ChangeNote'] ?? ''));
            $hash = strtolower((string) ($entry['ContentHash'] ?? ''));
            $hashText = $hash !== '' ? substr($hash, 0, 12) . '…' : '—';
            $active = (int) ($entry['ActiveSections'] ?? 0);

            echo '<tr>';
            echo '<td><strong>v' . esc_html((string) $version) . '</strong><br><small>' . esc_html((string) ($entry['UserDisplay'] ?? '')) . '</small></td>';
            echo '<td>' . esc_html($savedDisplay) . '</td>';
            echo '<td>' . ($note !== '' ? nl2br(esc_html($note)) : '<em>Ingen ændringsnote</em>') . '</td>';
            echo '<td><details><summary>Vis detaljer</summary>';
            echo '<small>Aktive sektioner: ' . esc_html((string) $active) . '<br>Versionshash: <code>' . esc_html($hashText) . '</code>';
            if ($currentHash !== '') {
                echo '<br>Aktuel WP-hash: <code>' . esc_html(substr($currentHash, 0, 12) . '…') . '</code>';
            }
            echo '<br>Restore-kilde: <code>' . esc_html($replaceFile !== '' ? $replaceFile : ($copyFile !== '' ? $copyFile : 'ingen')) . '</code>';
            echo '</small></details></td>';
            echo '<td>';

            if ($replaceAllowed) {
                self::renderAction(
                    'h18_ud_restore_page_version_original',
                    $slug,
                    $version,
                    $replaceFile,
                    'Erstat original',
                    true
                );
            } else {
                echo '<button type="button" class="button" disabled title="' . esc_attr($replaceReason) . '">Erstat original · låst</button> ';
            }

            if ($copyFile !== '') {
                self::renderAction(
                    'h18_ud_restore_page_version_copy',
                    $slug,
                    $version,
                    $copyFile,
                    'Restore som kopi',
                    false
                );
            } else {
                echo '<button type="button" class="button" disabled>Restore som kopi · ingen snapshot</button>';
            }

            if (!$replaceAllowed) {
                echo '<br><small>' . esc_html($replaceReason) . '</small>';
            }
            echo '</td></tr>';
        }

        echo '</tbody></table></div></div>';
    }

    public static function restoreOriginal(): void
    {
        self::authorize();
        $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));
        $version = absint($_POST['version'] ?? 0);

        try {
            if ($slug === '' || $version <= 0) {
                throw new RuntimeException('Side eller version mangler.');
            }
            $history = self::history($slug);
            $source = self::resolveSource($slug, $version, $history);
            $filename = sanitize_file_name((string) ($source['replace_file'] ?? ''));
            if ($filename === '') {
                throw new RuntimeException('Denne version har ikke en komplet restore-kilde til Erstat original. Brug Restore som kopi.');
            }

            // Do not trust a posted backup filename. Resolve it again from the
            // canonical version history and run the same B1 preflight as the
            // ordinary backup restore panel.
            $check = (new ManagedPageBackupRestorePreflightService())->analyzeReplace($filename, $slug);
            if (empty($check['Allowed'])) {
                throw new RuntimeException((string) ($check['Reason'] ?? 'Restore preflight afviste kilden.'));
            }

            $result = (new ManagedPageBackupRestoreService())->restoreOriginal($filename, $slug);
            self::redirect($slug, 'success', sprintf(
                'Version v%d erstattede originalsiden. Sikkerhedsbackup før restore: %s',
                $version,
                (string) ($result['SafetyBackup'] ?? '')
            ));
        } catch (\Throwable $error) {
            self::redirect($slug, 'error', 'Restore af version v' . $version . ' fejlede: ' . $error->getMessage());
        }
    }

    public static function restoreCopy(): void
    {
        self::authorize();
        $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));
        $version = absint($_POST['version'] ?? 0);

        try {
            if ($slug === '' || $version <= 0) {
                throw new RuntimeException('Side eller version mangler.');
            }
            $history = self::history($slug);
            $source = self::resolveSource($slug, $version, $history);
            $filename = sanitize_file_name((string) ($source['copy_file'] ?? ''));
            if ($filename === '') {
                throw new RuntimeException('Der findes ingen læsbar snapshot/backup for denne version.');
            }

            $result = (new ManagedPageBackupRestoreService())->createCopy($filename, $slug);
            self::redirect($slug, 'success', sprintf(
                'Version v%d blev restored som draft-kopi: %s (ID %d). Originalsiden blev ikke ændret.',
                $version,
                (string) ($result['TargetSlug'] ?? ''),
                (int) ($result['TargetPageId'] ?? 0)
            ));
        } catch (\Throwable $error) {
            self::redirect($slug, 'error', 'Restore som kopi af version v' . $version . ' fejlede: ' . $error->getMessage());
        }
    }

    private static function renderAction(
        string $action,
        string $slug,
        int $version,
        string $filename,
        string $label,
        bool $destructive
    ): void {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline-block;margin:0 8px 6px 0">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="' . esc_attr($action) . '">';
        echo '<input type="hidden" name="page_slug" value="' . esc_attr($slug) . '">';
        echo '<input type="hidden" name="version" value="' . esc_attr((string) $version) . '">';
        // Filename is display/audit context only. Handlers deliberately resolve
        // the canonical filename again instead of trusting this POST value.
        echo '<input type="hidden" name="source_file" value="' . esc_attr($filename) . '">';
        $confirm = $destructive
            ? ' onclick="return confirm(\'Erstat originalsiden med version v' . esc_js((string) $version) . '? Der oprettes først en sikkerhedsbackup af den nuværende original.\');"'
            : '';
        echo '<button type="submit" class="button' . ($destructive ? ' button-secondary' : '') . '"' . $confirm . '>' . esc_html($label) . '</button>';
        echo '</form>';
    }

    /** @return array<int,array<string,mixed>> */
    private static function history(string $slug): array
    {
        $all = get_option(self::HISTORY_OPTION, []);
        if (!is_array($all) || !isset($all[$slug]) || !is_array($all[$slug])) {
            return [];
        }

        $history = [];
        foreach ($all[$slug] as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $version = absint($entry['Version'] ?? 0);
            if ($version <= 0) {
                continue;
            }
            $history[] = [
                'Version' => $version,
                'SavedUtc' => sanitize_text_field((string) ($entry['SavedUtc'] ?? '')),
                'UserDisplay' => sanitize_text_field((string) ($entry['UserDisplay'] ?? '')),
                'ChangeNote' => sanitize_textarea_field((string) ($entry['ChangeNote'] ?? '')),
                'FullBackupFile' => sanitize_file_name((string) ($entry['FullBackupFile'] ?? '')),
                'SnapshotFile' => sanitize_file_name((string) ($entry['SnapshotFile'] ?? '')),
                'ContentHash' => preg_replace('/[^a-f0-9]/i', '', (string) ($entry['ContentHash'] ?? '')),
                'ActiveSections' => absint($entry['ActiveSections'] ?? 0),
            ];
        }

        usort($history, static fn(array $a, array $b): int => ((int) $b['Version']) <=> ((int) $a['Version']));
        return $history;
    }

    /** @return array<string,string> */
    private static function resolveSource(string $slug, int $version, array $history): array
    {
        $target = null;
        $newer = [];
        foreach ($history as $entry) {
            $entryVersion = (int) ($entry['Version'] ?? 0);
            if ($entryVersion === $version) {
                $target = $entry;
            } elseif ($entryVersion > $version) {
                $newer[] = $entry;
            }
        }
        if (!is_array($target)) {
            return ['replace_file' => '', 'copy_file' => ''];
        }

        // The full backup recorded on the next save is the state immediately
        // before that save: i.e. the complete state of the requested version.
        usort($newer, static fn(array $a, array $b): int => ((int) $a['Version']) <=> ((int) $b['Version']));
        $replaceFile = '';
        foreach ($newer as $entry) {
            $candidate = sanitize_file_name((string) ($entry['FullBackupFile'] ?? ''));
            if ($candidate === '') {
                continue;
            }
            try {
                $inspection = (new ManagedPageBackupRestoreService())->inspect($candidate);
                foreach ((array) ($inspection['Pages'] ?? []) as $page) {
                    if (is_array($page) && sanitize_title((string) ($page['Slug'] ?? '')) === $slug) {
                        $replaceFile = $candidate;
                        break 2;
                    }
                }
            } catch (\Throwable $ignore) {
                // Try the next newer full backup.
            }
        }

        $snapshotFile = sanitize_file_name((string) ($target['SnapshotFile'] ?? ''));
        $copyFile = $replaceFile !== '' ? $replaceFile : $snapshotFile;

        return [
            'replace_file' => $replaceFile,
            'copy_file' => $copyFile,
        ];
    }

    private static function authorize(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne restore-handling.', 'hangar18-manager'));
        }
        check_admin_referer(self::NONCE_ACTION);
    }

    private static function isPageEditorRequest(): bool
    {
        if (!is_admin()) {
            return false;
        }
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        return $page === self::PAGE_SLUG;
    }

    private static function requestedSlug(): string
    {
        return isset($_GET['page_slug'])
            ? sanitize_title((string) wp_unslash($_GET['page_slug']))
            : '';
    }

    private static function redirect(string $slug, string $status, string $message): void
    {
        $url = add_query_arg([
            'page' => self::PAGE_SLUG,
            'page_slug' => $slug,
            'h18_version_restore_status' => $status === 'error' ? 'error' : 'success',
            'h18_version_restore_message' => $message,
        ], admin_url('admin.php'));
        wp_safe_redirect($url);
        exit;
    }
}
