# Aave: what is different

Everything in `SKILL.md` holds on Aave. This file is only what is Aave's own. `aave` is
the default venue: use it unless the owner names another venue this skill lists, or the
USDC they mean is already lent there.

## The market

Aave V3's USDC market on **Base** (chain `8453`), native USDC only. Lenders get aUSDC,
whose balance grows every block as interest arrives: nothing to claim, nothing locked.
The rate is variable, set by how much of the pool is borrowed, and moves block by block.

Quotes and calldata come from `references/aave-helper.md`, written to
`/tmp/earn_aave.py`. Add money is `approve` (exact amount, skipped when the allowance
covers it) then `supply`; take it out is one `withdraw`, an amount or `all`.

## Reading the status

- `utilization_pct` near 100: nearly the whole pool is lent out. A withdrawal can take
  only `withdrawable_now_usdc` until borrowers repay or new money arrives. The rate
  jumps when that happens, which usually clears it within hours. Say so before a
  supply, not only when a withdrawal is short.
- `frozen`: Aave governance stopped new supply. Withdrawing still works.
- `paused`: nothing moves, in or out, until governance unpauses it.
- `cap_room_usdc`: how much more the market takes before its supply cap. `null` is no
  cap.

## Risks, Aave's words

- **Bad debt.** Every loan is backed by more collateral than it borrows, and is
  liquidated when that cushion runs thin. If prices crash faster than liquidations can
  run, the pool can take a loss, and lenders share it.
- **Smart contracts and price feeds.** Long-running and audited, never risk-free.
- **USDC itself.** aUSDC is only as good as the USDC under it.

## Say to the owner

"Lend 2,000 USDC on Aave (Base) at about 3.9% today, variable. You can take it out
whenever the pool has room."

When `utilization_pct` is high: "Almost all of Aave's USDC is lent out right now, so a
large withdrawal could wait a few hours. Rates are higher while that lasts."
