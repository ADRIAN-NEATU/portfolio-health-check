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

**Decision.** Keep 5% and 10%, now as documented thresholds rather than examples. The app says where they come from, under "Why it matters" on the Single position card, and says they are fund rules used as a reference.

**Consequences.**
- No score changes: the numbers stay the same.
- The sector thresholds (24% and 30%) remain examples. Finding a source for them is the rest of S1-13.
- The footer now says which thresholds are documented and which are examples.

**Sources.**
- Directive 2009/65/EC (UCITS), Article 52.
- Investment Company Act of 1940, section 5(b)(1), 15 U.S.C. 80a-5(b)(1).
- Employee Retirement Income Security Act of 1974 (ERISA), section 407(a), 29 U.S.C. 1107(a).
- FINRA (2022). Concentrate on Concentration Risk. Investor Insights, 15 June 2022.
- Bessembinder, H. (2018). Do stocks outperform Treasury bills? *Journal of Financial Economics*, 129(3), 440–457.
- Statman, M. (1987). How many stocks make a diversified portfolio? *Journal of Financial and Quantitative Analysis*, 22(3), 353–363.
