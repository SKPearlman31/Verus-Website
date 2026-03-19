#!/usr/bin/env python3
"""
Verus Basketball — G-League Stats Updater (nba_api)
Fetches G-League player stats from the NBA API.

Runs daily at 6 AM EST via GitHub Actions (1 hour after NBA updater).
Only updates the G-League section of players.json; preserves NBA/college/intl data.
"""

import json
import os
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from nba_api.stats.endpoints import playercareerstats, commonplayerinfo

# ── Configuration ──────────────────────────────────────────────────────────
CURRENT_SEASON = "2025-26"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "players.json")
OUTPUT_JS_PATH = os.path.join(SCRIPT_DIR, "js", "roster-data.js")
HEADSHOT_DIR = os.path.join(SCRIPT_DIR, "images", "players")

NBA_HEADSHOT_URL = "https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"

API_DELAY = 0.5  # seconds between NBA API calls

# ── G-League Roster ────────────────────────────────────────────────────────
GLEAGUE_PLAYERS = [
    {"id": 1630625, "name": "Dalano Banton",   "ig": "_dubberdon"},
    {"id": 1630835, "name": "LJ Figueroa",     "ig": "l_comeup",         "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4397125.png"},
    {"id": 1641746, "name": "Coleman Hawkins",  "ig": "colemanhawkins33", "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4432976.png"},
    {"id": 1642939, "name": "Miles Kelly",      "ig": "miles5kelly"},
    {"id": 1628995, "name": "Kevin Knox",       "ig": "kevinknox"},
    {"id": 1643019, "name": "Gabe Madsen",      "ig": "gabemadsen",      "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4432753.png"},
    {"id": 1630227, "name": "Daishen Nix",      "ig": "djdaishen"},
    {"id": 203506,  "name": "Victor Oladipo",   "ig": "victoroladipo"},
]

# ── G-League team full names ──────────────────────────────────────────────
GLEAGUE_TEAMS = {
    "BIR": "Birmingham Squadron",     "NOB": "Birmingham Squadron",
    "CLF": "Cleveland Charge",
    "CCG": "College Park Skyhawks",
    "DEL": "Delaware Blue Coats",
    "GRG": "Grand Rapids Gold",
    "GRN": "Greensboro Swarm",
    "IWA": "Iowa Wolves",
    "LIN": "Long Island Nets",
    "MNE": "Maine Celtics",
    "MEM": "Memphis Hustle",
    "MXC": "Mexico City Capitanes",
    "MHU": "Motor City Cruise",
    "OKL": "Oklahoma City Blue",
    "ONT": "Ontario Clippers",
    "OSH": "Osceola Magic",
    "RGV": "Rio Grande Valley Vipers",
    "RIP": "Rip City Remix",
    "SLC": "Salt Lake City Stars",
    "SBL": "San Diego Clippers",
    "SCW": "Santa Cruz Warriors",
    "SXF": "Sioux Falls Skyforce",
    "SDQ": "Stockton Kings",
    "TAR": "Raptors 905",
    "TEX": "Texas Legends",
    "WAC": "Capital City Go-Go",
    "WCB": "Westchester Knicks",
    "WIS": "Wisconsin Herd",
    "WBB": "Windy City Bulls",
}

# ───────────────────────────────────────────────────────────────────────────
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def download_file(url, dest):
    """Download a file, handling SSL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            with open(dest, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ⚠ Download failed ({url}): {e}")
        return False


def slug(name):
    return (
        name.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace("é", "e")
        .replace(".", "")
    )


def retry(fn, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if attempt < retries - 1:
                wait = delay * (attempt + 1)
                print(f"    ↻ Retry {attempt + 1}/{retries - 1} in {wait}s... ({e})")
                time.sleep(wait)
            else:
                raise


def fetch_nba_player_info(player_id):
    """Get player bio from CommonPlayerInfo."""
    info = commonplayerinfo.CommonPlayerInfo(player_id=str(player_id), timeout=60)
    rs = info.get_dict()["resultSets"]
    bio = dict(zip(rs[0]["headers"], rs[0]["rowSet"][0]))
    return {
        "display_name": bio["DISPLAY_FIRST_LAST"],
        "position": bio.get("POSITION", ""),
    }


def fetch_gleague_stats(player_id):
    """Get G-League per-game averages. Combines regular + showcase seasons."""
    kwargs = {"player_id": str(player_id), "per_mode36": "PerGame", "timeout": 60, "league_id_nullable": "20"}
    career = playercareerstats.PlayerCareerStats(**kwargs)
    result_sets = career.get_dict()["resultSets"]

    def find_season_row(rs_name):
        for rs in result_sets:
            if rs["name"] == rs_name:
                headers = rs["headers"]
                rows = [
                    dict(zip(headers, row))
                    for row in rs["rowSet"]
                    if row[headers.index("SEASON_ID")] == CURRENT_SEASON
                ]
                if rows:
                    return rows[-1]
        return None

    reg = find_season_row("SeasonTotalsRegularSeason")
    show = find_season_row("SeasonTotalsShowcaseSeason")

    if reg and show:
        reg_gp, show_gp = reg["GP"], show["GP"]
        total_gp = reg_gp + show_gp
        if total_gp > 0:
            return {
                "ppg": round((reg["PTS"] * reg_gp + show["PTS"] * show_gp) / total_gp, 1),
                "rpg": round((reg["REB"] * reg_gp + show["REB"] * show_gp) / total_gp, 1),
                "apg": round((reg["AST"] * reg_gp + show["AST"] * show_gp) / total_gp, 1),
                "fg_pct": round((reg["FG_PCT"] * reg_gp + show["FG_PCT"] * show_gp) / total_gp * 100, 1),
                "gp": total_gp,
                "team_abbr": reg["TEAM_ABBREVIATION"],
            }

    if reg:
        return {
            "ppg": round(reg["PTS"], 1),
            "rpg": round(reg["REB"], 1),
            "apg": round(reg["AST"], 1),
            "fg_pct": round(reg["FG_PCT"] * 100, 1),
            "gp": reg["GP"],
            "team_abbr": reg["TEAM_ABBREVIATION"],
        }
    return None


def process_gleague_players():
    """Fetch G-League player data sequentially (rate-limited API)."""
    print("═══ G-LEAGUE PLAYERS ═══")
    results = []
    headshot_tasks = []

    for entry in GLEAGUE_PLAYERS:
        pid = entry["id"]
        print(f"  {entry['name']} (ID {pid})...")
        try:
            # Get bio info
            try:
                info = retry(lambda pid=pid: fetch_nba_player_info(pid))
                time.sleep(API_DELAY)
            except Exception:
                info = None

            # Get G-League stats
            stats = retry(lambda pid=pid: fetch_gleague_stats(pid))
            time.sleep(API_DELAY)

            gl_team_abbr = stats["team_abbr"] if stats else ""
            gl_team_name = GLEAGUE_TEAMS.get(gl_team_abbr, gl_team_abbr)

            display_name = entry["name"]
            position = entry.get("position", "Forward")
            if info:
                display_name = info["display_name"] if info["display_name"].strip() else entry["name"]
                position = info["position"] or position

            headshot_file = f"{slug(entry['name'])}.png"
            nba_url = NBA_HEADSHOT_URL.format(player_id=pid)
            headshot_tasks.append((nba_url, os.path.join(HEADSHOT_DIR, headshot_file)))

            player = {
                "id": pid,
                "name": display_name,
                "position": position,
                "team": gl_team_name,
                "team_abbr": gl_team_abbr,
                "headshot_nba": nba_url,
                "headshot_local": f"images/players/{headshot_file}",
                "ig": entry.get("ig", ""),
                "stats": stats,
                "_espn_photo": entry.get("espn_photo"),
            }
            results.append(player)
            stat_line = f"{stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG" if stats else "No stats"
            print(f"    → {position} — {gl_team_name} | {stat_line}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # Download headshots in parallel
    print("  Downloading headshots...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda t: download_file(*t), headshot_tasks))

    # ESPN fallback for small headshots
    for player in results:
        espn_photo = player.pop("_espn_photo", None)
        if espn_photo:
            dest = os.path.join(HEADSHOT_DIR, f"{slug(player['name'])}.png")
            try:
                if os.path.exists(dest) and os.path.getsize(dest) < 50_000:
                    download_file(espn_photo, dest)
            except Exception:
                pass

    results.sort(key=lambda p: (p.get("team") or "zzz").lower())
    return results


def push_to_wordpress(data):
    """POST stats data to WordPress REST API. Non-fatal on failure."""
    site_url = os.environ.get("VERUS_SITE_URL", "").rstrip("/")
    api_key = os.environ.get("VERUS_STATS_API_KEY", "")
    if not site_url or not api_key:
        print("\n⚠ VERUS_SITE_URL or VERUS_STATS_API_KEY not set — skipping WordPress push")
        return
    endpoint = f"{site_url}/wp-json/verus/v1/update-stats"
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(endpoint, data=payload, headers={
        "Content-Type": "application/json",
        "X-Verus-Key": api_key,
        "User-Agent": "VerusGLeagueUpdater/1.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"\n✓ WordPress updated: {result.get('message', 'OK')}")
    except Exception as e:
        print(f"\n⚠ WordPress push failed (non-fatal): {e}")


def main():
    start = time.time()
    print(f"Verus G-League Stats Updater — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Season: {CURRENT_SEASON}\n")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    os.makedirs(HEADSHOT_DIR, exist_ok=True)

    # Fetch G-League stats
    gleague = process_gleague_players()

    # Load existing data to preserve NBA/college/intl
    existing = {}
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            existing = json.load(f)

    # Merge: use new G-League data, preserve everything else
    output = {
        "updated": datetime.now().isoformat(),
        "season": CURRENT_SEASON,
        "nba": existing.get("nba", []),
        "gleague": gleague,
        "college": existing.get("college", []),
        "international": existing.get("international", []),
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_JS_PATH, "w") as f:
        f.write("// Auto-generated — do not edit manually\n")
        f.write("var ROSTER_DATA = ")
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write(";\n")

    total = len(output["nba"]) + len(gleague) + len(output["college"]) + len(output["international"])
    elapsed = time.time() - start
    print(f"\nDone — {total} players ({len(output['nba'])} NBA, {len(gleague)} G-League, {len(output['college'])} College/NIL, {len(output['international'])} Intl)")
    print(f"Completed in {elapsed:.1f}s")

    push_to_wordpress(output)


if __name__ == "__main__":
    main()
