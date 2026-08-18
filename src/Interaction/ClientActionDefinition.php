<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use RuntimeException;

/** UD-080 validates declarative frontend element action chains. */
final class ClientActionDefinition
{
    /** @var list<string> */
    private const TYPES = ['navigate','scroll','open-modal','toggle'];

    /** @param list<array<string,mixed>> $actions @return list<string> */
    public function validate(array $actions): array
    {
        $errors = [];
        if (count($actions) > 12) { $errors[] = 'Action chain exceeds 12 actions.'; }
        foreach (array_values($actions) as $index => $action) {
            if (!is_array($action)) { $errors[] = "Action {$index} must be an object/array."; continue; }
            $type = strtolower(trim((string) ($action['Type'] ?? '')));
            if (!in_array($type, self::TYPES, true)) { $errors[] = "Action {$index} has unsupported Type."; continue; }
            if ($type === 'navigate') {
                $url = trim((string) ($action['Url'] ?? ''));
                if (!$this->safeUrl($url)) { $errors[] = "Navigate action {$index} has unsafe URL."; }
            } else {
                $target = trim((string) ($action['TargetId'] ?? ''));
                if ($target === '' || !preg_match('/^[a-zA-Z0-9_-]{1,80}$/', $target)) { $errors[] = "Action {$index} requires safe TargetId."; }
            }
        }
        return array_values(array_unique($errors));
    }

    /** @param list<array<string,mixed>> $actions */
    public function assertValid(array $actions): void
    {
        $errors = $this->validate($actions);
        if ($errors !== []) { throw new RuntimeException('Invalid client action chain: ' . implode(' ', $errors)); }
    }

    /** @param list<array<string,mixed>> $actions */
    public function dataAttribute(array $actions): string
    {
        $this->assertValid($actions);
        $json = json_encode(array_values($actions), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        return htmlspecialchars(is_string($json) ? $json : '[]', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }

    private function safeUrl(string $url): bool
    {
        if ($url === '') { return false; }
        if (str_starts_with($url, '/') || str_starts_with($url, '#')) { return true; }
        return in_array(strtolower((string) parse_url($url, PHP_URL_SCHEME)), ['http','https'], true);
    }
}
