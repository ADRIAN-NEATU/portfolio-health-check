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
# so it is shown as an exposure note instead (FOREIGN_CURRENCY_NOTE below).

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

# Positions that never count towards the single-position limit:
# bonds, cash, and broad ETFs (an ETF whose sector is BROAD_ETF_SECTOR).
ASSET_EXEMPT_TYPES = ("bond", "cash")  # EXAMPLE
BROAD_ETF_SECTOR = "Diversified"  # EXAMPLE

# ---------------------------------------------------------------------------
# Investor profile, from the share of bonds + cash
# ---------------------------------------------------------------------------
# above CONSERVATIVE_ABOVE -> Conservative
# from DYNAMIC_BELOW to CONSERVATIVE_ABOVE (both included) -> Balanced
# below DYNAMIC_BELOW -> Dynamic
CONSERVATIVE_ABOVE = 0.60  # EXAMPLE
DYNAMIC_BELOW = 0.30  # EXAMPLE

# ---------------------------------------------------------------------------
# Exposure notes (informative, no effect on the score)
# ---------------------------------------------------------------------------
# Market cap segments used in the data:
#   large > $10bn, mid $2-10bn, small < $2bn.
# Source: CRSP US Total Market Index, cap segments (factsheet; small includes
# micro). Approximate, to be checked against the current factsheet.
REFERENCE_CAP_MIX = {"large": 0.7, "mid": 0.15, "small": 0.15}  # EXAMPLE (the provider's figures were removed, D8)

# Small-cap note: small caps above this multiple of the reference share.
SMALL_NOTE_MULTIPLE = 2  # EXAMPLE

# Large-cap note: large caps above this share of the stocks.
LARGE_NOTE_SHARE = 0.90  # EXAMPLE

# Region note: one region (Global excluded) above this share of the portfolio.
SINGLE_REGION_NOTE = 0.80  # EXAMPLE

# Share of a region in the world stock market, for the Regions insight (decision
# D4). Source: MSCI ACWI Index factsheet (USD), 30 Sep 2026: large and mid-size
# companies in 23 developed and 24 emerging markets. Update it with the factsheet.
WORLD_MARKET_SHARE = {"US": 0.6}  # placeholder: the provider's figure was removed (D8)
WORLD_MARKET_SOURCE = (
    "Source: MSCI ACWI Index factsheet, 30 Sep 2026. The index covers large and "
    "mid-size companies in 23 developed and 24 emerging markets; the United States "
    "is the largest part of it."
)

# Currency note: one foreign currency (anything but RON) above this share of the
# portfolio. Same value as the old currency limit's yellow threshold.
FOREIGN_CURRENCY_NOTE = 0.56  # EXAMPLE

