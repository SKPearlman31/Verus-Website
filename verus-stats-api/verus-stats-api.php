<?php
/**
 * Plugin Name: Verus Stats API
 * Plugin URI: https://verusteam.com
 * Description: REST API endpoint for receiving auto-updated player stats from GitHub Actions.
 * Version: 1.0.0
 * Author: Verus Management Team
 * License: Private
 * Text Domain: verus-stats-api
 */

if (!defined('ABSPATH')) {
    exit;
}

// ── Settings Page ────────────────────────────────────────────────────────

add_action('admin_menu', function () {
    add_options_page(
        'Verus Stats',
        'Verus Stats',
        'manage_options',
        'verus-stats',
        'verus_stats_settings_page'
    );
});

add_action('admin_init', function () {
    register_setting('verus_stats_settings', 'verus_stats_api_key');
});

function verus_stats_settings_page() {
    $api_key = get_option('verus_stats_api_key', '');
    $roster_data = get_option('verus_roster_data', null);
    $last_updated = $roster_data && isset($roster_data['updated']) ? $roster_data['updated'] : 'Never';
    $player_count = 0;
    if ($roster_data) {
        foreach (['nba', 'gleague', 'college', 'international'] as $cat) {
            if (isset($roster_data[$cat]) && is_array($roster_data[$cat])) {
                $player_count += count($roster_data[$cat]);
            }
        }
    }
    ?>
    <div class="wrap">
        <h1>Verus Stats Settings</h1>
        <form method="post" action="options.php">
            <?php settings_fields('verus_stats_settings'); ?>
            <table class="form-table">
                <tr>
                    <th scope="row">API Key</th>
                    <td>
                        <input type="text" name="verus_stats_api_key" value="<?php echo esc_attr($api_key); ?>"
                               class="regular-text" readonly>
                        <button type="button" class="button" onclick="verusGenerateKey()">Generate New Key</button>
                        <p class="description">Copy this key to your GitHub repo secret <code>VERUS_STATS_API_KEY</code>.</p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">Last Updated</th>
                    <td><?php echo esc_html($last_updated); ?></td>
                </tr>
                <tr>
                    <th scope="row">Total Players</th>
                    <td><?php echo esc_html($player_count); ?></td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <script>
    function verusGenerateKey() {
        // Use crypto.getRandomValues for a cryptographically secure key
        var arr = new Uint8Array(36);
        crypto.getRandomValues(arr);
        var key = Array.from(arr, function(b) { return b.toString(16).padStart(2, '0'); }).join('').slice(0, 48);
        var input = document.querySelector('input[name="verus_stats_api_key"]');
        input.value = key;
        input.removeAttribute('readonly');
    }
    </script>
    <?php
}

// ── REST API Endpoint ────────────────────────────────────────────────────

add_action('rest_api_init', function () {
    register_rest_route('verus/v1', '/update-stats', [
        'methods' => 'POST',
        'callback' => 'verus_stats_update_callback',
        'permission_callback' => 'verus_stats_check_api_key',
    ]);
});

function verus_stats_check_api_key(WP_REST_Request $request) {
    $provided_key = $request->get_header('X-Verus-Key');
    $stored_key = get_option('verus_stats_api_key', '');

    if (empty($stored_key) || empty($provided_key)) {
        return new WP_Error('unauthorized', 'API key required.', ['status' => 401]);
    }

    if (!hash_equals($stored_key, $provided_key)) {
        return new WP_Error('forbidden', 'Invalid API key.', ['status' => 403]);
    }

    return true;
}

function verus_stats_update_callback(WP_REST_Request $request) {
    $data = $request->get_json_params();

    if (empty($data) || !isset($data['updated'])) {
        return new WP_Error('bad_request', 'Invalid stats data.', ['status' => 400]);
    }

    // Save to wp_options (autoloaded for fast reads)
    update_option('verus_roster_data', $data, true);

    $player_count = 0;
    foreach (['nba', 'gleague', 'college', 'international'] as $cat) {
        if (isset($data[$cat]) && is_array($data[$cat])) {
            $player_count += count($data[$cat]);
        }
    }

    return [
        'success' => true,
        'message' => "Stats updated: {$player_count} players.",
        'updated' => $data['updated'],
    ];
}
