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

## Day 4 – 30 Oct

(No daily that day. Written on 4 Nov.)

- **Done:** Nothing on the project. On 29 Oct, after the Day 3 daily, the values in the charts moved inside the bars, the tooltips got nicer, and the 5% and 10% limits got their sources.
- **Next:** Decide the open points: sector limits, the region question, insight colours.
- **Impediments:** None

## Day 5 – 31 Oct

(No daily that day. Written on 4 Nov.)

- **Done:** Nothing on the project.

## Day 6 – 1 Nov

(No daily that day. Written on 4 Nov.)

- **Done:**
  - The sector limit is now 25%, the level the US regulator uses for concentration. Up to 30% it shows as "Just over".
  - The US share is compared with the whole world, with the source behind a (?).
  - A "Before you start" window: the app is just math, not advice, how the score works and how my data is kept.
  - Corporate bonds and gold can be entered. Ten stress-test portfolios to check the limits.
  - Release check: I removed the index data I'm not allowed to use, fixed the package versions and added the MIT licence.
- **Next:** Check the screen and the score before the release.
- **Impediments:** None
- **My feedback:**
  - I don't want anything in the project that could get me in legal trouble.
  - Tips on how to raise the score are too close to advice. Explaining how the score works is enough.
  - An S&P 500 or a world fund adds diversification. It shouldn't count against you.
  - Feedback from users should come through an anonymous form, so I don't deal with personal data.
- **Product Backlog changes:** New S1-28: feedback form (waits for the link). S1-26, S1-27, S1-29, S1-30 and S1-31 pulled in and done the same day.

## Day 7 – 2 Nov (last day of the Sprint)

- **Done:**
  - The page no longer loads anything from Google.
  - New score from three parts: sector, positions and spread (HHI). The more you go over a limit, the more it costs.
  - The score is shown on a gauge from D to A+. Only the needle moves, the rest made the page lag.
  - Simpler screen: "What looks good" and "What to look at" next to the score. I removed what had no source. The region note stays.
  - The HHI has a small scale, so anyone can see what the number means.
- **Next:** Sprint Review and Retro, then the release. Reread the code with my notes (S1-14).
- **Impediments:** None
- **My feedback:**
  - A portfolio of only stocks should be flagged when it has too few of them, and say why. 20 equal stocks shouldn't get 100.
  - The score was calculated too simply. Going far over a limit should cost a lot more than going a bit over.
  - The HHI is important, but people need to understand it.
  - I want to share the app with my colleagues as a link.
- **Product Backlog changes:** S1-32 (too few stocks) is covered by the new score and removed. S1-33 and S1-34 done. S1-14 is not done, so it goes back to the Product Backlog.

## Day 8 – 3 Nov

(No daily that day. Written on 4 Nov.)

- **Done:** Nothing on the project.

## Day 9 – 4 Nov (getting ready for the release)

- **Done:**
  - All 10 ETFs from the Bucharest Stock Exchange and the biggest European ETFs are in the app's list, every ticker checked.
  - A BET fund now counts as about 20 companies, not as a fully spread fund. It works when you type only the ticker too.
  - Last legal and stability check: nothing secret goes to GitHub, no outside requests, no errors on 500 random portfolios.
  - Gold now counts as one position, with sources.
- **Next:** Sprint Review and Retro with the presentation. Then push, publish on Streamlit and send the link to colleagues.
- **Impediments:** The release is two days late, because of the extra checks and the ETF list.
- **My feedback:**
  - People who invest in BET funds or like ETFs need a good list of ETFs, but everything has to be legal. The biggest ones are enough for the MVP.
  - I don't see gold as a stock, but with a source it's fine to count it as one position.
- **Product Backlog changes:** The two Bucharest sector ETFs (energy, and energy and finance) wait for a decision.
