"""Thresholds and texts used by Portfolio Health Check.

EXAMPLE VALUES ONLY: every number and text below is a placeholder until it is
replaced with the rules from the author's thesis.

All shares are fractions of the total portfolio value (0.30 means 30%).
"""

# ---------------------------------------------------------------------------
# Scored limits
# ---------------------------------------------------------------------------
# Status of a limit, based on its largest non-exempt weight:
#   OK          below yellow_from
#   Watch       from yellow_from up to limit (both ends included)
#   Over limit  above limit

LIMITS = {
    "sector": {
        "label": "Sector",
        "yellow_from": 0.24,  # EXAMPLE
        "limit": 0.30,  # EXAMPLE
        "why": "When one sector falls, everything in it tends to fall together.",  # EXAMPLE
    },
    "asset": {
        "label": "Single position",
        # Same thresholds as the UCITS 5/10/40 rule for funds
        # (Directive 2009/65/EC, art. 52). Here the rule covers company risk
        # only: stocks and single-sector ETFs.
        "yellow_from": 0.05,  # EXAMPLE
        "limit": 0.10,  # EXAMPLE
        "why": "A single company's bad news can move your whole portfolio.",  # EXAMPLE
    },
    "currency": {
        "label": "Currency",
        "yellow_from": 0.56,  # EXAMPLE
        "limit": 0.70,  # EXAMPLE
        "why": "If that currency weakens against the leu, your portfolio loses value in lei.",  # EXAMPLE
    },
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

# Stress test: drop applied to the largest sector.
STRESS_DROP = 0.20  # EXAMPLE
