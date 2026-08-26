"""
Hlavní měsíční běh. Spustit ručně, přes cron, nebo přes GitHub Actions
(viz .github/workflows/monthly.yml):

    python run_monthly.py

Pro každý účet v config.json stáhne aktuální počet sledujících a uloží
do databáze. Pokud jeden účet selže (např. ban, změna IG, chybný token),
ostatní účty se přesto zpracují dál - chyba se jen vypíše.

Access token a heslo se čtou VÝHRADNĚ z proměnných prostředí
(GRAPH_ACCESS_TOKEN, IG_SCRAPER_PASSWORD) - nikdy z config.json.
"""
import json
import os
import random
import sys
import time
from pathlib import Path

import db
from fetch_own import fetch_own_profile
from fetch_foreign import get_loader, fetch_foreign_profile

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    if not CONFIG_PATH.exists():
        sys.exit(
            "Chybí config.json. Zkopírujte config.example.json na config.json "
            "a vyplňte vlastní údaje."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config()
    db.init_db()

    accounts = config["accounts"]
    own_accounts = [a for a in accounts if a["type"] == "own"]
    foreign_accounts = [a for a in accounts if a["type"] == "foreign"]

    results = []

    # --- Vlastní účty přes Graph API ---
    access_token = os.environ.get("GRAPH_ACCESS_TOKEN", "")
    ig_user_ids = config.get("graph_api", {}).get("ig_user_ids", {})

    if own_accounts and not access_token:
        print("[CHYBA] Chybí proměnná prostředí GRAPH_ACCESS_TOKEN, vlastní účty se přeskočí.")

    for acc in own_accounts:
        username = acc["username"]
        db.ensure_account(username, "own")
        ig_user_id = ig_user_ids.get(username)
        if not ig_user_id or not access_token:
            print(f"[PŘESKOČENO] {username}: chybí ig_user_id nebo access token")
            continue
        try:
            followers, posts = fetch_own_profile(ig_user_id, access_token)
            db.insert_snapshot(username, followers, posts=posts)
            results.append((username, followers, "own"))
            print(f"[OK] {username}: {followers} sledujících, {posts} příspěvků")
        except Exception as e:
            print(f"[CHYBA] {username}: {e}")

    # --- Cizí účty přes Instaloader ---
    if foreign_accounts:
        login_cfg = config.get("instaloader_login", {})
        loader = None
        try:
            loader = get_loader(login_cfg["username"])
        except Exception as e:
            print(f"[CHYBA] Přihlášení scraper účtu selhalo: {e}")

        if loader:
            delay_cfg = config.get("delay_seconds_between_foreign_requests", {"min": 20, "max": 60})
            for i, acc in enumerate(foreign_accounts):
                username = acc["username"]
                db.ensure_account(username, "foreign")
                try:
                    followers, posts = fetch_foreign_profile(loader, username)
                    db.insert_snapshot(username, followers, posts=posts)
                    results.append((username, followers, "foreign"))
                    print(f"[OK] {username}: {followers} sledujících, {posts} příspěvků")
                except Exception as e:
                    print(f"[CHYBA] {username}: {e}")

                # pauza mezi dotazy, aby to nevypadalo jako útok
                if i < len(foreign_accounts) - 1:
                    pause = random.randint(delay_cfg["min"], delay_cfg["max"])
                    time.sleep(pause)

    print(f"\nHotovo. Úspěšně uloženo {len(results)} z {len(accounts)} účtů.")


if __name__ == "__main__":
    main()
