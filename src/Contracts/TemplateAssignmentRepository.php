<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface TemplateAssignmentRepository
{
    /** @return list<array<string,mixed>> */
    public function all(): array;

    /** @param array<string,mixed> $assignment @return array<string,mixed> */
    public function save(array $assignment): array;

    public function delete(string $assignmentId): void;
}
