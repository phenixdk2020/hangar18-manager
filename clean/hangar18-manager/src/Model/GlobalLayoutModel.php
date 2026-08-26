<?php

declare(strict_types=1);

namespace Hangar18\Clean\Model;

final class GlobalLayoutModel
{
    public const MAX_HISTORY = 50;

    /** @return array<string,mixed> */
    public static function get(string $part): array
    {
        $part = self::part($part);
        $raw = get_option(self::modelOption($part), []);
        if (!is_array($raw)) {
            return LayoutModel::empty();
        }
        try {
            return LayoutModel::normalize($raw);
        } catch (\Throwable $error) {
            return LayoutModel::empty();
        }
    }

    /** @return array<string,mixed> */
    public static function settings(string $part): array
    {
        $part = self::part($part);
        $raw = get_option(self::settingsOption($part), []);
        $raw = is_array($raw) ? $raw : [];
        return [
            'enabled' => !empty($raw['enabled']),
            'sticky' => $part === 'header' && !empty($raw['sticky']),
            'overlay' => $part === 'header' && !empty($raw['overlay']),
            'contentWidth' => max(320, min(2400, (int) ($raw['contentWidth'] ?? 1440))),
        ];
    }

    /** @param array<string,mixed> $settings */
    public static function normalizeSettings(string $part, array $settings): array
    {
        $part = self::part($part);
        return [
            'enabled' => !empty($settings['enabled']),
            'sticky' => $part === 'header' && !empty($settings['sticky']),
            'overlay' => $part === 'header' && !empty($settings['overlay']),
            'contentWidth' => max(320, min(2400, (int) ($settings['contentWidth'] ?? 1440))),
        ];
    }

    /** @param array<string,mixed> $model @param array<string,mixed> $settings */
    public static function saveVersion(string $part, array $model, array $settings, int $userId, string $note): int
    {
        $part = self::part($part);
        $normalized = LayoutModel::normalize($model);
        $normalizedSettings = self::normalizeSettings($part, $settings);
        $version = self::version($part) + 1;
        $history = self::history($part);
        $history[] = [
            'version' => $version,
            'savedUtc' => gmdate('c'),
            'userId' => max(0, $userId),
            'note' => sanitize_text_field($note),
            'digest' => self::digest($normalized, $normalizedSettings),
            'model' => $normalized,
            'settings' => $normalizedSettings,
        ];
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }

        update_option(self::modelOption($part), $normalized, false);
        update_option(self::settingsOption($part), $normalizedSettings, false);
        update_option(self::historyOption($part), $history, false);
        update_option(self::versionOption($part), $version, false);
        return $version;
    }

    public static function version(string $part): int
    {
        $part = self::part($part);
        return max(0, (int) get_option(self::versionOption($part), 0));
    }

    /** @return array<int,array<string,mixed>> */
    public static function history(string $part): array
    {
        $part = self::part($part);
        $raw = get_option(self::historyOption($part), []);
        if (!is_array($raw)) {
            return [];
        }
        return array_values(array_filter($raw, static fn($row): bool => is_array($row) && (int) ($row['version'] ?? 0) > 0));
    }

    /** @return array{model:array<string,mixed>,settings:array<string,mixed>}|null */
    public static function historyState(string $part, int $version): ?array
    {
        $part = self::part($part);
        foreach (self::history($part) as $entry) {
            if ((int) ($entry['version'] ?? 0) !== $version || !isset($entry['model']) || !is_array($entry['model'])) {
                continue;
            }
            return [
                'model' => LayoutModel::normalize($entry['model']),
                'settings' => self::normalizeSettings($part, isset($entry['settings']) && is_array($entry['settings']) ? $entry['settings'] : []),
            ];
        }
        return null;
    }

    /** @param array<string,mixed> $model @param array<string,mixed> $settings */
    public static function digest(array $model, array $settings): string
    {
        $payload = [
            'model' => LayoutModel::normalize($model),
            'settings' => $settings,
        ];
        $json = wp_json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) {
            throw new \RuntimeException('Globalt layout kunne ikke serialiseres til digest.');
        }
        return hash('sha256', $json);
    }

    private static function part(string $part): string
    {
        $part = sanitize_key($part);
        if (!in_array($part, ['header', 'footer'], true)) {
            throw new \InvalidArgumentException('Ukendt global layoutdel.');
        }
        return $part;
    }

    private static function modelOption(string $part): string { return 'h18_clean_global_' . $part . '_layout_v1'; }
    private static function settingsOption(string $part): string { return 'h18_clean_global_' . $part . '_settings_v1'; }
    private static function historyOption(string $part): string { return 'h18_clean_global_' . $part . '_history_v1'; }
    private static function versionOption(string $part): string { return 'h18_clean_global_' . $part . '_version_v1'; }
}
