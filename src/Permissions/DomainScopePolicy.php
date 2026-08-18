<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

/** UD-097 restricts role access to selected Dynamic CMS datatype keys. */
final class DomainScopePolicy
{
    /** @param list<string> $domains */
    public function canAccess(array $domains, string $dataType): bool
    {
        $dataType = strtolower(trim($dataType));
        if ($dataType === '') { return false; }
        $normalized = [];
        foreach ($domains as $domain) {
            $domain = strtolower(trim((string) $domain));
            if ($domain !== '') { $normalized[$domain] = true; }
        }
        return isset($normalized['*']) || isset($normalized[$dataType]);
    }

    /** @param array<string,mixed> $roleDefinition */
    public function canRoleAccess(array $roleDefinition, string $dataType): bool
    {
        return $this->canAccess(array_values((array) ($roleDefinition['Domains'] ?? [])), $dataType);
    }
}
