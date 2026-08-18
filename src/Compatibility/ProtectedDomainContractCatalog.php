<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Compatibility;

use InvalidArgumentException;

final class ProtectedDomainContractCatalog
{
    private const CONTRACTS = [
        'vehicle' => [
            'slug' => 'koeretoejer-og-materiel',
            'marker' => 'HANGAR18-VEHICLE-DATA',
            'admin_actions' => ['h18_save_vehicle', 'h18_save_vehicle_register_settings', 'h18_save_vehicle_fields', 'h18_rebuild_vehicle_register'],
            'markup_hooks' => ['h18-vehicle-register', 'h18-vehicle-card', 'h18-vehicle-hero', 'h18-vehicle-main-layout'],
        ],
        'event' => [
            'slug' => 'events',
            'marker' => 'HANGAR18-EVENT-DATA',
            'admin_actions' => ['h18_save_event', 'h18_save_event_layout', 'h18_rebuild_event_register'],
            'markup_hooks' => ['h18-event-register', 'h18-event-card', 'h18-event-hero', 'h18-event-image'],
        ],
        'gallery' => [
            'slug' => 'billedgalleri',
            'marker' => 'HANGAR18-GALLERY-ALBUM-DATA',
            'admin_actions' => ['h18_save_gallery_album', 'h18_save_gallery_layout', 'h18_rebuild_gallery_index'],
            'markup_hooks' => ['h18-gallery-grid', 'h18-gallery-hero', 'h18-gallery-item'],
        ],
    ];

    public static function domains(): array
    {
        return array_keys(self::CONTRACTS);
    }

    public static function contract(string $domain): array
    {
        $key = strtolower(trim($domain));
        if (!isset(self::CONTRACTS[$key])) {
            throw new InvalidArgumentException("Unknown protected domain '{$domain}'.");
        }
        return self::CONTRACTS[$key];
    }

    public static function markupHooks(string $domain): array
    {
        return array_values(self::contract($domain)['markup_hooks']);
    }

    public static function adminActions(string $domain): array
    {
        return array_values(self::contract($domain)['admin_actions']);
    }

    public static function marker(string $domain): string
    {
        return (string) self::contract($domain)['marker'];
    }

    public static function slug(string $domain): string
    {
        return (string) self::contract($domain)['slug'];
    }

    private function __construct()
    {
    }
}
