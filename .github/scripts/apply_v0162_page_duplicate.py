from pathlib import Path
import json

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
ADMIN = PLUGIN_ROOT / 'src/Admin/AdminController.php'
ADMIN_CSS = PLUGIN_ROOT / 'assets/admin-v0123.css'
PLUGIN = PLUGIN_ROOT / 'hangar18-manager.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = PLUGIN_ROOT / 'release-history.json'
BACKLOG = ROOT / 'docs/clean-backlog-v0100.md'
HF_SPEC = ROOT / 'docs/HEADER-FOOTER-SPEC.md'
STATUS = ROOT / 'docs/v0162-status.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


def append_once(text: str, marker: str, block: str) -> str:
    return text if marker in text else text.rstrip() + '\n\n' + block.strip() + '\n'


# Admin: action, nonce and handler registration.
admin = ADMIN.read_text(encoding='utf-8')
admin = replace_once(
    admin,
    "    private const CREATE_PAGE_ACTION = 'h18_clean_create_page';\n",
    "    private const CREATE_PAGE_ACTION = 'h18_clean_create_page';\n    private const DUPLICATE_PAGE_ACTION = 'h18_clean_duplicate_page';\n",
    'duplicate page action constant'
)
admin = replace_once(
    admin,
    "    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n",
    "    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n    private const DUPLICATE_PAGE_NONCE = 'h18_clean_duplicate_page';\n",
    'duplicate page nonce constant'
)
admin = replace_once(
    admin,
    "        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n",
    "        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n        add_action('admin_post_' . self::DUPLICATE_PAGE_ACTION, [self::class, 'duplicatePage']);\n",
    'duplicate page action registration'
)

# Admin: copy UI lives only under Manager -> Sider.
copy_ui = r'''            if (current_user_can('edit_post', $page->ID)) {
                echo '<details class="h18-manager-copy-page"><summary class="button">Kopiér</summary>';
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-manager-copy-page-form">';
                wp_nonce_field(self::DUPLICATE_PAGE_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::DUPLICATE_PAGE_ACTION) . '"><input type="hidden" name="source_post_id" value="' . esc_attr((string) $page->ID) . '">';
                echo '<label><span class="screen-reader-text">Nyt sidenavn</span><input type="text" name="new_page_title" required value="' . esc_attr((string) $page->post_title . ' – kopi') . '" aria-label="Nyt sidenavn"></label>';
                echo '<button class="button button-primary" type="submit">Kopiér side</button></form></details>';
            }
'''
admin = replace_once(
    admin,
    "            if (!$isFrontPage && current_user_can('delete_post', $page->ID)) {\n",
    copy_ui + "            if (!$isFrontPage && current_user_can('delete_post', $page->ID)) {\n",
    'copy page UI under pages actions'
)

# Admin: duplicate handler. It intentionally creates an independent draft with its own Designer history.
duplicate_handler = r'''
    public static function duplicatePage(): void
    {
        self::guard();
        check_admin_referer(self::DUPLICATE_PAGE_NONCE);

        $sourceId = absint($_POST['source_post_id'] ?? 0);
        $newTitle = sanitize_text_field((string) wp_unslash($_POST['new_page_title'] ?? ''));
        if ($sourceId <= 0 || get_post_type($sourceId) !== 'page' || !current_user_can('edit_post', $sourceId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kildesiden er ikke gyldig eller du mangler rettighed.']));
            exit;
        }
        if ($newTitle === '') {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Nyt sidenavn mangler.']));
            exit;
        }

        $source = get_post($sourceId);
        if (!$source instanceof \WP_Post) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kildesiden kunne ikke læses.']));
            exit;
        }

        $newSlug = self::uniquePageSlug(sanitize_title($newTitle));
        $newPostId = wp_insert_post([
            'post_type' => 'page',
            'post_title' => $newTitle,
            'post_name' => $newSlug,
            'post_parent' => (int) $source->post_parent,
            'post_status' => 'draft',
            'post_content' => (string) $source->post_content,
            'post_excerpt' => (string) $source->post_excerpt,
            'menu_order' => (int) $source->menu_order,
            'comment_status' => (string) $source->comment_status,
            'ping_status' => (string) $source->ping_status,
            'post_author' => get_current_user_id(),
        ], true);

        if (is_wp_error($newPostId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke kopieres: ' . $newPostId->get_error_message()]));
            exit;
        }
        $newPostId = (int) $newPostId;
        if ($newPostId <= 0) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'WordPress returnerede ikke et gyldigt ID til kopien.']));
            exit;
        }

        try {
            $pageTemplate = sanitize_text_field((string) get_post_meta($sourceId, '_wp_page_template', true));
            if ($pageTemplate !== '') {
                update_post_meta($newPostId, '_wp_page_template', $pageTemplate);
            }
            $thumbnailId = absint(get_post_thumbnail_id($sourceId));
            if ($thumbnailId > 0) {
                set_post_thumbnail($newPostId, $thumbnailId);
            }

            TemplateLayoutModel::ensureMigrated();
            TemplateLayoutModel::setPageChoice($newPostId, 'header', TemplateLayoutModel::pageChoice($sourceId, 'header'));
            TemplateLayoutModel::setPageChoice($newPostId, 'footer', TemplateLayoutModel::pageChoice($sourceId, 'footer'));

            $sourceHasDesigner = metadata_exists('post', $sourceId, LayoutModel::META)
                || (int) get_post_meta($sourceId, LayoutModel::VERSION_META, true) > 0;
            if ($sourceHasDesigner) {
                $sourceModel = LayoutModel::get($sourceId);
                $newVersion = LayoutModel::saveVersion(
                    $newPostId,
                    $sourceModel,
                    get_current_user_id(),
                    'Kopieret fra side ID ' . $sourceId . ' · ' . (string) $source->post_title
                );
                if ($newVersion !== 1) {
                    throw new \RuntimeException('Den kopierede Designer-side startede ikke med sin egen v1-historik.');
                }
                if (!hash_equals(LayoutModel::structuralDigest($sourceModel), LayoutModel::structuralDigest(LayoutModel::get($newPostId)))) {
                    throw new \RuntimeException('Designer-layoutet på kopien matcher ikke kildesiden.');
                }
            }

            clean_post_cache($newPostId);
        } catch (\Throwable $error) {
            wp_trash_post($newPostId);
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kopien blev rullet tilbage: ' . $error->getMessage()]));
            exit;
        }

        wp_safe_redirect(self::url('h18-clean-pages', [
            'vd_status' => 'ok',
            'vd_message' => '“' . (string) $source->post_title . '” er kopieret som “' . $newTitle . '” (kladde).',
        ]));
        exit;
    }
'''
admin = replace_once(
    admin,
    "\n\n    public static function updatePageStatus(): void\n",
    "\n" + duplicate_handler + "\n    public static function updatePageStatus(): void\n",
    'duplicate page handler'
)
ADMIN.write_text(admin, encoding='utf-8')


# Small UI treatment for the inline copy/name form.
css = ADMIN_CSS.read_text(encoding='utf-8')
css_block = r'''.h18-manager-copy-page{display:inline-block;vertical-align:top}.h18-manager-copy-page>summary{list-style:none;cursor:pointer}.h18-manager-copy-page>summary::-webkit-details-marker{display:none}.h18-manager-copy-page-form{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-top:6px}.h18-manager-copy-page-form input[type=text]{min-width:220px;max-width:320px}'''
css = append_once(css, '.h18-manager-copy-page{', css_block)
ADMIN_CSS.write_text(css, encoding='utf-8')


# Version bump.
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.61', ' * Version: 0.1.62', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.61');", "define('H18_CLEAN_VERSION', '0.1.62');", 'runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')


# Technical contract.
tech = TECH.read_text(encoding='utf-8')
tech_block = r'''## 0.1.62 – Kopiér side

### VD-PAGE-DUPLICATE-001
- Funktionen ligger under `Visual Designer Manager → Sider` og ikke i den generelle Designer-toolbar.
- Brugeren vælger `Kopiér`, angiver et nyt sidenavn og får en ny WordPress-side med nyt side-ID og unik slug.
- Kopien oprettes altid som `draft`; hjemmeside-status kopieres aldrig.
- WordPress-indhold, parent, menu-order, side-template og featured image kopieres som sikre sideattributter.
- Hvis kildesiden er en Visual Designer-side, kopieres den aktuelle canonical model til kopien og gemmes som kopiens egen version 1. Kildens versionshistorik kopieres ikke.
- Header- og Footer-sidevalg kopieres eksplicit med `TemplateLayoutModel::pageChoice()` / `setPageChoice()`.
- Den nye Designer-model SHA/digest verificeres mod kilden. Hvis kopieringen fejler efter oprettelsen, rulles den nye side tilbage til papirkurven.
- Original side og original versionshistorik ændres ikke.'''
tech = append_once(tech, '### VD-PAGE-DUPLICATE-001', tech_block)
TECH.write_text(tech, encoding='utf-8')


# Release notes and structured history.
notes = NOTES.read_text(encoding='utf-8')
release_notes = '<h4>0.1.62 – Kopiér side og Header/Footer Klar</h4><ul><li><strong>VD-PAGE-DUPLICATE-001:</strong> Manager → Sider har nu Kopiér med obligatorisk nyt sidenavn.</li><li>Kopien oprettes som kladde med nyt side-ID, unik slug og egen Designer-v1-historik.</li><li>Canonical Designer-layout, Header/Footer-valg, page template og featured image kopieres; original versionshistorik og hjemmeside-status kopieres ikke.</li><li>Kopieret Designer-layout verificeres strukturelt, og en fejl ruller den nye side tilbage.</li><li>Header/Footer vises som <strong>Klar</strong> i Admin. Klar betyder produktionsbaseline, ikke frysning: relevante fælles Designer-fejlrettelser og forbedringer skal fortsat gælde Header/Footer.</li></ul>\n'
if not notes.startswith('<h4>0.1.62'):
    notes = release_notes + notes
NOTES.write_text(notes, encoding='utf-8')

history_data = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history_data.setdefault('versions', [])
if not versions or versions[0].get('version') != '0.1.62':
    versions.insert(0, {
        'version': '0.1.62',
        'date': '2026-08-30',
        'items': [
            'VD-PAGE-DUPLICATE-001: Manager → Sider kan kopiere en side og kræver et nyt sidenavn.',
            'Kopien oprettes som kladde med nyt WordPress-ID, unik slug og separat Designer-v1-historik.',
            'Canonical layout samt Header/Footer-sidevalg kopieres; original historik og hjemmeside-status kopieres ikke.',
            'Header/Footer Admin-status er Klar, mens fælles Designer-forbedringer fortsat skal propagere til Header/Footer.'
        ],
    })
HISTORY.write_text(json.dumps(history_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# Canonical backlog current status.
backlog = BACKLOG.read_text(encoding='utf-8')
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.61', '## Aktuel milepælsstatus · v0.1.62', 1)
if '- **VD-PAGE-DUPLICATE-001 — IMPLEMENTERET:**' not in backlog:
    anchor = '- **VD-CLIPBOARD-001 — IMPLEMENTERET:** `Ctrl/Cmd+C`, `Ctrl/Cmd+V` og `Ctrl/Cmd+D`, subtree-kopi af Kasse/Sektion, nye IDs/parentId-remap og clipboard mellem Designer-sider.\n'
    backlog = replace_once(
        backlog,
        anchor,
        anchor + '- **VD-PAGE-DUPLICATE-001 — IMPLEMENTERET:** Sider kan kopieres med nyt navn som selvstændig kladde, nyt WordPress-ID, unik slug og egen Designer-v1-historik.\n',
        'backlog duplicate page status'
    )
BACKLOG.write_text(backlog, encoding='utf-8')


# Header/Footer remains maintained by the shared Designer after baseline closure.
hf = HF_SPEC.read_text(encoding='utf-8')
hf_rule = r'''## 16. Klar betyder vedligeholdt – fælles Designer-paritet

Admin-status **Klar** betyder, at Header/Footer-arkitekturen er en afsluttet produktionsbaseline. Det betyder ikke, at Header/Footer fryses.

Permanent vedligeholdelsesregel:

- fejlrettelser i den fælles Visual Designer-layoutmotor, elementmodel, Inspector, renderer eller responsive adfærd skal også gælde Header/Footer, når funktionen er relevant dér;
- nye eller forbedrede generelle Designer-elementer skal stilles til rådighed i Header/Footer, når de giver mening i globale templates;
- Side Designer og Header/Footer Designer skal så vidt muligt bruge samme canonical model, editor-runtime og renderer frem for parallel specialkode;
- release-QA skal ved relevante fælles Designer-ændringer kontrollere både Side Designer og Header/Footer for regression/paritet;
- en fælles Designer-forbedring må ikke betragtes som færdig, hvis den efterlader en relevant Header/Footer-variant på ældre adfærd.

`Klar` er derfor en vedligeholdt baseline, ikke en funktionsfrysning.'''
hf = append_once(hf, '## 16. Klar betyder vedligeholdt – fælles Designer-paritet', hf_rule)
HF_SPEC.write_text(hf, encoding='utf-8')


STATUS.write_text('''# Visual Designer Manager 0.1.62 status\n\n## Kopiér side\n- Placering: `Visual Designer Manager → Sider`.\n- `Kopiér` åbner et lille navnefelt direkte ved den valgte side.\n- Nyt sidenavn er obligatorisk.\n- Ny side oprettes altid som kladde med nyt WordPress-ID og unik slug.\n- WordPress-indhold, parent, menu-order, side-template og featured image kopieres.\n- Visual Designer-layout kopieres som kopiens egen v1; kildens historik kopieres ikke.\n- Header/Footer-sidevalg kopieres.\n- Hjemmeside-status kopieres aldrig.\n- Strukturel Designer-digest verificeres; fejl ruller kopien tilbage.\n\n## Header/Footer\n- Synlig Admin-status: `Klar`.\n- `Klar` er ikke en frysning. Relevante fælles Designer-fejlrettelser og forbedringer skal fortsat ramme Header/Footer og regressionstestes dér.\n''', encoding='utf-8')

print('Applied v0.1.62 page duplicate release patch.')
