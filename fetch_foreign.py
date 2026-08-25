"""
Stahuje počet sledujících u cizích veřejných účtů pomocí knihovny Instaloader.

POZOR: Toto je neoficiální cesta mimo podmínky Instagramu. Riziko:
- dočasné omezení nebo ban přihlášeného 'scraper' účtu,
- Instagram může strukturu bez varování změnit a skript přestane fungovat.

Doporučení pro snížení rizika:
- používejte samostatný 'obětovaný' IG účet, ne svůj hlavní,
- session si uložte a znovupoužívejte (neloguj se pokaždé znovu),
- mezi jednotlivými účty čekejte náhodnou pauzu (viz run_monthly.py),
- nespouštějte to častěji než jednou za měsíc.
"""
import os
from pathlib import Path

import instaloader

SESSION_DIR = Path(__file__).parent / ".sessions"


def get_loader(login_username: str) -> instaloader.Instaloader:
    SESSION_DIR.mkdir(exist_ok=True)
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
    )
    session_file = SESSION_DIR / f"{login_username}.session"

    if session_file.exists():
        L.load_session_from_file(login_username, str(session_file))
    else:
        password_env = os.environ.get("IG_SCRAPER_PASSWORD")
        if not password_env:
            raise RuntimeError(
                "Chybí proměnná prostředí IG_SCRAPER_PASSWORD s heslem k 'scraper' účtu."
            )
        L.login(login_username, password_env)
        L.save_session_to_file(str(session_file))

    return L


def fetch_foreign_followers(loader: instaloader.Instaloader, target_username: str) -> int:
    profile = instaloader.Profile.from_username(loader.context, target_username)
    return profile.followers
