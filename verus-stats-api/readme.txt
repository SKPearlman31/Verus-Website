=== Verus Stats API ===
Contributors: verusteam
Tags: sports, basketball, stats
Requires at least: 5.0
Tested up to: 6.7
Requires PHP: 7.4
Stable tag: 1.0.0
License: Private

REST API endpoint for receiving auto-updated player stats from GitHub Actions.

== Description ==

This plugin provides a secure REST API endpoint that receives player statistics
data from an automated GitHub Actions workflow. Data is stored in the WordPress
database and served to the theme via wp_add_inline_script().

== Installation ==

1. Upload the plugin via Plugins > Add New > Upload.
2. Activate the plugin.
3. Go to Settings > Verus Stats and generate an API key.
4. Copy the API key to your GitHub repo secret (VERUS_STATS_API_KEY).
