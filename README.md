# butler-skill-stable-earn

Lets the butler lend an owner's idle USDC on Base into Aave V3, show the live rate and
balance, and withdraw on request. Published to butlers: `SKILL.md` and
`references/explain.md`.

## How it works

- `earn_helper.py` (written by step 1) reads Aave's official address book
  (bgd-labs/aave-address-book) for the Pool, USDC and aUSDC addresses, cross-checks the
  aUSDC address against the Pool's own `getReserveData`, and reads balances, allowance,
  rate, utilization, reserve flags and the supply cap over public Base RPC.
- It builds calldata only: `approve` (exact amount), `supply`, `withdraw`. The butler
  sends each with `acp wallet send-transaction --chain-id 8453` under an idempotency key.
- The owner's address comes from `bevo-read me` (`user.agentWalletAddress`), the same
  read the shipped `papertrade-xyz` skill uses. An earlier draft used
  `acp wallet address`, which no shipped skill uses and which the validator cannot
  check — the container enumerates only `send-transaction`, `sign-typed-data` and
  `sign-message` under `acp wallet`.
- Function selectors were checked with keccak: approve `095ea7b3`, supply `617ba037`,
  withdraw `69328dec`, balanceOf `70a08231`, allowance `dd62ed3e`,
  getReserveData `35ea6a75`, totalSupply `18160ddd`.

## Validate

```bash
curl -sSLO https://virtual-protocol.github.io/butler-skills/tools/validate.py
python3 validate.py --standalone .
```

## To confirm before listing

- **Wallet policy.** `acp wallet send-transaction` is blocked unless the destination is
  allowed (wallet policies / Transaction Mode). The USDC token and the Aave Pool on Base
  must be allowed for butlers, or every send returns "Bad Request".
- **`--idempotency-key` on `acp wallet send-transaction`**, and the `bevo-read request`
  route for it (assumed `execute`).
- **Pocket behaviour** for raw transactions: whether an `approve` + `supply` pair raises
  two approval cards when the pocket is unfunded.
- **Network from the container** to raw.githubusercontent.com and the two public Base
  RPCs. If `bevo-rpc` is preferred, swap the helper's `call()` for it.
- **Keyword overlap** with `options-trading` ("earn on my usdc", "idle cash", "make my
  money work"). Suggest moving those to this skill as the lower-risk default and keeping
  options-specific phrases on `options-trading`.

## Next

- v0.2: a `stable-earn-sweep` duty template that sweeps idle USDC in above a floor and
  withdraws just-in-time when a trade or duty needs cash.
- v0.3: whitelisted Morpho vaults (ERC-4626 `deposit`/`redeem`) with rate-shopping.
