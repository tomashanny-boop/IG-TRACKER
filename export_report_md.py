"""
Vygeneruje REPORT.md s tabulkou (stejná data jako report.py, jen jako
Markdown soubor) - aby šel report číst přímo na GitHubu bez spouštění
čehokoliv lokálně.

Spouští se automaticky na konci GitHub Actions workflow.
"""
from datetime import date

import db


def format_delta(delta: int) -> str:
    if delta > 0:
        return f"+{delta}"
    if delta < 0:
        return str(delta)
    return "0"


def main():
    accounts = db.get_all_accounts()
    lines = [
        "# IG Tracker - přehled sledujících",
        "",
        f"_Poslední aktualizace: {date.today().isoformat()}_",
        "",
        "| Účet | Typ | Datum | Sledující | Změna |",
        "|---|---|---|---|---|",
    ]

    for username, acc_type in accounts:
        history = db.get_latest_two_snapshots(username)
        if not history:
            lines.append(f"| {username} | {acc_type} | - | - | - |")
            continue
        latest_date, latest_followers = history[0]
        if len(history) > 1:
            _, prev_followers = history[1]
            delta_str = format_delta(latest_followers - prev_followers)
        else:
            delta_str = "(první záznam)"
        lines.append(
            f"| {username} | {acc_type} | {latest_date} | {latest_followers} | {delta_str} |"
        )

    with open("REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("REPORT.md vygenerován.")


if __name__ == "__main__":
    main()
