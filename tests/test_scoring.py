import io
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import rules  # noqa: E402
import scoring  # noqa: E402
from scoring import GREEN, RED, YELLOW  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"

SECTOR = rules.LIMITS["sector"]
ASSET = rules.LIMITS["asset"]
CURRENCY = rules.LIMITS["currency"]


def make(rows, region=True):
    """Build a validated portfolio from tuples:
    (asset, value, sector, asset_type, market_cap, currency, region)."""
    columns = list(scoring.COLUMNS)
    df = pd.DataFrame(rows, columns=columns)
    if not region:
        df = df.drop(columns="region")
    return scoring.validate(df)


def sample(file_name):
    return scoring.analyze(scoring.load_portfolio(scoring.DATA_DIR / file_name))


# ---------------------------------------------------------------------------
# Sample portfolios: every expected result fixed explicitly
# ---------------------------------------------------------------------------

# file -> (sector, asset, currency, score, profile, notes)
EXPECTED = {
    "diversified.csv": (GREEN, GREEN, GREEN, 100, "Dynamic", []),
    "tech_heavy.csv": (RED, GREEN, GREEN, 83, "Dynamic", []),
    "all_in_ron.csv": (GREEN, GREEN, RED, 85, "Balanced", []),
    "beginner_3_stocks.csv": (GREEN, RED, GREEN, 73, "Balanced", []),
    "conservative_saver.csv": (GREEN, GREEN, GREEN, 100, "Conservative", []),
    "small_cap_fan.csv": (GREEN, GREEN, GREEN, 100, "Dynamic", ["small_cap"]),
    "one_global_etf.csv": (GREEN, GREEN, RED, 85, "Dynamic", []),
    "andrei.csv": (GREEN, YELLOW, RED, 81, "Dynamic", ["large_cap", "region"]),
}


def test_every_sample_is_listed():
    files = {p.name for p in scoring.DATA_DIR.glob("*.csv")} - {"template.csv"}
    assert files == set(scoring.SAMPLE_PORTFOLIOS) == set(EXPECTED)


@pytest.mark.parametrize("file_name", EXPECTED)
def test_sample_limit_statuses(file_name):
    analysis = sample(file_name)
    statuses = tuple(r.status for r in analysis.limits)
    assert [r.key for r in analysis.limits] == ["sector", "asset", "currency"]
    assert statuses == EXPECTED[file_name][:3]


@pytest.mark.parametrize("file_name", EXPECTED)
def test_sample_score_profile_and_notes(file_name):
    analysis = sample(file_name)
    _, _, _, score, profile, notes = EXPECTED[file_name]
    assert analysis.score == score
    assert analysis.profile.name == profile
    assert [n.key for n in analysis.notes] == notes


@pytest.mark.parametrize("file_name", EXPECTED)
def test_weights_sum_to_100_percent(file_name):
    df = scoring.load_portfolio(scoring.DATA_DIR / file_name)
    for column in ["asset", "sector", "asset_type", "currency", "region"]:
        assert scoring.weights(df, column).sum() == pytest.approx(1.0)
    caps = scoring.cap_mix(df)
    if (df["asset_type"] == "stock").any():
        assert caps.sum() == pytest.approx(1.0)
    else:
        assert caps.empty


def test_diversified_has_no_warnings_and_at_least_20_positions():
    analysis = sample("diversified.csv")
    assert len(analysis.positions) >= 20
    assert analysis.warnings == []
    assert analysis.verdict == "No limit breaches."


def test_tech_heavy_sector_is_technology_45_percent():
    analysis = sample("tech_heavy.csv")
    sector = analysis.limits[0]
    assert (sector.category, sector.weight) == ("Technology", pytest.approx(0.45))
    assert analysis.verdict == "1 issue: sector (Technology 45%)."


def test_andrei_at_a_glance():
    analysis = sample("andrei.csv")
    assert analysis.verdict == "2 issues. The most serious: currency (USD 100%)."
    assert [(row.status, row.tab) for row in analysis.glance] == [
        (RED, "Overview"),
        (YELLOW, "Overview"),
        ("", "Stocks"),
    ]
    assert analysis.glance[0].text == "Currency USD: 100% (limit 70%)"
    assert analysis.glance[1].text == "Position Apple: 8% (limit 10%) and 6 more"


def test_one_global_etf_region_is_global():
    analysis = sample("one_global_etf.csv")
    assert scoring.weights(analysis.positions, "region").to_dict() == {"Global": 1.0}
    regions = next(i for i in analysis.insights if i.key == "regions")
    assert regions.text == "Global funds cover 100% of your portfolio."


# ---------------------------------------------------------------------------
# Boundaries between colours and graded score
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "weight, expected",
    [
        (0.2399, GREEN),
        (0.24, YELLOW),  # exactly yellow_from
        (0.27, YELLOW),
        (0.30, YELLOW),  # exactly the limit
        (0.3001, RED),  # just above
    ],
)
def test_status_boundaries(weight, expected):
    assert scoring.status_for(weight, SECTOR) == expected


def test_status_tolerates_floating_point_error():
    limit = {"yellow_from": 0.50, "limit": 0.64}
    assert 0.8 * 0.8 > 0.64  # 0.6400000000000001
    assert scoring.status_for(0.8 * 0.8, limit) == YELLOW
    assert scoring.status_for(0.24 - 1e-12, SECTOR) == YELLOW


@pytest.mark.parametrize(
    "weight, expected",
    [
        (0.10, 100),
        (0.24, 100),  # yellow_from
        (0.27, 90),  # halfway between yellow_from and limit
        (0.30, 80),  # limit
        (0.45, 50),  # 80 - 60 * 0.5
        (0.60, 20),  # twice the limit
        (0.90, 20),  # floor
    ],
)
def test_graded_score(weight, expected):
    assert scoring.limit_score(weight, SECTOR) == pytest.approx(expected)


def test_overall_score_is_rounded_mean():
    # sector 100, asset 88 (8%), currency 80 (70%) -> 89.33 -> 89
    df = make(
        [
            ("A", 8, "Technology", "stock", "large", "USD", "US"),
            ("B", 62, "Diversified", "ETF", "n/a", "USD", "Global"),
            ("C", 30, "n/a", "cash", "n/a", "RON", "Romania"),
        ]
    )
    analysis = scoring.analyze(df)
    assert [round(r.score, 2) for r in analysis.limits] == [100, 88, 80]
    assert analysis.score == 89


def test_round_half_up():
    assert scoring.round_half_up(92.5) == 93
    assert scoring.round_half_up(92.49) == 92


def test_exempt_categories_do_not_count():
    df = make(
        [
            ("World ETF", 50, "Diversified", "ETF", "n/a", "EUR", "Global"),
            ("Bond", 30, "n/a", "bond", "n/a", "RON", "Romania"),
            ("Tech ETF", 20, "Technology", "ETF", "n/a", "USD", "US"),
        ]
    )
    limits = {r.key: r for r in scoring.analyze(df).limits}
    assert (limits["sector"].category, limits["sector"].weight) == ("Technology", 0.2)
    # the sector ETF counts as a single position, the broad ETF and the bond do not
    assert (limits["asset"].category, limits["asset"].weight) == ("Tech ETF", 0.2)


def test_warnings_sorted_red_then_yellow_then_size():
    df = make(
        [
            ("A", 12, "Technology", "stock", "large", "USD", "US"),
            ("B", 6, "Financials", "stock", "large", "USD", "US"),
            ("C", 9, "Health Care", "stock", "large", "USD", "US"),
            ("D", 73, "Diversified", "ETF", "n/a", "USD", "Global"),
        ]
    )
    texts = [w.text for w in scoring.analyze(df).warnings]
    assert texts == [
        "Currency USD: 100% (limit 70%)",
        "Position A: 12% (limit 10%)",
        "Position C: 9% (limit 10%)",
        "Position B: 6% (limit 10%)",
    ]


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


def portfolio_with_defensive(share_percent):
    return make(
        [
            ("Fund", 100 - share_percent, "Diversified", "ETF", "n/a", "EUR", "Global"),
            ("Bond", share_percent, "n/a", "bond", "n/a", "RON", "Romania"),
        ]
    )


@pytest.mark.parametrize(
    "share, expected",
    [
        (61, "Conservative"),
        (60, "Balanced"),
        (45, "Balanced"),
        (30, "Balanced"),
        (29, "Dynamic"),
    ],
)
def test_profile(share, expected):
    profile = scoring.profile_for(portfolio_with_defensive(share))
    assert profile.name == expected
    assert profile.message == scoring.PROFILE_MESSAGES[expected]


def test_profile_breakdown():
    df = make(
        [
            ("A", 40, "Technology", "stock", "large", "USD", "US"),
            ("B", 30, "Diversified", "ETF", "n/a", "EUR", "Global"),
            ("C", 20, "n/a", "bond", "n/a", "RON", "Romania"),
            ("D", 10, "n/a", "cash", "n/a", "RON", "Romania"),
        ]
    )
    profile = scoring.profile_for(df)
    assert profile.breakdown == pytest.approx({"stock": 0.4, "ETF": 0.3, "bond": 0.2, "cash": 0.1})
    assert profile.defensive_share == pytest.approx(0.3)

    slices = scoring.asset_class_slices(profile)
    assert slices["label"].tolist() == ["Equity", "Bonds", "Cash"]
    assert slices["share"].tolist() == pytest.approx([0.7, 0.2, 0.1])
    assert slices["detail"][0] == "Stocks 40% · ETFs 30%"


def test_asset_class_slices_skip_empty_classes():
    slices = scoring.asset_class_slices(sample("one_global_etf.csv").profile)
    assert slices["label"].tolist() == ["Equity"]


def test_csv_saved_with_bom():
    data = "﻿asset,value,sector,asset_type,market_cap,currency,region\nA,10,Technology,stock,large,USD,US\n"
    df = scoring.load_portfolio(io.BytesIO(data.encode("utf-8")))
    assert list(df.columns) == list(scoring.COLUMNS)


# ---------------------------------------------------------------------------
# Exposure notes
# ---------------------------------------------------------------------------


def stocks_by_cap(small, mid, large, region_share=0.5):
    """Stocks split by cap (percent of the stocks) next to a broad fund."""
    rows = [
        ("Small Co", small, "Industrials", "stock", "small", "USD", "US"),
        ("Mid Co", mid, "Financials", "stock", "mid", "EUR", "Europe"),
        ("Large Co", large, "Health Care", "stock", "large", "RON", "Romania"),
    ]
    rows = [r for r in rows if r[1] > 0]
    rows.append(("Fund", 300, "Diversified", "ETF", "n/a", "EUR", "Global"))
    return make(rows)


def note_keys(df, has_region=True):
    return [n.key for n in scoring.exposure_notes(df, has_region)]


def test_small_cap_note():
    assert note_keys(stocks_by_cap(30, 30, 40)) == ["small_cap"]
    assert note_keys(stocks_by_cap(28, 32, 40)) == []  # exactly at the threshold
    note = scoring.exposure_notes(stocks_by_cap(30, 30, 40), True)[0]
    assert note.text.startswith("Small caps are 30% of your stocks vs about 15% of the total US market.")
    assert note.headline == "Small caps are 30% of your stocks vs about 15% of the total US market."


def test_large_cap_note():
    assert note_keys(stocks_by_cap(0, 9, 91)) == ["large_cap"]
    assert note_keys(stocks_by_cap(0, 10, 90)) == []  # exactly 90%


def test_no_note_for_mid_caps():
    assert note_keys(stocks_by_cap(0, 100, 0)) == []


def test_single_region_note():
    df = make(
        [
            ("US fund", 81, "Diversified", "ETF", "n/a", "USD", "US"),
            ("Bond", 19, "n/a", "bond", "n/a", "RON", "Romania"),
        ]
    )
    assert note_keys(df) == ["region"]
    exactly = make(
        [
            ("US fund", 80, "Diversified", "ETF", "n/a", "USD", "US"),
            ("Bond", 20, "n/a", "bond", "n/a", "RON", "Romania"),
        ]
    )
    assert note_keys(exactly) == []


def test_global_does_not_trigger_region_note():
    df = make([("World", 100, "Diversified", "ETF", "n/a", "USD", "Global")])
    assert note_keys(df) == []


def test_portfolio_without_stocks():
    analysis = sample("conservative_saver.csv")
    assert analysis.cap_mix.empty
    assert analysis.notes == []
    assert scoring.stocks_table(analysis).empty
    assert scoring.cap_comparison(analysis)["yours"].tolist() == [0.0, 0.0, 0.0]


# ---------------------------------------------------------------------------
# Insights, on a portfolio computed by hand
# ---------------------------------------------------------------------------
# Total 100. Weights: A 40%, B 20%, C 15%, D 10%, E 10%, F 5%.
# Sum of squares = 0.16 + 0.04 + 0.0225 + 0.01 + 0.01 + 0.0025 = 0.245 -> 1/0.245 = 4.08
HAND = [
    ("A", 40, "Technology", "stock", "large", "USD", "US"),
    ("B", 20, "Financials", "stock", "mid", "EUR", "Europe"),
    ("C", 15, "Diversified", "ETF", "n/a", "EUR", "Global"),
    ("D", 10, "n/a", "bond", "n/a", "RON", "Romania"),
    ("E", 10, "n/a", "cash", "n/a", "RON", "Romania"),
    ("F", 5, "Health Care", "stock", "small", "USD", "US"),
]


@pytest.fixture
def hand_insights():
    return {i.key: i for i in scoring.analyze(make(HAND)).insights}


def test_effective_positions(hand_insights):
    insight = hand_insights["effective_positions"]
    assert insight.text == "You hold 6 positions, but your portfolio behaves like 4 equal ones."
    assert insight.label == "Watch"  # A is 40%: single-position limit is red


def test_top5(hand_insights):
    assert hand_insights["top5"].text == "Your 5 largest positions make up 95% of your portfolio."


def test_largest_sector(hand_insights):
    insight = hand_insights["largest_sector"]
    assert insight.text == "Your largest sector exposure is Technology, at 40% of your portfolio."
    assert insight.label == "Watch"


def test_other_currencies(hand_insights):
    insight = hand_insights["other_currencies"]
    assert insight.text == "80% of your portfolio is in currencies other than RON."
    assert insight.label == "Info"  # USD 45% is below 56%


def test_stress_test(hand_insights):
    assert hand_insights["stress_test"].text == (
        "If Technology fell 20%, your portfolio would fall about 8%."
    )


def test_sector_coverage(hand_insights):
    assert hand_insights["sector_coverage"].text == "You cover 3 of 11 GICS sectors."


def test_regions(hand_insights):
    insight = hand_insights["regions"]
    assert insight.text == (
        "Global funds cover 15% of your portfolio; the largest single region is US with 45%."
    )
    assert insight.label == "Info"


def test_insights_without_sector_exposure():
    df = make([("World", 100, "Diversified", "ETF", "n/a", "RON", "Global")])
    insights = {i.key: i for i in scoring.analyze(df).insights}
    assert insights["effective_positions"].text == "You hold a single position."
    assert insights["top5"].text == "With 1 position, your top 5 are the whole portfolio."
    assert insights["other_currencies"].text == "All of your portfolio is in RON."
    assert insights["sector_coverage"].text == "You cover 0 of 11 GICS sectors."
    assert "No single sector" in insights["stress_test"].text


def test_insights_do_not_change_the_score():
    analysis = scoring.analyze(make(HAND))
    assert analysis.score == scoring.overall_score(analysis.limits)


# ---------------------------------------------------------------------------
# Charts and tables
# ---------------------------------------------------------------------------


def test_chart_data_sector():
    analysis = sample("tech_heavy.csv")
    bars, limit = scoring.chart_data(analysis, "sector")
    assert limit == SECTOR["limit"]
    assert bars["weight"].is_monotonic_decreasing
    statuses = dict(zip(bars["category"], bars["status"]))
    assert statuses["Technology"] == RED
    assert statuses["Diversified"] == GREEN  # exempt, never coloured


def test_chart_data_region_has_no_limit():
    _, limit = scoring.chart_data(sample("andrei.csv"), "region")
    assert limit is None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_missing_currency_column_gives_clear_error():
    with pytest.raises(scoring.PortfolioError, match="Missing required column: currency"):
        scoring.load_portfolio(FIXTURES / "missing_column.csv")


def test_missing_region_still_works():
    csv = io.StringIO(
        "asset,value,sector,asset_type,market_cap,currency\n"
        "Apple,4000,Technology,stock,large,USD\n"
        "World ETF,6000,Diversified,ETF,n/a,EUR\n"
    )
    analysis = scoring.analyze(scoring.load_portfolio(csv))
    assert analysis.has_region is False
    assert analysis.info == ["No region column: the analysis continues without regions."]
    assert "regions" not in [i.key for i in analysis.insights]
    assert "region" not in scoring.chart_dimensions(analysis)
    assert "region" not in scoring.stocks_table(analysis).columns


@pytest.mark.parametrize("value", ["0", "-5", "abc", ""])
def test_value_must_be_positive_number(value):
    csv = io.StringIO(
        "asset,value,sector,asset_type,market_cap,currency,region\n"
        "Apple,1000,Technology,stock,large,USD,US\n"
        f"Bad,{value},Technology,stock,large,USD,US\n"
    )
    with pytest.raises(scoring.PortfolioError, match="positive number.*line\\(s\\) 3"):
        scoring.load_portfolio(csv)


def test_na_text_stays_a_category():
    df = scoring.load_portfolio(scoring.DATA_DIR / "conservative_saver.csv")
    assert "n/a" in set(df["sector"])
    assert not df.isna().any().any()


def test_empty_file():
    with pytest.raises(scoring.PortfolioError):
        scoring.load_portfolio(io.StringIO(""))


def test_template_is_valid():
    df = scoring.load_portfolio(scoring.TEMPLATE_PATH)
    assert list(df.columns) == list(scoring.COLUMNS)
    assert len(df) == 2
