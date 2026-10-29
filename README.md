# stable-earn

The `stable-earn` skill for [Butler](https://github.com/Virtual-Protocol/butler-skills):
earning on idle stablecoins. It lends USDC on Base into Aave V3, and it answers the open
question ("how can I earn on my USDC?") by routing between lending and selling a put. This
README is for the people maintaining the repo. A butler receives only `SKILL.md` and
`references/**/*.md`.

- **Version:** 0.2.0 (`SKILL.md`). What changed in each release: `CHANGELOG.md`.
- **Installed from a GitHub link**, not listed in the skill hub (see Installing).
- **Routes to** `options-trading` (`mamamatcha/butler-skill-yield-notes`, listed in the
  hub) for selling a put.
- **Replaces** `butler-skill-stable-yield`, folded in at 0.2.0.

## Installing

Send the butler, in chat:

```text
Install this skill: https://github.com/mamamatcha/butler-skill-stable-earn/blob/main/SKILL.md
Then install options-trading from the skill hub, if it is not installed already.
```

A link install (`hub_install_url`) writes `SKILL.md` alone: no `references/`, and no
`requires.skills`. So `SKILL.md` fetches each reference file itself from one pinned
commit (`REF` below), and installs `options-trading` from the hub only when an owner
picks a put. To update an agent, send the same line again; to switch it to another
repo or fork, `hub_remove stable-earn` first.

## What it does

- **The open question.** Asked "how can I earn on my USDC", "what's the best yield", the
  skill asks one thing before any number: *"Is there a coin you'd be glad to own if it
  got cheaper?"* A no is lending, said as the right fit. A yes shows that asset's put on
  each `options-trading` venue (Derive, Paradex, Rysk) beside lending's live rate, the
  promise first, and hands off. It never ranks by rate and never counters a no.
- **Lending.** Supplies an amount of the owner's USDC on Base to Aave V3, shows the live
  rate and what they have lent, and withdraws part or all of it.

Not covered: borrowing, other assets or chains, other protocols, fixed-rate products,
and sweeping idle cash on a schedule.

## How the pieces fit

| Piece | Where | Does |
| --- | --- | --- |
| Who the owner is | `bevo-read me` | `user.agentWalletAddress`, the wallet that sends and receives. Never an address from the chat. |
| Reference files | `curl` from `raw.githubusercontent.com/mamamatcha/butler-skill-stable-earn/<REF>/references/` | Read at the commit `SKILL.md` pins (`REF`), never a branch. The helper is piped through `awk` straight to a file, so the agent never retypes it. |
| Reads and calldata | `references/helper.md`, fetched to `/tmp/earn_helper.py` and run with `python3` | Keyless and read-only. Takes the Pool, USDC, aUSDC and address-provider addresses from Aave's address book at a pinned commit, checks them on-chain, reads rate, utilization, balances, allowance, reserve flags and supply cap over public Base RPC, and builds `approve`, `supply` or `withdraw` calldata. It never sends. |
| Sending | `acp wallet send-transaction --chain-id 8453 ... --idempotency-key <KEY>:<op> --json` | One approval card per transaction. `asked: true` means a card is up. |
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

Write `references/helper.md`'s Python block to a file, then run it against mainnet with
any Base address that holds some USDC (the burn address does):

```sh
python3 earn_helper.py status <ADDRESS>
python3 earn_helper.py supply <ADDRESS> 10
python3 earn_helper.py withdraw <ADDRESS> all
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

### Moving the pins

There are two, and both are full commit hashes, never a branch or tag:

- **`REF`**, in `SKILL.md` (Before you start, and step 2): the commit of this repo whose
  `references/` a butler reads. Any change to a reference file is two commits: the
  reference change, then `SKILL.md` moved to that commit's hash. Merge PRs with a merge
  commit, never a squash, so the pinned hash stays on `main`.
- **`BOOK`**, in `references/helper.md`: the Aave address book. To move it, take the
  latest commit to `src/ts/AaveV3Base.ts` in `bgd-labs/aave-address-book`, read that
  file's `POOL`, `POOL_ADDRESSES_PROVIDER` and `USDC` block, check them against Aave's
  own docs, and run the checks above. Then move `REF` to the commit that carries it.

## Validating a change

```sh
curl -sSLO https://virtual-protocol.github.io/butler-skills/tools/validate.py
python3 validate.py --standalone .
```

CI runs the same. A link install checks only what Mastra needs, but keep the body under
the validator's 12,000 characters so the skill can still be listed one day: new detail
goes into a reference file, with a pointer to it in `SKILL.md`.

## Releasing

1. Bump `version` in `SKILL.md`, add the `CHANGELOG.md` entry, and move `REF` if any
   reference file changed.
2. Merge to `main` with a merge commit, and tag `vX.Y.Z`.
3. Agents installed from the `main` link pick it up when the install line is sent again;
   nothing updates them on its own.

## Growing it

Everything about earning on stablecoins lands here, not in a new repo. A new lender or
vault is a `references/<venue>.md` and its helper, giving the same `status`, `supply` and
`withdraw` JSON, so `SKILL.md`'s single send line takes any venue's `txs` unchanged. A
sweep duty is a `templates/<name>/`.

Planned:

- A server-side `acp earn deposit|withdraw|account --venue aave` command, so the owner
  approves one card that says what it does, and reads go through Butler's server rather
  than public RPC.
- A sweep duty that lends idle USDC above a floor and withdraws in time when a trade or
  duty needs cash.
- Morpho vaults (ERC-4626 `deposit`/`redeem`) as a second venue.

## Layout

```
SKILL.md              the procedure a butler follows
references/
  helper.md           the Aave read and calldata script
  compare.md          lending and selling a put, as promises
  explain.md          how lending works and its risks, in plain words
```
