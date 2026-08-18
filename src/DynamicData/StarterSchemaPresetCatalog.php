<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\DynamicData;

use InvalidArgumentException;

/**
 * UD-060 starter schemas for the generic Dynamic CMS motor.
 *
 * These are passive preset definitions only. They do not install schemas,
 * migrate legacy pages or switch Vehicle/Event/Gallery away from v0.5.30.
 *
 * The schema payload deliberately matches the existing UD-051 generic data
 * shape (SchemaVersion 2). Extra preset/compatibility metadata is kept outside
 * the installable Schema member.
 */
final class StarterSchemaPresetCatalog
{
    public const PRESET_VERSION = '1.0.0';
    public const GENERIC_SCHEMA_VERSION = 2;

    /** @var list<string> */
    public const PRESET_KEYS = ['vehicle', 'event', 'gallery'];

    /** @return array<string,array<string,mixed>> */
    public static function all(): array
    {
        return [
            'vehicle' => self::vehicle(),
            'event' => self::event(),
            'gallery' => self::gallery(),
        ];
    }

    /** @return array<string,mixed> */
    public static function get(string $key): array
    {
        $key = strtolower(trim($key));
        $all = self::all();
        if (!isset($all[$key])) {
            throw new InvalidArgumentException("Unknown starter schema preset '{$key}'.");
        }
        return $all[$key];
    }

    /** @return array<string,mixed> */
    public static function installableSchema(string $key): array
    {
        return self::get($key)['Schema'];
    }

    /** @return array<string,mixed> */
    private static function vehicle(): array
    {
        return [
            'PresetVersion' => self::PRESET_VERSION,
            'Domain' => 'vehicle',
            'EntryTitle' => ['Required' => true, 'LegacySource' => 'Name'],
            'Schema' => [
                'Key' => 'vehicle',
                'SingularLabel' => 'Køretøj',
                'PluralLabel' => 'Køretøjer',
                'SchemaVersion' => self::GENERIC_SCHEMA_VERSION,
                'Fields' => [
                    self::field('description', 'Beskrivelse', 'text'),
                    self::field('image', 'Billede', 'media'),
                    self::field('type', 'Type', 'text'),
                    self::field('manufacturer', 'Producent', 'text'),
                    self::field('model', 'Model', 'text'),
                    self::field('year', 'Produktionsår', 'number'),
                    self::field('engine', 'Motor', 'text'),
                    self::field('weight', 'Vægt', 'number'),
                    self::field('color', 'Farve', 'text'),
                    self::field('crew', 'Besætning', 'text'),
                    self::field('service_period', 'Tjenesteperiode', 'text'),
                    self::field('restoration_status', 'Restaureringsstatus', 'text'),
                    self::field('history', 'Historik', 'text'),
                    self::field('aalborg_service', 'Tjeneste ved Aalborg Kaserner', 'text'),
                    self::field('restoration_text', 'Restaurering og status', 'text'),
                    self::field('technical_source_url', 'Teknisk kilde-URL', 'text'),
                    self::field('active', 'Aktiv', 'bool'),
                ],
            ],
            'LegacyCompatibility' => [
                'ParentSlug' => 'koeretoejer-og-materiel',
                'Marker' => 'HANGAR18-VEHICLE-DATA',
                'FieldSources' => [
                    'description' => ['ShortDescription'],
                    'image' => ['MainMediaId'],
                    'type' => ['CustomFields.type', 'Type'],
                    'manufacturer' => ['CustomFields.manufacturer', 'Manufacturer'],
                    'model' => [],
                    'year' => ['CustomFields.production_year', 'ProductionYear'],
                    'engine' => ['CustomFields.engine', 'Engine'],
                    'weight' => ['CustomFields.weight', 'Weight'],
                    'color' => ['CustomFields.color', 'Color'],
                    'crew' => ['CustomFields.crew', 'Crew'],
                    'service_period' => ['CustomFields.service_period', 'ServicePeriod'],
                    'restoration_status' => ['CustomFields.restoration_status', 'RestorationStatus'],
                    'history' => ['History'],
                    'aalborg_service' => ['AalborgService'],
                    'restoration_text' => ['RestorationText'],
                    'technical_source_url' => ['TechnicalSourceUrl'],
                    'active' => [],
                ],
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function event(): array
    {
        return [
            'PresetVersion' => self::PRESET_VERSION,
            'Domain' => 'event',
            'EntryTitle' => ['Required' => true, 'LegacySource' => 'EventName'],
            'Schema' => [
                'Key' => 'event',
                'SingularLabel' => 'Event',
                'PluralLabel' => 'Events',
                'SchemaVersion' => self::GENERIC_SCHEMA_VERSION,
                'Fields' => [
                    self::field('short_description', 'Kort beskrivelse', 'text'),
                    self::field('event_date', 'Dato', 'date', true),
                    self::field('start_time', 'Starttid', 'text'),
                    self::field('end_time', 'Sluttid', 'text'),
                    self::field('venue', 'Sted', 'text'),
                    self::field('address', 'Adresse', 'text'),
                    self::field('contact', 'Kontakt', 'text'),
                    self::field('description', 'Beskrivelse', 'text'),
                    self::field('program', 'Program', 'text'),
                    self::field('practical', 'Praktisk information', 'text'),
                    self::field('image', 'Billede', 'media'),
                    self::relationField('gallery_album', 'Billedalbum', 'gallery'),
                    self::field('active', 'Aktiv', 'bool'),
                ],
            ],
            'LegacyCompatibility' => [
                'ParentSlug' => 'events',
                'Marker' => 'HANGAR18-EVENT-DATA',
                'FieldSources' => [
                    'short_description' => ['ShortDescription'],
                    'event_date' => ['EventDate'],
                    'start_time' => ['StartTime'],
                    'end_time' => ['EndTime'],
                    'venue' => ['Venue'],
                    'address' => ['Address'],
                    'contact' => ['Contact'],
                    'description' => ['Description'],
                    'program' => ['Program'],
                    'practical' => ['Practical'],
                    'image' => ['MainMediaId'],
                    'gallery_album' => ['GalleryAlbumPageId'],
                    'active' => [],
                ],
                'RelationRemapRequired' => ['gallery_album'],
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function gallery(): array
    {
        return [
            'PresetVersion' => self::PRESET_VERSION,
            'Domain' => 'gallery',
            'EntryTitle' => ['Required' => true, 'LegacySource' => 'AlbumName'],
            'Schema' => [
                'Key' => 'gallery',
                'SingularLabel' => 'Billedalbum',
                'PluralLabel' => 'Billedalbummer',
                'SchemaVersion' => self::GENERIC_SCHEMA_VERSION,
                'Fields' => [
                    self::field('album_type', 'Albumtype', 'text'),
                    self::field('description', 'Beskrivelse', 'text'),
                    self::field('cover_image', 'Forsidebillede', 'media'),
                    self::repeaterField('items', 'Billeder', [
                        self::nestedField('image', 'Billede', 'media', true),
                        self::nestedField('title', 'Titel', 'text'),
                        self::nestedField('description', 'Beskrivelse', 'text'),
                    ], 20),
                    self::field('active', 'Aktiv', 'bool'),
                ],
            ],
            'LegacyCompatibility' => [
                'ParentSlug' => 'billedgalleri',
                'Marker' => 'HANGAR18-GALLERY-ALBUM-DATA',
                'FieldSources' => [
                    'album_type' => ['AlbumType'],
                    'description' => ['Description'],
                    'cover_image' => ['FeaturedImageId', 'Items.0.MediaId'],
                    'items' => ['Items'],
                    'active' => [],
                ],
                'ItemTransform' => [
                    'image' => 'MediaId',
                    'title' => 'Title',
                    'description' => 'Description',
                ],
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function field(string $key, string $label, string $type, bool $required = false): array
    {
        return [
            'Key' => $key,
            'Label' => $label,
            'Type' => $type,
            'Required' => $required,
            'RelationTargetType' => '',
            'NestedFields' => [],
            'RepeaterMaxItems' => 0,
        ];
    }

    /** @return array<string,mixed> */
    private static function relationField(string $key, string $label, string $targetType, bool $required = false): array
    {
        $field = self::field($key, $label, 'relation', $required);
        $field['RelationTargetType'] = $targetType;
        return $field;
    }

    /** @param list<array<string,mixed>> $nestedFields @return array<string,mixed> */
    private static function repeaterField(string $key, string $label, array $nestedFields, int $maxItems): array
    {
        $field = self::field($key, $label, 'repeater');
        $field['NestedFields'] = $nestedFields;
        $field['RepeaterMaxItems'] = $maxItems;
        return $field;
    }

    /** @return array<string,mixed> */
    private static function nestedField(string $key, string $label, string $type, bool $required = false): array
    {
        return [
            'Key' => $key,
            'Label' => $label,
            'Type' => $type,
            'Required' => $required,
        ];
    }

    private function __construct()
    {
    }
}
