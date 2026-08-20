<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;
use WP_Post;

/** Dry-run planning plus explicit, safety-backed B2 full/selective restore. */
final class SiteBackupRestoreService
{
    public const AUDIT_OPTION = 'hangar18_manager_site_backup_restore_audit_v1';
    private const LOCK_OPTION = 'hangar18_manager_site_backup_restore_lock_v1';
    private const PLAN_TTL = 900;

    private SiteBackupPackageService $packages;
    private SiteBackupSnapshotCollector $collector;
    private SiteBackupManifestService $canonical;

    public function __construct(
        ?SiteBackupPackageService $packages = null,
        ?SiteBackupSnapshotCollector $collector = null,
        ?SiteBackupManifestService $canonical = null
    ) {
        $this->packages = $packages ?? new SiteBackupPackageService();
        $this->collector = $collector ?? new SiteBackupSnapshotCollector();
        $this->canonical = $canonical ?? new SiteBackupManifestService();
    }

    /** @return array<string,mixed> */
    public function plan(string $backupId, string $scope = 'full', string $pageSlug = ''): array
    {
        $scope = $scope === 'page' ? 'page' : 'full';
        $pageSlug = $scope === 'page' ? sanitize_title($pageSlug) : '';
        $validation = $this->packages->validate($backupId);
        $package = $this->packages->read($backupId);
        $manifest = $package['Manifest'];
        $payloads = $package['Payloads'];
        $errors = (array)($validation['Errors'] ?? []);
        $warnings = (array)($validation['Warnings'] ?? []);

        $sourceHost = (string)($manifest['SourceSite']['Host'] ?? '');
        $currentHost = function_exists('home_url') ? (string)(parse_url((string)home_url('/'), PHP_URL_HOST) ?: '') : '';
        if ($sourceHost !== '' && $currentHost !== '' && strcasecmp($sourceHost, $currentHost) !== 0) {
            $warnings[] = 'Backuppen stammer fra et andet hostnavn (' . $sourceHost . ' → ' . $currentHost . '). Media/URL mapping udføres under restore.';
        }

        $pages = (array)($payloads['managed-site']['Pages'] ?? []);
        $targetPages = [];
        foreach ($pages as $page) {
            if (!is_array($page)) {
                continue;
            }
            $slug = sanitize_title((string)($page['Slug'] ?? ''));
            if ($slug === '') {
                continue;
            }
            if ($scope === 'page' && $slug !== $pageSlug) {
                continue;
            }
            $existing = function_exists('get_page_by_path') ? get_page_by_path($slug, OBJECT, 'page') : null;
            $targetPages[] = [
                'SourceId'=>(int)($page['ID'] ?? 0),
                'Slug'=>$slug,
                'Title'=>(string)($page['Title'] ?? ''),
                'Action'=>$existing instanceof WP_Post ? 'update-existing' : 'create-missing',
                'TargetId'=>$existing instanceof WP_Post ? (int)$existing->ID : 0,
            ];
        }
        if ($scope === 'page' && ($pageSlug === '' || !$targetPages)) {
            $errors[] = 'Den valgte side findes ikke i backuppakken.';
        }

        $mediaActions = [];
        $uploads = function_exists('wp_upload_dir') ? wp_upload_dir() : [];
        $baseDir = empty($uploads['basedir']) ? '' : rtrim((string)$uploads['basedir'], '/\\');
        foreach ((array)($manifest['Media'] ?? []) as $media) {
            if (!is_array($media)) {
                continue;
            }
            $relative = $this->safeRelativePath((string)($media['RelativePath'] ?? ''));
            $destination = $relative !== '' && $baseDir !== '' ? $baseDir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative) : '';
            $action = 'copy-new';
            if ($destination !== '' && is_file($destination)) {
                $actual = hash_file('sha256', $destination);
                $action = is_string($actual) && hash_equals(strtolower((string)($media['Sha256'] ?? '')), strtolower($actual)) ? 'reuse-same-sha' : 'copy-collision-safe';
            }
            $mediaActions[] = ['MediaId'=>(int)($media['MediaId'] ?? 0),'RelativePath'=>$relative,'Action'=>$action];
        }

        $stateHash = $this->currentStateHash();
        $plan = [
            'SchemaVersion'=>'1.0',
            'BackupId'=>$backupId,
            'ManifestSha256'=>(string)($manifest['ManifestSha256'] ?? ''),
            'Scope'=>$scope,
            'PageSlug'=>$pageSlug,
            'CurrentStateHash'=>$stateHash,
            'CreatedUtc'=>gmdate('c'),
            'ExpiresAt'=>time() + self::PLAN_TTL,
            'Pages'=>$targetPages,
            'Media'=>$mediaActions,
            'Errors'=>array_values(array_unique($errors)),
            'Warnings'=>array_values(array_unique($warnings)),
        ];
        $plan['Executable'] = $plan['Errors'] === [];
        $plan['Token'] = $this->signPlan($plan);
        return $plan;
    }

    /** @return array<string,mixed> */
    public function restoreFull(string $planToken): array
    {
        $plan = $this->verifyPlan($planToken, 'full');
        return $this->execute($plan, 'full', '');
    }

    /** @return array<string,mixed> */
    public function restorePage(string $planToken): array
    {
        $plan = $this->verifyPlan($planToken, 'page');
        return $this->execute($plan, 'page', sanitize_title((string)($plan['PageSlug'] ?? '')));
    }

    /** @return array<int,array<string,mixed>> */
    public function audit(int $limit = 30): array
    {
        if (!function_exists('get_option')) {
            return [];
        }
        $value = get_option(self::AUDIT_OPTION, []);
        return is_array($value) ? array_slice(array_values($value), 0, max(1, $limit)) : [];
    }

    /** @return array<string,mixed> */
    private function execute(array $plan, string $scope, string $pageSlug): array
    {
        if (empty($plan['Executable'])) {
            throw new RuntimeException('Restore-planen er ikke eksekverbar.');
        }
        $this->acquireLock();
        try {
            $backupId = (string)$plan['BackupId'];
            $package = $this->packages->read($backupId);
            $manifest = $package['Manifest'];
            $payloads = $package['Payloads'];
            $safety = $this->packages->create('B2 sikkerhedsbackup før ' . ($scope === 'full' ? 'fuld restore' : 'side-restore') . ' fra ' . $backupId);

            [$idMap, $urlMap] = $this->restoreMedia($manifest, (string)$package['Directory'], $backupId);
            $pageResult = $this->restorePages((array)($payloads['managed-site']['Pages'] ?? []), $idMap, $urlMap, $scope === 'page' ? $pageSlug : '');

            if ($scope === 'full') {
                $this->restorePluginOptions((array)($payloads['plugin-metadata']['Options'] ?? []), $idMap, $urlMap);
                $this->restoreDataEntries((array)($payloads['forms-polls-data']['DataEntries'] ?? []), $idMap, $urlMap);
            } else {
                $this->restoreSelectivePageEditor($pageSlug, (array)($payloads['plugin-metadata']['Options'] ?? []), $idMap, $urlMap);
                $this->restoreSelectivePageVersions($pageSlug, (array)($payloads['plugin-metadata']['Options'] ?? []), $idMap, $urlMap);
            }

            $audit = [
                'Utc'=>gmdate('c'),
                'Mode'=>$scope === 'full' ? 'full-restore' : 'page-restore',
                'BackupId'=>$backupId,
                'PageSlug'=>$pageSlug,
                'SafetyBackupId'=>(string)($safety['BackupId'] ?? ''),
                'Pages'=>$pageResult,
                'MediaMapped'=>count($idMap),
                'UserId'=>function_exists('get_current_user_id') ? (int)get_current_user_id() : 0,
            ];
            $this->appendAudit($audit);
            return $audit;
        } finally {
            $this->releaseLock();
        }
    }

    /** @return array{0:array<int,int>,1:array<string,string>} */
    private function restoreMedia(array $manifest, string $packageDir, string $backupId): array
    {
        $uploads = function_exists('wp_upload_dir') ? wp_upload_dir() : [];
        if (!empty($uploads['error']) || empty($uploads['basedir']) || empty($uploads['baseurl'])) {
            throw new RuntimeException('Uploads-mappen er ikke tilgængelig til media-restore.');
        }
        $baseDir = rtrim((string)$uploads['basedir'], '/\\');
        $baseUrl = rtrim((string)$uploads['baseurl'], '/');
        $idMap = [];
        $urlMap = [];

        $mediaMapPayload = [];
        try {
            $package = $this->packages->read($backupId);
            $mediaMapPayload = (array)($package['Payloads']['media-map'] ?? []);
        } catch (\Throwable $error) {
            $mediaMapPayload = [];
        }

        foreach ((array)($manifest['Media'] ?? []) as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $oldId = (int)($entry['MediaId'] ?? 0);
            $relative = $this->safeRelativePath((string)($entry['RelativePath'] ?? ''));
            if ($oldId <= 0 || $relative === '') {
                continue;
            }
            $source = $packageDir . DIRECTORY_SEPARATOR . 'media' . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
            if (!is_file($source)) {
                throw new RuntimeException('Media mangler i package: ' . $relative);
            }
            $destinationRelative = $relative;
            $destination = $baseDir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $destinationRelative);
            $this->mkdir(dirname($destination));
            $expectedSha = strtolower((string)($entry['Sha256'] ?? ''));
            $reuse = false;
            if (is_file($destination)) {
                $actual = hash_file('sha256', $destination);
                $reuse = is_string($actual) && hash_equals($expectedSha, strtolower($actual));
                if (!$reuse) {
                    [$destinationRelative,$destination] = $this->collisionSafeMediaPath($relative, $baseDir, $backupId);
                }
            }
            if (!$reuse && !is_file($destination) && !copy($source, $destination)) {
                throw new RuntimeException('Media kunne ikke kopieres: ' . $relative);
            }

            $newUrl = $baseUrl . '/' . str_replace(' ', '%20', $destinationRelative);
            $newId = $this->resolveOrCreateAttachment($destination, $destinationRelative, $newUrl, (string)($entry['MimeType'] ?? ''));
            if ($newId > 0) {
                $idMap[$oldId] = $newId;
            }
            $oldUrl = (string)($mediaMapPayload[$oldId]['Url'] ?? '');
            if ($oldUrl !== '') {
                $urlMap[$oldUrl] = $newUrl;
            }

            // Derivatives are copied only when their packaged relative path is free
            // or byte-identical. WordPress can regenerate sizes for renamed originals.
            foreach ((array)($entry['Derivatives'] ?? []) as $derivative) {
                if (!is_array($derivative)) {
                    continue;
                }
                $dRel = $this->safeRelativePath((string)($derivative['RelativePath'] ?? ''));
                if ($dRel === '') {
                    continue;
                }
                $dSource = $packageDir . DIRECTORY_SEPARATOR . 'media' . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $dRel);
                $dDest = $baseDir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $dRel);
                if (!is_file($dSource)) {
                    continue;
                }
                if (is_file($dDest)) {
                    $actual = hash_file('sha256', $dDest);
                    if (!is_string($actual) || !hash_equals(strtolower((string)($derivative['Sha256'] ?? '')), strtolower($actual))) {
                        continue;
                    }
                } else {
                    $this->mkdir(dirname($dDest));
                    @copy($dSource, $dDest);
                }
            }
        }
        return [$idMap,$urlMap];
    }

    private function resolveOrCreateAttachment(string $path, string $relative, string $url, string $mime): int
    {
        if (function_exists('attachment_url_to_postid')) {
            $existing = (int)attachment_url_to_postid($url);
            if ($existing > 0) {
                return $existing;
            }
        }
        if (!function_exists('wp_insert_attachment')) {
            return 0;
        }
        $id = wp_insert_attachment([
            'post_mime_type'=>$mime !== '' ? $mime : (function_exists('wp_check_filetype') ? (string)(wp_check_filetype($path)['type'] ?? '') : ''),
            'post_title'=>sanitize_text_field(pathinfo($path, PATHINFO_FILENAME)),
            'post_content'=>'',
            'post_status'=>'inherit',
        ], $path, 0, true);
        if (function_exists('is_wp_error') && is_wp_error($id)) {
            throw new RuntimeException('Attachment kunne ikke oprettes: ' . $id->get_error_message());
        }
        $id = (int)$id;
        if ($id > 0 && function_exists('update_post_meta')) {
            update_post_meta($id, '_wp_attached_file', $relative);
        }
        if ($id > 0 && function_exists('wp_generate_attachment_metadata') && function_exists('wp_update_attachment_metadata')) {
            $meta = wp_generate_attachment_metadata($id, $path);
            if (is_array($meta)) {
                wp_update_attachment_metadata($id, $meta);
            }
        }
        return $id;
    }

    /** @param array<int,array<string,mixed>> $pages @param array<int,int> $idMap @param array<string,string> $urlMap @return array<int,array<string,mixed>> */
    private function restorePages(array $pages, array $idMap, array $urlMap, string $onlySlug): array
    {
        $pageIdMap = [];
        $records = [];
        foreach ($pages as $page) {
            if (!is_array($page)) {
                continue;
            }
            $slug = sanitize_title((string)($page['Slug'] ?? ''));
            if ($slug === '' || ($onlySlug !== '' && $slug !== $onlySlug)) {
                continue;
            }
            $existing = function_exists('get_page_by_path') ? get_page_by_path($slug, OBJECT, 'page') : null;
            $content = (string)$this->remapValue((string)($page['Content'] ?? ''), $idMap, $urlMap, 'Content');
            $data = [
                'post_type'=>'page',
                'post_title'=>sanitize_text_field((string)($page['Title'] ?? $slug)),
                'post_status'=>$this->safeStatus((string)($page['Status'] ?? 'draft')),
                'post_excerpt'=>(string)($page['Excerpt'] ?? ''),
                'post_content'=>$content,
                'post_parent'=>0,
            ];
            if ($existing instanceof WP_Post) {
                $data['ID'] = (int)$existing->ID;
                $result = wp_update_post($data, true);
                $action = 'updated';
                $targetId = (int)$existing->ID;
            } else {
                $data['post_name'] = $slug;
                $result = wp_insert_post($data, true);
                $action = 'created';
                $targetId = (int)$result;
            }
            if (function_exists('is_wp_error') && is_wp_error($result)) {
                throw new RuntimeException('Side-restore fejlede for ' . $slug . ': ' . $result->get_error_message());
            }
            if ($targetId <= 0) {
                throw new RuntimeException('Side-restore gav intet Page ID for ' . $slug . '.');
            }
            $oldId = (int)($page['ID'] ?? 0);
            if ($oldId > 0) {
                $pageIdMap[$oldId] = $targetId;
            }
            $this->restoreMeta($targetId, (array)($page['Meta'] ?? []), $idMap, $urlMap);
            $featured = (int)($page['FeaturedId'] ?? 0);
            $featured = $idMap[$featured] ?? $featured;
            if ($featured > 0 && function_exists('set_post_thumbnail')) {
                set_post_thumbnail($targetId, $featured);
            } elseif ($featured <= 0 && function_exists('delete_post_thumbnail')) {
                delete_post_thumbnail($targetId);
            }
            $records[] = ['Slug'=>$slug,'TargetId'=>$targetId,'Action'=>$action,'SourceId'=>$oldId];
        }

        foreach ($pages as $page) {
            if (!is_array($page)) {
                continue;
            }
            $slug = sanitize_title((string)($page['Slug'] ?? ''));
            if ($slug === '' || ($onlySlug !== '' && $slug !== $onlySlug)) {
                continue;
            }
            $oldId = (int)($page['ID'] ?? 0);
            $targetId = $pageIdMap[$oldId] ?? 0;
            $oldParent = (int)($page['ParentId'] ?? 0);
            $newParent = $pageIdMap[$oldParent] ?? 0;
            if ($targetId > 0 && $newParent > 0) {
                wp_update_post(['ID'=>$targetId,'post_parent'=>$newParent], true);
            }
        }
        return $records;
    }

    /** @param array<string,mixed> $options @param array<int,int> $idMap @param array<string,string> $urlMap */
    private function restorePluginOptions(array $options, array $idMap, array $urlMap): void
    {
        foreach ($options as $name=>$value) {
            $name = (string)$name;
            if (!$this->isRestorableOption($name) || !function_exists('update_option')) {
                continue;
            }
            update_option($name, $this->remapValue($value, $idMap, $urlMap, $name), false);
        }
    }

    /** @param array<int,array<string,mixed>> $entries @param array<int,int> $idMap @param array<string,string> $urlMap */
    private function restoreDataEntries(array $entries, array $idMap, array $urlMap): void
    {
        foreach ($entries as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $oldId = (int)($entry['ID'] ?? 0);
            $existing = $oldId > 0 && function_exists('get_post') ? get_post($oldId) : null;
            $data = [
                'post_type'=>'h18_data_entry',
                'post_title'=>sanitize_text_field((string)($entry['Title'] ?? 'Data entry')),
                'post_status'=>$this->safeStatus((string)($entry['Status'] ?? 'draft')),
                'post_content'=>(string)$this->remapValue((string)($entry['Content'] ?? ''), $idMap, $urlMap, 'Content'),
                'post_excerpt'=>(string)($entry['Excerpt'] ?? ''),
            ];
            if ($existing instanceof WP_Post && $existing->post_type === 'h18_data_entry') {
                $data['ID'] = $oldId;
                $result = wp_update_post($data, true);
                $targetId = $oldId;
            } else {
                $result = wp_insert_post($data, true);
                $targetId = (int)$result;
            }
            if (function_exists('is_wp_error') && is_wp_error($result)) {
                throw new RuntimeException('Data entry restore fejlede: ' . $result->get_error_message());
            }
            if ($targetId > 0) {
                $this->restoreMeta($targetId, (array)($entry['Meta'] ?? []), $idMap, $urlMap);
            }
        }
    }

    /** @param array<string,mixed> $options @param array<int,int> $idMap @param array<string,string> $urlMap */
    private function restoreSelectivePageEditor(string $slug, array $options, array $idMap, array $urlMap): void
    {
        $name = 'hangar18_manager_pages_v1';
        $source = $options[$name] ?? null;
        if (!is_array($source) || !isset($source[$slug]) || !function_exists('get_option') || !function_exists('update_option')) {
            return;
        }
        $current = get_option($name, []);
        $current = is_array($current) ? $current : [];
        $current[$slug] = $this->remapValue($source[$slug], $idMap, $urlMap, $slug);
        update_option($name, $current, false);
    }

    /** @param array<string,mixed> $options @param array<int,int> $idMap @param array<string,string> $urlMap */
    private function restoreSelectivePageVersions(string $slug, array $options, array $idMap, array $urlMap): void
    {
        $name = 'hangar18_manager_page_versions_v1';
        $source = $options[$name] ?? null;
        if (!is_array($source) || !isset($source[$slug]) || !function_exists('get_option') || !function_exists('update_option')) {
            return;
        }
        $current = get_option($name, []);
        $current = is_array($current) ? $current : [];
        $current[$slug] = $this->remapValue($source[$slug], $idMap, $urlMap, $slug);
        update_option($name, $current, false);
    }

    /** @param array<string,mixed> $meta @param array<int,int> $idMap @param array<string,string> $urlMap */
    private function restoreMeta(int $postId, array $meta, array $idMap, array $urlMap): void
    {
        if (!function_exists('update_post_meta')) {
            return;
        }
        foreach ($meta as $key=>$value) {
            $key = (string)$key;
            if ($key === '' || str_starts_with($key, '_edit_')) {
                continue;
            }
            update_post_meta($postId, $key, $this->remapValue($value, $idMap, $urlMap, $key));
        }
    }

    /** @param mixed $value @param array<int,int> $idMap @param array<string,string> $urlMap @return mixed */
    private function remapValue($value, array $idMap, array $urlMap, string $key)
    {
        if (is_array($value)) {
            $result = [];
            foreach ($value as $childKey=>$child) {
                $result[$childKey] = $this->remapValue($child, $idMap, $urlMap, (string)$childKey);
            }
            return $result;
        }
        if ((is_int($value) || (is_string($value) && ctype_digit($value))) && preg_match('/(media|image|attachment|featured|logo|icon|background|thumbnail)/i', $key)) {
            $old = (int)$value;
            return $idMap[$old] ?? $value;
        }
        if (is_string($value)) {
            if ($urlMap) {
                $value = strtr($value, $urlMap);
            }
            foreach ($idMap as $old=>$new) {
                $value = preg_replace('/((?:media|image|attachment|featured|thumbnail)[_-]?(?:id)?["\'=: ]+)' . preg_quote((string)$old, '/') . '(\b)/i', '$1' . $new . '$2', $value) ?? $value;
            }
        }
        return $value;
    }

    /** @return array<string,mixed> */
    private function verifyPlan(string $token, string $requiredScope): array
    {
        $parts = explode('.', trim($token), 2);
        if (count($parts) !== 2) {
            throw new RuntimeException('Restore-plan token har ugyldigt format.');
        }
        [$encoded,$signature] = $parts;
        $expected = hash_hmac('sha256', $encoded, $this->secret());
        if (!hash_equals($expected, $signature)) {
            throw new RuntimeException('Restore-plan token signatur er ugyldig.');
        }
        $json = $this->base64UrlDecode($encoded);
        $plan = json_decode($json, true);
        if (!is_array($plan) || ($plan['Scope'] ?? '') !== $requiredScope || (int)($plan['ExpiresAt'] ?? 0) < time()) {
            throw new RuntimeException('Restore-planen er ugyldig eller udløbet.');
        }
        $validation = $this->packages->validate((string)($plan['BackupId'] ?? ''));
        if (empty($validation['Valid'])) {
            throw new RuntimeException('Backuppakken er ikke længere valid.');
        }
        $package = $this->packages->read((string)$plan['BackupId']);
        if (!hash_equals((string)($plan['ManifestSha256'] ?? ''), (string)($package['Manifest']['ManifestSha256'] ?? ''))) {
            throw new RuntimeException('Backuppakken har ændret sig siden dry-run.');
        }
        if (!hash_equals((string)($plan['CurrentStateHash'] ?? ''), $this->currentStateHash())) {
            throw new RuntimeException('Den nuværende side/site-state har ændret sig siden dry-run. Kør dry-run igen.');
        }
        return $plan;
    }

    /** @param array<string,mixed> $plan */
    private function signPlan(array $plan): string
    {
        $copy = $plan;
        unset($copy['Token']);
        $encoded = $this->base64UrlEncode($this->canonical->canonicalJson($copy));
        return $encoded . '.' . hash_hmac('sha256', $encoded, $this->secret());
    }

    private function currentStateHash(): string
    {
        $snapshot = $this->collector->collect();
        $payloads = (array)($snapshot['Payloads'] ?? []);
        $stable = [
            'Pages'=>(array)($payloads['managed-site']['Pages'] ?? []),
            'Options'=>(array)($payloads['plugin-metadata']['Options'] ?? []),
            'DataEntries'=>(array)($payloads['forms-polls-data']['DataEntries'] ?? []),
        ];
        return hash('sha256', $this->canonical->canonicalJson($stable));
    }

    private function secret(): string
    {
        if (function_exists('wp_salt')) {
            return (string)wp_salt('auth');
        }
        if (defined('AUTH_SALT') && (string)AUTH_SALT !== '') {
            return (string)AUTH_SALT;
        }
        $site = function_exists('home_url') ? (string)home_url('/') : 'hangar18';
        return hash('sha256', 'h18-b2|' . $site . '|' . __FILE__);
    }

    private function acquireLock(): void
    {
        if (function_exists('add_option')) {
            if (!add_option(self::LOCK_OPTION, ['Utc'=>gmdate('c'),'UserId'=>function_exists('get_current_user_id')?(int)get_current_user_id():0], '', false)) {
                throw new RuntimeException('En anden B2 restore ser ud til at køre allerede.');
            }
            return;
        }
        if (function_exists('get_option') && get_option(self::LOCK_OPTION, false)) {
            throw new RuntimeException('En anden B2 restore ser ud til at køre allerede.');
        }
        if (function_exists('update_option')) {
            update_option(self::LOCK_OPTION, ['Utc'=>gmdate('c')], false);
        }
    }

    private function releaseLock(): void
    {
        if (function_exists('delete_option')) {
            delete_option(self::LOCK_OPTION);
        }
    }

    /** @param array<string,mixed> $entry */
    private function appendAudit(array $entry): void
    {
        if (!function_exists('get_option') || !function_exists('update_option')) {
            return;
        }
        $items = get_option(self::AUDIT_OPTION, []);
        $items = is_array($items) ? array_values($items) : [];
        array_unshift($items, $entry);
        update_option(self::AUDIT_OPTION, array_slice($items, 0, 100), false);
    }

    private function isRestorableOption(string $name): bool
    {
        if (!(str_starts_with($name, 'hangar18_') || str_starts_with($name, 'h18_'))) {
            return false;
        }
        return !preg_match('/(_transient|update_lock|update_state|notice_|backup_restore_audit|site_backup_catalog|site_backup_restore)/', $name);
    }

    private function safeStatus(string $status): string
    {
        return in_array($status, ['publish','draft','private','pending'], true) ? $status : 'draft';
    }

    /** @return array{0:string,1:string} */
    private function collisionSafeMediaPath(string $relative, string $baseDir, string $backupId): array
    {
        $dir = dirname($relative);
        $name = pathinfo($relative, PATHINFO_FILENAME);
        $ext = pathinfo($relative, PATHINFO_EXTENSION);
        $suffix = strtolower(str_replace('H18-BACKUP-', 'b', $backupId));
        for ($i=1; $i<=999; $i++) {
            $candidateName = $name . '-h18-' . $suffix . ($i > 1 ? '-' . $i : '') . ($ext !== '' ? '.' . $ext : '');
            $candidateRel = ($dir === '.' ? '' : $dir . '/') . $candidateName;
            $candidate = $baseDir . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $candidateRel);
            if (!file_exists($candidate)) {
                return [$candidateRel,$candidate];
            }
        }
        throw new RuntimeException('Kunne ikke finde collision-safe filnavn for media: ' . $relative);
    }

    private function safeRelativePath(string $path): string
    {
        $path = str_replace('\\', '/', trim($path));
        if ($path === '' || str_starts_with($path, '/') || preg_match('/^[A-Za-z]:\//', $path) || preg_match('#(^|/)\.\.(/|$)#', $path)) {
            return '';
        }
        return trim($path, '/');
    }

    private function mkdir(string $dir): void
    {
        if (is_dir($dir)) {
            return;
        }
        $ok = function_exists('wp_mkdir_p') ? wp_mkdir_p($dir) : mkdir($dir, 0775, true);
        if (!$ok && !is_dir($dir)) {
            throw new RuntimeException('Mappe kunne ikke oprettes: ' . $dir);
        }
    }

    private function base64UrlEncode(string $value): string
    {
        return rtrim(strtr(base64_encode($value), '+/', '-_'), '=');
    }

    private function base64UrlDecode(string $value): string
    {
        $padding = strlen($value) % 4;
        if ($padding) {
            $value .= str_repeat('=', 4 - $padding);
        }
        $decoded = base64_decode(strtr($value, '-_', '+/'), true);
        if (!is_string($decoded)) {
            throw new RuntimeException('Restore-plan token kunne ikke afkodes.');
        }
        return $decoded;
    }
}
