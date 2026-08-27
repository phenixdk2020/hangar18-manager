from pathlib import Path

root = Path('.')
updater_path = root / 'clean/hangar18-manager/src/Update/GitHubUpdater.php'
admin_path = root / 'clean/hangar18-manager/src/Admin/AdminController.php'

updater = updater_path.read_text(encoding='utf-8')
admin = admin_path.read_text(encoding='utf-8')

# Keep a useful rolling history of local update checkpoints.
updater = updater.replace('private const MAX_BACKUPS = 8;', 'private const MAX_BACKUPS = 12;', 1)

marker = '    public static function installNow(): void\n'
if marker not in updater:
    raise SystemExit('Updater installNow marker missing')
public_methods = r'''    /** @return array<int,array<string,mixed>> */
    public static function programBackups(): array
    {
        $history = get_option(self::BACKUP_OPTION, []);
        if (!is_array($history)) {
            return [];
        }
        $rows = array_values(array_filter($history, static fn($row): bool => is_array($row) && (string) ($row['file'] ?? '') !== ''));
        return array_reverse($rows);
    }

    /** @return array<int,array{version:string,date:string,items:array<int,string>}> */
    public static function releaseHistory(): array
    {
        $path = H18_CLEAN_DIR . 'release-history.json';
        if (!is_file($path)) {
            return [];
        }
        $decoded = json_decode((string) file_get_contents($path), true);
        if (!is_array($decoded)) {
            return [];
        }
        $rows = [];
        foreach ($decoded as $row) {
            if (!is_array($row)) {
                continue;
            }
            $version = sanitize_text_field((string) ($row['version'] ?? ''));
            if (!preg_match('/^\d+\.\d+\.\d+$/', $version)) {
                continue;
            }
            $items = [];
            foreach (is_array($row['items'] ?? null) ? $row['items'] : [] as $item) {
                $text = sanitize_text_field((string) $item);
                if ($text !== '') {
                    $items[] = $text;
                }
            }
            $rows[] = [
                'version' => $version,
                'date' => sanitize_text_field((string) ($row['date'] ?? '')),
                'items' => $items,
            ];
        }
        usort($rows, static fn(array $a, array $b): int => version_compare($b['version'], $a['version']));
        return $rows;
    }

'''
updater = updater.replace(marker, public_methods + marker, 1)

entry_marker = "        $entry = [\n            'id' => substr(hash('sha256', $filename . '|' . $sha256), 0, 20),"
if entry_marker not in updater:
    raise SystemExit('Updater backup entry marker missing')
entry_replacement = r'''        $checkpoint = self::createDesignerCheckpoint($directory, pathinfo($filename, PATHINFO_FILENAME), $targetVersion);
        if (is_wp_error($checkpoint)) {
            @unlink($path);
            return $checkpoint;
        }

        $entry = [
            'id' => substr(hash('sha256', $filename . '|' . $sha256), 0, 20),'''
updater = updater.replace(entry_marker, entry_replacement, 1)

size_marker = "            'size' => (int) filesize($path),\n        ];"
if size_marker not in updater:
    raise SystemExit('Updater backup size marker missing')
size_replacement = r'''            'size' => (int) filesize($path),
            'dataFile' => (string) ($checkpoint['file'] ?? ''),
            'dataSha256' => (string) ($checkpoint['sha256'] ?? ''),
            'dataSize' => (int) ($checkpoint['size'] ?? 0),
        ];'''
updater = updater.replace(size_marker, size_replacement, 1)

prune_marker = r'''                if ($oldFile !== '') {
                    @unlink(trailingslashit($directory) . $oldFile);
                }
'''
if prune_marker not in updater:
    raise SystemExit('Updater prune marker missing')
prune_replacement = r'''                if ($oldFile !== '') {
                    @unlink(trailingslashit($directory) . $oldFile);
                }
                $oldDataFile = basename((string) ($old['dataFile'] ?? ''));
                if ($oldDataFile !== '') {
                    @unlink(trailingslashit($directory) . $oldDataFile);
                }
'''
updater = updater.replace(prune_marker, prune_replacement, 1)

backup_dir_marker = '    private static function backupDirectory(): string\n'
if backup_dir_marker not in updater:
    raise SystemExit('Updater backupDirectory marker missing')
checkpoint_method = r'''    /** @return array{file:string,sha256:string,size:int}|\WP_Error */
    private static function createDesignerCheckpoint(string $directory, string $baseName, string $targetVersion): array|\WP_Error
    {
        try {
            \Hangar18\Clean\Model\TemplateLayoutModel::ensureMigrated();
            $payload = [
                'product' => 'Visual Designer Manager update checkpoint',
                'schemaVersion' => \Hangar18\Clean\Model\LayoutModel::SCHEMA,
                'currentVersion' => H18_CLEAN_VERSION,
                'targetVersion' => $targetVersion,
                'generatedUtc' => gmdate('c'),
                'pages' => [],
                'templates' => [],
            ];

            $pages = get_posts([
                'post_type' => 'page',
                'post_status' => 'any',
                'numberposts' => -1,
                'orderby' => 'ID',
                'order' => 'ASC',
            ]);
            foreach ($pages as $page) {
                if (!$page instanceof \WP_Post) {
                    continue;
                }
                $postId = (int) $page->ID;
                $headerChoice = \Hangar18\Clean\Model\TemplateLayoutModel::pageChoice($postId, 'header');
                $footerChoice = \Hangar18\Clean\Model\TemplateLayoutModel::pageChoice($postId, 'footer');
                $hasLayout = metadata_exists('post', $postId, \Hangar18\Clean\Model\LayoutModel::META)
                    || (int) get_post_meta($postId, \Hangar18\Clean\Model\LayoutModel::VERSION_META, true) > 0;
                if (!$hasLayout && $headerChoice === 'auto' && $footerChoice === 'auto') {
                    continue;
                }
                $payload['pages'][] = [
                    'postId' => $postId,
                    'title' => (string) $page->post_title,
                    'slug' => (string) $page->post_name,
                    'status' => (string) $page->post_status,
                    'version' => (int) get_post_meta($postId, \Hangar18\Clean\Model\LayoutModel::VERSION_META, true),
                    'model' => \Hangar18\Clean\Model\LayoutModel::get($postId),
                    'history' => \Hangar18\Clean\Model\LayoutModel::history($postId),
                    'headerChoice' => $headerChoice,
                    'footerChoice' => $footerChoice,
                ];
            }

            foreach (['header', 'footer'] as $type) {
                foreach (\Hangar18\Clean\Model\TemplateLayoutModel::all($type) as $row) {
                    $id = (string) ($row['id'] ?? '');
                    if ($id === '') {
                        continue;
                    }
                    $payload['templates'][] = [
                        'id' => $id,
                        'type' => $type,
                        'name' => (string) ($row['name'] ?? ''),
                        'active' => !empty($row['active']),
                        'isDefault' => !empty($row['isDefault']),
                        'version' => \Hangar18\Clean\Model\TemplateLayoutModel::version($id),
                        'model' => \Hangar18\Clean\Model\TemplateLayoutModel::model($id),
                        'settings' => \Hangar18\Clean\Model\TemplateLayoutModel::settings($id),
                        'history' => \Hangar18\Clean\Model\TemplateLayoutModel::history($id),
                    ];
                }
            }

            $json = wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if (!is_string($json)) {
                return new \WP_Error('h18_clean_checkpoint_json', 'Designer-data kunne ikke serialiseres til update-checkpoint.');
            }
            $filename = sanitize_file_name($baseName . '-designer-data.json');
            $path = trailingslashit($directory) . $filename;
            if (@file_put_contents($path, $json . "\n") === false || !is_file($path) || (int) filesize($path) <= 0) {
                @unlink($path);
                return new \WP_Error('h18_clean_checkpoint_write', 'Designer-data-checkpoint kunne ikke gemmes.');
            }
            $sha256 = strtolower((string) hash_file('sha256', $path));
            if (!preg_match('/^[a-f0-9]{64}$/', $sha256)) {
                @unlink($path);
                return new \WP_Error('h18_clean_checkpoint_hash', 'Designer-data-checkpointets SHA-256 kunne ikke beregnes.');
            }
            return ['file' => $filename, 'sha256' => $sha256, 'size' => (int) filesize($path)];
        } catch (\Throwable $error) {
            return new \WP_Error('h18_clean_checkpoint_exception', 'Designer-data-checkpoint fejlede: ' . $error->getMessage());
        }
    }

'''
updater = updater.replace(backup_dir_marker, checkpoint_method + backup_dir_marker, 1)

# Replace the Updates admin page with visible checkpoints and bundled release history.
start = admin.find('    public static function updates(): void\n')
end = admin.find('    public static function log(): void\n', start)
if start < 0 or end < 0:
    raise SystemExit('Admin updates method markers missing')
new_updates = r'''    public static function updates(): void
    {
        self::guard();
        $status = GitHubUpdater::status();
        $backups = GitHubUpdater::programBackups();
        $versions = GitHubUpdater::releaseHistory();
        self::open('Opdateringer', 'Tjek, installer og se update-checkpoints for Visual Designer Manager');
        echo '<div class="h18-manager-card"><h2>Version</h2><p class="h18-manager-big-version">' . esc_html(H18_CLEAN_VERSION) . '</p>';
        if ($status['ok']) {
            echo '<p>Seneste GitHub-version: <strong>' . esc_html($status['latest']) . '</strong></p>';
            echo $status['available'] ? '<p><span class="h18-manager-badge is-progress">Opdatering tilgængelig</span></p>' : '<p><span class="h18-manager-badge is-ok">Du er opdateret</span></p>';
        } else {
            echo '<p><span class="h18-manager-badge">Manifest kunne ikke læses</span></p>';
        }
        echo '<p>Downloadpakken SHA-256-verificeres. Før installation gemmes både program-ZIP og et Designer-data-checkpoint; opdateringen stoppes hvis checkpointet fejler.</p><div class="h18-manager-toolbar">';
        echo GitHubUpdater::checkButtonHtml();
        echo GitHubUpdater::installButtonHtml();
        echo '</div></div>';

        echo '<div class="h18-manager-card"><h2>Update-checkpoints</h2><p>De seneste automatiske checkpoints før plugin-opdateringer. Der beholdes op til 12.</p>';
        if (!$backups) {
            echo '<p>Ingen lokale update-checkpoints er registreret endnu.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Fra</th><th>Til</th><th>Dato</th><th>Program</th><th>Designer-data</th></tr></thead><tbody>';
            foreach ($backups as $backup) {
                $created = (string) ($backup['createdUtc'] ?? '');
                $programSize = isset($backup['size']) ? size_format((int) $backup['size']) : '—';
                $dataSize = isset($backup['dataSize']) && (int) $backup['dataSize'] > 0 ? size_format((int) $backup['dataSize']) : '—';
                echo '<tr><td><strong>' . esc_html((string) ($backup['version'] ?? '—')) . '</strong></td><td>' . esc_html((string) ($backup['targetVersion'] ?? '—')) . '</td><td>' . esc_html(self::prettyDate($created)) . '</td>';
                echo '<td><code>' . esc_html((string) ($backup['file'] ?? '—')) . '</code><br><small>' . esc_html($programSize) . '</small></td>';
                echo '<td>';
                if (!empty($backup['dataFile'])) {
                    echo '<code>' . esc_html((string) $backup['dataFile']) . '</code><br><small>' . esc_html($dataSize) . '</small>';
                } else {
                    echo '<span class="description">Ældre checkpoint · kun program-ZIP</span>';
                }
                echo '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</div>';

        echo '<div class="h18-manager-card"><h2>Versionshistorik</h2><p>Hvad de enkelte Visual Designer Manager-versioner indeholder.</p>';
        if (!$versions) {
            echo '<p>Versionshistorikken kunne ikke læses.</p>';
        } else {
            foreach ($versions as $row) {
                $version = (string) ($row['version'] ?? '');
                $current = $version === H18_CLEAN_VERSION ? ' <span class="h18-manager-badge is-ok">Installeret</span>' : '';
                echo '<details' . ($version === H18_CLEAN_VERSION ? ' open' : '') . '><summary><strong>v' . esc_html($version) . '</strong>' . $current . ' <span class="description">' . esc_html((string) ($row['date'] ?? '')) . '</span></summary>';
                echo '<ul class="h18-manager-list">';
                foreach (is_array($row['items'] ?? null) ? $row['items'] : [] as $item) {
                    echo '<li>' . esc_html((string) $item) . '</li>';
                }
                echo '</ul></details>';
            }
        }
        echo '</div>';
        self::close();
    }

'''
admin = admin[:start] + new_updates + admin[end:]

updater_path.write_text(updater, encoding='utf-8')
admin_path.write_text(admin, encoding='utf-8')
