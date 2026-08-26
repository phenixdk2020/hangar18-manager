from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly 1 match, found {count}')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# 1. Canonical model: add button as a real leaf element.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Model/LayoutModel.php'
text = read(path)
text = replace_once(
    text,
    "if (!in_array($type, ['section', 'container', 'text', 'image'], true)) {",
    "if (!in_array($type, ['section', 'container', 'text', 'image', 'button'], true)) {",
    'LayoutModel allowed types'
)
button_props = """        if ($type === 'button') {
            $linkType = strtolower((string) ($raw['linkType'] ?? 'url'));
            if (!in_array($linkType, ['page', 'url', 'anchor', 'email', 'phone'], true)) {
                $linkType = 'url';
            }
            return array_merge([
                'text' => sanitize_text_field((string) ($raw['text'] ?? 'Knap')),
                'linkType' => $linkType,
                'pageId' => absint($raw['pageId'] ?? 0),
                'url' => sanitize_text_field((string) ($raw['url'] ?? '')),
                'targetBlank' => !empty($raw['targetBlank']),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#30382a')) ?: '#30382a',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#ffffff')) ?: '#ffffff',
                'hoverBackground' => sanitize_hex_color((string) ($raw['hoverBackground'] ?? '#525a5f')) ?: '#525a5f',
                'hoverTextColor' => sanitize_hex_color((string) ($raw['hoverTextColor'] ?? '#ffffff')) ?: '#ffffff',
                'focusColor' => sanitize_hex_color((string) ($raw['focusColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'paddingX' => self::clamp($raw['paddingX'] ?? 20, 0, 120, 20),
                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),
            ], $border);
        }
"""
text = replace_once(
    text,
    "        if ($type === 'image') {\n",
    button_props + "        if ($type === 'image') {\n",
    'LayoutModel button props insertion'
)
write(path, text)


# ---------------------------------------------------------------------------
# 2. Multi-template Header/Footer storage and resolver.
# ---------------------------------------------------------------------------
template_model = r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Model;

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
            return $id;
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

    public static function resolveId(int $postId, string $type): string
    {
        $type = self::type($type);
        $choice = self::pageChoice($postId, $type);
        if ($choice === 'none') {
            return '';
        }
        if ($choice !== 'auto') {
            $meta = self::meta($choice);
            if ($meta && !empty($meta['active'])) {
                return $choice;
            }
        }
        $default = self::defaultId($type);
        $meta = $default !== '' ? self::meta($default) : null;
        return $meta && !empty($meta['active']) ? $default : '';
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
        return $name !== '' ? mb_substr($name, 0, 120) : $fallback;
    }

    private static function modelOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_model_v1'; }
    private static function settingsOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_settings_v1'; }
    private static function historyOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_history_v1'; }
    private static function versionOption(string $id): string { return 'h18_clean_tpl_' . self::id($id) . '_version_v1'; }
}
'''
write('clean/hangar18-manager/src/Model/TemplateLayoutModel.php', template_model)


# ---------------------------------------------------------------------------
# 3. Core editor: button type, better transaction labels, history exposure,
#    rich-text preview fidelity.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v018-core.js'
text = read(path)
text = replace_once(text, "const TYPES = ['section', 'container', 'text', 'image'];", "const TYPES = ['section', 'container', 'text', 'image', 'button'];", 'core TYPES')
text = replace_once(
    text,
    "    function normalizeColor(value) { return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? String(value).toLowerCase() : '#000000'; }\n",
    "    function normalizeColor(value) { return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? String(value).toLowerCase() : '#000000'; }\n"
    "    function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap'})[String(type || '')] || String(type || 'Element'); }\n"
    "    function fieldLabel(field) { return ({gx:'X-position',gw:'bredde',gy:'Y-position',gh:'højde',heading:'overskrift',headingLevel:'overskrifttype',text:'tekstindhold',align:'tekstjustering',fit:'billedtilpasning',imageAlignX:'vandret billedplacering',imageAlignY:'lodret billedplacering',boxTransparent:'boksbaggrund',boxBackground:'boksbaggrundsfarve',focalX:'billedfokus X',focalY:'billedfokus Y',alt:'alt-tekst',background:'baggrund',radius:'hjørner',padding:'padding',borderWidth:'ramme',borderColor:'rammefarve',gapX:'Afstand X',gapY:'Afstand Y',buttonText:'knaptekst',linkType:'linktype',pageId:'intern side',url:'linkdestination',targetBlank:'ny fane',textColor:'tekstfarve',hoverBackground:'hover-baggrund',hoverTextColor:'hover-tekstfarve',focusColor:'focus-farve',paddingX:'vandret padding',paddingY:'lodret padding'})[String(field || '')] || String(field || 'felt'); }\n"
    "    function richPreviewHtml(value) {\n"
    "        const raw = String(value || '');\n"
    "        const tpl = document.createElement('template');\n"
    "        tpl.innerHTML = raw.indexOf('<') === -1 ? raw.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\r?\\n/g, '<br>') : raw;\n"
    "        const allowed = new Set(['P','BR','STRONG','B','EM','I','U','S','UL','OL','LI','A']);\n"
    "        Array.from(tpl.content.querySelectorAll('*')).forEach(function (el) {\n"
    "            if (!allowed.has(el.tagName)) { el.replaceWith(...Array.from(el.childNodes)); return; }\n"
    "            Array.from(el.attributes).forEach(function (attr) {\n"
    "                const ok = el.tagName === 'A' && ['href','target','rel'].includes(attr.name.toLowerCase());\n"
    "                if (!ok) { el.removeAttribute(attr.name); }\n"
    "            });\n"
    "            if (el.tagName === 'A') {\n"
    "                const href = String(el.getAttribute('href') || '');\n"
    "                if (/^javascript:/i.test(href)) { el.removeAttribute('href'); }\n"
    "            }\n"
    "        });\n"
    "        return tpl.innerHTML;\n"
    "    }\n",
    'core helpers'
)
button_normalize = """        if (type === 'button') {
            const linkType = ['page', 'url', 'anchor', 'email', 'phone'].includes(String(raw.linkType || '').toLowerCase()) ? String(raw.linkType).toLowerCase() : 'url';
            return Object.assign(common, {
                text: String(raw.text || 'Knap'),
                linkType: linkType,
                pageId: parseInt(raw.pageId || 0, 10) || 0,
                url: String(raw.url || ''),
                targetBlank: !!raw.targetBlank,
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#30382a',
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#ffffff',
                hoverBackground: /^#[0-9a-f]{6}$/i.test(String(raw.hoverBackground || '')) ? String(raw.hoverBackground).toLowerCase() : '#525a5f',
                hoverTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.hoverTextColor || '')) ? String(raw.hoverTextColor).toLowerCase() : '#ffffff',
                focusColor: /^#[0-9a-f]{6}$/i.test(String(raw.focusColor || '')) ? String(raw.focusColor).toLowerCase() : '#c3ae83',
                paddingX: clamp(parseInt(raw.paddingX || 20, 10) || 20, 0, 120),
                paddingY: clamp(parseInt(raw.paddingY || 10, 10) || 10, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100)
            });
        }
"""
text = replace_once(text, "        if (type === 'image') {\n", button_normalize + "        if (type === 'image') {\n", 'core button normalize')
text = replace_once(text, "        updateHidden();\n    }\n    function undo() {", "        updateHidden();\n    }\n    window.H18CleanHistory = { labels: function () { return undoStack.map(function (entry) { return entry.label; }); } };\n    function undo() {", 'core history exposure')
text = replace_once(text, "const defaultRows = { section: 20, container: 16, text: 14, image: 20 };", "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8 };", 'core button default height')
text = replace_once(text, "commit(before, 'Tilføj ' + type + ' · ' + p.zone);", "commit(before, 'Tilføj ' + typeLabel(type) + ' · ' + p.zone);", 'core add label')
text = replace_once(text, "commit(before, 'Slet ' + node.type);", "commit(before, 'Slet ' + typeLabel(node.type));", 'core delete label')
text = replace_once(text, "commit(before, 'Flyt ' + node.type + ' · ' + placement.zone);", "commit(before, 'Flyt ' + typeLabel(node.type) + ' · ' + placement.zone);", 'core move label')
text = replace_once(text, "commit(current.before, 'Resize ' + current.id);", "commit(current.before, 'Ændr størrelse på ' + typeLabel((nodeById(current.id) || {}).type));", 'core resize label')
text = replace_once(
    text,
    "            body.textContent = String(node.props.text || 'Ny tekst').replace(/<[^>]+>/g, '') || 'Tekst';",
    "            body.innerHTML = richPreviewHtml(String(node.props.text || 'Ny tekst')) || 'Tekst';",
    'core rich preview'
)
button_card = """        } else if (node.type === 'button') {
            wrap.classList.add('h18-clean-node-preview--button');
            const button = document.createElement('span');
            button.className = 'h18-clean-button-preview';
            button.textContent = String(node.props.text || 'Knap');
            button.style.display = 'flex';
            button.style.alignItems = 'center';
            button.style.justifyContent = 'center';
            button.style.width = '100%';
            button.style.height = '100%';
            button.style.boxSizing = 'border-box';
            button.style.background = node.props.background || '#30382a';
            button.style.color = node.props.textColor || '#ffffff';
            button.style.borderRadius = String(node.props.radius || 0) + 'px';
            button.style.padding = String(node.props.paddingY || 10) + 'px ' + String(node.props.paddingX || 20) + 'px';
            wrap.appendChild(button);
"""
text = replace_once(text, "        } else if (node.type === 'image') {\n", button_card + "        } else if (node.type === 'image') {\n", 'core button card')
text = replace_once(text, "({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type]", "({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP'}[node.type]", 'core inspector heading')
button_inspector = """        } else if (node.type === 'button') {
            html += '<label>Knaptekst<input data-field="buttonText" type="text" value="' + escapeAttr(node.props.text || 'Knap') + '"></label>';
            html += '<label>Linktype<select data-field="linkType"><option value="page"' + (node.props.linkType === 'page' ? ' selected' : '') + '>Intern side</option><option value="url"' + (node.props.linkType === 'url' ? ' selected' : '') + '>Ekstern URL</option><option value="anchor"' + (node.props.linkType === 'anchor' ? ' selected' : '') + '>Anker</option><option value="email"' + (node.props.linkType === 'email' ? ' selected' : '') + '>E-mail</option><option value="phone"' + (node.props.linkType === 'phone' ? ' selected' : '') + '>Telefon</option></select></label>';
            if (node.props.linkType === 'page') {
                html += '<label>Intern side<select data-field="pageId"><option value="0">Vælg side…</option>' + (Array.isArray(CFG.pages) ? CFG.pages.map(function (page) { const id = parseInt(page.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.pageId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(page.title || ('Side ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
            } else {
                const linkLabel = ({url:'URL',anchor:'Anker, fx #kontakt',email:'E-mailadresse',phone:'Telefonnummer'})[node.props.linkType] || 'Destination';
                html += '<label>' + linkLabel + '<input data-field="url" type="text" value="' + escapeAttr(node.props.url || '') + '"></label>';
            }
            html += '<label class="h18-clean-checkbox"><input data-field="targetBlank" type="checkbox"' + (node.props.targetBlank ? ' checked' : '') + '> Åbn i ny fane</label>';
            html += '<div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#30382a') + '"></label><label>Tekstfarve<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#ffffff') + '"></label><label>Hover baggrund<input data-field="hoverBackground" type="color" value="' + escapeAttr(node.props.hoverBackground || '#525a5f') + '"></label><label>Hover tekst<input data-field="hoverTextColor" type="color" value="' + escapeAttr(node.props.hoverTextColor || '#ffffff') + '"></label><label>Focus-farve<input data-field="focusColor" type="color" value="' + escapeAttr(node.props.focusColor || '#c3ae83') + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label><label>Padding X<input data-field="paddingX" type="number" min="0" max="120" value="' + (node.props.paddingX || 20) + '"></label><label>Padding Y<input data-field="paddingY" type="number" min="0" max="120" value="' + (node.props.paddingY || 10) + '"></label></div>';
"""
text = replace_once(text, "        } else if (node.type === 'image') {\n            html += '<button type=\"button\" class=\"button\" id=\"h18-clean-pick-image\">", button_inspector + "        } else if (node.type === 'image') {\n            html += '<button type=\"button\" class=\"button\" id=\"h18-clean-pick-image\">", 'core button inspector')
field_handlers = """                else if (field === 'buttonText') { current.props.text = String(control.value || 'Knap'); }
                else if (field === 'linkType') { current.props.linkType = ['page', 'url', 'anchor', 'email', 'phone'].includes(control.value) ? control.value : 'url'; }
                else if (field === 'pageId') { current.props.pageId = parseInt(control.value || 0, 10) || 0; }
                else if (field === 'url') { current.props.url = String(control.value || ''); }
                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }
                else if (field === 'textColor') { current.props.textColor = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'hoverBackground') { current.props.hoverBackground = normalizeColor(control.value || '#525a5f'); }
                else if (field === 'hoverTextColor') { current.props.hoverTextColor = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'focusColor') { current.props.focusColor = normalizeColor(control.value || '#c3ae83'); }
                else if (field === 'paddingX') { current.props.paddingX = clamp(parseInt(control.value || 20, 10) || 20, 0, 120); }
                else if (field === 'paddingY') { current.props.paddingY = clamp(parseInt(control.value || 10, 10) || 10, 0, 120); }
"""
text = replace_once(text, "                else if (field === 'fit') {", field_handlers + "                else if (field === 'fit') {", 'core button field handlers')
text = replace_once(text, "commit(before, 'Ændr ' + field + ' på ' + current.type);", "commit(before, 'Ændr ' + fieldLabel(field) + ' på ' + typeLabel(current.type));", 'core inspector transaction label')
write(path, text)


# ---------------------------------------------------------------------------
# 4. Hierarchy gate accepts button as a normal leaf.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v0122-hierarchy.js'
text = read(path)
text = replace_once(text, "const TYPES = ['section', 'container', 'text', 'image'];", "const TYPES = ['section', 'container', 'text', 'image', 'button'];", 'hierarchy TYPES')
text = replace_once(text, "        image: 'Billede'\n", "        image: 'Billede',\n        button: 'Knap'\n", 'hierarchy button label')
write(path, text)


# ---------------------------------------------------------------------------
# 5. Rich-text toolbar overlay and exact Undo-label based automatic notes.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v0123-ux.js'
text = read(path)
text = replace_once(
    text,
    "    function automaticChangeNote() {\n        var before = mapNodes(clone(CFG.initialModel || { nodes: [] }));",
    "    function automaticChangeNote() {\n        var labels = window.H18CleanHistory && typeof window.H18CleanHistory.labels === 'function' ? window.H18CleanHistory.labels() : [];\n        labels = Array.isArray(labels) ? labels.filter(Boolean) : [];\n        if (labels.length) { return labels.slice(-12).join(' · ').slice(0, 240); }\n        var before = mapNodes(clone(CFG.initialModel || { nodes: [] }));",
    'automatic notes from undo labels'
)
text = replace_once(
    text,
    "        form.addEventListener('submit', function () {\n            if (window.H18CleanV0120",
    "        form.addEventListener('submit', function () {\n            if (window.H18RichTextV0125 && typeof window.H18RichTextV0125.sync === 'function') { window.H18RichTextV0125.sync(); }\n            if (window.H18CleanV0120",
    'rich text sync before note'
)
write(path, text)

rich_js = r'''(function () {
    'use strict';

    var active = null;

    function cleanHtml(html) {
        var tpl = document.createElement('template');
        tpl.innerHTML = String(html || '');
        var allowed = ['P', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'S', 'UL', 'OL', 'LI', 'A'];
        Array.prototype.slice.call(tpl.content.querySelectorAll('*')).forEach(function (el) {
            if (allowed.indexOf(el.tagName) === -1) {
                el.replaceWith.apply(el, Array.prototype.slice.call(el.childNodes));
                return;
            }
            Array.prototype.slice.call(el.attributes).forEach(function (attr) {
                var ok = el.tagName === 'A' && ['href', 'target', 'rel'].indexOf(attr.name.toLowerCase()) !== -1;
                if (!ok) { el.removeAttribute(attr.name); }
            });
            if (el.tagName === 'A') {
                var href = String(el.getAttribute('href') || '').trim();
                if (/^javascript:/i.test(href)) { el.removeAttribute('href'); }
                if (el.getAttribute('target') === '_blank') { el.setAttribute('rel', 'noopener'); }
            }
        });
        return tpl.innerHTML;
    }

    function plainToHtml(value) {
        var text = String(value || '');
        if (text.indexOf('<') !== -1) { return cleanHtml(text); }
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\r?\n/g, '<br>');
    }

    function command(name, value) {
        if (!active || !active.editor) { return; }
        active.editor.focus();
        try { document.execCommand(name, false, value || null); } catch (ignore) {}
        active.dirty = true;
        active.textarea.value = cleanHtml(active.editor.innerHTML);
        updateCanvasPreview(active.textarea.value);
    }

    function updateCanvasPreview(html) {
        var selected = document.querySelector('.h18-clean-node.is-selected[data-node-id]');
        var body = selected && selected.querySelector(':scope > .h18-clean-node-preview--text .h18-clean-text-body');
        if (body) { body.innerHTML = cleanHtml(html); }
    }

    function sync() {
        if (!active || !active.textarea || !active.editor) { return; }
        var html = cleanHtml(active.editor.innerHTML);
        active.textarea.value = html;
        if (active.dirty) {
            active.dirty = false;
            active.textarea.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    function toolbarButton(label, title, handler) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'button h18-vd-rich-button';
        button.innerHTML = label;
        button.title = title;
        button.addEventListener('mousedown', function (event) { event.preventDefault(); });
        button.addEventListener('click', handler);
        return button;
    }

    function enhance() {
        var textarea = document.querySelector('#h18-clean-inspector textarea[data-field="text"]');
        if (!textarea || textarea.dataset.vdRich === '1') { return; }
        if (active) { sync(); active = null; }
        textarea.dataset.vdRich = '1';

        var shell = document.createElement('div');
        shell.className = 'h18-vd-rich-shell';
        var toolbar = document.createElement('div');
        toolbar.className = 'h18-vd-rich-toolbar';
        var editor = document.createElement('div');
        editor.className = 'h18-vd-rich-editor';
        editor.contentEditable = 'true';
        editor.setAttribute('role', 'textbox');
        editor.setAttribute('aria-multiline', 'true');
        editor.innerHTML = plainToHtml(textarea.value || '');

        active = { textarea: textarea, editor: editor, dirty: false };

        toolbar.appendChild(toolbarButton('<strong>B</strong>', 'Fed', function () { command('bold'); }));
        toolbar.appendChild(toolbarButton('<em>I</em>', 'Kursiv', function () { command('italic'); }));
        toolbar.appendChild(toolbarButton('<u>U</u>', 'Understregning', function () { command('underline'); }));
        toolbar.appendChild(toolbarButton('• Liste', 'Punktopstilling', function () { command('insertUnorderedList'); }));
        toolbar.appendChild(toolbarButton('1. Liste', 'Nummereret liste', function () { command('insertOrderedList'); }));
        toolbar.appendChild(toolbarButton('Link', 'Indsæt/redigér link', function () {
            var url = window.prompt('Linkdestination (URL, #anker, mailto: eller tel:):', 'https://');
            if (url) { command('createLink', url.trim()); }
        }));
        toolbar.appendChild(toolbarButton('× format', 'Fjern formatering', function () { command('removeFormat'); }));

        editor.addEventListener('input', function () {
            if (!active || active.editor !== editor) { return; }
            active.dirty = true;
            textarea.value = cleanHtml(editor.innerHTML);
            updateCanvasPreview(textarea.value);
        });
        editor.addEventListener('blur', function () { sync(); });

        textarea.style.display = 'none';
        textarea.parentNode.insertBefore(shell, textarea);
        shell.appendChild(toolbar);
        shell.appendChild(editor);
        shell.appendChild(textarea);
    }

    function install() {
        var inspector = document.getElementById('h18-clean-inspector');
        if (!inspector) { return; }
        enhance();
        new MutationObserver(function () { enhance(); }).observe(inspector, { childList: true, subtree: true });
        var form = document.getElementById('h18-clean-save-form');
        if (form) { form.addEventListener('submit', sync, true); }
    }

    window.H18RichTextV0125 = { sync: sync };
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
'''
write('clean/hangar18-manager/assets/editor-v0125.js', rich_js)

rich_css = r'''.h18-vd-rich-shell{display:block;margin-top:4px}.h18-vd-rich-toolbar{display:flex;flex-wrap:wrap;gap:4px;padding:6px;border:1px solid #c3c4c7;border-bottom:0;background:#f6f7f7}.h18-vd-rich-button{min-width:34px;padding:0 8px!important}.h18-vd-rich-editor{min-height:150px;max-height:360px;overflow:auto;padding:10px 12px;border:1px solid #8c8f94;background:#fff;color:#1d2327;line-height:1.45;white-space:normal}.h18-vd-rich-editor:focus{border-color:#2271b1;box-shadow:0 0 0 1px #2271b1;outline:0}.h18-vd-rich-editor p{margin:0 0 .75em}.h18-vd-rich-editor ul,.h18-vd-rich-editor ol{padding-left:24px}.h18-clean-node-preview--button{height:100%;width:100%;box-sizing:border-box}.h18-clean-button-preview{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
'''
write('clean/hangar18-manager/assets/editor-v0125.css', rich_css)


# ---------------------------------------------------------------------------
# 6. Frontend renderer: button + explicit rich text parity.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Frontend/Renderer.php'
text = read(path)
text = replace_once(
    text,
    "        echo '.h18-clean-front-text{overflow-wrap:anywhere}';",
    "        echo '.h18-clean-front-text{overflow-wrap:anywhere}';\n        echo '.h18-clean-front-text>p:first-of-type{margin-top:0}.h18-clean-front-text>p:last-child{margin-bottom:0}';\n        echo '.h18-clean-front-button-link{display:flex;width:100%;height:100%;box-sizing:border-box;align-items:center;justify-content:center;text-decoration:none;background:var(--h18-btn-bg);color:var(--h18-btn-color);transition:background-color .15s ease,color .15s ease,border-color .15s ease}';\n        echo '.h18-clean-front-button-link:hover{background:var(--h18-btn-hover-bg);color:var(--h18-btn-hover-color)}';\n        echo '.h18-clean-front-button-link:focus-visible{outline:3px solid var(--h18-btn-focus);outline-offset:2px}';",
    'renderer css button'
)
button_render = r'''        if ($type === 'button') {
            $linkType = in_array((string) ($props['linkType'] ?? 'url'), ['page', 'url', 'anchor', 'email', 'phone'], true) ? (string) $props['linkType'] : 'url';
            $href = '';
            if ($linkType === 'page') {
                $pageId = absint($props['pageId'] ?? 0);
                $permalink = $pageId > 0 ? get_permalink($pageId) : false;
                $href = is_string($permalink) ? $permalink : '';
            } elseif ($linkType === 'anchor') {
                $anchor = trim((string) ($props['url'] ?? ''));
                $href = preg_match('/^#[A-Za-z][A-Za-z0-9_\-:.]*$/', $anchor) ? $anchor : '';
            } elseif ($linkType === 'email') {
                $mail = sanitize_email((string) ($props['url'] ?? ''));
                $href = $mail !== '' ? 'mailto:' . $mail : '';
            } elseif ($linkType === 'phone') {
                $phone = preg_replace('/[^0-9+() .\-]/', '', (string) ($props['url'] ?? ''));
                $href = is_string($phone) && trim($phone) !== '' ? 'tel:' . preg_replace('/[() .\-]/', '', $phone) : '';
            } else {
                $href = esc_url_raw((string) ($props['url'] ?? ''));
            }
            if ($href === '') { $href = '#'; }
            $background = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
            $hoverBackground = sanitize_hex_color((string) ($props['hoverBackground'] ?? '#525a5f')) ?: '#525a5f';
            $hoverTextColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#ffffff')) ?: '#ffffff';
            $focusColor = sanitize_hex_color((string) ($props['focusColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 20)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 10)));
            $buttonStyle = $style . $borderStyle . $spacingStyle . $radiusStyle
                . '--h18-btn-bg:' . $background . ';--h18-btn-color:' . $textColor . ';--h18-btn-hover-bg:' . $hoverBackground . ';--h18-btn-hover-color:' . $hoverTextColor . ';--h18-btn-focus:' . $focusColor . ';padding:0;overflow:visible;';
            $linkStyle = 'border-radius:' . $radius . 'px;padding:' . $paddingY . 'px ' . $paddingX . 'px;';
            $target = !empty($props['targetBlank']) ? ' target="_blank" rel="noopener"' : '';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-button" style="' . esc_attr($buttonStyle) . '"><a class="h18-clean-front-button-link" href="' . esc_url($href) . '"' . $target . ' style="' . esc_attr($linkStyle) . '">' . esc_html((string) ($props['text'] ?? 'Knap')) . '</a></div>';
        }

'''
text = replace_once(text, "        if ($type === 'image') {\n", button_render + "        if ($type === 'image') {\n", 'renderer button block')
write(path, text)


# ---------------------------------------------------------------------------
# 7. Editor page palette + per-page Header/Footer choices + public naming.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Admin/EditorController.php'
text = read(path)
text = replace_once(text, "use Hangar18\\Clean\\Model\\LayoutModel;\n", "use Hangar18\\Clean\\Model\\LayoutModel;\nuse Hangar18\\Clean\\Model\\TemplateLayoutModel;\n", 'EditorController Template use')
text = replace_once(text, "        $model = LayoutModel::get($postId);\n", "        TemplateLayoutModel::ensureMigrated();\n        $model = LayoutModel::get($postId);\n        $headerTemplates = TemplateLayoutModel::all('header');\n        $footerTemplates = TemplateLayoutModel::all('footer');\n        $headerChoice = TemplateLayoutModel::pageChoice($postId, 'header');\n        $footerChoice = TemplateLayoutModel::pageChoice($postId, 'footer');\n", 'EditorController template data')
text = replace_once(
    text,
    "        echo '<input type=\"hidden\" id=\"h18-clean-change-note\" name=\"change_note\" value=\"\">';\n\n        echo '<div class=\"h18-clean-toolbar\">';",
    "        echo '<input type=\"hidden\" id=\"h18-clean-change-note\" name=\"change_note\" value=\"\">';\n\n        echo '<section class=\"h18-clean-page-shell\"><strong>Header / Footer på denne side</strong><label>Header <select name=\"header_template_choice\">';\n        echo '<option value=\"auto\"' . selected($headerChoice, 'auto', false) . '>Automatisk / standard</option><option value=\"none\"' . selected($headerChoice, 'none', false) . '>Ingen Header</option>';\n        foreach ($headerTemplates as $template) { if (!empty($template['active'])) { echo '<option value=\"' . esc_attr((string) $template['id']) . '\"' . selected($headerChoice, (string) $template['id'], false) . '>' . esc_html((string) $template['name']) . '</option>'; } }\n        echo '</select></label><label>Footer <select name=\"footer_template_choice\">';\n        echo '<option value=\"auto\"' . selected($footerChoice, 'auto', false) . '>Automatisk / standard</option><option value=\"none\"' . selected($footerChoice, 'none', false) . '>Ingen Footer</option>';\n        foreach ($footerTemplates as $template) { if (!empty($template['active'])) { echo '<option value=\"' . esc_attr((string) $template['id']) . '\"' . selected($footerChoice, (string) $template['id'], false) . '>' . esc_html((string) $template['name']) . '</option>'; } }\n        echo '</select></label><span class=\"description\">Header og Footer vælges uafhængigt. Frontend-overtagelse aktiveres først med Theme-shell.</span></section>';\n\n        echo '<div class=\"h18-clean-toolbar\">';",
    'EditorController page shell selectors'
)
text = replace_once(text, "            'image' => 'Billede',\n", "            'image' => 'Billede',\n            'button' => 'Knap',\n", 'EditorController button palette')
text = replace_once(
    text,
    "            $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gem fra Visual Designer');",
    "            $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');\n            TemplateLayoutModel::ensureMigrated();\n            TemplateLayoutModel::setPageChoice($postId, 'header', sanitize_key((string) wp_unslash($_POST['header_template_choice'] ?? 'auto')));\n            TemplateLayoutModel::setPageChoice($postId, 'footer', sanitize_key((string) wp_unslash($_POST['footer_template_choice'] ?? 'auto')));",
    'EditorController save shell choices'
)
text = text.replace('Clean version', 'Designer-version')
text = text.replace('Clean-version', 'Designer-version')
text = text.replace('clean layout', 'Visual Designer-layout')
write(path, text)


# ---------------------------------------------------------------------------
# 8. Header/Footer Controller rewritten for named templates.
# ---------------------------------------------------------------------------
global_controller = r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;

final class GlobalDesignerController
{
    private const PAGE = 'h18-clean-header-footer';
    private const SAVE_ACTION = 'h18_clean_global_layout_save';
    private const RESTORE_ACTION = 'h18_clean_global_layout_restore';
    private const TEMPLATE_ACTION = 'h18_clean_global_template_action';
    private const NONCE_SAVE = 'h18_clean_global_layout_save';
    private const NONCE_RESTORE = 'h18_clean_global_layout_restore';
    private const NONCE_TEMPLATE = 'h18_clean_global_template_action';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 8);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 9);
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);
        add_action('admin_post_' . self::RESTORE_ACTION, [self::class, 'restore']);
        add_action('admin_post_' . self::TEMPLATE_ACTION, [self::class, 'templateAction']);
    }

    public static function menu(): void
    {
        remove_submenu_page(AdminController::MENU, self::PAGE);
        add_submenu_page(AdminController::MENU, 'Header / Footer Designer', 'Header / Footer', 'edit_theme_options', self::PAGE, [self::class, 'render']);
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_theme_options') || strpos($hook, self::PAGE) === false) { return; }
        wp_enqueue_media();
        wp_enqueue_style('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.css', [], H18_CLEAN_VERSION);
        wp_enqueue_style('h18-global-designer-v0123', H18_CLEAN_URL . 'assets/global-designer-v0123.css', ['h18-clean-editor-v0125'], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-global-designer-v0123', H18_CLEAN_URL . 'assets/global-designer-v0123.js', ['h18-clean-editor-v0125'], H18_CLEAN_VERSION, true);
    }

    public static function render(): void
    {
        self::guard();
        TemplateLayoutModel::ensureMigrated();
        $part = self::part($_GET['part'] ?? 'header');
        $templates = TemplateLayoutModel::all($part);
        $templateId = sanitize_key((string) ($_GET['template'] ?? ''));
        if ($templateId === '' || !TemplateLayoutModel::exists($templateId, $part)) {
            $templateId = TemplateLayoutModel::defaultId($part);
        }
        if ($templateId === '' && $templates) { $templateId = (string) $templates[0]['id']; }
        if ($templateId === '') { $templateId = TemplateLayoutModel::create($part, $part === 'header' ? 'Header – Standard' : 'Footer – Standard'); }

        $meta = TemplateLayoutModel::meta($templateId) ?? [];
        $model = TemplateLayoutModel::model($templateId);
        $settings = TemplateLayoutModel::settings($templateId);
        $history = array_reverse(TemplateLayoutModel::history($templateId));
        $version = TemplateLayoutModel::version($templateId);
        $label = $part === 'header' ? 'Header' : 'Footer';
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));

        echo '<div class="wrap h18-clean-admin h18-global-designer">';
        echo '<h1>Visual Designer · Header / Footer</h1>';
        echo '<p class="description">Navngivne globale templates med egne modeller og versionshistorik. Header og Footer kan vælges uafhængigt pr. side.</p>';
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }

        echo '<nav class="nav-tab-wrapper h18-global-tabs"><a class="nav-tab' . ($part === 'header' ? ' nav-tab-active' : '') . '" href="' . esc_url(self::url('header')) . '">Headers</a><a class="nav-tab' . ($part === 'footer' ? ' nav-tab-active' : '') . '" href="' . esc_url(self::url('footer')) . '">Footers</a></nav>';

        echo '<section class="h18-global-template-manager"><div class="h18-global-template-list"><h2>' . esc_html($label) . '-templates</h2><table class="widefat striped"><thead><tr><th>Navn</th><th>Status</th><th>Version</th><th>Handling</th></tr></thead><tbody>';
        foreach ($templates as $row) {
            $id = (string) $row['id'];
            echo '<tr><td><strong>' . esc_html((string) $row['name']) . '</strong>' . (!empty($row['isDefault']) ? ' <span class="h18-manager-badge is-ok">Standard</span>' : '') . '</td><td>' . (!empty($row['active']) ? 'Aktiv' : 'Inaktiv') . '</td><td>v' . esc_html((string) ($row['version'] ?? 0)) . '</td><td><a class="button' . ($id === $templateId ? ' button-primary' : '') . '" href="' . esc_url(self::url($part, $id)) . '">Redigér</a> ';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><input type="hidden" name="operation" value="duplicate"><button class="button" type="submit">Duplikér</button></form> ';
            if (empty($row['isDefault'])) { echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><input type="hidden" name="operation" value="default"><button class="button" type="submit">Sæt standard</button></form>'; }
            echo '</td></tr>';
        }
        echo '</tbody></table></div><div class="h18-global-template-create"><h2>Ny ' . esc_html($label) . '</h2><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="operation" value="create"><input type="text" name="template_name" placeholder="Navn" required><button class="button button-primary" type="submit">Opret template</button></form></div></section>';

        echo '<div class="h18-global-statusbar"><strong>' . esc_html((string) ($meta['name'] ?? $label)) . '</strong><span>Version v' . esc_html((string) $version) . '</span><span class="h18-manager-badge is-progress">Under udvikling</span></div>';
        echo '<form class="h18-global-rename" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type="hidden" name="action" value="' . esc_attr(self::TEMPLATE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($templateId) . '"><input type="hidden" name="operation" value="rename"><label>Templatenavn <input type="text" name="template_name" value="' . esc_attr((string) ($meta['name'] ?? '')) . '"></label><button class="button" type="submit">Omdøb</button></form>';

        echo '<form id="h18-clean-save-form" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::NONCE_SAVE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SAVE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($templateId) . '"><input type="hidden" id="h18-clean-model-json" name="model_json" value="' . esc_attr((string) wp_json_encode($model)) . '"><input type="hidden" id="h18-clean-change-note" name="change_note" value="">';

        echo '<section class="h18-global-settings"><label class="h18-clean-checkbox"><input type="checkbox" name="template_active" value="1"' . checked(!empty($meta['active']), true, false) . '> Template aktiv</label>';
        if ($part === 'header') { echo '<label class="h18-clean-checkbox"><input type="checkbox" name="global_sticky" value="1"' . checked(!empty($settings['sticky']), true, false) . '> Sticky Header</label><label class="h18-clean-checkbox"><input type="checkbox" name="global_overlay" value="1"' . checked(!empty($settings['overlay']), true, false) . '> Overlay første sektion</label>'; }
        echo '<label>Indre max-bredde px <input type="number" name="global_content_width" min="320" max="2400" value="' . esc_attr((string) ($settings['contentWidth'] ?? 1440)) . '"></label><p class="description">Theme-shell overtager endnu ikke frontend automatisk. Først tester vi templates og resolver uden risiko for dobbelt Header/Footer.</p></section>';

        echo '<div class="h18-clean-toolbar"><button type="button" class="button" id="h18-clean-undo" disabled>↶ Fortryd</button><button type="button" class="button" id="h18-clean-redo" disabled>↷ Gentag</button><span class="h18-clean-grid-label">' . esc_html($label) . ' · 120 units · 8 px lodret snap</span><button type="button" class="button" id="h18-global-local-preview">Forhåndsvis layout</button><button type="submit" class="button button-primary h18-clean-save">Gem ' . esc_html($label) . ' som ny version</button></div>';
        echo '<div class="h18-clean-workspace"><aside class="h18-clean-palette"><h2>Elementer</h2>';
        foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede', 'button' => 'Knap'] as $type => $elementLabel) { echo '<button type="button" draggable="true" class="button h18-clean-add" data-type="' . esc_attr($type) . '">+ ' . esc_html($elementLabel) . '</button>'; }
        echo '<p class="description">Logo kan laves som Billede. Menu-elementet kommer efter template-/Header-layoutet er accepteret.</p></aside><main class="h18-clean-canvas-column"><div id="h18-clean-canvas" class="h18-clean-surface h18-clean-root" data-parent-id=""></div></main><aside class="h18-clean-inspector"><h2>Inspector</h2><div id="h18-clean-inspector"><p class="description">Vælg et element på canvas.</p></div></aside></div></form>';

        echo '<section class="h18-clean-history h18-global-history"><h2>' . esc_html((string) ($meta['name'] ?? $label)) . ' · gemte versioner</h2>';
        if (!$history) { echo '<p>Ingen gemte versioner endnu.</p>'; }
        else { echo '<table class="widefat striped"><thead><tr><th>Version</th><th>Gemt</th><th>Ændringer</th><th>Digest</th><th></th></tr></thead><tbody>'; foreach (array_slice($history, 0, 20) as $entry) { $entryVersion = (int) ($entry['version'] ?? 0); echo '<tr><td><strong>v' . esc_html((string) $entryVersion) . '</strong></td><td>' . esc_html((string) ($entry['savedUtc'] ?? '')) . '</td><td>' . esc_html((string) ($entry['note'] ?? '')) . '</td><td><code>' . esc_html(substr((string) ($entry['digest'] ?? ''), 0, 14)) . '…</code></td><td><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'; wp_nonce_field(self::NONCE_RESTORE); echo '<input type="hidden" name="action" value="' . esc_attr(self::RESTORE_ACTION) . '"><input type="hidden" name="part" value="' . esc_attr($part) . '"><input type="hidden" name="template_id" value="' . esc_attr($templateId) . '"><input type="hidden" name="version" value="' . esc_attr((string) $entryVersion) . '"><button type="submit" class="button">Gendan</button></form></td></tr>'; } echo '</tbody></table>'; }
        echo '</section></div>';
    }

    public static function save(): void
    {
        self::guard(); check_admin_referer(self::NONCE_SAVE); TemplateLayoutModel::ensureMigrated();
        $part = self::part($_POST['part'] ?? 'header'); $id = sanitize_key((string) ($_POST['template_id'] ?? ''));
        if (!TemplateLayoutModel::exists($id, $part)) { self::redirect($part, '', 'error', 'Template findes ikke.'); }
        $decoded = json_decode(isset($_POST['model_json']) ? (string) wp_unslash($_POST['model_json']) : '', true);
        if (!is_array($decoded)) { self::redirect($part, $id, 'error', 'Layoutmodellen er ikke gyldig JSON.'); }
        try {
            $normalized = LayoutModel::normalize($decoded);
            $settings = ['sticky' => !empty($_POST['global_sticky']), 'overlay' => !empty($_POST['global_overlay']), 'contentWidth' => absint($_POST['global_content_width'] ?? 1440)];
            $note = sanitize_text_field((string) wp_unslash($_POST['change_note'] ?? '')); if ($note === '') { $note = 'Opdateret ' . ($part === 'header' ? 'Header' : 'Footer') . '-template'; }
            TemplateLayoutModel::setActive($id, !empty($_POST['template_active']));
            $version = TemplateLayoutModel::saveVersion($id, $normalized, $settings, get_current_user_id(), $note);
            if (!hash_equals(LayoutModel::structuralDigest($normalized), LayoutModel::structuralDigest(TemplateLayoutModel::model($id)))) { throw new \RuntimeException('Save-verifikation fejlede.'); }
            self::redirect($part, $id, 'success', 'Template gemt og verificeret som v' . $version . '.');
        } catch (\Throwable $error) { self::redirect($part, $id, 'error', 'Gem fejlede: ' . $error->getMessage()); }
    }

    public static function restore(): void
    {
        self::guard(); check_admin_referer(self::NONCE_RESTORE); TemplateLayoutModel::ensureMigrated();
        $part = self::part($_POST['part'] ?? 'header'); $id = sanitize_key((string) ($_POST['template_id'] ?? '')); $version = absint($_POST['version'] ?? 0);
        $state = TemplateLayoutModel::exists($id, $part) ? TemplateLayoutModel::historyState($id, $version) : null;
        if ($state === null) { self::redirect($part, $id, 'error', 'Den valgte version findes ikke længere.'); }
        try { TemplateLayoutModel::saveVersion($id, $state['model'], $state['settings'], get_current_user_id(), 'Gendannet fra v' . $version); self::redirect($part, $id, 'success', 'Version v' . $version . ' er gendannet som en ny version.'); }
        catch (\Throwable $error) { self::redirect($part, $id, 'error', 'Gendannelse fejlede: ' . $error->getMessage()); }
    }

    public static function templateAction(): void
    {
        self::guard(); check_admin_referer(self::NONCE_TEMPLATE); TemplateLayoutModel::ensureMigrated();
        $part = self::part($_POST['part'] ?? 'header'); $operation = sanitize_key((string) ($_POST['operation'] ?? '')); $id = sanitize_key((string) ($_POST['template_id'] ?? ''));
        try {
            if ($operation === 'create') { $id = TemplateLayoutModel::create($part, (string) wp_unslash($_POST['template_name'] ?? '')); }
            elseif ($operation === 'duplicate') { $id = TemplateLayoutModel::duplicate($id); }
            elseif ($operation === 'rename') { TemplateLayoutModel::rename($id, (string) wp_unslash($_POST['template_name'] ?? '')); }
            elseif ($operation === 'default') { TemplateLayoutModel::setDefault($part, $id); }
            else { throw new \InvalidArgumentException('Ukendt template-handling.'); }
            self::redirect($part, $id, 'success', 'Template-handlingen er gennemført.');
        } catch (\Throwable $error) { self::redirect($part, $id, 'error', 'Template-handling fejlede: ' . $error->getMessage()); }
    }

    private static function guard(): void { if (!current_user_can('edit_theme_options')) { wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean')); } }
    private static function part($value): string { return sanitize_key((string) $value) === 'footer' ? 'footer' : 'header'; }
    private static function url(string $part, string $template = ''): string { $args = ['page' => self::PAGE, 'part' => self::part($part)]; if ($template !== '') { $args['template'] = sanitize_key($template); } return add_query_arg($args, admin_url('admin.php')); }
    private static function redirect(string $part, string $template, string $status, string $message): void { $args = ['page' => self::PAGE, 'part' => self::part($part), 'vd_status' => sanitize_key($status), 'vd_message' => $message]; if ($template !== '') { $args['template'] = sanitize_key($template); } wp_safe_redirect(add_query_arg($args, admin_url('admin.php'))); exit; }
}
'''
write('clean/hangar18-manager/src/Admin/GlobalDesignerController.php', global_controller)


# ---------------------------------------------------------------------------
# 9. Plugin bootstrap: Template model, current global template, page list,
#    v0.1.25 assets.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/hangar18-manager.php'
text = read(path)
text = replace_once(text, "require_once H18_CLEAN_DIR . 'src/Model/GlobalLayoutModel.php';\n", "require_once H18_CLEAN_DIR . 'src/Model/GlobalLayoutModel.php';\nrequire_once H18_CLEAN_DIR . 'src/Model/TemplateLayoutModel.php';\n", 'bootstrap Template model')
text = replace_once(
    text,
    "        $part = isset($_GET['part']) && sanitize_key((string) $_GET['part']) === 'footer' ? 'footer' : 'header';\n        $postId = 0;\n        $model = \\Hangar18\\Clean\\Model\\GlobalLayoutModel::get($part);",
    "        $part = isset($_GET['part']) && sanitize_key((string) $_GET['part']) === 'footer' ? 'footer' : 'header';\n        $postId = 0;\n        \\Hangar18\\Clean\\Model\\TemplateLayoutModel::ensureMigrated();\n        $templateId = isset($_GET['template']) ? sanitize_key((string) $_GET['template']) : '';\n        if ($templateId === '' || !\\Hangar18\\Clean\\Model\\TemplateLayoutModel::exists($templateId, $part)) { $templateId = \\Hangar18\\Clean\\Model\\TemplateLayoutModel::defaultId($part); }\n        $model = $templateId !== '' ? \\Hangar18\\Clean\\Model\\TemplateLayoutModel::model($templateId) : \\Hangar18\\Clean\\Model\\LayoutModel::empty();",
    'bootstrap global selected template'
)
text = replace_once(
    text,
    "        'initialModel' => $model,\n        'ajaxUrl' => admin_url('admin-ajax.php'),",
    "        'initialModel' => $model,\n        'pages' => array_values(array_map(static function ($page): array { return ['id' => (int) $page->ID, 'title' => (string) $page->post_title]; }, get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC']))),\n        'ajaxUrl' => admin_url('admin-ajax.php'),",
    'bootstrap localized pages'
)
text = replace_once(
    text,
    "    wp_enqueue_style(\n        'h18-clean-editor-v0123-ux',\n        H18_CLEAN_URL . 'assets/editor-v0123-ux.css',\n        ['h18-clean-editor-v0122-hierarchy'],\n        H18_CLEAN_VERSION\n    );\n",
    "    wp_enqueue_style(\n        'h18-clean-editor-v0123-ux',\n        H18_CLEAN_URL . 'assets/editor-v0123-ux.css',\n        ['h18-clean-editor-v0122-hierarchy'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0125',\n        H18_CLEAN_URL . 'assets/editor-v0125.css',\n        ['h18-clean-editor-v0123-ux'],\n        H18_CLEAN_VERSION\n    );\n",
    'bootstrap v0125 css'
)
text = replace_once(
    text,
    "    wp_enqueue_script(\n        'h18-clean-editor-v0123-ux',\n        H18_CLEAN_URL . 'assets/editor-v0123-ux.js',\n        ['h18-clean-editor-v0122-hierarchy'],\n        H18_CLEAN_VERSION,\n        true\n    );\n",
    "    wp_enqueue_script(\n        'h18-clean-editor-v0123-ux',\n        H18_CLEAN_URL . 'assets/editor-v0123-ux.js',\n        ['h18-clean-editor-v0122-hierarchy'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0125',\n        H18_CLEAN_URL . 'assets/editor-v0125.js',\n        ['h18-clean-editor-v0123-ux'],\n        H18_CLEAN_VERSION,\n        true\n    );\n",
    'bootstrap v0125 js'
)
write(path, text)


# ---------------------------------------------------------------------------
# 10. Public naming cleanup in Manager UI. Internal identifiers stay intact.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Admin/AdminController.php'
text = read(path)
replacements = {
    'Clean diagnostics pr. side': 'Visual Designer-diagnostics pr. side',
    'Clean Designer': 'Visual Designer',
    '<th>Clean</th>': '<th>Designer</th>',
    'Clean admin klar': 'Admin-grundlag klar',
    'Clean-datafunktion': 'Visual Designer-datafunktion',
    'ikke indlæst i Clean': 'ikke indlæst i Visual Designer Manager',
    'den kommende modeldrevne Clean-datafunktion': 'den kommende modeldrevne Visual Designer-datafunktion',
    'Indholdsoversigt med direkte adgang til WordPress og Clean Designer': 'Indholdsoversigt med direkte adgang til WordPress og Visual Designer',
}
for old, new in replacements.items():
    text = text.replace(old, new)
write(path, text)


# ---------------------------------------------------------------------------
# 11. Small layout styling for page shell and template manager.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/admin-v0123.css'
text = read(path)
text += "\n.h18-clean-page-shell{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:10px 0;padding:10px 12px;background:#fff;border:1px solid #dcdcde}.h18-clean-page-shell label{display:flex;align-items:center;gap:6px}.h18-global-template-manager{display:grid;grid-template-columns:minmax(0,1fr) minmax(250px,360px);gap:16px;margin:14px 0}.h18-global-template-create,.h18-global-template-list{background:#fff;border:1px solid #dcdcde;padding:12px}.h18-global-template-create h2,.h18-global-template-list h2{margin-top:0}.h18-global-rename{display:flex;align-items:center;gap:8px;margin:10px 0}.h18-global-rename label{display:flex;align-items:center;gap:6px}@media(max-width:900px){.h18-global-template-manager{grid-template-columns:1fr}}\n"
write(path, text)

print('Visual Designer Manager 0.1.25 implementation patch applied successfully.')
