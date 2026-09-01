from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f'Missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding='utf-8') == value:
        return
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    if new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one anchor, found {count}: {old[:140]!r}')
    write(rel, value.replace(old, new, 1))


def regex_replace_once(rel: str, pattern: str, replacement: str) -> None:
    value = read(rel)
    updated, count = re.subn(pattern, replacement, value, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{rel}: regex anchor count {count}: {pattern[:140]!r}')
    write(rel, updated)


MODULE_DESIGN_MODEL = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Model;

final class ModuleDesignModel
{
    public const META = '_h18_vd_module_design_v1';
    public const HISTORY_META = '_h18_vd_module_design_history_v1';
    public const MAX_HISTORY = 50;

    /** @return array<string,mixed> */
    public static function defaults(): array
    {
        return [
            'pageWidth' => 90,
            'columnsDesktop' => 3,
            'columnsTablet' => 2,
            'columnsMobile' => 1,
            'cardGap' => 22,
            'cardMaxWidth' => 0,
            'cardBackground' => '#eee8dc',
            'cardTextColor' => '#30382a',
            'cardPaddingX' => 20,
            'cardPaddingY' => 18,
            'cardRadius' => 6,
            'imageRatio' => '16/9',
            'h1Size' => 44,
            'h2Size' => 31,
            'h3Size' => 21,
            'bodySize' => 16,
            'accentColor' => '#536243',
            'sectionGap' => 44,
        ];
    }

    public static function supports(int $postId): bool
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        return in_array($slug, ['events', 'billedgalleri', 'koeretoejer-og-materiel'], true);
    }

    /** @return array<string,mixed> */
    public static function get(int $postId): array
    {
        $raw = get_post_meta($postId, self::META, true);
        return self::normalize(is_array($raw) ? $raw : []);
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public static function normalize(array $raw): array
    {
        $defaults = self::defaults();
        $ratio = (string) ($raw['imageRatio'] ?? $defaults['imageRatio']);
        if (!in_array($ratio, ['16/9', '3/2', '4/3', '1/1'], true)) {
            $ratio = (string) $defaults['imageRatio'];
        }

        return [
            'pageWidth' => self::clamp($raw['pageWidth'] ?? $defaults['pageWidth'], 60, 100, 90),
            'columnsDesktop' => self::clamp($raw['columnsDesktop'] ?? $defaults['columnsDesktop'], 1, 4, 3),
            'columnsTablet' => self::clamp($raw['columnsTablet'] ?? $defaults['columnsTablet'], 1, 3, 2),
            'columnsMobile' => self::clamp($raw['columnsMobile'] ?? $defaults['columnsMobile'], 1, 2, 1),
            'cardGap' => self::clamp($raw['cardGap'] ?? $defaults['cardGap'], 0, 64, 22),
            'cardMaxWidth' => self::clamp($raw['cardMaxWidth'] ?? $defaults['cardMaxWidth'], 0, 900, 0),
            'cardBackground' => self::color($raw['cardBackground'] ?? $defaults['cardBackground'], '#eee8dc'),
            'cardTextColor' => self::color($raw['cardTextColor'] ?? $defaults['cardTextColor'], '#30382a'),
            'cardPaddingX' => self::clamp($raw['cardPaddingX'] ?? $defaults['cardPaddingX'], 0, 64, 20),
            'cardPaddingY' => self::clamp($raw['cardPaddingY'] ?? $defaults['cardPaddingY'], 0, 64, 18),
            'cardRadius' => self::clamp($raw['cardRadius'] ?? $defaults['cardRadius'], 0, 40, 6),
            'imageRatio' => $ratio,
            'h1Size' => self::clamp($raw['h1Size'] ?? $defaults['h1Size'], 24, 72, 44),
            'h2Size' => self::clamp($raw['h2Size'] ?? $defaults['h2Size'], 18, 56, 31),
            'h3Size' => self::clamp($raw['h3Size'] ?? $defaults['h3Size'], 14, 40, 21),
            'bodySize' => self::clamp($raw['bodySize'] ?? $defaults['bodySize'], 12, 24, 16),
            'accentColor' => self::color($raw['accentColor'] ?? $defaults['accentColor'], '#536243'),
            'sectionGap' => self::clamp($raw['sectionGap'] ?? $defaults['sectionGap'], 12, 100, 44),
        ];
    }

    /** @return array<string,mixed> */
    public static function forRender(int $postId): array
    {
        if (
            isset($_GET['h18_vd_module_preview'], $_GET['h18_vd_module_design'])
            && current_user_can('edit_pages')
        ) {
            $json = (string) wp_unslash($_GET['h18_vd_module_design']);
            if ($json !== '' && strlen($json) <= 8192) {
                $decoded = json_decode($json, true);
                if (is_array($decoded)) {
                    return self::normalize($decoded);
                }
            }
        }
        return self::get($postId);
    }

    /** @param array<string,mixed> $design */
    public static function digest(array $design): string
    {
        $json = wp_json_encode(self::normalize($design), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) {
            throw new \RuntimeException('Moduldesign kunne ikke serialiseres.');
        }
        return hash('sha256', $json);
    }

    /** @param array<string,mixed> $design */
    public static function save(int $postId, array $design, int $version): void
    {
        $normalized = self::normalize($design);
        update_post_meta($postId, self::META, $normalized);

        $history = get_post_meta($postId, self::HISTORY_META, true);
        $history = is_array($history) ? array_values(array_filter($history, 'is_array')) : [];
        $history = array_values(array_filter($history, static fn(array $row): bool => (int) ($row['version'] ?? 0) !== $version));
        $history[] = [
            'version' => max(0, $version),
            'savedUtc' => gmdate('c'),
            'digest' => self::digest($normalized),
            'design' => $normalized,
        ];
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }
        update_post_meta($postId, self::HISTORY_META, $history);
    }

    /** @return array<string,mixed>|null */
    public static function historyDesign(int $postId, int $version): ?array
    {
        $history = get_post_meta($postId, self::HISTORY_META, true);
        if (!is_array($history)) {
            return null;
        }
        foreach ($history as $row) {
            if (!is_array($row) || (int) ($row['version'] ?? 0) !== $version || !isset($row['design']) || !is_array($row['design'])) {
                continue;
            }
            return self::normalize($row['design']);
        }
        return null;
    }

    private static function clamp(mixed $value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int) round((float) $value)));
    }

    private static function color(mixed $value, string $fallback): string
    {
        $clean = sanitize_hex_color((string) $value);
        return is_string($clean) && $clean !== '' ? strtolower($clean) : $fallback;
    }

    private function __construct() {}
}
'''

MODULE_DESIGN_JS = r'''(() => {
    'use strict';

    const panel = document.querySelector('.h18-vd-module-design-panel');
    const hidden = document.getElementById('h18-module-design-json');
    const frame = document.querySelector('.h18-vd-module-canonical-frame');
    if (!panel || !hidden || !frame) return;

    const fields = Array.from(panel.querySelectorAll('[data-module-design-key]'));
    const reset = panel.querySelector('[data-module-design-reset]');
    let state = {};
    let defaults = {};
    try { state = JSON.parse(hidden.value || '{}') || {}; } catch (error) { state = {}; }
    try { defaults = JSON.parse(panel.getAttribute('data-defaults') || '{}') || {}; } catch (error) { defaults = {}; }

    const readValue = (field) => {
        if (field.type === 'number' || field.type === 'range') {
            const value = Number(field.value);
            return Number.isFinite(value) ? value : 0;
        }
        return String(field.value || '');
    };

    const writeFields = (source) => {
        fields.forEach((field) => {
            const key = field.getAttribute('data-module-design-key');
            if (!key || !(key in source)) return;
            field.value = String(source[key]);
        });
    };

    const syncState = () => {
        fields.forEach((field) => {
            const key = field.getAttribute('data-module-design-key');
            if (!key) return;
            state[key] = readValue(field);
        });
        hidden.value = JSON.stringify(state);
    };

    let timer = 0;
    const refreshPreview = (immediate = false) => {
        syncState();
        window.clearTimeout(timer);
        const run = () => {
            const base = frame.getAttribute('data-base-url') || frame.src;
            const url = new URL(base, window.location.href);
            url.searchParams.set('h18_vd_module_preview', '1');
            url.searchParams.set('h18_vd_module_preview_version', String(window.H18CleanEditor?.version || '0.1.77'));
            url.searchParams.set('h18_vd_module_design', JSON.stringify(state));
            frame.src = url.toString();
        };
        if (immediate) run(); else timer = window.setTimeout(run, 220);
    };

    fields.forEach((field) => {
        field.addEventListener('input', () => refreshPreview(false));
        field.addEventListener('change', () => refreshPreview(true));
    });

    if (reset) {
        reset.addEventListener('click', () => {
            state = { ...defaults };
            writeFields(state);
            refreshPreview(true);
        });
    }

    writeFields(state);
})();
'''

MODULE_DESIGN_CSS = r'''/* VD-MODULE-DESIGN-001 · v0.1.77 */
.h18-vd-module-designer-layout{display:grid;grid-template-columns:minmax(270px,330px) minmax(0,1fr);gap:20px;align-items:start;margin-top:18px}
.h18-vd-module-design-panel{position:sticky;top:32px;background:#fff;border:1px solid #dcdcde;border-radius:6px;padding:16px;box-sizing:border-box}
.h18-vd-module-design-panel h2{margin:0 0 6px;font-size:18px}.h18-vd-module-design-panel>p{margin:0 0 16px;color:#646970}
.h18-vd-module-design-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.h18-vd-module-design-grid label{display:flex;flex-direction:column;gap:5px;font-weight:600;min-width:0}
.h18-vd-module-design-grid input,.h18-vd-module-design-grid select{width:100%;min-width:0;box-sizing:border-box}.h18-vd-module-design-grid input[type=color]{min-height:38px;padding:2px}
.h18-vd-module-design-span-2{grid-column:1/-1}.h18-vd-module-design-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.h18-vd-module-design-help{margin-top:12px!important;font-size:12px}
.h18-vd-module-designer-layout .h18-vd-module-canonical-preview{margin:0;min-width:0}.h18-vd-module-designer-layout .h18-vd-module-canonical-frame{min-height:760px}
@media(max-width:1100px){.h18-vd-module-designer-layout{grid-template-columns:1fr}.h18-vd-module-design-panel{position:static}.h18-vd-module-design-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.h18-vd-module-design-span-2{grid-column:auto}}
@media(max-width:782px){.h18-vd-module-design-grid{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.h18-vd-module-design-grid{grid-template-columns:1fr}}
'''

V0177_STATUS = '''# Visual Designer Manager v0.1.77 – Moduldesign\n\n**Dato:** 1. september 2026  \n**Status:** Release candidate; central ZIP/manifest-build kræves efter grøn QA.\n\n## Scope\n- Events, Billedgalleri og Køretøjer får et redigerbart **Moduldesign** i Visual Designer.\n- Samme canonical `CollectionPageRenderer` bruges fortsat i Designer-preview og frontend.\n- Live preview bruger kun en autoriseret same-origin preview-override; den publicerede side læser gemt post-meta.\n- Designparametre: sidebredde, Desktop/Tablet/Mobil-kolonner, kortafstand, maks. kortbredde, kortbaggrund, tekstfarve, padding, radius, kortbilledformat, H1/H2/H3, brødtekst, accentfarve og sektionsafstand.\n- `_old`-paritet er standardprofilen: 90% sidebredde, 3/2/1 kolonner, 22px gap, beige #eee8dc og 16:9 kortbilleder.\n- Moduldesign gemmes sammen med en Designer-version og kan gendannes ved versions-restore.\n\n## Releasegrænse\n- Source bumpes til `0.1.77` efter QA.\n- `clean-update.json` og ZIP må først ændres af central `visual-designer-release.yml`.\n'''

RELEASE_NOTES = '''<h2>0.1.77 – Redigerbart moduldesign</h2>\n<ul>\n<li><strong>Events, Billedgalleri og Køretøjer:</strong> de tre canonical modulsider kan nu designes direkte i Visual Designer uden at opgive Designer/frontend-paritet.</li>\n<li>Nyt <strong>Moduldesign</strong> styrer sidebredde, kolonner pr. breakpoint, kortafstand/maksbredde, baggrund, tekstfarve, padding, radius, billedformat, typografi, accentfarve og sektionsafstand.</li>\n<li>Designændringer vises live i den samme <code>CollectionPageRenderer</code> som frontend via en autoriseret same-origin preview-override.</li>\n<li><code>_old</code>-udseendet er fortsat standardprofil: 90% frame, 3/2/1 kolonner, 22px gap, beige kortkrop og 16:9 coverbilleder.</li>\n<li>Moduldesign gemmes versionsstyret og følger restore af tidligere Designer-versioner.</li>\n<li>Alle funktioner fra v0.1.76 bevares, herunder søgning/sortering, eventarkiv, event→album samt Kontakt/Bliv medlem-formularer.</li>\n</ul>\n'''

# New canonical model and editor assets.
write('clean/hangar18-manager/src/Model/ModuleDesignModel.php', MODULE_DESIGN_MODEL)
write('clean/hangar18-manager/assets/module-design-v0177.js', MODULE_DESIGN_JS)
write('clean/hangar18-manager/assets/module-design-v0177.css', MODULE_DESIGN_CSS)
write('docs/v0177-status.md', V0177_STATUS)
write('clean-release-notes.html', RELEASE_NOTES)

# Plugin version + bootstrap.
replace_once('clean/hangar18-manager/hangar18-manager.php', '* Version: 0.1.76', '* Version: 0.1.77')
replace_once("clean/hangar18-manager/hangar18-manager.php", "define('H18_CLEAN_VERSION', '0.1.76');", "define('H18_CLEAN_VERSION', '0.1.77');")
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';\nrequire_once H18_CLEAN_DIR . 'src/Model/ModuleDesignModel.php';\n",
)

# Collection renderer consumes the saved/preview design through CSS variables while retaining
# the v0.1.76 static fallback declarations for regression compatibility.
replace_once(
    'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "use VisualDesignerManager\\Modules\\ModuleStore;\n",
    "use VisualDesignerManager\\Modules\\ModuleStore;\nuse VisualDesignerManager\\Model\\ModuleDesignModel;\n",
)
replace_once(
    'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    "        return self::style() . $body;\n",
    "        $design = ModuleDesignModel::forRender($postId);\n        return self::style($design) . $body;\n",
)

style_method = r'''    /** @param array<string,mixed> $design */
    private static function style(array $design): string
    {
        $pageWidth = (int) ($design['pageWidth'] ?? 90);
        $desktop = (int) ($design['columnsDesktop'] ?? 3);
        $tablet = (int) ($design['columnsTablet'] ?? 2);
        $mobile = (int) ($design['columnsMobile'] ?? 1);
        $gap = (int) ($design['cardGap'] ?? 22);
        $cardMax = (int) ($design['cardMaxWidth'] ?? 0);
        $cardBackground = (string) ($design['cardBackground'] ?? '#eee8dc');
        $cardText = (string) ($design['cardTextColor'] ?? '#30382a');
        $paddingX = (int) ($design['cardPaddingX'] ?? 20);
        $paddingY = (int) ($design['cardPaddingY'] ?? 18);
        $radius = (int) ($design['cardRadius'] ?? 6);
        $ratio = in_array((string) ($design['imageRatio'] ?? '16/9'), ['16/9', '3/2', '4/3', '1/1'], true) ? (string) $design['imageRatio'] : '16/9';
        $h1 = (int) ($design['h1Size'] ?? 44);
        $h2 = (int) ($design['h2Size'] ?? 31);
        $h3 = (int) ($design['h3Size'] ?? 21);
        $body = (int) ($design['bodySize'] ?? 16);
        $accent = (string) ($design['accentColor'] ?? '#536243');
        $sectionGap = (int) ($design['sectionGap'] ?? 44);
        $maxWidth = $cardMax > 0 ? $cardMax . 'px' : 'none';

        return '<style id="h18-module-page-style-parity-002">'
            . '.h18-module-page{--h18-module-page-width:' . $pageWidth . '%;--h18-module-columns-desktop:' . $desktop . ';--h18-module-columns-tablet:' . $tablet . ';--h18-module-columns-mobile:' . $mobile . ';--h18-module-card-gap:' . $gap . 'px;--h18-module-card-max:' . $maxWidth . ';--h18-module-card-bg:' . $cardBackground . ';--h18-module-card-text:' . $cardText . ';--h18-module-card-pad-x:' . $paddingX . 'px;--h18-module-card-pad-y:' . $paddingY . 'px;--h18-module-card-radius:' . $radius . 'px;--h18-module-image-ratio:' . $ratio . ';--h18-module-h1:' . $h1 . 'px;--h18-module-h2:' . $h2 . 'px;--h18-module-h3:' . $h3 . 'px;--h18-module-body:' . $body . 'px;--h18-module-accent:' . $accent . ';--h18-module-section-gap:' . $sectionGap . 'px;width:90%;max-width:none;width:var(--h18-module-page-width);margin:0 auto;padding:36px 0 58px;color:#30382a;color:var(--h18-module-card-text);font-size:16px;font-size:var(--h18-module-body);box-sizing:border-box}.h18-module-page h1{margin:0 0 30px;font-size:44px;font-size:var(--h18-module-h1);line-height:1.08}.h18-module-section{margin:0 0 44px;margin-bottom:var(--h18-module-section-gap)}.h18-module-section h2{margin:0 0 18px;font-size:31px;font-size:var(--h18-module-h2);line-height:1.15}'
            . '.h18-module-intro{margin:-6px 0 22px;max-width:900px}.h18-module-card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-columns:repeat(var(--h18-module-columns-desktop),minmax(0,1fr));gap:22px;gap:var(--h18-module-card-gap);align-items:start;justify-items:start}.h18-module-card{background:transparent;border:0;border-radius:6px;border-radius:var(--h18-module-card-radius);overflow:hidden;box-shadow:none;min-width:0;width:100%;max-width:var(--h18-module-card-max)}.h18-module-card-image{display:block;width:100%;height:auto;aspect-ratio:16/9;aspect-ratio:var(--h18-module-image-ratio);object-fit:cover}.h18-module-card-body{background:#eee8dc;background:var(--h18-module-card-bg);color:var(--h18-module-card-text);padding:18px 20px 20px;padding:var(--h18-module-card-pad-y) var(--h18-module-card-pad-x);min-height:100%;box-sizing:border-box}.h18-module-card h3{font-size:21px;font-size:var(--h18-module-h3);line-height:1.18;margin:0 0 10px}.h18-module-card h3 a{color:inherit;text-decoration:none}.h18-module-card p{margin:8px 0}.h18-module-meta{font-size:.875em;line-height:1.45}.h18-module-more{font-weight:700;color:#536243;color:var(--h18-module-accent);text-decoration:none}.h18-module-more:hover,.h18-module-more:focus-visible{text-decoration:underline}.h18-module-card-actions{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:14px}.h18-module-description>*:first-child{margin-top:0}.h18-module-description>*:last-child{margin-bottom:0}'
            . '.h18-module-spec-table{width:100%;border-collapse:collapse;margin:14px 0}.h18-module-spec-table th,.h18-module-spec-table td{padding:7px 8px;border-bottom:1px solid rgba(48,56,42,.18);text-align:left;vertical-align:top}.h18-module-spec-table th{width:44%;font-weight:700}.h18-module-count{font-size:.875em;margin-top:14px!important}.h18-module-detail-image{display:block;width:min(100%,1100px);height:auto;max-height:620px;aspect-ratio:16/9;object-fit:cover;border-radius:6px;border-radius:var(--h18-module-card-radius);margin:15px 0 20px}.h18-module-detail-text{max-width:950px;margin:18px 0}.h18-module-back{font-weight:700;text-decoration:none;color:#536243;color:var(--h18-module-accent)}.h18-module-back:hover,.h18-module-back:focus-visible{text-decoration:underline}.h18-module-image-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-columns:repeat(var(--h18-module-columns-desktop),minmax(0,1fr));gap:14px;gap:var(--h18-module-card-gap);margin-top:24px}.h18-module-gallery-image{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border-radius:5px;border-radius:var(--h18-module-card-radius)}'
            . '.h18-module-controls{display:flex;align-items:end;gap:12px;flex-wrap:wrap;margin:-6px 0 30px;padding:0 0 18px;border-bottom:1px solid rgba(48,56,42,.16);background:transparent}.h18-module-controls label{display:flex;flex-direction:column;gap:5px;font-weight:700}.h18-module-search{flex:1 1 300px}.h18-module-controls input,.h18-module-controls select{min-height:40px;border:1px solid #aaa99f;border-radius:4px;background:#fff;padding:7px 10px;font:inherit}.h18-module-controls button{min-height:40px;border:0;border-radius:4px;padding:8px 16px;background:#30382a;color:#fff;font-weight:700;cursor:pointer}.h18-module-reset{padding:9px 4px;font-weight:700;color:#536243;color:var(--h18-module-accent)}.h18-module-empty{padding:18px;background:#eee8dc;background:var(--h18-module-card-bg);border-radius:6px;border-radius:var(--h18-module-card-radius)}'
            . '@media(max-width:980px){.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:repeat(2,minmax(0,1fr));grid-template-columns:repeat(var(--h18-module-columns-tablet),minmax(0,1fr))}}@media(max-width:650px){.h18-module-page{width:92%;width:min(94%,var(--h18-module-page-width));padding-top:24px}.h18-module-card-grid,.h18-module-image-grid{grid-template-columns:1fr;grid-template-columns:repeat(var(--h18-module-columns-mobile),minmax(0,1fr))}.h18-module-controls{align-items:stretch}.h18-module-controls label,.h18-module-controls button{width:100%}}'
            . '</style>';
    }
'''
regex_replace_once(
    'clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php',
    r"    private static function style\(\): string\n    \{.*?\n    \}\n(?=\n    private function __construct)",
    style_method.rstrip('\n'),
)

# Designer imports, assets and canonical module-design state.
replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "use VisualDesignerManager\\Model\\LayoutModel;\n",
    "use VisualDesignerManager\\Model\\LayoutModel;\nuse VisualDesignerManager\\Model\\ModuleDesignModel;\n",
)
replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "        wp_enqueue_script('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.js', ['jquery'], H18_CLEAN_VERSION, true);\n",
    "        wp_enqueue_script('h18-clean-editor', H18_CLEAN_URL . 'assets/editor.js', ['jquery'], H18_CLEAN_VERSION, true);\n        wp_enqueue_style('h18-vd-module-design-v0177', H18_CLEAN_URL . 'assets/module-design-v0177.css', [], H18_CLEAN_VERSION);\n        wp_enqueue_script('h18-vd-module-design-v0177', H18_CLEAN_URL . 'assets/module-design-v0177.js', [], H18_CLEAN_VERSION, true);\n",
)
replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $model = LayoutModel::get($postId);\n",
    "        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];\n        $moduleDesignDefaults = $isCollectionPage ? ModuleDesignModel::defaults() : [];\n        $model = LayoutModel::get($postId);\n",
)
replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "        echo '<input type=\"hidden\" id=\"h18-clean-change-note\" name=\"change_note\" value=\"\">';\n",
    "        echo '<input type=\"hidden\" id=\"h18-clean-change-note\" name=\"change_note\" value=\"\">';\n        echo '<input type=\"hidden\" id=\"h18-module-design-json\" name=\"module_design_json\" value=\"' . esc_attr((string) wp_json_encode($moduleDesign)) . '\">';\n",
)

collection_block = r'''        if ($isCollectionPage) {
            $moduleSlug = sanitize_title((string) get_post_field('post_name', $postId));
            $moduleAdminPage = $moduleSlug === 'events'
                ? 'h18-clean-events'
                : ($moduleSlug === 'billedgalleri' ? 'h18-clean-gallery' : 'h18-clean-vehicles');
            $moduleLabel = $moduleSlug === 'events'
                ? 'Events'
                : ($moduleSlug === 'billedgalleri' ? 'Billedgalleri' : 'Køretøjer');
            $permalink = get_permalink($postId);
            $previewBaseUrl = is_string($permalink) ? $permalink : '';
            $previewUrl = add_query_arg([
                'h18_vd_module_preview' => '1',
                'h18_vd_module_preview_version' => H18_CLEAN_VERSION,
                'h18_vd_module_design' => (string) wp_json_encode($moduleDesign),
            ], $previewBaseUrl);

            echo '<div class="h18-vd-module-designer-layout">';
            echo '<aside class="h18-vd-module-design-panel" data-defaults="' . esc_attr((string) wp_json_encode($moduleDesignDefaults)) . '">';
            echo '<h2>Moduldesign</h2><p>Ændringer vises direkte i den samme renderer som den offentlige side.</p>';
            echo '<div class="h18-vd-module-design-grid">';
            $numberFields = [
                'pageWidth' => ['Sidebredde (%)', 60, 100, 1],
                'columnsDesktop' => ['Kolonner · Desktop', 1, 4, 1],
                'columnsTablet' => ['Kolonner · Tablet', 1, 3, 1],
                'columnsMobile' => ['Kolonner · Mobil', 1, 2, 1],
                'cardGap' => ['Afstand mellem kort (px)', 0, 64, 1],
                'cardMaxWidth' => ['Maks. kortbredde (px · 0=auto)', 0, 900, 10],
                'cardPaddingX' => ['Kort padding vandret (px)', 0, 64, 1],
                'cardPaddingY' => ['Kort padding lodret (px)', 0, 64, 1],
                'cardRadius' => ['Hjørneradius (px)', 0, 40, 1],
                'sectionGap' => ['Afstand mellem sektioner (px)', 12, 100, 1],
                'h1Size' => ['H1 størrelse (px)', 24, 72, 1],
                'h2Size' => ['H2 størrelse (px)', 18, 56, 1],
                'h3Size' => ['Korttitel/H3 (px)', 14, 40, 1],
                'bodySize' => ['Brødtekst (px)', 12, 24, 1],
            ];
            foreach ($numberFields as $key => $field) {
                echo '<label>' . esc_html((string) $field[0]) . '<input type="number" min="' . esc_attr((string) $field[1]) . '" max="' . esc_attr((string) $field[2]) . '" step="' . esc_attr((string) $field[3]) . '" value="' . esc_attr((string) ($moduleDesign[$key] ?? '')) . '" data-module-design-key="' . esc_attr($key) . '"></label>';
            }
            echo '<label>Kortbillede format<select data-module-design-key="imageRatio">';
            foreach (['16/9' => '16:9', '3/2' => '3:2', '4/3' => '4:3', '1/1' => '1:1'] as $value => $label) {
                echo '<option value="' . esc_attr($value) . '"' . selected((string) ($moduleDesign['imageRatio'] ?? '16/9'), $value, false) . '>' . esc_html($label) . '</option>';
            }
            echo '</select></label>';
            echo '<label>Kortbaggrund<input type="color" value="' . esc_attr((string) ($moduleDesign['cardBackground'] ?? '#eee8dc')) . '" data-module-design-key="cardBackground"></label>';
            echo '<label>Tekstfarve<input type="color" value="' . esc_attr((string) ($moduleDesign['cardTextColor'] ?? '#30382a')) . '" data-module-design-key="cardTextColor"></label>';
            echo '<label>Accent/linkfarve<input type="color" value="' . esc_attr((string) ($moduleDesign['accentColor'] ?? '#536243')) . '" data-module-design-key="accentColor"></label>';
            echo '</div>';
            echo '<div class="h18-vd-module-design-actions"><button type="button" class="button" data-module-design-reset>Nulstil til _old-standard</button></div>';
            echo '<p class="h18-vd-module-design-help">Gem som ny version gemmer også Moduldesign. Versions-restore gendanner designet sammen med siden.</p>';
            echo '</aside>';

            echo '<section class="h18-vd-module-canonical-preview">';
            echo '<div class="h18-vd-module-canonical-preview-head"><div><strong>Canonical modul-preview · ' . esc_html($moduleLabel) . '</strong><p>Preview og frontend bruger samme CollectionPageRenderer. Moduldata redigeres fortsat i Manageren.</p></div><div class="h18-vd-module-canonical-preview-actions"><a class="button button-primary" href="' . esc_url(admin_url('admin.php?page=' . $moduleAdminPage)) . '">Redigér ' . esc_html($moduleLabel) . '</a><a class="button" target="_blank" rel="noopener" href="' . esc_url($previewBaseUrl) . '">Åbn offentlig side</a></div></div>';
            echo '<iframe class="h18-vd-module-canonical-frame" title="Canonical frontend-preview" data-base-url="' . esc_attr($previewBaseUrl) . '" src="' . esc_url($previewUrl) . '" loading="eager"></iframe>';
            echo '</section></div>';
        } else {
        echo '<div class="h18-clean-workspace">';'''
regex_replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    r"        if \(\$isCollectionPage\) \{\n            \$moduleSlug = .*?        \} else \{\n        echo '<div class=\"h18-clean-workspace\">';",
    collection_block,
)

save_old = r'''            $sameShell = TemplateLayoutModel::pageChoice($postId, 'header') === ($headerChoice !== '' ? $headerChoice : 'auto')
                && TemplateLayoutModel::pageChoice($postId, 'footer') === ($footerChoice !== '' ? $footerChoice : 'auto');
            $statusAction = sanitize_key((string) wp_unslash($_POST['post_status_action'] ?? ''));
            $desiredStatus = in_array($statusAction, ['publish', 'draft'], true) ? $statusAction : '';
            $currentPostStatus = (string) get_post_status($postId);
            $statusChanged = $desiredStatus !== '' && $desiredStatus !== $currentPostStatus;
            if ($desiredStatus === 'publish' && !current_user_can('publish_pages')) {
                throw new \RuntimeException('Du har ikke rettighed til at publicere sider.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell && !$statusChanged) {
                // A previous Designer save may already be canonical while a page cache still
                // contains older frontend HTML. Touching the page is therefore intentional
                // even on a canonical no-op save.
                self::touchFrontendPage($postId, '', $currentVersion);
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-and-shell-unchanged']);
                self::redirect($postId, 'info', 'Ingen ændringer at gemme.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell) {
                $version = $currentVersion;
            } else {
                $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');
                TemplateLayoutModel::setPageChoice($postId, 'header', $headerChoice);
                TemplateLayoutModel::setPageChoice($postId, 'footer', $footerChoice);
            }'''

save_new = r'''            $sameShell = TemplateLayoutModel::pageChoice($postId, 'header') === ($headerChoice !== '' ? $headerChoice : 'auto')
                && TemplateLayoutModel::pageChoice($postId, 'footer') === ($footerChoice !== '' ? $footerChoice : 'auto');
            $isCollectionPage = CollectionPageRenderer::supports($postId);
            $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];
            $sameModuleDesign = true;
            if ($isCollectionPage) {
                $moduleDesignJson = isset($_POST['module_design_json']) ? (string) wp_unslash($_POST['module_design_json']) : '';
                $moduleDesignRaw = json_decode($moduleDesignJson, true);
                if (!is_array($moduleDesignRaw)) {
                    throw new \RuntimeException('Moduldesign mangler eller er ugyldigt.');
                }
                $moduleDesign = ModuleDesignModel::normalize($moduleDesignRaw);
                $sameModuleDesign = hash_equals(ModuleDesignModel::digest(ModuleDesignModel::get($postId)), ModuleDesignModel::digest($moduleDesign));
            }
            $statusAction = sanitize_key((string) wp_unslash($_POST['post_status_action'] ?? ''));
            $desiredStatus = in_array($statusAction, ['publish', 'draft'], true) ? $statusAction : '';
            $currentPostStatus = (string) get_post_status($postId);
            $statusChanged = $desiredStatus !== '' && $desiredStatus !== $currentPostStatus;
            if ($desiredStatus === 'publish' && !current_user_can('publish_pages')) {
                throw new \RuntimeException('Du har ikke rettighed til at publicere sider.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell && $sameModuleDesign && !$statusChanged) {
                // A previous Designer save may already be canonical while a page cache still
                // contains older frontend HTML. Touching the page is therefore intentional
                // even on a canonical no-op save.
                self::touchFrontendPage($postId, '', $currentVersion);
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-shell-and-module-design-unchanged']);
                self::redirect($postId, 'info', 'Ingen ændringer at gemme.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell && $sameModuleDesign) {
                $version = $currentVersion;
            } else {
                $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : ($isCollectionPage ? 'Gemt Moduldesign' : 'Gemt Visual Designer-layout'));
                TemplateLayoutModel::setPageChoice($postId, 'header', $headerChoice);
                TemplateLayoutModel::setPageChoice($postId, 'footer', $footerChoice);
                if ($isCollectionPage) {
                    ModuleDesignModel::save($postId, $moduleDesign, $version);
                }
            }'''
replace_once('clean/hangar18-manager/src/Admin/EditorController.php', save_old, save_new)

replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "            $copyVersion = LayoutModel::saveVersion($copyId, $target, get_current_user_id(), 'Kopi fra side ' . $postId . ' · v' . $targetVersion);\n            DiagnosticStore::append($postId, 'restore_copy_result',",
    "            $copyVersion = LayoutModel::saveVersion($copyId, $target, get_current_user_id(), 'Kopi fra side ' . $postId . ' · v' . $targetVersion);\n            $copyDesign = ModuleDesignModel::historyDesign($postId, $targetVersion);\n            if ($copyDesign !== null) { ModuleDesignModel::save($copyId, $copyDesign, $copyVersion); }\n            DiagnosticStore::append($postId, 'restore_copy_result',",
)
replace_once(
    'clean/hangar18-manager/src/Admin/EditorController.php',
    "            );\n            self::touchFrontendPage($postId, '', $newVersion);\n            DiagnosticStore::append($postId, 'restore_result', [\n",
    "            );\n            $restoredDesign = ModuleDesignModel::historyDesign($postId, $targetVersion);\n            if ($restoredDesign !== null) { ModuleDesignModel::save($postId, $restoredDesign, $newVersion); }\n            self::touchFrontendPage($postId, '', $newVersion);\n            DiagnosticStore::append($postId, 'restore_result', [\n",
)

# Release history.
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', []) if isinstance(history, dict) else []
versions = [row for row in versions if not (isinstance(row, dict) and str(row.get('version', '')) == '0.1.77')]
versions.insert(0, {
    'version': '0.1.77',
    'date': '2026-09-01',
    'items': [
        'VD-MODULE-DESIGN-001: Events, Billedgalleri og Køretøjer får redigerbart Moduldesign uden separat frontend-implementation.',
        'Sidebredde, responsive kolonner, kort-gap/maksbredde, farver, padding, radius, billedformat, typografi og sektionsafstand kan justeres.',
        'Designerens live preview sender en autoriseret design-override til samme CollectionPageRenderer som den offentlige side.',
        '_old-profilen er standard: 90% frame, 3/2/1 kolonner, 22px gap, #eee8dc og 16:9.',
        'Moduldesign snapshots kobles til Designer-versioner og følger versions-restore.',
    ],
})
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

# Canonical backlog.
backlog_rel = 'docs/clean-backlog-v0100.md'
backlog = read(backlog_rel)
backlog = backlog.replace('**Aktuel release:** v0.1.76', '**Aktuel release:** v0.1.77', 1)
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.76', '## Aktuel milepælsstatus · v0.1.77', 1)
marker = '- **VD-MODULE-CUTOVER-001 — IMPLEMENTERET I v0.1.74:** Events, Billedgalleri og Køretøjer/materiel bruger dynamisk flow-rendering og naturlig indholdshøjde; `_old` er reference, mens den endelige visuelle paritet håndteres særskilt.\n'
addition = '- **VD-MODULE-DESIGN-001 — IMPLEMENTERET I v0.1.77:** Events, Billedgalleri og Køretøjer har redigerbart Moduldesign med live canonical preview og versionsstyrede design-snapshots.\n'
if addition not in backlog:
    if marker not in backlog:
        raise SystemExit('backlog milestone marker missing')
    backlog = backlog.replace(marker, marker + addition, 1)
roadmap_marker = '8. **v0.1.76 – VD-MODULE-VISUAL-PARITY-002 — FÆRDIG:** Events, Billedgalleri og Køretøjer bruger samme canonical frontend-rendering i Designer-preview; kortgeometri, billeder, beige kortkrop, spacing og responsive regler er justeret mod `_old`.\n'
roadmap_add = '9. **v0.1.77 – VD-MODULE-DESIGN-001 — FÆRDIG:** de tre canonical modulsider har redigerbar side-/kortgeometri, typografi og farver med live preview i samme frontend-renderer.\n'
if roadmap_add not in backlog:
    if roadmap_marker not in backlog:
        raise SystemExit('backlog roadmap marker missing')
    backlog = backlog.replace(roadmap_marker, roadmap_marker + roadmap_add, 1)
open_marker = '### CLEAN-RESPONSIVE-009 — DELVIST / MANUEL QA\n'
closed_section = '''### VD-MODULE-DESIGN-001 — FÆRDIG I v0.1.77\n- Gælder `events`, `billedgalleri` og `koeretoejer-og-materiel`.\n- Moduldesign ligger i separat canonical post-meta med validerede defaults og max-grænser.\n- Designer viser et Moduldesign-panel ved siden af canonical iframe-preview og opdaterer preview live.\n- Frontend bruger kun gemt design; preview-override accepteres kun for brugere med `edit_pages`.\n- Designændringer opretter en Designer-version og snapshot, som versions-restore kan gendanne.\n- Standardprofilen bevarer v0.1.76/_old-paritet.\n\n'''
if closed_section not in backlog:
    if open_marker not in backlog:
        raise SystemExit('backlog open marker missing')
    backlog = backlog.replace(open_marker, closed_section + open_marker, 1)
write(backlog_rel, backlog)

print('Applied Visual Designer Manager v0.1.77 module design source changes.')
