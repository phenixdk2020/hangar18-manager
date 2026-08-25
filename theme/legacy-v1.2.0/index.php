<?php
/**
 * Generic fallback template.
 *
 * @package Hangar18_Base
 */

get_header();
?>
<main id="primary" class="h18-theme-main">
    <div class="h18-base-fallback">
    <?php if (have_posts()) : ?>
        <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <?php if (!is_page()) : ?>
                    <h1><?php the_title(); ?></h1>
                <?php endif; ?>
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            </article>
        <?php endwhile; ?>
    <?php else : ?>
        <h1><?php esc_html_e('Intet indhold fundet', 'hangar18-base'); ?></h1>
    <?php endif; ?>
    </div>
</main>
<?php
get_footer();
