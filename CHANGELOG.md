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
  required bin.
- **Installs from a GitHub link.** A link install writes `SKILL.md` alone, so step 2
  fetches the helper with `curl` from a pinned commit of this repo, piped through `awk`
  straight to `/tmp/earn_helper.py`, and `compare.md` and `explain.md` are read the same
  way. The agent no longer retypes the helper. `curl` and `awk` join `requires.bins`.
  A link install skips `requires.skills`, so the put route installs `options-trading`
  from the hub when an owner picks it.
- **The address book is pinned to a commit.** The helper read `AaveV3Base.ts` from
  bgd-labs/aave-address-book's `main`, and only aUSDC was cross-checked, so a change
  upstream could have pointed the owner's `approve` and `supply` at another contract.
  It now reads one commit, and also checks the Pool against the address provider's
  `getPool` on-chain. A new pin is a release.
- An unreadable address book is `book_unavailable` and a call to an address with no
  code is `rpc_unavailable`, not a Python traceback; a missing amount is `bad_amount`
  and an unknown command `bad_command`, both before any network read. `SKILL.md` gives
  each error, and `more_than_earning`, its row.

## 0.1.0

- Lend USDC on Base into Aave V3, show live rate, balance and utilization, and withdraw
  part or all. Exact-amount approvals, address book cross-checked against the Pool.
- The owner's address comes from `bevo-read me`, the read shipped skills already use.
