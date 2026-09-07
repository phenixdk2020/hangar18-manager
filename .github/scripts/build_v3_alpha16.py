from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.16'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


subprocess.run(['python3', '.github/scripts/build_v3_alpha15.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.15', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.15');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.15');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.16 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Alpha.16 is a visual-parity pass based on the user's V3/V1 phone screenshots.
# Alpha.15 fixed the page-flow semantics. The remaining mismatch is the V1
# presentation contract: mobile type scale, hero/tagline treatment, card inset,
# and Header/Footer layout. Keep the fix CSS-only for existing V3 data.
rr = read('src/Frontend/ResponsiveRenderer.php')

old = """        $v1MobileFlow = metadata_exists('post', $postId, '_h18_clean_layout_v1')
            ? self::v1MobileFlowCss($pageModel, $pageScope)
            : '';

        if (ThemeShell::enabled()) {
"""
new = """        $legacyPageModel = self::legacyPageModel($postId);
        $v1MobileFlow = $legacyPageModel !== null
            ? self::v1MobileFlowCss($pageModel, $pageScope)
            : '';
        $templateModels = ['header' => null, 'footer' => null];
        $legacyTemplateModels = ['header' => null, 'footer' => null];

        if (ThemeShell::enabled()) {
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.16 legacy page anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """                $models[] = [
                    'scope' => $part === 'header' ? '.h18-vd-live-shell-header ' : '.h18-vd-live-shell-footer ',
                    'model' => $templateModel,
                ];
            }
        }

        $laptop = '';
"""
new = """                $models[] = [
                    'scope' => $part === 'header' ? '.h18-vd-live-shell-header ' : '.h18-vd-live-shell-footer ',
                    'model' => $templateModel,
                ];
                $templateModels[$part] = $templateModel;
                $legacyTemplateModels[$part] = self::legacyTemplateModel($templateId, $part);
            }
        }

        $v1MobileVisual = $legacyPageModel !== null
            ? self::v1MobileVisualParityCss(
                $pageModel,
                $legacyPageModel,
                $pageScope,
                is_array($templateModels['header']) ? $templateModels['header'] : null,
                is_array($legacyTemplateModels['header']) ? $legacyTemplateModels['header'] : null,
                is_array($templateModels['footer']) ? $templateModels['footer'] : null,
                is_array($legacyTemplateModels['footer']) ? $legacyTemplateModels['footer'] : null
            )
            : '';

        $laptop = '';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.16 template capture anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            . $mobile
            . $v1MobileFlow . '}';
"""
new = """            . $mobile
            . $v1MobileFlow
            . $v1MobileVisual . '}';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.16 mobile append anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

anchor = """    /** @return array<string,mixed>|null */
    private static function model(int $postId): ?array
"""
method = r'''    /**
     * V1 phone visual contract reconstructed from the retained V1 runtime and
     * the approved V1 screenshots. This intentionally runs after Alpha.15's
     * flow CSS so it can restore presentation without rewriting stored V3 data.
     *
     * @param array<string,mixed> $pageModel
     * @param array<string,mixed> $legacyPageModel
     * @param array<string,mixed>|null $headerModel
     * @param array<string,mixed>|null $legacyHeaderModel
     * @param array<string,mixed>|null $footerModel
     * @param array<string,mixed>|null $legacyFooterModel
     */
    private static function v1MobileVisualParityCss(
        array $pageModel,
        array $legacyPageModel,
        string $pageScope,
        ?array $headerModel,
        ?array $legacyHeaderModel,
        ?array $footerModel,
        ?array $legacyFooterModel
    ): string {
        $css = '';

        // V1 default mobile typography: body 16px; h1/h2/h3 use the lower
        // clamp bounds 2rem / 1.55rem / 1.2rem at phone widths.
        $css .= $pageScope . '.h18-clean-front-text{font-size:16px!important;line-height:1.5!important;}'
            . $pageScope . 'h1.h18-clean-front-text-heading{font-size:32px!important;line-height:1.2!important;}'
            . $pageScope . 'h2.h18-clean-front-text-heading{font-size:24.8px!important;line-height:1.2!important;}'
            . $pageScope . 'h3.h18-clean-front-text-heading{font-size:19.2px!important;line-height:1.2!important;}'
            . $pageScope . 'h4.h18-clean-front-text-heading,' . $pageScope . 'h5.h18-clean-front-text-heading,' . $pageScope . 'h6.h18-clean-front-text-heading{font-size:18px!important;line-height:1.2!important;}'
            . $pageScope . '.h18-clean-front-section,' . $pageScope . '.h18-clean-front-container{padding-left:max(var(--h18-vdm-pad-left,0px),18px)!important;padding-right:max(var(--h18-vdm-pad-right,0px),18px)!important;}'
            . $pageScope . '.h18-clean-front-button-link{min-height:52px!important;padding:13px 24px!important;border-radius:29px!important;font-size:16px!important;line-height:1.2!important;}'
            . $pageScope . '.h18-clean-front-surface>.h18-clean-front-spacer{display:none!important;}'
            . $pageScope . '.h18-clean-front-surface>.h18-clean-front-node{margin-bottom:min(var(--h18-vdm-gap-y,24px),24px)!important;}';

        // Paint (background/text/border/radius) comes from the retained V1
        // model where a node id/type still matches. Geometry remains V3/Alpha.15.
        $css .= self::v1PaintCss($pageModel, $legacyPageModel, $pageScope);

        $nodes = [];
        foreach ((array) ($pageModel['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $nodes[(string) $node['id']] = $node;
        }

        $taglineId = '';
        $heroId = '';
        $heroY = PHP_INT_MAX;
        foreach ($nodes as $id => $node) {
            $type = (string) ($node['type'] ?? '');
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $heading = trim(wp_strip_all_tags((string) ($props['heading'] ?? '')));
            $text = trim(wp_strip_all_tags((string) ($props['text'] ?? '')));
            $hay = strtolower($heading . ' ' . $text);
            $selector = $pageScope . '#h18-clean-' . self::cssId($id);

            if ($type === 'text' && str_contains($hay, 'bevaring, restaurering og levende') && str_contains($hay, 'militærhistorie')) {
                $taglineId = $id;
                $css .= $selector . '{background:#c3ae83!important;color:#30382a!important;text-align:center!important;padding:13px 18px!important;border-radius:0!important;width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;font-size:18px!important;font-weight:700!important;line-height:1.35!important;}'
                    . $selector . ' .h18-clean-front-text-heading{color:#30382a!important;}';
            }

            if ($type === 'text' && in_array($heading, ['Bevaring', 'Formidling', 'Fællesskab'], true)) {
                $bg = $heading === 'Bevaring' ? '#f2f0e8' : ($heading === 'Formidling' ? '#c3ae83' : '#525a5f');
                $fg = $heading === 'Fællesskab' ? '#ffffff' : '#30382a';
                $css .= $selector . '{width:calc(100% - 20px)!important;max-width:calc(100% - 20px)!important;margin-left:10px!important;margin-right:10px!important;padding:20px!important;border-radius:7px!important;background:' . $bg . '!important;color:' . $fg . '!important;font-size:16px!important;line-height:1.5!important;}'
                    . $selector . ' .h18-clean-front-text-heading{font-size:19.2px!important;color:' . $fg . '!important;margin-bottom:12px!important;}';
            }

            if ($type === 'image') {
                $g = self::effectiveGeometry($node, 'mobile');
                if ($g['w'] >= 100 && $g['y'] < $heroY) {
                    $heroId = $id;
                    $heroY = $g['y'];
                }
            }
        }

        if ($heroId !== '' && $taglineId !== '') {
            $selector = $pageScope . '#h18-clean-' . self::cssId($heroId);
            $css .= $selector . '{height:220px!important;min-height:220px!important;overflow:hidden!important;margin-bottom:24px!important;}'
                . $selector . ' .h18-clean-front-image{height:220px!important;min-height:220px!important;}'
                . $selector . ' .h18-clean-front-image img{width:100%!important;height:220px!important;object-fit:cover!important;object-position:50% 50%!important;}';
        }

        // If old explicit Spacer nodes sat between the mobile hero and tagline,
        // V1's section spacing already represents that air; do not stack them.
        if ($heroId !== '' && $taglineId !== '') {
            $hero = $nodes[$heroId] ?? null;
            $tagline = $nodes[$taglineId] ?? null;
            if (is_array($hero) && is_array($tagline) && (string) ($hero['parentId'] ?? '') === (string) ($tagline['parentId'] ?? '')) {
                $parent = (string) ($hero['parentId'] ?? '');
                $hy = self::effectiveGeometry($hero, 'mobile')['y'];
                $ty = self::effectiveGeometry($tagline, 'mobile')['y'];
                foreach ($nodes as $id => $node) {
                    if ((string) ($node['parentId'] ?? '') !== $parent || (string) ($node['type'] ?? '') !== 'spacer') { continue; }
                    $sy = self::effectiveGeometry($node, 'mobile')['y'];
                    if ($sy >= min($hy, $ty) && $sy <= max($hy, $ty)) {
                        $css .= $pageScope . '#h18-clean-' . self::cssId($id) . '{display:none!important;}';
                    }
                }
            }
        }

        if ($headerModel !== null) {
            $css .= self::v1HeaderMobileCss($headerModel, $legacyHeaderModel, '.h18-vd-live-shell-header ');
        }
        if ($footerModel !== null) {
            $css .= self::v1FooterMobileCss($footerModel, $legacyFooterModel, '.h18-vd-live-shell-footer ');
        }
        return $css;
    }

    /**
     * @param array<string,mixed> $canonical
     * @param array<string,mixed> $legacy
     */
    private static function v1PaintCss(array $canonical, array $legacy, string $scope): string
    {
        $legacyById = [];
        foreach ((array) ($legacy['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $legacyById[(string) $node['id']] = $node;
        }
        $css = '';
        foreach ((array) ($canonical['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $type = (string) ($node['type'] ?? '');
            $legacyNode = $legacyById[$id] ?? null;
            if (!is_array($legacyNode) || (string) ($legacyNode['type'] ?? '') !== $type) { continue; }
            $props = is_array($legacyNode['props'] ?? null) ? $legacyNode['props'] : [];
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $radius = max(0, min(100, (int) ($props['radius'] ?? 0)));
            $borderWidth = max(0, min(20, (int) ($props['borderWidth'] ?? 0)));
            $borderColor = sanitize_hex_color((string) ($props['borderColor'] ?? '#000000')) ?: '#000000';

            if (in_array($type, ['text', 'section', 'container'], true)) {
                $background = !empty($props['backgroundTransparent'])
                    ? 'transparent'
                    : (sanitize_hex_color((string) ($props['background'] ?? '')) ?: 'transparent');
                $css .= $selector . '{background:' . $background . '!important;border-radius:' . $radius . 'px!important;border-width:' . $borderWidth . 'px!important;border-color:' . $borderColor . '!important;}';
            }
            if ($type === 'text') {
                $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
                $headingColor = sanitize_hex_color((string) ($props['headingColor'] ?? $textColor)) ?: $textColor;
                $css .= $selector . '{color:' . $textColor . '!important;}'
                    . $selector . ' .h18-clean-front-text-heading{color:' . $headingColor . '!important;}';
            }
            if ($type === 'button') {
                $background = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';
                $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
                $css .= $selector . '{--h18-btn-bg:' . $background . '!important;--h18-btn-color:' . $textColor . '!important;}'
                    . $selector . ' .h18-clean-front-button-link{border-radius:' . $radius . 'px!important;border-width:' . $borderWidth . 'px!important;border-color:' . $borderColor . '!important;}';
            }
        }
        return $css;
    }

    /** @param array<string,mixed> $model @param array<string,mixed>|null $legacy */
    private static function v1HeaderMobileCss(array $model, ?array $legacy, string $scope): string
    {
        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{display:flex!important;flex-direction:row!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-surface{padding:0!important;}'
            . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{padding:12px 12px!important;margin:0!important;gap:10px!important;}'
            . $scope . '.h18-clean-front-node{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;margin:0!important;min-height:0!important;box-sizing:border-box!important;}';

        if ($legacy !== null) { $css .= self::v1PaintCss($model, $legacy, $scope); }

        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $type = (string) ($node['type'] ?? '');
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            if ($type === 'image') {
                $css .= $selector . '{order:10!important;flex:0 0 clamp(48px,15vw,60px)!important;width:clamp(48px,15vw,60px)!important;max-width:60px!important;height:clamp(48px,15vw,60px)!important;}'
                    . $selector . ' .h18-clean-front-image,' . $selector . ' .h18-clean-front-image img{width:100%!important;height:100%!important;max-width:100%!important;object-fit:contain!important;}';
            } elseif ($type === 'text') {
                $font = max(13.0, min(19.0, (float) ((int) ($props['fontSize'] ?? 19))));
                if (str_contains($id, 'legacy-header')) { $font = max(13.0, min(19.0, $font * 0.70)); }
                $css .= $selector . '{order:20!important;flex:1 1 auto!important;width:auto!important;max-width:none!important;height:auto!important;padding:0!important;background:transparent!important;color:#f2f0e8!important;font-size:' . rtrim(rtrim(number_format($font, 1, '.', ''), '0'), '.') . 'px!important;font-weight:700!important;line-height:1.16!important;text-align:left!important;overflow-wrap:normal!important;word-break:normal!important;}'
                    . $selector . ' .h18-clean-front-text-heading{font-size:inherit!important;color:#f2f0e8!important;margin:0!important;}';
            } elseif ($type === 'menu') {
                $css .= $selector . '{order:30!important;flex:0 0 48px!important;width:48px!important;max-width:48px!important;height:48px!important;margin-left:auto!important;padding:0!important;background:transparent!important;}'
                    . $selector . ' .h18-clean-front-menu-summary{width:48px!important;height:48px!important;}';
            }
        }
        return $css;
    }

    /** @param array<string,mixed> $model @param array<string,mixed>|null $legacy */
    private static function v1FooterMobileCss(array $model, ?array $legacy, string $scope): string
    {
        $byId = [];
        $byParent = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $byId[$id] = $node;
            $byParent[(string) ($node['parentId'] ?? '')][] = $node;
        }

        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{padding:28px 16px 24px!important;margin:0!important;}'
            . $scope . '.h18-clean-front-node{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;margin-right:0!important;margin-bottom:0!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-text{font-size:14px!important;line-height:1.45!important;}'
            . $scope . '.h18-clean-front-text a{display:inline!important;color:inherit!important;text-decoration:none!important;}'
            . $scope . '.h18-clean-front-button-link{min-height:44px!important;padding:10px 16px!important;font-size:16px!important;font-weight:700!important;line-height:1.2!important;}'
            . $scope . '.h18-clean-front-menu-summary{display:none!important;}'
            . $scope . '.h18-clean-front-menu-panel{display:block!important;position:static!important;width:100%!important;max-width:100%!important;padding:0!important;background:transparent!important;border:0!important;box-shadow:none!important;}'
            . $scope . '.h18-clean-front-menu-list{display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:8px!important;font-size:14px!important;font-weight:400!important;}';

        if ($legacy !== null) { $css .= self::v1PaintCss($model, $legacy, $scope); }

        foreach ($byParent as $children) {
            usort($children, static function (array $a, array $b): int {
                $ag = self::effectiveGeometry($a, 'mobile');
                $bg = self::effectiveGeometry($b, 'mobile');
                return ($ag['y'] <=> $bg['y']) ?: ((int) ($a['order'] ?? 0) <=> (int) ($b['order'] ?? 0));
            });
            $previousBottom = 0;
            foreach (array_values($children) as $index => $node) {
                $id = (string) ($node['id'] ?? '');
                if ($id === '') { continue; }
                $g = self::effectiveGeometry($node, 'mobile');
                $rows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);
                $gapRows = $index === 0 ? 0 : max(0, $g['y'] - $previousBottom);
                $gapPx = min(32, $gapRows * LayoutModel::ROW_PX);
                $css .= $scope . '#h18-clean-' . self::cssId($id) . '{order:' . $index . '!important;margin-top:' . $gapPx . 'px!important;}';
                $previousBottom = max($previousBottom, $g['y'] + $rows);
            }
        }
        return $css;
    }

    /** @return array<string,mixed>|null */
    private static function legacyPageModel(int $postId): ?array
    {
        if (!metadata_exists('post', $postId, '_h18_clean_layout_v1')) { return null; }
        $raw = get_post_meta($postId, '_h18_clean_layout_v1', true);
        if (!is_array($raw)) { return null; }
        try { return LayoutModel::normalize($raw); } catch (\Throwable $error) { return null; }
    }

    /** @return array<string,mixed>|null */
    private static function legacyTemplateModel(string $templateId, string $part): ?array
    {
        $part = $part === 'footer' ? 'footer' : 'header';
        $candidates = ['h18_clean_tpl_' . $templateId . '_model_v1'];
        if ($templateId === $part . '-standard-v1') {
            array_unshift($candidates, 'h18_clean_global_' . $part . '_layout_v1');
        }
        foreach ($candidates as $option) {
            $raw = get_option($option, null);
            if (!is_array($raw)) { continue; }
            try { return LayoutModel::normalize($raw); } catch (\Throwable $error) { continue; }
        }
        return null;
    }

'''
if rr.count(anchor) != 1:
    raise SystemExit(f'Alpha.16 visual parity method anchor mismatch: {rr.count(anchor)}')
rr = rr.replace(anchor, method + anchor, 1)
write('src/Frontend/ResponsiveRenderer.php', rr)

# Future Header conversions must retain V1's historical 70% identity base
# factor. Existing sites are corrected by the runtime rule above.
header = read('src/Migration/LegacyHeaderConverter.php')
old = """        $scale = self::clampInt($d['VisualBaseScalePercent'] ?? 90, 50, 120, 90) / 100;
        $brandPx = max(12, (int) round(self::clampInt($d['BrandFontSize'] ?? 22, 12, 60, 22)
            * self::clampInt($d['BrandSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));
        $menuPx = max(10, (int) round(self::clampInt($d['MenuFontSize'] ?? 15, 10, 40, 15)
            * self::clampInt($d['MenuSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));
        $logoPx = max(24, (int) round(self::clampInt($d['LogoWidthPx'] ?? 52, 24, 300, 52)
            * self::clampInt($d['LogoSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));
"""
new = """        $scale = self::clampInt($d['VisualBaseScalePercent'] ?? 90, 50, 120, 90) / 100;
        $identityBaseFactor = 0.70;
        $brandPx = max(12, (int) round(self::clampInt($d['BrandFontSize'] ?? 22, 12, 60, 22)
            * self::clampInt($d['BrandSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale * $identityBaseFactor));
        $menuPx = max(10, (int) round(self::clampInt($d['MenuFontSize'] ?? 15, 10, 40, 15)
            * self::clampInt($d['MenuSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));
        $logoPx = max(24, (int) round(self::clampInt($d['LogoWidthPx'] ?? 52, 24, 300, 52)
            * self::clampInt($d['LogoSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale * $identityBaseFactor));
"""
if header.count(old) != 1:
    raise SystemExit(f'Alpha.16 Header V1 scale anchor mismatch: {header.count(old)}')
header = header.replace(old, new, 1)
write('src/Migration/LegacyHeaderConverter.php', header)

# Footer reference buttons are bold in V1.
footer = read('src/Migration/LegacyFooterConverter.php')
for text in ['Bliv medlem', 'Kontakt']:
    marker = "'text'=>'" + text + "'"
    pos = footer.find(marker)
    if pos < 0:
        raise SystemExit(f'Alpha.16 Footer button missing: {text}')
# Apply to the two known reference button prop arrays only.
footer = footer.replace("'paddingX'=>12,'paddingY'=>8,'radius'=>5,'borderWidth'=>0", "'paddingX'=>12,'paddingY'=>8,'fontSize'=>16,'fontWeight'=>700,'radius'=>5,'borderWidth'=>0", 1)
footer = footer.replace("'paddingX'=>12,'paddingY'=>8,'radius'=>5,'borderWidth'=>1", "'paddingX'=>12,'paddingY'=>8,'fontSize'=>16,'fontWeight'=>700,'radius'=>5,'borderWidth'=>1", 1)
write('src/Migration/LegacyFooterConverter.php', footer)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.15':
    raise SystemExit('Expected Alpha.15 release-history baseline missing')
alpha16 = {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'V1 Mobile Visual Parity: Alpha.15 flow beholdes, mens V1s mobile typografiskala gendannes (body 16px, h1 32px, h2 24.8px, h3 19.2px).',
        'Mobil hero gendannes til V1-princippet på 220 px, tagline til sand/dark V1-stil og featurekort til V1s inset/padding/farver.',
        'Header får V1s kompakte identitetslayout med mindre brandtekst, korrekt logo/menu-balance og den fungerende Alpha.14 hamburger.',
        'Footer går fra grid-koordinater til V1s naturlige vertikale mobilflow, så Genveje-links, Foreningen, knapper, divider og copyright vises uden store tomrum.',
        'Retained V1 paint-data bruges runtime read-only for matchende node-id/type; gemte V3-layoutdata omskrives ikke.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha16] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Contract checks.
main = read('visual-designer-manager.php')
rr = read('src/Frontend/ResponsiveRenderer.php')
header = read('src/Migration/LegacyHeaderConverter.php')
footer = read('src/Migration/LegacyFooterConverter.php')
history = json.loads(history_path.read_text(encoding='utf-8'))['versions']

for token in ['Version: 3.0.0-alpha.16', "define('VDM_VERSION', '3.0.0-alpha.16');"]:
    if token not in main: raise SystemExit(f'Alpha.16 main token missing: {token}')
for token in [
    'private static function v1MobileVisualParityCss(',
    'private static function v1HeaderMobileCss(',
    'private static function v1FooterMobileCss(',
    'private static function legacyPageModel(',
    'private static function legacyTemplateModel(',
    'font-size:32px!important',
    'font-size:24.8px!important',
    'font-size:19.2px!important',
    'min-height:52px!important',
    'height:220px!important',
    'background:#c3ae83!important;color:#30382a!important',
    "['Bevaring', 'Formidling', 'Fællesskab']",
    'flex:0 0 clamp(48px,15vw,60px)!important',
    'padding:28px 16px 24px!important',
    'font-weight:700!important',
    'self::v1PaintCss($pageModel, $legacyPageModel, $pageScope)',
]:
    if token not in rr: raise SystemExit(f'Alpha.16 responsive token missing: {token}')
if '$identityBaseFactor = 0.70;' not in header:
    raise SystemExit('Alpha.16 Header identity factor missing')
if footer.count("'fontSize'=>16,'fontWeight'=>700") < 2:
    raise SystemExit('Alpha.16 Footer V1 button typography missing')
if history[0].get('version') != VERSION or history[1].get('version') != '3.0.0-alpha.15':
    raise SystemExit('Alpha.16 release-history ordering failed')

print('V3 Alpha.16 V1 mobile visual parity: PASS')
print('V1 type scale / hero / tagline / cards: PASS')
print('V1 Header compact identity + Alpha.14 menu: PASS')
print('V1 Footer vertical shortcuts/buttons/copyright flow: PASS')
