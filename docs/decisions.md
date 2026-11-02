# Product decisions

## D1 – Currency is a note, not part of the score (29 Oct 2026)

**Context.** The score used three limits: sector, single position and currency. A portfolio held all in lei scored red on currency, although for someone who earns in lei, the leu is not a currency risk (feedback at the Daily Scrum, 28–29 Oct). The question behind S1-24 was how currency should count at all.

**Decision.** Currency is no longer a scored limit. The score comes from two limits: sector and single position. When one foreign currency (anything but RON) holds a large share of the portfolio, the app shows a neutral note:
> "90.3% of your portfolio is in USD. If USD falls against the leu, these holdings lose value in lei. Over long periods this tends to matter less than company and sector risk."

**Why.**
- Over long horizons, exchange rates tend to move back towards what prices and inflation justify, so currency effects partly even out. Froot (1993) shows that hedging currency risk matters a lot over short horizons and much less over long ones.
- For stocks, currency moves are smaller than the moves of the companies and sectors themselves, which the two limits already measure.
- For a Romanian investor, holding foreign currencies can lower risk rather than raise it. Some currencies, such as the US dollar, tend to rise when stock markets fall (Campbell, Serfaty-de Medeiros and Viceira, 2010).

**Consequences.**
- The leu never triggers anything, so S1-16 is solved by this decision.
- Scores change: Tech-heavy 83 → 75, Beginner 73 → 60, Andrei 81 → 94, All in RON and One global ETF 85 → 100.
- One global ETF and Andrei now show the currency note instead of a red limit.
- Still open: currency matters more for bonds and cash held in a foreign currency, and for money needed soon in lei. The note threshold (56%) is an example value.

**Sources.**
- Froot, K. A. (1993). Currency hedging over long horizons. NBER Working Paper 4355.
- Campbell, J. Y., Serfaty-de Medeiros, K., & Viceira, L. M. (2010). Global currency hedging. *Journal of Finance*, 65(1), 87–121.

## D2 – Single-position thresholds come from fund law (29 Oct 2026)

**Context.** The single-position limit used 5% (Watch) and 10% (limit), marked as example values. At the Day 3 Daily Scrum the question was: is there a documented maximum for one stock?

**What the sources say.**
- **No regulator sets a percentage for an individual investor.** FINRA's investor guidance on concentration risk speaks of "a large portion of your holdings" and gives no number. A suitable share depends on the investor.
- **The law does set limits for diversified funds, and they match 5% and 10%:**
  - EU, UCITS (Directive 2009/65/EC, art. 52): a fund may put at most 10% of its assets in one issuer, and the holdings above 5% may together make up at most 40% of the fund.
  - US, Investment Company Act of 1940, section 5(b)(1): a "diversified" fund holds at most 5% of its assets in one issuer, for at least 75% of its assets.
  - US, ERISA section 407(a): a defined-benefit pension plan may hold at most 10% of its assets in the employer's own shares.
- **Research explains why one stock is risky:**
  - Over 1926–2016, about 4% of US stocks created all the net gain of the market; more than half did worse than Treasury bills over their life (Bessembinder, 2018). Owning one stock heavily is a bet on being in that 4%.
  - A well-diversified portfolio of randomly chosen stocks needs at least 30–40 of them (Statman, 1987). At equal weights, that is about 2.5–3.3% each, below the 5% Watch threshold.

**Decision** (confirmed on 1 Nov 2026). Keep 5% and 10%, now as documented thresholds rather than examples. The app says where they come from, under "Why it matters" on the Single position card, and says they are fund rules used as a reference.

**Consequences.**
- No score changes: the numbers stay the same.
- The sector thresholds were still examples on 29 Oct. They got their source on 1 Nov (D3).
- The footer now says which thresholds are documented and which are examples.

**Sources.**
- Directive 2009/65/EC (UCITS), Article 52.
- Investment Company Act of 1940, section 5(b)(1), 15 U.S.C. 80a-5(b)(1).
- Employee Retirement Income Security Act of 1974 (ERISA), section 407(a), 29 U.S.C. 1107(a).
- FINRA (2022). Concentrate on Concentration Risk. Investor Insights, 15 June 2022.
- Bessembinder, H. (2018). Do stocks outperform Treasury bills? *Journal of Financial Economics*, 129(3), 440–457.
- Statman, M. (1987). How many stocks make a diversified portfolio? *Journal of Financial and Quantitative Analysis*, 22(3), 353–363.

## D3 – The sector limit is 25%, with a safety margin (1 Nov 2026)

**Context.** The sector limit was 30%, with Watch from 24%, both examples (rest of S1-13).

**What the sources say.** The US regulator (SEC) treats a fund that holds 25% or more of its assets in one industry as concentrated. A fund that does not want to be called concentrated may not buy more of an industry once it reaches 25%. The rule comes from Guide 19 to Form N-1A (1983); the guides were withdrawn in 1998, but the SEC staff and funds still apply the 25% test. As with D2, this is a rule for funds, and no regulator sets one for an individual investor.

**Decision.**
- Limit: **25%** (documented).
- Watch from **20%**: the same ratio to the limit as before (24/30 = 80%). An example value.
- **Safety margin of 5 points:** from 25% to 30%, the status is **Just over**, shown in a darker orange; above 30%, **Over limit** in red. The margin is our own choice, an example value.
- "Why it matters" on the Sector card gives the source and says the margin is the app's choice.

**Consequences.**
- The score formula is unchanged, now measured from 25%. The margin changes only the status and the colour.
- Scores change: Tech-heavy 75 → 66 (Information Technology 45%, Over limit), Andrei 94 → 91 (Information Technology 21.5%, Watch). The Beginner portfolio stays at 60, but its sector now shows Watch: Tesla alone is 20% of the portfolio, all in one sector.
- A real portfolio with Industrials at 28.9% now shows Just over, and its score drops from 85 to 79.
- S1-13 is done: both limits now come from documented rules. The Watch thresholds and the margin remain examples.

**Sources.**
- U.S. Securities and Exchange Commission (1983). Guidelines for Form N-1A, Guide 19 (industry concentration), as applied in SEC staff correspondence with funds and in the Sequoia Fund case at the US Court of Appeals for the Second Circuit (2019).

## D4 – Compare the largest region with the world market (1 Nov 2026)

*Updated by D8: the figure now comes from the World Bank (about 49%), no longer from an index provider.*

**Context.** S1-22 asked for a neutral question when one region holds a large share. A portfolio with 68% in the US got no note, because the note starts at 80%.

**Decision.** When the largest region is the US, the Regions insight adds a neutral comparison with the world stock market:
> "68% of your money is in the US. For comparison, the US is about 49% of the value of all listed companies in the world." (wording since D8)

A (?) next to it shows the source on hover. The comparison is not a target and says nothing about what to buy or sell. The region note threshold (80%) stays as it is.

**Why.** A comparison with a documented figure is easier to judge than an arbitrary threshold, and it stays neutral: the reader decides whether their share is intentional.

**Consequences.**
- Only the US has a world figure for now, because the factsheet gives country weights. Other regions keep the plain sentence.
- The figure changes every month: it lives in `rules.py`, with its date, and should be updated from the factsheet.

**Source.**
- First an index factsheet (MSCI ACWI); since D8, World Bank, World Development Indicators (CC BY 4.0).

## D5 – Insights marked Good when their limit is OK (1 Nov 2026, provisional)

**Context.** S1-20 asked for a colour per insight: good, watch, worth asking. The design so far used colour only where there is a problem.

**Decision (provisional, not final).** Keep Info and Watch, and add **Good**, with a green dot:
- **Watch:** the insight's limit is not OK, or its region or currency note is shown.
- **Good:** the insight belongs to a scored limit (sector or single position) and that limit is OK.
- **Info:** the insight has no limit (currency, regions).

Every label is a word as well as a colour. The question is still open: whether a third, "worth asking" label is needed, and whether green should be stronger.

## D6 – Index funds: diversified, with what they hold shown (1 Nov 2026)

*Updated by D8: the index figures were removed from the project the same day; the code stays and waits for public-domain figures.*

**Context.** The score treated every broad ETF as diversified and never looked inside it. Someone with an S&P 500 or Nasdaq-100 fund holds a lot of technology and the largest US companies, and may hold the same companies directly.

**What we found.**
- Even the world market is concentrated: in a world index, technology is about a third and the largest company is above 5% (index factsheet, 30 Sep 2026). Counting a world fund by what it holds would put it over the 25% sector limit and above 5% for one company: the score would punish holding the market.
- EU law gives index funds a higher limit, up to 20% in one company, because indices are concentrated (UCITS, art. 53).
- Look-through tools (for example Morningstar Portfolio X-Ray) count a fund's holdings in proportion to the money invested in it.

**Decision.**
- **A fund on a whole market** (a country, a region, the world) stays diversified: it does not count towards the limits.
- **A fund on a narrower index**, one that leaves sectors out, counts towards the sector limit by what it holds. Today that is the Nasdaq-100, which holds no financial companies. Single-sector ETFs already counted fully.
- **"Inside your funds"** (information, never in the score): the largest sector and the US share including the funds, the 3 largest companies through them, and the company with the largest total when it is also held directly. It is marked Watch when that total is above the single-position limit.
- Funds are recognised by name and counted as copies of their index. Data: `data/index_funds.csv`, from the factsheets of 30 Sep 2026. S&P 500 funds use MSCI USA and FTSE All-World funds use MSCI ACWI, as close proxies. Nasdaq uses its own industry groups (ICB); Alphabet and Meta were moved from Technology to Communication Services, where GICS puts them.

**Consequences.**
- No sample score changes: the samples hold only broad funds.
- Andrei sees that Apple is 8% directly plus 2.6% through his funds, 10.6% in total.
- The figures need updating from the factsheets, about every quarter.

**Sources.**
- MSCI index factsheets (USD), 30 Sep 2026: MSCI ACWI, MSCI World, MSCI USA, MSCI Emerging Markets.
- Nasdaq, Nasdaq-100 Index factsheet, 30 Sep 2026.
- Directive 2009/65/EC (UCITS), Article 53.

## D7 – Corporate bonds count; precious metals are information (1 Nov 2026)

**Decision.**
- **Government bonds** and cash stay outside the limits: EU law lets a fund hold up to 100% in government bonds from at least six issues (UCITS, art. 54).
- **Corporate bonds** are a new type, `corporate bond`, and count towards the single-position limit: their risk is the company's.
- **Precious metals** are a new type, `precious metal` (`gold` and `silver` are accepted). They get their own slice in the profile and an insight, and don't count towards the limits, as with currency (D1): they are not companies, and no documented limit exists for one investor.
- **Crypto-assets** are not supported.

**Sources.**
- Directive 2009/65/EC (UCITS), Article 54.

## D8 – Nothing in the project that its source doesn't allow (1 Nov 2026)

**Context.** Before the release, every figure in the project was checked against the terms of its source. Index providers don't allow their index data to be reproduced or redistributed without written consent (for MSCI: its terms of use and the terms for its index data).

**Decision.**
- **Index figures removed.** The table of what index funds hold (MSCI ACWI, World, USA, Emerging Markets and Nasdaq-100) is no longer in the project, and `data/index_funds.csv` is in `.gitignore`. Without it, every broad fund counts as diversified, as before D6. The code stays, tested on made-up figures, and waits for public-domain figures from the holdings US funds file with the SEC (Form N-PORT).
- **World comparison from the World Bank.** The Regions insight compares the US share with the US share of all listed companies in the world: about 49% in 2025 (World Bank, World Development Indicators, CC BY 4.0, reuse allowed with attribution). It replaces an index-provider figure, which measured something narrower: large and mid-size companies only.
- **No market reference for company sizes.** The CRSP figures were removed. The small-cap note now starts above 28% of the stocks, the threshold it had in practice, and is an example value.
- **Licence and trademarks.** The code is under the MIT licence. The README says that GICS, S&P 500, Nasdaq-100, MSCI and FTSE are their owners' trademarks and that the built-in sectors are our own assignments.
- **Kept, because their sources allow it:** laws and regulators' texts (UCITS, the Investment Company Act, ERISA, SEC guidance, FINRA), research papers cited by name, SEC EDGAR (public domain) and OpenFIGI (MIT licence).

**Also checked.** SEC blocks automated requests that don't identify themselves properly. The app's identification works; adding a web address to it got it blocked, so it stays as it is.

## D9 – A score from three parts, with a progressive penalty and tiers (2 Nov 2026)

**Context.** The score looked only at the largest sector and the largest position, and its steps (100, 80, 20) had no source. Six companies at 15% each scored the same as one company at 15% next to a world fund (75 both). Twenty equal stocks scored 100, although research says a well-diversified portfolio needs at least 30.

**Decision.**
- **Three parts of equal weight**, each 0–100: sector, positions and spread.
- **Sector and positions:** 100 minus a penalty for every category above its limit (25% and 10%), not only the largest. Each excess is measured in limits and squared, so the penalty grows faster than the breach: half a limit over costs 25 points, a full limit over costs 100.
- **Spread:** the HHI of the single companies (stocks and corporate bonds; each one's share in %, squared, added up), turned into the number of equal stocks it is worth (10,000 / HHI). 30 or more scores 100 (Statman, 1987). Funds, government bonds, cash and precious metals add nothing.
- **Watch and Just over cost nothing,** but a breach caps the score: below 95 while a limit is Just over, below 85 while one is Over limit, so the tier never contradicts a warning.
- **Tiers:** A+ from 95, A from 85, B from 70, C from 50, D below. The score is shown on a half-circle gauge, red to green, that draws in, swings to the score and counts up when a portfolio opens.
- **The HHI is shown** as an insight, with a (?) that explains it in plain words.
- **The region note stays:** a portfolio in one region gets the note, as Bucharest only does.

**Our choices, written as such:** the equal weights, squaring the excess, the caps and the tier boundaries. The limits (25%, 10%) and the 30 stocks come from the sources in D2, D3 and Statman (1987).

**Consequences.**
- Six companies at 15% plus cash: 75 → 42 (D). One company at 15% next to a world fund: 75 → 84 (B).
- Samples: Tech-heavy 66 → 79, Beginner 60 → 59, Andrei 91 → 98, Bucharest only 56 → 65, Five stocks a little index 63 → 39, 25 US large caps 100 → 94. A real portfolio of about 20 equal stocks with one sector Just over: 79 → 88 (A).
- The idea in S1-32 (a note below 30 equal stocks) is covered by the spread part.

**Sources.**
- Statman, M. (1987). How many stocks make a diversified portfolio? *Journal of Financial and Quantitative Analysis*, 22(3), 353–363.
- The HHI (Herfindahl–Hirschman Index) is the standard measure of concentration, used for example in competition law.

## D10 – A simpler screen, and nothing without a reason (2 Nov 2026)

**Context.** Before the release: the screen should read easily, the animation lagged, and anything without a source or a clear reason should go.

**Decision.**
- **Summary instead of "What matters most":** two short lists next to the score, "What looks good" (at most three points) and "What to look at" (breaches, warnings, spread below 30 stocks, the region note).
- **Only the needle moves.** The drawing segments and the counting number were removed: they made the page lag.
- **Removed, because their thresholds had no source:** the profile labels (Conservative, Balanced, Dynamic, at 60% and 30%), the small-cap note (28%), the large-cap note (90%) and the currency note (56%). The asset mix, the cap mix and the share outside RON are still shown, as facts.
- **Kept:** the region note (80%, example value), as asked; its text now names the region and its share.
- **Removed as duplicates:** the "Largest sector" insight (it is on the Sector card and in the summary) and the verdict line under the score (the summary replaces it).
- **The "Good" label is gone** (it replaces the provisional D5): insights show a pill only when there is something to watch.
- **"Your data"** now reads true both on a computer and in a shared online copy (Streamlit Community Cloud).

**Consequences.** No score changes. The screen has fewer elements, and the only example values left are the Watch thresholds, the sector margin and the region note.
- **HHI bands (added the same day):** well spread below 333 (30 or more equal stocks, Statman), partly spread to 1,000 (10 equal stocks would each sit at the 10% limit), concentrated to 2,500 (4 equal stocks would each be 25%, the size of the sector limit), very concentrated above. Shown on a small scale under the HHI insight.
