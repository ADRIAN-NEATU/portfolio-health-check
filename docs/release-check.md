# Release check – v0.1 MVP (2 Nov 2026)

Every feature, sorted by how ready it is, and the security and legal checks before the repository goes public.

## Features

| Rating | What it means |
|---|---|
| ✅ Solid | Core of the MVP: documented, tested, stable |
| 👍 Good | Works and is useful; small known limits |
| ⚠️ Good but sketchy | Works, but rests on example values or data that can be wrong |
| ⏭️ Sprint 2 | Good idea, not ready for v0.1 |
| ❌ Dropped | Tried or proposed, then dropped, with the reason |

### ✅ Solid
- Pick a sample, upload a CSV (also Excel with Romanian settings), download the template; clear messages for a missing column or a bad value.
- Type or paste positions; details fill in from the built-in list.
- The score from three parts (D9): sector (limit 25%, the US regulator's concentration level), positions (10%, EU and US fund law) and spread (the HHI against 30 stocks, Statman 1987). Every breach counts and costs more the bigger it is; tiers D to A+ on an animated gauge. Funds, government bonds and cash are outside the limits; a precious metal counts as one position (D12).
- Statuses OK, Watch, Just over, Over limit, each with a word and a colour.
- At a glance, warnings in order of severity, limit cards with "Why it matters" and the source.
- Charts by sector, currency, position and region; values inside the bars; tooltips that list the positions; click a bar to list them.
- Positions table, Stocks tab with a detail card, profile donut.
- "Before you start" window (just math, not advice, how the score works, how data is kept) and the footer.
- Privacy: the page makes no requests outside your computer; the online lookup sends only names and tickers.
- 235 automated tests; pinned package versions; tested on Python 3.12 and 3.15; one-click start on Windows.

### 👍 Good
- Insights: concentration index (HHI), top 5, other currencies, sector coverage, regions; the summary "What looks good / What to look at".
- Comparison of the US share with all listed companies in the world (World Bank, about 49%).
- Region note.
- Corporate bonds and precious metals count as a position (D7, D12); metals have their own slice in the asset mix and an insight.
- Ten stress-test portfolios.

### ⚠️ Good but sketchy
- **Example values**, not from the thesis or a source yet: Watch at 20% (sector), the 5-point sector margin, the region note (80%). The profile labels and the small-cap, large-cap and currency notes were removed (D10).
- **The score's own choices** (D9): equal weights of the three parts, the squared penalty, the caps and the tier boundaries.
- **Online lookup:** legal and free, but sector comes from SIC codes, not GICS, and size from the public float companies report, which is sometimes wrong by orders of magnitude.
- **Look and feel tied to Streamlit and Plotly internals** (tooltip cards, radio cards, chart overflow): pinned versions protect it; an upgrade may break it.

### ⏭️ Sprint 2
- Index funds counted by what they hold ("Inside your funds", Nasdaq-100 by sector): the code is ready, the figures need a public-domain source (SEC Form N-PORT).
- Give feedback through an anonymous form (S1-28): waits for the form link.
- Search with suggestions as you type (S1-17).
- Adding a company's bond and stock together; a yearly refresh of the World Bank figure; browser tests inside the project.

### ❌ Dropped
- Currency as a scored limit (D1): it punished money held in lei.
- "If a sector fell 20%" (S1-19): hard to read.
- Tips on how to raise the score, or "add assets of type X": too close to investment advice.
- Counting broad funds by what they hold in the score: even the world market would fail the limits.
- Index-provider figures in the project (D8): their terms don't allow it.
- Crypto-assets: not supported.
- Yahoo Finance: its terms don't allow automated extraction.
- A temporary e-mail, or an e-mail password in the code, for feedback.

## Security and legal checks

| Check | Result |
|---|---|
| Passwords, API keys, tokens in any commit | none |
| Local paths, e-mail or Jira site in the files | none; every commit uses GitHub's private no-reply address (since 4 Nov, for the whole history) |
| `notes/` and the real portfolio file | never committed; `notes/` is in `.gitignore` |
| Index-provider data (MSCI, Nasdaq, CRSP) | not in any file or any commit: the few figures older commits quoted were removed from the whole history on 4 Nov, before the first push |
| Requests from the page to other sites | none from the app (Google Fonts and the Google-hosted tab icon removed on 2 Nov). Online, the Streamlit Community Cloud page adds its own analytics and cookies (Google Analytics, Segment, Heap); the "Before you start" window and the README say so, with Streamlit's privacy policy |
| Licence | MIT, "as is", in `LICENSE` |
| Terms and privacy | `TERMS.md` and `PRIVACY.md` (5 Nov), linked in the footer and the "Before you start" window |
| Trademarks | GICS, S&P 500, Nasdaq-100, MSCI, FTSE named as their owners' marks in the README |
| Third-party data | SEC EDGAR (public domain), OpenFIGI (MIT), World Bank (CC BY 4.0, attributed) |
| Not investment advice | "Before you start" window with "I understand", a line under the title, the footer, no buy or sell recommendations |
| Sources' usage rules | SEC: identified requests, at most about 7 a second (its limit is 10); OpenFIGI: public API, without a key by default |
| Feedback | anonymous Google form: no name or e-mail asked, no sign-in; the app itself collects nothing |

**Still the owner's choice:**
- The documents mention shares from the author's real portfolio (68% in the US, Industrials 28.9%), without amounts.
