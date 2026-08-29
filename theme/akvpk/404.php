<?php
/**
 * 404 template.
 *
 * @package Hangar18_Base
 */

get_header();
?>
<main id="primary" class="h18-theme-main">
    <div class="h18-base-fallback">
        <h1><?php esc_html_e('Siden blev ikke fundet', 'hangar18-base'); ?></h1>
        <p><?php esc_html_e('Den ønskede side findes ikke eller er blevet flyttet.', 'hangar18-base'); ?></p>
        <p><a href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Tilbage til forsiden', 'hangar18-base'); ?></a></p>
    </div>
</main>
<?php
get_footer();
