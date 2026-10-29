# Putting a Sprint on the Jira board

About 10–15 minutes. Project **PHC** (Scrum). Epics E1–E6 and version v0.1 already exist.

**Sprint 1: done on 29 Oct 2026.** Jira accepted 27 Oct as the start date, and the comments came in with the import. The Jira key of each item is in [sprint-1.md](sprint-1.md).

## 1. Rename the version
Releases (or Versions) → **v0.1** → ••• → Edit:
- Name: `v0.1 – MVP`
- Release date: `2 Nov 2026`

## 2. Create the Sprint Backlog items
In the Backlog view (Jira's name for the Product Backlog), create one item per row. For each story, copy the user story and its criteria from [sprint-1.md](sprint-1.md) into Description.

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

### Faster: half by hand, half imported
1. Create **S1-01** and **S1-03** by hand, as above, to learn the fields.
2. Import the other 15 from [jira-import.csv](jira-import.csv): Jira settings → System → External system import → CSV (or the Import option in the project).
3. Match the columns:
   - Summary → Summary
   - Issue Type → Issue Type
   - Story Points → Story point estimate (or Story Points)
   - Fix Version → Fix versions
   - Labels → Labels
   - Description → Description
   - Comment → Comment
   - Don't import Doc ID and Epic (they are for you).
4. Set the epics by hand: in the Backlog, Ctrl+click the items of one epic (see the Epic column in the file), right-click → **Parent** → choose the epic. Repeat for each epic.
5. Rename the version (step 1) **before** importing, so "v0.1 – MVP" matches.

## 3. Sprint Planning: start the Sprint
- Drag the 16 items from the Product Backlog into **PHC Sprint 1**. They become the Sprint Backlog.
- Click **Start sprint** and set:
  - Name: `Sprint 1 – MVP`
  - Dates: 27 Oct 2026 – 2 Nov 2026
  - Sprint Goal: `A user loads a portfolio and, in under a minute, sees their concentration score, the main risks and key insights.`
- If Jira refuses a start date in the past, use today's date and add to the goal: `Work started on 27 Oct.`

## 4. Mark what already meets the Definition of Done
On the board, move S1-01 to S1-12 to **Done** and add this comment to each:

| Items | Comment |
|---|---|
| S1-01 to S1-09 | `Done on 27 Oct 2026` |
| S1-10 | `Done on 28 Oct 2026 – commits 0e8cd3c, a4b27a7, d1b4d0c` |
| S1-11 | `Done on 28 Oct 2026 – commits 796244f, bcbb19b` |
| S1-12 | `Done on 28 Oct 2026 – commits 2ec5891, c3ad7f7, 686b97c, c9a927c, b39e8dc, f347ba6` |

## 5. After each Daily Scrum
For every new row under "Product Backlog changes" in [daily-log.md](daily-log.md), create an item the same way: type, summary, parent, points, version `v0.1 – MVP`, label `must`. Put it in the Sprint if it is for this week; otherwise leave it in the Product Backlog.

From the Daily Scrum on 28 Oct:
- **S1-16** is already in the table above and goes into the Sprint.
- **S1-13:** if you already created it, update its summary to the one above.
- Create **S1-17** and leave it in the Product Backlog, without a version (it is for after v0.1):

| # | Type | Summary | Parent (epic) | Story points | Fix version | Label | Description |
|---|---|---|---|---|---|---|---|
| S1-17 | Story | Search bar with suggestions as you type a name or ticker | E2 Introducerea portofoliului | 3 | – | – | sprint-1.md › S1-17 |

From the Daily Scrum on 29 Oct: all seven go into Sprint 1. Import [jira-import-29-oct.csv](jira-import-29-oct.csv) the same way as before (don't map Doc ID or Epic), set each Parent from the table below, then drag the seven into the Sprint.

| # | Type | Summary | Parent (epic) | Story points | Description |
|---|---|---|---|---|---|
| S1-18 | Story | Explain "behaves like N equal positions" in plain words | E3 Analiza diversificării | 1 | sprint-1.md › S1-18 |
| S1-19 | Story | Replace the stress test with simple exposure figures by sector and region | E3 Analiza diversificării | 2 | sprint-1.md › S1-19 |
| S1-20 | Story | Colour each insight by what it means: good, watch, worth asking | E3 Analiza diversificării | 3 | sprint-1.md › S1-20 |
| S1-21 | Story | Explain "n/a" and "Diversified" in the charts | E3 Analiza diversificării | 1 | sprint-1.md › S1-21 |
| S1-22 | Story | Ask a neutral question when one region holds a large share | E4 Avertismente și scor | 2 | sprint-1.md › S1-22 |
| S1-23 | Story | See which positions make up each bar in the charts | E3 Analiza diversificării | 3 | sprint-1.md › S1-23 |
| S1-24 | Task | Review how the currency and sector limits are calculated | E4 Avertismente și scor | 3 | – |

## 6. Sprint Review and Sprint Retrospective (2 Nov)
- Fill in the two last sections of [sprint-1.md](sprint-1.md).
- On the board, click **Complete sprint**. Items that are not Done go back to the Product Backlog or to the next Sprint.
- If the Sprint Goal is met: Releases → **v0.1 – MVP** → **Release**.

## Burndown
Jira draws a live burndown that follows the cards: Backlog → the chart icon at the top right (Insights), or Reports → Burndown chart, with Sprint 1 – MVP selected and story points as the estimate. Items added to the Sprint raise the line. For Sprint 1, Jira shows all the Day 1–2 work on 29 Oct, because the cards were moved to Done that day. The burndown in [sprint-1.md](sprint-1.md) keeps the real days.

## Lessons from setting up Sprint 1
- **Summary:** type the title, not the document ID ("S1-01").
- **Work type:** check the icon. A green bookmark is a Story; a blue tick box is a Task.
- **Import:** don't map **Doc ID** (Jira would use it as the key) or **Epic** (Parent needs the epic's key, such as PHC-1).
- **Epics:** set them after the import: Ctrl+click the items, then right-click → Parent.
- **Version:** rename it before importing, so the names match exactly.
- **Keys:** Jira keys (PHC-x) follow the order of creation, not priority. Order the backlog by drag & drop, most important at the top.
