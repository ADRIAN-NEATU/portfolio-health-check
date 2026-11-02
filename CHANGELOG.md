# Changelog

## v0.1 – MVP (in progress)

### 2 Nov 2026
- A new score from three parts: sector, positions and spread. Every sector and company above its limit counts, not only the largest, and a bigger breach costs much more than a small one. The spread part uses the HHI: 30 or more equal stocks score full marks.
- The score is shown on a gauge with tiers from D to A+, red to green, that animates when a portfolio opens. While a limit is breached, the tier can't be the top one.
- A new insight shows your concentration index (HHI) on a scale from well spread to very concentrated; its (?) explains it in plain words.
- The page no longer loads anything from Google.
- A simpler screen: next to the score, "What looks good" and "What to look at". Only the needle moves, so the page no longer lags.
- Removed what had no source: the Conservative / Balanced / Dynamic labels and the small-cap, large-cap and currency notes. The asset mix, the company sizes and the share outside RON are still shown. The region note stays.
- The README explains how to share the app as a link, on Streamlit Community Cloud.

### 1 Nov 2026
- The sector limit is now 25%, the level the US regulator calls concentration. Watch starts at 20%.
- A sector up to 5 points over its limit shows as Just over, in a darker orange; above that, Over limit in red.
- "Why it matters" on the Sector card says where 25% comes from.
- When most of your money is in the US, the Regions insight compares it with the US share of all listed companies in the world (about 49%, World Bank). A (?) shows the source.
- Insights whose limit is OK are now marked Good, in green (provisional).
- A "Before you start" window explains, before you begin, that the app is just math and not investment advice, and how the score is calculated. "How the score works" at the bottom opens it again.
- Ten "Stress tests" in the side panel: portfolios built to sit right on a threshold, such as a sector just over its limit, both limits at their exact edge, or five stocks with a small index fund.
- Release check: the index figures and the market-size reference were removed, because their providers don't allow reproducing them. Funds count as diversified, and the small-cap note no longer compares with the US market.
- The packages are pinned to the versions the app was tested with, and Python 3.12 or newer is needed.
- The code is under the MIT licence.
- New position types: `corporate bond`, which counts as a position in the company, and `precious metal` (gold, silver), shown in the profile and outside the limits.
- The project is on GitHub.

### 29 Oct 2026
- Currency is no longer part of the score. When one foreign currency holds most of your portfolio, a note explains what that means in lei. Money in lei never counts as a currency risk.
- The score now comes from two limits: sector and single position.
- In Charts, hover over a bar to see the positions inside it, or click it to list them all.
- A note under the Sector chart explains "Diversified" (broad funds) and "n/a" (bonds and cash). The tables explain it too.
- The "what if a sector fell 20%" insight is gone. Your largest sector and region now show as simple percentages.
- "Behaves like N equal positions" now says why, in plain words.
- Every value in the charts now sits inside the end of its bar, and the limit line runs behind the bars, so it never crosses a value.
- Chart tooltips are small cards: the share first, then where it stands against the limit and the positions in it, lined up.
- The single-position thresholds (5% and 10%) now have sources: the limits EU and US law set for diversified funds. "Why it matters" on the Single position card says so.

### 28 Oct 2026
- You can type or paste your positions straight into the app.
- Type only a name or ticker and its value: sector, type, size, currency and region fill in by themselves. They come from a built-in list of about 220 well-known stocks and funds, and from free, open sources (the US regulator's public company database, SEC EDGAR, and OpenFIGI).
- A switch turns the online lookup off.
- CSV files saved by Excel with Romanian settings open as they are.
- A CSV with only names and values can be completed in one click.
- "Edit these positions" turns any sample into a starting point, and "Download as CSV" saves your positions.
- Sector names now follow the official GICS standard. Common names such as "Technology" or "Healthcare" are still accepted.
- The sector coverage insight no longer says "0 of 11" when you own global funds.
- A new look for the sample list, the upload area, the chart buttons, the tabs and the tables. Short tables no longer scroll inside.
- Double-click `start.bat` to start the app on Windows.
- Screenshots in the README.

### 27 Oct 2026
- First version: 8 sample portfolios, CSV upload and a template to start from.
- One score from 0 to 100, built from three limits: sector, single position and currency.
- An "At a glance" summary, the investor profile, insights and exposure notes.
- Charts, a stocks tab and a full positions table.
- Works on a phone. README and automated tests.
