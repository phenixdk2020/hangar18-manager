<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

/**
 * Migration guardrails for the architecture refactor.
 *
 * Vehicle, Event and Gallery must continue to use the proven v0.5.30
 * persistence/rendering path until an explicit compatibility test proves
 * equivalent markup, CSS hooks and behaviour for the replacement path.
 */
final class CompatibilityPolicy
{
    /** @var list<string> */
    public const PROTECTED_DOMAINS = ['vehicle', 'event', 'gallery'];

    public const LEGACY_RUNTIME_VERSION = '0.5.30';

    public static function isProtectedDomain(string $domain): bool
    {
        return in_array(strtolower(trim($domain)), self::PROTECTED_DOMAINS, true);
    }

    public static function mustUseLegacyRuntime(string $domain): bool
    {
        return self::isProtectedDomain($domain);
    }

    private function __construct()
    {
    }
}
