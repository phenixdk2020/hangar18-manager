<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use Hangar18\UltimateDesigner\Permissions\RoleDefinitionCatalog;
use RuntimeException;

/**
 * Explicit UD-094/097 installer. It is intentionally not invoked by the passive architecture bootstrap yet.
 */
final class WordPressRoleInstaller
{
    public const DOMAIN_OPTION = 'hangar18_ud_role_domains_v1';

    private RoleDefinitionCatalog $roles;

    public function __construct(?RoleDefinitionCatalog $roles = null)
    {
        $this->roles = $roles ?? new RoleDefinitionCatalog();
    }

    /** @return array{roles:list<string>,administrator_caps:list<string>} */
    public function install(): array
    {
        if (!function_exists('add_role') || !function_exists('get_role')) {
            throw new RuntimeException('WordPress role API is unavailable.');
        }
        $installed = [];
        $domains = [];
        foreach ($this->roles->definitions() as $slug => $definition) {
            $caps = ['read'=>true];
            foreach ($definition['Capabilities'] as $capability) { $caps[$capability] = true; }
            $role = get_role($slug);
            if ($role === null) { $role = add_role($slug, $definition['Label'], $caps); }
            if ($role !== null) {
                foreach ($caps as $capability => $grant) { $role->add_cap($capability, $grant); }
                $installed[] = $slug;
                $domains[$slug] = $definition['Domains'];
            }
        }

        $adminCaps = (new CapabilityCatalog())->all();
        $administrator = get_role('administrator');
        if ($administrator !== null) {
            foreach ($adminCaps as $capability) { $administrator->add_cap($capability, true); }
            $domains['administrator'] = ['*'];
        }
        update_option(self::DOMAIN_OPTION, $domains, false);
        return ['roles'=>$installed,'administrator_caps'=>$adminCaps];
    }

    /** @return list<string> */
    public function domainsForRole(string $role): array
    {
        $all = get_option(self::DOMAIN_OPTION, []);
        if (!is_array($all) || !is_array($all[$role] ?? null)) { return []; }
        return array_values(array_map('strval', $all[$role]));
    }
}
