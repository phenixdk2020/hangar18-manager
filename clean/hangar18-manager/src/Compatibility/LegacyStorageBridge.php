<?php

declare(strict_types=1);

namespace VisualDesignerManager\Compatibility;

use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

/**
 * Compatibility bridge for persisted identifiers written by pre-VDM naming.
 *
 * New runtime code must use canonical VDM concepts and call this bridge only
 * when it has to read/write historical WordPress storage during migration.
 */
final class LegacyStorageBridge
{
    private const TEMPLATE_REGISTRY_OPTION = 'h18_clean_global_template_registry_v1';
    private const TEMPLATE_DEFAULTS_OPTION = 'h18_clean_global_template_defaults_v1';

    /** @param array<string,mixed> $snapshot */
    public static function importTemplateSnapshot(array $snapshot): string
    {
        TemplateLayoutModel::ensureMigrated();
        $type = sanitize_key((string) ($snapshot['type'] ?? ''));
        if (!in_array($type, ['header', 'footer'], true)) {
            throw new \InvalidArgumentException('Ugyldig template-type i importpakken.');
        }

        $sourceId = self::templateId((string) ($snapshot['sourceId'] ?? ''));
        if ($sourceId === '') {
            throw new \InvalidArgumentException('Template-ID mangler i importpakken.');
        }
        $name = trim(sanitize_text_field((string) ($snapshot['name'] ?? '')));
        if ($name === '') {
            $name = $type === 'header' ? 'Header' : 'Footer';
        }

        $registry = self::registry();
        $targetId = $sourceId;
        if (isset($registry[$targetId]) && is_array($registry[$targetId])) {
            $existingType = sanitize_key((string) ($registry[$targetId]['type'] ?? ''));
            $existingName = trim((string) ($registry[$targetId]['name'] ?? ''));
            $standardId = $type . '-standard-v1';
            if ($existingType !== $type || ($targetId !== $standardId && $existingName !== '' && $existingName !== $name)) {
                $targetId = self::newTemplateId($type, $registry);
            }
        }

        $created = sanitize_text_field((string) ($snapshot['createdUtc'] ?? ''));
        $updated = sanitize_text_field((string) ($snapshot['updatedUtc'] ?? ''));
        $now = gmdate('c');
        $registry[$targetId] = [
            'id' => $targetId,
            'type' => $type,
            'name' => function_exists('mb_substr') ? mb_substr($name, 0, 120) : substr($name, 0, 120),
            'active' => !array_key_exists('active', $snapshot) || !empty($snapshot['active']),
            'createdUtc' => $created !== '' ? $created : $now,
            'updatedUtc' => $updated !== '' ? $updated : $now,
        ];
        update_option(self::TEMPLATE_REGISTRY_OPTION, $registry, false);

        $model = LayoutModel::normalize(isset($snapshot['model']) && is_array($snapshot['model']) ? $snapshot['model'] : LayoutModel::empty());
        $settings = TemplateLayoutModel::normalizeSettings($type, isset($snapshot['settings']) && is_array($snapshot['settings']) ? $snapshot['settings'] : []);
        $history = [];
        $highestVersion = 0;
        foreach ((array) ($snapshot['history'] ?? []) as $entry) {
            if (!is_array($entry) || !isset($entry['model']) || !is_array($entry['model'])) {
                continue;
            }
            $version = max(1, (int) ($entry['version'] ?? 0));
            $entryModel = LayoutModel::normalize($entry['model']);
            $entrySettings = TemplateLayoutModel::normalizeSettings($type, isset($entry['settings']) && is_array($entry['settings']) ? $entry['settings'] : []);
            $history[] = [
                'version' => $version,
                'savedUtc' => sanitize_text_field((string) ($entry['savedUtc'] ?? '')),
                'userId' => max(0, (int) ($entry['userId'] ?? 0)),
                'note' => sanitize_text_field((string) ($entry['note'] ?? '')),
                'digest' => TemplateLayoutModel::digest($entryModel, $entrySettings),
                'model' => $entryModel,
                'settings' => $entrySettings,
            ];
            $highestVersion = max($highestVersion, $version);
        }
        if (count($history) > TemplateLayoutModel::MAX_HISTORY) {
            $history = array_slice($history, -TemplateLayoutModel::MAX_HISTORY);
        }
        $version = max($highestVersion, max(0, (int) ($snapshot['version'] ?? 0)));

        update_option(self::templateOption($targetId, 'model'), $model, false);
        update_option(self::templateOption($targetId, 'settings'), $settings, false);
        update_option(self::templateOption($targetId, 'history'), $history, false);
        update_option(self::templateOption($targetId, 'version'), $version, false);
        return $targetId;
    }

    /** @param array<string,mixed> $defaults @param array<string,string> $idMap */
    public static function importTemplateDefaults(array $defaults, array $idMap): void
    {
        TemplateLayoutModel::ensureMigrated();
        $target = get_option(self::TEMPLATE_DEFAULTS_OPTION, []);
        $target = is_array($target) ? $target : [];
        foreach (['header', 'footer'] as $type) {
            $sourceId = self::templateId((string) ($defaults[$type] ?? ''));
            $mapped = $sourceId !== '' ? self::templateId((string) ($idMap[$sourceId] ?? $sourceId)) : '';
            if ($mapped !== '' && TemplateLayoutModel::exists($mapped, $type)) {
                $target[$type] = $mapped;
            }
        }
        update_option(self::TEMPLATE_DEFAULTS_OPTION, $target, false);
    }

    /** @return array<string,array<string,mixed>> */
    private static function registry(): array
    {
        $raw = get_option(self::TEMPLATE_REGISTRY_OPTION, []);
        if (!is_array($raw)) {
            return [];
        }
        $out = [];
        foreach ($raw as $id => $row) {
            if (!is_array($row)) {
                continue;
            }
            $clean = self::templateId((string) ($row['id'] ?? $id));
            if ($clean !== '') {
                $out[$clean] = $row;
            }
        }
        return $out;
    }

    /** @param array<string,array<string,mixed>> $registry */
    private static function newTemplateId(string $type, array $registry): string
    {
        do {
            $id = $type . '-' . substr(str_replace('-', '', wp_generate_uuid4()), 0, 16);
        } while (isset($registry[$id]));
        return $id;
    }

    private static function templateId(string $value): string
    {
        return substr(sanitize_key($value), 0, 100);
    }

    private static function templateOption(string $id, string $kind): string
    {
        $suffix = [
            'model' => '_model_v1',
            'settings' => '_settings_v1',
            'history' => '_history_v1',
            'version' => '_version_v1',
        ][$kind] ?? '';
        if ($suffix === '') {
            throw new \InvalidArgumentException('Ukendt legacy template storage-type.');
        }
        return 'h18_clean_tpl_' . self::templateId($id) . $suffix;
    }

    private function __construct()
    {
    }
}
