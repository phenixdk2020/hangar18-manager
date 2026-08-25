from pathlib import Path

root = Path(__file__).resolve().parents[1]
updater_path = root / 'clean/hangar18-manager/src/Update/GitHubUpdater.php'
plugin_path = root / 'clean/hangar18-manager/hangar18-manager.php'
notes_path = root / 'clean-release-notes.html'

text = updater_path.read_text(encoding='utf-8')
old = '''        wp_clean_plugins_cache(true);\n        if ($wasActive) {\n            $stillActive = $wasNetworkActive\n                ? is_plugin_active_for_network(self::PLUGIN_FILE)\n                : is_plugin_active(self::PLUGIN_FILE);\n            if (!$stillActive) {\n                $activation = activate_plugin(self::PLUGIN_FILE, '', $wasNetworkActive, true);\n                wp_clean_plugins_cache(true);\n                $stillActive = !is_wp_error($activation) && ($wasNetworkActive\n                    ? is_plugin_active_for_network(self::PLUGIN_FILE)\n                    : is_plugin_active(self::PLUGIN_FILE));\n                if (!$stillActive) {\n                    wp_safe_redirect(add_query_arg([\n                        'h18_clean_update_install' => 'activation_error',\n                        'h18_clean_update_version' => $latest,\n                    ], admin_url('plugins.php')));\n                    exit;\n                }\n            }\n        }\n\n        self::redirectToUpdates([\n            'h18_clean_update_install' => 'success',\n            'h18_clean_update_version' => $latest,\n        ]);\n'''
new = '''        // Never execute the freshly replaced plugin again inside this request.\n        // Plugin_Upgrader may temporarily remove the active flag while replacing files.\n        // Restore the pre-update activation state directly, then let the redirect start\n        // a clean WordPress request that loads the new plugin normally.\n        wp_clean_plugins_cache(true);\n        $validation = validate_plugin(self::PLUGIN_FILE);\n        if (is_wp_error($validation)) {\n            wp_safe_redirect(add_query_arg([\n                'h18_clean_update_install' => 'plugin_invalid',\n                'h18_clean_update_version' => $latest,\n            ], admin_url('plugins.php')));\n            exit;\n        }\n\n        if ($wasNetworkActive) {\n            $networkPlugins = get_site_option('active_sitewide_plugins', []);\n            $networkPlugins = is_array($networkPlugins) ? $networkPlugins : [];\n            if (!isset($networkPlugins[self::PLUGIN_FILE])) {\n                $networkPlugins[self::PLUGIN_FILE] = time();\n                update_site_option('active_sitewide_plugins', $networkPlugins);\n            }\n        } elseif ($wasActive) {\n            $activePlugins = get_option('active_plugins', []);\n            $activePlugins = is_array($activePlugins) ? array_values($activePlugins) : [];\n            if (!in_array(self::PLUGIN_FILE, $activePlugins, true)) {\n                $activePlugins[] = self::PLUGIN_FILE;\n                sort($activePlugins, SORT_STRING);\n                update_option('active_plugins', $activePlugins);\n            }\n        }\n\n        wp_clean_plugins_cache(true);\n        if ($wasActive) {\n            $stillActive = $wasNetworkActive\n                ? is_plugin_active_for_network(self::PLUGIN_FILE)\n                : is_plugin_active(self::PLUGIN_FILE);\n            if (!$stillActive) {\n                wp_safe_redirect(add_query_arg([\n                    'h18_clean_update_install' => 'activation_error',\n                    'h18_clean_update_version' => $latest,\n                ], admin_url('plugins.php')));\n                exit;\n            }\n        }\n\n        self::redirectToUpdates([\n            'h18_clean_update_install' => 'success',\n            'h18_clean_update_version' => $latest,\n        ]);\n'''
if old not in text:
    raise SystemExit('Expected v0.1.15 activation block not found')
text = text.replace(old, new, 1)
updater_path.write_text(text, encoding='utf-8')

plugin = plugin_path.read_text(encoding='utf-8')
plugin = plugin.replace('Version: 0.1.15', 'Version: 0.1.16', 1)
plugin = plugin.replace("H18_CLEAN_VERSION', '0.1.15'", "H18_CLEAN_VERSION', '0.1.16'", 1)
plugin_path.write_text(plugin, encoding='utf-8')

notes_path.write_text(
    '<h4>0.1.16</h4><ul>'
    '<li>Self-update bevarer nu pluginets aktive status uden at gen-eksekvere den nye pluginfil i samme request.</li>'
    '<li>Single-site active_plugins og multisite active_sitewide_plugins gendannes direkte til status før opdateringen.</li>'
    '<li>Den installerede pluginfil valideres efter udpakning, og aktiv status verificeres før redirect til Manager.</li>'
    '<li>Hvis filen eller aktiv status ikke kan verificeres, lander administratoren sikkert på Plugins i stedet for en uregistreret Manager-side.</li>'
    '</ul>\n',
    encoding='utf-8'
)
