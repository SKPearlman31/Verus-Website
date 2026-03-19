<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php if (function_exists('wp_body_open')) { wp_body_open(); } ?>

<!-- NAVIGATION -->
<nav id="navbar">
  <div class="nav-left">
    <a href="#hero"><img src="<?php echo esc_url(get_template_directory_uri()); ?>/images/logo.png" alt="Verus" class="nav-logo"></a>
    <a href="https://www.instagram.com/verusteam/" target="_blank" rel="noopener" class="nav-ig" title="Follow us on Instagram"><svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg></a>
  </div>
  <div class="nav-links" id="navLinks">
    <a href="#mission" onclick="closeNav()">Mission</a>
    <a href="#talent" onclick="closeNav()">Talent</a>
    <a href="#family" onclick="closeNav()">Family</a>
    <a href="#expertise" onclick="closeNav()">Expertise</a>
    <a href="#contact" onclick="closeNav()">Contact</a>
  </div>
  <div class="mobile-toggle" id="mobileToggle" onclick="toggleNav()">
    <span></span><span></span><span></span>
  </div>
</nav>
