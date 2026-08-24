<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner;

final class Autoload
{
    private const PREFIX = 'Hangar18\\UltimateDesigner\\';

    public static function register(): void
    {
        spl_autoload_register(static function (string $class): void {
            if (strncmp($class, self::PREFIX, strlen(self::PREFIX)) !== 0) {
                return;
            }

            $relative = substr($class, strlen(self::PREFIX));
            if ($relative === false || $relative === '') {
                return;
            }

            $path = __DIR__ . '/' . str_replace('\\', '/', $relative) . '.php';
            if (is_file($path)) {
                require_once $path;
            }
        });

        // Diagnostics must register on both admin/AJAX and public REST requests.
        if (function_exists('add_action')) {
            \Hangar18\UltimateDesigner\Diagnostics\EditorDiagnosticRuntime::register();
        }

        // Public runtimes remain unchanged in v0.9.0.
        if (
            function_exists('is_admin') &&
            function_exists('add_filter') &&
            !is_admin()
        ) {
            \Hangar18\UltimateDesigner\Event\EventArchiveRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\LegoLayoutFrontendRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\LegoStackFrontendRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\ImageElementFrontendRuntime::register();
        }

        // Admin-only tooling. v0.9.0 makes one canonical layout engine the
        // active generic Grid/Flex render/save owner. The v0.8.90 rebuild and
        // v0.8.91 save guard stay in the package for rollback/audit only and
        // are deliberately no longer registered here.
        if (
            function_exists('is_admin') &&
            function_exists('add_action') &&
            is_admin()
        ) {
            \Hangar18\UltimateDesigner\Admin\UpdaterPostInstallVerificationAdminController::register();
            \Hangar18\UltimateDesigner\Admin\UpdaterStateConsistencyAdminController::register();
            \Hangar18\UltimateDesigner\Admin\PageVersionRestoreAdminController::register();
            \Hangar18\UltimateDesigner\Admin\EditorNavigatorAdminController::register();
            \Hangar18\UltimateDesigner\Admin\LegacyCleanupAuditAdminController::register();
            \Hangar18\UltimateDesigner\Admin\LegacyStateBackupAdminController::register();
            \Hangar18\UltimateDesigner\Admin\BackupHealthAdminController::register();
            \Hangar18\UltimateDesigner\Admin\EditorLayoutEngineAdminController::register();
        }
    }
}
