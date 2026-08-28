from pathlib import Path
import json

ROOT = Path('.')
STATUSES = "['publish', 'draft', 'pending', 'private', 'future']"


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)

# Version + internal-page payload must include non-published editable pages.
path = 'clean/hangar18-manager/hangar18-manager.php'
s = read(path)
s = replace_once(s, ' * Version: 0.1.39', ' * Version: 0.1.40', 'plugin header version')
s = replace_once(s, "define('H18_CLEAN_VERSION', '0.1.39');", "define('H18_CLEAN_VERSION', '0.1.40');", 'version constant')
s = replace_once(
    s,
    "get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC'])",
    "get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC', 'post_status' => " + STATUSES + "])" ,
    'localized page choices statuses'
)
write(path, s)

# Manager -> Sider must list drafts/pending/private/future as well as published pages.
path = 'clean/hangar18-manager/src/Admin/AdminController.php'
s = read(path)
s = replace_once(
    s,
    "get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC'])",
    "get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC', 'post_status' => " + STATUSES + "])" ,
    'manager allPages statuses'
)
old = """            $status = $version > 0 ? '<span class=\"h18-manager-badge is-ok\">Designer v' . esc_html((string) $version) . '</span>' : '<span class=\"h18-manager-badge\">Ikke Visual Designer</span>';\n            echo '<tr><td><strong>' . esc_html((string) $page->post_title) . '</strong><br><small>ID ' . esc_html((string) $page->ID) . '</small></td>';\n            echo '<td><code>' . esc_html((string) $page->post_name) . '</code></td><td>' . $status . '</td><td>' . esc_html((string) count($model['nodes'])) . '</td><td>' . esc_html(self::prettyDate((string) ($last['savedUtc'] ?? ''))) . '</td><td class=\"h18-manager-actions\">';\n"""
new = """            $designerStatus = $version > 0 ? '<span class=\"h18-manager-badge is-ok\">Designer v' . esc_html((string) $version) . '</span>' : '<span class=\"h18-manager-badge\">Ikke Visual Designer</span>';\n            $wpStatusObject = get_post_status_object((string) $page->post_status);\n            $wpStatusLabel = $wpStatusObject ? (string) $wpStatusObject->label : (string) $page->post_status;\n            echo '<tr><td><strong>' . esc_html((string) $page->post_title) . '</strong><br><small>ID ' . esc_html((string) $page->ID) . '</small></td>';\n            echo '<td><code>' . esc_html((string) $page->post_name) . '</code></td><td><strong>' . esc_html($wpStatusLabel) . '</strong><br>' . $designerStatus . '</td><td>' . esc_html((string) count($model['nodes'])) . '</td><td>' . esc_html(self::prettyDate((string) ($last['savedUtc'] ?? ''))) . '</td><td class=\"h18-manager-actions\">';\n"""
s = replace_once(s, old, new, 'manager page status display')
write(path, s)

# Standalone Visual Designer page picker must show all editable page states and label them.
path = 'clean/hangar18-manager/src/Admin/EditorController.php'
s = read(path)
s = replace_once(
    s,
    "$pages = get_pages(['sort_column' => 'post_title', 'sort_order' => 'ASC']);",
    "$pages = get_pages(['sort_column' => 'post_title', 'sort_order' => 'ASC', 'post_status' => " + STATUSES + "]);",
    'designer page picker statuses'
)
s = replace_once(
    s,
    "echo '<table class=\"widefat striped\"><thead><tr><th>Side</th><th>Slug</th><th>Designer-version</th><th></th></tr></thead><tbody>';",
    "echo '<table class=\"widefat striped\"><thead><tr><th>Side</th><th>Slug</th><th>WordPress-status</th><th>Designer-version</th><th></th></tr></thead><tbody>';",
    'designer picker status column'
)
old = """            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);\n            echo '<tr><td>' . esc_html((string) $page->post_title) . '</td><td><code>' . esc_html((string) $page->post_name) . '</code></td><td>' . esc_html($version > 0 ? 'v' . $version : 'Ikke clean endnu') . '</td><td><a class=\"button button-primary\" href=\"' . esc_url(admin_url('admin.php?page=' . self::MENU . '&post=' . $page->ID)) . '\">Åbn designer</a></td></tr>';\n"""
new = """            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);\n            $statusObject = get_post_status_object((string) $page->post_status);\n            $statusLabel = $statusObject ? (string) $statusObject->label : (string) $page->post_status;\n            echo '<tr><td>' . esc_html((string) $page->post_title) . '</td><td><code>' . esc_html((string) $page->post_name) . '</code></td><td>' . esc_html($statusLabel) . '</td><td>' . esc_html($version > 0 ? 'v' . $version : 'Ikke gemt endnu') . '</td><td><a class=\"button button-primary\" href=\"' . esc_url(admin_url('admin.php?page=' . self::MENU . '&post=' . $page->ID)) . '\">Åbn designer</a></td></tr>';\n"""
s = replace_once(s, old, new, 'designer picker status label')
write(path, s)

# Release history.
path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(path))
if not history or history[0].get('version') != '0.1.40':
    history.insert(0, {
        'version': '0.1.40',
        'date': '2026-08-28',
        'items': [
            'BUG-09 rettet: Visual Designer-sidevælgeren viser nu Publiceret, Kladde, Afventer, Privat og Planlagt.',
            'Managerens Sider-oversigt bruger samme statusfilter, så nyoprettede kladder ikke forsvinder fra oversigten.',
            'WordPress-status vises tydeligt ved siden af Designer-versionen.',
            'Interne sidevalg i Designer inkluderer samme redigerbare sidestatusser.',
            'Header/Menu-funktionerne fra 0.1.39 og BUG-02 selection-kontrakten er uændrede.'
        ]
    })
write(path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '<h4>0.1.40</h4><ul><li><strong>BUG-09:</strong> kladder og andre ikke-publicerede sider vises nu i Visual Designer.</li><li><strong>Sidevælger:</strong> Publiceret, Kladde, Afventer, Privat og Planlagt understøttes og WordPress-status vises tydeligt.</li><li><strong>Manager → Sider:</strong> samme statusfilter bruges, så en ny kladde ikke forsvinder efter oprettelse.</li><li><strong>Interne links:</strong> Designerens sidevalg bruger samme redigerbare sidestatusser.</li><li><strong>Regression:</strong> Header/Menu fra 0.1.39 og BUG-02 fra 0.1.38 ændres ikke.</li></ul>')
write('docs/v0140-status.md', '# Visual Designer Manager 0.1.40 – implementation status\n\n- BUG-09: FIXED in source; awaiting user QA.\n- Visual Designer page picker includes publish, draft, pending, private and future pages.\n- Manager → Sider uses the same editable-page status set.\n- WordPress status is shown separately from Designer version.\n- Internal page choices include the same statuses.\n- Header/Menu 0.1.39 and BUG-02 rich-text contracts are unchanged.\n')

print('Visual Designer Manager 0.1.40 BUG-09 patch applied')
