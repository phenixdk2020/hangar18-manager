from pathlib import Path
import json

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# Version bump.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/hangar18-manager.php'
s = read(path)
s = replace_once(s, ' * Version: 0.1.41', ' * Version: 0.1.42', 'plugin header version')
s = replace_once(s, "define('H18_CLEAN_VERSION', '0.1.41');", "define('H18_CLEAN_VERSION', '0.1.42');", 'version constant')
write(path, s)

# ---------------------------------------------------------------------------
# BUG-11: make Header conversion observable and provide a deterministic
# screenshot-reference fallback when the historical options/blocks are gone.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php'
s = read(path)
s = replace_once(
    s,
    "    public const MIGRATION_OPTION = 'h18_vd_legacy_header_converted_v0141';\n",
    "    public const MIGRATION_OPTION = 'h18_vd_legacy_header_converted_v0142';\n    public const STATUS_OPTION = 'h18_vd_legacy_header_status_v0142';\n",
    'migration/status options'
)

start = s.index('    public static function maybeMigrate(): void\n')
end = s.index('    /**\n     * Pure conversion entry used by CI and by the migration itself.', start)
new_migration_block = r'''    public static function maybeMigrate(): void
    {
        if (!current_user_can('edit_theme_options') || get_option(self::MIGRATION_OPTION, false)) {
            return;
        }

        try {
            self::convert(false);
        } catch (\Throwable $error) {
            update_option(self::STATUS_OPTION, [
                'status' => 'error',
                'checkedUtc' => gmdate('c'),
                'message' => $error->getMessage(),
            ], false);
        }
    }

    /**
     * Run or re-run the Header conversion. The operation is non-destructive:
     * the target template is always saved through normal version history.
     *
     * @return array<string,mixed>
     */
    public static function convert(bool $force = true): array
    {
        if (!current_user_can('edit_theme_options')) {
            throw new \RuntimeException('Ingen adgang til Header-konvertering.');
        }
        if (!$force && get_option(self::MIGRATION_OPTION, false)) {
            return self::diagnosticStatus();
        }

        $stored = get_option(self::LEGACY_DESIGN_OPTION, []);
        $stored = is_array($stored) ? $stored : [];
        $shell = self::legacyShellHeader();
        $legacyFound = !empty($stored) || $shell !== '';

        $design = array_merge(self::defaultLegacyDesign(), $stored);
        if ($shell !== '') {
            $design = array_merge($design, self::parseShellHeader($shell));
        }

        $logo = self::resolveLogo($design);
        if ($logo['url'] !== '') {
            $design['ShowLogo'] = true;
            $design['LogoUrl'] = $logo['url'];
            $design['LogoMediaId'] = $logo['mediaId'];
        }

        $menuId = self::legacyMenuId();
        if ($menuId <= 0) {
            throw new \RuntimeException('Ingen WordPress-menu kunne findes til Headeren.');
        }

        if ($legacyFound) {
            $model = self::buildModelFromLegacyDesign($design, $menuId);
            $source = 'legacy';
            $note = 'Automatisk konvertering fra fundet legacy Header · v0.1.42';
        } else {
            $model = self::buildScreenshotReferenceModel($menuId, $logo['mediaId'], $logo['url']);
            $source = 'desktop-reference-2026-08-28';
            $note = 'Header-reference fra godkendt Desktop-screenshot · v0.1.42';
        }

        $counts = self::nodeCounts($model);
        if (($counts['section'] ?? 0) < 1 || ($counts['container'] ?? 0) < 1 || ($counts['menu'] ?? 0) < 1) {
            throw new \RuntimeException('Konverteringen gav ikke en gyldig Sektion/Kasse/Menu-struktur.');
        }
        if (($counts['text'] ?? 0) + ($counts['image'] ?? 0) < 1) {
            throw new \RuntimeException('Konverteringen mangler Header-identitet (Tekst/Billede).');
        }

        TemplateLayoutModel::ensureMigrated();
        $targetId = TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID, 'header')
            ? self::TARGET_TEMPLATE_ID
            : TemplateLayoutModel::defaultId('header');
        if ($targetId === '') {
            $targetId = TemplateLayoutModel::create('header', 'Header – Standard');
        }

        $settings = $legacyFound
            ? self::templateSettings($design)
            : ['sticky' => false, 'overlay' => false, 'contentWidth' => 2400];

        $version = TemplateLayoutModel::saveVersion(
            $targetId,
            $model,
            $settings,
            get_current_user_id(),
            $note
        );
        TemplateLayoutModel::rename($targetId, 'Header – Standard');
        TemplateLayoutModel::setActive($targetId, true);
        TemplateLayoutModel::setDefault('header', $targetId);

        $menu = wp_get_nav_menu_object($menuId);
        $items = $menu ? wp_get_nav_menu_items($menuId) : [];
        $result = [
            'status' => 'success',
            'convertedUtc' => gmdate('c'),
            'templateId' => $targetId,
            'templateVersion' => $version,
            'source' => $source,
            'legacyDesignFound' => !empty($stored),
            'legacyShellFound' => $shell !== '',
            'menuId' => $menuId,
            'menuName' => $menu ? (string) $menu->name : '',
            'menuItems' => is_array($items) ? count($items) : 0,
            'logoSource' => $logo['source'],
            'logoFound' => $logo['url'] !== '',
            'logoMediaId' => $logo['mediaId'],
            'logoUrl' => $logo['url'],
            'nodeCounts' => $counts,
            'digest' => LayoutModel::structuralDigest($model),
        ];
        update_option(self::STATUS_OPTION, $result, false);
        update_option(self::MIGRATION_OPTION, $result, false);
        return $result;
    }

    /** @return array<string,mixed> */
    public static function diagnosticStatus(): array
    {
        $stored = get_option(self::LEGACY_DESIGN_OPTION, []);
        $stored = is_array($stored) ? $stored : [];
        $shell = self::legacyShellHeader();
        $design = array_merge(self::defaultLegacyDesign(), $stored);
        if ($shell !== '') {
            $design = array_merge($design, self::parseShellHeader($shell));
        }
        $logo = self::resolveLogo($design);
        $menuId = self::legacyMenuId();
        $menu = $menuId > 0 ? wp_get_nav_menu_object($menuId) : false;
        $items = $menu ? wp_get_nav_menu_items($menuId) : [];

        TemplateLayoutModel::ensureMigrated();
        $targetId = TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID, 'header')
            ? self::TARGET_TEMPLATE_ID
            : TemplateLayoutModel::defaultId('header');
        $model = $targetId !== '' ? TemplateLayoutModel::model($targetId) : LayoutModel::empty();

        $last = get_option(self::STATUS_OPTION, []);
        $last = is_array($last) ? $last : [];
        return [
            'legacyDesignFound' => !empty($stored),
            'legacyShellFound' => $shell !== '',
            'fallbackAvailable' => true,
            'menuId' => $menuId,
            'menuName' => $menu ? (string) $menu->name : '',
            'menuItems' => is_array($items) ? count($items) : 0,
            'logoSource' => $logo['source'],
            'logoFound' => $logo['url'] !== '',
            'logoUrl' => $logo['url'],
            'targetTemplateId' => $targetId,
            'targetVersion' => $targetId !== '' ? TemplateLayoutModel::version($targetId) : 0,
            'targetNodeCounts' => self::nodeCounts($model),
            'lastConversion' => $last,
        ];
    }

    /**
     * Approved desktop fallback from the 2026-08-28 visual reference:
     * 90% centred Header, dark #30382a bar, logo/brand left, menu right.
     *
     * @return array<string,mixed>
     */
    public static function buildScreenshotReferenceModel(int $menuId, int $logoMediaId = 0, string $logoUrl = ''): array
    {
        $rowsDesktop = 15; // ca. 120 px at the canonical 8 px vertical grid.
        $rowsMobile = 14;
        $brand = 'Aalborg Kaserners Veteran Panser- og Køretøjsforening';
        $nodes = [];

        $nodes[] = self::node(
            'section-header-reference-v0142',
            'section',
            '',
            10,
            self::geometry([6, 0, 108, $rowsDesktop], [6, 0, 108, $rowsDesktop], [0, 0, 120, $rowsMobile]),
            [
                'background' => '#30382a', 'radius' => 0, 'padding' => 0,
                'minHeightRows' => $rowsDesktop, 'borderWidth' => 0,
                'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ]
        );
        $nodes[] = self::node(
            'container-header-reference-v0142',
            'container',
            'section-header-reference-v0142',
            10,
            self::geometry([0, 0, 120, $rowsDesktop], [0, 0, 120, $rowsDesktop], [0, 0, 120, $rowsMobile]),
            [
                'background' => '', 'radius' => 0, 'padding' => 0,
                'minHeightRows' => $rowsDesktop, 'borderWidth' => 0,
                'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ]
        );
        $nodes[] = self::node(
            'image-header-reference-logo-v0142',
            'image',
            'container-header-reference-v0142',
            10,
            self::geometry([0, 1, 7, 13], [0, 1, 7, 13], [0, 1, 20, 12]),
            [
                'mediaId' => max(0, $logoMediaId), 'url' => esc_url_raw($logoUrl),
                'alt' => $brand, 'fit' => 'contain', 'imageAlignX' => 'left',
                'imageAlignY' => 'center', 'boxBackground' => '#30382a',
                'boxTransparent' => true, 'focalX' => 50, 'focalY' => 50,
                'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ]
        );
        $nodes[] = self::node(
            'text-header-reference-brand-v0142',
            'text',
            'container-header-reference-v0142',
            20,
            self::geometry([8, 0, 28, $rowsDesktop], [8, 0, 30, $rowsDesktop], [20, 0, 73, $rowsMobile]),
            [
                'heading' => '', 'headingLevel' => 'h2', 'text' => $brand,
                'align' => 'left', 'background' => '#30382a', 'backgroundTransparent' => true,
                'textColor' => '#f2f0e8', 'headingColor' => '#f2f0e8',
                'padding' => 0, 'radius' => 0, 'fontFamily' => 'system',
                'fontSize' => 19, 'fontWeight' => 700, 'lineHeight' => 1.18,
                'letterSpacing' => 0, 'borderWidth' => 0, 'borderColor' => '#000000',
                'gapX' => 0, 'gapY' => 0,
            ]
        );
        $nodes[] = self::node(
            'menu-header-reference-primary-v0142',
            'menu',
            'container-header-reference-v0142',
            30,
            self::geometry([72, 0, 48, $rowsDesktop], [68, 0, 52, $rowsDesktop], [95, 0, 25, $rowsMobile]),
            [
                'menuId' => max(0, $menuId), 'orientation' => 'horizontal',
                'align' => 'right', 'mobileMode' => 'hamburger',
                'textColor' => '#f2f0e8', 'hoverTextColor' => '#c3ae83',
                'activeTextColor' => '#c3ae83', 'background' => '#30382a',
                'backgroundTransparent' => true, 'fontSize' => 17, 'fontWeight' => 600,
                'menuGap' => 22, 'paddingX' => 6, 'paddingY' => 8, 'radius' => 0,
                'borderWidth' => 0, 'borderColor' => '#000000', 'gapX' => 0, 'gapY' => 0,
            ]
        );

        return LayoutModel::normalize([
            'schemaVersion' => LayoutModel::SCHEMA,
            'units' => LayoutModel::UNITS,
            'rowPx' => LayoutModel::ROW_PX,
            'nodes' => $nodes,
        ]);
    }

    /** @param array<string,mixed> $design @return array{mediaId:int,url:string,source:string} */
    private static function resolveLogo(array $design): array
    {
        $url = esc_url_raw((string) ($design['LogoUrl'] ?? ''));
        $mediaId = max(0, (int) ($design['LogoMediaId'] ?? 0));
        if ($url !== '') {
            return ['mediaId' => $mediaId, 'url' => $url, 'source' => 'legacy-header'];
        }

        if (function_exists('get_theme_mod')) {
            $customLogoId = absint(get_theme_mod('custom_logo', 0));
            $customLogoUrl = $customLogoId > 0 ? wp_get_attachment_url($customLogoId) : false;
            if ($customLogoUrl) {
                return ['mediaId' => $customLogoId, 'url' => esc_url_raw((string) $customLogoUrl), 'source' => 'wordpress-custom-logo'];
            }
        }

        $siteIconId = absint(get_option('site_icon', 0));
        $siteIconUrl = $siteIconId > 0 ? wp_get_attachment_url($siteIconId) : false;
        if ($siteIconUrl) {
            return ['mediaId' => $siteIconId, 'url' => esc_url_raw((string) $siteIconUrl), 'source' => 'wordpress-site-icon'];
        }
        if (function_exists('get_site_icon_url')) {
            $siteIconUrl = (string) get_site_icon_url(512, '');
            if ($siteIconUrl !== '') {
                return ['mediaId' => 0, 'url' => esc_url_raw($siteIconUrl), 'source' => 'wordpress-site-icon-url'];
            }
        }

        return ['mediaId' => 0, 'url' => '', 'source' => 'not-found'];
    }

    /** @param array<string,mixed> $model @return array<string,int> */
    private static function nodeCounts(array $model): array
    {
        $counts = ['section' => 0, 'container' => 0, 'text' => 0, 'image' => 0, 'menu' => 0, 'button' => 0];
        foreach (($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) { continue; }
            $type = sanitize_key((string) ($node['type'] ?? ''));
            if (array_key_exists($type, $counts)) { $counts[$type]++; }
        }
        return $counts;
    }

'''
s = s[:start] + new_migration_block + s[end:]
write(path, s)

# ---------------------------------------------------------------------------
# Header/Footer UI: visible diagnosis + explicit re-conversion action.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
s = read(path)
s = replace_once(
    s,
    "use Hangar18\\Clean\\Model\\LayoutModel;\nuse Hangar18\\Clean\\Model\\TemplateLayoutModel;\n",
    "use Hangar18\\Clean\\Migration\\LegacyHeaderConverter;\nuse Hangar18\\Clean\\Model\\LayoutModel;\nuse Hangar18\\Clean\\Model\\TemplateLayoutModel;\n",
    'converter use'
)
s = replace_once(
    s,
    "    private const TEMPLATE_ACTION = 'h18_clean_global_template_action';\n",
    "    private const TEMPLATE_ACTION = 'h18_clean_global_template_action';\n    private const CONVERT_ACTION = 'h18_clean_legacy_header_convert';\n",
    'convert action constant'
)
s = replace_once(
    s,
    "    private const NONCE_TEMPLATE = 'h18_clean_global_template_action';\n",
    "    private const NONCE_TEMPLATE = 'h18_clean_global_template_action';\n    private const NONCE_CONVERT = 'h18_clean_legacy_header_convert';\n",
    'convert nonce constant'
)
s = replace_once(
    s,
    "        add_action('admin_post_' . self::TEMPLATE_ACTION, [self::class, 'templateAction']);\n",
    "        add_action('admin_post_' . self::TEMPLATE_ACTION, [self::class, 'templateAction']);\n        add_action('admin_post_' . self::CONVERT_ACTION, [self::class, 'convertLegacyHeader']);\n",
    'convert action registration'
)
rename_anchor = "        echo '<form class=\"h18-global-rename\" method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\">'; wp_nonce_field(self::NONCE_TEMPLATE); echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::TEMPLATE_ACTION) . '\"><input type=\"hidden\" name=\"part\" value=\"' . esc_attr($part) . '\"><input type=\"hidden\" name=\"template_id\" value=\"' . esc_attr($templateId) . '\"><input type=\"hidden\" name=\"operation\" value=\"rename\"><label>Templatenavn <input type=\"text\" name=\"template_name\" value=\"' . esc_attr((string) ($meta['name'] ?? '')) . '\"></label><button class=\"button\" type=\"submit\">Omdøb</button></form>';\n\n"
if rename_anchor not in s:
    raise SystemExit('Missing anchor: Header rename form')
s = s.replace(rename_anchor, rename_anchor + "        if ($part === 'header') { self::renderLegacyHeaderConversion(); }\n\n", 1)

save_marker = '    public static function save(): void\n'
idx = s.index(save_marker)
ui_methods = r'''    private static function renderLegacyHeaderConversion(): void
    {
        $status = LegacyHeaderConverter::diagnosticStatus();
        $counts = is_array($status['targetNodeCounts'] ?? null) ? $status['targetNodeCounts'] : [];
        $last = is_array($status['lastConversion'] ?? null) ? $status['lastConversion'] : [];

        echo '<section class="h18-manager-card h18-global-conversion"><h2>Gammel Header → Visual Designer</h2>';
        echo '<p class="description">Hvis de gamle Manager-data ikke længere findes, bruges den godkendte Desktop-reference fra 28-08-2026 som sikker fallback. Konverteringen gemmes altid som en ny Header-version.</p>';
        echo '<table class="widefat striped"><tbody>';
        echo '<tr><th>Legacy HeaderDesign</th><td>' . (!empty($status['legacyDesignFound']) ? 'Fundet' : 'Ikke fundet') . '</td></tr>';
        echo '<tr><th>Legacy Header-blok</th><td>' . (!empty($status['legacyShellFound']) ? 'Fundet' : 'Ikke fundet') . '</td></tr>';
        echo '<tr><th>WordPress-menu</th><td>' . esc_html((string) ($status['menuName'] ?? '')) . ' · ID ' . esc_html((string) ($status['menuId'] ?? 0)) . ' · ' . esc_html((string) ($status['menuItems'] ?? 0)) . ' elementer</td></tr>';
        echo '<tr><th>Logo-kilde</th><td>' . esc_html((string) ($status['logoSource'] ?? 'not-found')) . (!empty($status['logoFound']) ? ' · fundet' : ' · ikke fundet; Billede-plads oprettes stadig') . '</td></tr>';
        echo '<tr><th>Header – Standard nu</th><td>v' . esc_html((string) ($status['targetVersion'] ?? 0)) . ' · Sektion ' . esc_html((string) ($counts['section'] ?? 0)) . ' · Kasse ' . esc_html((string) ($counts['container'] ?? 0)) . ' · Billede ' . esc_html((string) ($counts['image'] ?? 0)) . ' · Tekst ' . esc_html((string) ($counts['text'] ?? 0)) . ' · Menu ' . esc_html((string) ($counts['menu'] ?? 0)) . '</td></tr>';
        if ($last) {
            echo '<tr><th>Seneste konvertering</th><td>' . esc_html((string) ($last['status'] ?? '')) . ' · ' . esc_html((string) ($last['source'] ?? '')) . ' · ' . esc_html((string) ($last['convertedUtc'] ?? $last['checkedUtc'] ?? '')) . (!empty($last['message']) ? ' · ' . esc_html((string) $last['message']) : '') . '</td></tr>';
        }
        echo '</tbody></table>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="margin-top:12px">';
        wp_nonce_field(self::NONCE_CONVERT);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::CONVERT_ACTION) . '"><button class="button button-primary" type="submit">Konvertér gammel Header igen</button></form></section>';
    }

    public static function convertLegacyHeader(): void
    {
        self::guard();
        check_admin_referer(self::NONCE_CONVERT);
        try {
            $result = LegacyHeaderConverter::convert(true);
            $counts = is_array($result['nodeCounts'] ?? null) ? $result['nodeCounts'] : [];
            $message = 'Header konverteret som v' . (int) ($result['templateVersion'] ?? 0)
                . ' fra ' . (string) ($result['source'] ?? 'ukendt kilde')
                . '. Sektion ' . (int) ($counts['section'] ?? 0)
                . ', Kasse ' . (int) ($counts['container'] ?? 0)
                . ', Billede ' . (int) ($counts['image'] ?? 0)
                . ', Tekst ' . (int) ($counts['text'] ?? 0)
                . ', Menu ' . (int) ($counts['menu'] ?? 0) . '.';
            self::redirect('header', (string) ($result['templateId'] ?? ''), 'success', $message);
        } catch (\Throwable $error) {
            self::redirect('header', TemplateLayoutModel::defaultId('header'), 'error', 'Header-konvertering fejlede: ' . $error->getMessage());
        }
    }

'''
s = s[:idx] + ui_methods + s[idx:]
write(path, s)

# ---------------------------------------------------------------------------
# Model QA for screenshot reference.
# ---------------------------------------------------------------------------
path = '.github/scripts/v0125_model_qa.php'
s = read(path)
old_echo = 'echo "Visual Designer Manager 0.1.41 model QA PASS\\n";'
if old_echo not in s:
    raise SystemExit('Missing anchor: 0.1.41 QA echo')
qa = r'''/* 0.1.42 approved Desktop screenshot fallback is deterministic and canonical. */
$referenceHeader = LegacyHeaderConverter::buildScreenshotReferenceModel(91, 77, 'https://example.test/header-logo.png');
$referenceByType = [];
foreach ($referenceHeader['nodes'] as $node) { $referenceByType[(string) ($node['type'] ?? '')][] = $node; }
vdAssert(count($referenceByType['section'] ?? []) === 1, 'Reference Header must contain one Section.');
vdAssert(count($referenceByType['container'] ?? []) === 1, 'Reference Header must contain one Container.');
vdAssert(count($referenceByType['image'] ?? []) === 1, 'Reference Header must reserve one logo Image.');
vdAssert(count($referenceByType['text'] ?? []) === 1, 'Reference Header must contain the association name Text.');
vdAssert(count($referenceByType['menu'] ?? []) === 1, 'Reference Header must contain one Menu.');
$referenceSection = ($referenceByType['section'] ?? [])[0] ?? [];
$referenceImage = ($referenceByType['image'] ?? [])[0] ?? [];
$referenceText = ($referenceByType['text'] ?? [])[0] ?? [];
$referenceMenu = ($referenceByType['menu'] ?? [])[0] ?? [];
vdAssert((int) ($referenceSection['geometry']['desktop']['x'] ?? -1) === 6, 'Reference Header must start at 5 percent / X=6.');
vdAssert((int) ($referenceSection['geometry']['desktop']['w'] ?? -1) === 108, 'Reference Header must be 90 percent / 108 units wide.');
vdAssert((int) ($referenceSection['geometry']['desktop']['h'] ?? -1) === 15, 'Reference Header must be ca. 120 px / 15 rows high.');
vdAssert(($referenceSection['props']['background'] ?? '') === '#30382a', 'Reference Header background color is wrong.');
vdAssert((int) ($referenceImage['geometry']['desktop']['w'] ?? -1) === 7, 'Reference logo width must match approved Desktop geometry.');
vdAssert((int) ($referenceImage['props']['mediaId'] ?? 0) === 77, 'Reference logo media ID was not retained.');
vdAssert(($referenceText['props']['text'] ?? '') === 'Aalborg Kaserners Veteran Panser- og Køretøjsforening', 'Reference brand text is wrong.');
vdAssert(($referenceText['props']['textColor'] ?? '') === '#f2f0e8', 'Reference brand text color is wrong.');
vdAssert((int) ($referenceMenu['geometry']['desktop']['x'] ?? -1) === 72, 'Reference Menu must occupy the right-side Desktop area.');
vdAssert((int) ($referenceMenu['geometry']['desktop']['w'] ?? -1) === 48, 'Reference Menu Desktop width is wrong.');
vdAssert((int) ($referenceMenu['props']['menuId'] ?? 0) === 91, 'Reference WordPress menu ID was not retained.');
vdAssert(($referenceMenu['props']['mobileMode'] ?? '') === 'hamburger', 'Reference mobile Menu must use hamburger mode.');
vdAssert((int) ($referenceMenu['geometry']['mobile']['x'] ?? -1) === 95, 'Reference mobile hamburger area must be right aligned.');

'''
s = s.replace(old_echo, qa + 'echo "Visual Designer Manager 0.1.42 model QA PASS\\n";', 1)
write(path, s)

# ---------------------------------------------------------------------------
# Release history and status.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(path))
if not history or history[0].get('version') != '0.1.42':
    history.insert(0, {
        'version': '0.1.42',
        'date': '2026-08-28',
        'items': [
            'BUG-11 rettet: Header-konvertering stopper ikke længere tavst når legacy HeaderDesign/Header-blok mangler.',
            'Header/Footer viser nu konverteringsdiagnose med legacy-kilder, WordPress-menu, logo-kilde, nodeantal og seneste konverteringsstatus.',
            'Ny knap Konvertér gammel Header igen gemmer altid resultatet non-destruktivt som en ny version af Header – Standard.',
            'Hvis legacy-kilden mangler, bruges den bruger-godkendte Desktop-reference fra 28-08-2026: 90% centreret, ca. 120 px høj, #30382A, logo/brand venstre og menu højre.',
            'Logo søges i legacy Header, WordPress Custom Logo og Site Icon; et Billede-element reserveres selv hvis filkilden ikke kan findes.',
            'Theme Shell-cutover forbliver OFF, indtil Desktop/Laptop/Mobil parity er bruger-QA PASS.'
        ]
    })
write(path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '<h4>0.1.42</h4><ul><li><strong>BUG-11:</strong> Header-konvertering er nu observerbar og fejler ikke længere tavst.</li><li><strong>Konvertér igen:</strong> Header/Footer har en eksplicit knap til non-destruktiv genkonvertering.</li><li><strong>Diagnose:</strong> viser legacy HeaderDesign, Header-blok, WordPress-menu, logo-kilde, nodeantal og seneste resultat.</li><li><strong>Desktop-reference:</strong> hvis legacy-data mangler, bygges Header – Standard efter den godkendte 28-08-2026-reference: 90% centreret, ca. 120 px, #30382A, logo/brand venstre og menu højre.</li><li><strong>Logo fallback:</strong> legacy-logo, WordPress Custom Logo og Site Icon undersøges i den rækkefølge.</li><li><strong>Sikkerhed:</strong> Theme Shell-cutover forbliver OFF indtil parity-QA.</li></ul>')
write('docs/v0142-status.md', '# Visual Designer Manager 0.1.42 – implementation status\n\n- BUG-11: FIXED in source; awaiting user QA.\n- Header conversion now records visible status instead of silently returning when legacy source data is absent.\n- Header/Footer shows source diagnosis and a manual re-conversion action.\n- Approved Desktop screenshot reference 2026-08-28 is the deterministic fallback: 90% centred, about 120 px, #30382A, logo/brand left and Menu right.\n- WordPress Menu remains a data source, not copied content.\n- Logo source resolution: legacy Header → WordPress Custom Logo → Site Icon; Image geometry is retained even when the image file cannot be resolved.\n- Re-conversion uses TemplateLayoutModel::saveVersion and is therefore non-destructive.\n- Theme Shell cutover remains OFF pending Desktop/Laptop/Mobile user QA.\n- BUG-02 remains user-QA PASS.\n- BUG-10 remains fixed.\n')

print('Visual Designer Manager 0.1.42 patch applied')
