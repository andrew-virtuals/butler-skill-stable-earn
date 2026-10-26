# Changelog

## 0.2.0

- **The open question lives here now.** `stable-yield` is folded in and deprecated:
  asked "how can I earn on my USDC", the skill asks one question first - "is there a
  coin you'd be glad to own if it got cheaper?" A no is lending, said as the right fit;
  a yes shows that asset's put on each `options-trading` venue beside lending's live
  rate, promise first, and hands off. It never ranks by rate and never counters a no.
- `requires.skills: ["options-trading"]`, so installing this one brings both. Routing
  covers Derive, Paradex and Rysk, now all in `options-trading`; `stable-yield` named a
  separate `rysk` skill, which is deprecated.
- `references/compare.md` (from `stable-yield`) compares the promises without the
  hard-coded rates and minimums it carried: every figure is read live.
- The helper moved from a heredoc in `SKILL.md` to `references/helper.md`, written to
  `/tmp/earn_helper.py`, which frees the body for the routing; `cat` is no longer a
  required bin. Lending behaviour is unchanged.

## 0.1.0

- Lend USDC on Base into Aave V3, show live rate, balance and utilization, and withdraw
  part or all. Exact-amount approvals, address book cross-checked against the Pool.
- The owner's address comes from `bevo-read me`, the read shipped skills already use.
