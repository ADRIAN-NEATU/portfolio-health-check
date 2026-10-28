# Putting Sprint 1 on the Jira board

About 10–15 minutes. Project **PHC** (Scrum). Epics E1–E6 and version v0.1 already exist.

## 1. Rename the version
Releases (or Versions) → **v0.1** → ••• → Edit:
- Name: `v0.1 – MVP`
- Release date: `2 Nov 2026`

## 2. Create the sprint items in the Backlog
In the Backlog, create one item per row. For each story, copy the user story and its criteria from [sprint-1.md](sprint-1.md) into Description.

| # | Type | Summary | Parent (epic) | Story points | Fix version | Label | Description |
|---|---|---|---|---|---|---|---|
| S1-01 | Task | Set up the project and write the example rules | E1 Cerințe și cercetare | 2 | v0.1 – MVP | must | – |
| S1-02 | Task | Create 8 sample portfolios and a CSV template | E5 Testare și lansare | 2 | v0.1 – MVP | must | – |
| S1-03 | Story | Load a sample portfolio or my own CSV | E2 Introducerea portofoliului | 3 | v0.1 – MVP | must | sprint-1.md › S1-03 |
| S1-04 | Story | See my concentration score and warnings | E4 Avertismente și scor | 5 | v0.1 – MVP | must | sprint-1.md › S1-04 |
| S1-05 | Story | See the essentials at a glance | E4 Avertismente și scor | 3 | v0.1 – MVP | must | sprint-1.md › S1-05 |
| S1-06 | Story | Read my profile and key insights | E3 Analiza diversificării | 3 | v0.1 – MVP | must | sprint-1.md › S1-06 |
| S1-07 | Story | Explore my portfolio in charts and a positions table | E3 Analiza diversificării | 2 | v0.1 – MVP | must | sprint-1.md › S1-07 |
| S1-08 | Story | Compare my stocks' company sizes with the market | E6 Analiza companiilor | 3 | v0.1 – MVP | must | sprint-1.md › S1-08 |
| S1-09 | Task | Automated tests and README | E5 Testare și lansare | 3 | v0.1 – MVP | must | – |
| S1-10 | Story | Type or paste positions and get the details filled in | E2 Introducerea portofoliului | 5 | v0.1 – MVP | must | sprint-1.md › S1-10 |
| S1-11 | Story | Upload a CSV straight from Excel, even with only names and values | E2 Introducerea portofoliului | 2 | v0.1 – MVP | must | sprint-1.md › S1-11 |
| S1-12 | Task | Polish: official GICS names, interface details, one-click start, screenshots | E5 Testare și lansare | 3 | v0.1 – MVP | must | – |
| S1-13 | Task | Replace the EXAMPLE thresholds with documented, simpler rules from my thesis | E4 Avertismente și scor | 3 | v0.1 – MVP | must | – |
| S1-14 | Task | Reread and explain the code | E5 Testare și lansare | 2 | v0.1 – MVP | must | – |
| S1-15 | Task | Publish the project on GitHub | E5 Testare și lansare | 1 | v0.1 – MVP | must | – |
| S1-16 | Story | Don't count RON as a currency risk for someone who earns in lei | E4 Avertismente și scor | 3 | v0.1 – MVP | must | sprint-1.md › S1-16 |

The epic goes in the **Parent** field. The points field is called "Story point estimate" or "Story Points", depending on the project type.

## 3. Start the sprint
- Drag the 16 items from the Backlog into **PHC Sprint 1**.
- Click **Start sprint** and set:
  - Name: `Sprint 1 – MVP`
  - Dates: 27 Oct 2026 – 2 Nov 2026
  - Goal: `A user loads a portfolio and, in under a minute, sees their concentration score, the main risks and key insights.`
- If Jira refuses a start date in the past, use today's date and add to the goal: `Work started on 27 Oct.`

## 4. Close what is already done
On the board, move S1-01 to S1-12 to **Done** and add this comment to each:

| Items | Comment |
|---|---|
| S1-01 to S1-09 | `Done on 27 Oct 2026` |
| S1-10 | `Done on 28 Oct 2026 – commits 0e8cd3c, a4b27a7, d1b4d0c` |
| S1-11 | `Done on 28 Oct 2026 – commits 796244f, bcbb19b` |
| S1-12 | `Done on 28 Oct 2026 – commits 2ec5891, c3ad7f7, 686b97c, c9a927c, b39e8dc, f347ba6` |

## 5. After each daily
For every new row under "Backlog changes" in [daily-log.md](daily-log.md), create an item the same way: type, summary, parent, points, version `v0.1 – MVP`, label `must`. Put it in the sprint if it is for this week; otherwise leave it in the Backlog.

From the Day 2 daily (28 Oct):
- **S1-16** is already in the table above and goes into the sprint.
- **S1-13:** if you already created it, update its summary to the one above.
- Create **S1-17** and leave it in the Backlog, without a version (it is for after v0.1):

| # | Type | Summary | Parent (epic) | Story points | Fix version | Label | Description |
|---|---|---|---|---|---|---|---|
| S1-17 | Story | Search bar with suggestions as you type a name or ticker | E2 Introducerea portofoliului | 3 | – | – | sprint-1.md › S1-17 |
