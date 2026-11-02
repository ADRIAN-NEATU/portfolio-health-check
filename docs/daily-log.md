# Daily Scrum log

Five minutes at the end of each working day.

## Day 1 – 27 Oct

- **Done:**
  - A user can pick one of 8 sample portfolios or upload their own CSV, starting from a template.
  - The app gives one score from 0 to 100, built from three limits (sector, single position, currency), each marked OK, Watch or Over limit.
  - "At a glance" shows the score, a one-sentence verdict, the investor profile and up to three findings that matter most.
  - Insights, exposure notes, charts, a stocks tab and a full positions table explain the details.
  - A calm design that also works on a phone, a README and automated tests.
- **Next:** use the app myself, polish what still looks unfinished, add screenshots.
- **Impediments:** None
- **My feedback:** It was the first version, so I wrote the core features down on paper, from my own ideas, and worked from that list to have a working increment.
- **Product Backlog changes:** None. The Sprint Backlog started from that paper list.

## Day 2 – 28 Oct

- **Done:**
  - Moved the project to this computer. The app now starts on Windows with a double-click.
  - Sector names follow the official GICS standard, and the sector coverage insight now counts global funds.
  - Polished the look: sample portfolios as cards, chart choices as pills, cleaner tabs and tables. Added screenshots.
  - Positions can be typed or pasted into the app. Names and tickers fill in sector, size, currency and region, from a built-in list and from free online sources.
  - CSV files saved by Excel open as they are, and a file with only names and values can be completed in one click.
- **Next:** Day 3: stop counting RON as a currency risk (S1-16). Then documented, simpler rules (S1-13), reread and explain the code (S1-14), publish on GitHub (S1-15).
- **Impediments:** I don't know yet how the app will reach the public or friends for feedback. For now it only runs on my computer. I will sort it out.
- **My feedback:**
  - The design and the core features are nice.
  - Someone who buys in RON because they work in Romania should not get a currency problem. To be fixed on Day 3.
  - The score weights are still placeholders. They will be replaced with rules that are documented and simpler.
  - Search could be better, with a bar that suggests names as you type. Fine for the first version.
  - Nothing else to change or add for now: the points above are the priorities.
- **Product Backlog changes:**
  - New S1-16: don't count RON as a currency risk for someone who earns in lei (planned for Day 3).
  - Updated S1-13: the thresholds and weights will also be documented and simplified (no new item).
  - New S1-17: search bar with suggestions as you type (after v0.1).

## Day 3 – 29 Oct

- **Done:**
  - Set up Sprint 1 in Jira: 17 items with epics, points and the v0.1 – MVP version. 16 are in the Sprint and 1 is in the Product Backlog.
  - Started the Sprint with its goal and dates (27 Oct – 2 Nov). Moved the 12 finished items to Done, with their comments.
  - Added a burndown chart to the Sprint document.
- **Next:** review how currency and sector risk are calculated (S1-24), then decide the RON rule (S1-16). Decide which of today's new items come into this Sprint.
- **Impediments:** None
- **My feedback:**
  - I don't really understand "You hold 22 positions, but your portfolio behaves like 13 equal ones". It doesn't look well calculated; I need to check it.
  - "If Information Technology fell 20%, your portfolio would fall about 1.8%" isn't intuitive for someone who isn't good with numbers, and I don't get it either. Maybe just show the total exposure in %, by sector or by country.
  - "You cover 11 of 11 GICS sectors directly, plus global funds that span all sectors" is a good insight. Each insight should have a colour code, so the user knows what it means: good, bad, worth a question. Friendly, suggestive colours.
  - I like the Stocks page and how it shows each market-cap group in %.
  - In Charts, "n/a" and "Diversified" need explaining. What do they refer to? ETFs?
  - On my portfolio: I like what it says about market cap, and the yellow warning on a stock above 5%.
  - I don't understand the USD and currency part yet, but I'll work it out. Nothing warns me that 68% of my portfolio sits in one place. At least a question whether it's intentional, and maybe a hint to spread to Europe or elsewhere, or leave it as it is so it isn't financial advice. Not sure whether to add this now.
  - In the exposure charts I'd like to see which stocks or assets make up each category. For example: Industrials 28.9%, then a click, a hover or a "+" on the bar shows the stocks in it. The same for the other views.
  - I'm not sure how currency should work: if I hold US stocks, is it counted as if I had bought USD with RON? I don't think that's right. And Tech-heavy shouldn't look green when it's mostly tech. We need to work on how things are calculated.
  - The weights are still placeholders. That's fine: they will be checked against the literature at a later stage.
- **Product Backlog changes:**
  - New S1-18: explain "behaves like N equal positions" in plain words.
  - New S1-19: replace the stress test with simple exposure figures by sector and region.
  - New S1-20: colour each insight by what it means (good, watch, worth asking).
  - New S1-21: explain "n/a" and "Diversified" in the charts.
  - New S1-22: ask a neutral question when one region holds a large share of the portfolio.
  - New S1-23: see which positions make up each bar in the charts.
  - New S1-24: review how the currency and sector limits are calculated. S1-16 (RON) waits for it.
  - S1-13: the weights stay as placeholders for now, to be checked against the literature later.
  - S1-18 to S1-24 pulled into Sprint 1 (+15 points). Whatever is not Done by 2 Nov goes back to the Product Backlog.
- _Daily Scrum: 13 min 30 s._

## Day 7 – 2 Nov (last day of the Sprint)

- **Done since Day 3:**
  - 29 Oct: values inside the chart bars and card-like tooltips (S1-25). The single-position thresholds got their sources (D2).
  - 30–31 Oct: no Sprint work.
  - 1 Nov: the sector limit became 25%, with a safety margin (S1-13, D3). The US share is compared with the world (S1-22, D4). Insights are marked Good, Watch or Info (S1-20, D5). A "Before you start" window was added (S1-26). Index funds can be looked inside (S1-27, D6). Corporate bonds and precious metals are supported (S1-29, D7). Ten stress-test portfolios were added (S1-30). The release check removed everything its source doesn't allow (S1-31, D8).
  - 2 Nov: the page no longer loads anything from Google (fonts, tab icon). The release check is written up in [release-check.md](release-check.md).
- **Next:** Sprint Review and Retrospective, then the v0.1 release. I reread the code with my notes (S1-14).
- **Impediments:** None.
- **My feedback:** a portfolio made only of stocks should be flagged when it holds too few of them, and say why. Five stocks are already caught by the single-position limit, but 20 to 29 equal stocks score 100.
- **Product Backlog changes:** New S1-32: a note when a portfolio is mostly individual stocks spread as fewer than 30 equal ones (Statman, 1987), for Sprint 2.
- **Later the same day:** S1-33 gave the score a new formula, from three parts with the HHI ([D9](decisions.md)), shown on an animated gauge with tiers D to A+. Its spread part covers S1-32, which was removed.
