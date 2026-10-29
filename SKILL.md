---
name: stable-earn
description: Earn interest on idle USDC by lending it on Aave (Base) - see what is earning and today's variable rate, lend more, or withdraw any time the pool has cash.
version: 0.2.0
metadata: {"butler":{"moneyMoving":true,"keywords":["earn interest","earn interest on usdc","interest on my usdc","earn on my usdc","earn on idle usdc","idle usdc","idle stables","idle cash","my stables to work","make my money work","stablecoin yield","stablecoin interest","stablecoins interest","earn on stablecoins","best yield on usdc","best yield on stablecoins","usdc yield","usdc apy","usdc interest rate","passive income on usdc","lend usdc","lend my usdc","usdc lending","aave","aave usdc","lend on aave","deposit usdc to aave","supply usdc to aave","withdraw from aave","stable earn","earn","savings","usdc savings","how much am i earning","my earn balance","withdraw from earn","withdraw my savings","low risk yield","safest yield"],"requires":{"bins":["acp","bevo-read","python3"]}}}
---

## When to use

Your owner wants idle USDC earning interest, or wants to check or take out what is
already earning: "earn interest on my USDC", "put my stables to work", "move $2k into
Earn", "lend on Aave", "how much am I earning", "take $500 out of Earn".

This skill lends USDC to a lending venue: borrowers pay interest and lenders earn it, at
a variable rate set by how much of the pool is borrowed. The venues are listed in
"Before you start"; today that is Aave V3 on Base.

Not this skill: selling options or puts; yield on ETH, HYPE or anything that is not
dollars; fixed-rate products; borrowing.

## Before you start

1. **Venue.** `aave` unless they name another listed here, or the USDC they mean is
   already lent there. Each venue is `references/<venue>.md`, for what is its own, and
   `scripts/<venue>.py`, its script; every step below runs that venue's script. Never
   move money from one venue to another on your own.

   | Venue | Lends | Chain | Read | Script |
   | --- | --- | --- | --- | --- |
   | `aave` | USDC, Aave V3 | Base | `references/aave.md` | `scripts/aave.py` |

2. **How much.** A dollar amount of USDC on the venue's chain, never more than they
   hold. Suggest keeping some out for trades they expect to make soon.
3. **The trade-off.** The rate is variable, never promised. Funds sit in the venue's
   smart contracts, not a bank: no deposit insurance, and there is smart contract and
   bad-debt risk. If the pool is almost fully borrowed, a withdrawal can have to wait
   until borrowers repay.
4. **Words.** Call it "Earn" or "lending on <venue>", never a "savings account" or a
   "deposit", and never "guaranteed" or "risk-free". `references/explain.md` has how the
   yield works and the wording for the risks.

## Procedure

1. [FIXED] Read who the owner is. `<ADDRESS>` everywhere below is
   `user.agentWalletAddress` from this, always, never an address from the chat:

   ```sh
   bevo-read me
   ```

   The venue's script was installed with this skill, at
   `$HOME/skills/stable-earn/scripts/<venue>.py`. Run it where it is: never write, copy
   or edit a script, and never build a transaction any other way. It only prints JSON
   and never sends anything. Missing: say Earn is not set up right, and stop.

2. [FIXED] Read the market and the owner's position:

   ```sh
   python3 "$HOME/skills/stable-earn/scripts/<venue>.py" status <ADDRESS>
   ```

   For "how much am I earning", stop here and answer from `earning_usdc`, `apy_pct` and
   `est_week_usd`. Never invent an "earned so far" figure: the script does not track it.

3. [ADAPT] Build the transactions. To add money, `supply` with the agreed dollar amount;
   to take money out, `withdraw` with an amount or the word `all`:

   ```sh
   python3 "$HOME/skills/stable-earn/scripts/<venue>.py" supply <ADDRESS> <AMOUNT>
   python3 "$HOME/skills/stable-earn/scripts/<venue>.py" withdraw <ADDRESS> <AMOUNT>
   ```

   On any `error`, stop and use "Failure handling". Otherwise show the owner one line,
   with the venue and chain, the amount and `apy_pct` as variable, as in the venue's
   "Say to the owner", and get a clear yes before step 4.

4. [FIXED] Send each transaction in `txs`, in order, once, on the answer's `chain_id`.
   `KEY` is `earn-<venue>-<owner's short address>-<UTC yyyymmddHHMM of their yes>`, with
   the `op` as suffix:

   ```sh
   acp wallet send-transaction --chain-id <chain_id> --to <tx.to> --data <tx.data> --idempotency-key <KEY>:<op> --json
   ```

   After an `approve`, re-run step 2 until `allowance_usdc` covers the amount before
   sending `supply`. If the answer says `"asked": true`, an approval card is up: tell
   the owner, and send the next transaction only after that request shows executed.

5. [FIXED] Confirm with step 2 that `earning_usdc` (or `wallet_usdc` after a withdrawal)
   moved by about the amount.

## Idempotency and retries

Reads are free: re-run them rather than reasoning from a figure minutes old.

Each transaction is sent once under its own key (`<KEY>:approve`, `<KEY>:supply`,
`<KEY>:withdraw`). On an error, a timeout or an unclear answer, do not re-run the send:
look it up instead.

```sh
bevo-read request <KEY>:<op> --route execute
```

A send that is still pending is not a failed one: wait, then re-read step 2. Rebuild
transactions with step 3 only for a new request from the owner, under a new `KEY`.

## Failure handling

| Outcome | What to do |
| --- | --- |
| `not_enough_usdc` | Say how much USDC they have on the venue's chain; offer that amount, or swapping or bridging in first. |
| `not_enough_liquidity` | The pool is almost fully borrowed. Offer `withdrawable_now_usdc` now and the rest later. Rates rise until borrowers repay, so it usually clears within hours. |
| `market_closed`, `market_paused` | The venue has stopped new money, or all movement. Do nothing and say so (`references/<venue>.md`). |
| `supply_cap_reached` | Offer `cap_room_usdc`, or wait. |
| `more_than_earning` | Say what `earning_usdc` is and offer that, or `all`. |
| `address_mismatch`, `book_unavailable`, `rpc_unavailable` | Do not send, and never build a transaction by hand. Tell the owner the market could not be read safely, and try later. |
| `bad_amount`, `bad_address` | Re-read the amount they said and `user.agentWalletAddress`, then run it again. |
| The send is refused or returns "Bad Request" | Report it as given, and do not re-send. |
| An approval card times out | Nothing moved. Ask if they still want it. |
| "Which is best?", "is there anything higher?" | Give this venue's live rate and its risks. Never rank, recommend or compare against products this skill does not offer. |

## Limits

- Lends USDC on the venues in "Before you start" only; never borrows. No other assets.
- One request at a time. Auto-sweeping idle cash on a schedule is a duty, not this skill.
- Interest accrues as the balance itself grows; there is nothing to claim.
- The approval is for the exact amount, never unlimited.
- Not financial advice and not a bank account.

## Say to the owner

After adding: "Done: 2,000 USDC is now earning about 3.9% (variable) on Aave. That's
roughly $1.50 a week at today's rate. Say 'withdraw from Earn' anytime." Each venue's
file has its own lines.

After withdrawing: "500 USDC is back in your wallet. 1,500 USDC is still earning."

When asked how it's going: lead with the balance earning and today's rate, then the
rough weekly figure, and say the rate moves with demand.
