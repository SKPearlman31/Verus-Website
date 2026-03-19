<?php
/**
 * Default template fallback.
 * WordPress requires index.php in every theme.
 * The homepage is served by front-page.php.
 */
get_header();
?>

<section class="section" style="min-height:60vh;display:flex;align-items:center;justify-content:center;text-align:center">
  <div>
    <h1 class="section-title">Page Not Found</h1>
    <p style="color:var(--gray-light);margin-top:20px">
      <a href="<?php echo esc_url(home_url('/')); ?>" style="color:var(--white)">Return to homepage</a>
    </p>
  </div>
</section>

<?php get_footer(); ?>
