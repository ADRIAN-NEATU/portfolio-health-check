# Daily log

## Day 1 – 27 Oct

- **Done:**
  - A user can pick one of 8 sample portfolios or upload their own CSV, starting from a template.
  - The app gives one score from 0 to 100, built from three limits (sector, single position, currency), each marked OK, Watch or Over limit.
  - "At a glance" shows the score, a one-sentence verdict, the investor profile and up to three findings that matter most.
  - Insights, exposure notes, charts, a stocks tab and a full positions table explain the details.
  - A calm design that also works on a phone, a README and automated tests.
- **Next:** use the app myself, polish what still looks unfinished, add screenshots.
- **Blockers:** TBD
- **My feedback:** TBD
- **Backlog changes:** TBD

## Day 2 – 28 Oct

- **Done:**
  - Moved the project to this computer. The app now starts on Windows with a double-click.
  - Sector names follow the official GICS standard, and the sector coverage insight now counts global funds.
  - Polished the look: sample portfolios as cards, chart choices as pills, cleaner tabs and tables. Added screenshots.
  - Positions can be typed or pasted into the app. Names and tickers fill in sector, size, currency and region, from a built-in list and from free online sources.
  - CSV files saved by Excel open as they are, and a file with only names and values can be completed in one click.
- **Next:** Day 3: stop counting RON as a currency risk (S1-16). Then documented, simpler rules (S1-13), reread and explain the code (S1-14), publish on GitHub (S1-15).
- **Blockers:** I don't know yet how the app will reach the public or friends for feedback. For now it only runs on my computer. I will sort it out.
- **My feedback:**
  - The design and the core features are nice.
  - Someone who buys in RON because they work in Romania should not get a currency problem. To be fixed on Day 3.
  - The score weights are still placeholders. They will be replaced with rules that are documented and simpler.
  - Search could be better, with a bar that suggests names as you type. Fine for the first version.
  - Nothing else to change or add for now: the points above are the priorities.
- **Backlog changes:**
  - New S1-16: don't count RON as a currency risk for someone who earns in lei (planned for Day 3).
  - Updated S1-13: the thresholds and weights will also be documented and simplified (no new item).
  - New S1-17: search bar with suggestions as you type (after v0.1).
