from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'clean' / 'hangar18-manager'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Visual Designer Manager 0.1.52
# ---------------------------------------------------------------------------
plugin_path = PLUGIN / 'hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.51', ' * Version: 0.1.52', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.51');", "define('H18_CLEAN_VERSION', '0.1.52');", 'plugin constant version')
plugin = replace_once(
    plugin,
    "require_once H18_CLEAN_DIR . 'src/Migration/ExternalPageSourceService.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';",
    "require_once H18_CLEAN_DIR . 'src/Migration/ExternalPageSourceService.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/VisualBlockConversionService.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';",
    'visual conversion service require',
)
write(plugin_path, plugin)


# ---------------------------------------------------------------------------
# External source extraction: prefer the real page frame and always remove any
# nested legacy shell/navigation before conversion.
# ---------------------------------------------------------------------------
source_path = PLUGIN / 'src' / 'Migration' / 'ExternalPageSourceService.php'
source = read(source_path)
source = source.replace('Visual-Designer-Manager/0.1.51;', 'Visual-Designer-Manager/0.1.52;')
source = replace_once(
    source,
    "        foreach ([\n            '//main[1]',\n            '//article[1]',\n            '//*[contains(concat(\" \", normalize-space(@class), \" \"), \" entry-content \")][1]',\n            '//*[@id=\"content\"][1]',\n            '//body[1]',\n        ] as $query) {",
    "        foreach ([\n            '//*[contains(concat(\" \", normalize-space(@class), \" \"), \" h18-page-frame \")][1]',\n            '//*[contains(concat(\" \", normalize-space(@class), \" \"), \" entry-content \")][1]',\n            '//main[1]',\n            '//article[1]',\n            '//*[@id=\"content\"][1]',\n            '//body[1]',\n        ] as $query) {",
    'external page frame root priority',
)
source = replace_once(
    source,
    "        if (strtolower((string) $root->nodeName) === 'body') {\n            foreach (['header', 'footer', 'nav'] as $tag) {\n                $nodes = $xpath->query('.//' . $tag, $root);\n                if (!$nodes) { continue; }\n                $remove = [];\n                foreach ($nodes as $node) { $remove[] = $node; }\n                foreach ($remove as $node) {\n                    if ($node->parentNode) { $node->parentNode->removeChild($node); }\n                }\n            }\n        }",
    "        // Header/Footer/Menu are global Visual Designer models. They must never\n        // become page nodes, regardless of which content root was selected.\n        foreach (['header', 'footer', 'nav'] as $tag) {\n            $nodes = $xpath->query('.//' . $tag, $root);\n            if (!$nodes) { continue; }\n            $remove = [];\n            foreach ($nodes as $node) { $remove[] = $node; }\n            foreach ($remove as $node) {\n                if ($node->parentNode) { $node->parentNode->removeChild($node); }\n            }\n        }",
    'always remove external shell',
)
# DOM-less fallback should also understand the old Manager page frame.
source = replace_once(
    source,
    "        $body = $raw;\n        if (preg_match('/<main\\b[^>]*>(.*?)<\\/main>/is', $raw, $match)) {",
    "        $body = $raw;\n        if (preg_match('/<!--\\s*HANGAR18-PAGE-FRAME-START\\s*-->(.*?)<!--\\s*HANGAR18-PAGE-FRAME-END\\s*-->/is', $raw, $match)) {\n            $body = (string) $match[1];\n        } elseif (preg_match('/<main\\b[^>]*>(.*?)<\\/main>/is', $raw, $match)) {",
    'fallback page frame',
)
write(source_path, source)


# ---------------------------------------------------------------------------
# Canonical Gutenberg/legacy-page-frame -> LEGO model converter.
# ---------------------------------------------------------------------------
visual_service = r'''<?php

declare(strict_types=1);

namespace Hangar18\Clean\Migration;

use Hangar18\Clean\Model\LayoutModel;

/**
 * Converts visible Gutenberg/page-frame structure into canonical Visual
 * Designer LEGO nodes. It intentionally does not import Header/Footer/Menu;
 * those are global Theme Shell models.
 */
final class VisualBlockConversionService
{
    private const OLIVE = '#30382a';
    private const SAND = '#c3ae83';
    private const OFFWHITE = '#f2f0e8';

    /**
     * @param array<int,string> $warnings
     * @return array<string,mixed>|null
     */
    public static function build(int $postId, string $html, array &$warnings): ?array
    {
        if (!class_exists('DOMDocument') || trim($html) === '') {
            $warnings[] = 'visual-block-conversion-dom-unavailable';
            return null;
        }

        $previous = libxml_use_internal_errors(true);
        $dom = new \DOMDocument('1.0', 'UTF-8');
        $loaded = $dom->loadHTML(
            '<?xml encoding="utf-8" ?><div id="h18-vd-conversion-root">' . $html . '</div>',
            LIBXML_NONET | LIBXML_NOERROR | LIBXML_NOWARNING
        );
        libxml_clear_errors();
        libxml_use_internal_errors($previous);
        if (!$loaded) {
            $warnings[] = 'visual-block-conversion-dom-load-failed';
            return null;
        }

        $root = $dom->getElementById('h18-vd-conversion-root');
        if (!$root instanceof \DOMElement) {
            return null;
        }

        $nodes = [];
        $suffix = substr(hash('sha256', (string) $postId . '|' . $html), 0, 8);
        $sectionOrder = 10;
        $desktopY = 4; // 32 px top frame spacing.
        $mobileY = 3;  // 24 px mobile frame spacing.
        $sectionCount = 0;
        $heroCount = 0;
        $buttonCount = 0;
        $columnCount = 0;

        foreach (self::childElements($root) as $element) {
            if (self::isHidden($element)) { continue; }
            $text = self::plainText($element);
            if ($text === '' && self::firstImage($element) === null) { continue; }

            $classes = self::classes($element);
            if (in_array('h18-page-frame', $classes, true)) {
                // Defensive: ExternalPageSourceService normally returns the frame's
                // children, but accept an extra wrapper without adding a fake section.
                foreach (self::childElements($element) as $nested) {
                    self::appendTopLevel($nested, $nodes, $suffix, $sectionOrder, $desktopY, $mobileY, $sectionCount, $heroCount, $buttonCount, $columnCount);
                }
                continue;
            }
            self::appendTopLevel($element, $nodes, $suffix, $sectionOrder, $desktopY, $mobileY, $sectionCount, $heroCount, $buttonCount, $columnCount);
        }

        if ($sectionCount === 0 || count($nodes) < 2) {
            return null;
        }

        $warnings[] = 'visual-block-conversion-v0152';
        $warnings[] = 'visual-sections-' . $sectionCount;
        if ($heroCount > 0) { $warnings[] = 'visual-hero-image-converted'; }
        if ($buttonCount > 0) { $warnings[] = 'visual-buttons-' . $buttonCount; }
        if ($columnCount > 0) { $warnings[] = 'visual-columns-' . $columnCount; }
        $warnings = array_values(array_unique($warnings));

        return LayoutModel::normalize(['nodes' => $nodes]);
    }

    /** @param array<int,array<string,mixed>> $nodes */
    private static function appendTopLevel(
        \DOMElement $element,
        array &$nodes,
        string $suffix,
        int &$sectionOrder,
        int &$desktopY,
        int &$mobileY,
        int &$sectionCount,
        int &$heroCount,
        int &$buttonCount,
        int &$columnCount
    ): void {
        if (self::isHidden($element)) { return; }
        $classes = self::classes($element);
        if (in_array('avpf-home-hero', $classes, true) || in_array('wp-block-cover', $classes, true)) {
            [$desktopH, $mobileH] = self::buildHero($element, $nodes, $suffix, $sectionOrder, $desktopY, $mobileY);
            $heroCount++;
        } elseif (in_array('avpf-home-tagline', $classes, true)) {
            [$desktopH, $mobileH] = self::buildTagline($element, $nodes, $suffix, $sectionOrder, $desktopY, $mobileY);
        } else {
            [$desktopH, $mobileH, $buttons, $columns] = self::buildContentSection($element, $nodes, $suffix, $sectionOrder, $desktopY, $mobileY);
            $buttonCount += $buttons;
            $columnCount += $columns;
        }
        if ($desktopH <= 0 || $mobileH <= 0) { return; }
        $sectionCount++;
        $sectionOrder += 10;
        $desktopY += $desktopH + 4; // 32 px desktop/laptop section gap.
        $mobileY += $mobileH + 3;   // 24 px mobile section gap.
    }

    /** @param array<int,array<string,mixed>> $nodes @return array{0:int,1:int} */
    private static function buildHero(\DOMElement $element, array &$nodes, string $suffix, int $order, int $desktopY, int $mobileY): array
    {
        $desktopH = 33; // ~264 px; old source is 260 px.
        $mobileH = 23;  // ~184 px; old source is 180 px.
        $sectionId = 'section-hero-' . $suffix . '-' . $order;
        $nodes[] = self::sectionNode($sectionId, $order, $desktopY, $mobileY, $desktopH, $mobileH, '#ffffff');

        $img = self::firstImage($element);
        $url = $img instanceof \DOMElement ? trim($img->getAttribute('src')) : '';
        $alt = $img instanceof \DOMElement ? trim($img->getAttribute('alt')) : '';
        if ($url === '') {
            $style = $element->getAttribute('style');
            if (preg_match('/background-image\s*:\s*url\((["\']?)(.*?)\1\)/i', $style, $match)) {
                $url = trim((string) $match[2]);
            }
        }
        if ($url !== '') {
            $nodes[] = [
                'id' => 'image-hero-' . $suffix . '-' . $order,
                'type' => 'image', 'parentId' => $sectionId, 'order' => 10,
                'geometry' => self::geometry(0, 0, 120, $desktopH, 0, 0, 120, $mobileH),
                'props' => [
                    'mediaId' => 0, 'url' => $url, 'alt' => $alt, 'fit' => 'cover',
                    'imageAlignX' => 'center', 'imageAlignY' => 'center',
                    'boxBackground' => '#ffffff', 'boxTransparent' => true,
                    'focalX' => 50, 'focalY' => 50,
                    'borderWidth' => 0, 'borderColor' => '#000000', 'radius' => 0,
                    'gapX' => 0, 'gapY' => 0,
                ],
            ];
        }
        return [$desktopH, $mobileH];
    }

    /** @param array<int,array<string,mixed>> $nodes @return array{0:int,1:int} */
    private static function buildTagline(\DOMElement $element, array &$nodes, string $suffix, int $order, int $desktopY, int $mobileY): array
    {
        $desktopH = 8;
        $mobileH = 7;
        $background = self::styleColor($element, 'background-color', self::SAND);
        $color = self::styleColor($element, 'color', self::OLIVE);
        $sectionId = 'section-tagline-' . $suffix . '-' . $order;
        $nodes[] = self::sectionNode($sectionId, $order, $desktopY, $mobileY, $desktopH, $mobileH, $background);
        $nodes[] = self::textNode(
            'text-tagline-' . $suffix . '-' . $order,
            $sectionId,
            10,
            self::plainText($element),
            '',
            'h2',
            'center',
            $color,
            self::geometry(2, 0, 116, $desktopH, 3, 0, 114, $mobileH),
            20,
            650,
            0,
            'center'
        );
        return [$desktopH, $mobileH];
    }

    /**
     * @param array<int,array<string,mixed>> $nodes
     * @return array{0:int,1:int,2:int,3:int}
     */
    private static function buildContentSection(\DOMElement $element, array &$nodes, string $suffix, int $order, int $desktopY, int $mobileY): array
    {
        $background = self::styleColor($element, 'background-color', self::OFFWHITE);
        $color = self::styleColor($element, 'color', self::OLIVE);
        $sectionId = 'section-content-' . $suffix . '-' . $order;
        $index = count($nodes);
        $nodes[] = self::sectionNode($sectionId, $order, $desktopY, $mobileY, 20, 16, $background);

        $items = self::collectItems($element);
        if (!$items) {
            $plain = self::plainText($element);
            if ($plain !== '') { $items[] = ['kind' => 'paragraph', 'node' => $element]; }
        }
        [$contentD, $contentM, $buttons, $columns] = self::buildFlow($items, $sectionId, $nodes, $suffix . '-' . $order, 8, 5, $color);
        $desktopH = max(20, $contentD + 8);
        $mobileH = max(16, $contentM + 5);
        $nodes[$index]['geometry'] = self::geometry(6, $desktopY, 108, $desktopH, 0, $mobileY, 120, $mobileH);
        $nodes[$index]['props']['minHeightRows'] = $desktopH;
        return [$desktopH, $mobileH, $buttons, $columns];
    }

    /**
     * @param array<int,array{kind:string,node:\DOMElement}> $items
     * @param array<int,array<string,mixed>> $nodes
     * @return array{0:int,1:int,2:int,3:int}
     */
    private static function buildFlow(array $items, string $parentId, array &$nodes, string $suffix, int $startD, int $startM, string $defaultColor): array
    {
        $dY = $startD;
        $mY = $startM;
        $order = 10;
        $buttons = 0;
        $columns = 0;
        foreach ($items as $item) {
            $node = $item['node'];
            $kind = $item['kind'];
            if (self::isHidden($node)) { continue; }

            if ($kind === 'heading') {
                $tag = strtolower($node->tagName);
                $level = in_array($tag, ['h2','h3','h4','h5','h6'], true) ? $tag : 'h2';
                $desktopH = $level === 'h2' ? 8 : 6;
                $mobileH = $level === 'h2' ? 7 : 6;
                $size = ['h2' => 38, 'h3' => 30, 'h4' => 25, 'h5' => 21, 'h6' => 18][$level] ?? 32;
                $align = self::alignment($node, 'left');
                $nodes[] = self::textNode(
                    'text-heading-' . $suffix . '-' . $order,
                    $parentId, $order, '', self::plainText($node), $level, $align,
                    self::styleColor($node, 'color', $defaultColor),
                    self::geometry(4, $dY, 112, $desktopH, 5, $mY, 110, $mobileH),
                    16, 400, $size, 'top'
                );
                $dY += $desktopH + 1;
                $mY += $mobileH + 1;
            } elseif ($kind === 'paragraph' || $kind === 'list') {
                $html = self::innerHtml($node);
                if ($html === '') { $html = self::plainText($node); }
                $plain = self::plainText($node);
                $desktopH = self::textRows($plain, false);
                $mobileH = self::textRows($plain, true);
                $align = self::alignment($node, 'left');
                $nodes[] = self::textNode(
                    'text-body-' . $suffix . '-' . $order,
                    $parentId, $order, $html, '', 'h2', $align,
                    self::styleColor($node, 'color', $defaultColor),
                    self::geometry(4, $dY, 112, $desktopH, 5, $mY, 110, $mobileH),
                    16, 400, 0, 'top'
                );
                $dY += $desktopH + 1;
                $mY += $mobileH + 1;
            } elseif ($kind === 'button') {
                $label = self::plainText($node);
                if ($label === '') { continue; }
                $href = trim($node->getAttribute('href'));
                $desktopW = max(14, min(32, 10 + (int) ceil(mb_strlen($label) / 2)));
                $desktopX = (120 - $desktopW) / 2;
                $desktopX = (int) floor($desktopX);
                $nodes[] = self::buttonNode(
                    'button-' . $suffix . '-' . $order,
                    $parentId, $order, $label, $href,
                    self::geometry($desktopX, $dY, $desktopW, 7, 5, $mY, 110, 7),
                    self::styleColor($node, 'background-color', self::OLIVE),
                    self::styleColor($node, 'color', '#ffffff')
                );
                $dY += 8;
                $mY += 8;
                $buttons++;
            } elseif ($kind === 'image') {
                $img = strtolower($node->tagName) === 'img' ? $node : self::firstImage($node);
                if (!$img instanceof \DOMElement) { continue; }
                $url = trim($img->getAttribute('src'));
                if ($url === '') { continue; }
                $nodes[] = [
                    'id' => 'image-' . $suffix . '-' . $order,
                    'type' => 'image', 'parentId' => $parentId, 'order' => $order,
                    'geometry' => self::geometry(4, $dY, 112, 28, 5, $mY, 110, 24),
                    'props' => [
                        'mediaId' => 0, 'url' => $url, 'alt' => trim($img->getAttribute('alt')),
                        'fit' => 'contain', 'imageAlignX' => 'center', 'imageAlignY' => 'center',
                        'boxBackground' => '#ffffff', 'boxTransparent' => true,
                        'borderWidth' => 0, 'borderColor' => '#000000', 'radius' => 0,
                        'gapX' => 0, 'gapY' => 0,
                    ],
                ];
                $dY += 29;
                $mY += 25;
            } elseif ($kind === 'columns') {
                [$dHeight, $mHeight, $buttonAdded, $columnAdded] = self::buildColumns($node, $parentId, $nodes, $suffix . '-' . $order, $dY, $mY, $defaultColor, $order);
                $dY += $dHeight + 2;
                $mY += $mHeight + 2;
                $buttons += $buttonAdded;
                $columns += $columnAdded;
            } elseif ($kind === 'card') {
                [$dHeight, $mHeight, $buttonAdded] = self::buildCard($node, $parentId, $nodes, $suffix . '-' . $order, $dY, $mY, $defaultColor, $order, 4, 112, 5, 110);
                $dY += $dHeight + 2;
                $mY += $mHeight + 2;
                $buttons += $buttonAdded;
            }
            $order += 10;
        }
        return [$dY, $mY, $buttons, $columns];
    }

    /**
     * @param array<int,array<string,mixed>> $nodes
     * @return array{0:int,1:int,2:int,3:int}
     */
    private static function buildColumns(\DOMElement $element, string $parentId, array &$nodes, string $suffix, int $desktopY, int $mobileY, string $defaultColor, int $order): array
    {
        $columns = [];
        foreach (self::childElements($element) as $child) {
            if (in_array('wp-block-column', self::classes($child), true)) { $columns[] = $child; }
        }
        if (!$columns) {
            foreach ($element->getElementsByTagName('div') as $child) {
                if ($child instanceof \DOMElement && in_array('wp-block-column', self::classes($child), true)) { $columns[] = $child; }
            }
        }
        $count = count($columns);
        if ($count === 0) { return [0, 0, 0, 0]; }

        $gap = 2;
        $available = 112 - ($gap * ($count - 1));
        $colW = max(12, (int) floor($available / $count));
        $maxDesktopH = 0;
        $mobileCursor = 0;
        $buttonCount = 0;
        foreach ($columns as $i => $column) {
            $card = self::firstDescendantByClass($column, 'avpf-card');
            $contentRoot = $card instanceof \DOMElement ? $card : $column;
            $background = $card instanceof \DOMElement ? self::styleColor($card, 'background-color', '#ffffff') : '';
            $radius = $card instanceof \DOMElement ? 8 : 0;
            $containerId = 'container-column-' . $suffix . '-' . ($i + 1);
            $index = count($nodes);
            $desktopX = 4 + ($i * ($colW + $gap));
            $nodes[] = self::containerNode(
                $containerId, ($i + 1) * 10,
                self::geometry($desktopX, $desktopY, $colW, 20, 5, $mobileY + $mobileCursor, 110, 16),
                $background, $radius, $card instanceof \DOMElement ? 18 : 0
            );
            $items = self::collectItems($contentRoot, $card instanceof \DOMElement);
            [$dEnd, $mEnd, $buttons] = self::buildFlow($items, $containerId, $nodes, $suffix . '-c' . ($i + 1), 3, 3, $defaultColor);
            $dH = max(14, $dEnd + 3);
            $mH = max(14, $mEnd + 3);
            $nodes[$index]['geometry'] = self::geometry($desktopX, $desktopY, $colW, $dH, 5, $mobileY + $mobileCursor, 110, $mH);
            $nodes[$index]['props']['minHeightRows'] = $dH;
            $maxDesktopH = max($maxDesktopH, $dH);
            $mobileCursor += $mH + 2;
            $buttonCount += $buttons;
        }
        return [$maxDesktopH, max(0, $mobileCursor - 2), $buttonCount, $count];
    }

    /**
     * @param array<int,array<string,mixed>> $nodes
     * @return array{0:int,1:int,2:int}
     */
    private static function buildCard(\DOMElement $element, string $parentId, array &$nodes, string $suffix, int $desktopY, int $mobileY, string $defaultColor, int $order, int $dx, int $dw, int $mx, int $mw): array
    {
        $containerId = 'container-card-' . $suffix;
        $index = count($nodes);
        $nodes[] = self::containerNode(
            $containerId, $order,
            self::geometry($dx, $desktopY, $dw, 18, $mx, $mobileY, $mw, 16),
            self::styleColor($element, 'background-color', '#ffffff'), 8, 18
        );
        $items = self::collectItems($element, true);
        [$dEnd, $mEnd, $buttons] = self::buildFlow($items, $containerId, $nodes, $suffix . '-inner', 3, 3, $defaultColor);
        $dH = max(14, $dEnd + 3);
        $mH = max(14, $mEnd + 3);
        $nodes[$index]['geometry'] = self::geometry($dx, $desktopY, $dw, $dH, $mx, $mobileY, $mw, $mH);
        $nodes[$index]['props']['minHeightRows'] = $dH;
        return [$dH, $mH, $buttons];
    }

    /**
     * @return array<int,array{kind:string,node:\DOMElement}>
     */
    private static function collectItems(\DOMElement $root, bool $insideCard = false): array
    {
        $items = [];
        foreach (self::childElements($root) as $child) {
            if (self::isHidden($child)) { continue; }
            $tag = strtolower($child->tagName);
            $classes = self::classes($child);
            if (in_array('wp-block-columns', $classes, true)) {
                $items[] = ['kind' => 'columns', 'node' => $child];
                continue;
            }
            if (!$insideCard && in_array('avpf-card', $classes, true)) {
                $items[] = ['kind' => 'card', 'node' => $child];
                continue;
            }
            if (preg_match('/^h[2-6]$/', $tag)) {
                $items[] = ['kind' => 'heading', 'node' => $child];
                continue;
            }
            if ($tag === 'p' || $tag === 'blockquote') {
                if (self::plainText($child) !== '') { $items[] = ['kind' => 'paragraph', 'node' => $child]; }
                continue;
            }
            if (in_array($tag, ['ul', 'ol'], true)) {
                if (self::plainText($child) !== '') { $items[] = ['kind' => 'list', 'node' => $child]; }
                continue;
            }
            if (in_array('wp-block-buttons', $classes, true) || in_array('wp-block-button', $classes, true)) {
                foreach ($child->getElementsByTagName('a') as $anchor) {
                    if ($anchor instanceof \DOMElement && self::plainText($anchor) !== '') { $items[] = ['kind' => 'button', 'node' => $anchor]; }
                }
                continue;
            }
            if ($tag === 'figure' || $tag === 'img' || in_array('wp-block-image', $classes, true)) {
                if (self::firstImage($child) instanceof \DOMElement || $tag === 'img') { $items[] = ['kind' => 'image', 'node' => $child]; }
                continue;
            }
            $nested = self::collectItems($child, $insideCard);
            foreach ($nested as $item) { $items[] = $item; }
        }
        return $items;
    }

    /** @return array<string,mixed> */
    private static function sectionNode(string $id, int $order, int $desktopY, int $mobileY, int $desktopH, int $mobileH, string $background): array
    {
        return [
            'id' => $id, 'type' => 'section', 'parentId' => '', 'order' => $order,
            'geometry' => self::geometry(6, $desktopY, 108, $desktopH, 0, $mobileY, 120, $mobileH),
            'props' => [
                'background' => $background, 'radius' => 0, 'padding' => 0, 'minHeightRows' => $desktopH,
                'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function containerNode(string $id, int $order, array $geometry, string $background, int $radius, int $padding): array
    {
        return [
            'id' => $id, 'type' => 'container', 'parentId' => '', 'order' => $order,
            'geometry' => $geometry,
            'props' => [
                'background' => $background, 'radius' => $radius, 'padding' => $padding, 'minHeightRows' => (int) ($geometry['desktop']['h'] ?? 0),
                'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function textNode(string $id, string $parentId, int $order, string $text, string $heading, string $headingLevel, string $align, string $color, array $geometry, int $fontSize, int $fontWeight, int $headingSize, string $verticalAlign): array
    {
        return [
            'id' => $id, 'type' => 'text', 'parentId' => $parentId, 'order' => $order,
            'geometry' => $geometry,
            'props' => [
                'heading' => $heading, 'headingLevel' => $headingLevel, 'text' => $text,
                'align' => $align, 'verticalAlign' => $verticalAlign,
                'background' => '#ffffff', 'backgroundTransparent' => true,
                'textColor' => $color, 'headingColor' => $color,
                'padding' => 0, 'radius' => 0,
                'fontFamily' => 'system', 'fontSize' => $fontSize, 'fontWeight' => $fontWeight,
                'lineHeight' => 1.5, 'letterSpacing' => 0,
                'headingFontFamily' => 'body', 'headingFontSize' => $headingSize,
                'headingFontWeight' => 600, 'headingLineHeight' => 1.15, 'headingLetterSpacing' => -0.3,
                'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function buttonNode(string $id, string $parentId, int $order, string $label, string $href, array $geometry, string $background, string $textColor): array
    {
        return [
            'id' => $id, 'type' => 'button', 'parentId' => $parentId, 'order' => $order,
            'geometry' => $geometry,
            'props' => [
                'text' => $label, 'linkType' => 'url', 'pageId' => 0, 'url' => $href,
                'targetBlank' => false, 'background' => $background, 'textColor' => $textColor,
                'hoverBackground' => '#525a5f', 'hoverTextColor' => '#ffffff', 'focusColor' => self::SAND,
                'paddingX' => 22, 'paddingY' => 11, 'autoSize' => true,
                'placementMode' => 'normal', 'zIndex' => 20,
                'borderWidth' => 0, 'borderColor' => $background, 'radius' => 32,
                'gapX' => 0, 'gapY' => 0,
            ],
        ];
    }

    /** @return array<string,array<string,int|bool>> */
    private static function geometry(int $dx, int $dy, int $dw, int $dh, int $mx, int $my, int $mw, int $mh): array
    {
        return [
            'desktop' => ['x' => $dx, 'y' => $dy, 'w' => $dw, 'h' => $dh],
            'laptop' => ['x' => $dx, 'y' => $dy, 'w' => $dw, 'h' => $dh, 'inheritDesktop' => true],
            'tablet' => ['x' => $dx, 'y' => $dy, 'w' => $dw, 'h' => $dh, 'inheritDesktop' => true],
            'mobile' => ['x' => $mx, 'y' => $my, 'w' => $mw, 'h' => $mh, 'inheritDesktop' => false],
        ];
    }

    /** @return array<int,\DOMElement> */
    private static function childElements(\DOMElement $element): array
    {
        $result = [];
        foreach ($element->childNodes as $child) {
            if ($child instanceof \DOMElement) { $result[] = $child; }
        }
        return $result;
    }

    /** @return array<int,string> */
    private static function classes(\DOMElement $element): array
    {
        return array_values(array_filter(preg_split('/\s+/', trim($element->getAttribute('class'))) ?: []));
    }

    private static function isHidden(\DOMElement $element): bool
    {
        $style = strtolower($element->getAttribute('style'));
        return str_contains($style, 'display:none') || str_contains($style, 'display: none')
            || str_contains($style, 'visibility:hidden') || str_contains($style, 'visibility: hidden')
            || $element->hasAttribute('hidden');
    }

    private static function plainText(\DOMElement $element): string
    {
        return trim((string) preg_replace('/\s+/u', ' ', (string) $element->textContent));
    }

    private static function innerHtml(\DOMElement $element): string
    {
        $html = '';
        foreach ($element->childNodes as $child) {
            $part = $element->ownerDocument ? $element->ownerDocument->saveHTML($child) : '';
            if (is_string($part)) { $html .= $part; }
        }
        return trim($html);
    }

    private static function firstImage(\DOMElement $element): ?\DOMElement
    {
        if (strtolower($element->tagName) === 'img') { return $element; }
        $images = $element->getElementsByTagName('img');
        foreach ($images as $image) {
            if ($image instanceof \DOMElement) { return $image; }
        }
        return null;
    }

    private static function firstDescendantByClass(\DOMElement $element, string $class): ?\DOMElement
    {
        foreach ($element->getElementsByTagName('*') as $candidate) {
            if ($candidate instanceof \DOMElement && in_array($class, self::classes($candidate), true)) { return $candidate; }
        }
        return null;
    }

    private static function styleColor(\DOMElement $element, string $property, string $fallback): string
    {
        $style = $element->getAttribute('style');
        if (preg_match('/(?:^|;)\s*' . preg_quote($property, '/') . '\s*:\s*(#[0-9a-f]{6}|#[0-9a-f]{3})(?:\s*!important)?\s*(?:;|$)/i', $style, $match)) {
            $color = strtolower((string) $match[1]);
            if (strlen($color) === 4) {
                $color = '#' . $color[1] . $color[1] . $color[2] . $color[2] . $color[3] . $color[3];
            }
            return $color;
        }
        return $fallback;
    }

    private static function alignment(\DOMElement $element, string $fallback): string
    {
        $classes = self::classes($element);
        foreach (['left','center','right'] as $align) {
            if (in_array('has-text-align-' . $align, $classes, true)) { return $align; }
        }
        if (preg_match('/text-align\s*:\s*(left|center|right)/i', $element->getAttribute('style'), $match)) {
            return strtolower((string) $match[1]);
        }
        return $fallback;
    }

    private static function textRows(string $text, bool $mobile): int
    {
        $length = max(1, mb_strlen($text));
        $chars = $mobile ? 48 : 110;
        $lines = max(1, (int) ceil($length / $chars));
        return max($mobile ? 5 : 4, min($mobile ? 36 : 20, $lines * 4));
    }

    private function __construct()
    {
    }
}
'''
write(PLUGIN / 'src' / 'Migration' / 'VisualBlockConversionService.php', visual_service)


# ---------------------------------------------------------------------------
# PageConversionService: external source uses visual block conversion first,
# with the old one-text importer only as a deliberate fallback.
# ---------------------------------------------------------------------------
service_path = PLUGIN / 'src' / 'Migration' / 'PageConversionService.php'
service = read(service_path)
service = replace_once(
    service,
    "        $sourceTitle = sanitize_text_field((string) ($sourceData['title'] ?? ''));\n        $model = self::modelFromHtml($postId, $html);\n        $digest = LayoutModel::structuralDigest($model);",
    "        $sourceTitle = sanitize_text_field((string) ($sourceData['title'] ?? ''));\n        $model = VisualBlockConversionService::build($postId, $html, $warnings);\n        if ($model === null) {\n            $warnings[] = 'visual-block-conversion-fallback-to-single-text';\n            $model = self::modelFromHtml($postId, $html);\n        }\n        $warnings = array_values(array_unique(array_map('sanitize_text_field', $warnings)));\n        $digest = LayoutModel::structuralDigest($model);",
    'external visual model first',
)
service = service.replace('Godkendt ekstern sidekonvertering v0.1.51', 'Godkendt ekstern visuel sidekonvertering v0.1.52')
service = service.replace('Godkendt lokal sidekonvertering v0.1.51', 'Godkendt lokal sidekonvertering v0.1.52')
write(service_path, service)


# ---------------------------------------------------------------------------
# Conversion admin copy: set the right expectation for the visual importer.
# ---------------------------------------------------------------------------
controller_path = PLUGIN / 'src' / 'Admin' / 'ConversionController.php'
controller = read(controller_path)
controller = replace_once(
    controller,
    "echo '<p class=\"h18-manager-description\">Forbered Visual Designer-versioner af lokale WordPress-sider eller hent en eksisterende side fra et andet offentligt HTTPS-site. Alt oprettes først som QA-kandidat; først <strong>Godkend og aktivér</strong> ændrer mål-sidens Visual Designer-model.</p>';",
    "echo '<p class=\"h18-manager-description\">Forbered Visual Designer-versioner af lokale WordPress-sider eller hent en eksisterende side fra et andet offentligt HTTPS-site. Eksterne Gutenberg/page-frame-sider opdeles nu i rigtige Sektioner, Tekst, Billeder, Knapper og Kasser. Alt oprettes først som QA-kandidat; først <strong>Godkend og aktivér</strong> ændrer mål-sidens Visual Designer-model.</p>';",
    'conversion visual intro',
)
controller = replace_once(
    controller,
    "echo '<p class=\"description\">Kilden læses kun. Scripts og stylesheets importeres ikke. Relative links/billeder gøres absolutte mod kildesiden, og billeder forbliver kilde-linkede i første version. Kandidaten kan forhåndsvises med den aktive Visual Designer Header/Footer.</p>';",
    "echo '<p class=\"description\">Kilden læses kun. På det gamle Hangar18-layout vælges selve <code>h18-page-frame</code>, så gammel Header/Footer/Menu ikke importeres som sideindhold. Hero, baggrundsfarver, Gutenberg-sektioner, kolonner, tekst, billeder og knapper bliver canonical Visual Designer-elementer. Eksterne billeder er fortsat kilde-linkede og skal QA-godkendes.</p>';",
    'external visual explanation',
)
controller = controller.replace('Den eksterne side er hentet som QA-kandidat.', 'Den eksterne side er hentet som visuel QA-kandidat.')
write(controller_path, controller)


# ---------------------------------------------------------------------------
# Release history and status.
# ---------------------------------------------------------------------------
history_path = PLUGIN / 'release-history.json'
history = json.loads(read(history_path))
versions = history.setdefault('versions', [])
if not any(str(v.get('version')) == '0.1.52' for v in versions):
    versions.insert(0, {
        'version': '0.1.52',
        'date': '2026-08-29',
        'items': [
            'CONV-03: ekstern Gutenberg/page-frame-konvertering bygger nu rigtige canonical Sektion/Text/Image/Button/Kasse-noder i stedet for én stor Tekst-node.',
            'test2/Hangar18-sideframe vælges før entry-content, så gammel Header, Footer og desktop/mobile Menu ikke importeres i sideindholdet.',
            'Hjem-reference: 90% desktop/laptop frame, 100% mobil, 32/24 px sektionsafstand, Banner-6 hero, sand tagline og off-white indholdssektioner konverteres strukturelt.',
            'Gutenberg columns/cards bliver Kasser; knapper bliver canonical Button; billeder bliver canonical Image og er fortsat source-linked til QA.',
            'Hvis en ekstern side ikke kan strukturanalyseres, falder importen sikkert tilbage til den tidligere one-text kandidat og markerer fallback som warning.',
        ],
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

status = '''# Visual Designer Manager 0.1.52 – CONV-03 visual conversion\n\n## Scope\n- External page conversion now targets canonical visual structure instead of one giant Text node.\n- Source site remains read-only. Approval is still a separate explicit action.\n- Global Header/Footer/Menu are not part of page conversion.\n\n## test2 home reference contract\n- Source: `https://test2.hangar18.dk/` read-only.\n- Prefer `.h18-page-frame` over generic `.entry-content`.\n- Desktop/Laptop root sections: x=6, w=108 (90%). Mobile: x=0, w=120 (100%).\n- Frame top/gaps: 32 px desktop/laptop; 24 px mobile.\n- Hero: canonical Image with cover fit; source reference Banner-6.jpg; ~260/180 px.\n- Tagline: #c3ae83 / #30382a, centered.\n- `.avpf-section`: canonical Section with #f2f0e8 default and structured Text/Button/Columns/Cards.\n\n## Safety\n- External scripts/styles are not imported.\n- Source images remain external/source-linked and are surfaced as QA warnings.\n- Existing live model is not replaced until Godkend og aktivér.\n- Original local post_content is not overwritten.\n- Source hash is rechecked before approval.\n'''
write(ROOT / 'docs' / 'v0152-status.md', status)

print('Applied Visual Designer Manager 0.1.52 visual conversion patch')
