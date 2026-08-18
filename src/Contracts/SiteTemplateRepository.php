<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

/**
 * Version-safe persistence boundary for Site Builder templates.
 *
 * Implementations store template definitions separately from legacy shell
 * content. Global assignment is metadata only; activation remains controlled
 * by the runtime compatibility layer until legacy page conversion is approved.
 */
interface SiteTemplateRepository
{
    /** @return array<string,array<string,mixed>> */
    public function all(): array;

    /** @return array<string,mixed>|null */
    public function get(string $templateId): ?array;

    /** @param array<string,mixed> $template @return array<string,mixed> */
    public function save(array $template): array;

    public function delete(string $templateId): void;

    public function assignGlobal(string $kind, ?string $templateId): void;

    public function globalAssignment(string $kind): ?string;
}
