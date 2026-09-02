from pathlib import Path
import json

root = Path('.')
plugin_path = root / 'clean/hangar18-manager/hangar18-manager.php'
admin_path = root / 'clean/hangar18-manager/src/Admin/AdminController.php'
transfer_path = root / 'clean/hangar18-manager/src/Admin/PortableTransferController.php'
history_path = root / 'clean/hangar18-manager/release-history.json'
notes_path = root / 'clean-release-notes.html'
release_workflow = root / '.github/workflows/visual-designer-release.yml'

plugin = plugin_path.read_text(encoding='utf-8')
if 'Version: 0.1.85' not in plugin:
    raise SystemExit('Expected v0.1.85 bootstrap before applying v0.1.86')
plugin = plugin.replace('Version: 0.1.85', 'Version: 0.1.86', 1)
plugin = plugin.replace("define('VDM_VERSION', '0.1.85');", "define('VDM_VERSION', '0.1.86');", 1)
plugin = plugin.replace("define('H18_CLEAN_VERSION', '0.1.85');", "define('H18_CLEAN_VERSION', '0.1.86');", 1)
needle = "require_once VDM_DIR . 'src/Admin/PortableTransferController.php';\n"
if needle not in plugin:
    raise SystemExit('PortableTransferController require anchor missing')
plugin = plugin.replace(needle, needle + "require_once VDM_DIR . 'src/Admin/SiteSettingsController.php';\n", 1)
needle = "    \\VisualDesignerManager\\Admin\\PortableTransferController::register();\n"
if needle not in plugin:
    raise SystemExit('PortableTransferController register anchor missing')
plugin = plugin.replace(needle, needle + "    \\VisualDesignerManager\\Admin\\SiteSettingsController::register();\n", 1)
plugin_path.write_text(plugin, encoding='utf-8')

controller = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

final class SiteSettingsController
{
    private const PAGE = 'vdm-site-settings';
    private const SAVE_ACTION = 'vdm_save_site_settings';
    private const NONCE = 'vdm_save_site_settings';
    public const OPTION_ORGANIZATION = 'vdm_organization_name';
    public const OPTION_CONTACT_EMAIL = 'vdm_contact_email';
    public const OPTION_CONTACT_PHONE = 'vdm_contact_phone';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 24);
        add_action('admin_post_' . self::SAVE_ACTION, [self::class, 'save']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function menu(): void
    {
        add_submenu_page(
            AdminController::MENU,
            'Siteindstillinger',
            'Siteindstillinger',
            'manage_options',
            self::PAGE,
            [self::class, 'render']
        );
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('manage_options') || strpos($hook, self::PAGE) === false) {
            return;
        }
        wp_enqueue_media();
        $js = <<<'JS'
(function(){
  function bind(button){
    button.addEventListener('click', function(e){
      e.preventDefault();
      var target = button.getAttribute('data-target');
      var preview = button.getAttribute('data-preview');
      var field = document.getElementById(target);
      var image = document.getElementById(preview);
      if (!field) return;
      var frame = wp.media({title:'Vælg billede', button:{text:'Brug dette billede'}, multiple:false, library:{type:'image'}});
      frame.on('select', function(){
        var item = frame.state().get('selection').first().toJSON();
        field.value = item.id || 0;
        if (image) {
          image.src = (item.sizes && item.sizes.medium ? item.sizes.medium.url : item.url) || '';
          image.style.display = image.src ? 'block' : 'none';
        }
      });
      frame.open();
    });
  }
  document.querySelectorAll('.vdm-site-media-select').forEach(bind);
  document.querySelectorAll('.vdm-site-media-clear').forEach(function(button){
    button.addEventListener('click', function(e){
      e.preventDefault();
      var field = document.getElementById(button.getAttribute('data-target'));
      var image = document.getElementById(button.getAttribute('data-preview'));
      if (field) field.value = '0';
      if (image) { image.removeAttribute('src'); image.style.display = 'none'; }
    });
  });
})();
JS;
        wp_add_inline_script('media-editor', $js);
    }

    public static function render(): void
    {
        self::guard();
        $saved = sanitize_key((string) wp_unslash($_GET['vdm_status'] ?? '')) === 'saved';
        $logoId = absint(get_theme_mod('custom_logo', 0));
        $iconId = absint(get_option('site_icon', 0));
        ?>
        <div class="wrap vdm-site-settings">
            <style>
                .vdm-site-settings .vdm-card{max-width:980px;background:#fff;border:1px solid #dcdcde;border-radius:6px;padding:22px;margin:18px 0;box-sizing:border-box}
                .vdm-site-settings .form-table th{width:220px}.vdm-site-preview{display:block;max-width:220px;max-height:120px;margin:8px 0;border:1px solid #dcdcde;background:#f6f7f7;padding:6px;box-sizing:border-box}
                .vdm-site-settings input.regular-text{width:min(520px,100%)}.vdm-site-readonly{background:#f6f7f7}
            </style>
            <h1>Visual Designer Manager – Siteindstillinger</h1>
            <p>Redigér den grundlæggende site-identitet ét sted. Webstedstitel og slogan svarer til WordPress’ generelle indstillinger og bruges også af temaer, browsermetadata og VDM-eksport.</p>
            <?php if ($saved) : ?><div class="notice notice-success is-dismissible"><p><strong>Siteindstillinger gemt.</strong></p></div><?php endif; ?>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <input type="hidden" name="action" value="<?php echo esc_attr(self::SAVE_ACTION); ?>">
                <?php wp_nonce_field(self::NONCE); ?>
                <div class="vdm-card">
                    <h2>Identitet</h2>
                    <table class="form-table" role="presentation">
                        <tr><th><label for="vdm-site-title">Webstedstitel</label></th><td><input class="regular-text" id="vdm-site-title" name="site_title" type="text" value="<?php echo esc_attr((string) get_option('blogname', '')); ?>"><p class="description">Det er dette felt, der bl.a. kan stå som “My new WordPress installation”.</p></td></tr>
                        <tr><th><label for="vdm-site-tagline">Slogan</label></th><td><input class="regular-text" id="vdm-site-tagline" name="tagline" type="text" value="<?php echo esc_attr((string) get_option('blogdescription', '')); ?>"></td></tr>
                        <tr><th><label for="vdm-organization-name">Virksomhed / forening</label></th><td><input class="regular-text" id="vdm-organization-name" name="organization_name" type="text" value="<?php echo esc_attr((string) get_option(self::OPTION_ORGANIZATION, '')); ?>"><p class="description">VDM-felt til genbrug i templates og fremtidige dynamiske elementer.</p></td></tr>
                        <tr><th><label for="vdm-contact-email">Kontakt-e-mail</label></th><td><input class="regular-text" id="vdm-contact-email" name="contact_email" type="email" value="<?php echo esc_attr((string) get_option(self::OPTION_CONTACT_EMAIL, '')); ?>"></td></tr>
                        <tr><th><label for="vdm-contact-phone">Kontakttelefon</label></th><td><input class="regular-text" id="vdm-contact-phone" name="contact_phone" type="text" value="<?php echo esc_attr((string) get_option(self::OPTION_CONTACT_PHONE, '')); ?>"></td></tr>
                    </table>
                </div>
                <div class="vdm-card">
                    <h2>Logo og site-ikon</h2>
                    <?php self::mediaField('Logo', 'custom_logo_id', $logoId, 'vdm-logo-preview', 'Bruges som WordPress custom logo for det aktive tema.'); ?>
                    <?php self::mediaField('Site-ikon / favicon', 'site_icon_id', $iconId, 'vdm-icon-preview', 'WordPress anbefaler et kvadratisk billede på mindst 512 × 512 px.'); ?>
                </div>
                <div class="vdm-card">
                    <h2>Installation</h2>
                    <table class="form-table" role="presentation">
                        <tr><th>Hjemmeadresse</th><td><input class="regular-text vdm-site-readonly" type="text" readonly value="<?php echo esc_attr(home_url('/')); ?>"><p class="description">Vises kun som reference og ændres ikke her for at undgå at låse sitet ude.</p></td></tr>
                        <tr><th>WordPress-adresse</th><td><input class="regular-text vdm-site-readonly" type="text" readonly value="<?php echo esc_attr(site_url('/')); ?>"></td></tr>
                    </table>
                </div>
                <?php submit_button('Gem Siteindstillinger'); ?>
            </form>
        </div>
        <?php
    }

    public static function save(): void
    {
        self::guard();
        check_admin_referer(self::NONCE);

        update_option('blogname', sanitize_text_field((string) wp_unslash($_POST['site_title'] ?? '')));
        update_option('blogdescription', sanitize_text_field((string) wp_unslash($_POST['tagline'] ?? '')));
        update_option(self::OPTION_ORGANIZATION, sanitize_text_field((string) wp_unslash($_POST['organization_name'] ?? '')));
        update_option(self::OPTION_CONTACT_EMAIL, sanitize_email((string) wp_unslash($_POST['contact_email'] ?? '')));
        update_option(self::OPTION_CONTACT_PHONE, sanitize_text_field((string) wp_unslash($_POST['contact_phone'] ?? '')));

        self::saveImageChoice('custom_logo_id', static function (int $id): void {
            if ($id > 0) { set_theme_mod('custom_logo', $id); } else { remove_theme_mod('custom_logo'); }
        });
        self::saveImageChoice('site_icon_id', static function (int $id): void {
            if ($id > 0) { update_option('site_icon', $id); } else { delete_option('site_icon'); }
        });

        wp_safe_redirect(admin_url('admin.php?page=' . self::PAGE . '&vdm_status=saved'));
        exit;
    }

    private static function saveImageChoice(string $field, callable $save): void
    {
        $id = absint($_POST[$field] ?? 0);
        if ($id > 0 && (!get_post($id) || get_post_type($id) !== 'attachment' || !wp_attachment_is_image($id))) {
            wp_die(esc_html__('Det valgte medie er ikke et gyldigt billede.', 'visual-designer-manager'));
        }
        $save($id);
    }

    private static function mediaField(string $label, string $name, int $id, string $previewId, string $description): void
    {
        $url = $id > 0 ? wp_get_attachment_image_url($id, 'medium') : false;
        echo '<div style="margin:18px 0"><strong>' . esc_html($label) . '</strong>';
        echo '<input type="hidden" id="' . esc_attr($name) . '" name="' . esc_attr($name) . '" value="' . esc_attr((string) $id) . '">';
        echo '<img id="' . esc_attr($previewId) . '" class="vdm-site-preview" ' . (is_string($url) && $url !== '' ? 'src="' . esc_url($url) . '"' : 'style="display:none"') . ' alt="">';
        echo '<p><button type="button" class="button vdm-site-media-select" data-target="' . esc_attr($name) . '" data-preview="' . esc_attr($previewId) . '">Vælg billede</button> ';
        echo '<button type="button" class="button vdm-site-media-clear" data-target="' . esc_attr($name) . '" data-preview="' . esc_attr($previewId) . '">Fjern</button></p>';
        echo '<p class="description">' . esc_html($description) . '</p></div>';
    }

    private static function guard(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Du har ikke rettigheder til at ændre siteindstillinger.', 'visual-designer-manager'));
        }
    }
}
'''
(root / 'clean/hangar18-manager/src/Admin/SiteSettingsController.php').write_text(controller, encoding='utf-8')

admin = admin_path.read_text(encoding='utf-8')
card_anchor = "        self::card('Designer', 'Byg sider med 120-unit / 8-px grid, Undo/Redo og versionshistorik.', self::designerUrl(), 'Åbn Designer');\n"
if card_anchor not in admin:
    raise SystemExit('Dashboard card anchor missing')
site_card = "        self::card('Siteindstillinger', 'Ret webstedstitel, slogan, virksomhed/forening, kontaktoplysninger, logo og site-ikon.', admin_url('admin.php?page=vdm-site-settings'), 'Åbn Siteindstillinger');\n"
admin = admin.replace(card_anchor, card_anchor + site_card, 1)
admin_path.write_text(admin, encoding='utf-8')

transfer = transfer_path.read_text(encoding='utf-8')
site_anchor = "            'settings' => [\n                'showOnFront' => (string) get_option('show_on_front', 'posts'),\n"
if site_anchor not in transfer:
    raise SystemExit('siteData settings anchor missing')
identity = "            'settings' => [\n                'siteIdentity' => [\n                    'siteTitle' => (string) get_option('blogname', ''),\n                    'tagline' => (string) get_option('blogdescription', ''),\n                    'customLogoSourceId' => (int) get_theme_mod('custom_logo', 0),\n                    'siteIconSourceId' => (int) get_option('site_icon', 0),\n                    'organizationName' => (string) get_option(SiteSettingsController::OPTION_ORGANIZATION, ''),\n                    'contactEmail' => (string) get_option(SiteSettingsController::OPTION_CONTACT_EMAIL, ''),\n                    'contactPhone' => (string) get_option(SiteSettingsController::OPTION_CONTACT_PHONE, ''),\n                ],\n                'showOnFront' => (string) get_option('show_on_front', 'posts'),\n"
transfer = transfer.replace(site_anchor, identity, 1)

old = "            $pages = self::readJson($zip, 'pages/pages.json');\n            $templates = self::readJson($zip, 'templates/templates.json');\n"
new = "            $site = self::readJson($zip, 'site.json');\n            $pages = self::readJson($zip, 'pages/pages.json');\n            $templates = self::readJson($zip, 'templates/templates.json');\n"
if old not in transfer:
    raise SystemExit('inspectPackage JSON anchor missing')
transfer = transfer.replace(old, new, 1)
warning_anchor = "            $warnings = [];\n            $sourceSite = (string) ($manifest['sourceSite'] ?? '');\n"
warning_new = "            $warnings = [];\n            $siteSettings = isset($site['settings']) && is_array($site['settings']) ? $site['settings'] : [];\n            if (!isset($siteSettings['siteIdentity']) || !is_array($siteSettings['siteIdentity'])) {\n                $warnings[] = 'Pakken har ikke eksplicit site-identitet (VDM 0.1.85 eller ældre). Målsitets webstedstitel, slogan, logo, site-ikon og VDM-kontaktfelter bevares ved import.';\n            }\n            $sourceSite = (string) ($manifest['sourceSite'] ?? '');\n"
if warning_anchor not in transfer:
    raise SystemExit('inspectPackage warning anchor missing')
transfer = transfer.replace(warning_anchor, warning_new, 1)

old = "            self::applySiteSettings($site, $pageMap);\n"
new = "            self::applySiteSettings($site, $pageMap, $mediaMap);\n"
if old not in transfer:
    raise SystemExit('applySiteSettings call missing')
transfer = transfer.replace(old, new, 1)

old_func = "    /** @param array<string,mixed> $site @param array<int,int> $pageMap */\n    private static function applySiteSettings(array $site, array $pageMap): void\n    {\n        $settings = isset($site['settings']) && is_array($site['settings']) ? $site['settings'] : [];\n        $show = (string) ($settings['showOnFront'] ?? 'posts');\n"
new_func = "    /** @param array<string,mixed> $site @param array<int,int> $pageMap @param array<int,int> $mediaMap */\n    private static function applySiteSettings(array $site, array $pageMap, array $mediaMap): void\n    {\n        $settings = isset($site['settings']) && is_array($site['settings']) ? $site['settings'] : [];\n        $identity = isset($settings['siteIdentity']) && is_array($settings['siteIdentity']) ? $settings['siteIdentity'] : null;\n        if (is_array($identity)) {\n            if (array_key_exists('siteTitle', $identity)) { update_option('blogname', sanitize_text_field((string) $identity['siteTitle'])); }\n            if (array_key_exists('tagline', $identity)) { update_option('blogdescription', sanitize_text_field((string) $identity['tagline'])); }\n            if (array_key_exists('organizationName', $identity)) { update_option(SiteSettingsController::OPTION_ORGANIZATION, sanitize_text_field((string) $identity['organizationName'])); }\n            if (array_key_exists('contactEmail', $identity)) { update_option(SiteSettingsController::OPTION_CONTACT_EMAIL, sanitize_email((string) $identity['contactEmail'])); }\n            if (array_key_exists('contactPhone', $identity)) { update_option(SiteSettingsController::OPTION_CONTACT_PHONE, sanitize_text_field((string) $identity['contactPhone'])); }\n\n            if (array_key_exists('customLogoSourceId', $identity)) {\n                $sourceLogo = absint($identity['customLogoSourceId']);\n                if ($sourceLogo === 0) {\n                    remove_theme_mod('custom_logo');\n                } elseif (isset($mediaMap[$sourceLogo])) {\n                    set_theme_mod('custom_logo', (int) $mediaMap[$sourceLogo]);\n                }\n            }\n            if (array_key_exists('siteIconSourceId', $identity)) {\n                $sourceIcon = absint($identity['siteIconSourceId']);\n                if ($sourceIcon === 0) {\n                    delete_option('site_icon');\n                } elseif (isset($mediaMap[$sourceIcon])) {\n                    update_option('site_icon', (int) $mediaMap[$sourceIcon]);\n                }\n            }\n        }\n\n        $show = (string) ($settings['showOnFront'] ?? 'posts');\n"
if old_func not in transfer:
    raise SystemExit('applySiteSettings function anchor missing')
transfer = transfer.replace(old_func, new_func, 1)
transfer_path.write_text(transfer, encoding='utf-8')

history = json.loads(history_path.read_text(encoding='utf-8'))
versions = history.get('versions', [])
if not versions or versions[0].get('version') != '0.1.85':
    raise SystemExit('release history is not headed by v0.1.85')
versions.insert(0, {
    'version': '0.1.86',
    'date': '2026-09-02',
    'items': [
        'VDM-SITE-IDENTITY-001: ny Siteindstillinger-side i Visual Designer Manager med webstedstitel, slogan, virksomhed/forening og kontaktoplysninger.',
        'Logo og WordPress site-ikon/favicon kan vælges direkte fra mediebiblioteket og fjernes igen.',
        'Site-identitet eksporteres nu eksplicit i den portable sitepakke og logo/site-ikon remappes via medie-ID ved import.',
        'VDM 0.1.85 og ældre portable pakker overskriver ikke målsitets identitet, fordi de ikke har et eksplicit siteIdentity-afsnit.',
        'Den uploadede 0.1.85-eksport er valideret som schema 1.0 med intakte SHA-256-signaturer og kan bruges som migrationsbackup.'
    ]
})
history['versions'] = versions
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

notes = notes_path.read_text(encoding='utf-8')
section = '<section data-version="0.1.86"><h2>0.1.86</h2><ul><li>Ny <strong>Siteindstillinger</strong>-side med Webstedstitel, Slogan, Virksomhed/forening, Kontakt-e-mail og Kontakttelefon.</li><li>Logo og WordPress site-ikon/favicon kan vælges direkte fra mediebiblioteket.</li><li>Site-identiteten er nu en eksplicit del af den portable VDM-eksport og importerer logo/site-ikon via sikker medie-ID-remapping.</li><li>Gamle 0.1.85-eksporter uden <code>siteIdentity</code> bevarer målsitets identitet ved import, så fx “My new WordPress installation” ikke genindføres utilsigtet.</li></ul></section>\n'
if 'data-version="0.1.86"' not in notes:
    notes_path.write_text(section + notes, encoding='utf-8')

status = '''# Visual Designer Manager v0.1.86 – Siteindstillinger og portabel site-identitet

Status: release candidate

## Leverance

- Ny Manager-side: Siteindstillinger.
- Webstedstitel og slogan redigeres direkte og gemmes i WordPress `blogname` / `blogdescription`.
- Virksomhed/forening, kontakt-e-mail og kontakttelefon gemmes i VDM-navngivne options.
- Logo og site-ikon/favicon vælges via WordPress mediebibliotek.
- Portabel eksport indeholder eksplicit `settings.siteIdentity`.
- Import remapper logo og site-ikon gennem den importerede mediemap.
- VDM 0.1.85 og ældre pakker uden `siteIdentity` bevarer målsitets identitet.
- Den brugerleverede 0.1.85 ZIP er verificeret separat: schema 1.0 og alle manifest-hashes matcher.
'''
(root / 'docs/v0186-status.md').write_text(status, encoding='utf-8')

qa = r'''from pathlib import Path
import json
import re

root = Path('.')
plugin = (root / 'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
controller = (root / 'clean/hangar18-manager/src/Admin/SiteSettingsController.php').read_text(encoding='utf-8')
transfer = (root / 'clean/hangar18-manager/src/Admin/PortableTransferController.php').read_text(encoding='utf-8')

for needle in [
    'Version: 0.1.86',
    "define('VDM_VERSION', '0.1.86');",
    "src/Admin/SiteSettingsController.php",
    r'\VisualDesignerManager\Admin\SiteSettingsController::register();',
]:
    if needle not in plugin:
        raise SystemExit(f'Missing v0.1.86 bootstrap requirement: {needle}')

for needle in [
    "private const PAGE = 'vdm-site-settings';",
    "private const SAVE_ACTION = 'vdm_save_site_settings';",
    "get_option('blogname'",
    "get_option('blogdescription'",
    "update_option('blogname'",
    "update_option('blogdescription'",
    "OPTION_ORGANIZATION = 'vdm_organization_name'",
    "OPTION_CONTACT_EMAIL = 'vdm_contact_email'",
    "OPTION_CONTACT_PHONE = 'vdm_contact_phone'",
    "wp_enqueue_media();",
    "set_theme_mod('custom_logo'",
    "update_option('site_icon'",
    'My new WordPress installation',
]:
    if needle not in controller:
        raise SystemExit(f'Missing SiteSettings requirement: {needle}')

if re.search(r'(?i)(h18|hangar18|clean[_-]|\bclean\b)', controller):
    raise SystemExit('Legacy/site-specific naming leaked into new SiteSettingsController')

for needle in [
    "'siteIdentity' => [",
    "'siteTitle' => (string) get_option('blogname', '')",
    "'tagline' => (string) get_option('blogdescription', '')",
    "'customLogoSourceId' => (int) get_theme_mod('custom_logo', 0)",
    "'siteIconSourceId' => (int) get_option('site_icon', 0)",
    'self::applySiteSettings($site, $pageMap, $mediaMap);',
    'private static function applySiteSettings(array $site, array $pageMap, array $mediaMap): void',
    "isset($settings['siteIdentity'])",
    "set_theme_mod('custom_logo', (int) $mediaMap[$sourceLogo])",
    "update_option('site_icon', (int) $mediaMap[$sourceIcon])",
    'Pakken har ikke eksplicit site-identitet',
]:
    if needle not in transfer:
        raise SystemExit(f'Missing portable identity requirement: {needle}')

apply_start = transfer.find('    private static function applySiteSettings(')
apply_end = transfer.find('    private static function remapValue(', apply_start)
apply_block = transfer[apply_start:apply_end]
if "['source']['name']" in apply_block or "['source'][\"name\"]" in apply_block:
    raise SystemExit('Legacy package source.name must not be used as implicit identity fallback')

history = json.loads((root / 'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
if not history.get('versions') or history['versions'][0].get('version') != '0.1.86':
    raise SystemExit('release-history.json is not headed by v0.1.86')
if 'data-version="0.1.86"' not in (root / 'clean-release-notes.html').read_text(encoding='utf-8'):
    raise SystemExit('v0.1.86 release notes missing')
if not (root / 'docs/v0186-status.md').is_file():
    raise SystemExit('v0.1.86 status document missing')

updater = json.loads((root / 'clean-update.json').read_text(encoding='utf-8'))
if tuple(map(int, updater['version'].split('.'))) < (0, 1, 85):
    raise SystemExit('Updater regressed below v0.1.85')
if tuple(map(int, updater['version'].split('.'))) > (0, 1, 86):
    raise SystemExit('Updater is unexpectedly ahead of candidate')

print('Visual Designer Manager v0.1.86 SITE SETTINGS QA: PASS')
'''
(root / '.github/scripts/v0186_site_settings_qa.py').write_text(qa, encoding='utf-8')

wf = release_workflow.read_text(encoding='utf-8')
qa_call = '          python3 .github/scripts/v0186_site_settings_qa.py\n'
if qa_call not in wf:
    anchor = '          python3 .github/scripts/v0172_gallery_design_qa.py\n'
    if anchor not in wf:
        raise SystemExit('Central release QA insertion anchor missing')
    wf = wf.replace(anchor, anchor + qa_call, 1)
release_workflow.write_text(wf, encoding='utf-8')

print('Applied Visual Designer Manager v0.1.86 site settings candidate')
