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

COLUMNS = ("asset", "value", "sector", "asset_type", "market_cap", "currency", "region")
OPTIONAL_COLUMNS = ("region",)
REQUIRED_COLUMNS = tuple(c for c in COLUMNS if c not in OPTIONAL_COLUMNS)
TEXT_COLUMNS = tuple(c for c in COLUMNS if c != "value")

# Sector spelling (any letter case, or an alias) -> official name.
SECTOR_NAMES = {
    **{name.lower(): name for name in rules.GICS_SECTORS + rules.SECTOR_EXEMPT},
    **{alias.lower(): name for alias, name in rules.SECTOR_ALIASES.items()},
}

ASSET_TYPES = ("stock", "ETF", "bond", "cash")
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
        "deposit": "cash",
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

GREEN, YELLOW, RED = "green", "yellow", "red"
STATUS_LABELS = {GREEN: "OK", YELLOW: "Watch", RED: "Over limit"}
STATUS_RANK = {RED: 0, YELLOW: 1, GREEN: 2}

# Word that starts a warning, e.g. "Position Apple: 8% (limit 10%)".
WARNING_PREFIX = {"sector": "Sector", "asset": "Position"}

# Dimensions offered in the Charts tab.
CHART_DIMENSIONS = {
    "sector": "Sector",
    "currency": "Currency",
    "asset": "Position",
    "region": "Region",
}

PROFILE_MESSAGES = {
    "Conservative": (
        "Most of your money is in bonds and cash: less exposed to stock market "
        "drops, with lower expected returns."
    ),
    "Balanced": (
        "Your money is split between equity and bonds or cash: moderately exposed "
        "to stock market drops, with moderate expected returns."
    ),
    "Dynamic": (
        "Most of your money is in stocks and equity funds: more exposed to stock "
        "market drops, with higher expected returns."
    ),
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
    name: str
    message: str
    defensive_share: float  # bonds + cash
    breakdown: dict[str, float]  # share of each asset type


@dataclass
class Insight:
    key: str
    title: str
    text: str
    label: str  # "Info" or "Watch"


@dataclass
class Note:
    key: str
    text: str
    tab: str  # where the details are shown

    @property
    def headline(self) -> str:
        """First sentence of the note, for the short At a glance row."""
        first = self.text.split(". ")[0]
        return first if first.endswith(".") else first + "."


@dataclass
class GlanceRow:
    text: str
    tab: str
    status: str  # RED or YELLOW for a problem, "" for a note or an insight


@dataclass
class Analysis:
    positions: pd.DataFrame  # input rows plus a "weight" column, largest first
    has_region: bool
    info: list[str]
    limits: list[LimitResult]
    score: int
    worst_status: str
    verdict: str
    warnings: list[LimitWarning]
    profile: Profile
    insights: list[Insight]
    notes: list[Note]
    cap_mix: pd.Series  # share of each cap segment within the stocks
    glance: list[GlanceRow]


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
    """Share of the total value in each category of `column`, largest first."""
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
# Limits and score
# ---------------------------------------------------------------------------


def status_for(weight: float, limit: dict) -> str:
    """Green below yellow_from, yellow up to the limit (ends included), red above."""
    if weight < limit["yellow_from"] - EPS:
        return GREEN
    if weight <= limit["limit"] + EPS:
        return YELLOW
    return RED


def limit_score(weight: float, limit: dict) -> float:
    """100 up to yellow_from, 100 -> 80 linearly up to the limit, then down to 20."""
    yellow_from, cap = limit["yellow_from"], limit["limit"]
    if weight <= yellow_from + EPS:
        return 100.0
    if weight <= cap + EPS:
        return 100 - 20 * (weight - yellow_from) / (cap - yellow_from)
    return 80 - 60 * min(weight / cap - 1, 1)


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
                yellow_from=limit["yellow_from"],
                limit=limit["limit"],
                category=category,
                weight=weight,
                status=status_for(weight, limit),
                score=limit_score(weight, limit),
            )
        )
    return results


def overall_score(limits: list[LimitResult]) -> int:
    return round_half_up(sum(r.score for r in limits) / len(limits))


def by_severity(items: list) -> list:
    """Red first, then yellow, then by how far over the threshold (lower score first)."""
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


def verdict(limits: list[LimitResult]) -> str:
    issues = by_severity([r for r in limits if r.status != GREEN])
    if not issues:
        return "No limit breaches."
    worst = issues[0]
    detail = f"{worst.label.lower()} ({worst.category} {fmt_pct(worst.weight)})"
    if len(issues) == 1:
        return f"1 issue: {detail}."
    return f"{len(issues)} issues. The most serious: {detail}."


# ---------------------------------------------------------------------------
# Profile, insights and notes (no effect on the score)
# ---------------------------------------------------------------------------


def profile_for(df: pd.DataFrame) -> Profile:
    by_type = weights(df, "asset_type")
    breakdown = {t: float(by_type.get(t, 0.0)) for t in ASSET_TYPES}
    defensive = breakdown["bond"] + breakdown["cash"]
    if defensive > rules.CONSERVATIVE_ABOVE + EPS:
        name = "Conservative"
    elif defensive < rules.DYNAMIC_BELOW - EPS:
        name = "Dynamic"
    else:
        name = "Balanced"
    return Profile(name, PROFILE_MESSAGES[name], defensive, breakdown)


def exposure_notes(df: pd.DataFrame, has_region: bool) -> list[Note]:
    notes = []
    caps = cap_mix(df)
    small = float(caps.get("small", 0.0))
    large = float(caps.get("large", 0.0))
    small_reference = rules.REFERENCE_CAP_MIX["small"]

    if small > rules.SMALL_NOTE_MULTIPLE * small_reference + EPS:
        notes.append(
            Note(
                "small_cap",
                f"Small caps are {fmt_pct(small)} of your stocks vs about "
                f"{fmt_pct(small_reference)} of the total US market. Historically they "
                "have been more volatile and less liquid; research is divided on whether "
                "they earn a higher return. This may be intentional.",
                "Stocks",
            )
        )
    if large > rules.LARGE_NOTE_SHARE + EPS:
        notes.append(
            Note(
                "large_cap",
                "Your stocks behave close to a large-cap index, with little exposure to "
                "mid and small companies.",
                "Stocks",
            )
        )
    if has_region and largest_region(df)[1] > rules.SINGLE_REGION_NOTE + EPS:
        notes.append(
            Note(
                "region",
                "Most of your portfolio depends on one region's economy. This may be "
                "intentional.",
                "Charts › Region",
            )
        )
    currency, share = largest_foreign_currency(df)
    if share > rules.FOREIGN_CURRENCY_NOTE + EPS:
        notes.append(
            Note(
                "currency",
                f"{fmt_pct(share)} of your portfolio is in {currency}. If {currency} falls "
                "against the leu, these holdings lose value in lei. Over long periods this "
                "tends to matter less than company and sector risk.",
                "Charts › Currency",
            )
        )
    return notes


def insights_for(
    df: pd.DataFrame, limits: list[LimitResult], notes: list[Note], has_region: bool
) -> list[Insight]:
    """Plain-language facts. "Watch" when the same dimension already has a
    yellow or red limit (or a region or currency note); "Info" otherwise."""
    flagged = {r.key for r in limits if r.status != GREEN}
    flagged |= {n.key for n in notes if n.key in ("region", "currency")}

    def label(key: str) -> str:
        return "Watch" if key in flagged else "Info"

    insights = []

    positions = weights(df, "asset")
    count = len(positions)
    equal = round_half_up(1 / float((positions**2).sum()))
    if count == 1:
        text = "You hold a single position."
    elif equal >= count:
        text = f"You hold {count} positions of about equal size."
    elif equal == 1:
        text = f"You hold {count} positions, but your portfolio behaves like a single one."
    else:
        text = f"You hold {count} positions, but your portfolio behaves like {equal} equal ones."
    insights.append(Insight("effective_positions", "Effective positions", text, label("asset")))

    if count <= 5:
        text = f"With {count} position{'s' if count > 1 else ''}, your top 5 are the whole portfolio."
    else:
        text = f"Your 5 largest positions make up {fmt_pct(positions.head(5).sum())} of your portfolio."
    insights.append(Insight("top5", "Top 5 positions", text, label("asset")))

    sectors = limit_weights(df, "sector")
    if sectors.empty:
        stress = "No single sector to stress-test: your holdings are broad funds, bonds or cash."
        largest = "You have no single-sector exposure outside broad funds, bonds and cash."
    else:
        sector, share = sectors.index[0], float(sectors.iloc[0])
        stress = (
            f"If {sector} fell {fmt_pct(rules.STRESS_DROP)}, your portfolio would fall "
            f"about {fmt_pct(share * rules.STRESS_DROP)}."
        )
        largest = f"Your largest sector exposure is {sector}, at {fmt_pct(share)} of your portfolio."
    insights.append(Insight("stress_test", "Stress test", stress, label("sector")))
    insights.append(Insight("largest_sector", "Largest sector", largest, label("sector")))

    other = 1 - float(weights(df, "currency").get(HOME_CURRENCY, 0.0))
    if other <= EPS:
        text = f"All of your portfolio is in {HOME_CURRENCY}."
    elif other >= 1 - EPS:
        text = f"All of your portfolio is in currencies other than {HOME_CURRENCY}."
    else:
        text = f"{fmt_pct(other)} of your portfolio is in currencies other than {HOME_CURRENCY}."
    insights.append(Insight("other_currencies", "Other currencies", text, label("currency")))

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
        text = f"Global funds cover {fmt_pct(global_share)} of your portfolio"
        text += f"; the largest single region is {region} with {fmt_pct(share)}." if region else "."
        insights.append(Insight("regions", "Regions", text, label("region")))

    return insights


def at_a_glance(
    limits: list[LimitResult],
    warnings: list[LimitWarning],
    notes: list[Note],
    insights: list[Insight],
    max_rows: int = 3,
) -> list[GlanceRow]:
    """Up to 3 rows: red limits, yellow limits, then one note or the best insight."""
    rows = []
    for result in by_severity([r for r in limits if r.status != GREEN]):
        own = [w for w in warnings if w.key == result.key]
        text = own[0].text
        if len(own) > 1:
            text += f" and {len(own) - 1} more"
        rows.append(GlanceRow(text, "Overview", result.status))
    rows = rows[:max_rows]

    if len(rows) < max_rows:
        if notes:
            rows.append(GlanceRow(notes[0].headline, notes[0].tab, ""))
        elif insights:
            best = next((i for i in insights if i.label == "Watch"), insights[0])
            rows.append(GlanceRow(best.text, "Overview", ""))
    return rows


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
    warnings = warnings_for(df)
    notes = exposure_notes(df, has_region)
    insights = insights_for(df, limits, notes, has_region)

    return Analysis(
        positions=positions,
        has_region=has_region,
        info=info,
        limits=limits,
        score=overall_score(limits),
        worst_status=min((r.status for r in limits), key=STATUS_RANK.get),
        verdict=verdict(limits),
        warnings=warnings,
        profile=profile_for(df),
        insights=insights,
        notes=notes,
        cap_mix=cap_mix(df),
        glance=at_a_glance(limits, warnings, notes, insights),
    )


def chart_dimensions(analysis: Analysis) -> dict[str, str]:
    """Dimensions available in the Charts tab (no region if the column is missing)."""
    return {k: v for k, v in CHART_DIMENSIONS.items() if k != "region" or analysis.has_region}


def chart_data(analysis: Analysis, dimension: str) -> tuple[pd.DataFrame, float | None]:
    """Bars for one dimension, largest first, with a status per bar, and the limit
    to draw (None for region). Exempt categories are always green."""
    df = analysis.positions
    shares = weights(df, dimension)
    limit = rules.LIMITS.get(dimension)
    counted = set(limit_weights(df, dimension).index) if limit else set()
    statuses = [
        status_for(share, limit) if category in counted else GREEN
        for category, share in shares.items()
    ]
    bars = pd.DataFrame({"category": shares.index, "weight": shares.values, "status": statuses})
    return bars, (limit["limit"] if limit else None)


def asset_class_slices(profile: Profile) -> pd.DataFrame:
    """Donut slices: stocks and ETFs grouped as Equity, then bonds and cash.
    Empty slices are left out."""
    b = profile.breakdown
    slices = pd.DataFrame(
        {
            "label": ["Equity", "Bonds", "Cash"],
            "share": [b["stock"] + b["ETF"], b["bond"], b["cash"]],
            "detail": [
                f"Stocks {fmt_pct(b['stock'])} · ETFs {fmt_pct(b['ETF'])}",
                f"{fmt_pct(b['bond'])} of your portfolio",
                f"{fmt_pct(b['cash'])} of your portfolio",
            ],
        }
    )
    return slices[slices["share"] > EPS].reset_index(drop=True)


def cap_comparison(analysis: Analysis) -> pd.DataFrame:
    """Your stocks vs the reference market, per cap segment (small, mid, large)."""
    return pd.DataFrame(
        {
            "segment": CAP_SEGMENTS,
            "yours": [float(analysis.cap_mix.get(s, 0.0)) for s in CAP_SEGMENTS],
            "market": [rules.REFERENCE_CAP_MIX[s] for s in CAP_SEGMENTS],
        }
    )


def stocks_table(analysis: Analysis) -> pd.DataFrame:
    """The individual stocks, largest first."""
    columns = ["asset", "sector", "market_cap", "region", "weight"]
    stocks = analysis.positions[analysis.positions["asset_type"] == "stock"]
    return stocks[[c for c in columns if c in stocks.columns]].reset_index(drop=True)
