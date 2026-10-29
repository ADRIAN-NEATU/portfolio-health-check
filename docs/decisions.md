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
