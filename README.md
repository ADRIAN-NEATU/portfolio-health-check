# Portfolio Health Check

Portfolio Health Check is a local web tool that shows an individual investor, in under a minute, how concentrated their portfolio is. You pick a sample portfolio or upload a CSV of your positions. The app gives a score from 0 to 100, based on three concentration limits: sector, single position and currency. It then lists what to look at first, compares every figure with its threshold, and adds plain-language insights about asset classes, market cap and regions. It is analysis, not investment advice.

## Install and run

Requires Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501. Run the tests with `pytest`.

## How to read the score

The score is the average of three limit scores (sector, single position, currency), rounded to a whole number. Each limit scores 100 while its largest weight stays below the yellow threshold, falls linearly from 100 to 80 between the yellow threshold and the limit, and above the limit scores 80 − 60 × min(weight / limit − 1, 1), so never less than 20.

| Limit | Watch from | Limit | Not counted |
|---|---|---|---|
| Sector | 24% | 30% | Diversified, n/a |
| Single position | 5% | 10% | broad ETFs, bonds, cash |
| Currency | 56% | 70% | – |

All thresholds live in [rules.py](rules.py) and are examples (see Known limitations).

## Informative dimensions (not scored)

- **Asset classes:** the share of bonds and cash sets a profile (Conservative, Balanced or Dynamic). There is no right mix: it depends on the investor's profile, so it is described, not scored.
- **Market cap:** the stocks' small / mid / large split is compared with the US market. A note appears when small caps are well above the market share or when almost everything is large cap. As with asset classes, the right mix depends on the investor, so it does not affect the score.
- **Region:** the region of the company or fund, not of the currency, so it measures something different from the currency limit. It is shown as a note, not scored: the note appears when one region (Global funds excluded) holds most of the portfolio.
- **Insights:** effective number of positions, top 5 share, largest sector, a stress test on that sector, share outside RON, GICS sector coverage and regions. Each insight is labelled Info or Watch and has no effect on the score.

## CSV format

One row per position. Start from [data/template.csv](data/template.csv).

| Column | Values | Rules |
|---|---|---|
| asset | any name | |
| value | number > 0 | always in lei (RON) |
| sector | an official GICS sector name, `Diversified` or `n/a` | broad ETFs are `Diversified`; single-sector ETFs keep their sector; bonds and cash are `n/a` |
| asset_type | `stock` / `ETF` / `bond` / `cash` | ETFs are treated as equity; bond ETFs are marked `bond` |
| market_cap | `large` / `mid` / `small` / `n/a` | `n/a` for everything that is not a stock; large > $10bn, mid $2–10bn, small < $2bn |
| currency | `RON`, `USD`, `EUR`, … | the currency of the asset |
| region | `US` / `Europe` / `Romania` / `Emerging` / `Global` | the region of the company or fund, not of the currency; global ETFs are `Global`; bonds and cash take the region of the issuer or bank |

The 11 official GICS sectors: Energy, Materials, Industrials, Consumer Discretionary, Consumer Staples, Health Care, Financials, Information Technology, Communication Services, Utilities, Real Estate. Common aliases are accepted and replaced by the official name, in any letter case: for example Technology → Information Technology, Healthcare → Health Care, Telecom → Communication Services (full list in [rules.py](rules.py)).

`region` is optional: without it, the analysis runs without the region part. Every other column is required.

## Known limitations

- The thresholds are EXAMPLES until they are replaced with the rules from the author's bachelor's thesis.
- ETFs are not broken down into their companies, sectors or regions.
- The market-cap reference is approximate: CRSP uses cumulative cap bands, while the data here use dollar thresholds.
- Issuer risk on bonds is not analysed.
- No live prices: values are entered by hand, in lei.

## Sources

- CRSP US Total Market Index, factsheet (cap segments). Center for Research in Security Prices.
- Banz, R. W. (1981). The relationship between return and market value of common stocks. *Journal of Financial Economics*, 9(1), 3–18.
- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3–56.
- Directive 2009/65/EC (UCITS), Article 52: the 5/10/40 diversification rule for funds.

## How it was built

Developed with the help of AI (Claude). The rules, product decisions and testing are mine.
