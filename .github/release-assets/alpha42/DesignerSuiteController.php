<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Model\LayoutModel;

final class DesignerSuiteController
{
    private const COMPONENTS_OPTION = 'vdm_designer_suite_components_v1';
    private const TOKENS_OPTION = 'vdm_designer_suite_tokens_v1';

    public static function register(): void
    {
        add_action('wp_ajax_vdm_designer_suite', [self::class, 'ajax']);
    }

    public static function nonce(): string
    {
        return wp_create_nonce('vdm_designer_suite');
    }

    /** @return array<string,mixed> */
    public static function tokens(): array
    {
        $defaults = [
            'colors' => [
                'olive' => ['label' => 'Mørkegrøn', 'value' => '#30382a'],
                'sand' => ['label' => 'Sand', 'value' => '#c3ae83'],
                'offwhite' => ['label' => 'Offwhite', 'value' => '#f4f1e8'],
                'rust' => ['label' => 'Rust', 'value' => '#9a4d2d'],
                'steel' => ['label' => 'Steel', 'value' => '#525a5f'],
                'text' => ['label' => 'Primær tekst', 'value' => '#30382a'],
            ],
            'radius' => [
                'square' => ['label' => 'Firkantet', 'value' => 0],
                'small' => ['label' => 'Lille', 'value' => 6],
                'medium' => ['label' => 'Medium', 'value' => 10],
                'pill' => ['label' => 'Pille', 'value' => 28],
            ],
            'spacing' => [
                'xs' => ['label' => 'XS', 'value' => 6],
                's' => ['label' => 'S', 'value' => 12],
                'm' => ['label' => 'M', 'value' => 20],
                'l' => ['label' => 'L', 'value' => 32],
                'xl' => ['label' => 'XL', 'value' => 48],
            ],
            'fonts' => [
                'body' => ['label' => 'Brødtekst', 'value' => 'system'],
                'heading' => ['label' => 'Overskrift', 'value' => 'system'],
            ],
        ];
        $saved = get_option(self::TOKENS_OPTION, []);
        if (!is_array($saved)) {
            return $defaults;
        }
        foreach ($defaults as $group => $rows) {
            if (!isset($saved[$group]) || !is_array($saved[$group])) {
                $saved[$group] = $rows;
            }
        }
        return $saved;
    }

    public static function ajax(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettighed til Designer-værktøjerne.'], 403);
        }
        check_ajax_referer('vdm_designer_suite', 'nonce');

        $op = sanitize_key((string) ($_POST['op'] ?? 'bootstrap'));
        try {
            if ($op === 'bootstrap') {
                wp_send_json_success([
                    'components' => array_values(self::components()),
                    'tokens' => self::tokens(),
                ]);
            }
            if ($op === 'versions') {
                self::versions();
            }
            if ($op === 'save_component') {
                self::saveComponent();
            }
            if ($op === 'delete_component') {
                self::deleteComponent();
            }
            if ($op === 'save_tokens') {
                self::saveTokens();
            }
            wp_send_json_error(['message' => 'Ukendt Designer Suite-handling.'], 400);
        } catch (\Throwable $error) {
            wp_send_json_error(['message' => $error->getMessage()], 500);
        }
    }

    /** @return array<string,array<string,mixed>> */
    private static function components(): array
    {
        $raw = get_option(self::COMPONENTS_OPTION, []);
        if (!is_array($raw)) {
            return [];
        }
        $out = [];
        foreach ($raw as $id => $row) {
            if (!is_array($row)) {
                continue;
            }
            $clean = sanitize_key((string) $id);
            if ($clean === '') {
                continue;
            }
            $out[$clean] = $row;
        }
        return $out;
    }

    private static function versions(): void
    {
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page') {
            wp_send_json_error(['message' => 'Ugyldig side.'], 400);
        }
        $rows = [];
        foreach (array_reverse(LayoutModel::history($postId)) as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $rows[] = [
                'version' => (int) ($entry['version'] ?? 0),
                'savedUtc' => (string) ($entry['savedUtc'] ?? ''),
                'userId' => (int) ($entry['userId'] ?? 0),
                'note' => (string) ($entry['note'] ?? ''),
                'digest' => (string) ($entry['digest'] ?? ''),
                'model' => isset($entry['model']) && is_array($entry['model']) ? $entry['model'] : null,
            ];
        }
        wp_send_json_success(['versions' => $rows]);
    }

    private static function saveComponent(): void
    {
        $name = sanitize_text_field((string) wp_unslash($_POST['name'] ?? 'Komponent'));
        if ($name === '') {
            $name = 'Komponent';
        }
        $id = sanitize_key((string) wp_unslash($_POST['component_id'] ?? ''));
        if ($id === '') {
            $id = 'component-' . strtolower(wp_generate_password(10, false, false));
        }
        $decoded = json_decode((string) wp_unslash($_POST['model_json'] ?? ''), true);
        if (!is_array($decoded)) {
            wp_send_json_error(['message' => 'Komponenten indeholder ikke gyldig layoutdata.'], 400);
        }
        $model = LayoutModel::normalize($decoded);
        $roots = array_values(array_filter($model['nodes'] ?? [], static fn($node): bool => is_array($node) && (string) ($node['parentId'] ?? '') === ''));
        if (count($roots) !== 1 || (string) ($roots[0]['type'] ?? '') !== 'section') {
            wp_send_json_error(['message' => 'Globale komponenter skal gemmes som én Sektion.'], 400);
        }

        $all = self::components();
        $previous = isset($all[$id]) && is_array($all[$id]) ? $all[$id] : [];
        $version = max(0, (int) ($previous['version'] ?? 0)) + 1;
        $row = [
            'id' => $id,
            'name' => $name,
            'version' => $version,
            'updatedUtc' => gmdate('c'),
            'userId' => get_current_user_id(),
            'model' => $model,
        ];
        $all[$id] = $row;
        if (count($all) > 50) {
            uasort($all, static fn(array $a, array $b): int => strcmp((string) ($a['updatedUtc'] ?? ''), (string) ($b['updatedUtc'] ?? '')));
            while (count($all) > 50) {
                array_shift($all);
            }
        }
        update_option(self::COMPONENTS_OPTION, $all, false);

        $synced = 0;
        if (!empty($_POST['sync'])) {
            $synced = self::syncComponentAcrossPages($row);
        }
        wp_send_json_success(['component' => $row, 'syncedPages' => $synced, 'components' => array_values(self::components())]);
    }

    private static function deleteComponent(): void
    {
        $id = sanitize_key((string) wp_unslash($_POST['component_id'] ?? ''));
        $all = self::components();
        unset($all[$id]);
        update_option(self::COMPONENTS_OPTION, $all, false);
        wp_send_json_success(['components' => array_values($all)]);
    }

    private static function saveTokens(): void
    {
        $decoded = json_decode((string) wp_unslash($_POST['tokens_json'] ?? ''), true);
        if (!is_array($decoded)) {
            wp_send_json_error(['message' => 'Ugyldige design tokens.'], 400);
        }
        $clean = self::sanitizeTokens($decoded);
        update_option(self::TOKENS_OPTION, $clean, false);
        $synced = 0;
        if (!empty($_POST['sync'])) {
            $synced = self::syncTokensAcrossPages($clean);
        }
        wp_send_json_success(['tokens' => $clean, 'syncedPages' => $synced]);
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function sanitizeTokens(array $raw): array
    {
        $out = ['colors' => [], 'radius' => [], 'spacing' => [], 'fonts' => []];
        foreach (['colors', 'radius', 'spacing', 'fonts'] as $group) {
            $rows = isset($raw[$group]) && is_array($raw[$group]) ? $raw[$group] : [];
            foreach (array_slice($rows, 0, 50, true) as $key => $row) {
                if (!is_array($row)) {
                    continue;
                }
                $id = sanitize_key((string) $key);
                if ($id === '') {
                    continue;
                }
                $label = sanitize_text_field((string) ($row['label'] ?? $id));
                if ($group === 'colors') {
                    $value = sanitize_hex_color((string) ($row['value'] ?? ''));
                    if (!$value) {
                        continue;
                    }
                } elseif ($group === 'fonts') {
                    $value = sanitize_key((string) ($row['value'] ?? 'system'));
                    if (!in_array($value, ['system', 'arial', 'verdana', 'tahoma', 'trebuchet', 'georgia', 'times', 'courier'], true)) {
                        $value = 'system';
                    }
                } else {
                    $value = max(0, min(200, (int) ($row['value'] ?? 0)));
                }
                $out[$group][$id] = ['label' => $label, 'value' => $value];
            }
        }
        return $out;
    }

    /** @param array<string,mixed> $component */
    private static function syncComponentAcrossPages(array $component): int
    {
        $id = sanitize_key((string) ($component['id'] ?? ''));
        $template = isset($component['model']) && is_array($component['model']) ? $component['model'] : [];
        $templateNodes = isset($template['nodes']) && is_array($template['nodes']) ? array_values($template['nodes']) : [];
        $templateRoot = null;
        foreach ($templateNodes as $node) {
            if (is_array($node) && (string) ($node['parentId'] ?? '') === '') {
                $templateRoot = $node;
                break;
            }
        }
        if ($id === '' || !is_array($templateRoot)) {
            return 0;
        }

        $changedPages = 0;
        foreach (get_pages(['post_status' => ['publish', 'draft', 'pending', 'private', 'future']]) as $page) {
            if (!$page instanceof \WP_Post) {
                continue;
            }
            $postId = (int) $page->ID;
            $model = LayoutModel::get($postId);
            $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
            $instanceIds = [];
            foreach ($nodes as $node) {
                $props = is_array($node['props'] ?? null) ? $node['props'] : [];
                if ((string) ($props['suiteComponentId'] ?? '') === $id) {
                    $instanceIds[] = (string) ($node['id'] ?? '');
                }
            }
            if (!$instanceIds) {
                continue;
            }
            foreach ($instanceIds as $instanceId) {
                $nodes = self::replaceComponentInstance($nodes, $instanceId, $templateNodes, $templateRoot, $id, (int) ($component['version'] ?? 1));
            }
            $model['nodes'] = $nodes;
            LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'Synkronisér global komponent: ' . (string) ($component['name'] ?? $id));
            $changedPages++;
        }
        return $changedPages;
    }

    /** @param array<int,array<string,mixed>> $nodes @param array<int,array<string,mixed>> $templateNodes @param array<string,mixed> $templateRoot @return array<int,array<string,mixed>> */
    private static function replaceComponentInstance(array $nodes, string $instanceId, array $templateNodes, array $templateRoot, string $componentId, int $version): array
    {
        $byId = [];
        foreach ($nodes as $node) {
            if (is_array($node) && !empty($node['id'])) {
                $byId[(string) $node['id']] = $node;
            }
        }
        if (!isset($byId[$instanceId])) {
            return $nodes;
        }
        $instance = $byId[$instanceId];
        $remove = [$instanceId => true];
        $changed = true;
        while ($changed) {
            $changed = false;
            foreach ($nodes as $node) {
                $nid = (string) ($node['id'] ?? '');
                $parent = (string) ($node['parentId'] ?? '');
                if ($nid !== '' && isset($remove[$parent]) && !isset($remove[$nid])) {
                    $remove[$nid] = true;
                    $changed = true;
                }
            }
        }
        $kept = array_values(array_filter($nodes, static fn($node): bool => is_array($node) && !isset($remove[(string) ($node['id'] ?? '')])));

        $templateRootId = (string) ($templateRoot['id'] ?? '');
        $idMap = [$templateRootId => $instanceId];
        foreach ($templateNodes as $node) {
            if (!is_array($node)) {
                continue;
            }
            $sourceId = (string) ($node['id'] ?? '');
            if ($sourceId === '' || $sourceId === $templateRootId) {
                continue;
            }
            $base = substr(sanitize_key($instanceId . '-' . substr(md5($sourceId), 0, 8)), 0, 90);
            $candidate = $base !== '' ? $base : 'component-node-' . substr(md5($instanceId . $sourceId), 0, 12);
            $suffix = 2;
            while (isset($byId[$candidate]) || in_array($candidate, $idMap, true)) {
                $candidate = substr($base, 0, 84) . '-' . $suffix;
                $suffix++;
            }
            $idMap[$sourceId] = $candidate;
        }

        $clones = [];
        foreach ($templateNodes as $source) {
            if (!is_array($source)) {
                continue;
            }
            $sourceId = (string) ($source['id'] ?? '');
            if (!isset($idMap[$sourceId])) {
                continue;
            }
            $next = $source;
            $next['id'] = $idMap[$sourceId];
            if ($sourceId === $templateRootId) {
                $next['parentId'] = (string) ($instance['parentId'] ?? '');
                $next['order'] = (int) ($instance['order'] ?? 10);
                $next['geometry'] = $instance['geometry'] ?? ($source['geometry'] ?? []);
                $next['props'] = is_array($source['props'] ?? null) ? $source['props'] : [];
                $next['props']['suiteComponentId'] = $componentId;
                $next['props']['suiteComponentVersion'] = $version;
                $next['props']['suiteLabel'] = (string) (($instance['props']['suiteLabel'] ?? '') ?: ($next['props']['suiteLabel'] ?? ''));
            } else {
                $next['parentId'] = $idMap[(string) ($source['parentId'] ?? '')] ?? $instanceId;
            }
            $clones[] = $next;
        }
        return array_merge($kept, $clones);
    }

    /** @param array<string,mixed> $tokens */
    private static function syncTokensAcrossPages(array $tokens): int
    {
        $changedPages = 0;
        foreach (get_pages(['post_status' => ['publish', 'draft', 'pending', 'private', 'future']]) as $page) {
            if (!$page instanceof \WP_Post) {
                continue;
            }
            $model = LayoutModel::get((int) $page->ID);
            $changed = false;
            foreach ($model['nodes'] as &$node) {
                if (!is_array($node) || !isset($node['props']) || !is_array($node['props'])) {
                    continue;
                }
                $props = &$node['props'];
                $color = self::tokenValue($tokens, 'colors', (string) ($props['suiteTokenBackground'] ?? ''));
                if (is_string($color) && $color !== '') {
                    if (array_key_exists('background', $props)) {
                        $props['background'] = $color;
                    } elseif (array_key_exists('boxBackground', $props)) {
                        $props['boxBackground'] = $color;
                    }
                    $changed = true;
                }
                $text = self::tokenValue($tokens, 'colors', (string) ($props['suiteTokenText'] ?? ''));
                if (is_string($text) && $text !== '') {
                    if (array_key_exists('textColor', $props)) {
                        $props['textColor'] = $text;
                    }
                    if (array_key_exists('headingColor', $props)) {
                        $props['headingColor'] = $text;
                    }
                    $changed = true;
                }
                $radius = self::tokenValue($tokens, 'radius', (string) ($props['suiteTokenRadius'] ?? ''));
                if (is_int($radius) && array_key_exists('radius', $props)) {
                    $props['radius'] = $radius;
                    $changed = true;
                }
                $spacing = self::tokenValue($tokens, 'spacing', (string) ($props['suiteTokenSpacing'] ?? ''));
                if (is_int($spacing)) {
                    if (array_key_exists('padding', $props)) {
                        $props['padding'] = $spacing;
                    }
                    $props['gapY'] = $spacing;
                    $changed = true;
                }
                $font = self::tokenValue($tokens, 'fonts', (string) ($props['suiteTokenFont'] ?? ''));
                if (is_string($font) && $font !== '') {
                    if (array_key_exists('fontFamily', $props)) {
                        $props['fontFamily'] = $font;
                    }
                    if (array_key_exists('headingFontFamily', $props)) {
                        $props['headingFontFamily'] = $font;
                    }
                    $changed = true;
                }
                unset($props);
            }
            unset($node);
            if ($changed) {
                LayoutModel::saveVersion((int) $page->ID, $model, get_current_user_id(), 'Synkronisér Design Tokens');
                $changedPages++;
            }
        }
        return $changedPages;
    }

    /** @param array<string,mixed> $tokens @return mixed */
    private static function tokenValue(array $tokens, string $group, string $key)
    {
        if ($key === '' || !isset($tokens[$group][$key]) || !is_array($tokens[$group][$key])) {
            return null;
        }
        return $tokens[$group][$key]['value'] ?? null;
    }
}
