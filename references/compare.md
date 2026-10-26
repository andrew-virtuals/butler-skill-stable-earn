# The routes, compared honestly

Use this when the owner asks what the differences really are, or "which is best". The
rates and minimums come from the live reads in `SKILL.md` step 1, never from here.

## They are not rates. They are promises.

| | Lend on Aave | Sell a put on Derive or Paradex | Sell a put on Rysk |
| --- | --- | --- | --- |
| **You are agreeing to** | nothing | to buy an asset lower | to buy an asset lower |
| **Your money stays** | dollars | dollars, unless assigned | dollars, unless assigned |
| **If the asset falls** | unaffected | you take the loss **in cash** | you **receive the asset** |
| **Rate** | variable, set by borrowing | higher, fixed at the sale | higher, fixed at the sale |
| **Locked** | no | until expiry, or a buy-back | until expiry, no way out early |
| **Smallest** | no minimum | the venue's minimum | Rysk's minimum, usually larger |
| **Can lose money?** | only to bad debt | yes, if the asset falls | yes, if the asset falls |

Read each figure live - `stable-earn`'s `status` for lending, `options-trading`'s quotes
for the puts - and say which venue it is from.

## Why the higher number is not "better"

Lending pays for taking almost no view. Selling a put pays more because the owner is
**selling someone insurance** against a fall. The extra is not free money: it is the
price of a promise, and the promise is sometimes called in.

An owner who hears "4% or 20%" and picks 20% has not chosen a yield. They have agreed to
buy the asset at the strike, and they should be told that in those words before any
number.

## The difference most people miss

**Derive and Paradex settle in cash. Rysk delivers the asset.**

If a put lands in the money:

- On **Derive or Paradex**, the collateral is reduced. The owner is simply down money;
  they do not get the asset unless something separately goes and buys it.
- On **Rysk**, the owner buys the asset at the strike and holds it. "You now own 2 ETH at
  $2,150" is literally true.

For an owner whose reason was *"I'd like to own ETH cheaper"*, those are opposite
outcomes. Say which one applies.

## Routing, in one question

> "Is there a coin you'd be glad to own if it got cheaper?"

- **No** -> lending. Say it as the right answer, not the small one. Nothing else on this
  page applies to them, so do not recite it.
- **Yes, and they name an asset** -> the options routes for *that asset*, Rysk first
  where it quotes it, because delivery matches the reason they gave. Keep lending on the
  list so the comparison stays honest.
- **Yes, but they want out early** -> lending. Every put locks the money until expiry.
- **Yes, but the amount is small** -> lending, or a venue whose minimum it clears. Rysk's
  minimums are real money, and a shortfall cannot be filled at all.

## What never to say

- Any ranking: "best", "I'd recommend", "the smart move".
- A rate before the promise it is paid for.
- "Safe", "guaranteed", "risk-free" about any route.
- A higher rate in answer to a no. A no ends it.
