#!/usr/bin/env python3
"""
Verus Basketball — Daily Stats Updater
Fetches live player stats from the NBA API (NBA + G-League) and ESPN (college),
downloads headshots, and writes data/players.json for the website.

Speed improvements:
  - Parallel headshot downloads via ThreadPoolExecutor
  - Parallel ESPN college stats fetching
  - Reduced sleep between NBA API calls (0.4s)

Run daily via GitHub Actions or manually:
  python3 update_stats.py
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
ESPN_HEADSHOT_URL = "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/{espn_id}.png"

API_DELAY = 0.4  # seconds between NBA API calls

# ── NBA Roster ─────────────────────────────────────────────────────────────
NBA_PLAYERS = [
    {"id": 1630625, "name": "Dalano Banton",    "ig": "_dubberdon"},
    {"id": 1631217, "name": "Moussa Diabaté",   "ig": "m0ussadiabate"},
    {"id": 1642352, "name": "Keshad Johnson",   "ig": "kj_showtime0"},
    {"id": 1630228, "name": "Jonathan Kuminga",  "ig": "jonathan_kuminga"},
    {"id": 1630544, "name": "Tre Mann",          "ig": "treshaunmann"},
    {"id": 1631169, "name": "Josh Minott",       "ig": "jday.8"},
    {"id": 1641803, "name": "Tristen Newton",    "ig": "tristenewton", "gleague_stats": True},
    {"id": 1641772, "name": "Nae'Qwan Tomlin",   "ig": "nae_ratty"},
    {"id": 1641771, "name": "Jalen Slawson",     "ig": "jalenslawson"},
]

# ── G-League Roster ────────────────────────────────────────────────────────
GLEAGUE_PLAYERS = [
    {"id": 1630835, "name": "LJ Figueroa",     "ig": "l_comeup",         "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4397125.png"},
    {"id": 1641746, "name": "Coleman Hawkins",  "ig": "colemanhawkins33", "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4432976.png"},
    {"id": 1642939, "name": "Miles Kelly",      "ig": "miles5kelly"},
    {"id": 1628995, "name": "Kevin Knox",       "ig": "kevinknox"},
    {"id": 1643019, "name": "Gabe Madsen",      "ig": "gabemadsen",      "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4432753.png"},
    {"id": 1630227, "name": "Daishen Nix",      "ig": "djdaishen"},
]

# ── G-League team full names (NBA API only returns abbreviations) ──────────
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

# ── College / NIL Roster ──────────────────────────────────────────────────
COLLEGE_PLAYERS = [
    {"espn_id": 5101784, "name": "Akai Fleming",           "school": "Georgia Tech",    "position": "Guard",  "ig": "akai.fleming"},
    {"espn_id": 5142608, "name": "Jaiden Glover-Toscano",  "school": "Saint Joseph's",  "position": "Guard",  "ig": "jglove.11"},
    {"espn_id": 4710770, "name": "Meechie Johnson Jr.",    "school": "South Carolina",  "position": "Guard",  "ig": "meechie.1"},
    {"espn_id": 5311849, "name": "Devin Brown",            "school": "Davidson",        "position": "Guard",  "ig": "_devinbrown"},
]

# ── High School Commits (static — no stats) ───────────────────────────────
HS_PLAYERS = [
    {"name": "Kayden Allen",       "commitment": "UNCOMMITTED",  "position": "Guard",   "ig": "kaydenallennn",     "photo": "images/players/kayden-allen.jpg"},
    {"name": "Gallagher Placide",  "commitment": "Wake Forest",  "position": "Forward", "ig": "gallagherplacide",  "photo": "images/players/gallagher-placide.jpg"},
    {"name": "Gavin Placide",      "commitment": "Wake Forest",  "position": "Forward", "ig": "gavinplacide",      "photo": "images/players/gavin-placide.jpg"},
    {"name": "Jaron Saulsberry",   "commitment": "Ole Miss",     "position": "Forward", "ig": "guard_upronny",     "photo": "images/players/jaron-saulsberry.jpg"},
]

# ── College/NIL players without ESPN stats (static) ─────────────────────────
COLLEGE_STATIC_PLAYERS = [
    {"name": "Kok Yat", "position": "Forward", "school": "", "ig": "tuloww.21", "photo": "images/players/kok-yat.png"},
]

# ── International Roster ───────────────────────────────────────────────────
INTL_PLAYERS = [
    {"name": "Kamar Baldwin",    "position": "Guard",   "team": "FC Bayern Munich",       "league": "BBL / EuroLeague",      "ig": "kamar_baldwin",  "photo": "images/players/kamar-baldwin.png"},
    {"name": "Kaiser Gates",     "position": "Forward", "team": "UCAM Murcia",             "league": "Liga ACB",              "ig": "kaiserg_22",     "photo": "images/players/kaiser-gates.png"},
    {"name": "Jakarr Sampson",   "position": "Forward", "team": "Zhejiang Guangsha Lions", "league": "CBA",                   "ig": "karrsampson14",  "photo": "images/players/jakarr-sampson.png"},
    {"name": "Kobi Simmons",     "position": "Guard",   "team": "Saski Baskonia",          "league": "Liga ACB / EuroLeague", "ig": "kobi_simmons2",  "photo": "images/players/kobi-simmons.png"},
]

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


def download_headshots_parallel(tasks):
    """Download multiple headshots in parallel. tasks = list of (url, dest) tuples."""
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(download_file, url, dest): (url, dest) for url, dest in tasks}
        for future in as_completed(futures):
            future.result()


def fetch_json(url):
    """Fetch JSON from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        return json.loads(resp.read().decode())


def slug(name):
    """Create a filename-safe slug from a player name."""
    return (
        name.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace("é", "e")
        .replace(".", "")
    )


def retry(fn, retries=3, delay=2):
    """Retry a function up to `retries` times with exponential backoff."""
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
    team_city = bio.get("TEAM_CITY", "").strip()
    team_name = bio.get("TEAM_NAME", "").strip()
    return {
        "display_name": bio["DISPLAY_FIRST_LAST"],
        "position": bio.get("POSITION", ""),
        "team_city": team_city,
        "team_name": team_name,
        "team_full": f"{team_city} {team_name}".strip() if team_city else "Free Agent",
        "team_abbr": bio.get("TEAM_ABBREVIATION", ""),
        "jersey": bio.get("JERSEY", ""),
    }


def fetch_nba_stats(player_id, league_id=None, season=None):
    """Get per-game averages for a given season. Use league_id='20' for G-League.
    For G-League, combines regular season + tip-off tournament (showcase) stats."""
    target_season = season or CURRENT_SEASON
    kwargs = {"player_id": str(player_id), "per_mode36": "PerGame", "timeout": 60}
    if league_id:
        kwargs["league_id_nullable"] = league_id
    career = playercareerstats.PlayerCareerStats(**kwargs)
    result_sets = career.get_dict()["resultSets"]

    def find_season_row(rs_name):
        for rs in result_sets:
            if rs["name"] == rs_name:
                headers = rs["headers"]
                rows = [
                    dict(zip(headers, row))
                    for row in rs["rowSet"]
                    if row[headers.index("SEASON_ID")] == target_season
                ]
                if rows:
                    return rows[-1]  # Use TOT row if multiple teams
        return None

    reg = find_season_row("SeasonTotalsRegularSeason")
    show = find_season_row("SeasonTotalsShowcaseSeason") if league_id == "20" else None

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


def fetch_espn_college_stats(espn_id):
    """Fetch current-season college stats from ESPN's public API."""
    url = f"https://site.web.api.espn.com/apis/common/v3/sports/basketball/mens-college-basketball/athletes/{espn_id}/stats"
    try:
        data = fetch_json(url)
        cat = data["categories"][0]
        labels = cat["labels"]
        current_year = int(CURRENT_SEASON.split("-")[0]) + 1
        for entry in cat.get("statistics", []):
            season = entry.get("season", {})
            if season.get("year") == current_year:
                row = dict(zip(labels, entry["stats"]))
                return {
                    "ppg": float(row.get("PTS", 0)),
                    "rpg": float(row.get("REB", 0)),
                    "apg": float(row.get("AST", 0)),
                    "fg_pct": float(row.get("FG%", 0)),
                    "gp": int(row.get("GP", 0)),
                }
        if cat.get("statistics"):
            last = cat["statistics"][-1]
            row = dict(zip(labels, last["stats"]))
            return {
                "ppg": float(row.get("PTS", 0)),
                "rpg": float(row.get("REB", 0)),
                "apg": float(row.get("AST", 0)),
                "fg_pct": float(row.get("FG%", 0)),
                "gp": int(row.get("GP", 0)),
            }
        return None
    except Exception as e:
        print(f"  ⚠ ESPN API error for {espn_id}: {e}")
        return None


def process_nba_players():
    """Fetch and return NBA player data, sorted by team city."""
    print("═══ NBA PLAYERS ═══")
    results = []
    headshot_tasks = []

    for entry in NBA_PLAYERS:
        pid = entry["id"]
        print(f"  {entry['name']} (ID {pid})...")
        try:
            info = retry(lambda pid=pid: fetch_nba_player_info(pid))
            time.sleep(API_DELAY)
            stats = retry(lambda pid=pid: fetch_nba_stats(pid))
            time.sleep(API_DELAY)

            gl_stats = None
            if entry.get("gleague_stats"):
                gl_stats = retry(lambda pid=pid: fetch_nba_stats(pid, league_id="20"))
                time.sleep(API_DELAY)

            headshot_file = f"{slug(entry['name'])}.png"
            headshot_tasks.append((
                NBA_HEADSHOT_URL.format(player_id=pid),
                os.path.join(HEADSHOT_DIR, headshot_file),
            ))

            player = {
                "id": pid,
                "name": info["display_name"],
                "position": info["position"],
                "team": info["team_full"],
                "team_city": info["team_city"],
                "team_abbr": info["team_abbr"],
                "headshot_nba": NBA_HEADSHOT_URL.format(player_id=pid),
                "headshot_local": f"images/players/{headshot_file}",
                "ig": entry.get("ig", ""),
                "stats": stats,
                "gleague_stats": gl_stats,
            }
            results.append(player)
            stat_line = f"{stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG" if stats else "No current NBA stats"
            gl_line = f" | GL: {gl_stats['ppg']} PPG | {gl_stats['rpg']} RPG | {gl_stats['apg']} APG" if gl_stats else ""
            print(f"    → {info['position']} — {info['team_full']} | {stat_line}{gl_line}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # Download all headshots in parallel (instead of one at a time)
    print("  Downloading headshots...")
    download_headshots_parallel(headshot_tasks)

    results.sort(key=lambda p: (p.get("team_city") or "zzz").lower())
    return results


def process_gleague_players():
    """Fetch and return G-League player data, sorted by team city."""
    print("\n═══ G-LEAGUE PLAYERS ═══")
    results = []
    headshot_tasks = []

    for entry in GLEAGUE_PLAYERS:
        pid = entry["id"]
        print(f"  {entry['name']} (ID {pid})...")
        try:
            try:
                info = retry(lambda pid=pid: fetch_nba_player_info(pid))
                time.sleep(API_DELAY)
            except Exception:
                info = None

            season_override = entry.get("season")
            stats = retry(lambda pid=pid: fetch_nba_stats(pid, league_id="20", season=season_override))
            time.sleep(API_DELAY)

            gl_team_abbr = stats["team_abbr"] if stats else ""
            gl_team_name = GLEAGUE_TEAMS.get(gl_team_abbr, entry.get("team_fallback", gl_team_abbr))

            headshot_file = f"{slug(entry['name'])}.png"
            nba_url = NBA_HEADSHOT_URL.format(player_id=pid)
            headshot_tasks.append((nba_url, os.path.join(HEADSHOT_DIR, headshot_file)))

            display_name = entry["name"]
            position = entry.get("position", "Forward")
            if info:
                display_name = info["display_name"] if info["display_name"].strip() else entry["name"]
                position = info["position"] or position

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
            stat_line = f"{stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG" if stats else "No current stats"
            print(f"    → {player['position']} — {gl_team_name} | {stat_line}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # Download all headshots in parallel
    print("  Downloading headshots...")
    download_headshots_parallel(headshot_tasks)

    # Post-download: check for ESPN fallback replacements
    for player in results:
        espn_photo = player.pop("_espn_photo", None)
        if espn_photo:
            headshot_file = f"{slug(player['name'])}.png"
            dest = os.path.join(HEADSHOT_DIR, headshot_file)
            try:
                if os.path.exists(dest) and os.path.getsize(dest) < 50_000:
                    download_file(espn_photo, dest)
            except Exception:
                pass

    results.sort(key=lambda p: (p.get("team") or "zzz").lower())
    return results


def process_college_players():
    """Fetch and return college player data. ESPN stats fetched in parallel."""
    print("\n═══ COLLEGE & NIL PLAYERS ═══")
    results = []

    # Fetch all ESPN stats in parallel
    espn_stats = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_espn_college_stats, entry["espn_id"]): entry
            for entry in COLLEGE_PLAYERS
        }
        for future in as_completed(futures):
            entry = futures[future]
            try:
                espn_stats[entry["espn_id"]] = future.result()
            except Exception as e:
                print(f"  ⚠ {entry['name']}: {e}")
                espn_stats[entry["espn_id"]] = None

    # Download college headshots in parallel
    headshot_tasks = [
        (ESPN_HEADSHOT_URL.format(espn_id=entry["espn_id"]),
         os.path.join(HEADSHOT_DIR, f"{slug(entry['name'])}.png"))
        for entry in COLLEGE_PLAYERS
    ]
    download_headshots_parallel(headshot_tasks)

    for entry in COLLEGE_PLAYERS:
        eid = entry["espn_id"]
        stats = espn_stats.get(eid)
        headshot_file = f"{slug(entry['name'])}.png"

        player = {
            "name": entry["name"],
            "position": entry["position"],
            "school": entry["school"],
            "type": "college",
            "espn_id": eid,
            "headshot_espn": ESPN_HEADSHOT_URL.format(espn_id=eid),
            "headshot_local": f"images/players/{headshot_file}",
            "ig": entry.get("ig", ""),
            "stats": stats,
        }
        results.append(player)
        if stats:
            print(f"  {entry['name']} → {entry['school']} | {stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG")
        else:
            print(f"  {entry['name']} → {entry['school']} | No stats available")

    print("\n  ── High School Commits ──")
    for entry in HS_PLAYERS:
        print(f"  {entry['name']} → {entry['commitment']} commit")
        player = {
            "name": entry["name"],
            "position": entry["position"],
            "school": "UNCOMMITTED" if entry["commitment"] == "UNCOMMITTED" else f"{entry['commitment']} Commit",
            "type": "highschool",
            "class_year": 2026,
            "commitment": entry["commitment"],
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": None,
        }
        results.append(player)

    for entry in COLLEGE_STATIC_PLAYERS:
        print(f"  {entry['name']} (static)")
        player = {
            "name": entry["name"],
            "position": entry["position"],
            "school": entry.get("school", ""),
            "type": "college",
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": None,
        }
        results.append(player)

    results.sort(key=lambda p: (
        0 if p["type"] == "college" else 1,
        (p.get("school") or "zzz").lower(),
    ))
    return results


def process_intl_players():
    """Return international player data (stats maintained manually)."""
    print("\n═══ INTERNATIONAL PLAYERS ═══")
    results = []
    for entry in INTL_PLAYERS:
        print(f"  {entry['name']} — {entry['team']} ({entry['league']})")
        player = {
            "name": entry["name"],
            "position": entry["position"],
            "team": entry["team"],
            "league": entry["league"],
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": entry.get("stats"),
        }
        results.append(player)
    results.sort(key=lambda p: p["team"].lower())
    return results


def push_to_wordpress(data):
    """POST stats data to the WordPress REST API. Non-fatal on failure."""
    site_url = os.environ.get("VERUS_SITE_URL", "").rstrip("/")
    api_key = os.environ.get("VERUS_STATS_API_KEY", "")

    if not site_url or not api_key:
        print("\n⚠ VERUS_SITE_URL or VERUS_STATS_API_KEY not set — skipping WordPress push")
        return

    endpoint = f"{site_url}/wp-json/verus/v1/update-stats"
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Verus-Key": api_key,
            "User-Agent": "VerusStatsUpdater/2.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"\n✓ WordPress updated: {result.get('message', 'OK')}")
    except Exception as e:
        print(f"\n⚠ WordPress push failed (non-fatal): {e}")


def main():
    start = time.time()
    print(f"Verus Stats Updater — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Season: {CURRENT_SEASON}\n")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    os.makedirs(HEADSHOT_DIR, exist_ok=True)

    nba = process_nba_players()
    gleague = process_gleague_players()
    college = process_college_players()
    intl = process_intl_players()

    output = {
        "updated": datetime.now().isoformat(),
        "season": CURRENT_SEASON,
        "nba": nba,
        "gleague": gleague,
        "college": college,
        "international": intl,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_JS_PATH, "w") as f:
        f.write("// Auto-generated by update_stats.py — do not edit manually\n")
        f.write("var ROSTER_DATA = ")
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write(";\n")

    total = len(nba) + len(gleague) + len(college) + len(intl)
    elapsed = time.time() - start
    print(f"\nWrote {OUTPUT_PATH}")
    print(f"Wrote {OUTPUT_JS_PATH}")
    print(f"Done — {total} players ({len(nba)} NBA, {len(gleague)} G-League, {len(college)} College/NIL, {len(intl)} Intl)")
    print(f"Completed in {elapsed:.1f}s")

    push_to_wordpress(output)


if __name__ == "__main__":
    main()
