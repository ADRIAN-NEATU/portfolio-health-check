"""Online lookup, tested on canned answers: no test talks to SEC or OpenFIGI."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lookup  # noqa: E402
import scoring  # noqa: E402
from scoring import Found  # noqa: E402

SEC_TICKERS = {
    "fields": ["cik", "name", "ticker", "exchange"],
    "data": [
        [1, "MICRON TECHNOLOGY INC", "MU", "Nasdaq"],
        [2, "Micron Solutions Inc", "MICR", "NYSE"],
        [3, "FORD MOTOR CO", "F", "NYSE"],
        [4, "Forward Industries Inc", "FORD", "Nasdaq"],
        [5, "Vale S.A.", "VALE", "NYSE"],
        [6, "SPDR S&P 500 ETF TRUST", "SPY", "NYSE"],
        [7, "EuroDry Ltd.", "EDRY", "Nasdaq"],
    ],
}
SEC_FLOATS = {"data": [{"cik": 1, "val": 100e9}, {"cik": 2, "val": 0.05e9}, {"cik": 3, "val": 42e9}, {"cik": 4, "val": 0.01e9}]}
SEC_COMPANIES = {
    1: {"sic": "3674", "category": "Large accelerated filer", "addresses": {"business": {"stateOrCountry": "ID", "stateOrCountryDescription": "ID"}}},
    2: {"sic": "3672", "category": "Non-accelerated filer", "addresses": {"business": {"stateOrCountry": "MA"}}},
    3: {"sic": "3711", "category": "Large accelerated filer", "addresses": {"business": {"stateOrCountry": "MI"}}},
    4: {"sic": "3570", "category": "Non-accelerated filer", "addresses": {"business": {"stateOrCountry": "NY"}}},
    5: {"sic": "1000", "category": "Large accelerated filer", "addresses": {"business": {"stateOrCountry": "D5", "stateOrCountryDescription": "Brazil"}}},
    6: {"sic": "", "category": "", "addresses": {}},
    7: {"sic": "4400", "category": "Non-accelerated filer", "addresses": {"business": {"stateOrCountry": "J3", "stateOrCountryDescription": "Greece"}}},
}


@pytest.fixture
def online(monkeypatch):
    """Canned SEC and OpenFIGI answers; `figi` holds what OpenFIGI returns."""
    figi = {"mapping": [{"warning": "No identifier found."}], "search": {"data": []}}

    def get_json(url):
        if url == lookup.SEC_TICKERS_URL:
            return SEC_TICKERS
        if "EntityPublicFloat" in url:
            return SEC_FLOATS
        cik = int(url.rsplit("CIK", 1)[1].split(".")[0])
        return SEC_COMPANIES[cik]

    def post_json(url, payload):
        return figi["mapping"] if url == lookup.OPENFIGI_MAPPING_URL else figi["search"]

    monkeypatch.setattr(lookup, "_get_json", get_json)
    monkeypatch.setattr(lookup, "_post_json", post_json)
    lookup.clear_cache()
    yield figi
    lookup.clear_cache()


@pytest.mark.parametrize(
    "sic, sector",
    [
        ("3674", "Information Technology"),
        ("6324", "Health Care"),
        ("6798", "Real Estate"),
        ("1311", "Energy"),
        ("1000", "Materials"),
        ("4412", "Industrials"),
        ("3711", "Consumer Discretionary"),
        ("9999", None),
        ("", None),
    ],
)
def test_sic_sector(sic, sector):
    assert lookup.sic_sector(sic) == sector


@pytest.mark.parametrize(
    "public_float, category, size",
    [
        (15e9, None, "large"),
        (5e9, None, "mid"),
        (1e9, None, "small"),
        (None, "Non-accelerated filer", "small"),
        (None, "Accelerated filer", "small"),
        (None, "Large accelerated filer", None),
    ],
)
def test_size_class(public_float, category, size):
    assert lookup.size_class(public_float, category) == size


@pytest.mark.parametrize(
    "code, country, region",
    [("TX", "TX", "US"), ("G4", "Cyprus", "Europe"), ("X", "Romania", "Romania"),
     (None, "Brazil", "Emerging"), (None, "Bermuda", None)],
)
def test_address_region(code, country, region):
    assert lookup.address_region(code, country) == region


@pytest.mark.parametrize(
    "name, expected",
    [
        ("VANG FTSE AW USDA", ("ETF", "Diversified", "Global")),
        ("VANGUARD S&P 500 ETF", ("ETF", "Diversified", "US")),
        ("ISHARES CORE MSCI EM IMI", ("ETF", "Diversified", "Emerging")),
        ("VANECK SEMICONDUCTOR UCITS", ("ETF", "Information Technology", None)),
        ("ISHARES USD TREASURY BOND 7-10YR", ("bond", "n/a", None)),
    ],
)
def test_fund_details_from_the_name(name, expected):
    details = lookup.fund_details(name, "USD")
    assert (details["asset_type"], details["sector"], details["region"]) == expected


def test_sec_name_prefers_the_largest_company(online):
    found = lookup.find("Micron")
    assert found.name == "MICRON TECHNOLOGY INC"
    assert found.source == "SEC EDGAR"
    assert found.details == {"sector": "Information Technology", "asset_type": "stock",
                             "market_cap": "large", "currency": "USD", "region": "US"}


def test_capitals_read_as_ticker_words_as_name(online):
    assert lookup.find("Ford").name == "FORD MOTOR CO"
    assert lookup.find("FORD").name == "Forward Industries Inc"
    assert lookup.find("vale").name == "Vale S.A."


def test_foreign_company_listed_in_the_us(online):
    vale = lookup.find("VALE").details
    assert (vale["region"], vale["currency"], vale["market_cap"]) == ("Emerging", "USD", None)
    assert lookup.find("EuroDry").details["market_cap"] == "small"  # non-accelerated filer


def test_sec_fund_is_an_etf(online):
    spy = lookup.find("SPY").details
    assert (spy["asset_type"], spy["sector"], spy["region"]) == ("ETF", "Diversified", "US")


def test_openfigi_prefers_bucharest(online):
    online["mapping"] = [{"data": [
        {"name": "ENAPTER AG", "exchCode": "GY", "securityType": "Common Stock"},
        {"name": "SOCIETATEA DE PRODUCERE A EN", "exchCode": "RO", "securityType": "Common Stock"},
    ]}]
    found = lookup.find("H2O")
    assert found.source == "OpenFIGI"
    assert found.details == {"sector": None, "asset_type": "stock", "market_cap": None,
                             "currency": "RON", "region": "Romania"}


def test_openfigi_fund_in_london_leaves_the_currency_open(online):
    online["mapping"] = [{"data": [{"name": "ISHARES CORE MSCI WORLD", "exchCode": "LN", "securityType": "ETP"}]}]
    details = lookup.find("SWDA").details
    assert (details["asset_type"], details["region"], details["currency"]) == ("ETF", "Global", None)


def test_unknown_name(online):
    assert lookup.find("Nothing Like This") is None


def test_network_error_means_not_found(monkeypatch):
    def fail(*args):
        raise lookup.SourceError("offline")

    monkeypatch.setattr(lookup, "_get_json", fail)
    monkeypatch.setattr(lookup, "_post_json", fail)
    lookup.clear_cache()
    assert lookup.find_many(["Apple", "VWCE"]) == {"Apple": None, "VWCE": None}
    lookup.clear_cache()


def test_autofill_uses_known_list_then_online_lookup():
    df = pd.DataFrame(
        [
            ("VWCE", 2000, None, None, None, None, None),
            ("Netstreit", 400, None, None, None, None, None),
            ("Mystery Co", 100, None, None, None, None, None),
        ],
        columns=list(scoring.COLUMNS),
    )
    asked = []

    def fake_find_many(names):
        asked.extend(names)
        online = Found("NETSTREIT Corp.", "SEC EDGAR", {"sector": "Real Estate", "asset_type": "stock",
                                                        "market_cap": "small", "currency": "USD", "region": "US"})
        return {n: (online if n == "Netstreit" else None) for n in names}

    filled, fills, unknown = scoring.autofill(df, fake_find_many)
    assert asked == ["Netstreit", "Mystery Co"]  # VWCE is in our own list
    assert [(asset, found.source) for asset, found in fills] == [("VWCE", "the built-in list"), ("Netstreit", "SEC EDGAR")]
    assert filled.loc[1, "sector"] == "Real Estate"
    assert unknown == ["Mystery Co"]


def test_partial_details_leave_the_rest_to_the_user():
    df = pd.DataFrame([("NOVOB", 500, None, None, None, None, None)], columns=list(scoring.COLUMNS))
    partial = Found("NOVO NORDISK A/S-B", "OpenFIGI", {"sector": None, "asset_type": "stock",
                                                        "market_cap": None, "currency": "DKK", "region": "Europe"})
    filled, fills, unknown = scoring.autofill(df, lambda names: {n: partial for n in names})
    assert filled.loc[0, ["asset_type", "currency", "region"]].tolist() == ["stock", "DKK", "Europe"]
    assert pd.isna(filled.loc[0, "sector"])
    _, problems = scoring.check_editor_rows(filled)
    assert problems == ["NOVOB: sector, market cap"]
    # nothing new the second time: the editor does not refresh in a loop
    assert scoring.autofill(filled, lambda names: {n: partial for n in names})[1] == []
