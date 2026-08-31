<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

final class Renderer
{
    private static bool $forceStandaloneCss = false;

    public static function register(): void
    {
        add_filter('the_content', [self::class, 'content'], 20);
        add_action('wp_head', [self::class, 'css'], 1000);
        add_action('wp_footer', [self::class, 'previewBadge'], 1000);
        add_action('wp_footer', [self::class, 'menuScript'], 1001);
    }

    public static function content(string $content): string
    {
        if (is_admin() || !is_singular('page') || !in_the_loop() || !is_main_query()) {
            return $content;
        }
        $postId = get_the_ID();
        if ($postId <= 0) {
            return $content;
        }

        $preview = self::previewModel($postId);
        if ($preview !== null) {
            $pageHtml = empty($preview['nodes']) ? '' : self::renderModel($preview);
            return ThemeShell::enabled() ? self::renderLiveShell($postId, $pageHtml) : $pageHtml;
        }

        // Safe transition rule: legacy/non-Designer pages are untouched.
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
            return $content;
        }

        $model = LayoutModel::get($postId);
        $pageHtml = empty($model['nodes']) ? '' : self::renderModel($model);
        return ThemeShell::enabled() ? self::renderLiveShell($postId, $pageHtml) : $pageHtml;
    }

    private static function renderLiveShell(int $postId, string $pageHtml): string
    {
        $headerId = ThemeShell::resolvedTemplateId($postId, 'header');
        $footerId = ThemeShell::resolvedTemplateId($postId, 'footer');
        $headerHtml = self::renderResolvedTemplate($headerId, 'header');
        $footerHtml = self::renderResolvedTemplate($footerId, 'footer');

        return '<div class="h18-vd-live-shell" data-h18-vd-shell="active" data-h18-vd-header="' . esc_attr($headerId) . '" data-h18-vd-footer="' . esc_attr($footerId) . '">'
            . '<div class="h18-vd-live-shell-part h18-vd-live-shell-header">' . $headerHtml . '</div>'
            . '<div class="h18-vd-live-shell-part h18-vd-live-shell-page">' . $pageHtml . '</div>'
            . '<div class="h18-vd-live-shell-part h18-vd-live-shell-footer">' . $footerHtml . '</div>'
            . '</div>';
    }

    private static function renderResolvedTemplate(string $templateId, string $type): string
    {
        if ($templateId === '') {
            return '';
        }
        try {
            if (!TemplateLayoutModel::exists($templateId, $type)) {
                return '';
            }
            $model = TemplateLayoutModel::model($templateId);
            return empty($model['nodes']) ? '' : self::renderModel($model);
        } catch (\Throwable $error) {
            // Template failure must never suppress the page itself.
            return '';
        }
    }

    public static function css(): void
    {
        if (!self::$forceStandaloneCss) {
            if (!is_singular('page')) {
                return;
            }
            $postId = get_queried_object_id();
            if ($postId <= 0 || (!metadata_exists('post', $postId, LayoutModel::META) && self::previewModel($postId) === null)) {
                return;
            }
        }
        $rowPx = LayoutModel::ROW_PX;
        echo '<style id="h18-clean-frontend-css">';
        echo '.h18-clean-page,.h18-clean-front-surface{display:grid;position:relative;grid-template-columns:repeat(120,minmax(0,1fr));grid-auto-rows:' . esc_attr((string) $rowPx) . 'px;align-items:stretch;width:100%;box-sizing:border-box;min-width:0}';
        echo '.h18-clean-front-node{box-sizing:border-box;min-width:0;position:relative}';
        echo '.h18-clean-front-container,.h18-clean-front-section{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));grid-auto-rows:' . esc_attr((string) $rowPx) . 'px;align-items:stretch;min-width:0;box-sizing:border-box;background-clip:border-box}';
        echo '.h18-clean-front-text{overflow-wrap:anywhere}';
        echo '.h18-clean-front-text p{margin:0!important;padding:0!important}.h18-clean-front-text ul,.h18-clean-front-text ol{margin:0!important;padding-top:0!important;padding-bottom:0!important}.h18-clean-front-text li{margin:0!important}.h18-clean-front-text a{display:inline!important;margin:0!important;padding:0!important;color:inherit;text-decoration:inherit}';
        echo '.h18-clean-front-button-link{display:flex;width:100%;height:100%;box-sizing:border-box;align-items:center;justify-content:center;text-decoration:none;background:var(--h18-btn-bg);color:var(--h18-btn-color);transition:background-color .15s ease,color .15s ease,border-color .15s ease}';
        echo '.h18-clean-front-button-link:hover{background:var(--h18-btn-hover-bg);color:var(--h18-btn-hover-color)}';
        echo '.h18-clean-front-button-link:focus-visible{outline:3px solid var(--h18-btn-focus);outline-offset:2px}';
        echo '.h18-clean-front-menu{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-menu-list{list-style:none;margin:0;padding:0;display:flex;align-items:center;gap:var(--h18-menu-gap);font-size:var(--h18-menu-size);font-weight:var(--h18-menu-weight);justify-content:var(--h18-menu-justify);width:100%}.h18-clean-front-menu--vertical .h18-clean-front-menu-list{flex-direction:column;align-items:var(--h18-menu-items-align)}.h18-clean-front-menu-list li{margin:0;padding:0}.h18-clean-front-menu-list a{color:var(--h18-menu-color);text-decoration:none;white-space:nowrap}.h18-clean-front-menu-list a:hover,.h18-clean-front-menu-list a:focus-visible{color:var(--h18-menu-hover)}.h18-clean-front-menu-list .current-menu-item>a,.h18-clean-front-menu-list .current_page_item>a{color:var(--h18-menu-active)}.h18-clean-front-menu-toggle{display:none;margin-left:auto;background:transparent;color:var(--h18-menu-color);border:1px solid currentColor;border-radius:4px;padding:6px 10px;font:inherit}.h18-clean-front-menu .sub-menu{list-style:none;margin:4px 0 0;padding:0 0 0 14px}.h18-clean-front-menu--horizontal .sub-menu{display:none;position:absolute;background:inherit;padding:8px}.h18-clean-front-menu--horizontal li:hover>.sub-menu,.h18-clean-front-menu--horizontal li:focus-within>.sub-menu{display:block}@media(max-width:782px){.h18-clean-front-menu[data-mobile-mode="vertical"] .h18-clean-front-menu-list{flex-direction:column;align-items:flex-start}.h18-clean-front-menu[data-mobile-mode="wrap"] .h18-clean-front-menu-list{flex-wrap:wrap}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-toggle{display:block}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list{display:none;flex-direction:column;align-items:flex-start;padding-top:8px}.h18-clean-front-menu[data-mobile-mode="hamburger"].is-open{flex-wrap:wrap}.h18-clean-front-menu[data-mobile-mode="hamburger"].is-open .h18-clean-front-menu-list{display:flex;flex-basis:100%}}';
        echo '@media(max-width:782px){.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="dropdown"].is-open .h18-clean-front-menu-list{background:var(--h18-menu-panel-bg);padding:12px;box-sizing:border-box}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"]{position:relative}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"].is-open:before{content:"";position:fixed;inset:0;background:rgba(0,0,0,.38);z-index:99990}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"].is-open .h18-clean-front-menu-list{display:flex;position:fixed;top:0;bottom:0;width:min(340px,88vw);max-width:88vw;z-index:99991;overflow:auto;box-sizing:border-box;background:var(--h18-menu-panel-bg);padding:68px 24px 24px;gap:18px;align-items:flex-start;justify-content:flex-start}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-right"].is-open .h18-clean-front-menu-list{right:0;left:auto}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-left"].is-open .h18-clean-front-menu-list{left:0;right:auto}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"].is-open .h18-clean-front-menu-toggle{position:fixed;top:16px;z-index:99992;background:var(--h18-menu-panel-bg)}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-right"].is-open .h18-clean-front-menu-toggle{right:16px}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-left"].is-open .h18-clean-front-menu-toggle{left:16px;margin-left:0}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"] .sub-menu{display:block!important;position:static!important;background:transparent!important;padding:8px 0 0 16px!important}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list a{white-space:normal}}';
        echo '.h18-clean-front-text-heading{margin:0 0 8px;line-height:1.2}';
        echo '.h18-clean-front-image{margin:0;width:100%;max-width:none;overflow:hidden;box-sizing:border-box;height:100%}';
        echo '.h18-clean-front-image img{display:block;max-width:none;margin:0;box-sizing:border-box}';
        echo '.h18-clean-front-spacer{pointer-events:none;background:transparent!important;border:0!important}';
        echo '.h18-clean-front-divider{display:flex;align-items:center;justify-content:center;box-sizing:border-box}.h18-clean-front-divider-line{display:block;box-sizing:border-box}';
        echo '.h18-clean-front-icon{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-icon-mark{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box}.h18-clean-front-icon svg{display:block;width:100%;height:100%;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}';
        echo '.h18-clean-front-badge{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-badge-mark{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;white-space:nowrap}';
        echo '.h18-clean-front-link{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-link a{color:var(--h18-link-color);text-decoration:var(--h18-link-decoration);font:inherit}.h18-clean-front-link a:hover,.h18-clean-front-link a:focus-visible{color:var(--h18-link-hover)}';
        echo '.h18-clean-front-datalist{width:100%;box-sizing:border-box}.h18-clean-front-datalist-row{display:grid;grid-template-columns:var(--h18-data-label-width) minmax(0,1fr);box-sizing:border-box}.h18-clean-front-datalist.is-stacked .h18-clean-front-datalist-row{grid-template-columns:1fr}';
        echo '.h18-clean-front-table-wrap{width:100%;overflow-x:auto;box-sizing:border-box}.h18-clean-front-table{width:100%;border-collapse:collapse;table-layout:auto}.h18-clean-front-table th,.h18-clean-front-table td{text-align:left;vertical-align:top;box-sizing:border-box}@media(max-width:782px){.h18-clean-front-table-wrap[data-mobile-mode="cards"]{overflow:visible}.h18-clean-front-table-wrap[data-mobile-mode="cards"] .h18-clean-front-table,.h18-clean-front-table-wrap[data-mobile-mode="cards"] tbody,.h18-clean-front-table-wrap[data-mobile-mode="cards"] tr,.h18-clean-front-table-wrap[data-mobile-mode="cards"] td{display:block;width:100%}.h18-clean-front-table-wrap[data-mobile-mode="cards"] thead{display:none}.h18-clean-front-table-wrap[data-mobile-mode="cards"] tr{margin-bottom:12px;border:1px solid var(--h18-table-border)}.h18-clean-front-table-wrap[data-mobile-mode="cards"] td{display:grid;grid-template-columns:minmax(100px,40%) minmax(0,1fr);gap:10px;border-width:0 0 1px!important}.h18-clean-front-table-wrap[data-mobile-mode="cards"] td:last-child{border-bottom:0!important}.h18-clean-front-table-wrap[data-mobile-mode="cards"] td:before{content:attr(data-label);font-weight:700}}';
        echo '.h18-vd-live-shell,.h18-vd-live-shell-part{display:block;width:100%;max-width:none;margin:0;padding:0;box-sizing:border-box}.h18-vd-live-shell{position:relative}';
        echo '</style>';
    }


    /**
     * Standalone canonical preview used by the Designer. It remains isolated
     * from the active public shell so unsaved work never changes frontend output.
     * Header, page and Footer are rendered by the same PHP renderer as frontend.
     *
     * @param array<string,mixed> $pageModel
     * @param array<string,mixed>|null $headerModel
     * @param array<string,mixed>|null $footerModel
     */
    public static function standaloneDocument(array $pageModel, ?array $headerModel, ?array $footerModel, string $title = 'Visual Designer preview'): string
    {
        $previous = self::$forceStandaloneCss;
        self::$forceStandaloneCss = true;
        ob_start();
        self::css();
        $style = (string) ob_get_clean();
        self::$forceStandaloneCss = $previous;

        $header = $headerModel !== null ? self::renderModel(LayoutModel::normalize($headerModel)) : '';
        $page = self::renderModel(LayoutModel::normalize($pageModel));
        $footer = $footerModel !== null ? self::renderModel(LayoutModel::normalize($footerModel)) : '';
        $safeTitle = esc_html($title);

        return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' . $safeTitle . '</title>'
            . $style
            . '<style>html,body{margin:0;padding:0;background:#fff;color:#1d2327}body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.h18-vd-composite-part{width:100%;margin:0;padding:0}.h18-vd-composite-main{min-height:320px}.h18-clean-front-text-content{display:block;min-width:0}.h18-clean-front-text-content>p:first-child{margin-top:0!important}.h18-clean-front-text-content>p:last-child{margin-bottom:0!important}</style>'
            . '</head><body><header class="h18-vd-composite-part h18-vd-composite-header">' . $header . '</header><main class="h18-vd-composite-part h18-vd-composite-main">' . $page . '</main><footer class="h18-vd-composite-part h18-vd-composite-footer">' . $footer . '</footer>'
            . '<script>(function(){function setOpen(n,o){if(!n)return;n.classList.toggle("is-open",o);var b=n.querySelector(".h18-clean-front-menu-toggle");if(b){b.setAttribute("aria-expanded",o?"true":"false");b.textContent=o?"✕ Luk":"☰ Menu";if(o){window.setTimeout(function(){var first=n.querySelector(".h18-clean-front-menu-list a");if(first)first.focus();},0);}}}document.addEventListener("click",function(e){var b=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-toggle"):null;if(b){var n=b.closest(".h18-clean-front-menu");if(n){setOpen(n,!n.classList.contains("is-open"));}return;}var link=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu.is-open .h18-clean-front-menu-list a"):null;if(link){var nav=link.closest(".h18-clean-front-menu");if(nav&&nav.getAttribute("data-close-on-select")!=="0"){setOpen(nav,false);}return;}document.querySelectorAll(".h18-clean-front-menu.is-open[data-close-outside=\"1\"]").forEach(function(nav){if(!nav.contains(e.target)){setOpen(nav,false);}});});document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;document.querySelectorAll(".h18-clean-front-menu.is-open").forEach(function(nav){setOpen(nav,false);var b=nav.querySelector(".h18-clean-front-menu-toggle");if(b)b.focus();});});})();</script></body></html>';
    }

    public static function menuScript(): void
    {
        if (!is_singular('page')) { return; }
        echo '<script id="h18-clean-menu-js">(function(){function setOpen(n,o){if(!n)return;n.classList.toggle("is-open",o);var b=n.querySelector(".h18-clean-front-menu-toggle");if(b){b.setAttribute("aria-expanded",o?"true":"false");b.textContent=o?"✕ Luk":"☰ Menu";if(o){window.setTimeout(function(){var first=n.querySelector(".h18-clean-front-menu-list a");if(first)first.focus();},0);}}}document.addEventListener("click",function(e){var b=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-toggle"):null;if(b){var n=b.closest(".h18-clean-front-menu");if(n){setOpen(n,!n.classList.contains("is-open"));}return;}var link=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu.is-open .h18-clean-front-menu-list a"):null;if(link){var nav=link.closest(".h18-clean-front-menu");if(nav&&nav.getAttribute("data-close-on-select")!=="0"){setOpen(nav,false);}return;}document.querySelectorAll(".h18-clean-front-menu.is-open[data-close-outside=\"1\"]").forEach(function(nav){if(!nav.contains(e.target)){setOpen(nav,false);}});});document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;document.querySelectorAll(".h18-clean-front-menu.is-open").forEach(function(nav){setOpen(nav,false);var b=nav.querySelector(".h18-clean-front-menu-toggle");if(b)b.focus();});});})();</script>';
    }

    public static function previewKey(int $userId, int $postId, string $token): string
    {
        return 'h18_clean_preview_' . max(0, $userId) . '_' . max(0, $postId) . '_' . sanitize_key($token);
    }

    public static function previewBadge(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $postId = get_queried_object_id();
        if ($postId <= 0 || self::previewModel($postId) === null) {
            return;
        }
        $version = isset($_GET['h18_clean_preview_version']) ? absint($_GET['h18_clean_preview_version']) : 0;
        $label = $version > 0 ? 'Historisk version v' . $version . ' · ikke aktiv' : 'Forhåndsvisning · ikke gemt';
        echo '<div style="position:fixed;right:16px;bottom:16px;z-index:2147483647;padding:8px 12px;border:1px solid #2271b1;border-radius:6px;background:#fff;color:#1d2327;box-shadow:0 4px 18px rgba(0,0,0,.2);font:600 13px/1.3 system-ui,sans-serif;pointer-events:none">' . esc_html($label) . '</div>';
    }

    /** @return array<string,mixed>|null */
    private static function previewModel(int $postId): ?array
    {
        if (!is_user_logged_in() || !current_user_can('edit_pages')) {
            return null;
        }
        $token = isset($_GET['h18_clean_preview']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_preview'])) : '';
        if ($token === '' || !preg_match('/^[a-z0-9]{12,64}$/', $token)) {
            return null;
        }
        $raw = get_transient(self::previewKey(get_current_user_id(), $postId, $token));
        if (!is_array($raw)) {
            return null;
        }
        try {
            return LayoutModel::normalize($raw);
        } catch (\Throwable $error) {
            return null;
        }
    }

    /** @param array<string,mixed> $model */
    private static function renderModel(array $model): string
    {
        $byParent = [];
        $byId = [];
        foreach ($model['nodes'] as $node) {
            $byId[$node['id']] = $node;
            $byParent[$node['parentId']][] = $node;
        }
        foreach ($byParent as &$children) {
            usort($children, static fn(array $a, array $b): int => (int) $a['order'] <=> (int) $b['order']);
        }
        unset($children);

        return '<div class="h18-clean-page h18-clean-front-surface">' . self::children('', $byParent, $byId) . '</div>';
    }

    /** @param array<string,array<int,array<string,mixed>>> $byParent @param array<string,array<string,mixed>> $byId */
    private static function children(string $parentId, array $byParent, array $byId): string
    {
        $html = '';
        foreach ($byParent[$parentId] ?? [] as $node) {
            $html .= self::node($node, $byParent, $byId);
        }
        return $html;
    }

    /** @param array<string,mixed> $node @param array<string,array<int,array<string,mixed>>> $byParent @param array<string,array<string,mixed>> $byId */
    private static function node(array $node, array $byParent, array $byId): string
    {
        $g = isset($node['geometry']['desktop']) && is_array($node['geometry']['desktop']) ? $node['geometry']['desktop'] : ['x' => 0, 'y' => 0, 'w' => 120, 'h' => 0];
        $x = max(0, min(119, (int) ($g['x'] ?? 0)));
        $w = max(1, min(120 - $x, (int) ($g['w'] ?? 120)));
        $y = max(0, (int) ($g['y'] ?? 0));
        $h = max(0, (int) ($g['h'] ?? 0));
        $style = 'grid-column:' . ($x + 1) . '/span ' . $w . ';';
        if ($h > 0) {
            $style .= 'grid-row:' . ($y + 1) . '/span ' . $h . ';min-height:' . ($h * LayoutModel::ROW_PX) . 'px;';
        } elseif ($y !== 0) {
            $style .= 'margin-top:' . ($y * LayoutModel::ROW_PX) . 'px;';
        }

        $id = esc_attr((string) $node['id']);
        $type = (string) $node['type'];
        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $offsetX = max(-2000, min(2000, (int) ($props['offsetX'] ?? 0)));
        $offsetY = max(-2000, min(2000, (int) ($props['offsetY'] ?? 0)));
        $offsetStyle = ($offsetX !== 0 || $offsetY !== 0) ? 'transform:translate(' . $offsetX . 'px,' . $offsetY . 'px);' : '';
        $style .= $offsetStyle;
        $borderStyle = self::borderStyle($props);
        $spacingStyle = self::spacingStyle($props);
        $radius = max(0, min(100, (int) ($props['radius'] ?? 0)));
        $radiusStyle = 'border-radius:' . $radius . 'px;';

        if ($type === 'text') {
            $heading = trim((string) ($props['heading'] ?? ''));
            $headingLevel = in_array((string) ($props['headingLevel'] ?? 'h2'), ['h2', 'h3', 'h4', 'h5', 'h6'], true) ? (string) $props['headingLevel'] : 'h2';
            $headingColor = sanitize_hex_color((string) ($props['headingColor'] ?? '#000000')) ?: '#000000';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#000000')) ?: '#000000';
            $verticalAlign = in_array((string) ($props['verticalAlign'] ?? 'top'), ['top', 'center', 'bottom'], true) ? (string) $props['verticalAlign'] : 'top';
            $verticalJustify = ['top' => 'flex-start', 'center' => 'center', 'bottom' => 'flex-end'][$verticalAlign];
            $background = !empty($props['backgroundTransparent'])
                ? 'transparent'
                : (sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff');
            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
            $bodyFamily = self::fontCss((string) ($props['fontFamily'] ?? 'system'));
            $headingFamilyToken = (string) ($props['headingFontFamily'] ?? 'body');
            $headingFamily = $headingFamilyToken === 'body' ? $bodyFamily : self::fontCss($headingFamilyToken);
            $fontSize = max(8, min(120, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 400)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.5)));
            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));
            $headingSize = max(0, min(160, (int) ($props['headingFontSize'] ?? 0)));
            if ($headingSize === 0) { $headingSize = ['h2' => 32, 'h3' => 28, 'h4' => 24, 'h5' => 20, 'h6' => 18][$headingLevel] ?? 32; }
            $headingWeight = max(100, min(900, (int) ($props['headingFontWeight'] ?? 700)));
            $headingLineHeight = max(0.8, min(3.0, (float) ($props['headingLineHeight'] ?? 1.2)));
            $headingLetterSpacing = max(-10.0, min(30.0, (float) ($props['headingLetterSpacing'] ?? 0)));
            $headingHtml = $heading !== ''
                ? '<' . $headingLevel . ' class="h18-clean-front-text-heading" style="color:' . esc_attr($headingColor) . ';font-family:' . esc_attr($headingFamily) . ';font-size:' . esc_attr((string) $headingSize) . 'px;font-weight:' . esc_attr((string) $headingWeight) . ';line-height:' . esc_attr((string) $headingLineHeight) . ';letter-spacing:' . esc_attr((string) $headingLetterSpacing) . 'px">' . esc_html($heading) . '</' . $headingLevel . '>'
                : '';
            $textStyle = $style . $borderStyle . $spacingStyle . $radiusStyle
                . 'background:' . $background . ';padding:' . $padding . 'px;color:' . $textColor . ';text-align:' . (string) ($props['align'] ?? 'left') . ';font-family:' . $bodyFamily . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;display:flex;flex-direction:column;justify-content:' . $verticalJustify . ';';
            $rawText = (string) ($props['text'] ?? '');
            $bodyHtml = strpos($rawText, '<') === false ? nl2br(esc_html($rawText), false) : wp_kses_post($rawText);
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-text" style="' . esc_attr($textStyle) . '"><div class="h18-clean-front-text-content">' . $headingHtml . $bodyHtml . '</div></div>';
        }

        if ($type === 'menu') {
            $menuId = absint($props['menuId'] ?? 0);
            $orientation = (string) ($props['orientation'] ?? 'horizontal') === 'vertical' ? 'vertical' : 'horizontal';
            $align = in_array((string) ($props['align'] ?? 'right'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'right';
            $mobileMode = in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger';
            $mobilePresentation = in_array((string) ($props['mobilePresentation'] ?? 'dropdown'), ['dropdown', 'panel-right', 'panel-left'], true) ? (string) $props['mobilePresentation'] : 'dropdown';
            $mobileCloseOnSelect = !array_key_exists('mobileCloseOnSelect', $props) || !empty($props['mobileCloseOnSelect']);
            $mobileCloseOutside = !array_key_exists('mobileCloseOutside', $props) || !empty($props['mobileCloseOutside']);
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
            $hoverColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $activeColor = sanitize_hex_color((string) ($props['activeTextColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $baseBackground = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';
            $background = !empty($props['backgroundTransparent']) ? 'transparent' : $baseBackground;
            $fontSize = max(8, min(64, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 600)));
            $gap = max(0, min(120, (int) ($props['menuGap'] ?? 24)));
            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 8)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 8)));
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $itemsAlign = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $rendered = '';
            if ($menuId > 0) {
                $candidate = wp_nav_menu([
                    'menu' => $menuId,
                    'container' => false,
                    'echo' => false,
                    'fallback_cb' => false,
                    'menu_class' => 'h18-clean-front-menu-list',
                    'menu_id' => 'h18-clean-menu-list-' . $id,
                    'depth' => 2,
                ]);
                $rendered = is_string($candidate) ? $candidate : '';
            }
            if ($rendered === '') {
                $rendered = '<ul class="h18-clean-front-menu-list"><li><span>Vælg menu i Visual Designer</span></li></ul>';
            }
            $menuStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $paddingY . 'px ' . $paddingX . 'px;'
                . '--h18-menu-color:' . $textColor . ';--h18-menu-hover:' . $hoverColor . ';--h18-menu-active:' . $activeColor . ';--h18-menu-gap:' . $gap . 'px;'
                . '--h18-menu-size:' . $fontSize . 'px;--h18-menu-weight:' . $fontWeight . ';--h18-menu-justify:' . $justify . ';--h18-menu-items-align:' . $itemsAlign . ';--h18-menu-panel-bg:' . $baseBackground . ';';
            return '<nav id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '" data-mobile-mode="' . esc_attr($mobileMode) . '" data-mobile-presentation="' . esc_attr($mobilePresentation) . '" data-close-on-select="' . ($mobileCloseOnSelect ? '1' : '0') . '" data-close-outside="' . ($mobileCloseOutside ? '1' : '0') . '" aria-label="Navigation" style="' . esc_attr($menuStyle) . '"><button type="button" class="h18-clean-front-menu-toggle" aria-expanded="false" aria-controls="h18-clean-menu-list-' . $id . '">☰ Menu</button>' . $rendered . '</nav>';
        }

        if ($type === 'button') {
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
            $fontFamily = self::fontCss((string) ($props['fontFamily'] ?? 'system'));
            $fontSize = max(8, min(120, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 400)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.2)));
            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));
            $hoverBackground = sanitize_hex_color((string) ($props['hoverBackground'] ?? '#525a5f')) ?: '#525a5f';
            $hoverTextColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#ffffff')) ?: '#ffffff';
            $focusColor = sanitize_hex_color((string) ($props['focusColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 20)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 10)));
            $autoSize = !array_key_exists('autoSize', $props) || !empty($props['autoSize']);
            $whiteSpace = $autoSize ? 'nowrap' : 'normal';
            $placementMode = (string) ($props['placementMode'] ?? 'normal');
            $floating = $placementMode === 'overlay';
            $layoutStyle = $style;
            if ($floating) {
                $leftPct = ($x / LayoutModel::UNITS) * 100;
                $widthPct = ($w / LayoutModel::UNITS) * 100;
                $zIndex = max(1, min(200, (int) ($props['zIndex'] ?? 20)));
                $heightCss = $h > 0 ? 'height:' . ($h * LayoutModel::ROW_PX) . 'px;min-height:' . ($h * LayoutModel::ROW_PX) . 'px;' : '';
                $layoutStyle = 'position:absolute;left:' . $leftPct . '%;top:' . ($y * LayoutModel::ROW_PX) . 'px;width:' . $widthPct . '%;' . $heightCss . 'z-index:' . $zIndex . ';grid-column:auto;grid-row:auto;margin-top:0;' . $offsetStyle;
            }
            $buttonStyle = $layoutStyle . $spacingStyle
                . '--h18-btn-bg:' . $background . ';--h18-btn-color:' . $textColor . ';--h18-btn-hover-bg:' . $hoverBackground . ';--h18-btn-hover-color:' . $hoverTextColor . ';--h18-btn-focus:' . $focusColor . ';padding:0;overflow:visible;';
            $linkStyle = $borderStyle . $radiusStyle . 'padding:' . $paddingY . 'px ' . $paddingX . 'px;'
                . 'font-family:' . $fontFamily . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;white-space:' . $whiteSpace . ';';
            $target = !empty($props['targetBlank']) ? ' target="_blank" rel="noopener"' : '';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-button' . ($floating ? ' h18-clean-front-button--floating' : '') . '" style="' . esc_attr($buttonStyle) . '"><a class="h18-clean-front-button-link" href="' . esc_url($href) . '"' . $target . ' style="' . esc_attr($linkStyle) . '">' . esc_html((string) ($props['text'] ?? 'Knap')) . '</a></div>';
        }

        if ($type === 'spacer') {
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-spacer" aria-hidden="true" style="' . esc_attr($style . $spacingStyle) . '"></div>';
        }

        if ($type === 'divider') {
            $vertical = (string) ($props['orientation'] ?? 'horizontal') === 'vertical';
            $lineColor = sanitize_hex_color((string) ($props['lineColor'] ?? '#c3c4c7')) ?: '#c3c4c7';
            $lineWidth = max(1, min(20, (int) ($props['lineWidth'] ?? 1)));
            $lineStyle = in_array((string) ($props['lineStyle'] ?? 'solid'), ['solid', 'dashed', 'dotted'], true) ? (string) $props['lineStyle'] : 'solid';
            $lineCss = $vertical ? 'height:100%;width:0;border-left:' . $lineWidth . 'px ' . $lineStyle . ' ' . $lineColor . ';' : 'width:100%;height:0;border-top:' . $lineWidth . 'px ' . $lineStyle . ' ' . $lineColor . ';';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-divider" style="' . esc_attr($style . $spacingStyle) . '"><span class="h18-clean-front-divider-line" style="' . esc_attr($lineCss) . '"></span></div>';
        }

        if ($type === 'icon') {
            $align = in_array((string) ($props['align'] ?? 'center'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'center';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $size = max(8, min(240, (int) ($props['iconSize'] ?? 32)));
            $color = sanitize_hex_color((string) ($props['iconColor'] ?? '#30382a')) ?: '#30382a';
            $background = !empty($props['backgroundTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff');
            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
            $markStyle = 'width:' . $size . 'px;height:' . $size . 'px;color:' . $color . ';background:' . $background . ';padding:' . $padding . 'px;' . $radiusStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-icon" style="' . esc_attr($style . $borderStyle . $spacingStyle . 'justify-content:' . $justify . ';') . '"><span class="h18-clean-front-icon-mark" style="' . esc_attr($markStyle) . '">' . self::iconSvg((string) ($props['icon'] ?? 'star')) . '</span></div>';
        }

        if ($type === 'badge') {
            $align = in_array((string) ($props['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'left';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $background = sanitize_hex_color((string) ($props['background'] ?? '#c3ae83')) ?: '#c3ae83';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 13)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 700)));
            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 12)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 5)));
            $markStyle = 'background:' . $background . ';color:' . $textColor . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';padding:' . $paddingY . 'px ' . $paddingX . 'px;' . $radiusStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-badge" style="' . esc_attr($style . $borderStyle . $spacingStyle . 'justify-content:' . $justify . ';') . '"><span class="h18-clean-front-badge-mark" style="' . esc_attr($markStyle) . '">' . esc_html((string) ($props['text'] ?? 'Badge')) . '</span></div>';
        }

        if ($type === 'link') {
            $linkType = in_array((string) ($props['linkType'] ?? 'url'), ['page', 'url', 'anchor', 'email', 'phone'], true) ? (string) $props['linkType'] : 'url';
            $href = '';
            if ($linkType === 'page') { $pageId = absint($props['pageId'] ?? 0); $permalink = $pageId > 0 ? get_permalink($pageId) : false; $href = is_string($permalink) ? $permalink : ''; }
            elseif ($linkType === 'anchor') { $anchor = trim((string) ($props['url'] ?? '')); $href = preg_match('/^#[A-Za-z][A-Za-z0-9_\-:.]*$/', $anchor) ? $anchor : ''; }
            elseif ($linkType === 'email') { $mail = sanitize_email((string) ($props['url'] ?? '')); $href = $mail !== '' ? 'mailto:' . $mail : ''; }
            elseif ($linkType === 'phone') { $phone = preg_replace('/[^0-9+() .\-]/', '', (string) ($props['url'] ?? '')); $href = is_string($phone) && trim($phone) !== '' ? 'tel:' . preg_replace('/[() .\-]/', '', $phone) : ''; }
            else { $href = esc_url_raw((string) ($props['url'] ?? '')); }
            if ($href === '') { $href = '#'; }
            $align = in_array((string) ($props['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'left';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#2271b1')) ?: '#2271b1';
            $hoverColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#135e96')) ?: '#135e96';
            $fontSize = max(8, min(120, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 600)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.3)));
            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));
            $linkStyle = '--h18-link-color:' . $textColor . ';--h18-link-hover:' . $hoverColor . ';--h18-link-decoration:' . (!empty($props['underline']) ? 'underline' : 'none') . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;justify-content:' . $justify . ';';
            $target = !empty($props['targetBlank']) ? ' target="_blank" rel="noopener"' : '';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-link" style="' . esc_attr($style . $borderStyle . $spacingStyle . $linkStyle) . '"><a href="' . esc_url($href) . '"' . $target . '>' . esc_html((string) ($props['text'] ?? 'Læs mere →')) . '</a></div>';
        }

        if ($type === 'datalist') {
            $rows = is_array($props['rows'] ?? null) ? $props['rows'] : [];
            $stacked = (string) ($props['layout'] ?? 'rows') === 'stacked';
            $labelWidth = max(15, min(80, (int) ($props['labelWidth'] ?? 40)));
            $padding = max(0, min(60, (int) ($props['cellPadding'] ?? 8)));
            $background = sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff';
            $zebraBg = sanitize_hex_color((string) ($props['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7';
            $lineColor = sanitize_hex_color((string) ($props['lineColor'] ?? '#dcdcde')) ?: '#dcdcde';
            $labelColor = sanitize_hex_color((string) ($props['labelColor'] ?? '#30382a')) ?: '#30382a';
            $valueColor = sanitize_hex_color((string) ($props['valueColor'] ?? '#30382a')) ?: '#30382a';
            $labelWeight = max(100, min(900, (int) ($props['labelWeight'] ?? 600)));
            $valueWeight = max(100, min(900, (int) ($props['valueWeight'] ?? 400)));
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 15)));
            $listHtml = '';
            foreach ($rows as $index => $row) {
                if (!is_array($row)) { continue; }
                $rowBg = !empty($props['zebra']) && ((int) $index % 2 === 1) ? $zebraBg : $background;
                $divider = !empty($props['showDividers']) && (int) $index > 0 ? 'border-top:1px solid ' . $lineColor . ';' : '';
                $listHtml .= '<div class="h18-clean-front-datalist-row" style="background:' . esc_attr($rowBg) . ';' . esc_attr($divider) . '"><span style="padding:' . esc_attr((string) $padding) . 'px;color:' . esc_attr($labelColor) . ';font-weight:' . esc_attr((string) $labelWeight) . '">' . esc_html((string) ($row['label'] ?? '')) . '</span><span style="padding:' . esc_attr((string) $padding) . 'px;color:' . esc_attr($valueColor) . ';font-weight:' . esc_attr((string) $valueWeight) . '">' . esc_html((string) ($row['value'] ?? '')) . '</span></div>';
            }
            $listStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . '--h18-data-label-width:' . $labelWidth . '%;font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;overflow:hidden;';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-datalist' . ($stacked ? ' is-stacked' : '') . '" style="' . esc_attr($listStyle) . '">' . $listHtml . '</div>';
        }

        if ($type === 'table') {
            $headers = is_array($props['headers'] ?? null) ? array_values($props['headers']) : [];
            $rows = is_array($props['rows'] ?? null) ? array_values($props['rows']) : [];
            $headerBg = sanitize_hex_color((string) ($props['headerBackground'] ?? '#30382a')) ?: '#30382a';
            $headerColor = sanitize_hex_color((string) ($props['headerTextColor'] ?? '#ffffff')) ?: '#ffffff';
            $cellBg = sanitize_hex_color((string) ($props['cellBackground'] ?? '#ffffff')) ?: '#ffffff';
            $cellColor = sanitize_hex_color((string) ($props['cellTextColor'] ?? '#30382a')) ?: '#30382a';
            $zebraBg = sanitize_hex_color((string) ($props['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7';
            $cellBorderColor = sanitize_hex_color((string) ($props['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde';
            $cellBorderWidth = max(0, min(10, (int) ($props['cellBorderWidth'] ?? 1)));
            $cellPadding = max(0, min(60, (int) ($props['cellPadding'] ?? 8)));
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 14)));
            $headerWeight = max(100, min(900, (int) ($props['headerWeight'] ?? 700)));
            $cellBorder = $cellBorderWidth . 'px solid ' . $cellBorderColor;
            $thead = '<thead><tr>';
            foreach ($headers as $header) { $thead .= '<th style="background:' . esc_attr($headerBg) . ';color:' . esc_attr($headerColor) . ';font-weight:' . esc_attr((string) $headerWeight) . ';padding:' . esc_attr((string) $cellPadding) . 'px;border:' . esc_attr($cellBorder) . '">' . esc_html((string) $header) . '</th>'; }
            $thead .= '</tr></thead>';
            $tbody = '<tbody>';
            foreach ($rows as $rowIndex => $row) {
                if (!is_array($row)) { continue; }
                $rowBg = !empty($props['zebra']) && ((int) $rowIndex % 2 === 1) ? $zebraBg : $cellBg;
                $tbody .= '<tr>';
                foreach ($headers as $columnIndex => $header) { $tbody .= '<td data-label="' . esc_attr((string) $header) . '" style="background:' . esc_attr($rowBg) . ';color:' . esc_attr($cellColor) . ';padding:' . esc_attr((string) $cellPadding) . 'px;border:' . esc_attr($cellBorder) . '">' . esc_html((string) ($row[$columnIndex] ?? '')) . '</td>'; }
                $tbody .= '</tr>';
            }
            $tbody .= '</tbody>';
            $mobileMode = (string) ($props['mobileMode'] ?? 'scroll') === 'cards' ? 'cards' : 'scroll';
            $outerStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . '--h18-table-border:' . $cellBorderColor . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;overflow:hidden;';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($outerStyle) . '"><div class="h18-clean-front-table-wrap" data-mobile-mode="' . esc_attr($mobileMode) . '"><table class="h18-clean-front-table">' . $thead . $tbody . '</table></div></div>';
        }

        if ($type === 'image') {
            $url = esc_url((string) ($props['url'] ?? ''));
            if ($url === '' && !empty($props['mediaId'])) {
                $url = esc_url((string) wp_get_attachment_image_url((int) $props['mediaId'], 'full'));
            }
            $fit = (string) ($props['fit'] ?? 'contain');
            if (!in_array($fit, ['cover', 'contain', 'original', 'stretch', 'manual'], true)) {
                $fit = 'contain';
            }
            $alignX = in_array((string) ($props['imageAlignX'] ?? 'center'), ['left', 'center', 'right'], true) ? (string) $props['imageAlignX'] : 'center';
            $alignY = in_array((string) ($props['imageAlignY'] ?? 'center'), ['top', 'center', 'bottom'], true) ? (string) $props['imageAlignY'] : 'center';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$alignX];
            $alignItems = ['top' => 'flex-start', 'center' => 'center', 'bottom' => 'flex-end'][$alignY];
            $posX = ['left' => '0%', 'center' => '50%', 'right' => '100%'][$alignX];
            $posY = ['top' => '0%', 'center' => '50%', 'bottom' => '100%'][$alignY];
            $background = !empty($props['boxTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['boxBackground'] ?? '#ffffff')) ?: '#ffffff');
            $figureStyle = 'height:100%;background:' . $background . ';border-radius:inherit;overflow:hidden;';

            if ($fit === 'manual') {
                $manualX = max(-4000, min(4000, (int) ($props['manualX'] ?? 0)));
                $manualY = max(-4000, min(4000, (int) ($props['manualY'] ?? 0)));
                $manualW = max(1, min(4000, (int) ($props['manualW'] ?? 320)));
                $manualH = max(1, min(4000, (int) ($props['manualH'] ?? 240)));
                $figureStyle .= 'position:relative;display:block;';
                $imageStyle = 'position:absolute;left:' . $manualX . 'px;top:' . $manualY . 'px;width:' . $manualW . 'px;height:' . $manualH . 'px;max-width:none;max-height:none;object-fit:fill;object-position:50% 50%;';
            } else {
                $figureStyle .= 'display:flex;justify-content:' . $justify . ';align-items:' . $alignItems . ';';
                if ($fit === 'original') {
                    $imageStyle = 'display:block;width:auto;height:auto;max-width:100%;max-height:100%;object-fit:contain;object-position:' . $posX . ' ' . $posY . ';';
                } else {
                    $fitCss = $fit === 'stretch' ? 'fill' : $fit;
                    $objectPosition = $fit === 'cover'
                        ? ((int) ($props['focalX'] ?? 50) . '% ' . (int) ($props['focalY'] ?? 50) . '%')
                        : ($posX . ' ' . $posY);
                    $imageStyle = 'display:block;width:100%;height:100%;max-width:none;max-height:none;object-fit:' . $fitCss . ';object-position:' . $objectPosition . ';';
                }
            }

            $outerStyle = $style . $borderStyle . $spacingStyle . $radiusStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($outerStyle) . '"><figure class="h18-clean-front-image" style="' . esc_attr($figureStyle) . '">' . ($url !== '' ? '<img src="' . $url . '" alt="' . esc_attr((string) ($props['alt'] ?? '')) . '" style="' . esc_attr($imageStyle) . '">' : '') . '</figure></div>';
        }

        $background = sanitize_hex_color((string) ($props['background'] ?? '')) ?: 'transparent';
        $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
        $classes = $type === 'section' ? 'h18-clean-front-section' : 'h18-clean-front-container';
        $requiredHeight = self::requiredChildHeightPx((string) $node['id'], $byParent);
        $selectedHeight = $h * LayoutModel::ROW_PX;
        $minimumHeight = max($selectedHeight, $requiredHeight);
        if ($minimumHeight > 0) {
            $style .= 'min-height:' . $minimumHeight . 'px;';
        }
        $boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $padding . 'px;';
        return '<section id="h18-clean-' . $id . '" class="h18-clean-front-node ' . esc_attr($classes) . '" style="' . esc_attr($boxStyle) . '">' . self::children((string) $node['id'], $byParent, $byId) . '</section>';
    }

    private static function iconSvg(string $token): string
    {
        $shapes = [
            'star' => '<polygon points="12 2.7 14.8 8.4 21 9.3 16.5 13.7 17.6 20 12 17 6.4 20 7.5 13.7 3 9.3 9.2 8.4 12 2.7"/>',
            'check' => '<polyline points="4 12.5 9.5 18 20 6"/>',
            'info' => '<circle cx="12" cy="12" r="9"/><line x1="12" y1="10.5" x2="12" y2="17"/><line x1="12" y1="7" x2="12.01" y2="7"/>',
            'calendar' => '<rect x="3" y="5" width="18" height="16" rx="2"/><line x1="7" y1="3" x2="7" y2="7"/><line x1="17" y1="3" x2="17" y2="7"/><line x1="3" y1="10" x2="21" y2="10"/>',
            'camera' => '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.5-3h5L16 7"/><circle cx="12" cy="13.5" r="3.5"/>',
            'people' => '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-4 3-6 6-6s5.2 2 6 6"/><path d="M14 15c3.5-.5 6 1.1 7 4"/>',
            'ruler' => '<path d="M4 17L17 4l3 3L7 20z"/><line x1="13" y1="8" x2="16" y2="11"/><line x1="10" y1="11" x2="12" y2="13"/><line x1="7" y1="14" x2="10" y2="17"/>',
            'weight' => '<path d="M6 8h12l2 12H4z"/><path d="M9 8a3 3 0 016 0"/><line x1="12" y1="11" x2="14" y2="14"/>',
            'gear' => '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
            'link' => '<path d="M10 13a5 5 0 007 0l2-2a5 5 0 00-7-7l-1 1"/><path d="M14 11a5 5 0 00-7 0l-2 2a5 5 0 007 7l1-1"/>',
        ];
        $token = sanitize_key($token);
        $shape = $shapes[$token] ?? $shapes['star'];
        return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' . $shape . '</svg>';
    }

    private static function fontCss(string $token): string
    {
        return [
            'arial' => 'Arial,sans-serif',
            'verdana' => 'Verdana,sans-serif',
            'tahoma' => 'Tahoma,sans-serif',
            'trebuchet' => '"Trebuchet MS",sans-serif',
            'georgia' => 'Georgia,serif',
            'times' => '"Times New Roman",serif',
            'courier' => '"Courier New",monospace',
            'system' => 'system-ui,-apple-system,"Segoe UI",sans-serif',
        ][$token] ?? 'system-ui,-apple-system,"Segoe UI",sans-serif';
    }

    /** @param array<string,mixed> $props */
    private static function borderStyle(array $props): string
    {
        $width = max(0, min(20, (int) ($props['borderWidth'] ?? 0)));
        if ($width === 0) {
            return 'border:0 solid transparent;';
        }
        $color = sanitize_hex_color((string) ($props['borderColor'] ?? '#000000')) ?: '#000000';
        return 'border:' . $width . 'px solid ' . $color . ';';
    }

    /** @param array<string,mixed> $props */
    private static function spacingStyle(array $props): string
    {
        $gapX = max(0, min(200, (int) ($props['gapX'] ?? 0)));
        $gapY = max(0, min(200, (int) ($props['gapY'] ?? 0)));
        return 'margin-right:' . $gapX . 'px;margin-bottom:' . $gapY . 'px;';
    }

    /** @param array<string,array<int,array<string,mixed>>> $byParent */
    private static function requiredChildHeightPx(string $parentId, array $byParent): int
    {
        $required = 0;
        foreach ($byParent[$parentId] ?? [] as $child) {
            $g = isset($child['geometry']['desktop']) && is_array($child['geometry']['desktop']) ? $child['geometry']['desktop'] : [];
            $y = max(0, (int) ($g['y'] ?? 0));
            $h = max(0, (int) ($g['h'] ?? 0));
            $type = (string) ($child['type'] ?? '');
            if ($h > 0) {
                $childHeight = $h * LayoutModel::ROW_PX;
            } elseif ($type === 'image') {
                $childHeight = 10 * LayoutModel::ROW_PX;
            } elseif ($type === 'text') {
                $childHeight = 10 * LayoutModel::ROW_PX;
            } else {
                $childHeight = 8 * LayoutModel::ROW_PX;
            }
            if (in_array($type, ['section', 'container'], true)) {
                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent));
            }
            $required = max($required, ($y * LayoutModel::ROW_PX) + $childHeight);
        }
        return $required;
    }
}
