# Changelog

## v0.1 – MVP (in progress)

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
