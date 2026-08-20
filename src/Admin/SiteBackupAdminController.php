<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Backup\SiteBackupPackageService;
use Hangar18\UltimateDesigner\Backup\SiteBackupRestoreCoordinator;
use Hangar18\UltimateDesigner\Backup\SiteBackupSecurityPolicy;
use RuntimeException;

/** Admin-only B2 create/export/import/dry-run/restore workflow. */
final class SiteBackupAdminController
{
    private const NONCE = 'h18_ud_b2_backup';
    private const PLAN_TTL = 900;
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_post_h18_ud_b2_create_backup', [self::class, 'handleCreate']);
        add_action('admin_post_h18_ud_b2_validate_backup', [self::class, 'handleValidate']);
        add_action('admin_post_h18_ud_b2_download_backup', [self::class, 'handleDownload']);
        add_action('admin_post_h18_ud_b2_import_backup', [self::class, 'handleImport']);
        add_action('admin_post_h18_ud_b2_plan_restore', [self::class, 'handlePlan']);
        add_action('admin_post_h18_ud_b2_execute_restore', [self::class, 'handleExecute']);
    }

    public static function renderPanel(): void
    {
        echo '<section class="h18-ud-panel"><h2>B2 · Versioneret site-backup / export / restore</h2>';
        echo '<p>Portabel Hangar18-applikationsbackup af administrerede sider, sideversioner, Site Builder, formularer/polls/data, Hangar18-options og refererede mediefiler. Den er <strong>ikke</strong> et råt database-, plugin- eller theme-image.</p>';

        if (!current_user_can('manage_options')) {
            echo '<div class="notice notice-warning inline"><p>B2 create/import/restore kræver <code>manage_options</code>. B1 sidekopi/restore forbliver separat.</p></div></section>';
            return;
        }

        $packages = new SiteBackupPackageService();
        $restore = new SiteBackupRestoreCoordinator($packages);
        $items = $packages->listBackups();
        $plan = self::currentPlan();

        echo '<div class="h18-two-action-grid">';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-panel">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="h18_ud_b2_create_backup">';
        echo '<h3>Opret fuld Hangar18-backup</h3><p>Der oprettes et immutable ID som <code>H18-BACKUP-000001</code>, checksums og ZIP når ZipArchive findes.</p>';
        echo '<label class="h18-field"><span>Note</span><input type="text" name="note" maxlength="500" placeholder="F.eks. Før større layoutændring"></label>';
        echo '<button type="submit" class="button button-primary">Opret versioneret backup</button></form>';

        echo '<form method="post" enctype="multipart/form-data" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-panel">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="h18_ud_b2_import_backup">';
        echo '<h3>Importér B2 ZIP</h3><p>ZIP kontrolleres for checksum, path traversal, ZIP-bomb og eksekverbare filer før installation.</p>';
        echo '<label class="h18-field"><span>Backup ZIP</span><input type="file" name="package" accept=".zip,application/zip" required></label>';
        echo '<label><input type="checkbox" name="new_id_on_collision" value="1"> Bevar begge ved ID-kollision ved at tildele nyt lokalt ID</label><br><br>';
        echo '<button type="submit" class="button">Importér og validér</button></form>';
        echo '</div>';

        if (is_array($plan)) {
            self::renderPlan($plan);
        }

        echo '<h3>Versionerede backups</h3>';
        if (!$items) {
            echo '<p>Der er endnu ingen B2-backups.</p>';
        } else {
            echo '<div class="h18-log-table-wrap"><table class="widefat striped"><thead><tr><th>ID</th><th>Oprettet</th><th>Kilde</th><th>Indhold</th><th>Note</th><th>Handlinger</th></tr></thead><tbody>';
            foreach ($items as $item) {
                if (!is_array($item)) {
                    continue;
                }
                $id = (string) ($item['BackupId'] ?? '');
                $pages = self::backupPages($packages, $id);
                echo '<tr><td><code>' . esc_html($id) . '</code></td><td>' . esc_html((string) ($item['CreatedUtc'] ?? '')) . '</td><td>' . esc_html((string) ($item['SourceHost'] ?? '')) . '</td>';
                echo '<td>' . esc_html((string) ($item['PayloadCount'] ?? 0)) . ' payloads · ' . esc_html((string) ($item['MediaCount'] ?? 0)) . ' media</td><td>' . esc_html((string) ($item['Note'] ?? '')) . '</td><td>';
                self::smallPostForm('h18_ud_b2_validate_backup', $id, 'Validér');
                self::smallPostForm('h18_ud_b2_download_backup', $id, 'Download ZIP');
                self::planForm($id, 'full', '', 'Dry-run fuld restore');
                if ($pages) {
                    echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline-flex;gap:5px;align-items:center;margin:2px">';
                    wp_nonce_field(self::NONCE);
                    echo '<input type="hidden" name="action" value="h18_ud_b2_plan_restore"><input type="hidden" name="backup_id" value="' . esc_attr($id) . '"><input type="hidden" name="scope" value="page"><select name="page_slug">';
                    foreach ($pages as $slug => $title) {
                        echo '<option value="' . esc_attr($slug) . '">' . esc_html($title . ' · ' . $slug) . '</option>';
                    }
                    echo '</select><button class="button button-small" type="submit">Dry-run side</button></form>';
                }
                echo '</td></tr>';
            }
            echo '</tbody></table></div>';
        }

        $audit = $restore->audit(15);
        if ($audit) {
            echo '<h3>Restore-audit</h3><table class="widefat striped"><thead><tr><th>Tid</th><th>Mode</th><th>Backup</th><th>Safety backup</th><th>Resultat</th></tr></thead><tbody>';
            foreach ($audit as $entry) {
                if (!is_array($entry)) { continue; }
                echo '<tr><td>' . esc_html((string) ($entry['Utc'] ?? '')) . '</td><td>' . esc_html((string) ($entry['Mode'] ?? '')) . '</td><td><code>' . esc_html((string) ($entry['BackupId'] ?? '')) . '</code></td><td><code>' . esc_html((string) ($entry['SafetyBackupId'] ?? '')) . '</code></td><td>' . esc_html((string) ($entry['Error'] ?? 'OK')) . '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</section>';
    }

    public static function handleCreate(): void
    {
        self::authorize();
        try {
            SiteBackupSecurityPolicy::hardenStorage();
            $entry = (new SiteBackupPackageService())->create(sanitize_text_field((string) ($_POST['note'] ?? '')));
            self::redirect('success', 'B2 backup oprettet: ' . (string) ($entry['BackupId'] ?? 'ukendt'));
        } catch (\Throwable $error) {
            self::redirect('error', $error->getMessage());
        }
    }

    public static function handleValidate(): void
    {
        self::authorize();
        try {
            $id = self::postedBackupId();
            $report = (new SiteBackupPackageService())->validate($id);
            if (empty($report['Valid'])) {
                throw new RuntimeException('Validering fejlede: ' . implode(' | ', (array) ($report['Errors'] ?? [])));
            }
            self::redirect('success', $id . ' er valid. Payloads: ' . (int) ($report['PayloadCount'] ?? 0) . ' · media: ' . (int) ($report['MediaCount'] ?? 0));
        } catch (\Throwable $error) {
            self::redirect('error', $error->getMessage());
        }
    }

    public static function handleDownload(): void
    {
        self::authorize();
        try {
            SiteBackupSecurityPolicy::hardenStorage();
            $id = self::postedBackupId();
            $path = (new SiteBackupPackageService())->zipPath($id);
            if (!is_file($path) || !is_readable($path)) {
                throw new RuntimeException('ZIP-filen kan ikke læses.');
            }
            while (ob_get_level() > 0) { ob_end_clean(); }
            nocache_headers();
            header('Content-Type: application/zip');
            header('Content-Disposition: attachment; filename="' . basename($path) . '"');
            header('Content-Length: ' . (string) filesize($path));
            readfile($path);
            exit;
        } catch (\Throwable $error) {
            self::redirect('error', $error->getMessage());
        }
    }

    public static function handleImport(): void
    {
        self::authorize();
        try {
            $file = $_FILES['package'] ?? null;
            if (!is_array($file) || (int) ($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
                throw new RuntimeException('ZIP-uploaden blev ikke modtaget korrekt.');
            }
            $name = (string) ($file['name'] ?? '');
            $tmp = (string) ($file['tmp_name'] ?? '');
            $size = (int) ($file['size'] ?? 0);
            if (!preg_match('/\.zip$/i', $name) || $size <= 0 || $size > SiteBackupSecurityPolicy::MAX_ZIP_BYTES || !is_file($tmp)) {
                throw new RuntimeException('Uploaden er ikke en tilladt B2 ZIP-fil.');
            }
            SiteBackupSecurityPolicy::inspectZip($tmp);
            SiteBackupSecurityPolicy::hardenStorage();
            $entry = (new SiteBackupPackageService())->importZip($tmp, !empty($_POST['new_id_on_collision']));
            self::redirect('success', 'B2 package importeret som ' . (string) ($entry['BackupId'] ?? 'ukendt') . '.');
        } catch (\Throwable $error) {
            self::redirect('error', $error->getMessage());
        }
    }

    public static function handlePlan(): void
    {
        self::authorize();
        try {
            $id = self::postedBackupId();
            $scope = sanitize_key((string) ($_POST['scope'] ?? 'full')) === 'page' ? 'page' : 'full';
            $slug = $scope === 'page' ? sanitize_title((string) ($_POST['page_slug'] ?? '')) : '';
            $plan = (new SiteBackupRestoreCoordinator())->plan($id, $scope, $slug);
            set_transient(self::planKey(), $plan, self::PLAN_TTL);
            $message = empty($plan['Executable']) ? 'Dry-run fandt blokeringer. Se planen nedenfor.' : 'Dry-run er klar. Gennemgå planen før restore.';
            self::redirect(empty($plan['Executable']) ? 'error' : 'success', $message);
        } catch (\Throwable $error) {
            delete_transient(self::planKey());
            self::redirect('error', $error->getMessage());
        }
    }

    public static function handleExecute(): void
    {
        self::authorize();
        try {
            $plan = self::currentPlan();
            if (!is_array($plan) || empty($plan['Token']) || empty($plan['Executable'])) {
                throw new RuntimeException('Der findes ingen gyldig dry-run-plan. Kør dry-run igen.');
            }
            $scope = (string) ($plan['Scope'] ?? '');
            if ($scope === 'full') {
                $phrase = trim((string) ($_POST['confirm_phrase'] ?? ''));
                if ($phrase !== 'GENDAN HANGAR18') {
                    throw new RuntimeException('Fuld restore kræver bekræftelsesfrasen GENDAN HANGAR18.');
                }
            } elseif ($scope === 'page') {
                if (empty($_POST['confirm_page'])) {
                    throw new RuntimeException('Side-restore skal bekræftes eksplicit.');
                }
            } else {
                throw new RuntimeException('Restore-planen har ukendt scope.');
            }

            SiteBackupSecurityPolicy::hardenStorage();
            $coordinator = new SiteBackupRestoreCoordinator();
            $result = $scope === 'full'
                ? $coordinator->restoreFull((string) $plan['Token'])
                : $coordinator->restorePage((string) $plan['Token']);
            delete_transient(self::planKey());
            self::redirect('success', 'Restore gennemført. Safety backup: ' . (string) ($result['SafetyBackupId'] ?? 'ukendt'));
        } catch (\Throwable $error) {
            self::redirect('error', $error->getMessage());
        }
    }

    private static function renderPlan(array $plan): void
    {
        $errors = (array) ($plan['Errors'] ?? []);
        $warnings = (array) ($plan['Warnings'] ?? []);
        $scope = (string) ($plan['Scope'] ?? '');
        echo '<div class="h18-panel" style="margin:18px 0;border-left:5px solid ' . (empty($plan['Executable']) ? '#b32d2e' : '#2e7d32') . '"><h3>Aktuel B2 dry-run-plan</h3>';
        echo '<p><strong>Backup:</strong> <code>' . esc_html((string) ($plan['BackupId'] ?? '')) . '</code> · <strong>Scope:</strong> ' . esc_html($scope) . ($scope === 'page' ? ' · ' . esc_html((string) ($plan['PageSlug'] ?? '')) : '') . '</p>';
        echo '<p>' . count((array) ($plan['Pages'] ?? [])) . ' sidehandlinger · ' . count((array) ($plan['Media'] ?? [])) . ' mediahandlinger · udløber ' . esc_html(gmdate('Y-m-d H:i:s', (int) ($plan['ExpiresAt'] ?? 0))) . ' UTC.</p>';
        foreach ($errors as $error) { echo '<div class="notice notice-error inline"><p>' . esc_html((string) $error) . '</p></div>'; }
        foreach ($warnings as $warning) { echo '<div class="notice notice-warning inline"><p>' . esc_html((string) $warning) . '</p></div>'; }
        if (!empty($plan['Executable'])) {
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
            wp_nonce_field(self::NONCE);
            echo '<input type="hidden" name="action" value="h18_ud_b2_execute_restore">';
            if ($scope === 'full') {
                echo '<p><label>Skriv <code>GENDAN HANGAR18</code> for at aktivere fuld Hangar18-restore:<br><input type="text" name="confirm_phrase" autocomplete="off" required></label></p>';
                echo '<p class="description">Der oprettes en ny B2 safety backup før første restore-mutation.</p>';
            } else {
                echo '<p><label><input type="checkbox" name="confirm_page" value="1" required> Jeg bekræfter restore af siden <strong>' . esc_html((string) ($plan['PageSlug'] ?? '')) . '</strong>.</label></p>';
            }
            echo '<button type="submit" class="button button-primary" onclick="return confirm(\'Gennemfør den viste restore-plan?\')">Gennemfør restore</button></form>';
        }
        echo '</div>';
    }

    /** @return array<string,string> */
    private static function backupPages(SiteBackupPackageService $packages, string $id): array
    {
        try {
            $package = $packages->read($id);
            $result = [];
            foreach ((array) ($package['Payloads']['managed-site']['Pages'] ?? []) as $page) {
                if (!is_array($page)) { continue; }
                $slug = sanitize_title((string) ($page['Slug'] ?? ''));
                if ($slug !== '') { $result[$slug] = (string) ($page['Title'] ?? $slug); }
            }
            return $result;
        } catch (\Throwable $error) {
            return [];
        }
    }

    private static function smallPostForm(string $action, string $id, string $label): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline-block;margin:2px">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr($action) . '"><input type="hidden" name="backup_id" value="' . esc_attr($id) . '"><button type="submit" class="button button-small">' . esc_html($label) . '</button></form>';
    }

    private static function planForm(string $id, string $scope, string $slug, string $label): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline-block;margin:2px">';
        wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="h18_ud_b2_plan_restore"><input type="hidden" name="backup_id" value="' . esc_attr($id) . '"><input type="hidden" name="scope" value="' . esc_attr($scope) . '"><input type="hidden" name="page_slug" value="' . esc_attr($slug) . '"><button type="submit" class="button button-small">' . esc_html($label) . '</button></form>';
    }

    private static function authorize(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Du har ikke rettigheder til B2 backup/restore.', 'hangar18-manager'));
        }
        check_admin_referer(self::NONCE);
    }

    private static function postedBackupId(): string
    {
        $id = sanitize_text_field((string) ($_POST['backup_id'] ?? ''));
        if (!preg_match('/^H18-BACKUP-\d{6}$/', $id)) {
            throw new RuntimeException('Ugyldigt B2 BackupId.');
        }
        return $id;
    }

    /** @return array<string,mixed>|null */
    private static function currentPlan(): ?array
    {
        $plan = get_transient(self::planKey());
        return is_array($plan) ? $plan : null;
    }

    private static function planKey(): string
    {
        return 'h18_b2_plan_' . (function_exists('get_current_user_id') ? (int) get_current_user_id() : 0);
    }

    private static function redirect(string $status, string $message): void
    {
        $url = add_query_arg([
            'page'=>IntegrationAdminBootstrap::PAGE_SLUG,
            'ud_status'=>$status === 'error' ? 'error' : 'success',
            'ud_message'=>mb_substr(strip_tags($message), 0, 500),
        ], admin_url('admin.php'));
        wp_safe_redirect($url);
        exit;
    }
}
