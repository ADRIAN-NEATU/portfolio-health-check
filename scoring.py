"""Concentration analysis for Portfolio Health Check.

All the logic lives here and nothing here imports Streamlit: app.py only
displays what these functions return. Thresholds come from rules.py.
"""

from __future__ import annotations

import functools
import io
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

import rules

DATA_DIR = Path(__file__).parent / "data"
TEMPLATE_PATH = DATA_DIR / "template.csv"
# Stocks and funds the editor can fill in by name or ticker (details approximate).
KNOWN_SECURITIES_PATH = DATA_DIR / "known_securities.csv"
INDEX_FUNDS_PATH = DATA_DIR / "index_funds.csv"

# Sample portfolios offered in the app: file name -> (display name, description).
SAMPLE_PORTFOLIOS = {
    "diversified.csv": (
        "Diversified",
        "22 positions across funds, stocks, bonds and cash in four currencies.",
    ),
    "tech_heavy.csv": (
        "Tech-heavy",
        "Many small positions, but almost half of the money is in technology companies.",
    ),
    "all_in_ron.csv": (
        "All in RON",
        "Stocks, bonds, a fund and a deposit, all in lei: no foreign currency at all.",
    ),
    "beginner_3_stocks.csv": (
        "Beginner with 3 stocks",
        "Savings, an index fund and three stocks, one of which holds a fifth of the money.",
    ),
    "conservative_saver.csv": (
        "Conservative saver",
        "Mostly government bonds and deposits, plus one global fund.",
    ),
    "small_cap_fan.csv": (
        "Small-cap fan",
        "Spread across sectors and currencies, with most of the stocks in small companies.",
    ),
    "one_global_etf.csv": (
        "One global ETF",
        "Everything in a single worldwide index fund, bought in US dollars.",
    ),
    "andrei.csv": (
        "Andrei",
        "Andrei invests through a US broker: 12 American stocks and 2 ETFs, all in dollars.",
    ),
}

# Portfolios built to sit right on a threshold or to show one rule at work.
STRESS_PORTFOLIOS = {
    "stress_sector_just_over.csv": (
        "Just over a sector",
        "27% in industrial companies: 2 points past the 25% limit, inside the safety margin.",
    ),
    "stress_exact_limits.csv": (
        "Exactly at the limits",
        "One sector at exactly 25% and two stocks at exactly 10%: both limits at their edge.",
    ),
    "stress_sector_over_margin.csv": (
        "Past the safety margin",
        "31% in energy companies: just beyond the 30% margin, so over the limit.",
    ),
    "stress_small_index_slice.csv": (
        "Five stocks, a little index",
        "95% in five stocks and 5% in an S&P 500 fund: the fund barely helps.",
    ),
    "stress_half_index.csv": (
        "Five stocks, half index",
        "Half in five stocks, half in an S&P 500 fund.",
    ),
    "stress_corporate_bond.csv": (
        "One big corporate bond",
        "15% in one company's bond: it counts like a position in that company.",
    ),
    "stress_gold.csv": (
        "A quarter in gold",
        "25% in gold: no sector, but one position, over the 10% limit, plus a global fund and cash.",
    ),
    "stress_government_bonds.csv": (
        "Government bond ladder",
        "Five Romanian government bonds, cash and a global fund.",
    ),
    "stress_us_large_caps.csv": (
        "25 US large caps",
        "Spread evenly over 25 large American companies, all in dollars.",
    ),
    "stress_bvb_only.csv": (
        "Bucharest only",
        "Thirteen BVB shares, with 40% of the money in utilities.",
    ),
}

COLUMNS = ("asset", "value", "sector", "asset_type", "market_cap", "currency", "region")
OPTIONAL_COLUMNS = ("region",)
REQUIRED_COLUMNS = tuple(c for c in COLUMNS if c not in OPTIONAL_COLUMNS)
TEXT_COLUMNS = tuple(c for c in COLUMNS if c != "value")

# Sector spelling (any letter case, or an alias) -> official name.
SECTOR_NAMES = {
    **{name.lower(): name for name in rules.GICS_SECTORS + rules.SECTOR_EXEMPT},
    **{alias.lower(): name for alias, name in rules.SECTOR_ALIASES.items()},
}

# "bond" is a government bond; a corporate bond counts like the company (decision D7).
ASSET_TYPES = ("stock", "ETF", "bond", "corporate bond", "cash", "precious metal")
BOND_TYPES = ("bond", "corporate bond")
CAP_SEGMENTS = ("small", "mid", "large")
REGIONS = ("US", "Europe", "Romania", "Emerging", "Global")
HOME_CURRENCY = "RON"
GLOBAL_REGION = "Global"

# Currencies offered in the in-app editor (a CSV may use any code).
CURRENCIES = ("RON", "USD", "EUR", "GBP", "CHF", "NOK", "SEK", "DKK", "PLN", "HUF", "CZK", "CAD", "JPY")

# The columns that describe a position, and the choices the editor offers for them.
DETAIL_COLUMNS = ("sector", "asset_type", "market_cap", "currency", "region")
EDITOR_OPTIONS = {
    "sector": rules.GICS_SECTORS + rules.SECTOR_EXEMPT,
    "asset_type": ASSET_TYPES,
    "market_cap": CAP_SEGMENTS + ("n/a",),
    "currency": CURRENCIES,
    "region": REGIONS,
}
FIELD_NAMES = {
    "asset": "name",
    "value": "value",
    "sector": "sector",
    "asset_type": "type",
    "market_cap": "market cap",
    "currency": "currency",
    "region": "region",
}
# Words dropped from the end of a name before matching ("Apple Inc." -> "apple").
LEGAL_SUFFIXES = {"inc", "corp", "corporation", "co", "company", "plc", "ltd", "limited", "sa", "nv",
                  "ag", "se", "asa", "as", "spa", "ab", "publ", "oyj", "holdings", "reg"}

# Other spellings accepted for the category columns, matched in any letter case.
CATEGORY_NAMES = {
    "asset_type": {
        **{t.lower(): t for t in ASSET_TYPES},
        "stocks": "stock",
        "share": "stock",
        "shares": "stock",
        "etfs": "ETF",
        "bonds": "bond",
        "government bond": "bond",
        "government bonds": "bond",
        "corporate": "corporate bond",
        "corporate bonds": "corporate bond",
        "corp bond": "corporate bond",
        "deposit": "cash",
        "precious metals": "precious metal",
        "metal": "precious metal",
        "metals": "precious metal",
        "gold": "precious metal",
        "silver": "precious metal",
    },
    "market_cap": {
        **{c: c for c in CAP_SEGMENTS + ("n/a",)},
        "large cap": "large",
        "large-cap": "large",
        "mid cap": "mid",
        "mid-cap": "mid",
        "small cap": "small",
        "small-cap": "small",
    },
    "region": {
        **{r.lower(): r for r in REGIONS},
        "usa": "US",
        "united states": "US",
        "eu": "Europe",
        "ro": "Romania",
        "emerging markets": "Emerging",
        "em": "Emerging",
        "world": "Global",
    },
}

GREEN, YELLOW, ORANGE, RED = "green", "yellow", "orange", "red"
STATUS_LABELS = {GREEN: "OK", YELLOW: "Watch", ORANGE: "Just over", RED: "Over limit"}
STATUS_RANK = {RED: 0, ORANGE: 1, YELLOW: 2, GREEN: 3}

# Word that starts a warning, e.g. "Position Apple: 8% (limit 10%)".
WARNING_PREFIX = {"sector": "Sector", "asset": "Position"}

# How a region reads inside a sentence ("87% of your money is in the US").
REGION_PHRASES = {"US": "the US", "Emerging": "emerging markets"}

# What the two non-sector labels mean, shown under the Sector chart and in tables.
LABEL_EXPLANATIONS = {
    "Diversified": "Diversified: broad funds (ETFs) spread over many sectors.",
    "n/a": "n/a: bonds and cash, which have no sector.",
}

# Dimensions offered in the Charts tab.
CHART_DIMENSIONS = {
    "sector": "Sector",
    "currency": "Currency",
    "asset": "Position",
    "region": "Region",
}

# Tolerance for floating-point comparisons (0.8 * 0.8 = 0.6400000000000001).
EPS = 1e-9


class PortfolioError(ValueError):
    """The CSV cannot be analysed; the message is meant for the user."""


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass
class LimitResult:
    key: str
    label: str
    why: str
    source: str  # where the thresholds come from, "" while they are examples
    yellow_from: float
    limit: float
    category: str  # largest counted category, "" when nothing counts
    weight: float
    status: str
    score: float


@dataclass
class LimitWarning:
    key: str
    category: str
    weight: float
    status: str
    score: float
    text: str


@dataclass
class Profile:
    defensive_share: float  # bonds (government and corporate) + cash
    breakdown: dict[str, float]  # share of each asset type


@dataclass
class Insight:
    key: str
    title: str
    text: str
    label: str  # "Watch" or "Info"
    source: str = ""  # where a figure in the text comes from, shown behind a (?)


@dataclass
class Note:
    key: str
    text: str


@dataclass
class Summary:
    """The short list at the top: what is good and what to look at, in plain words."""
    good: list[str]
    look_at: list[str]


@dataclass
class Analysis:
    positions: pd.DataFrame  # input rows plus a "weight" column, largest first
    has_region: bool
    info: list[str]
    limits: list[LimitResult]
    score: int
    tier: str  # A+, A, B, C or D
    spread_score: float  # the spread part, 0-100
    hhi: float  # concentration index of the single companies
    equal_stocks: float  # the number of equal stocks the HHI is worth
    warnings: list[LimitWarning]
    profile: Profile
    insights: list[Insight]
    notes: list[Note]
    cap_mix: pd.Series  # share of each cap segment within the stocks
    summary: Summary


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def fmt_pct(share: float) -> str:
    """0.453 -> '45.3%', 0.45 -> '45%'."""
    return f"{round(share * 100, 1):g}%"


def fmt_ron(value: float) -> str:
    """12000 -> '12,000'."""
    return f"{value:,.0f}"


def round_half_up(x: float) -> int:
    """92.5 -> 93 (Python's round() would give 92)."""
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------------------
# Loading and validation
# ---------------------------------------------------------------------------


def load_portfolio(source) -> pd.DataFrame:
    """Read a portfolio CSV from a path or an uploaded file, then validate it."""
    return validate(read_table(source))


def read_table(source) -> pd.DataFrame:
    """The CSV as a table of text, before any check. Also reads files saved by
    Excel with Romanian settings: ';' between columns and a decimal comma (1.234,56)."""
    text = read_text(source)
    if not text.strip():
        raise PortfolioError("The file is empty. Start from the template.")
    header = text.splitlines()[0]
    separator = ";" if header.count(";") > header.count(",") else ","
    try:
        df = pd.read_csv(io.StringIO(text), sep=separator, dtype=str, keep_default_na=False)
    except pd.errors.ParserError:
        raise PortfolioError(
            "The file could not be read as a CSV. Start from the template."
        ) from None
    df.columns = [str(c).strip() for c in df.columns]
    if "value" in df.columns:
        df["value"] = df["value"].map(lambda v: parse_amount(v, decimal_comma=separator == ";"))
    return df


def read_text(source) -> str:
    """The file's text: UTF-8 (with or without the BOM Excel adds), or the
    Windows Central European encoding Excel uses for 'CSV' in Romanian."""
    raw = source.read() if hasattr(source, "read") else Path(source).read_bytes()
    if isinstance(raw, str):
        return raw.lstrip("\ufeff")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        pass
    try:
        return raw.decode("cp1250")
    except UnicodeDecodeError:
        raise PortfolioError("The file could not be read as text. Save it as CSV UTF-8.") from None


def parse_amount(text: str, decimal_comma: bool) -> str:
    """Write an amount the standard way: '1.234,56' -> '1234.56' in a file with a
    decimal comma, '1,234.56' -> '1234.56' otherwise. Spaces between thousands
    are dropped. Anything else is left for validate() to reject."""
    text = text.replace(" ", "").replace("\u00a0", "")
    if not decimal_comma:
        return text.replace(",", "")
    if "," in text:
        return text.replace(".", "").replace(",", ".")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", text):  # here the dot separates thousands: 1.234 = 1234
        return text.replace(".", "")
    return text


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Check the columns and values; return a clean copy."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        plural = "s" if len(missing) > 1 else ""
        raise PortfolioError(
            f"Missing required column{plural}: {', '.join(missing)}. "
            f"Expected columns: {', '.join(COLUMNS)} (region is optional)."
        )
    if df.empty:
        raise PortfolioError("The file has no positions.")

    values = pd.to_numeric(df["value"], errors="coerce")
    bad = ~values.between(0, math.inf, inclusive="neither")
    if bad.any():
        lines = ", ".join(str(i + 2) for i in df.index[bad][:5])  # line 1 is the header
        raise PortfolioError(
            f"Column 'value' must be a positive number (in lei). Check line(s) {lines}."
        )

    df["value"] = values.astype(float)
    df = clean_text(df)
    return df[[c for c in COLUMNS if c in df.columns]]


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """Trim the text columns and write categories the standard way
    ('Technology' -> 'Information Technology', 'Stock' -> 'stock', 'usd' -> 'USD')."""
    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype(str).str.strip()
    if "sector" in df.columns:
        df["sector"] = df["sector"].map(normalize_sector)
    for column, names in CATEGORY_NAMES.items():
        if column in df.columns:
            df[column] = df[column].map(lambda v, names=names: names.get(v.lower(), v))
    if "currency" in df.columns:
        df["currency"] = df["currency"].str.upper()
    return df


def editor_table(df: pd.DataFrame) -> pd.DataFrame:
    """The rows of a CSV that could not be analysed, ready for the editor: our
    columns only, amounts as numbers, missing details as empty cells."""
    table = clean_text(df.copy()).reindex(columns=COLUMNS)
    table["value"] = pd.to_numeric(table["value"], errors="coerce")
    for column in TEXT_COLUMNS:
        table[column] = [None if is_blank(v) else v for v in table[column]]
    return table.reset_index(drop=True)


def normalize_sector(name: str) -> str:
    """Official GICS name for a sector ('Technology' -> 'Information Technology');
    unknown names are kept as written."""
    return SECTOR_NAMES.get(name.lower(), name)


# ---------------------------------------------------------------------------
# In-app editor: known securities, auto-fill, checks, export
# ---------------------------------------------------------------------------


def is_blank(value) -> bool:
    """Empty cell: None, NaN or only spaces."""
    return value is None or (isinstance(value, float) and math.isnan(value)) or not str(value).strip()


def match_key(name: str) -> str:
    """The form used to compare names: 'Apple Inc.' -> 'apple', 'Vale S.A.' -> 'vale',
    'Johnson and Johnson' -> 'johnson & johnson', 'BRK-B' -> 'brk b', 'Nestlé' -> 'nestle'."""
    text = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    text = text.lower().replace("'", "").replace(" and ", " & ")
    text = re.sub(r"\b([a-z])[./](?=[a-z]\b)", r"\1", text)  # "s.a." -> "sa", "a/s" -> "as"
    words = re.sub(r"[^a-z0-9&]+", " ", text).split()
    if len(words) > 1 and words[0] == "the":
        words.pop(0)
    while len(words) > 1 and words[-1] in LEGAL_SUFFIXES:
        words.pop()
    return " ".join(words)


@dataclass
class Found:
    """A security found by name or ticker, and where its details come from."""

    name: str
    source: str
    details: dict  # some or all of DETAIL_COLUMNS; missing ones are None


@functools.cache
def known_securities() -> dict[str, Found]:
    """Name, ticker or alias (in match_key form) -> a security from our own list."""
    table = pd.read_csv(KNOWN_SECURITIES_PATH, dtype=str, keep_default_na=False)
    lookup = {}
    for row in table.to_dict("records"):
        found = Found(row["name"], "the built-in list", {column: row[column] for column in DETAIL_COLUMNS})
        for name in [row["name"], *row["aliases"].split("|")]:
            if name.strip():
                lookup.setdefault(match_key(name), found)
    return lookup


def empty_positions(rows: int = 0) -> pd.DataFrame:
    """A table with the portfolio columns and `rows` blank rows, to start the editor."""
    return pd.DataFrame(
        {c: pd.Series([None] * rows, dtype=float if c == "value" else object) for c in COLUMNS}
    )


def assets_to_look_up(df: pd.DataFrame) -> list[str]:
    """Names of rows with empty details that our own list does not know."""
    known = known_securities()
    names = [
        str(row["asset"]).strip()
        for _, row in df.iterrows()
        if not is_blank(row["asset"]) and any(is_blank(row[c]) for c in DETAIL_COLUMNS)
    ]
    return list(dict.fromkeys(n for n in names if match_key(n) not in known))


def autofill(df: pd.DataFrame, find_many=None) -> tuple[pd.DataFrame, list[tuple[str, Found]], list[str]]:
    """Fill the empty details of each row from our own list and, when `find_many`
    is given (name list -> {name: Found or None}), from an online lookup.
    Details already chosen are kept.

    Returns the table, (asset, Found) for every row that got new details, and
    the names nobody knows."""
    df = df.copy()
    known = known_securities()
    online = find_many(assets_to_look_up(df)) if find_many else {}
    filled, unknown = [], []
    for i, row in df.iterrows():
        if is_blank(row["asset"]):
            continue
        asset = str(row["asset"]).strip()
        found = known.get(match_key(asset)) or online.get(asset)
        empty = [c for c in DETAIL_COLUMNS if is_blank(row[c])]
        if found is None:
            if empty:
                unknown.append(asset)
            continue
        new = [c for c in empty if not is_blank(found.details.get(c))]
        for column in new:
            df.at[i, column] = found.details[column]
        if new:
            filled.append((asset, found))
    return df, filled, list(dict.fromkeys(unknown))


def check_editor_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """The rows typed in the editor without the blank ones, and what each row
    still misses, e.g. 'Netstreit: sector, market cap'."""
    typed = df[[not (is_blank(a) and is_blank(v)) for a, v in zip(df["asset"], df["value"])]]
    typed = typed.reset_index(drop=True)
    problems = []
    for number, row in typed.iterrows():
        missing = [FIELD_NAMES[c] for c in COLUMNS if is_blank(row[c])]
        if "value" not in missing and not pd.to_numeric(row["value"], errors="coerce") > 0:
            missing.append("a value above 0")
        if missing:
            label = f"row {number + 1}" if is_blank(row["asset"]) else str(row["asset"]).strip()
            problems.append(f"{label}: {', '.join(missing)}")
    return typed, problems


def to_csv(df: pd.DataFrame) -> bytes:
    """The positions as a CSV file, in the same format the app reads."""
    return df.reindex(columns=COLUMNS).to_csv(index=False, float_format="%.2f").encode("utf-8")


# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------


def weights(df: pd.DataFrame, column: str) -> pd.Series:
    """Share of the total value in each category of `column`, largest first. For
    sectors, a fund on a narrow index counts by what it holds."""
    if column == "sector":
        df = with_fund_sectors(df)
    shares = df.groupby(column)["value"].sum() / df["value"].sum()
    return shares.sort_values(ascending=False, kind="stable")


def cap_mix(df: pd.DataFrame) -> pd.Series:
    """Share of each market cap segment within the stocks only."""
    stocks = df[df["asset_type"] == "stock"]
    if stocks.empty:
        return pd.Series(dtype=float)
    return weights(stocks, "market_cap")


def counted_rows(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Rows that count towards a limit, exempt categories removed."""
    if key == "sector":
        df = with_fund_sectors(df)
        return df[~df["sector"].isin(rules.SECTOR_EXEMPT)]
    if key == "asset":
        broad_etf = (df["asset_type"] == "ETF") & (df["sector"] == rules.BROAD_ETF_SECTOR)
        return df[~(df["asset_type"].isin(rules.ASSET_EXEMPT_TYPES) | broad_etf)]
    return df


def limit_weights(df: pd.DataFrame, key: str) -> pd.Series:
    """Weights, as shares of the whole portfolio, of the categories a limit counts."""
    shares = counted_rows(df, key).groupby(key)["value"].sum() / df["value"].sum()
    return shares.sort_values(ascending=False, kind="stable")


def largest_foreign_currency(df: pd.DataFrame) -> tuple[str, float]:
    """Largest single currency other than RON; ("", 0.0) if everything is in RON."""
    currencies = weights(df, "currency").drop(HOME_CURRENCY, errors="ignore")
    if currencies.empty:
        return "", 0.0
    return currencies.index[0], float(currencies.iloc[0])


def largest_region(df: pd.DataFrame) -> tuple[str, float]:
    """Largest single region, Global excluded; ("", 0.0) if there is none."""
    regions = weights(df, "region").drop(GLOBAL_REGION, errors="ignore")
    if regions.empty:
        return "", 0.0
    return regions.index[0], float(regions.iloc[0])


# ---------------------------------------------------------------------------
# What index funds hold (decision D6)
# ---------------------------------------------------------------------------


@functools.cache
def index_funds() -> pd.DataFrame:
    """Sector weights, US share and largest companies of the indices we know; empty
    when data/index_funds.csv is missing, as in the published project (D8)."""
    if not INDEX_FUNDS_PATH.exists():
        return pd.DataFrame(columns=["index", "kind", "name", "weight", "sector"])
    return pd.read_csv(INDEX_FUNDS_PATH, keep_default_na=False)


def index_part(index: str, kind: str) -> pd.Series:
    """One part of an index ("sector", "country" or "company") -> its weights."""
    table = index_funds()
    rows = table[(table["index"] == index) & (table["kind"] == kind)]
    return pd.Series(rows["weight"].astype(float).values, index=rows["name"].values)


def fund_index(row) -> str:
    """The index a broad ETF follows, read from its name; "" if we don't know it or
    have no figures for it."""
    if row["asset_type"] != "ETF" or row["sector"] != rules.BROAD_ETF_SECTOR:
        return ""
    name = canonical_name(row["asset"]).lower()
    if re.search(rules.INDEX_NAME_EXCLUDE, name):
        return ""
    index = next((index for pattern, index in rules.INDEX_NAME_PATTERNS if re.search(pattern, name)), "")
    return index if index in set(index_funds()["index"]) else ""


def with_fund_sectors(df: pd.DataFrame) -> pd.DataFrame:
    """The portfolio with each fund on a narrow index split into its sectors, so it
    counts towards the sector limit by what it holds. Other rows are unchanged."""
    rows = []
    for _, row in df.iterrows():
        index = fund_index(row)
        if index not in rules.NARROW_INDICES:
            rows.append(row)
            continue
        for sector, share in index_part(index, "sector").items():
            part = row.copy()
            part["sector"] = sector
            part["value"] = row["value"] * share
            if "weight" in part:
                part["weight"] = row["weight"] * share
            rows.append(part)
    return pd.DataFrame(rows, columns=df.columns).reset_index(drop=True)


def canonical_name(name: str) -> str:
    """The built-in list's name for a security ("AAPL" -> "Apple"), or the name itself."""
    found = known_securities().get(match_key(name))
    return found.name if found else str(name).strip()


def funds_insight(df: pd.DataFrame, has_region: bool) -> Insight | None:
    """What the index funds hold, added to what is held directly: the largest sector,
    the US share and the largest companies. Information only: never in the score."""
    funds = [(fund_index(row), row) for _, row in df.iterrows()]
    funds = [(index, row) for index, row in funds if index]
    if not funds:
        return None
    total = df["value"].sum()
    direct = df.drop(index=[row.name for _, row in funds])
    counted = direct[~direct["sector"].isin(rules.SECTOR_EXEMPT)]
    sectors = counted.groupby("sector")["value"].sum() / total
    stocks = direct[direct["asset_type"] == "stock"]
    held = (stocks["value"] / total).groupby(stocks["asset"].map(canonical_name)).sum()
    us = float(direct.loc[direct["region"] == "US", "value"].sum() / total) if has_region else 0.0
    through = pd.Series(dtype=float)
    for index, row in funds:
        share = row["value"] / total
        sectors = sectors.add(index_part(index, "sector") * share, fill_value=0)
        through = through.add(index_part(index, "company") * share, fill_value=0)
        if has_region:
            us_part = index_part(index, "country").get("US")
            us += share * (us_part if us_part is not None else float(row["region"] == "US"))

    sectors = sectors.sort_values(ascending=False, kind="stable")
    through = through.sort_values(ascending=False, kind="stable")
    parts = [
        f"Including what your funds hold, about {fmt_pct(float(sectors.iloc[0]))} of your money "
        f"is in {sectors.index[0]}" + (f" and about {fmt_pct(us)} in the US." if has_region else ".")
    ]
    top = ", ".join(f"{name} {fmt_pct(float(w))}" for name, w in through.head(3).items())
    parts.append(f"Largest companies through your funds: {top}.")
    both = (held + through).dropna().sort_values(ascending=False, kind="stable")
    if not both.empty:
        name = both.index[0]
        parts.append(
            f"{name}: {fmt_pct(float(held[name]))} directly plus {fmt_pct(float(through[name]))} "
            f"through your funds, about {fmt_pct(float(both.iloc[0]))} in total."
        )
    over = not both.empty and float(both.iloc[0]) > rules.LIMITS["asset"]["limit"] + EPS
    return Insight("funds", "Inside your funds", " ".join(parts), "Watch" if over else "Info",
                   rules.INDEX_SOURCE)


# ---------------------------------------------------------------------------
# Limits and score
# ---------------------------------------------------------------------------


def status_for(weight: float, limit: dict) -> str:
    """Green below yellow_from, yellow up to the limit (ends included), orange up to
    the limit plus its margin (for a limit that has one), red above."""
    if weight < limit["yellow_from"] - EPS:
        return GREEN
    if weight <= limit["limit"] + EPS:
        return YELLOW
    if weight <= limit["limit"] + limit.get("margin", 0) + EPS:
        return ORANGE
    return RED


def limit_part(shares: pd.Series, limit: float) -> float:
    """100 minus a penalty for every category above the limit: its excess, measured in
    limits, squared, so a bigger breach costs more than several small ones."""
    over = ((shares - limit).clip(lower=0) / limit) ** 2
    return max(0.0, 100 - 100 * float(over.sum()))


def limit_score(weight: float, limit: dict) -> float:
    """The part one category would score on its own (orders the warnings)."""
    return limit_part(pd.Series([weight]), limit["limit"])


# Positions that are one holding each, for the spread: a company's stock or bond, or
# one precious metal (D12). Funds, government bonds and cash add nothing to the HHI.
COMPANY_TYPES = ("stock", "corporate bond", "precious metal")


def spread(df: pd.DataFrame) -> tuple[float, float]:
    """The HHI of the single companies (each one's share in %, squared, added up) and
    the number of equal stocks it is worth (10,000 / HHI; infinite with no company).
    A fund on a small index adds its share split over the index's companies (D11)."""
    total = df["value"].sum()
    companies = df[df["asset_type"].isin(COMPANY_TYPES)]
    shares = companies.groupby("asset")["value"].sum() / total * 100
    hhi = float((shares**2).sum())
    for _, row in df.iterrows():
        count = small_index_size(row)
        if count:
            hhi += (row["value"] / total * 100) ** 2 / count
    return hhi, (10_000 / hhi if hhi > EPS else math.inf)


def small_index_size(row) -> int:
    """How many companies a broad ETF's small index holds at most; 0 if it isn't one."""
    if row["asset_type"] != "ETF" or row["sector"] != rules.BROAD_ETF_SECTOR:
        return 0
    name = canonical_name(row["asset"]).lower()  # "TVBETETF" -> "etf bet patria-tradeville"
    return next((count for pattern, count in rules.SMALL_INDEX_FUNDS if re.search(pattern, name)), 0)


def spread_score(equal_stocks: float) -> float:
    return min(100.0, 100 * equal_stocks / rules.WELL_DIVERSIFIED_STOCKS)


def tier_for(score: int) -> str:
    return next(tier for tier, lowest in rules.SCORE_TIERS if score >= lowest)


def evaluate_limits(df: pd.DataFrame) -> list[LimitResult]:
    results = []
    for key, limit in rules.LIMITS.items():
        shares = limit_weights(df, key)
        category = shares.index[0] if len(shares) else ""
        weight = float(shares.iloc[0]) if len(shares) else 0.0
        results.append(
            LimitResult(
                key=key,
                label=limit["label"],
                why=limit["why"],
                source=limit.get("source", ""),
                yellow_from=limit["yellow_from"],
                limit=limit["limit"],
                category=category,
                weight=weight,
                status=status_for(weight, limit),
                score=limit_part(shares, limit["limit"]),
            )
        )
    return results


def overall_score(limits: list[LimitResult], spread_part: float) -> int:
    """The average of the limit parts and the spread part."""
    return round_half_up((sum(r.score for r in limits) + spread_part) / (len(limits) + 1))


def by_severity(items: list) -> list:
    """Red first, then orange, then yellow, then by how far over the threshold
    (lower score first)."""
    return sorted(items, key=lambda x: (STATUS_RANK[x.status], x.score, -x.weight))


def warnings_for(df: pd.DataFrame) -> list[LimitWarning]:
    found = []
    for key, limit in rules.LIMITS.items():
        for category, weight in limit_weights(df, key).items():
            status = status_for(weight, limit)
            if status == GREEN:
                continue
            text = (
                f"{WARNING_PREFIX[key]} {category}: {fmt_pct(weight)} "
                f"(limit {fmt_pct(limit['limit'])})"
            )
            found.append(
                LimitWarning(key, category, float(weight), status, limit_score(weight, limit), text)
            )
    return by_severity(found)


# ---------------------------------------------------------------------------
# Profile, insights and notes (no effect on the score)
# ---------------------------------------------------------------------------


def profile_for(df: pd.DataFrame) -> Profile:
    by_type = weights(df, "asset_type")
    breakdown = {t: float(by_type.get(t, 0.0)) for t in ASSET_TYPES}
    defensive = sum(breakdown[t] for t in BOND_TYPES) + breakdown["cash"]
    return Profile(defensive, breakdown)


def exposure_notes(df: pd.DataFrame, has_region: bool) -> list[Note]:
    """The region note, the only exposure note left (D10): most of the portfolio in
    one region."""
    notes = []
    if has_region:
        region, share = largest_region(df)
        if share > rules.SINGLE_REGION_NOTE + EPS:
            notes.append(Note(
                "region",
                f"{fmt_pct(share)} of your portfolio is in {REGION_PHRASES.get(region, region)}: "
                "it depends mostly on one region's economy. This may be intentional.",
            ))
    return notes


def insights_for(
    df: pd.DataFrame, limits: list[LimitResult], notes: list[Note], has_region: bool
) -> list[Insight]:
    """Plain-language facts, marked "Watch" when the same dimension has a limit that
    is not OK or the region note, "Info" otherwise."""
    flagged = {r.key for r in limits if r.status != GREEN} | {n.key for n in notes}

    def label(key: str) -> str:
        return "Watch" if key in flagged else "Info"

    insights = []

    insights.append(hhi_insight(df))

    positions = weights(df, "asset")
    count = len(positions)

    if count <= 5:
        text = f"With {count} position{'s' if count > 1 else ''}, your top 5 are the whole portfolio."
    else:
        text = f"Your 5 largest positions make up {fmt_pct(positions.head(5).sum())} of your portfolio."
    insights.append(Insight("top5", "Top 5 positions", text, label("asset")))

    other = 1 - float(weights(df, "currency").get(HOME_CURRENCY, 0.0))
    if other <= EPS:
        text = f"All of your portfolio is in {HOME_CURRENCY}."
    elif other >= 1 - EPS:
        text = f"All of your portfolio is in currencies other than {HOME_CURRENCY}."
    else:
        text = f"{fmt_pct(other)} of your portfolio is in currencies other than {HOME_CURRENCY}."
    if other > EPS:
        text += (" If they fall against the leu, these holdings lose value in lei; over long "
                 "periods this tends to matter less than company and sector risk.")
    insights.append(Insight("other_currencies", "Other currencies", text, "Info"))

    covered = len(set(df["sector"]) & set(rules.GICS_SECTORS))
    total = len(rules.GICS_SECTORS)
    broad_funds = ((df["asset_type"] == "ETF") & (df["sector"] == rules.BROAD_ETF_SECTOR)).any()
    if broad_funds and covered:
        text = (
            f"You cover {covered} of {total} GICS sectors directly, "
            "plus global funds that span all sectors."
        )
    elif broad_funds:
        text = "You hold global funds that span all sectors."
    else:
        text = f"You cover {covered} of {total} GICS sectors."
    insights.append(Insight("sector_coverage", "Sector coverage", text, label("sector")))

    if has_region:
        global_share = float(weights(df, "region").get(GLOBAL_REGION, 0.0))
        region, share = largest_region(df)
        source = ""
        if region:
            phrase = REGION_PHRASES.get(region, region)
            text = f"{fmt_pct(share)} of your money is in {phrase}"
            text += f", and {fmt_pct(global_share)} in global funds." if global_share > EPS else "."
            world = rules.WORLD_MARKET_SHARE.get(region)
            if world is not None:  # a neutral comparison, not a target (decision D4)
                text += (f" For comparison, {phrase} is about {fmt_pct(round(world, 2))} of the "
                         "value of all listed companies in the world.")
                source = rules.WORLD_MARKET_SOURCE
        else:
            text = "All of your money is in global funds."
        insights.append(Insight("regions", "Regions", text, label("region"), source))

    funds = funds_insight(df, has_region)
    if funds:
        insights.append(funds)

    metals = float(weights(df, "asset_type").get("precious metal", 0.0))
    if metals > EPS:
        text = (
            f"{fmt_pct(metals)} of your portfolio is in precious metals. They have no sector, but "
            "each one counts as a single position, as EU fund rules treat a gold ETC."
        )
        insights.append(Insight("precious_metals", "Precious metals", text, "Info"))

    return insights


HHI_EXPLAINED = (
    "How it works: take each company's share of your portfolio in %, square it, and add "
    "them up. One company with all your money gives 10,000; 100 equal companies give 100. "
    "The lower, the more spread out. Each precious metal counts as one holding; funds, "
    "government bonds and cash "
    "count as spread out. Dividing 10,000 by the HHI gives the number of equal stocks it is "
    "worth. Below 333 (30 or more equal stocks) is well spread: research finds that a "
    "well-diversified portfolio of randomly chosen stocks needs at least 30 (Statman, 1987). "
    "333 to 1,000 (10 to 29) is partly spread: 10 equal stocks would each sit at the 10% "
    "limit. 1,000 to 2,500 (4 to 9) is concentrated: 4 equal stocks would each be 25%, the "
    "size of the sector limit. Above 2,500 is very concentrated. The HHI is the standard "
    "measure of concentration, used for example by competition authorities."
)


def hhi_band(equal_stocks: float) -> int:
    """Which HHI band a portfolio is in: 0 well spread ... 3 very concentrated."""
    return next(i for i, (lowest, _) in enumerate(rules.HHI_BANDS) if equal_stocks >= lowest)


def hhi_insight(df: pd.DataFrame) -> Insight:
    """The concentration index of the single companies, in plain words, with a (?)."""
    hhi, equal = spread(df)
    target = rules.WELL_DIVERSIFIED_STOCKS
    if hhi <= EPS:
        text = ("Your HHI is 0: no single company carries your money, which is all in funds, "
                "government bonds or cash.")
    else:
        worth = "more than 100" if equal > 100 else f"about {round_half_up(equal)}"
        band = rules.HHI_BANDS[hhi_band(equal)][1]
        text = (f"Your concentration index (HHI) is {round_half_up(hhi):,}: your companies are "
                f"spread as if you held {worth} equal stocks, which is {band}.")
    return Insight("hhi", "Concentration index (HHI)", text, "Info" if equal >= target else "Watch",
                   HHI_EXPLAINED)


# How each limit is named in the summary.
SUMMARY_NOUNS = {"sector": "sector", "asset": "single company"}


def summary_for(df: pd.DataFrame, limits: list[LimitResult], warnings: list[LimitWarning],
                notes: list[Note], equal_stocks: float) -> Summary:
    """What is good (at most 3) and what to look at, from the same facts as the score."""
    good, look_at = [], []
    for r in by_severity(limits):
        limit = fmt_pct(r.limit)
        if r.status == GREEN:
            if r.category:
                good.append(f"No {SUMMARY_NOUNS[r.key]} is above the {limit} limit "
                            f"(the largest: {r.category}, {fmt_pct(r.weight)}).")
            continue
        others = len([w for w in warnings if w.key == r.key]) - 1
        where = "close to" if r.status == YELLOW else "above"
        more = f" (and {others} more)" if others > 0 else ""
        look_at.append(f"{r.category} is {fmt_pct(r.weight)} of your money, {where} the {limit} limit{more}.")
    target = rules.WELL_DIVERSIFIED_STOCKS
    if equal_stocks == math.inf:
        good.append("No single company carries your money: it is in funds, government bonds or cash.")
    elif equal_stocks >= target:
        good.append(f"Your companies are spread as if over {round_half_up(equal_stocks)} equal stocks; "
                    f"{target} or more counts as well diversified.")
    else:
        look_at.append(f"Your companies are spread as if over only {round_half_up(equal_stocks)} "
                       f"equal stocks; research suggests at least {target}.")
    broad_rows = (df["asset_type"] == "ETF") & (df["sector"] == rules.BROAD_ETF_SECTOR)
    broad_rows &= ~df.apply(small_index_size, axis=1).astype(bool)  # 20 companies are not "many"
    broad = float(df.loc[broad_rows, "value"].sum() / df["value"].sum())
    if broad > EPS:
        good.append(f"{fmt_pct(broad)} is in broad funds, which spread money over many companies.")
    look_at += [n.text.split(":")[0] + ": most of it depends on one region's economy." for n in notes]
    return Summary(good[:3], look_at)


# ---------------------------------------------------------------------------
# Full analysis and data for the screens
# ---------------------------------------------------------------------------


def analyze(df: pd.DataFrame) -> Analysis:
    """Run every check on a validated portfolio."""
    has_region = "region" in df.columns
    info = [] if has_region else ["No region column: the analysis continues without regions."]

    positions = df.assign(weight=df["value"] / df["value"].sum())
    positions = positions.sort_values("value", ascending=False, kind="stable").reset_index(drop=True)

    limits = evaluate_limits(df)
    hhi, equal_stocks = spread(df)
    spread_part = spread_score(equal_stocks)
    score = overall_score(limits, spread_part)
    score = min([score] + [rules.SCORE_CAPS[r.status] for r in limits if r.status in rules.SCORE_CAPS])
    warnings = warnings_for(df)
    notes = exposure_notes(df, has_region)
    insights = insights_for(df, limits, notes, has_region)

    return Analysis(
        positions=positions,
        has_region=has_region,
        info=info,
        limits=limits,
        score=score,
        tier=tier_for(score),
        spread_score=spread_part,
        hhi=hhi,
        equal_stocks=equal_stocks,
        warnings=warnings,
        profile=profile_for(df),
        insights=insights,
        notes=notes,
        cap_mix=cap_mix(df),
        summary=summary_for(df, limits, warnings, notes, equal_stocks),
    )


def chart_dimensions(analysis: Analysis) -> dict[str, str]:
    """Dimensions available in the Charts tab (no region if the column is missing)."""
    return {k: v for k, v in CHART_DIMENSIONS.items() if k != "region" or analysis.has_region}


def chart_data(analysis: Analysis, dimension: str) -> tuple[pd.DataFrame, float | None]:
    """Bars for one dimension, largest first, with a status per bar, whether the bar
    counts towards the limit, and the limit to draw (None for currency and region).
    Exempt categories are always green."""
    df = analysis.positions
    shares = weights(df, dimension)
    limit = rules.LIMITS.get(dimension)
    counted = set(limit_weights(df, dimension).index) if limit else set()
    statuses = [
        status_for(share, limit) if category in counted else GREEN
        for category, share in shares.items()
    ]
    bars = pd.DataFrame(
        {
            "category": shares.index,
            "weight": shares.values,
            "status": statuses,
            "counted": [category in counted for category in shares.index],
        }
    )
    return bars, (limit["limit"] if limit else None)


# How a bar stands against its limit, in words: the bar's colour says the same.
LIMIT_PHRASES = {
    GREEN: "Below the {limit} limit",
    YELLOW: "Close to the {limit} limit",
    ORANGE: "Just over the {limit} limit",
    RED: "Over the {limit} limit",
}


def limit_phrase(status: str, counted: bool, limit: float | None) -> str:
    if limit is None:
        return ""
    if not counted:
        return "Not counted towards the limit"
    return LIMIT_PHRASES[status].format(limit=fmt_pct(limit))


def asset_class_slices(profile: Profile) -> pd.DataFrame:
    """Donut slices: stocks and ETFs grouped as Equity, then bonds, cash and precious
    metals. Empty slices are left out."""
    b = profile.breakdown
    bonds = sum(b[t] for t in BOND_TYPES)
    slices = pd.DataFrame(
        {
            "label": ["Equity", "Bonds", "Cash", "Precious metals"],
            "share": [b["stock"] + b["ETF"], bonds, b["cash"], b["precious metal"]],
            "detail": [
                f"Stocks {fmt_pct(b['stock'])} · ETFs {fmt_pct(b['ETF'])}",
                f"{fmt_pct(bonds)} of your portfolio",
                f"{fmt_pct(b['cash'])} of your portfolio",
                f"{fmt_pct(b['precious metal'])} of your portfolio",
            ],
        }
    )
    return slices[slices["share"] > EPS].reset_index(drop=True)


def bar_members(analysis: Analysis, dimension: str) -> dict[str, list[tuple[str, float]]]:
    """For each bar of a chart (a sector, currency or region), the positions in it
    with their weights, largest first."""
    members = {}
    positions = with_fund_sectors(analysis.positions) if dimension == "sector" else analysis.positions
    for _, row in positions.iterrows():  # positions are already largest first
        members.setdefault(row[dimension], []).append((row["asset"], float(row["weight"])))
    return members


def label_explanations(categories) -> list[str]:
    """Explanations for the "Diversified" and "n/a" labels that appear in `categories`."""
    present = set(categories)
    return [text for label, text in LABEL_EXPLANATIONS.items() if label in present]


def cap_shares(analysis: Analysis) -> pd.DataFrame:
    """Share of your stocks in each cap segment (small, mid, large)."""
    return pd.DataFrame(
        {
            "segment": CAP_SEGMENTS,
            "yours": [float(analysis.cap_mix.get(s, 0.0)) for s in CAP_SEGMENTS],
        }
    )


def stocks_table(analysis: Analysis) -> pd.DataFrame:
    """The individual stocks, largest first."""
    columns = ["asset", "sector", "market_cap", "region", "weight"]
    stocks = analysis.positions[analysis.positions["asset_type"] == "stock"]
    return stocks[[c for c in columns if c in stocks.columns]].reset_index(drop=True)
