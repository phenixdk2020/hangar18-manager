<?php
/**
 * Minimal comments template.
 *
 * @package Hangar18_Base
 */

if (post_password_required()) {
    return;
}

if (have_comments()) :
    ?>
    <div class="h18-base-fallback">
        <h2><?php esc_html_e('Kommentarer', 'hangar18-base'); ?></h2>
        <ol class="comment-list">
            <?php
            wp_list_comments(
                [
                    'style'      => 'ol',
                    'short_ping' => true,
                ]
            );
            ?>
        </ol>
        <?php the_comments_navigation(); ?>
    </div>
    <?php
endif;

if (comments_open()) {
    echo '<div class="h18-base-fallback">';
    comment_form();
    echo '</div>';
}
