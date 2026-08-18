<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Core\Architecture;
use Hangar18\UltimateDesigner\Core\RuntimeBridge;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;

/**
 * Creates the passive bridge using adapters compatible with v0.5.30 storage,
 * permissions and logging. Construction alone registers no WordPress hooks.
 */
final class WordPressRuntimeBridgeFactory
{
    public static function create(): RuntimeBridge
    {
        return new RuntimeBridge(
            new Architecture(),
            new LegacyOptionPageRepository(),
            new WordPressSecurityGate(),
            new LegacyOptionLogger(),
            new PageSchemaValidator()
        );
    }

    private function __construct()
    {
    }
}
