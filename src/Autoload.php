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

        // Public EVENT-001 runtime: render-time archive classification only.
        // Admin/CLI tests keep the historical autoload-only behavior.
        if (
            function_exists('is_admin') &&
            function_exists('add_filter') &&
            !is_admin()
        ) {
            \Hangar18\UltimateDesigner\Event\EventArchiveRuntime::register();
        }

        // Admin-only compatibility/tooling layers. They do not own frontend rendering.
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
        }
    }
}
