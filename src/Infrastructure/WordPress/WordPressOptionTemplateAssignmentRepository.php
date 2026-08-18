<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\TemplateAssignmentRepository;
use RuntimeException;

final class WordPressOptionTemplateAssignmentRepository implements TemplateAssignmentRepository
{
    public const OPTION = 'hangar18_manager_template_assignments_v1';
    private const MAX_ASSIGNMENTS = 200;

    /** @return list<array<string,mixed>> */
    public function all(): array
    {
        $stored = get_option(self::OPTION, []);
        if (!is_array($stored)) {
            return [];
        }
        $result = [];
        foreach ($stored as $assignment) {
            if (is_array($assignment) && (string) ($assignment['Id'] ?? '') !== '') {
                $result[] = $assignment;
            }
        }
        return $result;
    }

    /** @param array<string,mixed> $assignment @return array<string,mixed> */
    public function save(array $assignment): array
    {
        $id = (string) ($assignment['Id'] ?? '');
        if ($id === '') {
            throw new RuntimeException('Template assignment Id is required.');
        }
        $all = $this->all();
        $found = false;
        foreach ($all as $index => $existing) {
            if (($existing['Id'] ?? '') === $id) {
                $all[$index] = $assignment;
                $found = true;
                break;
            }
        }
        if (!$found) {
            if (count($all) >= self::MAX_ASSIGNMENTS) {
                throw new RuntimeException('Maximum number of template assignments reached.');
            }
            $all[] = $assignment;
        }
        update_option(self::OPTION, array_values($all), false);
        return $assignment;
    }

    public function delete(string $assignmentId): void
    {
        $all = array_values(array_filter($this->all(), static fn(array $item): bool => ($item['Id'] ?? '') !== $assignmentId));
        update_option(self::OPTION, $all, false);
    }
}
