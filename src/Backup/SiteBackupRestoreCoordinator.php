<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;

/**
 * Safety coordinator around the B2 restore engine.
 *
 * Keeps the existing signed-plan restore motor authoritative while adding
 * package security preflight, stale-lock recovery and failure audit that
 * points at the safety backup created by the core restore.
 */
final class SiteBackupRestoreCoordinator
{
    private const LOCK_OPTION = 'hangar18_manager_site_backup_restore_lock_v1';
    private const LEGO_SPACING_OPTION = 'hangar18_ultimate_designer_lego_spacing_v2';
    private const STALE_LOCK_SECONDS = 1800;

    private SiteBackupPackageService $packages;
    private SiteBackupRestoreService $restore;

    public function __construct(?SiteBackupPackageService $packages = null, ?SiteBackupRestoreService $restore = null)
    {
        $this->packages = $packages ?? new SiteBackupPackageService();
        $this->restore = $restore ?? new SiteBackupRestoreService($this->packages);
    }

    /** @return array<string,mixed> */
    public function plan(string $backupId, string $scope = 'full', string $pageSlug = ''): array
    {
        $package = $this->packages->read($backupId);
        SiteBackupSecurityPolicy::assertManifestSafe((array) ($package['Manifest'] ?? []));
        return $this->restore->plan($backupId, $scope, $pageSlug);
    }

    /** @return array<string,mixed> */
    public function restoreFull(string $planToken): array
    {
        return $this->runRestore(static fn(SiteBackupRestoreService $service): array => $service->restoreFull($planToken), 'full-restore');
    }

    /** @return array<string,mixed> */
    public function restorePage(string $planToken): array
    {
        return $this->runRestore(function (SiteBackupRestoreService $service) use ($planToken): array {
            $result = $service->restorePage($planToken);
            // v0.8.31 extension of the same B2 operation: only the selected
            // slug's LEGO editor-state is restored. The core restore has already
            // verified the signed/state-bound plan and created its safety backup.
            $result['LegoSpacingRestored'] = $this->restoreSelectiveLegoSpacing($result);
            return $result;
        }, 'page-restore');
    }

    /** @return array<int,array<string,mixed>> */
    public function audit(int $limit = 30): array
    {
        return $this->restore->audit($limit);
    }

    /** @param callable(SiteBackupRestoreService):array<string,mixed> $callback @return array<string,mixed> */
    private function runRestore(callable $callback, string $mode): array
    {
        $this->clearStaleLock();
        $before = [];
        foreach ($this->packages->listBackups() as $entry) {
            if (is_array($entry) && !empty($entry['BackupId'])) {
                $before[(string) $entry['BackupId']] = true;
            }
        }

        try {
            return $callback($this->restore);
        } catch (\Throwable $error) {
            $safetyBackupId = '';
            foreach ($this->packages->listBackups() as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                $id = (string) ($entry['BackupId'] ?? '');
                $note = (string) ($entry['Note'] ?? '');
                if ($id !== '' && !isset($before[$id]) && str_contains($note, 'B2 sikkerhedsbackup før')) {
                    $safetyBackupId = $id;
                    break;
                }
            }
            $this->appendFailureAudit([
                'Utc'=>gmdate('c'),
                'Mode'=>$mode . '-failed',
                'SafetyBackupId'=>$safetyBackupId,
                'Error'=>mb_substr($error->getMessage(), 0, 1000),
                'UserId'=>function_exists('get_current_user_id') ? (int) get_current_user_id() : 0,
            ]);
            $suffix = $safetyBackupId !== '' ? ' Sikkerhedsbackup: ' . $safetyBackupId . '.' : '';
            throw new RuntimeException('B2 restore fejlede: ' . $error->getMessage() . $suffix, 0, $error);
        }
    }

    /** @param array<string,mixed> $restoreResult */
    private function restoreSelectiveLegoSpacing(array $restoreResult): bool
    {
        if (!function_exists('get_option') || !function_exists('update_option')) {
            return false;
        }
        $backupId = trim((string) ($restoreResult['BackupId'] ?? ''));
        $pageSlug = function_exists('sanitize_title')
            ? sanitize_title((string) ($restoreResult['PageSlug'] ?? ''))
            : trim((string) ($restoreResult['PageSlug'] ?? ''));
        if ($backupId === '' || $pageSlug === '') {
            return false;
        }

        $package = $this->packages->read($backupId);
        $options = (array) ($package['Payloads']['plugin-metadata']['Options'] ?? []);
        $source = $options[self::LEGO_SPACING_OPTION] ?? null;
        if (!is_array($source) || !array_key_exists($pageSlug, $source)) {
            // Older packages can legitimately predate LEGO spacing. In that
            // case selective restore preserves the current overlay rather than
            // silently deleting newer editor-state.
            return false;
        }

        $current = get_option(self::LEGO_SPACING_OPTION, []);
        $current = is_array($current) ? $current : [];
        $current[$pageSlug] = $source[$pageSlug];
        update_option(self::LEGO_SPACING_OPTION, $current, false);
        return true;
    }

    private function clearStaleLock(): void
    {
        if (!function_exists('get_option') || !function_exists('delete_option')) {
            return;
        }
        $lock = get_option(self::LOCK_OPTION, false);
        if (!is_array($lock) || empty($lock['Utc'])) {
            return;
        }
        $timestamp = strtotime((string) $lock['Utc']);
        if ($timestamp !== false && $timestamp < (time() - self::STALE_LOCK_SECONDS)) {
            delete_option(self::LOCK_OPTION);
        }
    }

    /** @param array<string,mixed> $entry */
    private function appendFailureAudit(array $entry): void
    {
        if (!function_exists('get_option') || !function_exists('update_option')) {
            return;
        }
        $items = get_option(SiteBackupRestoreService::AUDIT_OPTION, []);
        $items = is_array($items) ? array_values($items) : [];
        array_unshift($items, $entry);
        update_option(SiteBackupRestoreService::AUDIT_OPTION, array_slice($items, 0, 100), false);
    }
}
