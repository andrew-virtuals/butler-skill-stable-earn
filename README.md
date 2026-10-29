# stable-earn

The `stable-earn` skill for [Butler](https://github.com/Virtual-Protocol/butler-skills):
earning on idle stablecoins. It lends USDC on Base into Aave V3, and it answers the open
question ("how can I earn on my USDC?") by routing between lending and selling a put. This
README is for the people maintaining the repo. A butler receives `SKILL.md` and the
`references/*.md` and `scripts/*.py` files it names.

- **Version:** 0.2.0 (`SKILL.md`). What changed in each release: `CHANGELOG.md`.
- **Name:** `stable-earn`, not listed in the skill hub. It requires `options-trading`
  (`mamamatcha/butler-skill-yield-notes`) for the put route.
- **Replaces** `butler-skill-stable-yield`, folded in at 0.2.0.

## What it does

- **The open question.** Asked "how can I earn on my USDC", "what's the best yield", the
  skill asks one thing before any number: *"Is there a coin you'd be glad to own if it
  got cheaper?"* A no is lending, said as the right fit. A yes shows that asset's put on
  each `options-trading` venue (Derive, Paradex, Rysk) beside lending's live rate, the
  promise first, and hands off. It never ranks by rate and never counters a no.
- **Lending.** Supplies an amount of the owner's USDC to a lending venue, shows the live
  rate and what they have lent, and withdraws part or all of it.

Not covered: borrowing, assets other than USDC, fixed-rate products, and sweeping idle
cash on a schedule.

## Venues

| | Aave |
| --- | --- |
| Lends | USDC, Aave V3 |
| Chain | Base (`8453`) |
| Getting out | any time the pool has cash; near 100% utilization it waits |
| Script | `scripts/aave.py` |
| What differs | `references/aave.md` |

Aave is used unless the owner names another venue or already lends there.

## Installing

Send the butler, in chat:

```text
Install this skill: https://github.com/mamamatcha/butler-skill-stable-earn/blob/main/SKILL.md
```

The link install (`hub_install_url`) writes `SKILL.md` and every `references/*.md` and
`scripts/*.py` it names, from the same ref; a named file missing from the repo refuses
the install. That needs virtuals-agent with Virtual-Protocol/virtuals-agent#314: an
older agent installs `SKILL.md` alone, and step 2 then stops rather than run without
its script. Send the line again to update; to switch to another repo or fork,
`hub_remove stable-earn` first. The put route installs `options-trading` from the hub.

## How the pieces fit

| Piece | Where | Does |
| --- | --- | --- |
| Who the owner is | `bevo-read me` | `user.agentWalletAddress`, the wallet that sends and receives. Never an address from the chat. |
| Reads and calldata | `scripts/<venue>.py`, run in place with `python3 "$HOME/skills/stable-earn/scripts/<venue>.py"` | Keyless and read-only. Aave's takes the Pool, USDC, aUSDC and address-provider addresses from Aave's address book at a pinned commit, checks them on-chain, reads rate, utilization, balances, allowance, reserve flags and supply cap over public Base RPC, and builds `approve`, `supply` or `withdraw` calldata. It never sends. |
| Sending | `acp wallet send-transaction --chain-id <chain_id> ... --idempotency-key <KEY>:<op> --json` | One approval card per transaction, on the chain the helper names. `asked: true` means a card is up. |
| Outcome | `bevo-read request <KEY>:<op> --route execute` | Whether a send executed. A retry is always this lookup, never a second send. |
| Routing to puts | `options-trading` | Its own quote step and its own first-time checks. This skill carries no quote across. |

## Safety model

- **The contracts come from a pinned source and are checked on-chain.** The address book
  (`bgd-labs/aave-address-book`, `src/ts/AaveV3Base.ts`) is read at one commit, so a
  change upstream cannot move what the owner approves. The Pool must equal the address
  provider's `getPool`, and aUSDC the Pool's own `getReserveData`, or nothing is built
  (`address_mismatch`). No address is ever written in a published file.
- **Exact approvals.** `approve` is for the amount being supplied, never unlimited, and
  is skipped when the allowance already covers it.
- **Money only goes to the owner.** `supply` credits `onBehalfOf` the owner, and
  `withdraw` pays `to` the owner. Both are the `bevo-read me` address, which the helper
  checks is a 20-byte address before it goes into any calldata.
- **Every amount is checked before building.** Against wallet USDC, the supply cap, the
  reserve's active, frozen and paused flags, what is lent, and the pool's cash for a
  withdrawal. A refused build is an `error`, never a partial `txs`.
- **One key per transaction, never re-sent.** The owner approves each card in the app,
  and `supply` is sent only after `status` shows the allowance landed.
- **No secrets.** Nothing here signs: Butler's server signs with the owner's wallet after
  the owner approves the card.

What it does not protect against, so review knows: the public RPCs are trusted for
figures (a lying node can misstate a balance or rate, but cannot change where a
transaction goes), and the approval card shows a bare contract address, not "Supply to
Aave".

## Testing the helper

`tests/` runs offline in CI (`python3 -m unittest discover -s tests`). Against mainnet,
with any Base address that holds some USDC (the burn address does):

```sh
python3 scripts/aave.py status <ADDRESS>
python3 scripts/aave.py supply <ADDRESS> 10
python3 scripts/aave.py withdraw <ADDRESS> all
```

Check by hand after any change to the helper:

- `status` has no `error`, and `pool`, `usdc` and `ausdc` are Aave V3 Base's Pool, native
  USDC and aBasUSDC.
- `supply` builds `approve` then `supply` with no allowance, and `supply` alone with one.
  Over the wallet is `not_enough_usdc`.
- `withdraw all` builds one `withdraw` for everything lent; more than lent is
  `more_than_earning`.
- A missing or negative amount is `bad_amount`, a bad address `bad_address`, an unknown
  command `bad_command`, each with no network read.

### Moving the pin

The pin is the commit in `BOOK`, in `scripts/aave.py`. To move it, take the latest commit to
`src/ts/AaveV3Base.ts` in `bgd-labs/aave-address-book`, read that file's `POOL`,
`POOL_ADDRESSES_PROVIDER` and `USDC` block, check them against Aave's own docs, run the
checks above, and release it as a new version.

## Validating a change

```sh
curl -sSLO https://virtual-protocol.github.io/butler-skills/tools/validate.py
python3 validate.py --standalone .
```

CI runs the same. The validator refuses a `SKILL.md` body over 12,000 characters, so new
detail goes into a reference file with a pointer to it in `SKILL.md`.

## Releasing

1. Bump `version` in `SKILL.md` and add the `CHANGELOG.md` entry.
2. Merge to `main` with a merge commit, and tag `vX.Y.Z`.

## Adding a venue

Everything about earning on stablecoins lands here, not in a new repo. A venue is two
files and a row; `SKILL.md`'s steps do not change:

1. **`scripts/<venue>.py`**: standard library only, taking `status <ADDRESS>`,
   `supply <ADDRESS> <AMOUNT>` and `withdraw <ADDRESS> <AMOUNT|all>`, and printing one
   JSON object with the shared fields in `aave.md`: `venue`, `chain_id`, `apy_pct`, `wallet_usdc`, `earning_usdc`,
   `withdrawable_now_usdc`, `allowance_usdc`, `est_week_usd`, and `txs` (each
   `{op, to, data}`, in send order) or `error`. Errors `SKILL.md` already handles keep
   their names; a new one gets its row in `<venue>.md`. Addresses come from a pinned
   source and are checked on-chain, as Aave's are, never written in the file.
2. **`references/<venue>.md`**: only what differs, as `aave.md`: the market, what its
   status fields mean, its risks, and its "Say to the owner" lines.
3. **A row** in `SKILL.md`'s venue table (Before you start), and in this README's.

A sweep duty is a `templates/<name>/`.

Planned:

- A server-side `acp earn deposit|withdraw|account --venue <venue>` command, so the owner
  approves one card that says what it does, reads go through Butler's server rather than
  public RPC, and no helper is written at all.
- A sweep duty that lends idle USDC above a floor and withdraws in time when a trade or
  duty needs cash.
- Morpho vaults (ERC-4626 `deposit`/`redeem`) as a second venue.

## Layout

```
SKILL.md              the procedure a butler follows
scripts/
  aave.py             Aave's read and calldata script
tests/
  test_aave.py        offline checks of the script
references/
  aave.md             what is Aave's own: the market, its status, its risks
  compare.md          lending and selling a put, as promises
  explain.md          how lending works and its risks, in plain words
```
