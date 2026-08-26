"""
Jednorázové naplnění historických hodnot, které byly měřeny ručně
před spuštěním automatizace.

Spustit JEDNOU:
    python seed_history.py

Skript je bezpečný i při opakovaném spuštění - stejné datum u stejného
účtu se jen přepíše, nevznikne duplicita.

Počet příspěvků (posts) u těchto historických záznamů není k dispozici,
zůstává prázdný. Naplní se automaticky od prvního běhu workflow.

POZOR: hodnoty u chybikkristof jsou ODHAD (v podkladu bylo jen "19,3 k"),
ne skutečně naměřená čísla. Až bude známé přesné číslo, přepsat zde.
"""
import db

# datum měření -> hodnoty. Měří se vždy 1. den v měsíci.
HISTORY = {
    "2026-07-01": {
        "cmcarchitects": 2085,
        "a8000.cz": 4539,
        "adr_architects": 3227,
        "dam.architekti": 2717,
        "a69_architekti": 2301,
        "qartaarch": 2082,
        "jakub_cigler_architekti": 2053,
        "atelier_ra15": 1623,
        "adns.architekti": 1418,
        "editarchitects": 7580,
        "studio_perspektiv": 5860,
        "ova_architekti": 7060,
        "chybikkristof": 19300,   # ODHAD, ne měřená hodnota - v podkladu jen "19,3 k"
    },
    "2026-08-01": {
        "cmcarchitects": 2117,
        "a8000.cz": 4674,
        "adr_architects": 3236,
        "dam.architekti": 2734,
        "a69_architekti": 2362,
        "qartaarch": 2090,
        "jakub_cigler_architekti": 2073,
        "atelier_ra15": 1687,
        "adns.architekti": 1418,
        "editarchitects": 7621,
        "studio_perspektiv": 6026,
        "ova_architekti": 7083,
        "chybikkristof": 19400,   # ODHAD, ne měřená hodnota - v podkladu jen "19,3 k"
    },
}

TYPES = {"cmcarchitects": "own"}  # vše ostatní je konkurence


def main():
    db.init_db()
    total = 0
    for snapshot_date, values in sorted(HISTORY.items()):
        for username, followers in values.items():
            db.ensure_account(username, TYPES.get(username, "foreign"))
            db.insert_snapshot(username, followers, snapshot_date)
            total += 1
    print(f"Naplněno {total} historických záznamů.")


if __name__ == "__main__":
    main()
