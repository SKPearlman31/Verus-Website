#!/usr/bin/env python3
"""
Verus Basketball — NBA Stats Updater (ESPN)
Fetches NBA player stats and team info from ESPN's public API.
No rate limiting. All requests run in parallel.

Runs daily at 5 AM EST via GitHub Actions.
"""

import json
import os
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────
CURRENT_SEASON = "2025-26"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "players.json")
OUTPUT_JS_PATH = os.path.join(SCRIPT_DIR, "js", "roster-data.js")
HEADSHOT_DIR = os.path.join(SCRIPT_DIR, "images", "players")

NBA_HEADSHOT_URL = "https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png"
ESPN_NBA_STATS_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{espn_id}/stats"
ESPN_NBA_ATHLETE_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{espn_id}"
ESPN_COLLEGE_STATS_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/mens-college-basketball/athletes/{espn_id}/stats"
ESPN_HEADSHOT_URL = "https://a.espncdn.com/i/headshots/mens-college-basketball/players/full/{espn_id}.png"

# stats.nba.com for G-League stats (LeagueID=20)
NBA_STATS_CAREER_URL = "https://stats.nba.com/stats/playercareerstats?PlayerID={nba_id}&PerMode=PerGame&LeagueID=20"
NBA_STATS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "Accept": "application/json",
}

# Position abbreviation map
POSITION_MAP = {"F": "Forward", "G": "Guard", "C": "Center", "F-C": "Forward-Center", "G-F": "Guard-Forward"}

# ── NBA Roster (ESPN IDs) ─────────────────────────────────────────────────
NBA_PLAYERS = [
    {"espn_id": 4397885, "nba_id": 1630625, "name": "Dalano Banton",    "ig": "_dubberdon"},
    {"espn_id": 4433249, "nba_id": 1631217, "name": "Moussa Diabaté",   "ig": "m0ussadiabate"},
    {"espn_id": 4431786, "nba_id": 1642352, "name": "Keshad Johnson",   "ig": "kj_showtime0"},
    {"espn_id": 4433247, "nba_id": 1630228, "name": "Jonathan Kuminga",  "ig": "jonathan_kuminga"},
    {"espn_id": 4432819, "nba_id": 1630544, "name": "Tre Mann",          "ig": "treshaunmann"},
    {"espn_id": 4687718, "nba_id": 1631169, "name": "Josh Minott",       "ig": "jday.8"},
    {"espn_id": 4592965, "nba_id": 1641803, "name": "Tristen Newton",    "ig": "tristenewton"},
    {"espn_id": 5106268, "nba_id": 1641772, "name": "Nae'Qwan Tomlin",   "ig": "nae_ratty"},
    {"espn_id": 4398207, "nba_id": 1641771, "name": "Jalen Slawson",     "ig": "jalenslawson"},
]

# ── College / NIL Roster ──────────────────────────────────────────────────
COLLEGE_PLAYERS = [
    {"espn_id": 5101784, "name": "Akai Fleming",           "school": "Georgia Tech",    "position": "Guard",  "ig": "akai.fleming"},
    {"espn_id": 5142608, "name": "Jaiden Glover-Toscano",  "school": "Saint Joseph's",  "position": "Guard",  "ig": "jglove.11"},
    {"espn_id": 4710770, "name": "Meechie Johnson Jr.",    "school": "South Carolina",  "position": "Guard",  "ig": "meechie.1"},
    {"espn_id": 5311849, "name": "Devin Brown",            "school": "Davidson",        "position": "Guard",  "ig": "_devinbrown"},
]

# ── High School Commits (static) ─────────────────────────────────────────
HS_PLAYERS = [
    {"name": "Kayden Allen",       "commitment": "UNCOMMITTED",  "position": "Guard",   "ig": "kaydenallennn",     "photo": "images/players/kayden-allen.jpg"},
    {"name": "Gallagher Placide",  "commitment": "Wake Forest",  "position": "Forward", "ig": "gallagherplacide",  "photo": "images/players/gallagher-placide.jpg"},
    {"name": "Gavin Placide",      "commitment": "Wake Forest",  "position": "Forward", "ig": "gavinplacide",      "photo": "images/players/gavin-placide.jpg"},
    {"name": "Jaron Saulsberry",   "commitment": "Ole Miss",     "position": "Forward", "ig": "guard_upronny",     "photo": "images/players/jaron-saulsberry.jpg"},
]

# ── College/NIL players without ESPN stats (static) ──────────────────────
COLLEGE_STATIC_PLAYERS = [
    {"name": "Kok Yat", "position": "Forward", "school": "", "ig": "tuloww.21", "photo": "images/players/kok-yat.png"},
]

# ── International Roster (static) ────────────────────────────────────────
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


def fetch_json(url):
    """Fetch JSON from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
        return json.loads(resp.read().decode())


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
    """Create a filename-safe slug from a player name."""
    return (
        name.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace("é", "e")
        .replace(".", "")
    )


def fetch_gleague_stats(nba_id):
    """Fetch current-season G-League stats from stats.nba.com. Returns dict or None."""
    try:
        url = NBA_STATS_CAREER_URL.format(nba_id=nba_id)
        req = urllib.request.Request(url, headers=NBA_STATS_HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        reg = show = None
        for rs in data["resultSets"]:
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
                }
        elif reg:
            return {
                "ppg": round(reg["PTS"], 1),
                "rpg": round(reg["REB"], 1),
                "apg": round(reg["AST"], 1),
                "fg_pct": round(reg["FG_PCT"] * 100, 1),
                "gp": reg["GP"],
            }
        return None
    except Exception as e:
        print(f"    ⚠ G-League stats unavailable for {nba_id}: {e}")
        return None


def fetch_espn_nba_player(entry):
    """Fetch a single NBA player's stats and info from ESPN. Returns player dict."""
    espn_id = entry["espn_id"]
    nba_id = entry["nba_id"]

    try:
        # Fetch athlete info (team, position)
        athlete_data = fetch_json(ESPN_NBA_ATHLETE_URL.format(espn_id=espn_id))
        a = athlete_data.get("athlete", {})

        display_name = a.get("displayName", entry["name"])
        pos_abbr = a.get("position", {}).get("abbreviation", "F")
        position = POSITION_MAP.get(pos_abbr, pos_abbr)
        team_info = a.get("team", {})
        team_city = (team_info.get("location") or "").strip()
        team_name = (team_info.get("name") or "").strip()
        team_full = f"{team_city} {team_name}".strip() if team_city else "Free Agent"
        team_abbr = team_info.get("abbreviation", "")

        # Fetch stats
        stats_data = fetch_json(ESPN_NBA_STATS_URL.format(espn_id=espn_id))
        stats = None
        cats = stats_data.get("categories", [])
        if cats:
            labels = cats[0]["labels"]
            current_year = int(CURRENT_SEASON.split("-")[0]) + 1  # "2025-26" → 2026
            for stat_entry in cats[0].get("statistics", []):
                season = stat_entry.get("season", {})
                if season.get("year") == current_year:
                    row = dict(zip(labels, stat_entry["stats"]))
                    stats = {
                        "ppg": float(row.get("PTS", 0)),
                        "rpg": float(row.get("REB", 0)),
                        "apg": float(row.get("AST", 0)),
                        "fg_pct": float(row.get("FG%", 0)),
                        "gp": int(row.get("GP", 0)),
                        "team_abbr": team_abbr,
                    }
                    break
            # Fallback to last season entry
            if not stats and cats[0].get("statistics"):
                last = cats[0]["statistics"][-1]
                row = dict(zip(labels, last["stats"]))
                stats = {
                    "ppg": float(row.get("PTS", 0)),
                    "rpg": float(row.get("REB", 0)),
                    "apg": float(row.get("AST", 0)),
                    "fg_pct": float(row.get("FG%", 0)),
                    "gp": int(row.get("GP", 0)),
                    "team_abbr": team_abbr,
                }

        # Fetch G-League stats (non-fatal)
        gl_stats = fetch_gleague_stats(nba_id)

        headshot_file = f"{slug(entry['name'])}.png"
        player = {
            "id": nba_id,
            "name": display_name,
            "position": position,
            "team": team_full,
            "team_city": team_city,
            "team_abbr": team_abbr,
            "headshot_nba": NBA_HEADSHOT_URL.format(nba_id=nba_id),
            "headshot_local": f"images/players/{headshot_file}",
            "ig": entry.get("ig", ""),
            "stats": stats,
            "gleague_stats": gl_stats,
        }
        stat_line = f"{stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG | {stats['gp']} GP" if stats else "No stats"
        gl_line = f" | GL: {gl_stats['ppg']} PPG {gl_stats['gp']} GP" if gl_stats else ""
        print(f"  {display_name} → {team_full} | {stat_line}{gl_line}")
        return player

    except Exception as e:
        print(f"  ✗ {entry['name']}: {e}")
        return None


def fetch_espn_college_stats(espn_id):
    """Fetch current-season college stats from ESPN."""
    try:
        data = fetch_json(ESPN_COLLEGE_STATS_URL.format(espn_id=espn_id))
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
        print(f"  ⚠ ESPN error for {espn_id}: {e}")
        return None


def process_nba_players():
    """Fetch all NBA players from ESPN in parallel."""
    print("═══ NBA PLAYERS (via ESPN) ═══")
    results = []

    # Fetch all player data in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_espn_nba_player, entry): entry for entry in NBA_PLAYERS}
        for future in as_completed(futures):
            player = future.result()
            if player:
                results.append(player)

    # Download headshots in parallel
    headshot_tasks = [
        (NBA_HEADSHOT_URL.format(nba_id=entry["nba_id"]),
         os.path.join(HEADSHOT_DIR, f"{slug(entry['name'])}.png"))
        for entry in NBA_PLAYERS
    ]
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda t: download_file(*t), headshot_tasks))

    results.sort(key=lambda p: (p.get("team_city") or "zzz").lower())
    return results


def process_college_players():
    """Fetch college stats from ESPN in parallel."""
    print("\n═══ COLLEGE & NIL PLAYERS ═══")
    results = []

    # Fetch ESPN stats in parallel
    espn_stats = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_espn_college_stats, e["espn_id"]): e
            for e in COLLEGE_PLAYERS
        }
        for future in as_completed(futures):
            entry = futures[future]
            espn_stats[entry["espn_id"]] = future.result()

    # Download headshots in parallel
    headshot_tasks = [
        (ESPN_HEADSHOT_URL.format(espn_id=e["espn_id"]),
         os.path.join(HEADSHOT_DIR, f"{slug(e['name'])}.png"))
        for e in COLLEGE_PLAYERS
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda t: download_file(*t), headshot_tasks))

    for entry in COLLEGE_PLAYERS:
        stats = espn_stats.get(entry["espn_id"])
        headshot_file = f"{slug(entry['name'])}.png"
        player = {
            "name": entry["name"],
            "position": entry["position"],
            "school": entry["school"],
            "type": "college",
            "espn_id": entry["espn_id"],
            "headshot_espn": ESPN_HEADSHOT_URL.format(espn_id=entry["espn_id"]),
            "headshot_local": f"images/players/{headshot_file}",
            "ig": entry.get("ig", ""),
            "stats": stats,
        }
        results.append(player)
        if stats:
            print(f"  {entry['name']} → {entry['school']} | {stats['ppg']} PPG | {stats['rpg']} RPG | {stats['apg']} APG")
        else:
            print(f"  {entry['name']} → {entry['school']} | No stats")

    print("\n  ── High School Commits ──")
    for entry in HS_PLAYERS:
        print(f"  {entry['name']} → {entry['commitment']} commit")
        results.append({
            "name": entry["name"],
            "position": entry["position"],
            "school": "UNCOMMITTED" if entry["commitment"] == "UNCOMMITTED" else f"{entry['commitment']} Commit",
            "type": "highschool",
            "class_year": 2026,
            "commitment": entry["commitment"],
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": None,
        })

    for entry in COLLEGE_STATIC_PLAYERS:
        print(f"  {entry['name']} (static)")
        results.append({
            "name": entry["name"],
            "position": entry["position"],
            "school": entry.get("school", ""),
            "type": "college",
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": None,
        })

    results.sort(key=lambda p: (
        0 if p["type"] == "college" else 1,
        (p.get("school") or "zzz").lower(),
    ))
    return results


def process_intl_players():
    """Return international player data (static)."""
    print("\n═══ INTERNATIONAL PLAYERS ═══")
    results = []
    for entry in INTL_PLAYERS:
        print(f"  {entry['name']} — {entry['team']} ({entry['league']})")
        results.append({
            "name": entry["name"],
            "position": entry["position"],
            "team": entry["team"],
            "league": entry["league"],
            "headshot_local": entry.get("photo"),
            "ig": entry.get("ig", ""),
            "stats": entry.get("stats"),
        })
    results.sort(key=lambda p: p["team"].lower())
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
        "User-Agent": "VerusNBAUpdater/1.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"\n✓ WordPress updated: {result.get('message', 'OK')}")
    except Exception as e:
        print(f"\n⚠ WordPress push failed (non-fatal): {e}")


def main():
    import time
    start = time.time()
    print(f"Verus NBA Stats Updater (ESPN) — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Season: {CURRENT_SEASON}\n")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    os.makedirs(HEADSHOT_DIR, exist_ok=True)

    # Fetch NBA stats from ESPN
    nba = process_nba_players()

    # Load existing data to preserve G-League stats
    existing = {}
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            existing = json.load(f)

    # Fetch college + intl (always included)
    college = process_college_players()
    intl = process_intl_players()

    # Merge: use new NBA data, preserve existing G-League data
    output = {
        "updated": datetime.now().isoformat(),
        "season": CURRENT_SEASON,
        "nba": nba,
        "gleague": existing.get("gleague", []),  # preserved from G-League updater
        "college": college,
        "international": intl,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_JS_PATH, "w") as f:
        f.write("// Auto-generated — do not edit manually\n")
        f.write("var ROSTER_DATA = ")
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write(";\n")

    total = len(nba) + len(output["gleague"]) + len(college) + len(intl)
    elapsed = time.time() - start
    print(f"\nDone — {total} players ({len(nba)} NBA, {len(output['gleague'])} G-League, {len(college)} College/NIL, {len(intl)} Intl)")
    print(f"Completed in {elapsed:.1f}s")

    push_to_wordpress(output)


if __name__ == "__main__":
    main()
