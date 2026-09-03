from pathlib import Path
import json
import re

ROOT = Path('.')
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
ADMIN = ROOT / 'clean/hangar18-manager/src/Admin/AdminController.php'
EXPORT = ROOT / 'clean/hangar18-manager/src/Admin/ExportController.php'
TRANSFER = ROOT / 'clean/hangar18-manager/src/Admin/PortableTransferController.php'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
NOTES = ROOT / 'clean-release-notes.html'
STATUS = ROOT / 'docs/v0189-status.md'


def read(path):
    return path.read_text(encoding='utf-8')


def write(path, text):
    path.write_text(text, encoding='utf-8')

# Version bump.
plugin = read(PLUGIN)
for old, new in [
    ('Version: 0.1.88', 'Version: 0.1.89'),
    ("define('VDM_VERSION', '0.1.88');", "define('VDM_VERSION', '0.1.89');"),
    ("define('H18_CLEAN_VERSION', '0.1.88');", "define('H18_CLEAN_VERSION', '0.1.89');"),
]:
    if old not in plugin:
        raise SystemExit(f'Missing plugin version marker: {old}')
    plugin = plugin.replace(old, new, 1)
write(PLUGIN, plugin)

# Manager UI cleanup: hide conversion route, remove dashboard card and retire status-badge runtime.
admin = read(ADMIN)
visible_conversion = "        add_submenu_page(self::MENU, 'Konvertering af sider', 'Konvertering', $cap, 'h18-clean-conversion', [ConversionController::class, 'render']);"
hidden_conversion = "        // Legacy conversion/recovery route: intentionally hidden from the normal Manager menu.\n        add_submenu_page(null, 'Konvertering (intern)', 'Konvertering', $cap, 'h18-clean-conversion', [ConversionController::class, 'render']);"
if visible_conversion not in admin:
    raise SystemExit('Visible conversion menu line not found')
admin = admin.replace(visible_conversion, hidden_conversion, 1)

conversion_card = "        self::card('Konvertering', 'Forbered eksisterende WordPress-sider som ikke-destruktive Visual Designer-kandidater, QA dem og aktivér én side ad gangen.', self::url('h18-clean-conversion'), 'Konvertér sider');\n"
if conversion_card not in admin:
    raise SystemExit('Conversion dashboard card not found')
admin = admin.replace(conversion_card, '', 1)

status_enqueue = "        wp_enqueue_script('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.js', [], H18_CLEAN_VERSION, true);"
if status_enqueue not in admin:
    raise SystemExit('Status badge runtime enqueue not found')
admin = admin.replace(status_enqueue, "        // v0.1.89: development-status badges are no longer rendered in the user-facing Manager UI.", 1)
write(ADMIN, admin)

# Hide old combined transfer menu; keep the recovery/import route registered and functional.
transfer = read(TRANSFER)
menu_pattern = re.compile(
    r"    public static function menu\(\): void\n    \{\n        add_submenu_page\(\n            AdminController::MENU,\n            'Eksport / import',\n            'Eksport / import',\n            'manage_options',\n            self::PAGE,\n            \[self::class, 'render'\]\n        \);\n    \}",
    re.M,
)
hidden_menu = """    public static function menu(): void
    {
        // Recovery/import route only. Normal users export from the unified Export page.
        add_submenu_page(
            null,
            'Import / recovery',
            'Import / recovery',
            'manage_options',
            self::PAGE,
            [self::class, 'render']
        );
    }"""
transfer, count = menu_pattern.subn(hidden_menu, transfer, count=1)
if count != 1:
    raise SystemExit('Portable transfer visible menu block not found')

# Refactor portable site creation into a reusable builder for Export > All.
export_block = re.compile(
    r"    public static function exportSite\(\): void\n    \{.*?\n    \}\n\n    public static function preflightImport\(\): void",
    re.S,
)
replacement = r'''    public static function exportSite(): void
    {
        self::guard();
        check_admin_referer(self::EXPORT_NONCE);
        if (!class_exists('ZipArchive')) {
            wp_die(esc_html__('PHP ZipArchive mangler på serveren.', 'visual-designer-manager'));
        }

        @set_time_limit(0);
        $tmp = tempnam(get_temp_dir(), 'vdm-export-');
        if (!is_string($tmp) || $tmp === '') {
            wp_die(esc_html__('Kunne ikke oprette midlertidig eksportfil.', 'visual-designer-manager'));
        }

        try {
            self::buildPortablePackage($tmp);
        } catch (\Throwable $error) {
            @unlink($tmp);
            wp_die(esc_html('Eksport fejlede: ' . $error->getMessage()));
        }

        $sha = hash_file('sha256', $tmp);
        $name = self::downloadName();
        nocache_headers();
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . $name . '"');
        header('Content-Length: ' . (string) filesize($tmp));
        if (is_string($sha)) {
            header('X-Visual-Designer-SHA256: ' . $sha);
        }
        readfile($tmp);
        @unlink($tmp);
        exit;
    }

    /**
     * Build the canonical portable site ZIP at a caller-provided path.
     * Used both by the hidden recovery route and Export > Eksporter alt.
     *
     * @return array{sha256:string,filename:string,counts:array<string,int>}
     */
    public static function buildPortablePackage(string $targetPath): array
    {
        if (!class_exists('ZipArchive')) {
            throw new \RuntimeException('PHP ZipArchive mangler på serveren.');
        }
        if ($targetPath === '') {
            throw new \RuntimeException('Målstien til portable sitepakken er tom.');
        }

        $zip = new \ZipArchive();
        $opened = $zip->open($targetPath, \ZipArchive::CREATE | \ZipArchive::OVERWRITE);
        if ($opened !== true) {
            throw new \RuntimeException('Kunne ikke oprette den portable ZIP-pakke.');
        }

        $files = [];
        try {
            $site = self::siteData();
            $pages = self::pageData();
            $templates = self::templateData();
            $modules = self::moduleData();
            $fields = self::fieldData();
            $navigation = self::navigationData();
            $media = self::addMedia($zip, $files);
            $legacyMap = self::legacyMap();

            self::addJson($zip, 'site.json', $site, $files);
            self::addJson($zip, 'pages/pages.json', $pages, $files);
            self::addJson($zip, 'templates/templates.json', $templates, $files);
            self::addJson($zip, 'modules/modules.json', $modules, $files);
            self::addJson($zip, 'modules/custom-fields.json', $fields, $files);
            self::addJson($zip, 'navigation/navigation.json', $navigation, $files);
            self::addJson($zip, 'media/media-index.json', $media, $files);
            self::addJson($zip, 'migration/legacy-map.json', $legacyMap, $files);

            $counts = [
                'pages' => count($pages['records']),
                'templates' => count($templates['records']),
                'modules' => count($modules['records']),
                'menus' => count($navigation['menus']),
                'media' => count($media['records']),
                'vehicleFields' => count($fields['vehicleFields']),
                'eventFields' => count($fields['eventFields']),
            ];
            $manifest = self::manifest($files, $counts, $site);
            $manifestJson = wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if (!is_string($manifestJson) || !$zip->addFromString('manifest.json', $manifestJson . "\n")) {
                throw new \RuntimeException('manifest.json kunne ikke oprettes.');
            }
        } catch (\Throwable $error) {
            $zip->close();
            @unlink($targetPath);
            throw $error;
        }

        if (!$zip->close()) {
            @unlink($targetPath);
            throw new \RuntimeException('ZIP-pakken kunne ikke afsluttes.');
        }
        if (!is_file($targetPath) || filesize($targetPath) === 0) {
            @unlink($targetPath);
            throw new \RuntimeException('Den portable sitepakke blev ikke oprettet korrekt.');
        }
        $sha = hash_file('sha256', $targetPath);
        if (!is_string($sha) || $sha === '') {
            @unlink($targetPath);
            throw new \RuntimeException('SHA-256 kunne ikke beregnes for den portable sitepakke.');
        }

        return [
            'sha256' => $sha,
            'filename' => self::downloadName(),
            'counts' => $counts,
        ];
    }

    public static function preflightImport(): void'''
transfer, count = export_block.subn(replacement, transfer, count=1)
if count != 1:
    raise SystemExit('Portable exportSite block not found for refactor')
write(TRANSFER, transfer)

# Unified Export page: add All and replace disabled placeholder with working export.
export = read(EXPORT)
labels_old = "        'plugin' => 'Plugin',\n"
if labels_old not in export:
    raise SystemExit('Export labels marker not found')
export = export.replace(labels_old, "        'all' => 'Alt',\n" + labels_old, 1)

old_desc = "        echo '<p class=\"h18-manager-description\">Eksportér program, tema, sider, navigation og mediefiler som transportable pakker. Export er adskilt fra automatisk backup før opdatering.</p>';"
new_desc = "        echo '<p class=\"h18-manager-description\">Eksportér hele installationens VDM-indhold eller vælg enkelte dele. <strong>Eksporter alt</strong> samler plugin, aktivt tema og en komplet portabel sitepakke i én ZIP.</p>';"
if old_desc not in export:
    raise SystemExit('Export description not found')
export = export.replace(old_desc, new_desc, 1)

grid_marker = "        echo '<div class=\"h18-manager-card-grid\">';\n"
if grid_marker not in export:
    raise SystemExit('Export card grid marker not found')
export = export.replace(grid_marker, grid_marker + "        self::card('all', 'Eksporter alt', 'Komplet arkiv med Visual Designer Manager-plugin, aktivt tema/parent-theme og en direkte importerbar portabel VDM-sitepakke med sider/layouts/historik, Header/Footer, Events, Køretøjer, Billedgalleri, feltdefinitioner, navigation, medier og Siteindstillinger.', $zipReady);\n", 1)

placeholder = "        echo '<section class=\"h18-manager-card h18-manager-module\"><h2>Export hele sitet</h2><p>Planlagt samlet transportpakke med plugin, tema, globalt design, Header/Footer, sider, navigation, komponenter, data-moduler og medier.</p><button class=\"button\" type=\"button\" disabled>Kommer senere</button></section>';\n"
if placeholder not in export:
    raise SystemExit('Disabled export-all placeholder not found')
export = export.replace(placeholder, '', 1)

# Create temporary portable package only for the all bundle and add it as a nested, directly importable ZIP.
needle = "        $files = [];\n        $recordCount = 0;\n\n        try {\n            switch ($kind) {"
replacement2 = "        $files = [];\n        $recordCount = 0;\n        $portableTmp = null;\n\n        try {\n            switch ($kind) {\n                case 'all':\n                    $recordCount += self::addDirectory(\n                        $zip,\n                        H18_CLEAN_DIR,\n                        'plugin/' . basename(untrailingslashit(H18_CLEAN_DIR)),\n                        $files\n                    );\n                    self::addJson($zip, 'plugin.json', [\n                        'schemaVersion' => self::SCHEMA,\n                        'product' => 'Visual Designer Manager',\n                        'internalVersion' => H18_CLEAN_VERSION,\n                        'sourceDirectory' => basename(untrailingslashit(H18_CLEAN_DIR)),\n                    ], $files);\n                    $recordCount += self::addTheme($zip, $files);\n\n                    $portableTmp = tempnam(get_temp_dir(), 'vdm-portable-all-');\n                    if (!is_string($portableTmp) || $portableTmp === '') {\n                        throw new \\RuntimeException('Kunne ikke oprette midlertidig portabel sitepakke.');\n                    }\n                    $portable = PortableTransferController::buildPortablePackage($portableTmp);\n                    self::addFile($zip, $portableTmp, 'portable-site/' . sanitize_file_name((string) $portable['filename']), $files);\n                    $portableCounts = isset($portable['counts']) && is_array($portable['counts']) ? $portable['counts'] : [];\n                    $recordCount += array_sum(array_map('intval', $portableCounts));\n                    self::addJson($zip, 'all.json', [\n                        'schemaVersion' => self::SCHEMA,\n                        'type' => 'all',\n                        'portableSite' => [\n                            'filename' => (string) $portable['filename'],\n                            'sha256' => (string) $portable['sha256'],\n                            'counts' => $portableCounts,\n                        ],\n                        'includes' => ['plugin', 'active-theme', 'parent-theme-when-used', 'portable-site'],\n                    ], $files);\n                    break;"
if needle not in export:
    raise SystemExit('Export switch insertion point not found')
export = export.replace(needle, replacement2, 1)

# Always clean nested temporary portable ZIP.
catch_old = "        } catch (\\Throwable $error) {\n            $zip->close();\n            @unlink($tmp);\n            wp_die(esc_html('Export fejlede: ' . $error->getMessage()));\n        }\n\n        if (!is_file($tmp) || filesize($tmp) === 0) {"
catch_new = "        } catch (\\Throwable $error) {\n            $zip->close();\n            if (is_string($portableTmp) && $portableTmp !== '') { @unlink($portableTmp); }\n            @unlink($tmp);\n            wp_die(esc_html('Export fejlede: ' . $error->getMessage()));\n        }\n\n        if (is_string($portableTmp) && $portableTmp !== '') { @unlink($portableTmp); }\n\n        if (!is_file($tmp) || filesize($tmp) === 0) {"
if catch_old not in export:
    raise SystemExit('Export catch cleanup point not found')
export = export.replace(catch_old, catch_new, 1)
write(EXPORT, export)

# Release history.
history = json.loads(read(HISTORY))
entry = {
    'version': '0.1.89',
    'date': '2026-09-03',
    'items': [
        'VDM-MANAGER-CLEANUP-001: Konvertering og den gamle Eksport / import-side er fjernet fra den synlige Manager-menu og bevares kun som skjulte compatibility/recovery-ruter.',
        'Eksport er nu den eneste normale eksportindgang og har en aktiv Eksporter alt-funktion.',
        'Eksporter alt samler plugin, aktivt tema/parent-theme og en direkte importerbar portabel VDM-sitepakke i ét verificeret arkiv.',
        'Den portable sitepakke indeholder sider/layouts og historik, Header/Footer, modulrecords, køretøjs-/eventfelter, navigation, medier og Siteindstillinger.',
        'Udviklingsstatus-badges som Klar, Under udvikling og Ikke færdig er fjernet fra den brugerrettede Manager-menu og dashboard-legend.'
    ]
}
versions = history.setdefault('versions', [])
if not versions or versions[0].get('version') != '0.1.89':
    versions.insert(0, entry)
write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes = read(NOTES)
section = '''<section data-version="0.1.89"><h2>0.1.89</h2><ul><li><strong>Renere Manager-menu:</strong> Konvertering og det gamle Eksport / import-punkt er skjult fra normal navigation.</li><li><strong>Eksporter alt:</strong> Eksport-siden kan nu hente plugin, aktivt tema/parent-theme og en komplet portabel VDM-sitepakke i ét arkiv.</li><li>Den portable ZIP inde i totalpakken er direkte kompatibel med VDM-importens preflight/importmotor.</li><li>Sider/layouts/historik, Header/Footer, Events, Køretøjer, Billedgalleri, feltdefinitioner, navigation, medier og Siteindstillinger er med i den portable del.</li><li>Statusmærker som <strong>Klar</strong>, <strong>Under udvikling</strong> og <strong>Ikke færdig</strong> vises ikke længere ud for Manager-punkterne.</li></ul></section>\n'''
if 'data-version="0.1.89"' not in notes:
    notes = section + notes
write(NOTES, notes)

write(STATUS, '''# Visual Designer Manager v0.1.89 – Manager cleanup + Export All\n\nStatus: candidate\n\n## Scope\n- Hide Conversion from normal Manager navigation while preserving the internal recovery route.\n- Hide the old Export / import submenu while preserving import/preflight recovery.\n- Remove user-facing development-status badges and dashboard legend.\n- Make Export the single normal export entry point.\n- Add Export All: plugin + active/parent theme + nested directly importable portable VDM site ZIP.\n\n## Safety\nThe existing portable preflight/import engine remains intact. The total archive embeds the canonical portable site ZIP rather than inventing a second import schema.\n''')

print('Applied Visual Designer Manager v0.1.89 manager cleanup/export-all candidate')
