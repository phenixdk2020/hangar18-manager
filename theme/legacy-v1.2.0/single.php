<?php
/**
 * Single post template.
 *
 * @package Hangar18_Base
 */

get_header();
?>
<main id="primary" class="h18-theme-main">
    <div class="h18-base-fallback">
    <?php while (have_posts()) : the_post(); ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <h1><?php the_title(); ?></h1>
            <div class="entry-content">
                <?php the_content(); ?>
            </div>
        </article>
    <?php endwhile; ?>
    </div>
</main>
<?php
get_footer();
