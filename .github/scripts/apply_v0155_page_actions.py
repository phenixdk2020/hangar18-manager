from pathlib import Path
import json

ROOT = Path('.')
ADMIN = ROOT / 'clean/hangar18-manager/src/Admin/AdminController.php'
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
NOTES = ROOT / 'clean-release-notes.html'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
STATUS = ROOT / 'docs/v0155-status.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    return text.replace(old, new, 1)

admin = ADMIN.read_text(encoding='utf-8')

admin = replace_once(
    admin,
    "    private const SET_HOME_PAGE_ACTION = 'h18_clean_set_home_page';\n",
    "    private const SET_HOME_PAGE_ACTION = 'h18_clean_set_home_page';\n"
    "    private const PAGE_STATUS_ACTION = 'h18_clean_page_status';\n"
    "    private const TRASH_PAGE_ACTION = 'h18_clean_trash_page';\n",
    'page action constants'
)
admin = replace_once(
    admin,
    "    private const SET_HOME_PAGE_NONCE = 'h18_clean_set_home_page';\n",
    "    private const SET_HOME_PAGE_NONCE = 'h18_clean_set_home_page';\n"
    "    private const PAGE_STATUS_NONCE = 'h18_clean_page_status';\n"
    "    private const TRASH_PAGE_NONCE = 'h18_clean_trash_page';\n",
    'page action nonces'
)
admin = replace_once(
    admin,
    "        add_action('admin_post_' . self::SET_HOME_PAGE_ACTION, [self::class, 'setHomePage']);\n",
    "        add_action('admin_post_' . self::SET_HOME_PAGE_ACTION, [self::class, 'setHomePage']);\n"
    "        add_action('admin_post_' . self::PAGE_STATUS_ACTION, [self::class, 'updatePageStatus']);\n"
    "        add_action('admin_post_' . self::TRASH_PAGE_ACTION, [self::class, 'trashPage']);\n",
    'page action registration'
)

# Dedicated landing-page card: never combine publish + home selection.
old_landing = """            } elseif (metadata_exists('post', $landingId, LayoutModel::META)) {
                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\">';
                wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::SET_HOME_PAGE_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $landingId) . '\"><button class=\"button\" type=\"submit\">Publicér og sæt som Hjem</button></form>';
            }
"""
new_landing = """            } elseif (metadata_exists('post', $landingId, LayoutModel::META)) {
                $landingPost = get_post($landingId);
                if ($landingPost instanceof \\WP_Post && (string) $landingPost->post_status === 'publish') {
                    echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\">';
                    wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                    echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::SET_HOME_PAGE_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $landingId) . '\"><button class=\"button\" type=\"submit\">Sæt som Hjem</button></form>';
                } elseif ($landingPost instanceof \\WP_Post && current_user_can('publish_pages')) {
                    echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\">';
                    wp_nonce_field(self::PAGE_STATUS_NONCE);
                    echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::PAGE_STATUS_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $landingId) . '\"><input type=\"hidden\" name=\"page_status\" value=\"publish\"><button class=\"button\" type=\"submit\">Publicér</button></form>';
                    echo '<span class=\"description\">Publicér først; vælg derefter siden som Hjem.</span>';
                }
            }
"""
admin = replace_once(admin, old_landing, new_landing, 'landing action split')

old_actions = """            if ($frontId !== (int) $page->ID && metadata_exists('post', $page->ID, LayoutModel::META)) {
                $homeLabel = (string) $page->post_status === 'publish' ? 'Sæt som Hjem' : 'Publicér og sæt som Hjem';
                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" style=\"display:inline\">';
                wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::SET_HOME_PAGE_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $page->ID) . '\"><button class=\"button\" type=\"submit\">' . esc_html($homeLabel) . '</button></form>';
            }
"""
new_actions = """            $isFrontPage = $frontId === (int) $page->ID;
            $isPublished = (string) $page->post_status === 'publish';
            if (!$isPublished && current_user_can('publish_pages') && current_user_can('edit_post', $page->ID)) {
                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" style=\"display:inline\">';
                wp_nonce_field(self::PAGE_STATUS_NONCE);
                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::PAGE_STATUS_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $page->ID) . '\"><input type=\"hidden\" name=\"page_status\" value=\"publish\"><button class=\"button\" type=\"submit\">Publicér</button></form>';
            } elseif ($isPublished && !$isFrontPage && current_user_can('edit_post', $page->ID)) {
                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" style=\"display:inline\">';
                wp_nonce_field(self::PAGE_STATUS_NONCE);
                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::PAGE_STATUS_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $page->ID) . '\"><input type=\"hidden\" name=\"page_status\" value=\"draft\"><button class=\"button\" type=\"submit\" onclick=\"return confirm(\\'Gør denne side til kladde? Den fjernes fra offentlig visning.\\');\">Gør til kladde</button></form>';
            }
            if (!$isFrontPage && $isPublished && metadata_exists('post', $page->ID, LayoutModel::META)) {
                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" style=\"display:inline\">';
                wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::SET_HOME_PAGE_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $page->ID) . '\"><button class=\"button\" type=\"submit\">Sæt som Hjem</button></form>';
            }
            if (!$isFrontPage && current_user_can('delete_post', $page->ID)) {
                $confirmTitle = esc_js((string) $page->post_title);
                echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" style=\"display:inline\">';
                wp_nonce_field(self::TRASH_PAGE_NONCE);
                echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::TRASH_PAGE_ACTION) . '\"><input type=\"hidden\" name=\"post_id\" value=\"' . esc_attr((string) $page->ID) . '\"><button class=\"button button-link-delete\" type=\"submit\" onclick=\"return confirm(\\'Flyt “' . $confirmTitle . '” til papirkurven? Siden kan gendannes fra WordPress-papirkurven.\\');\">Slet</button></form>';
            } elseif ($isFrontPage) {
                echo '<span class=\"description\" title=\"Vælg en anden hjemmeside før denne side kan afpubliceres eller slettes.\">Hjemmesiden er beskyttet</span>';
            }
"""
admin = replace_once(admin, old_actions, new_actions, 'pages action toolbar')

# Insert dedicated status/trash handlers before setHomePage.
anchor = "\n\n    public static function setHomePage(): void\n"
handlers = r'''

    public static function updatePageStatus(): void
    {
        self::guard();
        check_admin_referer(self::PAGE_STATUS_NONCE);

        $postId = absint($_POST['post_id'] ?? 0);
        $desired = sanitize_key((string) ($_POST['page_status'] ?? ''));
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('edit_post', $postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den valgte side er ikke gyldig.']));
            exit;
        }
        if (!in_array($desired, ['publish', 'draft'], true)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den ønskede sidestatus er ikke gyldig.']));
            exit;
        }
        if ($desired === 'publish' && !current_user_can('publish_pages')) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Du har ikke rettighed til at publicere sider.']));
            exit;
        }

        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        if ($desired === 'draft' && $frontId === $postId) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den aktive hjemmeside kan ikke gøres til kladde. Vælg først en anden side som Hjem.']));
            exit;
        }

        $result = wp_update_post(['ID' => $postId, 'post_status' => $desired], true);
        if (is_wp_error($result) || (int) $result <= 0) {
            $detail = is_wp_error($result) ? $result->get_error_message() : 'Ukendt WordPress-fejl';
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Sidestatus kunne ikke ændres: ' . $detail]));
            exit;
        }
        clean_post_cache($postId);
        $message = $desired === 'publish'
            ? '“' . get_the_title($postId) . '” er nu publiceret.'
            : '“' . get_the_title($postId) . '” er nu kladde og ikke længere offentligt publiceret.';
        wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'ok', 'vd_message' => $message]));
        exit;
    }

    public static function trashPage(): void
    {
        self::guard();
        check_admin_referer(self::TRASH_PAGE_NONCE);

        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('delete_post', $postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kan ikke slettes eller du mangler rettighed.']));
            exit;
        }
        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        if ($frontId === $postId) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den aktive hjemmeside kan ikke slettes. Vælg først en anden side som Hjem.']));
            exit;
        }

        $title = (string) get_the_title($postId);
        $trashed = wp_trash_post($postId);
        if (!$trashed instanceof \WP_Post) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke flyttes til papirkurven.']));
            exit;
        }
        wp_safe_redirect(self::url('h18-clean-pages', [
            'vd_status' => 'ok',
            'vd_message' => '“' . $title . '” er flyttet til WordPress-papirkurven og kan gendannes derfra.',
        ]));
        exit;
    }
'''
admin = replace_once(admin, anchor, handlers + anchor, 'status/trash handler insertion')

# Home selection is now selection-only: page must already be published.
old_publish_home = """        if ((string) $page->post_status !== 'publish') {
            if (!current_user_can('publish_pages')) {
                wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden skal publiceres før den kan være hjemmeside.']));
                exit;
            }
            $published = wp_update_post(['ID' => $postId, 'post_status' => 'publish'], true);
            if (is_wp_error($published) || (int) $published <= 0) {
                $detail = is_wp_error($published) ? $published->get_error_message() : 'Ukendt WordPress-fejl';
                wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke publiceres: ' . $detail]));
                exit;
            }
        }
"""
new_publish_home = """        if ((string) $page->post_status !== 'publish') {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Publicér siden først. “Sæt som Hjem” ændrer kun hjemmesidevalget og publicerer aldrig automatisk.']));
            exit;
        }
"""
admin = replace_once(admin, old_publish_home, new_publish_home, 'home no-auto-publish')
admin = replace_once(
    admin,
    "            'vd_message' => '“' . get_the_title($postId) . '” er nu publiceret og valgt som hjemmeside.',",
    "            'vd_message' => '“' . get_the_title($postId) . '” er nu valgt som hjemmeside.',",
    'home success message'
)

if 'Publicér og sæt som Hjem' in admin:
    raise SystemExit('combined publish/home label still present after patch')
ADMIN.write_text(admin, encoding='utf-8')

plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.54\n', ' * Version: 0.1.55\n', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.54');", "define('H18_CLEAN_VERSION', '0.1.55');", 'plugin runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history.setdefault('versions', [])
if not any(str(v.get('version')) == '0.1.55' for v in versions):
    versions.insert(0, {
        'version': '0.1.55',
        'date': '2026-08-29',
        'items': [
            'VD-PAGES-ACTIONS-001: Manager → Sider har separate Publicér, Gør til kladde, Sæt som Hjem og Slet-handlinger.',
            'Sæt som Hjem publicerer ikke længere automatisk; siden skal være publiceret først.',
            'Slet flytter siden til WordPress-papirkurven efter bekræftelse, så den kan gendannes.',
            'Den aktive hjemmeside kan hverken gøres til kladde eller slettes, før en anden side er valgt som Hjem.',
            'Designer, WordPress og Vis bevares som separate handlinger.'
        ]
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

old_notes = NOTES.read_text(encoding='utf-8').strip() if NOTES.exists() else ''
head = '''<h4>0.1.55 – Sidehandlinger</h4><ul><li><strong>VD-PAGES-ACTIONS-001:</strong> Manager → Sider har nu separate knapper til Publicér, Gør til kladde, Sæt som Hjem og Slet.</li><li><strong>Sæt som Hjem</strong> ændrer kun WordPress-hjemmesiden og publicerer ikke længere siden automatisk.</li><li><strong>Slet</strong> flytter siden til WordPress-papirkurven efter bekræftelse; siden kan derfor gendannes.</li><li>Den aktive hjemmeside er beskyttet mod Gør til kladde og Slet, indtil en anden hjemmeside er valgt.</li></ul>'''
NOTES.write_text(head + ('\n' + old_notes if old_notes else '') + '\n', encoding='utf-8')

tech = TECH.read_text(encoding='utf-8').rstrip()
contract = r'''

## 0.1.55 – Sidehandlinger

### VD-PAGES-ACTIONS-001
- Manager → Sider viser publiceringsstatus og sidehandlinger uden at sammenblande publicering og hjemmesidevalg.
- `Publicér` ændrer kun WordPress `post_status` til `publish`.
- `Gør til kladde` ændrer kun WordPress `post_status` til `draft` og kræver en tydelig bekræftelse i UI.
- `Sæt som Hjem` kræver, at siden allerede er publiceret, og ændrer kun `show_on_front=page` + `page_on_front=<ID>`; handlingen må ikke auto-publicere.
- `Slet` er en recoverable handling og bruger WordPress-papirkurven (`wp_trash_post`) efter bekræftelse. Permanent sletning er ikke en normal VDM-sidehandling.
- Den aktive hjemmeside må ikke gøres til kladde eller flyttes til papirkurven. Brugeren skal først vælge en anden publiceret Visual Designer-side som Hjem.
- `Designer`, `WordPress` og `Vis` forbliver separate navigationshandlinger.
- Denne kontrakt superseder auto-publiceringsdelen af `VD-HOME-001` fra 0.1.49; hjemmesidevalget er fra 0.1.55 selection-only.
'''
if '### VD-PAGES-ACTIONS-001' not in tech:
    TECH.write_text(tech + contract + '\n', encoding='utf-8')

STATUS.write_text('''# Visual Designer Manager 0.1.55 – status\n\n## Scope\n- Separate sidehandlinger i Manager → Sider.\n- Publicér og Gør til kladde ændrer kun WordPress post_status.\n- Sæt som Hjem er selection-only og kræver publiceret side.\n- Slet flytter siden til WordPress-papirkurven.\n- Aktiv hjemmeside er beskyttet mod draft/trash.\n\n## QA\n- PHP syntax på hele pluginet.\n- Eksisterende HierarchyNormalizer/LayoutModel regression-QA.\n- Kontrakt-gates for separate action/nonces, wp_trash_post, capability-checks og fravær af “Publicér og sæt som Hjem”.\n''', encoding='utf-8')

print('Applied Visual Designer Manager 0.1.55 page actions patch')
