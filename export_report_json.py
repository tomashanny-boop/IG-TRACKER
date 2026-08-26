"""
Vygeneruje docs/data.json - kompletní historii všech účtů ve formátu,
který čte docs/index.html (webový dashboard na GitHub Pages).

Spouští se automaticky na konci GitHub Actions workflow.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import db

OUTPUT_PATH = Path(__file__).parent / "docs" / "data.json"


def main():
    accounts = db.get_all_accounts()
    result = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "accounts": [],
    }

    for username, acc_type in accounts:
        conn = db.get_connection()
        rows = conn.execute(
            "SELECT snapshot_date, followers, posts FROM snapshots "
            "WHERE username = ? ORDER BY snapshot_date ASC",
            (username,),
        ).fetchall()
        conn.close()

        history = [{"date": r[0], "followers": r[1], "posts": r[2]} for r in rows]
        latest = history[-1]["followers"] if history else None
        delta = None
        if len(history) >= 2:
            delta = history[-1]["followers"] - history[-2]["followers"]

        result["accounts"].append(
            {
                "username": username,
                "type": acc_type,
                "history": history,
                "latest": latest,
                "delta": delta,
            }
        )

    # vlastní účty první, pak podle jména
    result["accounts"].sort(key=lambda a: (a["type"] != "own", a["username"].lower()))

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Zapsáno {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
