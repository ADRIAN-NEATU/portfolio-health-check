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

**Context.** S1-22 asked for a neutral question when one region holds a large share. A portfolio with 68% in the US got no note, because the note starts at 80%.

**Decision.** When the largest region is the US, the Regions insight adds a neutral comparison with the world stock market:
> "68% of your money is in the US. For comparison, the US is 60% of the world stock market."

A (?) next to it shows the source on hover. The comparison is not a target and says nothing about what to buy or sell. The region note threshold (80%) stays as it is.

**Why.** A comparison with a documented figure is easier to judge than an arbitrary threshold, and it stays neutral: the reader decides whether their share is intentional.

**Consequences.**
- Only the US has a world figure for now, because the factsheet gives country weights. Other regions keep the plain sentence.
- The figure changes every month: it lives in `rules.py`, with its date, and should be updated from the factsheet.

**Source.**
- MSCI ACWI Index factsheet (USD), 30 Sep 2026: country weights (figures removed from the project, D8).

## D5 – Insights marked Good when their limit is OK (1 Nov 2026, provisional)

**Context.** S1-20 asked for a colour per insight: good, watch, worth asking. The design so far used colour only where there is a problem.

**Decision (provisional, not final).** Keep Info and Watch, and add **Good**, with a green dot:
- **Watch:** the insight's limit is not OK, or its region or currency note is shown.
- **Good:** the insight belongs to a scored limit (sector or single position) and that limit is OK.
- **Info:** the insight has no limit (currency, regions).

Every label is a word as well as a colour. The question is still open: whether a third, "worth asking" label is needed, and whether green should be stronger.

