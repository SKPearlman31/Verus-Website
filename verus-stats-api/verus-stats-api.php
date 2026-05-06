<?php
/**
 * Plugin Name: Verus Stats API
 * Plugin URI: https://verusteam.com
 * Description: Auto-syncs player stats from GitHub and provides a REST API endpoint for updates.
 * Version: 1.1.0
 * Author: Verus Management Team
 * License: Private
 * Text Domain: verus-stats-api
 */

if (!defined('ABSPATH')) {
    exit;
}

// ── GitHub Raw URL ──────────────────────────────────────────────────────
define('VERUS_GITHUB_RAW_URL', 'https://raw.githubusercontent.com/SKPearlman31/Verus-Website/main/data/players.json');

// ── Cron Schedule ───────────────────────────────────────────────────────

add_filter('cron_schedules', function ($schedules) {
    $schedules['verus_every_6h'] = [
        'interval' => 6 * HOUR_IN_SECONDS,
        'display'  => 'Every 6 hours',
    ];
    return $schedules;
});

register_activation_hook(__FILE__, function () {
    if (!wp_next_scheduled('verus_pull_stats_from_github')) {
        wp_schedule_event(time(), 'verus_every_6h', 'verus_pull_stats_from_github');
    }
});

register_deactivation_hook(__FILE__, function () {
    wp_clear_scheduled_hook('verus_pull_stats_from_github');
});

add_action('verus_pull_stats_from_github', 'verus_sync_from_github');

/**
 * Pull latest players.json from GitHub and update wp_options.
 */
function verus_sync_from_github() {
    $response = wp_remote_get(VERUS_GITHUB_RAW_URL, [
        'timeout'   => 30,
        'headers'   => ['Accept' => 'application/json'],
        'sslverify' => ABSPATH . WPINC . '/certificates/ca-bundle.crt',
    ]);

    if (is_wp_error($response)) {
        error_log('[Verus Stats] GitHub pull failed: ' . $response->get_error_message());
        return ['success' => false, 'message' => $response->get_error_message()];
    }

    $code = wp_remote_retrieve_response_code($response);
    if ($code !== 200) {
        error_log("[Verus Stats] GitHub returned HTTP {$code}");
        return ['success' => false, 'message' => "GitHub returned HTTP {$code}"];
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if (empty($data) || !isset($data['updated'])) {
        error_log('[Verus Stats] Invalid JSON from GitHub');
        return ['success' => false, 'message' => 'Invalid JSON from GitHub'];
    }

    // Check if data actually changed
    $current = get_option('verus_roster_data', null);
    if ($current && isset($current['updated']) && $current['updated'] === $data['updated']) {
        return ['success' => true, 'message' => 'Already up to date.'];
    }

    update_option('verus_roster_data', $data, true);

    $player_count = 0;
    foreach (['nba', 'gleague', 'college', 'international'] as $cat) {
        if (isset($data[$cat]) && is_array($data[$cat])) {
            $player_count += count($data[$cat]);
        }
    }

    return ['success' => true, 'message' => "Synced {$player_count} players from GitHub."];
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

// Handle manual sync
add_action('admin_init', function () {
    if (
        isset($_POST['verus_sync_now']) &&
        check_admin_referer('verus_sync_now_action', 'verus_sync_now_nonce')
    ) {
        $result = verus_sync_from_github();
        $msg = $result['success'] ? $result['message'] : 'Sync failed: ' . $result['message'];
        add_settings_error('verus_stats_settings', 'verus_sync', $msg, $result['success'] ? 'updated' : 'error');
    }
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
    $next_sync = wp_next_scheduled('verus_pull_stats_from_github');
    $next_sync_str = $next_sync ? date('Y-m-d H:i:s T', $next_sync) : 'Not scheduled';
    ?>
    <div class="wrap">
        <h1>Verus Stats Settings</h1>
        <?php settings_errors('verus_stats_settings'); ?>

        <h2>GitHub Sync</h2>
        <table class="form-table">
            <tr>
                <th scope="row">Last Updated</th>
                <td><?php echo esc_html($last_updated); ?></td>
            </tr>
            <tr>
                <th scope="row">Total Players</th>
                <td><?php echo esc_html($player_count); ?></td>
            </tr>
            <tr>
                <th scope="row">Next Auto-Sync</th>
                <td><?php echo esc_html($next_sync_str); ?></td>
            </tr>
            <tr>
                <th scope="row">Sync Now</th>
                <td>
                    <form method="post">
                        <?php wp_nonce_field('verus_sync_now_action', 'verus_sync_now_nonce'); ?>
                        <button type="submit" name="verus_sync_now" value="1" class="button button-primary">
                            Sync from GitHub Now
                        </button>
                        <p class="description">Pull latest roster data from GitHub immediately.</p>
                    </form>
                </td>
            </tr>
        </table>

        <hr>
        <h2>API Settings</h2>
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
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <script>
    function verusGenerateKey() {
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

// ── REST API Endpoint (still works if Cloudflare is bypassed later) ─────

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
