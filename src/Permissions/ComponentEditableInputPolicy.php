<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

/** UD-096 exposes only explicitly released component inputs to content-only roles. */
final class ComponentEditableInputPolicy
{
    /** @param array<string,mixed> $component @return array<string,true> */
    public function allowedPaths(array $component): array
    {
        $allowed = [];
        foreach ((array) ($component['Inputs'] ?? []) as $input) {
            if (!is_array($input)) { continue; }
            $section = trim((string) ($input['SectionKey'] ?? ''));
            $field = trim((string) ($input['Field'] ?? ''));
            if ($section === '' || $field === '') { continue; }
            if (!preg_match('/^[A-Za-z][A-Za-z0-9_-]{0,79}$/', $field)) { continue; }
            $allowed[$section . '.' . $field] = true;
        }
        return $allowed;
    }

    /**
     * @param array<string,mixed> $overrides path => value
     * @param array<string,mixed> $component
     * @return array<string,mixed>
     */
    public function filter(array $overrides, array $component): array
    {
        $allowed = $this->allowedPaths($component);
        $result = [];
        foreach ($overrides as $path => $value) {
            if (isset($allowed[(string) $path])) { $result[(string) $path] = $value; }
        }
        ksort($result);
        return $result;
    }
}
