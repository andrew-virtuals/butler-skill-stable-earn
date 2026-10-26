# butler-skill-stable-earn

The home of **earning with stablecoins** for Butler: lending today, more lenders and
vaults as they are added. For the humans maintaining this repo - never published to a
butler. Only `SKILL.md` and `references/**/*.md` reach one.

## What it does

- **Answers the open question** - "how can I earn on my USDC?" - by asking one thing
  first: *"Is there a coin you'd be glad to own if it got cheaper?"* A no is lending, said
  as the right fit; a yes shows that asset's put on each `options-trading` venue
  (Derive, Paradex, Rysk) beside lending's live rate, promise first, and hands off. It
  never ranks by rate. This was `butler-skill-stable-yield`, folded in at 0.2.0 and
  deprecated.
- **Lends** an owner's idle USDC on Base into Aave V3, shows the live rate and balance,
  and withdraws on request.

`requires.skills: ["options-trading"]`, so installing this skill brings both: an owner
asking the open question can take either answer without a second install. An owner who
asks to "sell a put" gets `options-trading` alone.

## Growing it

Everything about earning with stablecoins lands here, never in a new repo: a new lender
or vault is a `references/<venue>.md`, a sweep duty is a `templates/<name>/`. Grow it the
way `options-trading` grew, on one server command (`acp earn … --venue <id>`, on Butler's
server) rather than per-venue raw transactions: the registry caps a `SKILL.md` body at 12,000
characters and keeps every money command in it, so per-venue transaction lines stop
fitting after two or three venues.

## How it works

- `references/helper.md` (written to `/tmp/earn_helper.py` by step 2) reads Aave's
  official address book (bgd-labs/aave-address-book) for the Pool, USDC and aUSDC
  addresses, cross-checks the aUSDC address against the Pool's own `getReserveData`, and
  reads balances, allowance, rate, utilization, reserve flags and the supply cap over
  public Base RPC.
- It builds calldata only: `approve` (exact amount), `supply`, `withdraw`. The butler
  sends each with `acp wallet send-transaction --chain-id 8453` under an idempotency key.
- The owner's address comes from `bevo-read me` (`user.agentWalletAddress`), the same
  read the shipped `papertrade-xyz` skill uses.
- Function selectors were checked with keccak: approve `095ea7b3`, supply `617ba037`,
  withdraw `69328dec`, balanceOf `70a08231`, allowance `dd62ed3e`,
  getReserveData `35ea6a75`, totalSupply `18160ddd`.

## Validate

```bash
curl -sSLO https://virtual-protocol.github.io/butler-skills/tools/validate.py
python3 validate.py --standalone .
```

`--all` additionally checks that `options-trading`, which this requires, is listed.

## Before listing

Not listed yet, and not ready to be:

- **Public RPC.** The helper reads Base through public nodes and the address book from
  raw.githubusercontent.com. Production should read through Butler's server instead.
- **Two bare cards per deposit.** An `approve` then a `supply`, each an "On-chain action
  → address" card, with the second waiting on the first. A server-side `acp earn`
  command would file one card that says what it does.
- **Wallet policy.** The USDC token and the Aave Pool on Base must be allowed for
  butlers, or every send returns "Bad Request".
- **`--idempotency-key` on `acp wallet send-transaction`**, and the `bevo-read request`
  route for it (assumed `execute`).
- **Keyword overlap** with `options-trading` ("earn on my usdc", "idle cash", "make my
  money work"): the generic phrases belong here as the lower-risk entry point, the
  options-specific ones there.

## Next

- A server-side `acp earn deposit|withdraw|account --venue aave` command, so this skill
  stops building raw transactions.
- A sweep duty template that lends idle USDC above a floor and withdraws just in time
  when a trade or duty needs cash.
- Whitelisted Morpho vaults (ERC-4626 `deposit`/`redeem`) as a second venue.
