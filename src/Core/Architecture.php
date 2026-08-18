<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Core;

use Hangar18\UltimateDesigner\Registry\ElementRegistry;
use Hangar18\UltimateDesigner\Registry\PropertyRegistry;

/**
 * Small composition root for the new architecture layer.
 *
 * It intentionally has no WordPress hooks yet. The legacy v0.5.30 plugin
 * remains the runtime authority while services are extracted and regression
 * tested one boundary at a time.
 */
final class Architecture
{
    private ElementRegistry $elements;
    private PropertyRegistry $properties;

    public function __construct(?ElementRegistry $elements = null, ?PropertyRegistry $properties = null)
    {
        $this->elements = $elements ?? new ElementRegistry();
        $this->properties = $properties ?? new PropertyRegistry();
    }

    public function elements(): ElementRegistry
    {
        return $this->elements;
    }

    public function properties(): PropertyRegistry
    {
        return $this->properties;
    }
}
