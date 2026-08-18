<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\SecurityGate;

/**
 * WordPress adapter for the centralized security boundary.
 *
 * Legacy Hangar18 Manager currently protects its main admin operations with
 * the `edit_pages` capability and WordPress nonces. This adapter preserves
 * those primitives while removing the dependency from future domain services.
 */
final class WordPressSecurityGate implements SecurityGate
{
    public function can(string $capability): bool
    {
        $capability = trim($capability);
        return $capability !== '' && current_user_can($capability);
    }

    public function validateWriteToken(string $action, string $token): bool
    {
        $action = trim($action);
        $token = trim($token);
        if ($action === '' || $token === '') {
            return false;
        }

        return wp_verify_nonce($token, $action) !== false;
    }
}
