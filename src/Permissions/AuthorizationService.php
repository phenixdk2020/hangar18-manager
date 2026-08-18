<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

use Hangar18\UltimateDesigner\Contracts\SecurityGate;

/** Resolves named actions to capabilities and applies optional datatype scope. */
final class AuthorizationService
{
    private SecurityGate $gate;
    private CapabilityCatalog $capabilities;
    private DomainScopePolicy $domains;

    public function __construct(SecurityGate $gate, ?CapabilityCatalog $capabilities = null, ?DomainScopePolicy $domains = null)
    {
        $this->gate = $gate;
        $this->capabilities = $capabilities ?? new CapabilityCatalog();
        $this->domains = $domains ?? new DomainScopePolicy();
    }

    /** @param array<string,mixed>|null $roleDefinition */
    public function can(string $action, ?string $dataType = null, ?array $roleDefinition = null): bool
    {
        if (!$this->gate->can($this->capabilities->forAction($action))) { return false; }
        if ($dataType === null || $dataType === '') { return true; }
        if ($roleDefinition === null) { return false; }
        return $this->domains->canRoleAccess($roleDefinition, $dataType);
    }
}
