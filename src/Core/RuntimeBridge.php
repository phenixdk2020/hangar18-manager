<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Core;

use Hangar18\UltimateDesigner\Compatibility\CompatibilityPolicy;
use Hangar18\UltimateDesigner\Contracts\Logger;
use Hangar18\UltimateDesigner\Contracts\PageRepository;
use Hangar18\UltimateDesigner\Contracts\SchemaValidator;
use Hangar18\UltimateDesigner\Contracts\SecurityGate;

/**
 * Passive bridge between the legacy v0.5.30 runtime and the new architecture.
 *
 * The bridge exposes extracted services without registering WordPress hooks or
 * replacing any legacy handler. Vehicle, Event and Gallery are explicitly
 * forced onto the legacy runtime until their compatibility gates are removed.
 */
final class RuntimeBridge
{
    public const MODE_SHADOW = 'shadow';
    public const ROUTE_LEGACY = 'legacy';
    public const ROUTE_ARCHITECTURE_SHADOW = 'architecture-shadow';

    private Architecture $architecture;
    private PageRepository $pages;
    private SecurityGate $security;
    private Logger $logger;
    private SchemaValidator $pageSchema;

    public function __construct(
        Architecture $architecture,
        PageRepository $pages,
        SecurityGate $security,
        Logger $logger,
        SchemaValidator $pageSchema
    ) {
        $this->architecture = $architecture;
        $this->pages = $pages;
        $this->security = $security;
        $this->logger = $logger;
        $this->pageSchema = $pageSchema;
    }

    public function mode(): string
    {
        return self::MODE_SHADOW;
    }

    public function architecture(): Architecture
    {
        return $this->architecture;
    }

    public function pages(): PageRepository
    {
        return $this->pages;
    }

    public function security(): SecurityGate
    {
        return $this->security;
    }

    public function logger(): Logger
    {
        return $this->logger;
    }

    public function pageSchema(): SchemaValidator
    {
        return $this->pageSchema;
    }

    public function routeDomain(string $domain): string
    {
        if (CompatibilityPolicy::mustUseLegacyRuntime($domain)) {
            return self::ROUTE_LEGACY;
        }

        return self::ROUTE_ARCHITECTURE_SHADOW;
    }

    public function mayReplaceLegacyHandler(string $domain): bool
    {
        return false;
    }
}
