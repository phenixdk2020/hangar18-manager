<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface SecurityGate
{
    public function can(string $capability): bool;

    /**
     * Validate the anti-CSRF token for a named write action.
     * WordPress-specific implementations may use nonces internally.
     */
    public function validateWriteToken(string $action, string $token): bool;
}
