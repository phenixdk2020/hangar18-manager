<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Core;

/**
 * Version metadata for the new architecture layer.
 *
 * RuntimeVersion deliberately mirrors the unchanged legacy v0.5.30 runtime.
 * ArchitectureVersion may evolve independently while the compatibility bridge
 * is introduced without changing public rendering or stored data.
 */
final class Version
{
    public const RUNTIME = '0.5.30';
    public const ARCHITECTURE = '0.1.0';
    public const PAGE_SCHEMA = '1.22';

    private function __construct()
    {
    }
}
