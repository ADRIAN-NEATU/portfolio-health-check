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

# file -> (sector, asset, score, profile, notes)
EXPECTED = {
    "diversified.csv": (GREEN, GREEN, 100, "Dynamic", []),
    "tech_heavy.csv": (RED, GREEN, 75, "Dynamic", []),
    "all_in_ron.csv": (GREEN, GREEN, 100, "Balanced", []),
    "beginner_3_stocks.csv": (GREEN, RED, 60, "Balanced", []),
    "conservative_saver.csv": (GREEN, GREEN, 100, "Conservative", []),
    "small_cap_fan.csv": (GREEN, GREEN, 100, "Dynamic", ["small_cap"]),
    "one_global_etf.csv": (GREEN, GREEN, 100, "Dynamic", ["currency"]),
    "andrei.csv": (GREEN, YELLOW, 94, "Dynamic", ["large_cap", "region", "currency"]),
}


def test_every_sample_is_listed():
    files = {p.name for p in scoring.DATA_DIR.glob("*.csv")} - {"template.csv", "known_securities.csv"}
    assert files == set(scoring.SAMPLE_PORTFOLIOS) == set(EXPECTED)


@pytest.mark.parametrize("file_name", EXPECTED)
def test_sample_limit_statuses(file_name):
    analysis = sample(file_name)
    statuses = tuple(r.status for r in analysis.limits)
    assert [r.key for r in analysis.limits] == ["sector", "asset"]
    assert statuses == EXPECTED[file_name][:2]


@pytest.mark.parametrize("file_name", EXPECTED)
def test_sample_score_profile_and_notes(file_name):
    analysis = sample(file_name)
    _, _, score, profile, notes = EXPECTED[file_name]
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
    assert (sector.category, sector.weight) == ("Information Technology", pytest.approx(0.45))
    assert analysis.verdict == "1 issue: sector (Information Technology 45%)."


def test_andrei_at_a_glance():
    analysis = sample("andrei.csv")
    assert analysis.verdict == "1 issue: single position (Apple 8%)."
    assert [(row.status, row.tab) for row in analysis.glance] == [
        (YELLOW, "Overview"),
        ("", "Stocks"),
    ]
    assert analysis.glance[0].text == "Position Apple: 8% (limit 10%) and 6 more"


def test_one_global_etf_region_is_global():
    analysis = sample("one_global_etf.csv")
    assert scoring.weights(analysis.positions, "region").to_dict() == {"Global": 1.0}
    regions = next(i for i in analysis.insights if i.key == "regions")
    assert regions.text == "All of your money is in global funds."


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
    # sector 100, asset 88 (8%) -> 94; currency is a note, not a limit
    df = make(
        [
            ("A", 8, "Information Technology", "stock", "large", "USD", "US"),
            ("B", 62, "Diversified", "ETF", "n/a", "USD", "Global"),
            ("C", 30, "n/a", "cash", "n/a", "RON", "Romania"),
        ]
    )
    analysis = scoring.analyze(df)
    assert [round(r.score, 2) for r in analysis.limits] == [100, 88]
    assert analysis.score == 94


def test_round_half_up():
    assert scoring.round_half_up(92.5) == 93
    assert scoring.round_half_up(92.49) == 92


def test_exempt_categories_do_not_count():
    df = make(
        [
            ("World ETF", 50, "Diversified", "ETF", "n/a", "EUR", "Global"),
            ("Bond", 30, "n/a", "bond", "n/a", "RON", "Romania"),
            ("Tech ETF", 20, "Information Technology", "ETF", "n/a", "USD", "US"),
        ]
    )
    limits = {r.key: r for r in scoring.analyze(df).limits}
    assert (limits["sector"].category, limits["sector"].weight) == ("Information Technology", 0.2)
    # the sector ETF counts as a single position, the broad ETF and the bond do not
    assert (limits["asset"].category, limits["asset"].weight) == ("Tech ETF", 0.2)


def test_warnings_sorted_red_then_yellow_then_size():
    df = make(
        [
            ("A", 12, "Information Technology", "stock", "large", "USD", "US"),
            ("B", 6, "Financials", "stock", "large", "USD", "US"),
            ("C", 9, "Health Care", "stock", "large", "USD", "US"),
            ("D", 73, "Diversified", "ETF", "n/a", "USD", "Global"),
        ]
    )
    texts = [w.text for w in scoring.analyze(df).warnings]
    assert texts == [
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
            ("A", 40, "Information Technology", "stock", "large", "USD", "US"),
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
    data = "\ufeffasset,value,sector,asset_type,market_cap,currency,region\nA,10,Information Technology,stock,large,USD,US\n"
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
    rows.append(("Fund", 300, "Diversified", "ETF", "n/a", "RON", "Global"))
    return make(rows)


def note_keys(df, has_region=True, ignore=("currency",)):
    """Notes raised for a portfolio; the currency note is left out unless asked for."""
    return [n.key for n in scoring.exposure_notes(df, has_region) if n.key not in ignore]


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


def foreign_share(usd_percent):
    return make(
        [
            ("US fund", usd_percent, "Diversified", "ETF", "n/a", "USD", "US"),
            ("Deposit", 100 - usd_percent, "n/a", "cash", "n/a", "RON", "Romania"),
        ]
    )


def test_currency_is_a_note_not_a_limit():
    analysis = scoring.analyze(foreign_share(90))
    assert [r.key for r in analysis.limits] == ["sector", "asset"]
    note = next(n for n in analysis.notes if n.key == "currency")
    assert note.headline == "90% of your portfolio is in USD."
    assert "lose value in lei" in note.text
    other = next(i for i in analysis.insights if i.key == "other_currencies")
    assert other.label == "Watch"


def test_currency_note_threshold_and_ron():
    assert "currency" in note_keys(foreign_share(57), ignore=())
    assert "currency" not in note_keys(foreign_share(56), ignore=())  # exactly the threshold
    all_ron = make([("Deposit", 100, "n/a", "cash", "n/a", "RON", "Romania")])
    assert "currency" not in note_keys(all_ron, ignore=())  # RON is never a currency risk


def test_currency_chart_has_no_limit_line():
    bars, limit = scoring.chart_data(sample("andrei.csv"), "currency")
    assert limit is None
    assert set(bars["status"]) == {GREEN}


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
    ("A", 40, "Information Technology", "stock", "large", "USD", "US"),
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
    assert insight.text == (
        "You hold 6 positions of different sizes. Because a few large ones weigh more, "
        "your money is spread as if you held 4 equal positions."
    )
    assert insight.label == "Watch"  # A is 40%: single-position limit is red


def test_top5(hand_insights):
    assert hand_insights["top5"].text == "Your 5 largest positions make up 95% of your portfolio."


def test_largest_sector(hand_insights):
    insight = hand_insights["largest_sector"]
    assert insight.text == "40% of your money is in Information Technology."
    assert insight.label == "Watch"


def test_other_currencies(hand_insights):
    insight = hand_insights["other_currencies"]
    assert insight.text == "80% of your portfolio is in currencies other than RON."
    assert insight.label == "Info"  # USD 45% is below 56%


def test_no_stress_test_but_plain_exposure():
    insights = {i.key: i for i in sample("tech_heavy.csv").insights}
    assert "stress_test" not in insights
    assert insights["largest_sector"].text == "45% of your money is in Information Technology."


def test_sector_coverage_with_global_funds(hand_insights):
    # HAND holds 3 sectors directly plus a Diversified ETF
    assert hand_insights["sector_coverage"].text == (
        "You cover 3 of 11 GICS sectors directly, plus global funds that span all sectors."
    )


def test_sector_coverage_without_funds():
    df = make(
        [
            ("A", 50, "Energy", "stock", "large", "USD", "US"),
            ("B", 30, "Utilities", "stock", "large", "EUR", "Europe"),
            ("C", 20, "n/a", "bond", "n/a", "RON", "Romania"),
        ]
    )
    coverage = next(i for i in scoring.analyze(df).insights if i.key == "sector_coverage")
    assert coverage.text == "You cover 2 of 11 GICS sectors."


def test_sector_coverage_never_zero_with_global_funds():
    for file_name in ["one_global_etf.csv", "conservative_saver.csv"]:
        coverage = next(i for i in sample(file_name).insights if i.key == "sector_coverage")
        assert coverage.text == "You hold global funds that span all sectors."


def test_regions(hand_insights):
    insight = hand_insights["regions"]
    assert insight.text == (
        "45% of your money is in the US, and 15% in global funds."
    )
    assert insight.label == "Info"


def test_insights_without_sector_exposure():
    df = make([("World", 100, "Diversified", "ETF", "n/a", "RON", "Global")])
    insights = {i.key: i for i in scoring.analyze(df).insights}
    assert insights["effective_positions"].text == "You hold a single position."
    assert insights["top5"].text == "With 1 position, your top 5 are the whole portfolio."
    assert insights["other_currencies"].text == "All of your portfolio is in RON."
    assert insights["sector_coverage"].text == "You hold global funds that span all sectors."
    assert insights["largest_sector"].text.startswith("You have no single-sector exposure")


def test_one_dominant_position():
    df = make(
        [
            ("Big", 97, "Energy", "stock", "large", "USD", "US"),
            ("Small", 3, "Utilities", "stock", "large", "USD", "US"),
        ]
    )
    insight = next(i for i in scoring.analyze(df).insights if i.key == "effective_positions")
    assert insight.text == (
        "You hold 2 positions, but one is much bigger than the rest: "
        "your money is spread as if you held a single position."
    )


def test_bar_members():
    analysis = scoring.analyze(make(HAND))
    sectors = scoring.bar_members(analysis, "sector")
    assert sectors["Information Technology"] == [("A", pytest.approx(0.4))]
    assert [name for name, _ in sectors["n/a"]] == ["D", "E"]
    usd = scoring.bar_members(analysis, "currency")["USD"]
    assert [name for name, _ in usd] == ["A", "F"]  # largest first
    assert sum(w for _, w in usd) == pytest.approx(0.45)


def test_label_explanations():
    texts = scoring.label_explanations(["Information Technology", "Diversified", "n/a"])
    assert texts == [
        "Diversified: broad funds (ETFs) spread over many sectors.",
        "n/a: bonds and cash, which have no sector.",
    ]
    assert scoring.label_explanations(["Energy"]) == []


def test_bonds_only_covers_zero_sectors():
    df = make([("Bond", 100, "n/a", "bond", "n/a", "RON", "Romania")])
    coverage = next(i for i in scoring.analyze(df).insights if i.key == "sector_coverage")
    assert coverage.text == "You cover 0 of 11 GICS sectors."


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
    assert statuses["Information Technology"] == RED
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
        "Apple,4000,Information Technology,stock,large,USD\n"
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
        "Apple,1000,Information Technology,stock,large,USD,US\n"
        f"Bad,{value},Information Technology,stock,large,USD,US\n"
    )
    with pytest.raises(scoring.PortfolioError, match="positive number.*line\\(s\\) 3"):
        scoring.load_portfolio(csv)


@pytest.mark.parametrize(
    "written, official",
    [
        ("Technology", "Information Technology"),
        ("technology", "Information Technology"),
        ("Healthcare", "Health Care"),
        ("Telecom", "Communication Services"),
        ("health care", "Health Care"),
        ("DIVERSIFIED", "Diversified"),
        ("N/A", "n/a"),
        ("Crypto", "Crypto"),  # unknown names are kept as written
    ],
)
def test_sector_aliases_are_normalised(written, official):
    csv = io.StringIO(
        "asset,value,sector,asset_type,market_cap,currency,region\n"
        f"A,100,{written},stock,large,USD,US\n"
    )
    assert scoring.load_portfolio(csv)["sector"].tolist() == [official]


def test_aliases_point_to_official_names():
    assert len(rules.GICS_SECTORS) == 11
    assert set(rules.SECTOR_ALIASES.values()) <= set(rules.GICS_SECTORS)


@pytest.mark.parametrize("file_name", sorted(EXPECTED) + ["template.csv"])
def test_data_files_use_official_sector_names(file_name):
    raw = pd.read_csv(scoring.DATA_DIR / file_name, keep_default_na=False)
    allowed = set(rules.GICS_SECTORS) | set(rules.SECTOR_EXEMPT)
    assert set(raw["sector"]) <= allowed


def test_csv_from_excel_with_semicolons_and_decimal_comma():
    csv = io.StringIO(
        "asset;value;sector;asset_type;market_cap;currency;region\n"
        "Apple;1.234,56;Information Technology;stock;large;USD;US\n"
        "Fund;413,02;Diversified;ETF;n/a;EUR;Global\n"
        "Bond;2.000;n/a;bond;n/a;RON;Romania\n"
        "Cash;99.5;n/a;cash;n/a;RON;Romania\n"
    )
    df = scoring.load_portfolio(csv)
    assert df["value"].tolist() == pytest.approx([1234.56, 413.02, 2000, 99.5])


def test_csv_with_thousands_separators():
    csv = io.StringIO(
        "asset,value,sector,asset_type,market_cap,currency,region\n"
        'Apple,"1,234.56",Information Technology,stock,large,USD,US\n'
        "Fund,12 000,Diversified,ETF,n/a,EUR,Global\n"
    )
    assert scoring.load_portfolio(csv)["value"].tolist() == pytest.approx([1234.56, 12000])


def test_csv_saved_with_windows_encoding():
    data = (
        "asset;value;sector;asset_type;market_cap;currency;region\n"
        "Societatea Naţională;100;Utilities;stock;mid;ron;Romania\n"  # cp1250 has the cedilla ţ
    )
    df = scoring.load_portfolio(io.BytesIO(data.encode("cp1250")))
    assert df["asset"][0] == "Societatea Naţională"
    assert df["currency"][0] == "RON"


@pytest.mark.parametrize(
    "column, written, expected",
    [
        ("asset_type", "Stock", "stock"),
        ("asset_type", "etf", "ETF"),
        ("asset_type", "Bonds", "bond"),
        ("market_cap", "Large cap", "large"),
        ("market_cap", "small-cap", "small"),
        ("region", "USA", "US"),
        ("region", "europe", "Europe"),
        ("region", "World", "Global"),
    ],
)
def test_category_spellings_are_normalised(column, written, expected):
    row = {"asset": "A", "value": 100, "sector": "Energy", "asset_type": "stock",
           "market_cap": "large", "currency": "USD", "region": "US"}
    row[column] = written
    assert scoring.validate(pd.DataFrame([row]))[column][0] == expected


# ---------------------------------------------------------------------------
# In-app editor: known securities, auto-fill, checks, export
# ---------------------------------------------------------------------------


def test_known_securities_use_valid_details():
    table = pd.read_csv(scoring.KNOWN_SECURITIES_PATH, dtype=str, keep_default_na=False)
    for column, options in scoring.EDITOR_OPTIONS.items():
        assert set(table[column]) <= set(options), column
    assert not (table == "").drop(columns="aliases").any().any()


def test_known_security_names_do_not_collide():
    table = pd.read_csv(scoring.KNOWN_SECURITIES_PATH, dtype=str, keep_default_na=False)
    owner = {}
    for row in table.to_dict("records"):
        for name in [row["name"], *row["aliases"].split("|")]:
            if name:
                key = scoring.match_key(name)
                assert owner.setdefault(key, row["name"]) == row["name"], name


@pytest.mark.parametrize(
    "written, key",
    [
        ("Apple Inc.", "apple"),
        ("Johnson and Johnson", "johnson & johnson"),
        ("BRK-B", "brk b"),
        ("BRK.B", "brk b"),
        ("Nestlé", "nestle"),
        ("McDonald's", "mcdonalds"),
        ("Vale S.A.", "vale"),
        ("Novo Nordisk A/S", "novo nordisk"),
        ("Seanergy Maritime Holdings Corp.", "seanergy maritime"),
        ("SIEMENS AG-REG", "siemens"),
        ("The Walt Disney Company", "walt disney"),
    ],
)
def test_match_key(written, key):
    assert scoring.match_key(written) == key


def editor_rows(*rows):
    return pd.DataFrame(rows, columns=list(scoring.COLUMNS))


def test_autofill_by_name_or_ticker():
    df = editor_rows(
        ("Apple Inc.", 1000, None, None, None, None, None),
        ("VWCE", 2000, None, None, None, None, None),
        ("Some Unknown Co", 300, None, None, None, None, None),
    )
    filled, fills, unknown = scoring.autofill(df)  # our own list only, no online lookup
    assert [(asset, found.name) for asset, found in fills] == [
        ("Apple Inc.", "Apple"),
        ("VWCE", "Vanguard FTSE All-World UCITS ETF"),
    ]
    assert unknown == ["Some Unknown Co"]
    assert filled.iloc[0, 2:].tolist() == ["Information Technology", "stock", "large", "USD", "US"]
    assert filled.iloc[1, 2:].tolist() == ["Diversified", "ETF", "n/a", "EUR", "Global"]
    assert filled.iloc[2, 2:].isna().all()


def test_autofill_keeps_what_the_user_chose():
    df = editor_rows(("Microsoft", 1000, None, None, None, "EUR", None))
    filled, _, _ = scoring.autofill(df)
    assert filled.loc[0, "currency"] == "EUR"
    assert filled.loc[0, "region"] == "US"
    assert scoring.autofill(filled)[1] == []  # nothing left to fill


def test_check_editor_rows():
    df = editor_rows(
        ("Apple", 1000, "Information Technology", "stock", "large", "USD", "US"),
        (None, None, None, None, None, None, None),  # blank row, ignored
        ("Netstreit", 400, None, "stock", None, "USD", "US"),
        (None, 50, "n/a", "cash", "n/a", "RON", "Romania"),
        ("Zero", 0, "Energy", "stock", "small", "USD", "US"),
    )
    rows, problems = scoring.check_editor_rows(df)
    assert len(rows) == 4
    assert problems == [
        "Netstreit: sector, market cap",
        "row 3: name",
        "Zero: a value above 0",
    ]


def test_editor_csv_round_trip():
    df = editor_rows(
        ("Apple", 1234.5, "Information Technology", "stock", "large", "USD", "US"),
        ("VWCE", 2000, "Diversified", "ETF", "n/a", "EUR", "Global"),
    )
    loaded = scoring.load_portfolio(io.BytesIO(scoring.to_csv(df)))
    assert loaded["value"].tolist() == [1234.5, 2000]
    assert loaded["asset"].tolist() == ["Apple", "VWCE"]


def test_csv_with_only_names_and_values_goes_to_the_editor():
    text = "asset;value\nApple;1.000\nNetstreit;412,5\nStock Without Value;\n"
    with pytest.raises(scoring.PortfolioError, match="Missing required columns"):
        scoring.load_portfolio(io.StringIO(text))
    table = scoring.editor_table(scoring.read_table(io.StringIO(text)))
    assert list(table.columns) == list(scoring.COLUMNS)
    assert table["asset"].tolist() == ["Apple", "Netstreit", "Stock Without Value"]
    assert table["value"].tolist()[:2] == [1000, 412.5]
    assert pd.isna(table["value"][2])
    assert table["sector"].isna().all()
    filled, fills, _ = scoring.autofill(table)
    assert filled.loc[0, "sector"] == "Information Technology"


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
