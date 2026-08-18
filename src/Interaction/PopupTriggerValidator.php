<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use RuntimeException;

/** UD-079 validates click/time/scroll/context trigger combinations. */
final class PopupTriggerValidator
{
    /** @var list<string> */
    private const TYPES = ['click','time','scroll','context'];

    /** @param array<string,mixed> $definition @return list<string> */
    public function validate(array $definition): array
    {
        $errors = [];
        $mode = strtoupper(trim((string) ($definition['Mode'] ?? 'ANY')));
        if (!in_array($mode, ['ANY','ALL'], true)) { $errors[] = 'Trigger Mode must be ANY or ALL.'; }
        $triggers = $definition['Triggers'] ?? null;
        if (!is_array($triggers) || $triggers === [] || count($triggers) > 8) {
            $errors[] = 'Triggers must contain 1-8 entries.';
            return $errors;
        }
        foreach (array_values($triggers) as $index => $trigger) {
            if (!is_array($trigger)) { $errors[] = "Trigger {$index} must be an object/array."; continue; }
            $type = strtolower(trim((string) ($trigger['Type'] ?? '')));
            if (!in_array($type, self::TYPES, true)) { $errors[] = "Trigger {$index} has unsupported Type."; continue; }
            if ($type === 'click') {
                $target = trim((string) ($trigger['ElementId'] ?? ''));
                if ($target === '' || !preg_match('/^[a-zA-Z0-9_-]{1,80}$/', $target)) { $errors[] = "Click trigger {$index} requires a safe ElementId."; }
            } elseif ($type === 'time') {
                $delay = $trigger['DelayMs'] ?? null;
                if (!is_int($delay) || $delay < 0 || $delay > 600000) { $errors[] = "Time trigger {$index} DelayMs is invalid."; }
            } elseif ($type === 'scroll') {
                $percent = $trigger['Percent'] ?? null;
                if (!is_int($percent) || $percent < 0 || $percent > 100) { $errors[] = "Scroll trigger {$index} Percent is invalid."; }
            } else {
                $key = trim((string) ($trigger['Key'] ?? ''));
                if ($key === '' || !preg_match('/^[a-z][a-z0-9_.-]{0,79}$/i', $key)) { $errors[] = "Context trigger {$index} Key is invalid."; }
                if (!isset($trigger['Operator']) || !in_array((string) $trigger['Operator'], ['equals','not_equals','exists'], true)) { $errors[] = "Context trigger {$index} Operator is invalid."; }
            }
        }
        return array_values(array_unique($errors));
    }

    /** @param array<string,mixed> $definition */
    public function assertValid(array $definition): void
    {
        $errors = $this->validate($definition);
        if ($errors !== []) { throw new RuntimeException('Invalid popup triggers: ' . implode(' ', $errors)); }
    }
}
