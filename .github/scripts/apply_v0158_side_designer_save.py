from pathlib import Path
import json

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
PLUGIN = PLUGIN_ROOT / 'hangar18-manager.php'
EDITOR = PLUGIN_ROOT / 'src/Admin/EditorController.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = PLUGIN_ROOT / 'release-history.json'
STATUS = ROOT / 'docs/v0158-status.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# BUG-20 / VD-PAGE-SAVE-CACHE-001
# Visual Designer persists its canonical layout in post meta. A normal save must
# also touch the WordPress page after that meta write so normal save_post /
# post_updated based cache invalidation runs AFTER the new model exists.
editor = EDITOR.read_text(encoding='utf-8')

noop_old = '''            if ($currentVersion > 0 && $sameModel && $sameShell && !$statusChanged) {
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-and-shell-unchanged']);
                self::redirect($postId, 'success', 'Ingen ændringer siden seneste gemte version. Der blev ikke oprettet en ny version.');
            }
'''
noop_new = '''            if ($currentVersion > 0 && $sameModel && $sameShell && !$statusChanged) {
                // A previous Designer save may already be canonical while a page cache still
                // contains older frontend HTML. Touching the page is therefore intentional
                // even on a canonical no-op save.
                self::touchFrontendPage($postId, '', $currentVersion);
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-and-shell-unchanged']);
                self::redirect($postId, 'success', 'Ingen layoutændringer siden seneste gemte version. Frontend-cache er blevet invalideret.');
            }
'''
editor = replace_once(editor, noop_old, noop_new, 'no-op frontend cache invalidation')

status_old = '''            if ($statusChanged) {
                $updatedPost = wp_update_post(['ID' => $postId, 'post_status' => $desiredStatus], true);
                if (is_wp_error($updatedPost)) {
                    throw new \\RuntimeException($updatedPost->get_error_message());
                }
                DiagnosticStore::append($postId, 'page_status_changed', ['from' => $currentPostStatus, 'to' => $desiredStatus, 'version' => $version]);
            }
'''
status_new = '''            // LayoutModel::saveVersion() writes canonical Designer data to post meta.
            // Touch the WordPress page only AFTER those writes so conventional WordPress,
            // host and plugin caches observe and purge against the new Designer state.
            self::touchFrontendPage($postId, $statusChanged ? $desiredStatus : '', $version);
            if ($statusChanged) {
                DiagnosticStore::append($postId, 'page_status_changed', ['from' => $currentPostStatus, 'to' => $desiredStatus, 'version' => $version]);
            }
'''
editor = replace_once(editor, status_old, status_new, 'normal save page touch')

preview_old = '''                if (is_string($permalink) && $permalink !== '') {
                    wp_safe_redirect($permalink);
                    exit;
                }
'''
preview_new = '''                if (is_string($permalink) && $permalink !== '') {
                    // The version query makes Gem & vis unambiguous even behind a cache layer
                    // that does not immediately honour a WordPress purge event.
                    wp_safe_redirect(add_query_arg('h18_vd_saved', $version, $permalink));
                    exit;
                }
'''
editor = replace_once(editor, preview_old, preview_new, 'save and view cache buster')

restore_old = '''            DiagnosticStore::append($postId, 'restore_result', [
                'targetVersion' => $targetVersion,
                'newVersion' => $newVersion,
                'saved' => DiagnosticStore::modelSummary(LayoutModel::get($postId)),
            ]);
'''
restore_new = '''            self::touchFrontendPage($postId, '', $newVersion);
            DiagnosticStore::append($postId, 'restore_result', [
                'targetVersion' => $targetVersion,
                'newVersion' => $newVersion,
                'saved' => DiagnosticStore::modelSummary(LayoutModel::get($postId)),
            ]);
'''
editor = replace_once(editor, restore_old, restore_new, 'restore frontend cache invalidation')

helper_marker = '''    private static function redirect(int $postId, string $status, string $message): void
'''
helper = '''    /**
     * Make a Designer meta save visible through the normal WordPress post lifecycle.
     *
     * Canonical Designer data is already persisted before this method is called. The
     * subsequent wp_update_post() deliberately fires post_updated/save_post hooks so
     * WordPress and full-page cache integrations invalidate the old public rendering.
     */
    private static function touchFrontendPage(int $postId, string $desiredStatus, int $version): void
    {
        $post = get_post($postId);
        if (!$post instanceof \\WP_Post || $post->post_type !== 'page') {
            throw new \\RuntimeException('Frontend-cache kunne ikke invalideres: siden findes ikke længere.');
        }

        $update = ['ID' => $postId];
        if ($desiredStatus !== '') {
            $update['post_status'] = $desiredStatus;
        }

        $updatedPost = wp_update_post($update, true);
        if (is_wp_error($updatedPost)) {
            throw new \\RuntimeException('Frontend-cache kunne ikke invalideres: ' . $updatedPost->get_error_message());
        }

        clean_post_cache($postId);
        do_action('h18_clean_designer_page_saved', $postId, $version, (string) get_post_status($postId));
        DiagnosticStore::append($postId, 'frontend_cache_invalidated', [
            'version' => $version,
            'status' => (string) get_post_status($postId),
            'strategy' => 'wp_update_post+clean_post_cache',
        ]);
    }

'''
if helper_marker not in editor:
    raise SystemExit('Could not find redirect marker for touchFrontendPage helper')
editor = editor.replace(helper_marker, helper + helper_marker, 1)
EDITOR.write_text(editor, encoding='utf-8')

# Version bump.
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.57', ' * Version: 0.1.58', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.57');", "define('H18_CLEAN_VERSION', '0.1.58');", 'runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')

# Technical contract and release documentation.
tech = TECH.read_text(encoding='utf-8')
contract = r'''

## 0.1.58 – Side Designer Gem → frontend synkronisering

### VD-PAGE-SAVE-CACHE-001
- Side Designerens canonical model gemmes fortsat i `_h18_clean_layout_v1`/versionshistorikken; WordPress `post_content` bliver ikke Designer-datakilde.
- Efter en verificerbar Designer-gemning skal den tilhørende WordPress-side touches med `wp_update_post()` og derefter `clean_post_cache()`.
- Touch udføres **efter** Designer-meta og Header/Footer-valg er skrevet, så `post_updated`/`save_post`-baserede host-, plugin- og full-page caches invaliderer den gamle offentlige render og efterfølgende læser den nye canonical model.
- En canonical no-op Gem må også invaliderer frontend-cache. Det gør det muligt at reparere en allerede stale offentlig side uden at oprette en kunstig Designer-version.
- `Gem & vis` skal åbne permalinket med `h18_vd_saved=<version>` som cache-buster for den umiddelbare efterkontrol.
- Restore af en Designer-version skal bruge samme frontend-invalideringsvej.
- Menu-save og navigationens datamodel er uden for denne kontrakt og må ikke ændres af 0.1.58.
'''
if '## 0.1.58 – Side Designer Gem → frontend synkronisering' not in tech:
    tech += contract
TECH.write_text(tech, encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8')
release_notes = '''<h4>0.1.58 – Side Designer Gem → frontend synkronisering</h4><ul><li><strong>BUG-20:</strong> Side Designer → Gem toucher nu WordPress-siden efter den canonical Designer-model er gemt, så <code>save_post</code>/<code>post_updated</code>-baserede caches ser den nye version.</li><li>Der køres desuden <code>clean_post_cache()</code> efter hver Designer-gemning og restore.</li><li>En Gem uden nye layoutændringer invaliderer også frontend-cache, så en stale offentlig side kan repareres uden en falsk ny version.</li><li><strong>Gem &amp; vis</strong> åbner den gemte side med versions-cache-buster.</li><li>Menuadministrationen er ikke ændret i denne release.</li></ul>\n'''
if not notes.startswith('<h4>0.1.58'):
    notes = release_notes + notes
NOTES.write_text(notes, encoding='utf-8')

history_data = json.loads(HISTORY.read_text(encoding='utf-8'))
if isinstance(history_data, dict):
    versions = history_data.setdefault('versions', [])
else:
    raise SystemExit('release-history.json has unexpected top-level format')
if not versions or versions[0].get('version') != '0.1.58':
    versions.insert(0, {
        'version': '0.1.58',
        'date': '2026-08-30',
        'items': [
            'BUG-20: Side Designer Gem invaliderer nu frontend efter canonical meta-save.',
            'wp_update_post køres efter Designer-data er skrevet, så save_post/post_updated cache hooks arbejder på ny state.',
            'clean_post_cache køres ved Gem, canonical no-op Gem og restore.',
            'Gem & vis får h18_vd_saved=<version> cache-buster til umiddelbar verifikation.',
            'Menuadministration og navigation er uændret.'
        ],
    })
HISTORY.write_text(json.dumps(history_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text('''# Visual Designer Manager 0.1.58 status\n\n- BUG-20 / VD-PAGE-SAVE-CACHE-001 implementeret i Side Designerens server-side save-lifecycle.\n- Canonical Designer-model gemmes og verificeres før WordPress-siden touches.\n- `wp_update_post()` udløser standard `post_updated` / `save_post` integrationspunkter efter den nye Designer-state findes.\n- `clean_post_cache()` køres eksplicit bagefter.\n- Canonical no-op Gem invaliderer også frontend-cache.\n- `Gem & vis` bruger `h18_vd_saved=<version>` som cache-buster.\n- Restore invaliderer samme frontend-cachevej.\n- Menu-kode er ikke ændret.\n''', encoding='utf-8')

print('Applied Visual Designer Manager 0.1.58 Side Designer save/frontend synchronization patch.')
