"""Thresholds and texts used by Portfolio Health Check.

EXAMPLE VALUES unless a comment gives a source: they are placeholders until
they are replaced with the rules from the author's thesis.

All shares are fractions of the total portfolio value (0.30 means 30%).
"""

# ---------------------------------------------------------------------------
# Scored limits
# ---------------------------------------------------------------------------
# Status of a limit, based on its largest non-exempt weight:
#   OK          below yellow_from
#   Watch       from yellow_from up to limit (both ends included)
#   Just over   above limit, up to limit + margin (only for a limit with a margin)
#   Over limit  above that

LIMITS = {
    "sector": {
        "label": "Sector",
        # Documented (decision D3, docs/decisions.md): the US regulator (SEC, Guide 19
        # to Form N-1A) treats a fund with 25% or more of its assets in one industry
        # as concentrated. The Watch threshold keeps the old ratio to the limit (80%),
        # and the margin is a safety margin of our own choice.
        "yellow_from": 0.20,  # EXAMPLE
        "limit": 0.25,
        "margin": 0.05,  # EXAMPLE
        "why": "When one sector falls, everything in it tends to fall together.",  # EXAMPLE
        "source": (
            "Why 25%: the US regulator (SEC) treats a fund with 25% or more in one "
            "industry as concentrated. Up to 5 points over it shows as Just over: "
            "that safety margin is this app's choice."
        ),
    },
    "asset": {
        "label": "Single position",
        # Documented, not an example (decision D2, docs/decisions.md). No regulator
        # sets a limit for an individual investor, so these are the limits the law
        # sets for diversified funds:
        #   EU:  UCITS, Directive 2009/65/EC, art. 52: at most 10% in one issuer,
        #        and holdings over 5% together at most 40% of the fund.
        #   US:  Investment Company Act 1940, section 5(b)(1): a diversified fund
        #        holds at most 5% in one issuer (for 75% of its assets).
        # Here the rule covers company risk only: stocks and single-sector ETFs.
        "yellow_from": 0.05,
        "limit": 0.10,
        "why": "A single company's bad news can move your whole portfolio.",  # EXAMPLE
        "source": (
            "Why 5% and 10%: EU law lets a fund put at most 10% in one company, "
            "and US law caps a diversified fund at 5%. These are fund rules, used "
            "here as a reference for one investor."
        ),
    },
}
# Currency is not a scored limit (decision of 29 Oct 2026, see docs/decisions.md):
# over long horizons it matters less for stocks than company and sector risk,
# so the share in other currencies is shown as an insight instead (D1, D10).

# ---------------------------------------------------------------------------
# The score (decision D9)
# ---------------------------------------------------------------------------
# Three parts of equal weight (our choice), each from 0 to 100:
#   sector     100 minus a penalty for every sector above its limit
#   position   the same for every single company above its limit
#   spread     how many equal stocks the single companies are worth (10,000 / HHI),
#              out of WELL_DIVERSIFIED_STOCKS
# The penalty measures each excess in limits and squares it, so a bigger breach
# costs more than several small ones: a position of 15% (half a limit over) costs
# 25 points, one of 20% (a full limit over) costs all 100. Watch and Just over are
# warnings and cost nothing.
WELL_DIVERSIFIED_STOCKS = 30  # Statman (1987): at least 30 randomly chosen stocks

# What an HHI means, in bands of "equal stocks" (10,000 / HHI), each from a reason:
#   30 or more   well spread         Statman (1987)          HHI below 333
#   10 to 29     partly spread       10 equal = each at the 10% limit     333-1,000
#   4 to 9       concentrated        4 equal = each at 25%, the sector limit  1,000-2,500
#   under 4      very concentrated                           HHI above 2,500
HHI_BANDS = ((30, "well spread"), (10, "partly spread"), (4, "concentrated"), (0, "very concentrated"))

# Score tiers, best first, with the lowest score of each (our choice).
SCORE_TIERS = (("A+", 95), ("A", 85), ("B", 70), ("C", 50), ("D", 0))
# The highest score while a limit is breached, so the tier never contradicts a
# warning: Just over keeps you out of A+, Over limit out of A (our choice).
SCORE_CAPS = {"orange": 94, "red": 84}

# The 11 official GICS sectors (not an example: this is the standard).
GICS_SECTORS = (
    "Energy",
    "Materials",
    "Industrials",
    "Consumer Discretionary",
    "Consumer Staples",
    "Health Care",
    "Financials",
    "Information Technology",
    "Communication Services",
    "Utilities",
    "Real Estate",
)

# Common names accepted in uploaded CSVs and replaced by the official GICS
# name. Matching ignores letter case.
SECTOR_ALIASES = {
    "Technology": "Information Technology",
    "Tech": "Information Technology",
    "IT": "Information Technology",
    "Healthcare": "Health Care",
    "Telecom": "Communication Services",
    "Telecommunications": "Communication Services",
    "Telecommunication Services": "Communication Services",
    "Financial Services": "Financials",
    "Basic Materials": "Materials",
    "Consumer Cyclical": "Consumer Discretionary",
    "Consumer Defensive": "Consumer Staples",
}

# Sectors that never count towards the sector limit.
SECTOR_EXEMPT = ("Diversified", "n/a")  # EXAMPLE

# Positions that never count towards the single-position limit: government bonds
# ("bond"), cash, precious metals, and broad ETFs (an ETF whose sector is
# BROAD_ETF_SECTOR). Government bonds: a fund may hold up to 100% in them (UCITS,
# art. 54). Corporate bonds do count: their risk is the company's (decision D7).
# Precious metals are not companies; they are shown as information only (D7).
ASSET_EXEMPT_TYPES = ("bond", "cash", "precious metal")
BROAD_ETF_SECTOR = "Diversified"  # EXAMPLE

# ---------------------------------------------------------------------------
# What index funds hold (decision D6)
# ---------------------------------------------------------------------------
# data/index_funds.csv (index, kind, name, weight, sector): sector weights, US share
# and largest companies of each index. The project ships WITHOUT it: the figures we
# had came from index providers whose terms don't allow redistribution (decision D8).
# Without the file, every broad fund simply counts as diversified. Public-domain
# figures from SEC N-PORT filings are planned. An ETF whose sector is
# BROAD_ETF_SECTOR is matched to an index by its name, first pattern first; S&P 500
# funds use the "MSCI USA" figures and FTSE All-World funds the "MSCI ACWI" ones.
INDEX_NAME_PATTERNS = (
    (r"nasdaq[ -]?100", "Nasdaq-100"),
    (r"s&p ?500|msci usa", "MSCI USA"),
    (r"all[- ]world|acwi|all country world|total world", "MSCI ACWI"),
    (r"msci world", "MSCI World"),
    (r"emerging|msci em\b|em imi", "MSCI Emerging Markets"),  # not MSCI EMU (euro area)
)
# Funds whose name has one of these words follow another index (small caps, a
# factor, a sector), so they are not matched.
INDEX_NAME_EXCLUDE = (
    r"small cap|dividend|equal weight|momentum|quality|value|growth|min(imum)? vol|esg|sri|"
    r"islamic|sector|information technology|health care|financials|energy"
)
# Indices narrower than the market they come from, because they leave sectors out:
# the Nasdaq-100 holds no financial companies (its published methodology). Their funds
# count towards the sector limit by what they hold; funds on a whole market
# (a country, a region, the world) stay diversified.
NARROW_INDICES = ("Nasdaq-100",)
INDEX_SOURCE = (
    "Funds are counted as copies of their index, using the figures in "
    "data/index_funds.csv. Only the largest companies of each index are listed."
)

# ---------------------------------------------------------------------------
# Exposure notes (informative, no effect on the score)
# ---------------------------------------------------------------------------
# Market cap segments used in the data:
#   large > $10bn, mid $2-10bn, small < $2bn.
# There is no market reference: the figures we had came from an index provider
# whose terms don't allow reproducing them (decision D8).



# Region note: one region (Global excluded) above this share of the portfolio.
SINGLE_REGION_NOTE = 0.80  # EXAMPLE

# Share of a region in the value of all listed companies in the world, for the
# Regions insight (decisions D4, D8). Source: World Bank, World Development
# Indicators, CM.MKT.LCAP.CD (market capitalization of listed domestic companies),
# 2025: United States $68.94 trillion of $141.30 trillion. Licence CC BY 4.0, which
# allows reuse with attribution. Update it once a year.
WORLD_MARKET_SHARE = {"US": 0.4879}
WORLD_MARKET_SOURCE = (
    "Source: World Bank, World Development Indicators, market capitalization of listed "
    "domestic companies, 2025: United States $68.9 trillion of $141.3 trillion "
    "worldwide. Licence: CC BY 4.0."
)


