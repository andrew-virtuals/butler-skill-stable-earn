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
- **Aave is a venue, and its helper is a real script.** The helper moved from a heredoc
  in `SKILL.md`, which the model retyped into `/tmp` on every use, to `scripts/aave.py`,
  installed with the skill and run in place; what is Aave's own (its market, status
  fields, risks and wording) is `references/aave.md`. `SKILL.md`'s steps run
  `scripts/<venue>.py` and send on the `chain_id` it answers with, so a new venue is a
  script, a reference and a table row. Every script answers with the same fields, now
  including `venue` and `chain_id`. `cat` is no longer a required bin. Installing from a
  link needs virtuals-agent with Virtual-Protocol/virtuals-agent#314, which brings the
  files `SKILL.md` names.
- `tests/test_aave.py` checks the script offline, the address book and every chain read
  stubbed: exact `approve`, `supply` and `withdraw` calldata, every refusal, and both
  address cross-checks. CI runs it.
- **The address book is pinned to a commit.** The helper read `AaveV3Base.ts` from
  bgd-labs/aave-address-book's `main`, and only aUSDC was cross-checked, so a change
  upstream could have pointed the owner's `approve` and `supply` at another contract.
  It now reads one commit, and also checks the Pool against the address provider's
  `getPool` on-chain. A new pin is a release.
- An unreadable address book is `book_unavailable` and a call to an address with no
  code is `rpc_unavailable`, not a Python traceback; an unknown command is
  `bad_command` and a malformed address `bad_address`, both before any network read,
  and a missing amount `bad_amount`. `SKILL.md` gives each error, and
  `more_than_earning`, its row.

## 0.1.0

- Lend USDC on Base into Aave V3, show live rate, balance and utilization, and withdraw
  part or all. Exact-amount approvals, address book cross-checked against the Pool.
- The owner's address comes from `bevo-read me`, the read shipped skills already use.
