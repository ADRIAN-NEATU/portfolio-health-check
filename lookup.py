"""Online lookup of a ticker or company name in free sources whose terms allow it.

- SEC EDGAR (U.S. government data, public domain): every company listed in the
  US, including European and emerging-market companies with US listings.
  Sector comes from the official SIC code through our own table, size from the
  public float the company reports, region from its business address.
- OpenFIGI (Bloomberg's open symbology, MIT licence, free): listings on other
  exchanges. It gives the type and the exchange (so the currency); for funds the
  region and sector are read from the fund's name.

Sector and size are approximations: official GICS classifications and live
market caps are licensed data. Nothing here imports Streamlit, and every
network failure ends in "not found", so the editor keeps working offline.
"""

from __future__ import annotations

import datetime as dt
import functools
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from scoring import Found, match_key

# SEC asks automated clients to identify themselves; set PHC_CONTACT to add an e-mail.
CONTACT = os.environ.get("PHC_CONTACT", "")
USER_AGENT = "PortfolioHealthCheck/1.0 (educational project" + (f"; {CONTACT}" if CONTACT else "") + ")"
TIMEOUT = 8  # seconds per request
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
SEC_FLOAT_URL = "https://data.sec.gov/api/xbrl/frames/dei/EntityPublicFloat/USD/CY{period}I.json"
SEC_COMPANY_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
OPENFIGI_MAPPING_URL = "https://api.openfigi.com/v3/mapping"
OPENFIGI_SEARCH_URL = "https://api.openfigi.com/v3/search"

# Size bands used by the data (see rules.py): large > $10bn, mid $2-10bn, small < $2bn.
LARGE_CAP_USD = 10e9
MID_CAP_USD = 2e9

# SIC code ranges -> sector, first match wins (our approximation of GICS sectors).
SIC_SECTORS = [
    ((2830, 2836), "Health Care"),
    ((2840, 2844), "Consumer Staples"),
    ((3011, 3011), "Consumer Discretionary"),
    ((3570, 3579), "Information Technology"),
    ((3630, 3639), "Consumer Discretionary"),
    ((3651, 3652), "Consumer Discretionary"),
    ((3660, 3679), "Information Technology"),
    ((3710, 3716), "Consumer Discretionary"),
    ((3751, 3751), "Consumer Discretionary"),
    ((3790, 3799), "Consumer Discretionary"),
    ((3812, 3812), "Industrials"),
    ((3820, 3829), "Information Technology"),
    ((3840, 3851), "Health Care"),
    ((3861, 3861), "Information Technology"),
    ((1220, 1241), "Energy"),
    ((1300, 1389), "Energy"),
    ((2900, 2999), "Energy"),
    ((4610, 4619), "Energy"),
    ((4950, 4959), "Industrials"),
    ((5120, 5122), "Health Care"),
    ((5140, 5149), "Consumer Staples"),
    ((5170, 5172), "Energy"),
    ((5400, 5499), "Consumer Staples"),
    ((5912, 5912), "Consumer Staples"),
    ((6324, 6324), "Health Care"),
    ((6500, 6553), "Real Estate"),
    ((6798, 6798), "Real Estate"),
    ((7310, 7319), "Communication Services"),
    ((7370, 7379), "Information Technology"),
    ((7800, 7899), "Communication Services"),
    ((8731, 8731), "Health Care"),
    ((8000, 8099), "Health Care"),
    ((100, 999), "Consumer Staples"),
    ((1000, 1499), "Materials"),
    ((1500, 1799), "Industrials"),
    ((2000, 2199), "Consumer Staples"),
    ((2200, 2399), "Consumer Discretionary"),
    ((2400, 2499), "Materials"),
    ((2500, 2599), "Consumer Discretionary"),
    ((2600, 2699), "Materials"),
    ((2700, 2799), "Communication Services"),
    ((2800, 2899), "Materials"),
    ((3000, 3099), "Materials"),
    ((3100, 3199), "Consumer Discretionary"),
    ((3200, 3399), "Materials"),
    ((3400, 3899), "Industrials"),
    ((3900, 3999), "Consumer Discretionary"),
    ((4000, 4799), "Industrials"),
    ((4800, 4899), "Communication Services"),
    ((4900, 4999), "Utilities"),
    ((5000, 5199), "Industrials"),
    ((5200, 5999), "Consumer Discretionary"),
    ((6000, 6799), "Financials"),
    ((7000, 7299), "Consumer Discretionary"),
    ((7300, 7399), "Industrials"),
    ((7500, 7599), "Consumer Discretionary"),
    ((7600, 7699), "Industrials"),
    ((7900, 7999), "Consumer Discretionary"),
    ((8100, 8199), "Industrials"),
    ((8200, 8299), "Consumer Discretionary"),
    ((8300, 8799), "Industrials"),
]

US_STATES = set(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH "
    "NJ NM NY NC ND OH OK OR PA PR RI SC SD TN TX UT VT VA VI WA WV WI WY".split()
)
EUROPE = {
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czech republic", "denmark", "estonia",
    "finland", "france", "germany", "greece", "hungary", "iceland", "ireland", "italy", "latvia",
    "lithuania", "luxembourg", "malta", "monaco", "netherlands", "norway", "poland", "portugal",
    "slovakia", "slovenia", "spain", "sweden", "switzerland", "united kingdom", "jersey",
    "guernsey", "isle of man", "liechtenstein",
}
EMERGING = {
    "argentina", "brazil", "chile", "china", "colombia", "egypt", "india", "indonesia",
    "korea, republic of", "kuwait", "malaysia", "mexico", "peru", "philippines", "qatar",
    "saudi arabia", "south africa", "taiwan, province of china", "thailand", "turkey",
    "united arab emirates",
}

# Bloomberg exchange codes we recognise: code -> (currency, region), in order of preference.
EXCHANGES = {
    "RO": ("RON", "Romania"),
    "US": ("USD", "US"), "UN": ("USD", "US"), "UW": ("USD", "US"), "UQ": ("USD", "US"),
    "UR": ("USD", "US"), "UA": ("USD", "US"), "UP": ("USD", "US"),
    "GY": ("EUR", "Europe"), "FP": ("EUR", "Europe"), "NA": ("EUR", "Europe"),
    "IM": ("EUR", "Europe"), "SM": ("EUR", "Europe"), "BB": ("EUR", "Europe"),
    "AV": ("EUR", "Europe"), "FH": ("EUR", "Europe"), "ID": ("EUR", "Europe"),
    "PL": ("EUR", "Europe"), "DC": ("DKK", "Europe"), "SS": ("SEK", "Europe"),
    "NO": ("NOK", "Europe"), "SW": ("CHF", "Europe"), "SE": ("CHF", "Europe"),
    "LN": ("GBP", "Europe"), "PW": ("PLN", "Europe"), "HB": ("HUF", "Europe"),
    "CK": ("CZK", "Europe"),
    "GR": ("EUR", "Europe"), "GF": ("EUR", "Europe"), "GM": ("EUR", "Europe"),
    "GS": ("EUR", "Europe"), "GD": ("EUR", "Europe"), "GH": ("EUR", "Europe"),
}
EXCHANGE_RANK = {code: rank for rank, code in enumerate(EXCHANGES)}
STOCK_TYPES = {"Common Stock", "REIT"}
FUND_TYPES = {"ETP"}

# Words in a fund's name -> region, sector, or a bond fund.
FUND_REGIONS = [
    (r"\b(ALL[- ]?WORLD|AW|WORLD|ACWI|GLOBAL|ALL COUNTRY)\b", "Global"),
    (r"\b(EMERGING|EM|EMG)\b", "Emerging"),
    (r"\b(ROMANIA|BET)\b", "Romania"),
    (r"\b(EUROPE|EURO STOXX|STOXX|EUROZONE|EMU|DAX|CAC|FTSE 100|UK)\b", "Europe"),
    (r"\b(S&P ?500|NASDAQ|QQQ|USA|US|RUSSELL|DOW JONES|TOTAL STOCK|TOTAL MARKET)\b", "US"),
]
FUND_SECTORS = [
    (r"\b(TECH\w*|INFORMATION TECH\w*|SEMICONDUCTOR\w*|SOFTWARE)\b", "Information Technology"),
    (r"\b(HEALTH\w*|BIOTECH\w*|PHARMA\w*)\b", "Health Care"),
    (r"\b(FINANCIAL\w*|BANKS?)\b", "Financials"),
    (r"\b(ENERGY|OIL|GAS)\b", "Energy"),
    (r"\b(DEFEN[CS]E|AEROSPACE|INDUSTRIALS?)\b", "Industrials"),
    (r"\b(UTILIT\w*)\b", "Utilities"),
    (r"\b(REAL ESTATE|REITS?|PROPERTY)\b", "Real Estate"),
    (r"\b(CONSUMER STAPLES)\b", "Consumer Staples"),
    (r"\b(CONSUMER DISCRETIONARY)\b", "Consumer Discretionary"),
    (r"\b(MATERIALS|MINING|MINERS)\b", "Materials"),
    (r"\b(COMMUNICATION\w*|MEDIA|TELECOM\w*)\b", "Communication Services"),
]
BOND_WORDS = r"\b(BOND|BONDS|TREASURY|TREAS|GOVT|GOVERNMENT|AGGREGATE|AGG|T-BILL|MONEY MARKET)\b"



class SourceError(Exception):
    """A source could not be reached or answered with an error."""


# SEC's fair-access policy allows at most 10 requests a second: every request to SEC
# (all GETs here) waits its turn, so the app stays well below that, even with threads.
SEC_MIN_INTERVAL = 0.15  # seconds between two requests, about 7 a second
_pace_lock = threading.Lock()
_last_request = 0.0


def _pace() -> None:
    global _last_request
    with _pace_lock:
        wait = _last_request + SEC_MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request = time.monotonic()


def _get_json(url: str):
    _pace()
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise SourceError(str(error)) from None


def _post_json(url: str, payload):
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
    if os.environ.get("OPENFIGI_API_KEY"):
        headers["X-OPENFIGI-APIKEY"] = os.environ["OPENFIGI_API_KEY"]
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise SourceError(str(error)) from None


# ---------------------------------------------------------------------------
# Translating source data into our categories
# ---------------------------------------------------------------------------


def sic_sector(sic) -> str | None:
    try:
        code = int(sic)
    except (TypeError, ValueError):
        return None
    return next((sector for (low, high), sector in SIC_SECTORS if low <= code <= high), None)


def size_class(public_float: float | None, filer_category: str | None) -> str | None:
    """Market cap band from the public float; without it, only the SEC filer
    categories that are always below $700m of float can be read (as small)."""
    if public_float:
        return "large" if public_float >= LARGE_CAP_USD else "mid" if public_float >= MID_CAP_USD else "small"
    category = (filer_category or "").lower()
    if "non-accelerated" in category or "smaller reporting" in category or category.startswith("accelerated"):
        return "small"
    return None


def address_region(code: str | None, country: str | None) -> str | None:
    if code in US_STATES:
        return "US"
    name = (country or "").strip().lower()
    if name == "romania":
        return "Romania"
    if name in EUROPE:
        return "Europe"
    if name in EMERGING:
        return "Emerging"
    return None


def fund_details(name: str, currency: str | None) -> dict:
    """Type, region and sector of a fund, read from its name."""
    text = f" {name.upper()} "
    if re.search(BOND_WORDS, text):
        details = {"asset_type": "bond", "sector": "n/a", "market_cap": "n/a"}
    else:
        sector = next((s for pattern, s in FUND_SECTORS if re.search(pattern, text)), "Diversified")
        details = {"asset_type": "ETF", "sector": sector, "market_cap": "n/a"}
    details["region"] = next((r for pattern, r in FUND_REGIONS if re.search(pattern, text)), None)
    details["currency"] = currency
    return details


# ---------------------------------------------------------------------------
# SEC EDGAR
# ---------------------------------------------------------------------------


@functools.cache
def sec_listings() -> tuple[dict, dict]:
    """(ticker -> (cik, name), name key -> list of (cik, name)) for every US listing."""
    data = _get_json(SEC_TICKERS_URL)
    columns = data["fields"]
    by_ticker, by_name = {}, {}
    for row in data["data"]:
        record = dict(zip(columns, row))
        cik, name, ticker = record["cik"], record["name"], record["ticker"]
        if ticker:
            by_ticker.setdefault(ticker.upper(), (cik, name))
        by_name.setdefault(match_key(name), []).append((cik, name))
    return by_ticker, by_name


@functools.cache
def sec_public_float() -> dict[int, float]:
    """CIK -> latest reported public float in USD. Companies report it for the
    end of their second fiscal quarter, so every quarter of recent years is read."""
    year = dt.date.today().year
    periods = [f"{y}Q{q}" for y in (year - 2, year - 1, year) for q in (1, 2, 3, 4)]

    def frame(period):
        try:
            return _get_json(SEC_FLOAT_URL.format(period=period))["data"]
        except SourceError:  # periods not published yet answer with an error
            return []

    floats = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for rows in pool.map(frame, periods):  # oldest first, so the latest value wins
            floats.update({row["cik"]: row["val"] for row in rows})
    return floats


@functools.cache
def sec_company(cik: int) -> dict:
    return _get_json(SEC_COMPANY_URL.format(cik=cik))


def sec_details(cik: int, name: str) -> dict:
    company = sec_company(cik)
    addresses = company.get("addresses", {})
    region = None
    for kind in ("business", "mailing"):
        address = addresses.get(kind) or {}
        region = region or address_region(address.get("stateOrCountry"), address.get("stateOrCountryDescription"))
    if " ETF" in f" {name.upper()} ":
        details = fund_details(name, "USD")
        details["region"] = details["region"] or region
        return details
    return {
        "sector": sic_sector(company.get("sic")),
        "asset_type": "stock",
        "market_cap": size_class(sec_public_float().get(cik), company.get("category")),
        "currency": "USD",
        "region": region,
    }


def find_sec(query: str) -> Found | None:
    by_ticker, by_name = sec_listings()
    key = match_key(query)
    ticker = query.strip().upper()
    as_ticker = by_ticker.get(ticker)
    as_name = None
    if key in by_name:
        as_name = by_name[key][0]
    else:
        # "Micron" -> "Micron Technology": among names that start with it, the largest
        starting = [c for k, companies in by_name.items() if k.startswith(key + " ") for c in companies]
        if starting and len(key) >= 3:
            floats = sec_public_float()
            as_name = max(starting, key=lambda c: floats.get(c[0], 0))
    # Typed in capitals ("FORD") reads as a ticker first, "Ford" as a name first.
    typed_as_ticker = query.strip().isupper() and " " not in query.strip()
    choice = (as_ticker or as_name) if typed_as_ticker else (as_name or as_ticker)
    if choice is None:
        return None
    cik, name = choice
    return Found(name, "SEC EDGAR", sec_details(cik, name))


# ---------------------------------------------------------------------------
# OpenFIGI
# ---------------------------------------------------------------------------


def _usable(hit: dict) -> bool:
    return hit.get("exchCode") in EXCHANGES and hit.get("securityType") in STOCK_TYPES | FUND_TYPES


def figi_details(hit: dict) -> dict:
    currency, region = EXCHANGES[hit["exchCode"]]
    if hit["securityType"] in FUND_TYPES:
        # London lists the same fund in several currencies under different tickers.
        return fund_details(hit.get("name", ""), None if hit["exchCode"] == "LN" else currency)
    return {"sector": None, "asset_type": "stock", "market_cap": None, "currency": currency, "region": region}


def find_figi(query: str) -> Found | None:
    text = query.strip()
    hits = []
    if re.fullmatch(r"[A-Za-z0-9.\-]{1,12}", text):
        answer = _post_json(OPENFIGI_MAPPING_URL, [{"idType": "TICKER", "idValue": text.upper()}])
        hits = answer[0].get("data", []) if answer else []
    if not any(_usable(h) for h in hits):
        hits = _post_json(OPENFIGI_SEARCH_URL, {"query": text}).get("data", [])
    hits = [h for h in hits if _usable(h)]
    if not hits:
        return None
    key = match_key(text)

    def rank(hit):
        name_key = match_key(hit.get("name", ""))
        closeness = 0 if name_key == key else 1 if name_key.startswith(key) else 2
        return closeness, EXCHANGE_RANK[hit["exchCode"]], len(hit.get("name", ""))

    best = min(hits, key=rank)
    return Found(best.get("name", text), "OpenFIGI", figi_details(best))


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, Found | None]] = {}
_cache_lock = threading.Lock()
ERROR_RETRY_SECONDS = 300  # after a network error, try again only after 5 minutes


def find(query: str) -> Found | None:
    """Details of a ticker or company name, or None when no source knows it."""
    key = query.strip()
    with _cache_lock:
        cached = _cache.get(key)
    if cached and (cached[1] is not None or time.monotonic() < cached[0]):
        return cached[1]
    result, failed = None, False
    for source in (find_sec, find_figi):
        try:
            result = source(key)
        except SourceError:
            failed = True
            continue
        if result:
            break
    retry_at = time.monotonic() + ERROR_RETRY_SECONDS if failed else float("inf")
    with _cache_lock:
        _cache[key] = (retry_at, result)
    return result


def uncached(queries: list[str]) -> list[str]:
    """The names that find() has not answered yet (they will need the network)."""
    now = time.monotonic()
    with _cache_lock:
        cached = {q: _cache.get(q.strip()) for q in queries}
    return [q for q, c in cached.items() if c is None or (c[1] is None and now >= c[0])]


def find_many(queries: list[str]) -> dict[str, Found | None]:
    """find() for several names at once (in parallel, within SEC's 10 requests/second)."""
    unique = list(dict.fromkeys(q.strip() for q in queries if q and q.strip()))
    with ThreadPoolExecutor(max_workers=4) as pool:
        return dict(zip(unique, pool.map(find, unique)))


def clear_cache() -> None:
    with _cache_lock:
        _cache.clear()
    for cached in (sec_listings, sec_public_float, sec_company):
        cached.cache_clear()
