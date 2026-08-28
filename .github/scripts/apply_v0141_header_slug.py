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
# Main plugin: version + converter registration.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/hangar18-manager.php'
s = read(path)
s = replace_once(s, ' * Version: 0.1.40', ' * Version: 0.1.41', 'plugin header version')
s = replace_once(s, "define('H18_CLEAN_VERSION', '0.1.40');", "define('H18_CLEAN_VERSION', '0.1.41');", 'version constant')
s = replace_once(
    s,
    "require_once H18_CLEAN_DIR . 'src/Model/TemplateLayoutModel.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Model/TemplateLayoutModel.php';\nrequire_once H18_CLEAN_DIR . 'src/Migration/LegacyHeaderConverter.php';\n",
    'legacy header converter require'
)
s = replace_once(
    s,
    "add_action('plugins_loaded', static function (): void {\n    \\Hangar18\\Clean\\Diagnostics\\DiagnosticStore::register();",
    "add_action('plugins_loaded', static function (): void {\n    \\Hangar18\\Clean\\Migration\\LegacyHeaderConverter::register();\n    \\Hangar18\\Clean\\Diagnostics\\DiagnosticStore::register();",
    'legacy header converter register'
)
write(path, s)

# ---------------------------------------------------------------------------
# BUG-10: deterministic slug generation for drafts + one-time repair of the
# blank draft slugs created by 0.1.39/0.1.40.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Admin/AdminController.php'
s = read(path)
s = replace_once(
    s,
    "    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n",
    "    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n    private const BLANK_SLUG_REPAIR_OPTION = 'h18_vd_blank_page_slugs_repaired_v0141';\n",
    'blank slug repair constant'
)
s = replace_once(
    s,
    "        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n",
    "        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n        add_action('admin_init', [self::class, 'repairBlankPageSlugs'], 20);\n",
    'blank slug repair hook'
)
s = replace_once(
    s,
    "        $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));\n        $parent = absint($_POST['page_parent'] ?? 0);",
    "        $requestedSlug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));\n        $slugBase = $requestedSlug !== '' ? $requestedSlug : sanitize_title($title);\n        $slug = self::uniquePageSlug($slugBase);\n        $parent = absint($_POST['page_parent'] ?? 0);",
    'automatic unique slug creation'
)
anchor = """    public static function exportBackup(): void\n    {\n"""
helpers = r'''    public static function repairBlankPageSlugs(): void
    {
        if (!current_user_can('edit_pages') || get_option(self::BLANK_SLUG_REPAIR_OPTION, false)) {
            return;
        }

        $repaired = 0;
        foreach (self::allPages() as $page) {
            if (!$page instanceof \WP_Post || trim((string) $page->post_name) !== '') {
                continue;
            }
            if (!current_user_can('edit_post', $page->ID)) {
                continue;
            }

            $base = sanitize_title((string) $page->post_title);
            $slug = self::uniquePageSlug($base !== '' ? $base : 'side');
            $result = wp_update_post([
                'ID' => (int) $page->ID,
                'post_name' => $slug,
            ], true);
            if (!is_wp_error($result) && (int) $result > 0) {
                $repaired++;
            }
        }

        update_option(self::BLANK_SLUG_REPAIR_OPTION, [
            'repairedUtc' => gmdate('c'),
            'count' => $repaired,
        ], false);
    }

    private static function uniquePageSlug(string $base): string
    {
        $base = sanitize_title($base);
        if ($base === '') {
            $base = 'side';
        }

        $candidate = $base;
        $suffix = 2;
        while (self::pageSlugExists($candidate)) {
            $candidate = $base . '-' . $suffix;
            $suffix++;
            if ($suffix > 10000) {
                throw new \RuntimeException('Kunne ikke finde en ledig side-slug.');
            }
        }
        return $candidate;
    }

    private static function pageSlugExists(string $slug): bool
    {
        $ids = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish', 'draft', 'pending', 'private', 'future'],
            'name' => sanitize_title($slug),
            'fields' => 'ids',
            'posts_per_page' => 1,
            'no_found_rows' => true,
            'suppress_filters' => true,
        ]);
        return is_array($ids) && !empty($ids);
    }

'''
s = replace_once(s, anchor, helpers + anchor, 'slug repair helpers')
write(path, s)

# ---------------------------------------------------------------------------
# Model QA: converter must serialize to canonical Header nodes without losing
# the WordPress menu reference or responsive geometry.
# ---------------------------------------------------------------------------
path = '.github/scripts/v0125_model_qa.php'
s = read(path)
s = replace_once(
    s,
    "require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/TemplateLayoutModel.php';\n",
    "require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/TemplateLayoutModel.php';\nrequire_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php';\n",
    'converter QA require'
)
s = replace_once(
    s,
    "use Hangar18\\Clean\\Model\\TemplateLayoutModel;\n",
    "use Hangar18\\Clean\\Model\\TemplateLayoutModel;\nuse Hangar18\\Clean\\Migration\\LegacyHeaderConverter;\n",
    'converter QA use'
)
old_tail = '''vdAssert(count(TemplateLayoutModel::history('header-standard-v1')) === count($beforeHistory), 'Migration duplicated historical versions.');\n\necho "Visual Designer Manager 0.1.25 model QA PASS\\n";'''
new_tail = '''vdAssert(count(TemplateLayoutModel::history('header-standard-v1')) === count($beforeHistory), 'Migration duplicated historical versions.');\n\n/* Legacy HeaderDesign is converted into a canonical editable Header model. */\n$convertedHeader = LegacyHeaderConverter::buildModelFromLegacyDesign([\n    'DesktopContentWidthPercent' => 90,\n    'LaptopContentWidthPercent' => 95,\n    'ShowBrand' => true,\n    'BrandText' => 'Aalborg Kaserners Veteran Panser- og Køretøjsforening',\n    'ShowLogo' => true,\n    'LogoMediaId' => 55,\n    'LogoUrl' => 'https://example.test/logo.png',\n    'MenuAlignment' => 'Right',\n    'BackgroundMode' => 'None',\n    'TextColor' => '#30382a',\n    'AccentColor' => '#c3ae83',\n    'MenuFontWeight' => 'Semibold',\n], 77);\n$convertedByType = [];\nforeach ($convertedHeader['nodes'] as $node) { $convertedByType[(string) ($node['type'] ?? '')][] = $node; }\nvdAssert(count($convertedByType['section'] ?? []) === 1, 'Legacy Header conversion must create one root Section.');\nvdAssert(count($convertedByType['container'] ?? []) === 1, 'Legacy Header conversion must create one inner Container.');\nvdAssert(count($convertedByType['image'] ?? []) === 1, 'Legacy Header logo was not converted to Image.');\nvdAssert(count($convertedByType['text'] ?? []) === 1, 'Legacy Header brand was not converted to Text.');\nvdAssert(count($convertedByType['menu'] ?? []) === 1, 'Legacy Header menu was not converted to Menu.');\n$convertedSection = ($convertedByType['section'] ?? [])[0] ?? [];\n$convertedMenu = ($convertedByType['menu'] ?? [])[0] ?? [];\nvdAssert((int) ($convertedSection['geometry']['desktop']['x'] ?? -1) === 6, '90 percent legacy Header width did not center at X=6.');\nvdAssert((int) ($convertedSection['geometry']['desktop']['w'] ?? -1) === 108, '90 percent legacy Header width did not become 108/120 units.');\nvdAssert((int) ($convertedMenu['props']['menuId'] ?? 0) === 77, 'Legacy active WordPress menu ID was not retained.');\nvdAssert(($convertedMenu['props']['textColor'] ?? '') === '#30382a', 'Transparent legacy Header did not retain dark menu text.');\nvdAssert((int) ($convertedMenu['props']['fontWeight'] ?? 0) === 600, 'Legacy Semibold menu weight was not converted.');\nvdAssert((int) ($convertedMenu['geometry']['mobile']['w'] ?? 0) === 30, 'Converted mobile Menu must reserve the right-side hamburger area.');\nvdAssert(empty($convertedMenu['geometry']['mobile']['inheritDesktop']), 'Converted mobile Menu geometry must be explicit.');\n\necho "Visual Designer Manager 0.1.41 model QA PASS\\n";'''
s = replace_once(s, old_tail, new_tail, 'converter QA assertions')
write(path, s)

# ---------------------------------------------------------------------------
# Release notes/status.
# ---------------------------------------------------------------------------
path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(path))
if not history or history[0].get('version') != '0.1.41':
    history.insert(0, {
        'version': '0.1.41',
        'date': '2026-08-28',
        'items': [
            'BUG-10 rettet: tomt Slug-felt genererer nu automatisk en slug fra sidetitlen allerede ved oprettelse af kladder.',
            'Automatiske og manuelt angivne side-slugs gøres unikke på tværs af Publiceret, Kladde, Afventer, Privat og Planlagt.',
            'Eksisterende Visual Designer-sider med tom slug fra 0.1.39/0.1.40 repareres én gang uden at ændre sideindhold eller Designer-layout.',
            'Legacy Hangar18 Header konverteres automatisk og non-destruktivt til Header – Standard ud fra de faktiske gemte HeaderDesign-data og den eksisterende Header-blok.',
            'Konverteringen binder Menu-elementet til den aktive WordPress-menu og bevarer den tidligere Visual Designer Header i template-historikken.',
            'Theme Shell-cutover forbliver OFF; den konverterede Header afventer brugerens 1:1 parity-QA på Desktop/Laptop/Mobil.'
        ]
    })
write(path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '<h4>0.1.41</h4><ul><li><strong>BUG-10:</strong> tomt Slug-felt genererer nu automatisk en unik slug fra sidetitlen, også for kladder.</li><li><strong>Repair:</strong> eksisterende sider med tom slug fra 0.1.39/0.1.40 repareres én gang.</li><li><strong>Header-konvertering:</strong> legacy Hangar18 HeaderDesign og Header-blok konverteres automatisk til det redigerbare <em>Header – Standard</em>.</li><li><strong>Menu:</strong> den aktive WordPress-menu kobles til det konverterede Menu-element som datakilde.</li><li><strong>Non-destruktiv:</strong> tidligere Visual Designer Header bevares i template-historikken.</li><li><strong>Sikkerhed:</strong> Theme Shell-cutover forbliver OFF, indtil Desktop/Laptop/Mobil parity er bruger-QA PASS.</li></ul>')
write('docs/v0141-status.md', '# Visual Designer Manager 0.1.41 – implementation status\n\n- BUG-10: FIXED in source; awaiting user QA.\n- Blank slug derives from title and is made unique before wp_insert_post, including drafts.\n- Existing blank page slugs are repaired once, non-destructively.\n- Legacy HeaderDesign conversion reads hangar18_manager_header_design_v25 plus the existing HANGAR18-HEADER block.\n- Header – Standard receives Section → Container → Logo/Brand/Menu as available.\n- Active legacy WordPress menu ID is retained as the Menu data source.\n- Existing Visual Designer Header state is retained through normal template version history.\n- Theme Shell cutover remains OFF; visual 1:1 parity awaits user QA.\n- BUG-02 rich-text selection remains user-QA PASS.\n')

print('Visual Designer Manager 0.1.41 patch applied')
