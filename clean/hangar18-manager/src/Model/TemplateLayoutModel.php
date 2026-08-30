<?php

declare(strict_types=1);

namespace VisualDesignerManager\Model;

final class TemplateLayoutModel
{
    public const HEADER_META = '_h18_clean_header_template_v1';
    public const FOOTER_META = '_h18_clean_footer_template_v1';
    public const MAX_HISTORY = 50;

    private const REGISTRY_OPTION = 'h18_clean_global_template_registry_v1';
    private const DEFAULTS_OPTION = 'h18_clean_global_template_defaults_v1';
    private const MIGRATED_OPTION = 'h18_clean_global_template_migrated_v1';

    public static function ensureMigrated(): void
    {
        $registry = self::registry();
        if ($registry) {
            return;
        }

        foreach (['header', 'footer'] as $type) {
            $id = $type . '-standard-v1';
            $name = $type === 'header' ? 'Header – Standard' : 'Footer – Standard';
            $registry[$id] = self::registryRow($id, $type, $name, true);

            $model = GlobalLayoutModel::get($type);
            $settings = GlobalLayoutModel::settings($type);
            $history = GlobalLayoutModel::history($type);
            $version = GlobalLayoutModel::version($type);

            update_option(self::modelOption($id), LayoutModel::normalize($model), false);
            update_option(self::settingsOption($id), self::normalizeSettings($type, $settings), false);
            update_option(self::historyOption($id), array_slice(array_values(array_filter($history, 'is_array')), -self::MAX_HISTORY), false);
            update_option(self::versionOption($id), max(0, $version), false);
        }

        update_option(self::REGISTRY_OPTION, $registry, false);
        update_option(self::DEFAULTS_OPTION, [
            'header' => 'header-standard-v1',
            'footer' => 'footer-standard-v1',
        ], false);
        update_option(self::MIGRATED_OPTION, gmdate('c'), false);
    }

    /** @return array<int,array<string,mixed>> */
    public static function all(string $type): array
    {
        self::ensureMigrated();
        $type = self::type($type);
        $rows = array_values(array_filter(self::registry(), static fn(array $row): bool => ($row['type'] ?? '') === $type));
        usort($rows, static function (array $a, array $b): int {
            $aName = (string) ($a['name'] ?? '');
            $bName = (string) ($b['name'] ?? '');
            return strnatcasecmp($aName, $bName);
        });
        foreach ($rows as &$row) {
            $id = (string) $row['id'];
            $row['version'] = self::version($id);
            $row['isDefault'] = self::defaultId($type) === $id;
        }
        unset($row);
        return $rows;
    }

    /** @return array<string,mixed>|null */
    public static function meta(string $id): ?array
    {
        self::ensureMigrated();
        $id = self::id($id);
        $registry = self::registry();
        return isset($registry[$id]) && is_array($registry[$id]) ? $registry[$id] : null;
    }

    public static function exists(string $id, ?string $type = null): bool
    {
        $meta = self::meta($id);
        if ($meta === null) {
            return false;
        }
        return $type === null || ($meta['type'] ?? '') === self::type($type);
    }

    /** @return array<string,mixed> */
    public static function model(string $id): array
    {
        $meta = self::requireMeta($id);
        $raw = get_option(self::modelOption((string) $meta['id']), []);
        try {
            return is_array($raw) ? LayoutModel::normalize($raw) : LayoutModel::empty();
        } catch (\Throwable $error) {
            return LayoutModel::empty();
        }
    }

    /** @return array<string,mixed> */
    public static function settings(string $id): array
    {
        $meta = self::requireMeta($id);
        $raw = get_option(self::settingsOption((string) $meta['id']), []);
        return self::normalizeSettings((string) $meta['type'], is_array($raw) ? $raw : []);
    }

    /** @param array<string,mixed> $settings @return array<string,mixed> */
    public static function normalizeSettings(string $type, array $settings): array
    {
        $type = self::type($type);
        return [
            'sticky' => $type === 'header' && !empty($settings['sticky']),
            'overlay' => $type === 'header' && !empty($settings['overlay']),
            'contentWidth' => max(320, min(2400, (int) ($settings['contentWidth'] ?? 1440))),
        ];
    }

    public static function create(string $type, string $name): string
    {
        self::ensureMigrated();
        $type = self::type($type);
        $name = self::name($name, $type === 'header' ? 'Ny Header' : 'Ny Footer');
        $id = self::newId($type);
        $registry = self::registry();
        $registry[$id] = self::registryRow($id, $type, $name, true);
        update_option(self::REGISTRY_OPTION, $registry, false);
        update_option(self::modelOption($id), LayoutModel::empty(), false);
        update_option(self::settingsOption($id), self::normalizeSettings($type, []), false);
        update_option(self::historyOption($id), [], false);
        update_option(self::versionOption($id), 0, false);
        return $id;
    }

    public static function duplicate(string $sourceId, string $name = ''): string
    {
        $source = self::requireMeta($sourceId);
        $newId = self::create((string) $source['type'], $name !== '' ? $name : ((string) $source['name'] . ' – kopi'));
        update_option(self::modelOption($newId), self::model($sourceId), false);
        update_option(self::settingsOption($newId), self::settings($sourceId), false);
        return $newId;
    }

    public static function rename(string $id, string $name): void
    {
        $meta = self::requireMeta($id);
        $registry = self::registry();
        $registry[$id]['name'] = self::name($name, (string) $meta['name']);
        $registry[$id]['updatedUtc'] = gmdate('c');
        update_option(self::REGISTRY_OPTION, $registry, false);
    }

    public static function setActive(string $id, bool $active): void
    {
        self::requireMeta($id);
        $registry = self::registry();
        $registry[$id]['active'] = $active;
        $registry[$id]['updatedUtc'] = gmdate('c');
        update_option(self::REGISTRY_OPTION, $registry, false);
    }

    public static function defaultId(string $type): string
    {
        self::ensureMigrated();
        $type = self::type($type);
        $raw = get_option(self::DEFAULTS_OPTION, []);
        $id = is_array($raw) ? self::id($raw[$type] ?? '') : '';
        if ($id !== '' && self::exists($id, $type)) {
            $meta = self::meta($id);
            if ($meta && !empty($meta['active'])) {
                return $id;
            }
        }
        foreach (self::allWithoutDefaultRecursion($type) as $row) {
            if (!empty($row['active'])) {
                return (string) $row['id'];
            }
        }
        return '';
    }

    public static function setDefault(string $type, string $id): void
    {
        $type = self::type($type);
        $meta = self::requireMeta($id);
        if (($meta['type'] ?? '') !== $type) {
            throw new \InvalidArgumentException('Template-typen matcher ikke standardvalget.');
        }
        self::setActive($id, true);
        $raw = get_option(self::DEFAULTS_OPTION, []);
        $raw = is_array($raw) ? $raw : [];
        $raw[$type] = $id;
        update_option(self::DEFAULTS_OPTION, $raw, false);
    }

    /** @param array<string,mixed> $model @param array<string,mixed> $settings */
    public static function saveVersion(string $id, array $model, array $settings, int $userId, string $note): int
    {
        $meta = self::requireMeta($id);
        $normalized = LayoutModel::normalize($model);
        $normalizedSettings = self::normalizeSettings((string) $meta['type'], $settings);
        $version = self::version($id) + 1;
        $history = self::history($id);
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
        update_option(self::modelOption($id), $normalized, false);
        update_option(self::settingsOption($id), $normalizedSettings, false);
        update_option(self::historyOption($id), $history, false);
        update_option(self::versionOption($id), $version, false);

        $registry = self::registry();
        $registry[$id]['updatedUtc'] = gmdate('c');
        update_option(self::REGISTRY_OPTION, $registry, false);
        return $version;
    }

    public static function version(string $id): int
    {
        self::requireMeta($id);
        return max(0, (int) get_option(self::versionOption($id), 0));
    }

    /** @return array<int,array<string,mixed>> */
    public static function history(string $id): array
    {
        self::requireMeta($id);
        $raw = get_option(self::historyOption($id), []);
        if (!is_array($raw)) {
            return [];
        }
        return array_values(array_filter($raw, static fn($row): bool => is_array($row) && (int) ($row['version'] ?? 0) > 0));
    }

    /** @return array{model:array<string,mixed>,settings:array<string,mixed>}|null */
    public static function historyState(string $id, int $version): ?array
    {
        $meta = self::requireMeta($id);
        foreach (self::history($id) as $entry) {
            if ((int) ($entry['version'] ?? 0) !== $version || !isset($entry['model']) || !is_array($entry['model'])) {
                continue;
            }
            return [
                'model' => LayoutModel::normalize($entry['model']),
                'settings' => self::normalizeSettings((string) $meta['type'], isset($entry['settings']) && is_array($entry['settings']) ? $entry['settings'] : []),
            ];
        }
        return null;
    }

    public static function pageChoice(int $postId, string $type): string
    {
        $type = self::type($type);
        $metaKey = $type === 'header' ? self::HEADER_META : self::FOOTER_META;
        $value = sanitize_key((string) get_post_meta($postId, $metaKey, true));
        if ($value === '' || $value === 'auto') {
            return 'auto';
        }
        if ($value === 'none') {
            return 'none';
        }
        return self::exists($value, $type) ? $value : 'auto';
    }

    public static function setPageChoice(int $postId, string $type, string $choice): void
    {
        $type = self::type($type);
        $choice = sanitize_key($choice);
        if (!in_array($choice, ['auto', 'none'], true) && !self::exists($choice, $type)) {
            $choice = 'auto';
        }
        $metaKey = $type === 'header' ? self::HEADER_META : self::FOOTER_META;
        update_post_meta($postId, $metaKey, $choice);
    }

    public static function resolveChoiceId(string $type, string $choice): string
    {
        $type = self::type($type);
        $choice = sanitize_key($choice);
        if ($choice === 'none') {
            return '';
        }
        if ($choice !== '' && $choice !== 'auto') {
            $meta = self::meta($choice);
            if ($meta && ($meta['type'] ?? '') === $type && !empty($meta['active'])) {
                return $choice;
            }
        }
        $default = self::defaultId($type);
        $meta = $default !== '' ? self::meta($default) : null;
        return $meta && !empty($meta['active']) ? $default : '';
    }

    public static function resolveId(int $postId, string $type): string
    {
        $type = self::type($type);
        return self::resolveChoiceId($type, self::pageChoice($postId, $type));
    }

    /** @param array<string,mixed> $model @param array<string,mixed> $settings */
    public static function digest(array $model, array $settings): string
    {
        $json = wp_json_encode([
            'model' => LayoutModel::normalize($model),
            'settings' => $settings,
        ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) {
            throw new \RuntimeException('Template-layout kunne ikke serialiseres til digest.');
        }
        return hash('sha256', $json);
    }

    /** @return array<string,array<string,mixed>> */
    private static function registry(): array
    {
        $raw = get_option(self::REGISTRY_OPTION, []);
        if (!is_array($raw)) {
            return [];
        }
        $result = [];
        foreach ($raw as $id => $row) {
            if (!is_array($row)) {
                continue;
            }
            $cleanId = self::id($row['id'] ?? $id);
            $type = sanitize_key((string) ($row['type'] ?? ''));
            if ($cleanId === '' || !in_array($type, ['header', 'footer'], true)) {
                continue;
            }
            $result[$cleanId] = self::registryRow(
                $cleanId,
                $type,
                self::name((string) ($row['name'] ?? ''), $type === 'header' ? 'Header' : 'Footer'),
                !array_key_exists('active', $row) || !empty($row['active']),
                (string) ($row['createdUtc'] ?? ''),
                (string) ($row['updatedUtc'] ?? '')
            );
        }
        return $result;
    }

    /** @return array<int,array<string,mixed>> */
    private static function allWithoutDefaultRecursion(string $type): array
    {
        $type = self::type($type);
        return array_values(array_filter(self::registry(), static fn(array $row): bool => ($row['type'] ?? '') === $type));
    }

    /** @return array<string,mixed> */
    private static function registryRow(string $id, string $type, string $name, bool $active, string $created = '', string $updated = ''): array
    {
        $now = gmdate('c');
        return [
            'id' => $id,
            'type' => $type,
            'name' => $name,
            'active' => $active,
            'createdUtc' => $created !== '' ? $created : $now,
            'updatedUtc' => $updated !== '' ? $updated : $now,
        ];
    }

    /** @return array<string,mixed> */
    private static function requireMeta(string $id): array
    {
        $meta = self::meta($id);
        if ($meta === null) {
            throw new \InvalidArgumentException('Ukendt Header/Footer-template.');
        }
        return $meta;
    }

    private static function newId(string $type): string
    {
        $type = self::type($type);
        do {
            $id = $type . '-' . substr(str_replace('-', '', wp_generate_uuid4()), 0, 16);
        } while (isset(self::registry()[$id]));
        return $id;
    }

    private static function id($value): string
    {
        $id = sanitize_key((string) $value);
        return substr($id, 0, 100);
    }

    private static function type(string $type): string
    {
        $type = sanitize_key($type);
        if (!in_array($type, ['header', 'footer'], true)) {
            throw new \InvalidArgumentException('Ukendt template-type.');
        }
        return $type;
    }

    private static function name(string $name, string $fallback): string
    {
        $name = trim(sanitize_text_field($name));
        return $name !== '' ? (function_exists('mb_substr') ? mb_substr($name, 0, 120) : substr($name, 0, 120)) : $fallback;
    }

    private static function modelOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_model_v1'; }
    private static function settingsOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_settings_v1'; }
    private static function historyOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_history_v1'; }
    private static function versionOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_version_v1'; }
}
