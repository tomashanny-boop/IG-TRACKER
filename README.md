# IG Tracker

Sleduje počet sledujících u ~20 Instagram účtů (vlastních i cizích) a
ukládá historii, aby šlo vidět měsíční změnu.

## 1. Instalace

```bash
pip install -r requirements.txt
```

## 2. Nastavení konfigurace

```bash
cp config.example.json config.json
```

Otevřete `config.json` a doplňte:

- **`accounts`** – seznam všech ~20 účtů, u každého `"type": "own"` nebo `"type": "foreign"`.

### Vlastní účty (own) – Meta Graph API, zdarma a stabilní

1. Účet musí být Instagram **Business** nebo **Creator** a propojený
   s Facebook stránkou, kterou spravujete.
2. Jděte na [developers.facebook.com](https://developers.facebook.com),
   vytvořte aplikaci → přidejte produkt "Instagram Graph API".
3. V Graph API Exploreru vygenerujte **dlouhodobý access token**
   (long-lived, ideálně dobu platnosti co nejdéle prodloužit –
   krátkodobé tokeny vyprší za hodinu, dlouhodobé vydrží ~60 dní a dají
   se obnovovat).
4. Zjistěte **IG User ID** vašeho účtu (přes stejný Graph API Explorer,
   dotaz `/me/accounts` → `/{page-id}?fields=instagram_business_account`).
5. Vyplňte `access_token` a `ig_user_ids` v `config.json`.

### Cizí účty (foreign) – Instaloader, zdarma, ale s rizikem

1. Založte si **samostatný, "obětovaný" IG účet** jen pro tohle sledování
   – ne svůj hlavní ani firemní účet. Pokud by ho Instagram omezil,
   nic důležitého tím neztratíte.
2. Nastavte heslo tohoto účtu jako proměnnou prostředí (nikdy ho nedávejte
   do config.json):

   ```bash
   export IG_SCRAPER_PASSWORD="heslo_scraper_uctu"
   ```

3. V `config.json` vyplňte `instaloader_login.username`.
4. Při prvním spuštění se skript přihlásí a uloží session do `.sessions/`,
   takže se příště nebude muset přihlašovat znovu (menší riziko banu).

## 3. Spuštění lokálně (volitelné, pro test)

Měsíční sběr dat:

```bash
export GRAPH_ACCESS_TOKEN="váš_token"
export IG_SCRAPER_PASSWORD="heslo_scraper_uctu"
python run_monthly.py
```

Zobrazení tabulky s aktuálním stavem a změnou:

```bash
python report.py
```

## 4. Automatizace přes GitHub Actions (doporučeno, zdarma)

Tohle spustí sběr dat automaticky každý měsíc v cloudu, aniž by u vás
cokoliv muselo běžet.

1. **Založte si (nebo použijte) GitHub účet** a vytvořte nový repozitář,
   nejlépe **privátní** (Settings při vytváření → Private) - obsahuje
   seznam sledovaných účtů, ať to není veřejné.

2. **Nahrajte do něj celý obsah této složky**, včetně skryté složky
   `.github/workflows/monthly.yml`. Nejjednodušší je přes web GitHubu
   (Add file → Upload files), nebo přes git:

   ```bash
   cd ig-tracker
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/VASE_JMENO/ig-tracker.git
   git push -u origin main
   ```

   `config.json` (bez tajných údajů - jen seznam účtů a IG user id) do
   repa klidně nahrajte, potřebuje ho workflow ke spuštění.

3. **Přidejte secrets** (tajné údaje, které workflow uvidí, ale nikdo
   jiný): v repozitáři jděte na **Settings → Secrets and variables →
   Actions → New repository secret** a vytvořte:
   - `GRAPH_ACCESS_TOKEN` – token z Meta Graph API (krok 2 výše)
   - `IG_SCRAPER_PASSWORD` – heslo k "obětovanému" IG účtu

4. **Povolte workflow zapisovat zpět do repa**: Settings → Actions →
   General → Workflow permissions → zaškrtněte **"Read and write
   permissions"** → Save. (Bez tohoto by workflow nemohl uložit novou
   databázi zpět do repozitáře.)

5. **Hotovo.** Workflow se od teď spustí automaticky vždy 1. den v
   měsíci v 9:00 UTC. Průběh a případné chyby uvidíte v repozitáři pod
   záložkou **Actions**. Aktuální tabulku se stavem a změnami najdete
   v souboru `REPORT.md` přímo v repu (GitHub ho hezky vykreslí).

   Chcete-li to vyzkoušet hned, bez čekání na 1. den v měsíci: záložka
   **Actions → Měsíční sběr IG followers → Run workflow**.

## Rizika a údržba (cizí účty)

- Instaloader je neoficiální nástroj a Instagram může kdykoliv změnit
  chování webu tak, že přestane fungovat – bude potřeba ho aktualizovat
  (`pip install --upgrade instaloader`) nebo počkat na opravu autorů knihovny.
- Scraper účet může být dočasně omezen. Při 20 účtech jednou měsíčně je
  zátěž nízká, ale riziko není nulové.
- Pokud automatika u nějakého účtu selže, `run_monthly.py` to jen ohlásí
  a pokračuje dál – číslo pro ten účet ten měsíc můžete doplnit ručně
  přímo do databáze, nebo počkat na příští běh.
