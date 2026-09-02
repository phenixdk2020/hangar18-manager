<?php

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
