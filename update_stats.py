#!/usr/bin/env python3
"""
Verus Basketball — Daily Stats Updater
Fetches live player stats from the NBA API (NBA + G-League) and ESPN (college),
downloads headshots, and writes data/players.json for the website.

Run daily via cron:
  0 8 * * * cd /Users/admin/Desktop/Verus_Website && python3 update_stats.py

Or manually:
  python3 update_stats.py
"""

import json
import os
import ssl
import time
import urllib.request
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

# ── NBA Roster ─────────────────────────────────────────────────────────────
# espn_id = ESPN athlete ID used to fetch stats from ESPN's public API
NBA_PLAYERS = [
    {"id": 1630625, "espn_id": 4397885, "name": "Dalano Banton",   "ig": "_dubberdon",   "gleague_stats": True},
    {"id": 1631217, "espn_id": 4433249, "name": "Moussa Diabaté",   "ig": "m0ussadiabate"},
    {"id": 1642352, "espn_id": 4431786, "name": "Keshad Johnson",   "ig": "kj_showtime0"},
    {"id": 1642939, "espn_id": 4696317, "name": "Miles Kelly",       "ig": "miles5kelly",  "gleague_stats": True},
    {"id": 1630228, "espn_id": 4433247, "name": "Jonathan Kuminga",  "ig": "jonathan_kuminga"},
    {"id": 1630544, "espn_id": 4432819, "name": "Tre Mann",          "ig": "treshaunmann"},
    {"id": 1631169, "espn_id": 4687718, "name": "Josh Minott",       "ig": "jday.8"},
    {"id": 1641803, "espn_id": 4592965, "name": "Tristen Newton",    "ig": "tristenewton", "gleague_stats": True},
    {"id": 1641772, "espn_id": 5106268, "name": "Nae'Qwan Tomlin",   "ig": "nae_ratty"},
]

# ── G-League Roster ────────────────────────────────────────────────────────
# espn_photo_url = fallback headshot from ESPN for players with placeholder NBA CDN images
GLEAGUE_PLAYERS = [
    {"id": 1630835, "name": "LJ Figueroa",     "ig": "l_comeup",         "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4397125.png"},
    {"id": 1641746, "name": "Coleman Hawkins",  "ig": "colemanhawkins33", "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4432976.png"},
    {"id": 1628995, "name": "Kevin Knox",       "ig": "kevinknox"},
    {"id": 1643019, "name": "Gabe Madsen",      "ig": "gabemadsen",      "espn_photo": "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/4432753.png"},
    {"id": 1630227, "name": "Daishen Nix",      "ig": "djdaishen"},
    {"id": 203506,  "name": "Victor Oladipo",   "ig": "victoroladipo"},
    {"id": 1641771, "name": "Jalen Slawson",    "ig": "jalenslawson"},
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
    {"name": "Kayden Allen",       "commitment": "Cincinnati",   "position": "Guard",   "ig": "kaydenallennn",     "photo": "images/players/kayden-allen.jpg"},
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
    {"name": "Brandon Goodwin",  "position": "Guard",   "team": "Shanghai Sharks",         "league": "CBA",                   "ig": "toughlay",       "photo": "images/players/brandon-goodwin.png"},
    {"name": "Jakarr Sampson",   "position": "Forward", "team": "Zhejiang Guangsha Lions", "league": "CBA",                   "ig": "karrsampson14",  "photo": "images/players/jakarr-sampson.png"},
    {"name": "Kobi Simmons",     "position": "Guard",   "team": "Saski Baskonia",          "league": "Liga ACB / EuroLeague", "ig": "kobi_simmons2",  "photo": "images/players/kobi-simmons.png"},
]

# ───────────────────────────────────────────────────────────────────────────
# SSL context for downloads (macOS certificate issue workaround)
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


def fetch_nba_player_info(player_id):
    """Get player bio from CommonPlayerInfo (used for G-League players)."""
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


# ── ESPN NBA helpers (more reliable than nba_api in CI environments) ──────

ESPN_NBA_BIO_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{espn_id}"
ESPN_NBA_STATS_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{espn_id}/stats"


def fetch_espn_nba_player_info(espn_id):
    """Get player bio from ESPN's public NBA API."""
    data = fetch_json(ESPN_NBA_BIO_URL.format(espn_id=espn_id))
    athlete = data.get("athlete", data)
    team = athlete.get("team", {})
    pos = athlete.get("position", {})
    team_location = team.get("location", "")
    team_name = team.get("name", "")
    return {
        "display_name": athlete.get("displayName", ""),
        "position": pos.get("abbreviation", ""),
        "team_city": team_location,
        "team_name": team_name,
        "team_full": team.get("displayName", "") or (f"{team_location} {team_name}".strip() if team_location else "Free Agent"),
        "jersey": athlete.get("jersey", ""),
    }


def fetch_espn_nba_stats(espn_id):
    """Fetch current-season NBA stats from ESPN's public API."""
    data = fetch_json(ESPN_NBA_STATS_URL.format(espn_id=espn_id))
    current_year = int(CURRENT_SEASON.split("-")[0]) + 1  # "2025-26" → 2026

    # Find the "averages" category
    for cat in data.get("categories", []):
        if cat.get("name") != "averages":
            continue
        names = cat.get("names", [])

        # Build a name→index mapping for dynamic lookup
        idx = {n: i for i, n in enumerate(names)}

        # Find the entry for the current season
        for entry in cat.get("statistics", []):
            season = entry.get("season", {})
            if season.get("year") == current_year:
                row = entry["stats"]
                return {
                    "ppg": float(row[idx["avgPoints"]]) if "avgPoints" in idx else 0.0,
                    "rpg": float(row[idx["avgRebounds"]]) if "avgRebounds" in idx else 0.0,
                    "apg": float(row[idx["avgAssists"]]) if "avgAssists" in idx else 0.0,
                    "fg_pct": float(row[idx["fieldGoalPct"]]) if "fieldGoalPct" in idx else 0.0,
                    "gp": int(row[idx["gamesPlayed"]]) if "gamesPlayed" in idx else 0,
                }

        # Fallback: use the most recent season if current not found
        if cat.get("statistics"):
            last = cat["statistics"][-1]
            row = last["stats"]
            return {
                "ppg": float(row[idx["avgPoints"]]) if "avgPoints" in idx else 0.0,
                "rpg": float(row[idx["avgRebounds"]]) if "avgRebounds" in idx else 0.0,
                "apg": float(row[idx["avgAssists"]]) if "avgAssists" in idx else 0.0,
                "fg_pct": float(row[idx["fieldGoalPct"]]) if "fieldGoalPct" in idx else 0.0,
                "gp": int(row[idx["gamesPlayed"]]) if "gamesPlayed" in idx else 0,
            }
    return None


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

    # Combine regular + showcase if both exist (full G-League season)
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

    # Regular season only (fallback)
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
        # Season Averages is the first category
        cat = data["categories"][0]
        labels = cat["labels"]
        # Find the entry matching the current season year (2026 for 2025-26)
        current_year = int(CURRENT_SEASON.split("-")[0]) + 1  # "2025-26" → 2026
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
        # Fallback: use the last entry
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
    """Fetch and return NBA player data using ESPN API, sorted by team city."""
    print("═══ NBA PLAYERS (via ESPN) ═══")
    results = []
    for entry in NBA_PLAYERS:
        pid = entry["id"]
        espn_id = entry["espn_id"]
        print(f"  {entry['name']} (NBA {pid} / ESPN {espn_id})...")
        try:
            info = fetch_espn_nba_player_info(espn_id)
            time.sleep(0.6)
            stats = fetch_espn_nba_stats(espn_id)
            time.sleep(0.6)

            # Also fetch G-League stats via nba_api if flagged
            gl_stats = None
            if entry.get("gleague_stats"):
                try:
                    gl_stats = fetch_nba_stats(pid, league_id="20")
                    time.sleep(0.6)
                except Exception as gl_err:
                    print(f"    ⚠ G-League stats unavailable: {gl_err}")

            headshot_file = f"{slug(entry['name'])}.png"
            download_file(
                NBA_HEADSHOT_URL.format(player_id=pid),
                os.path.join(HEADSHOT_DIR, headshot_file),
            )

            player = {
                "id": pid,
                "name": info["display_name"],
                "position": info["position"],
                "team": info["team_full"],
                "team_city": info["team_city"],
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

    # Sort by team city alphabetically
    results.sort(key=lambda p: (p.get("team_city") or "zzz").lower())
    return results


def process_gleague_players():
    """Fetch and return G-League player data, sorted by team city."""
    print("\n═══ G-LEAGUE PLAYERS ═══")
    results = []
    for entry in GLEAGUE_PLAYERS:
        pid = entry["id"]
        print(f"  {entry['name']} (ID {pid})...")
        try:
            # Get bio info (may fail for G-League-only players)
            try:
                info = fetch_nba_player_info(pid)
                time.sleep(0.6)
            except Exception:
                info = None

            # Get G-League stats (league_id='20')
            season_override = entry.get("season")
            stats = fetch_nba_stats(pid, league_id="20", season=season_override)
            time.sleep(0.6)

            # Resolve G-League team name from abbreviation
            gl_team_abbr = stats["team_abbr"] if stats else ""
            gl_team_name = GLEAGUE_TEAMS.get(gl_team_abbr, entry.get("team_fallback", gl_team_abbr))

            headshot_file = f"{slug(entry['name'])}.png"
            # Try NBA CDN first; if an ESPN fallback is configured, also download that
            nba_url = NBA_HEADSHOT_URL.format(player_id=pid)
            download_file(nba_url, os.path.join(HEADSHOT_DIR, headshot_file))
            espn_photo = entry.get("espn_photo")
            if espn_photo:
                dest = os.path.join(HEADSHOT_DIR, headshot_file)
                # If the NBA CDN file is suspiciously small (<50KB), replace with ESPN photo
                if os.path.getsize(dest) < 50_000:
                    download_file(espn_photo, dest)

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
            }
            results.append(player)
            stat_line = f"{stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG" if stats else "No current stats"
            print(f"    → {player['position']} — {gl_team_name} | {stat_line}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # Sort by team name (city) alphabetically
    results.sort(key=lambda p: (p.get("team") or "zzz").lower())
    return results


def process_college_players():
    """Fetch and return college player data, sorted by school."""
    print("\n═══ COLLEGE & NIL PLAYERS ═══")
    results = []

    for entry in COLLEGE_PLAYERS:
        eid = entry["espn_id"]
        print(f"  {entry['name']} ({entry['school']})...")
        try:
            stats = fetch_espn_college_stats(eid)
            time.sleep(0.6)

            headshot_file = f"{slug(entry['name'])}.png"
            headshot_url = ESPN_HEADSHOT_URL.format(espn_id=eid)
            download_file(headshot_url, os.path.join(HEADSHOT_DIR, headshot_file))

            player = {
                "name": entry["name"],
                "position": entry["position"],
                "school": entry["school"],
                "type": "college",
                "espn_id": eid,
                "headshot_espn": headshot_url,
                "headshot_local": f"images/players/{headshot_file}",
                "ig": entry.get("ig", ""),
                "stats": stats,
            }
            results.append(player)
            if stats:
                print(f"    → {entry['position']} — {entry['school']} | {stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG")
            else:
                print(f"    → {entry['position']} — {entry['school']} | No stats available")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # High school commits — no stats, photo from 247sports
    print("\n  ── High School Commits ──")
    for entry in HS_PLAYERS:
        print(f"  {entry['name']} → {entry['commitment']} commit")
        player = {
            "name": entry["name"],
            "position": entry["position"],
            "school": f"{entry['commitment']} Commit",
            "type": "highschool",
            "class_year": 2026,
            "commitment": entry["commitment"],
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": None,
        }
        results.append(player)

    # Static college/NIL players (no ESPN stats)
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

    # Sort: college players by school, then HS commits by school
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
    # Sort alphabetically by team name
    results.sort(key=lambda p: p["team"].lower())
    return results


def main():
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

    # Also write an inline JS file so the site works without a server (file:// protocol)
    with open(OUTPUT_JS_PATH, "w") as f:
        f.write("// Auto-generated by update_stats.py — do not edit manually\n")
        f.write("var ROSTER_DATA = ")
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write(";\n")

    total = len(nba) + len(gleague) + len(college) + len(intl)
    print(f"\nWrote {OUTPUT_PATH}")
    print(f"Wrote {OUTPUT_JS_PATH}")
    print(f"Done — {total} players ({len(nba)} NBA, {len(gleague)} G-League, {len(college)} College/NIL, {len(intl)} Intl)")


if __name__ == "__main__":
    main()
