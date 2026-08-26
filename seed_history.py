"""
Načte ručně zapsané hodnoty z manual_entries.json do databáze.

Spouští se automaticky přes GitHub Actions pokaždé, když se
manual_entries.json změní. Dá se spustit i ručně:

    python seed_history.py

Opakované spuštění nevadí - stejné datum u stejného účtu se přepíše,
duplicity nevzniknou. Hodnoty stažené automatikou se tím nepřepíšou,
pokud pro dané datum v manual_entries.json nic není.
"""
import json
import sys
from pathlib import Path

import db

ENTRIES_PATH = Path(__file__).parent / "manual_entries.json"
CONFIG_PATH = Path(__file__).parent / "config.json"


def account_types():
    """Typ účtu (own/foreign) načte z config.json, ať to sedí na jednom místě."""
    types = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        for acc in cfg.get("accounts", []):
            types[acc["username"]] = acc.get("type", "foreign")
    return types


def main():
    if not ENTRIES_PATH.exists():
        print("manual_entries.json neexistuje, není co načítat.")
        return

    with open(ENTRIES_PATH, encoding="utf-8") as f:
        entries = json.load(f)

    db.init_db()
    types = account_types()

    total = 0
    for snapshot_date in sorted(entries.keys()):
        values = entries[snapshot_date]
        for username, vals in values.items():
            if isinstance(vals, dict):
                followers = vals.get("followers")
                posts = vals.get("posts")
            else:
                followers, posts = vals, None

            if followers is None:
                print(f"[PŘESKOČENO] {snapshot_date} {username}: chybí followers")
                continue

            db.ensure_account(username, types.get(username, "foreign"))
            db.insert_snapshot(username, int(followers), snapshot_date,
                               posts=int(posts) if posts is not None else None)
            total += 1

    print(f"Načteno {total} ručně zapsaných záznamů.")


if __name__ == "__main__":
    main()
