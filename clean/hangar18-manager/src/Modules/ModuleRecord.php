<?php

declare(strict_types=1);

namespace VisualDesignerManager\Modules;

final class ModuleRecord
{
    public const SCHEMA = 1;
    private const MAX_ATTRIBUTES = 100;
    private const MAX_MEDIA_ITEMS = 500;

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public static function normalize(string $module, array $raw): array
    {
        $module = ModuleRegistry::key($module);
        $definition = ModuleRegistry::definition($module);
        if ($definition === null) {
            return [];
        }

        $title = sanitize_text_field((string) ($raw['title'] ?? ''));
        $status = strtolower((string) ($raw['status'] ?? 'draft'));
        if (!in_array($status, ['draft', 'publish', 'archive'], true)) {
            $status = 'draft';
        }

        $slugSource = (string) ($raw['slug'] ?? $title);
        $slug = function_exists('sanitize_title') ? sanitize_title($slugSource) : sanitize_key($slugSource);

        $fields = [];
        $rawFields = isset($raw['fields']) && is_array($raw['fields']) ? $raw['fields'] : [];
        foreach (ModuleRegistry::fieldDefinitions($module) as $key => $field) {
            $type = (string) ($field['type'] ?? 'text');
            $fields[(string) $key] = self::fieldValue($type, $rawFields[$key] ?? self::defaultValue($type));
        }

        return [
            'schema' => self::SCHEMA,
            'module' => $module,
            'id' => self::recordId($raw['id'] ?? ''),
            'title' => $title,
            'slug' => $slug,
            'status' => $status,
            'sortOrder' => self::clampInt($raw['sortOrder'] ?? 0, -100000, 100000, 0),
            'featuredMediaId' => absint($raw['featuredMediaId'] ?? 0),
            'summary' => self::textarea($raw['summary'] ?? ''),
            'fields' => $fields,
            'attributes' => self::attributes($raw['attributes'] ?? []),
            'createdAt' => self::timestamp($raw['createdAt'] ?? ''),
            'updatedAt' => self::timestamp($raw['updatedAt'] ?? ''),
        ];
    }

    /** @param array<string,mixed> $record */
    public static function canonicalJson(array $record): string
    {
        $module = ModuleRegistry::key((string) ($record['module'] ?? ''));
        $normalized = self::normalize($module, $record);
        return (string) wp_json_encode($normalized, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }

    /** @param array<string,mixed> $record */
    public static function digest(array $record): string
    {
        return hash('sha256', self::canonicalJson($record));
    }

    private static function recordId($value): string
    {
        $id = strtolower(trim((string) $value));
        return preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $id) ? $id : '';
    }

    private static function timestamp($value): string
    {
        $value = trim((string) $value);
        return preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/', $value) ? $value : '';
    }

    private static function textarea($value): string
    {
        if (function_exists('sanitize_textarea_field')) {
            return sanitize_textarea_field((string) $value);
        }
        return sanitize_text_field((string) $value);
    }

    /** @param mixed $value @return array<int,array<string,mixed>> */
    private static function attributes($value): array
    {
        if (!is_array($value)) {
            return [];
        }
        $out = [];
        foreach ($value as $index => $raw) {
            if (count($out) >= self::MAX_ATTRIBUTES || !is_array($raw)) {
                continue;
            }
            $key = sanitize_key((string) ($raw['key'] ?? ''));
            if ($key === '') {
                $key = 'field_' . ($index + 1);
            }
            $type = strtolower((string) ($raw['type'] ?? 'text'));
            if (!in_array($type, ['text', 'textarea', 'richtext', 'number', 'integer', 'boolean', 'date', 'datetime', 'url', 'media'], true)) {
                $type = 'text';
            }
            $out[] = [
                'key' => $key,
                'label' => sanitize_text_field((string) ($raw['label'] ?? $key)),
                'type' => $type,
                'value' => self::fieldValue($type, $raw['value'] ?? self::defaultValue($type)),
                'enabled' => array_key_exists('enabled', $raw) ? (bool) $raw['enabled'] : true,
                'order' => self::clampInt($raw['order'] ?? (($index + 1) * 10), 0, 100000, ($index + 1) * 10),
            ];
        }
        usort($out, static function (array $a, array $b): int {
            $order = ((int) $a['order']) <=> ((int) $b['order']);
            return $order !== 0 ? $order : strcmp((string) $a['key'], (string) $b['key']);
        });
        return array_values($out);
    }

    /** @param mixed $value @return mixed */
    private static function fieldValue(string $type, $value)
    {
        switch ($type) {
            case 'richtext':
                return wp_kses_post((string) $value);
            case 'textarea':
                return self::textarea($value);
            case 'number':
                return is_numeric($value) ? (float) $value : 0.0;
            case 'integer':
                return (int) $value;
            case 'boolean':
                return (bool) $value;
            case 'date':
                $date = trim((string) $value);
                return preg_match('/^\d{4}-\d{2}-\d{2}$/', $date) ? $date : '';
            case 'datetime':
                $dateTime = trim((string) $value);
                return preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?$/', $dateTime) ? $dateTime : '';
            case 'url':
                return esc_url_raw((string) $value);
            case 'media':
                return absint($value);
            case 'media_list':
                if (!is_array($value)) {
                    return [];
                }
                $ids = [];
                foreach ($value as $id) {
                    $id = absint($id);
                    if ($id > 0) {
                        $ids[$id] = $id;
                    }
                    if (count($ids) >= self::MAX_MEDIA_ITEMS) {
                        break;
                    }
                }
                return array_values($ids);
            case 'text':
            default:
                return sanitize_text_field((string) $value);
        }
    }

    /** @return mixed */
    private static function defaultValue(string $type)
    {
        if ($type === 'boolean') {
            return false;
        }
        if ($type === 'number') {
            return 0.0;
        }
        if ($type === 'integer' || $type === 'media') {
            return 0;
        }
        if ($type === 'media_list') {
            return [];
        }
        return '';
    }

    private static function clampInt($value, int $min, int $max, int $default): int
    {
        if (!is_numeric($value)) {
            return $default;
        }
        return max($min, min($max, (int) $value));
    }

    private function __construct()
    {
    }
}
