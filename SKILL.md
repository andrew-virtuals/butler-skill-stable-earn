---
name: stable-earn
description: Earn on idle stablecoins - lend USDC on Aave (Base) with the live rate and balance, or, for an owner who would own a coin cheaper, hand off to selling a put.
version: 0.2.0
metadata: {"butler":{"moneyMoving":true,"keywords":["earn on my usdc","put my stables to work","idle usdc","idle stables","savings","earn interest","lend my usdc","aave","stable earn","withdraw my savings","how much am i earning","my earn balance","earn yield","what can i earn","best yield on usdc","where should i put my stables","how to earn on my usdc","yield options","compare yield","safest yield","highest yield"],"requires":{"bins":["acp","bevo-read","python3","curl","awk"],"skills":["options-trading"]}}}
---

## When to use

Your owner wants their idle dollars earning. Two ways in:

- **The open question** - "how can I earn on my USDC", "what's the best yield", "where
  should I put my stables": they have not chosen a product, so do not sell them one.
  Start at step 1.
- **Lending, named** - "put my stables to work", "move $2k into Earn", "how much am I
  earning", "take $500 out of Earn": start at step 2.

This skill lends USDC on Base into Aave V3's USDC market: borrowers pay interest and
lenders earn it, at a variable rate set by how much of the pool is borrowed. Selling a
put is the other route, and it lives in `options-trading`.

Not this skill: an owner who already named an options trade ("sell a put") - go straight
to `options-trading`; yield on ETH, HYPE or anything that is not dollars; fixed-rate
products; lending off Base.

## Before you start

1. **The rates are not the comparison.** Lending and selling a put are different
   promises, not one product at two rates:

   | Route | What the owner agrees to | Getting out |
   | --- | --- | --- |
   | Lend on Aave | Nothing. The dollars stay dollars. | Any time the pool has liquidity |
   | Sell a put | To **buy an asset** if it falls below a price | Not until expiry |

   So the question that decides it is not "how much" but: **"Is there a coin you'd be
   glad to own if it got cheaper?"** Ask it before showing any number, and take the
   answer at face value: never counter a no with a higher rate.
   `references/compare.md` has the full comparison.

2. **How much.** A dollar amount of USDC on Base, never more than they hold. Suggest
   keeping some out for trades they expect to make soon.
3. **The trade-off.** The rate is variable, never promised. Funds sit in Aave's smart
   contracts on Base, not a bank: no deposit insurance, and there is smart contract and
   bad-debt risk. If the pool is almost fully borrowed, a withdrawal can have to wait
   until borrowers repay.
4. **Words.** Call it "Earn" or "lending on Aave", never a "savings account" or a
   "deposit", and never "guaranteed" or "risk-free". `references/explain.md` has how the
   yield works and the wording for the risks.
5. **Reference files are fetched, not installed.** A GitHub-link install brings this
   file alone. Every `references/<file>.md` named here is read from one pinned commit,
   never a branch: `curl -fsSL https://raw.githubusercontent.com/mamamatcha/butler-skill-stable-earn/20c909230eda8b5ae4a11c068fcbbffc575af8a4/references/<file>.md`.
   If it cannot be read, say so and stop; never write a helper from memory.

## Procedure

1. [ADAPT] Only for the open question. Read what they hold, then ask the question from
   "Before you start" and wait for the answer:

   ```sh
   bevo-read me
   bevo-read assets
   ```

   - **No:** lending is the answer - say it as the right fit, not the lesser one ("your
     money stays dollars, out whenever the pool has room"), and go on to step 2. Never
     mention the higher rates again.
   - **Yes, naming an asset:** for that asset only, show lending's live rate (step 3)
     beside what `options-trading` quotes for it on each venue, read with that skill's
     own step 2 - never a remembered number. Promise first, rate second; Rysk first
     where it quotes that asset, because it delivers the asset they said they want,
     while Derive and Paradex settle in cash. Then let them pick: lending goes on to
     step 2; a put hands off to `options-trading` and stops here, carrying no quote.
     Without `options-trading` installed, `hub_install options-trading` first.

2. [FIXED] Fetch the helper from the pinned commit into `/tmp/earn_helper.py`, never
   retyping it. It only prints JSON and never sends anything:

   ```sh
   curl -fsSL https://raw.githubusercontent.com/mamamatcha/butler-skill-stable-earn/20c909230eda8b5ae4a11c068fcbbffc575af8a4/references/helper.md | awk '/^```python$/{f=1;next} /^```$/{f=0} f' > /tmp/earn_helper.py
   ```

   An empty file or a failed fetch: say the market cannot be read now, and stop.

3. [FIXED] Read the market and the owner's position. `<ADDRESS>` is
   `user.agentWalletAddress` from `bevo-read me`, always:

   ```sh
   python3 /tmp/earn_helper.py status <ADDRESS>
   ```

   For "how much am I earning", stop here and answer from `earning_usdc`, `apy_pct` and
   `est_week_usd`. Never invent an "earned so far" figure: the helper does not track it.

4. [ADAPT] Build the transactions. To add money, `supply` with the agreed dollar amount;
   to take money out, `withdraw` with an amount or the word `all`:

   ```sh
   python3 /tmp/earn_helper.py supply <ADDRESS> <AMOUNT>
   python3 /tmp/earn_helper.py withdraw <ADDRESS> <AMOUNT>
   ```

   On any `error`, stop and use "Failure handling". Otherwise show the owner one line,
   for example "Lend 2,000 USDC on Aave (Base) at about 3.9% variable. Withdraw anytime
   liquidity allows." and get a clear yes before step 5.

5. [FIXED] Send each transaction in `txs`, in order, once. `KEY` is
   `earn-<owner's short address>-<UTC yyyymmddHHMM of their yes>`, with the `op` as suffix:

   ```sh
   acp wallet send-transaction --chain-id 8453 --to <tx.to> --data <tx.data> --idempotency-key <KEY>:<op> --json
   ```

   After an `approve`, re-run step 3 until `allowance_usdc` covers the amount before
   sending `supply`. If the answer says `"asked": true`, an approval card is up: tell
   the owner, and send the next transaction only after that request shows executed.

6. [FIXED] Confirm with step 3 that `earning_usdc` (or `wallet_usdc` after a withdrawal)
   moved by about the amount.

## Idempotency and retries

Reads are free: re-run them rather than reasoning from a figure minutes old, and a rate
shown in step 1 is for choosing a route, never for acting on.

Each transaction is sent once under its own key (`<KEY>:approve`, `<KEY>:supply`,
`<KEY>:withdraw`). On an error, a timeout or an unclear answer, do not re-run the send:
look it up instead.

```sh
bevo-read request <KEY>:<op> --route execute
```

A send that is still pending is not a failed one: wait, then re-read step 3. Rebuild
transactions with step 4 only for a new request from the owner, under a new `KEY`.

## Failure handling

| Outcome | What to do |
| --- | --- |
| A route in step 1 cannot be read | Leave it out and say it is unavailable right now. Never show a remembered rate. |
| They ask "which is best" | Best is the one whose promise they are happy with. Give the promises again, not a ranking. |
| Their amount is under the options minimums | Say the minimum plainly and that lending has none. Do not suggest a bigger amount. |
| They say no to owning the asset | Lending, full stop. Never re-offer options at another strike or asset. |
| `not_enough_usdc` | Say how much USDC on Base they have; offer that amount, or swapping or bridging in first. |
| `not_enough_liquidity` | The pool is almost fully borrowed. Offer `withdrawable_now_usdc` now and the rest later. Rates rise until borrowers repay, so it usually clears within hours. |
| `market_closed`, `market_paused` | Aave governance has frozen or paused USDC on Base. Do nothing and say so. |
| `supply_cap_reached` | Offer `cap_room_usdc`, or wait. |
| `more_than_earning` | Say what `earning_usdc` is and offer that, or `all`. |
| `address_mismatch`, `book_unavailable`, `rpc_unavailable` | Do not send, and never build a transaction by hand. Tell the owner the market could not be read safely, and try later. |
| `bad_amount`, `bad_address` | Re-read the amount they said and `user.agentWalletAddress`, then run it again. |
| The send is refused or returns "Bad Request" | Report it as given, and do not re-send. |
| An approval card times out | Nothing moved. Ask if they still want it. |

## Limits

- Lends USDC on Base, Aave V3 only; never borrows. No other assets, chains, protocols or
  vaults yet.
- Compares two routes only: lending here, and selling a put through `options-trading`.
  Never ranks by rate, and never counters a no with a higher one.
- One request at a time. Auto-sweeping idle cash on a schedule is a duty, not this skill.
- Interest accrues as the balance itself grows; there is nothing to claim.
- The approval is for the exact amount, never unlimited.
- Not financial advice and not a bank account.

## Say to the owner

Open the open question with the question, not a rate: "Before I show you numbers - is
there a coin you'd be glad to own if it got cheaper? That one answer changes what's
worth doing with this money."

After adding: "Done: 2,000 USDC is now earning about 3.9% (variable) on Aave. That's
roughly $1.50 a week at today's rate. Say 'withdraw from Earn' anytime."

After withdrawing: "500 USDC is back in your wallet. 1,500 USDC is still earning."

When asked how it's going: lead with the balance earning and today's rate, then the
rough weekly figure, and say the rate moves with demand.
