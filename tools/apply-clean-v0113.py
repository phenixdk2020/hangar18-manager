from pathlib import Path

# Version + asset loading
p = Path('clean/hangar18-manager/hangar18-manager.php')
s = p.read_text(encoding='utf-8')
s = s.replace('Version: 0.1.12', 'Version: 0.1.13')
s = s.replace("H18_CLEAN_VERSION', '0.1.12'", "H18_CLEAN_VERSION', '0.1.13'")
s = s.replace('0.1.12 keeps editor labels outside canonical geometry and excludes layout wrappers from overlap warnings.', '0.1.13 preserves plugin activation across in-manager self-update and gives new text elements the same 80 px default height as images.')
p.write_text(s, encoding='utf-8')

# Editor: 80px = 10 rows default for text and image.
p = Path('clean/hangar18-manager/assets/editor-v018-core.js')
s = p.read_text(encoding='utf-8')
old = "        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: 0 }, false);"
new = "        const defaultH = (type === 'text' || type === 'image') ? Math.max(1, Math.ceil(80 / ROW_PX)) : 0;\n        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: defaultH }, false);"
if old not in s:
    raise SystemExit('addNode desktop geometry anchor not found')
s = s.replace(old, new, 1)
s = s.replace("                mobile: { x: 0, y: 0, w: 120, h: 0, inheritDesktop: true }", "                mobile: { x: 0, y: 0, w: 120, h: defaultH, inheritDesktop: true }", 1)
p.write_text(s, encoding='utf-8')

# Updater: preserve active/network-active state and verify reactivation before redirect.
p = Path('clean/hangar18-manager/src/Update/GitHubUpdater.php')
s = p.read_text(encoding='utf-8')
anchor = "        self::clearCache();\n        delete_site_transient('update_plugins');\n        wp_clean_plugins_cache(true);\n        require_once ABSPATH . 'wp-admin/includes/update.php';\n        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';\n        wp_update_plugins();\n\n        $skin = new \\Automatic_Upgrader_Skin();"
replacement = "        require_once ABSPATH . 'wp-admin/includes/plugin.php';\n        $wasNetworkActive = is_multisite() && is_plugin_active_for_network(self::PLUGIN_FILE);\n        $wasActive = $wasNetworkActive || is_plugin_active(self::PLUGIN_FILE);\n\n        self::clearCache();\n        delete_site_transient('update_plugins');\n        wp_clean_plugins_cache(true);\n        require_once ABSPATH . 'wp-admin/includes/update.php';\n        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';\n        wp_update_plugins();\n\n        $skin = new \\Automatic_Upgrader_Skin();"
if anchor not in s:
    raise SystemExit('updater pre-upgrade anchor not found')
s = s.replace(anchor, replacement, 1)
anchor2 = "        if (is_wp_error($result) || $result === false) {\n            self::redirectToUpdates([\n                'h18_clean_update_install' => 'error',\n                'h18_clean_update_version' => $latest,\n            ]);\n        }\n\n        self::redirectToUpdates([\n            'h18_clean_update_install' => 'success',"
replacement2 = "        if (is_wp_error($result) || $result === false) {\n            self::redirectToUpdates([\n                'h18_clean_update_install' => 'error',\n                'h18_clean_update_version' => $latest,\n            ]);\n        }\n\n        wp_clean_plugins_cache(true);\n        if ($wasActive) {\n            $stillActive = $wasNetworkActive\n                ? is_plugin_active_for_network(self::PLUGIN_FILE)\n                : is_plugin_active(self::PLUGIN_FILE);\n            if (!$stillActive) {\n                $activation = activate_plugin(self::PLUGIN_FILE, '', $wasNetworkActive, true);\n                wp_clean_plugins_cache(true);\n                $stillActive = !is_wp_error($activation) && ($wasNetworkActive\n                    ? is_plugin_active_for_network(self::PLUGIN_FILE)\n                    : is_plugin_active(self::PLUGIN_FILE));\n                if (!$stillActive) {\n                    wp_safe_redirect(add_query_arg([\n                        'h18_clean_update_install' => 'activation_error',\n                        'h18_clean_update_version' => $latest,\n                    ], admin_url('plugins.php')));\n                    exit;\n                }\n            }\n        }\n\n        self::redirectToUpdates([\n            'h18_clean_update_install' => 'success',"
if anchor2 not in s:
    raise SystemExit('updater post-upgrade anchor not found')
s = s.replace(anchor2, replacement2, 1)
p.write_text(s, encoding='utf-8')

# Readme/changelog
p = Path('clean/hangar18-manager/readme.txt')
s = p.read_text(encoding='utf-8')
s = s.replace('Version: 0.1.12', 'Version: 0.1.13', 1)
marker = '== 0.1.12 =='
entry = "== 0.1.13 ==\n* Direkte opdatering fra Hangar18 Manager husker om pluginet var aktivt eller netværksaktivt før opdateringen og genaktiverer/verificerer samme tilstand før redirect.\n* Hvis genaktivering mod forventning fejler, sendes administratoren sikkert til Plugins i stedet for en ikke-registreret Manager-side.\n* Nye Tekst-elementer starter med 80 px / 10 grid-rækker, samme grundhøjde som Billede.\n* Celle-split kan stadig ændre højden efterfølgende, og eksisterende elementer ændres ikke automatisk.\n\n"
if marker not in s:
    raise SystemExit('readme 0.1.12 marker not found')
s = s.replace(marker, entry + marker, 1)
p.write_text(s, encoding='utf-8')

Path('clean-release-notes.html').write_text("<h4>0.1.13</h4><ul><li>Direkte self-update bevarer og verificerer pluginets aktive/netværksaktive tilstand før redirect.</li><li>Fallback går til Plugins hvis genaktivering mod forventning fejler, så administratoren ikke lander på en ikke-registreret Manager-side.</li><li>Nye Tekst-elementer starter med 80 px / 10 grid-rækker, samme standardhøjde som Billede.</li><li>Eksisterende layouts og cell-split-geometri ændres ikke automatisk.</li></ul>\n", encoding='utf-8')
Path('clean-release-now.txt').write_text('v0.1.13\ntriggered_utc=2026-08-25T16:58:00Z\nreason=Preserve plugin activation across direct self-update and use 80px default text height.\nnonce=13\n', encoding='utf-8')
print('Clean v0.1.13 patch applied successfully.')
