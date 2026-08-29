<?php
/**
 * Page template.
 *
 * Hangar18 Manager stores the managed header/footer and page-specific
 * frontend shell directly in post_content. Therefore this theme does
 * not print an extra title, header, footer or sidebar around the page.
 *
 * @package Hangar18_Base
 */

get_header();
?>
<main id="primary" class="h18-theme-main">
<?php
while (have_posts()) :
    the_post();
    ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class('h18-theme-page'); ?>>
        <div class="h18-theme-entry-content entry-content">
            <?php the_content(); ?>
        </div>
    </article>
    <?php
endwhile;
?>
</main>
<?php
get_footer();
