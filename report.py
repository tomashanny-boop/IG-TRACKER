"""
Vypíše přehlednou tabulku: účet | aktuální počet | změna oproti minulému záznamu.

Spustit kdykoliv:
    python report.py
"""
import db


def format_delta(delta: int) -> str:
    if delta > 0:
        return f"+{delta}"
    if delta < 0:
        return str(delta)
    return "0"


def main():
    accounts = db.get_all_accounts()
    if not accounts:
        print("Zatím nejsou žádná data. Nejdřív spusťte run_monthly.py.")
        return

    rows = []
    for username, acc_type in accounts:
        history = db.get_latest_two_snapshots(username)
        if not history:
            rows.append((username, acc_type, "-", "-", "-"))
            continue
        latest_date, latest_followers = history[0]
        if len(history) > 1:
            _, prev_followers = history[1]
            delta = latest_followers - prev_followers
            delta_str = format_delta(delta)
        else:
            delta_str = "(první záznam)"
        rows.append((username, acc_type, latest_date, str(latest_followers), delta_str))

    headers = ("Účet", "Typ", "Datum", "Sledující", "Změna")
    widths = [
        max(len(headers[i]), max(len(r[i]) for r in rows)) for i in range(len(headers))
    ]

    def print_row(cols):
        print("  ".join(c.ljust(widths[i]) for i, c in enumerate(cols)))

    print_row(headers)
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print_row(r)


if __name__ == "__main__":
    main()
