<?php

declare(strict_types=1);

namespace VisualDesignerManager\Modules;

final class ModuleRegistry
{
    public const SCHEMA = 1;

    /** @return array<string,array<string,mixed>> */
    public static function all(): array
    {
        return [
            'vehicles' => [
                'key' => 'vehicles',
                'label' => 'Køretøjer',
                'singular' => 'Køretøj',
                'schemaVersion' => 1,
                'iconSet' => 'core',
                'icon' => 'gear',
                'fields' => [
                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],
                    'category' => ['label' => 'Kategori', 'type' => 'text', 'required' => false],
                    'imageIds' => ['label' => 'Galleri', 'type' => 'media_list', 'required' => false],
                ],
            ],
            'events' => [
                'key' => 'events',
                'label' => 'Events',
                'singular' => 'Event',
                'schemaVersion' => 1,
                'iconSet' => 'core',
                'icon' => 'calendar',
                'fields' => [
                    'start' => ['label' => 'Start', 'type' => 'datetime', 'required' => false],
                    'end' => ['label' => 'Slut', 'type' => 'datetime', 'required' => false],
                    'location' => ['label' => 'Sted', 'type' => 'text', 'required' => false],
                    'address' => ['label' => 'Adresse', 'type' => 'text', 'required' => false],
                    'contact' => ['label' => 'Kontakt', 'type' => 'text', 'required' => false],
                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],
                    'galleryRecordId' => ['label' => 'Tilknyttet album', 'type' => 'text', 'required' => false],
                ],
            ],
            'galleries' => [
                'key' => 'galleries',
                'label' => 'Billedgalleri',
                'singular' => 'Album',
                'schemaVersion' => 1,
                'iconSet' => 'core',
                'icon' => 'camera',
                'fields' => [
                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],
                    'imageIds' => ['label' => 'Billeder', 'type' => 'media_list', 'required' => false],
                ],
            ],
        ];
    }

    public static function key($value): string
    {
        $key = sanitize_key((string) $value);
        $aliases = [
            'vehicle' => 'vehicles',
            'event' => 'events',
            'gallery' => 'galleries',
            'album' => 'galleries',
        ];
        return $aliases[$key] ?? $key;
    }

    public static function supports($value): bool
    {
        return self::definition($value) !== null;
    }

    /** @return array<string,mixed>|null */
    public static function definition($value): ?array
    {
        $key = self::key($value);
        $all = self::all();
        return isset($all[$key]) ? $all[$key] : null;
    }

    /** @return array<string,array<string,mixed>> */
    public static function fieldDefinitions($value): array
    {
        $definition = self::definition($value);
        if ($definition === null || !isset($definition['fields']) || !is_array($definition['fields'])) {
            return [];
        }
        return $definition['fields'];
    }

    /** @return array{schema:int,modules:array<int,array<string,mixed>>} */
    public static function editorCatalog(): array
    {
        $modules = [];
        foreach (self::all() as $definition) {
            $fields = [];
            foreach ((array) ($definition['fields'] ?? []) as $key => $field) {
                $fields[] = [
                    'key' => (string) $key,
                    'label' => (string) ($field['label'] ?? $key),
                    'type' => (string) ($field['type'] ?? 'text'),
                    'required' => !empty($field['required']),
                ];
            }
            $modules[] = [
                'key' => (string) ($definition['key'] ?? ''),
                'label' => (string) ($definition['label'] ?? ''),
                'singular' => (string) ($definition['singular'] ?? ''),
                'schemaVersion' => (int) ($definition['schemaVersion'] ?? 1),
                'iconSet' => (string) ($definition['iconSet'] ?? 'core'),
                'icon' => (string) ($definition['icon'] ?? 'info'),
                'fields' => $fields,
            ];
        }
        return ['schema' => self::SCHEMA, 'modules' => $modules];
    }

    private function __construct()
    {
    }
}
