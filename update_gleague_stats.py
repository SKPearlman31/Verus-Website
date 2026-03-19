#!/usr/bin/env python3
"""
Verus Basketball — G-League Stats Updater
Fetches G-League player stats directly from stats.nba.com (parallel requests).

Runs daily at 6 AM EST via GitHub Actions (1 hour after NBA updater).
Only updates the G-League section of players.json; preserves NBA/college/intl data.
"""

import json
import os
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

# ── Configuration ──────────────────────────────────────────────────────────
CURRENT_SEASON = "2025-26"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "players.json")
OUTPUT_JS_PATH = os.path.join(SCRIPT_DIR, "js", "roster-data.js")
HEADSHOT_DIR = os.path.join(SCRIPT_DIR, "images", "players")

NBA_HEADSHOT_URL = "https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"

NBA_STATS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "Accept": "application/json",
}

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

# ── NBA → G-League affiliate mapping ─────────────────────────────────────
NBA_TO_GLEAGUE = {
    "ATL": "CCG",   "BOS": "MNE",   "BKN": "LIN",   "CHA": "GRN",
    "CHI": "WBB",   "CLE": "CLF",   "DAL": "TEX",   "DEN": "GRG",
    "DET": "MHU",   "GSW": "SCW",   "HOU": "RGV",   "IND": "IWA",
    "LAC": "SBL",   "LAL": "SLC",   "MEM": "MEM",   "MIA": "SXF",
    "MIL": "WIS",   "MIN": "IWA",   "NOP": "BIR",   "NYK": "WCB",
    "OKC": "OKL",   "ORL": "OSH",   "PHI": "DEL",   "PHX": "RGV",
    "POR": "RIP",   "SAC": "SDQ",   "SAS": "MXC",   "TOR": "TAR",
    "UTA": "SLC",   "WAS": "WAC",
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


def fetch_player_data(entry):
    """Fetch G-League stats and bio for a single player via stats.nba.com."""
    pid = entry["id"]

    # Fetch career stats (G-League = LeagueID 20)
    stats_url = (
        f"https://stats.nba.com/stats/playercareerstats"
        f"?PlayerID={pid}&PerMode=PerGame&LeagueID=20"
    )
    stats_resp = requests.get(stats_url, headers=NBA_STATS_HEADERS, timeout=30)
    stats_resp.raise_for_status()
    stats_data = stats_resp.json()

    # Find current-season rows for regular and showcase
    reg = show = None
    for rs in stats_data["resultSets"]:
        if not rs["rowSet"]:
            continue
        headers = rs["headers"]
        for row in rs["rowSet"]:
            r = dict(zip(headers, row))
            if r.get("SEASON_ID") != CURRENT_SEASON:
                continue
            if rs["name"] == "SeasonTotalsRegularSeason":
                reg = r
            elif rs["name"] == "SeasonTotalsShowcaseSeason":
                show = r

    # Combine regular + showcase (GP-weighted averages)
    stats = None
    if reg and show:
        reg_gp, show_gp = reg["GP"], show["GP"]
        total_gp = reg_gp + show_gp
        if total_gp > 0:
            stats = {
                "ppg": round((reg["PTS"] * reg_gp + show["PTS"] * show_gp) / total_gp, 1),
                "rpg": round((reg["REB"] * reg_gp + show["REB"] * show_gp) / total_gp, 1),
                "apg": round((reg["AST"] * reg_gp + show["AST"] * show_gp) / total_gp, 1),
                "fg_pct": round((reg["FG_PCT"] * reg_gp + show["FG_PCT"] * show_gp) / total_gp * 100, 1),
                "gp": total_gp,
                "team_abbr": reg["TEAM_ABBREVIATION"],
            }
    elif reg:
        stats = {
            "ppg": round(reg["PTS"], 1),
            "rpg": round(reg["REB"], 1),
            "apg": round(reg["AST"], 1),
            "fg_pct": round(reg["FG_PCT"] * 100, 1),
            "gp": reg["GP"],
            "team_abbr": reg["TEAM_ABBREVIATION"],
        }

    # Fetch bio (position, display name, current team)
    bio_url = f"https://stats.nba.com/stats/commonplayerinfo?PlayerID={pid}"
    position = entry.get("position", "Forward")
    display_name = entry["name"]
    bio_team_abbr = ""
    try:
        bio_resp = requests.get(bio_url, headers=NBA_STATS_HEADERS, timeout=15)
        if bio_resp.status_code == 200:
            bio_data = bio_resp.json()
            rs = bio_data["resultSets"][0]
            bio = dict(zip(rs["headers"], rs["rowSet"][0]))
            if bio.get("DISPLAY_FIRST_LAST", "").strip():
                display_name = bio["DISPLAY_FIRST_LAST"]
            if bio.get("POSITION"):
                position = bio["POSITION"]
            bio_team_abbr = bio.get("TEAM_ABBREVIATION", "")
    except Exception:
        pass  # Use defaults from roster config

    # Use bio's current NBA team to find the correct G-League affiliate,
    # since stats may show a previous team from before a trade.
    gl_team_abbr = stats["team_abbr"] if stats else ""
    if bio_team_abbr:
        gl_team_abbr = NBA_TO_GLEAGUE.get(bio_team_abbr, gl_team_abbr)
    gl_team_name = GLEAGUE_TEAMS.get(gl_team_abbr, gl_team_abbr)

    headshot_file = f"{slug(entry['name'])}.png"

    player = {
        "id": pid,
        "name": display_name,
        "position": position,
        "team": gl_team_name,
        "team_abbr": gl_team_abbr,
        "headshot_nba": NBA_HEADSHOT_URL.format(player_id=pid),
        "headshot_local": f"images/players/{headshot_file}",
        "ig": entry.get("ig", ""),
        "stats": stats,
        "_espn_photo": entry.get("espn_photo"),
    }

    stat_line = f"{stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG" if stats else "No stats"
    print(f"  {display_name} — {position} — {gl_team_name} | {stat_line}")
    return player


def process_gleague_players():
    """Fetch all G-League player data in parallel."""
    print("═══ G-LEAGUE PLAYERS ═══")
    results = []

    # Fetch stats + bio in parallel (4 workers to be respectful)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_player_data, e): e for e in GLEAGUE_PLAYERS}
        for future in futures:
            entry = futures[future]
            try:
                player = future.result()
                results.append(player)
            except Exception as e:
                print(f"  ✗ {entry['name']}: {e}")

    # Download headshots in parallel
    headshot_tasks = []
    for player in results:
        headshot_file = f"{slug(player['name'])}.png"
        nba_url = NBA_HEADSHOT_URL.format(player_id=player["id"])
        headshot_tasks.append((nba_url, os.path.join(HEADSHOT_DIR, headshot_file)))

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
