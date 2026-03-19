<?php
/**
 * Verus Basketball Theme — functions.php
 */

// ── Theme Setup ──────────────────────────────────────────────────────────
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('html5', ['search-form', 'gallery', 'caption']);
});

// ── Vimeo Video ID (change this to your Vimeo video ID) ──────────────────
define('VERUS_VIDEO_URL', '1175204118'); // Vimeo video ID from https://vimeo.com/1175204118

// ── Enqueue Styles & Scripts ─────────────────────────────────────────────
add_action('wp_enqueue_scripts', function () {
    // Google Fonts
    wp_enqueue_style(
        'verus-google-fonts',
        'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@400;600;700&display=swap',
        [],
        null
    );

    // Theme CSS
    wp_enqueue_style(
        'verus-style',
        get_template_directory_uri() . '/css/style.css',
        ['verus-google-fonts'],
        '1.0.0'
    );

    // Main JS
    wp_enqueue_script(
        'verus-main',
        get_template_directory_uri() . '/js/main.js',
        [],
        '1.0.0',
        true // Load in footer
    );

    // Inject themeUrl as a small config object (wp_localize_script is fine for flat data)
    wp_localize_script('verus-main', 'VERUS_WP', [
        'themeUrl' => get_template_directory_uri(),
    ]);

    // Inject ROSTER_DATA as inline script (wp_add_inline_script preserves types/nesting)
    $roster_data = get_option('verus_roster_data', null);
    if ($roster_data) {
        wp_add_inline_script(
            'verus-main',
            'var VERUS_ROSTER = ' . wp_json_encode($roster_data) . ';',
            'before'
        );
    }
});
