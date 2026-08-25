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

        // Public runtimes. v0.9.1 adds physical 120-unit geometry parity while
        // the existing 12-column runtime remains a compatibility fallback.
        if (
            function_exists('is_admin') &&
            function_exists('add_filter') &&
            !is_admin()
        ) {
            \Hangar18\UltimateDesigner\Event\EventArchiveRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\LegoLayoutFrontendRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\LegoStackFrontendRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\ImageElementFrontendRuntime::register();
            \Hangar18\UltimateDesigner\Frontend\PhysicalCanvasFrontendRuntime::register();
        }

        // Admin-only tooling. v0.9.x keeps one canonical layout model. The
        // physical canvas controller adds geometry/history/re-parenting after
        // the canonical engine. v0.9.2 observes Save/Restore end-to-end without
        // taking ownership of editor or restore mutations.
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
            \Hangar18\UltimateDesigner\Admin\EditorPhysicalCanvasAdminController::register();
            \Hangar18\UltimateDesigner\Admin\SaveRestoreDiagnosticAdminController::register();
        }
    }
}
