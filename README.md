# Portfolio Health Check

Portfolio Health Check is a local web tool that shows an individual investor, in under a minute, how concentrated their portfolio is. You pick a sample portfolio, upload a CSV, or type your positions straight into the app. The app gives a score from 0 to 100, based on two concentration limits: sector and single position. It then lists what to look at first, compares every figure with its threshold, and adds plain-language insights about asset classes, market cap and regions. It is analysis, not investment advice.

![At a glance and the concentration limits for a sample portfolio](docs/screenshots/andrei-overview-desktop.png)

## Quick start on Windows

1. Install Python 3.12 or newer from [python.org](https://www.python.org/downloads/) and tick "Add python.exe to PATH".
2. Double-click **`start.bat`**.

The first time, it sets everything up (about a minute). After that, it starts at once. The app opens in your browser at http://localhost:8501. Keep the black window open while you use the app, and close it to stop the app.

## Three ways to enter a portfolio

1. **Try a sample:** pick one of the eight sample portfolios in the side panel, or one of the ten "Stress tests" below them, each built to sit right on a threshold. "Edit these positions" turns any of them into a starting point for your own.
2. **Type or paste:** click "Type or paste positions" and enter a name or ticker and its value in lei. Sector, type, market cap, currency and region fill in by themselves (see below), and whatever cannot be found is chosen from drop-down lists. You can also paste rows copied from Excel or Google Sheets (name, then value). "Download as CSV" keeps them for next time.
3. **Upload a CSV:** the format is below. Files saved by Excel with Romanian settings work as they are, with `;` between columns and a decimal comma (1.234,56). Common spellings are accepted too ("Stock", "Large cap", "USA"). A file with only names and values is enough: the app offers to fill in the missing details.

![Positions pasted from a spreadsheet, filled in automatically](docs/screenshots/editor-paste-desktop.png)

## Where the details come from

Only free sources whose terms allow this use, in this order:

| Source | Covers | Licence | Gives |
|---|---|---|---|
| Built-in list, [data/known_securities.csv](data/known_securities.csv) | about 220 popular stocks and ETFs: US and European large caps, Bucharest (BVB) shares, US and UCITS ETFs | our own compilation | everything |
| [SEC EDGAR](https://www.sec.gov/edgar) | every company listed in the US (about 10,000), including European and emerging-market companies with US listings | U.S. government data, public domain | sector (from the SIC code), size (from the public float), region (from the business address), currency |
| [OpenFIGI](https://www.openfigi.com) | listings on other exchanges, and funds | free, MIT licence, no restrictions on use or redistribution | type and currency; for funds, region and sector read from the fund's name |

- **Not used:** Yahoo Finance and the libraries that read it (such as yfinance). Yahoo's terms do not allow automated extraction.
- **Approximate sector and size:** GICS sector assignments and live market caps are licensed commercial data. The sector here comes from the official SIC code through our own table, and the size from the public float the company last reported. The app says so and lets you change both.
- **What still needs a choice:** a European share that is not in the built-in list gets its type, currency and region, but you choose its sector and size. A ticker on its own is read as the US ticker (M is Macy's, not MedLife on BVB), so type the company name for a share listed only in Europe.
- **Privacy and offline use:** only the names you type are sent. The "Look up names online" switch turns the lookup off, and the editor works offline.
- **Optional settings:** a free [OpenFIGI API key](https://www.openfigi.com/api) in the `OPENFIGI_API_KEY` environment variable raises OpenFIGI's limit on name searches. `PHC_CONTACT` adds an e-mail to the identification string SEC asks automated clients to send.

Add a row to the built-in list to teach the app a new stock or fund.

## Install and run by hand

Requires Python 3.12 or newer. `requirements.txt` pins the exact versions the app was tested with (tested on Python 3.12 and 3.15).

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501. Run the tests with `pytest`.

## How to read the score

The app opens with a short "Before you start" window: the app is just math on the numbers you enter, not investment advice. It also explains the score in a few lines. "How the score works" at the bottom of the page opens it again.

**Your data.** The app runs on your computer and keeps your portfolio only in memory: nothing is written to a file, and it is gone when you close the app. With the online lookup on, only names and tickers are sent to SEC EDGAR and OpenFIGI, never values. Streamlit's usage statistics are turned off in [.streamlit/config.toml](.streamlit/config.toml).

The score is the average of two limit scores (sector and single position), rounded to a whole number. Each limit scores 100 while its largest weight stays below the yellow threshold, falls linearly from 100 to 80 between the yellow threshold and the limit, and above the limit scores 80 − 60 × min(weight / limit − 1, 1), so never less than 20. The sector limit also has a safety margin: up to 5 points over it, the status is Just over (orange) instead of Over limit (red). The score is the same either way.

| Limit | Watch from | Limit | Just over up to | Not counted |
|---|---|---|---|---|
| Sector | 20% | 25% | 30% | broad funds (Diversified), n/a |
| Single position | 5% | 10% | – | broad ETFs, government bonds, cash, precious metals |

All thresholds live in [rules.py](rules.py). No regulator sets a limit for an individual investor, so the two limits are the ones set for funds, used here as a reference:
- **Single position, 5% and 10%:** the limits EU and US law set for diversified funds ([decision D2](docs/decisions.md)).
- **Sector, 25%:** the US regulator treats a fund with 25% or more in one industry as concentrated ([decision D3](docs/decisions.md)). The sector Watch threshold (20%) and the 5-point margin are examples.

**Funds.** A broad fund counts as diversified: it doesn't count towards the limits, so it never lowers the score. Its weight still matters: a fund of 5% barely changes a portfolio of five stocks, while a fund of 50% halves every stock's weight (see the "Five stocks" stress tests). The app can also count index funds by what they hold, from a table of index figures (`data/index_funds.csv`), but it ships without that table: the figures we had came from index providers whose terms don't allow redistribution ([decision D8](docs/decisions.md)). Public-domain figures, from the holdings US funds file with the SEC, are planned.

**Bonds and precious metals.** Government bonds and cash don't count towards the limits. A corporate bond counts towards the single-position limit, like a position in the company. Precious metals are shown in the profile and in an insight, but don't count towards the limits ([decision D7](docs/decisions.md)).

## Informative dimensions (not scored)

- **Asset classes:** the share of bonds and cash sets a profile (Conservative, Balanced or Dynamic). There is no right mix: it depends on the investor's profile, so it is described, not scored.
- **Market cap:** the stocks' small / mid / large split is shown. A note appears when small caps are more than 28% of the stocks or when almost everything is large cap. As with asset classes, the right mix depends on the investor, so it does not affect the score.
- **Currency:** a note, not a limit ([decision D1](docs/decisions.md)). It appears when one foreign currency holds most of the portfolio. Over long periods currency moves matter less for stocks than company and sector risk, and the leu never counts, since it is the investor's own currency. The currency is the one the asset is listed in, not the one the company earns in.
- **Region:** the region of the company or fund, not of the currency, so it measures something different from the currency note. It is shown as a note, not scored: the note appears when one region (Global funds excluded) holds most of the portfolio. When your largest region is the US, the Regions insight compares it with the US share of all listed companies in the world (about 49%, World Bank, 2025), with the source behind a (?) ([decisions D4, D8](docs/decisions.md)).
- **Insights:** effective number of positions, top 5 share, largest sector and largest region in %, share outside RON, and GICS sector coverage. Each insight is labelled Good (its limit is OK), Watch (its limit or note needs a look) or Info (no limit), and has no effect on the score. The Good label is provisional ([decision D5](docs/decisions.md)).

## CSV format

One row per position. Start from [data/template.csv](data/template.csv).

| Column | Values | Rules |
|---|---|---|
| asset | any name | |
| value | number > 0 | always in lei (RON) |
| sector | an official GICS sector name, `Diversified` or `n/a` | broad ETFs are `Diversified`; single-sector ETFs keep their sector; bonds, cash and precious metals are `n/a` |
| asset_type | `stock` / `ETF` / `bond` / `corporate bond` / `cash` / `precious metal` | `bond` is a government bond; ETFs are treated as equity; bond ETFs are marked `bond`; `gold` and `silver` are read as `precious metal` |
| market_cap | `large` / `mid` / `small` / `n/a` | `n/a` for everything that is not a stock; large > $10bn, mid $2–10bn, small < $2bn |
| currency | `RON`, `USD`, `EUR`, … | the currency of the asset |
| region | `US` / `Europe` / `Romania` / `Emerging` / `Global` | the region of the company or fund, not of the currency; global ETFs are `Global`; bonds and cash take the region of the issuer or bank |

The 11 official GICS sectors: Energy, Materials, Industrials, Consumer Discretionary, Consumer Staples, Health Care, Financials, Information Technology, Communication Services, Utilities, Real Estate. Common aliases are accepted and replaced by the official name, in any letter case: for example Technology → Information Technology, Healthcare → Health Care, Telecom → Communication Services (full list in [rules.py](rules.py)).

`region` is optional: without it, the analysis runs without the region part. Every other column is required.

## Known limitations

- The Watch thresholds, the sector margin and the note thresholds are EXAMPLES until they are replaced with the rules from the author's bachelor's thesis.
- Funds are not looked inside: an S&P 500 fund and a company you also hold directly are not added together.
- There is no market reference for company sizes: the figures we had came from an index provider whose terms don't allow reproducing them.
- A corporate bond and a stock of the same company are not added together, because their names differ.
- No live prices: values are entered by hand, in lei.
- The details filled in automatically are approximate: market caps change, sectors come from SIC codes (not GICS), and each fund in the built-in list has one common listing, so if you bought it in another currency, change the currency in the editor.

## Sources

- Banz, R. W. (1981). The relationship between return and market value of common stocks. *Journal of Financial Economics*, 9(1), 3–18.
- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3–56.
- Froot, K. A. (1993). Currency hedging over long horizons. NBER Working Paper 4355.
- Campbell, J. Y., Serfaty-de Medeiros, K., & Viceira, L. M. (2010). Global currency hedging. *Journal of Finance*, 65(1), 87–121.
- Directive 2009/65/EC (UCITS), Article 52: the 5/10/40 diversification rule for funds.
- Investment Company Act of 1940, section 5(b)(1): at most 5% in one issuer for a diversified US fund.
- ERISA section 407(a): at most 10% of a US pension plan in the employer's own shares.
- U.S. Securities and Exchange Commission, Guidelines for Form N-1A, Guide 19 (1983): 25% or more in one industry is concentration.
- World Bank, World Development Indicators, CM.MKT.LCAP.CD (market capitalization of listed domestic companies), 2025. Licence CC BY 4.0.
- Directive 2009/65/EC (UCITS), Articles 53 (index funds) and 54 (government bonds).
- FINRA (2022). Concentrate on Concentration Risk. Investor Insights.
- Bessembinder, H. (2018). Do stocks outperform Treasury bills? *Journal of Financial Economics*, 129(3), 440–457.
- Statman, M. (1987). How many stocks make a diversified portfolio? *Journal of Financial and Quantitative Analysis*, 22(3), 353–363.
- U.S. Securities and Exchange Commission, EDGAR company tickers, submissions and XBRL frames (public float) APIs.
- OpenFIGI, Open Symbology API (Bloomberg; FIGI under the MIT licence).

## Licence and trademarks

The code is under the [MIT licence](LICENSE). GICS®, S&P 500®, Nasdaq-100®, MSCI® and FTSE® are trademarks of their respective owners, used here only to name what they refer to; this project is not affiliated with, endorsed or sponsored by any of them. The sectors in the built-in list are our own assignments, made from public information, not official GICS data.

## How it was built

Developed with the help of AI (Claude). The rules, product decisions and testing are mine.
