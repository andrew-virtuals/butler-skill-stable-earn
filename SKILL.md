---
name: stable-earn
description: Put your owner's idle USDC on Base to work in Aave's lending market, show the live rate and balance, and pull it back out when they need it.
version: 0.1.0
metadata: {"butler":{"moneyMoving":true,"keywords":["earn on my usdc","put my stables to work","idle usdc","savings","earn interest","lend my usdc","aave","stable earn","withdraw my savings","how much am i earning","my earn balance"],"requires":{"bins":["acp","bevo-read","python3","cat"]}}}
---

## When to use

Your owner wants their idle dollars earning: "put my stables to work", "earn on my
USDC", "move $2k into savings", "how much am I earning", "take $500 out of savings",
"withdraw everything from Aave".

This skill lends USDC on Base into Aave V3's USDC market. Borrowers pay interest, and
lenders earn it. The rate is variable and set by how much of the pool is borrowed.

Not this skill: options income (cash-secured puts, covered calls) is `options-trading`;
yield on ETH, HYPE or other tokens; fixed-rate products; anything off Base.

## Before you start

Find the owner's wallet address and holdings:

```sh
bevo-read me
bevo-read assets
```

The address is `user.agentWalletAddress` from `bevo-read me`, always.

Settle these in plain words before moving anything:

1. **How much.** A dollar amount of USDC on Base, never more than they hold. Suggest
   keeping some USDC out for trades and gas they expect to need soon.
2. **The trade-off.** The rate is variable, never promised. Funds sit in Aave's smart
   contracts on Base, not a bank: there is no deposit insurance, and there is smart
   contract and bad-debt risk. If the pool is almost fully borrowed, a withdrawal can
   have to wait until borrowers repay.
3. **Words.** Call it "Earn" or "lending on Aave", never a "savings account" or a
   "deposit", and never say "guaranteed" or "risk-free".

`references/explain.md` has how the yield works and the wording for the risks.

## Procedure

1. [FIXED] Save the read-and-build helper. It reads Aave's official address book and Base
   on-chain state, and only ever prints JSON; it never sends anything:

```sh
cat > earn_helper.py <<'PY'
import json, re, sys, urllib.request
from decimal import Decimal
RPCS = ["https://mainnet.base.org", "https://base-rpc.publicnode.com"]
BOOK = "https://raw.githubusercontent.com/bgd-labs/aave-address-book/main/src/ts/AaveV3Base.ts"
HEX40 = r"0x[0-9a-fA-F]{40}"
def out(d):
    print(json.dumps(d)); sys.exit(0)
def http(url, body=None):
    h = {"User-Agent": "butler-stable-earn", "Content-Type": "application/json"}
    with urllib.request.urlopen(urllib.request.Request(url, body, h), timeout=15) as f:
        return f.read().decode()
def book():
    t = http(BOOK)
    pool = re.search(r"export const POOL = '(%s)'" % HEX40, t).group(1)
    blk = re.search(r"\n  USDC: \{(.*?)\n  \}", t, re.S).group(1)
    pick = lambda k: re.search(k + r": '(%s)'" % HEX40, blk).group(1)
    return pool, pick("UNDERLYING"), pick("A_TOKEN")
def call(to, data):
    err = None
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    for url in RPCS:
        try:
            r = json.loads(http(url, body))
            if r.get("result"):
                return r["result"][2:]
            err = r.get("error")
        except Exception as e:
            err = str(e)
    out({"error": "rpc_unavailable", "detail": str(err)})
A = lambda x: x.lower()[2:].rjust(64, "0")
U = lambda n: format(n, "064x")
W = lambda h: [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]
APY = lambda ray: round(((1 + ray / 1e27 / 31536000) ** 31536000 - 1) * 100, 2)
def units(x):
    try:
        v = int(Decimal(x) * 10**6)
    except Exception:
        v = 0
    if v <= 0:
        out({"error": "bad_amount"})
    return v
cmd, owner = sys.argv[1], sys.argv[2]
if not re.fullmatch(HEX40, owner):
    out({"error": "bad_address"})
pool, usdc, ausdc = book()
rd = W(call(pool, "0x35ea6a75" + A(usdc)))
if "0x%040x" % rd[8] != ausdc.lower():
    out({"error": "address_mismatch"})
cfg = rd[0]
bal = lambda tok, who: W(call(tok, "0x70a08231" + A(who)))[0]
wallet, earning, cash = bal(usdc, owner), bal(ausdc, owner), bal(usdc, ausdc)
supply = W(call(ausdc, "0x18160ddd"))[0]
allow = W(call(usdc, "0xdd62ed3e" + A(owner) + A(pool)))[0]
cap = (cfg >> 116) & (2**36 - 1)
s = {"owner": owner, "pool": pool, "usdc": usdc, "ausdc": ausdc,
     "apy_pct": APY(rd[2]), "borrow_apy_pct": APY(rd[4]),
     "utilization_pct": round(100 * (1 - cash / supply), 1) if supply else 0.0,
     "wallet_usdc": wallet / 1e6, "earning_usdc": earning / 1e6,
     "withdrawable_now_usdc": min(earning, cash) / 1e6, "allowance_usdc": allow / 1e6,
     "est_week_usd": round(earning / 1e6 * APY(rd[2]) / 100 / 52, 2),
     "active": bool(cfg >> 56 & 1), "frozen": bool(cfg >> 57 & 1), "paused": bool(cfg >> 60 & 1),
     "cap_room_usdc": None if cap == 0 else max(0, cap * 10**6 - supply) / 1e6}
if cmd == "status":
    out(s)
if cmd == "supply":
    amt = units(sys.argv[3])
    if not s["active"] or s["frozen"] or s["paused"]:
        out({**s, "error": "market_closed"})
    if amt > wallet:
        out({**s, "error": "not_enough_usdc"})
    if s["cap_room_usdc"] is not None and amt / 1e6 > s["cap_room_usdc"]:
        out({**s, "error": "supply_cap_reached"})
    txs = [] if allow >= amt else [{"op": "approve", "to": usdc, "data": "0x095ea7b3" + A(pool) + U(amt)}]
    txs.append({"op": "supply", "to": pool, "data": "0x617ba037" + A(usdc) + U(amt) + A(owner) + U(0)})
    out({**s, "amount_usdc": amt / 1e6, "txs": txs})
if cmd == "withdraw":
    every = sys.argv[3] == "all"
    amt = 2**256 - 1 if every else units(sys.argv[3])
    need = earning if every else amt
    if s["paused"]:
        out({**s, "error": "market_paused"})
    if need == 0 or need > earning:
        out({**s, "error": "more_than_earning"})
    if need > cash:
        out({**s, "error": "not_enough_liquidity"})
    out({**s, "amount_usdc": need / 1e6, "txs": [{"op": "withdraw", "to": pool,
        "data": "0x69328dec" + A(usdc) + U(amt) + A(owner)}]})
out({"error": "bad_command"})
PY
```

2. [FIXED] Read the market and the owner's position. `<ADDRESS>` is
   `user.agentWalletAddress` from step "Before you start":

   ```sh
   python3 earn_helper.py status <ADDRESS>
   ```

   For "how much am I earning", stop here and answer from `earning_usdc`, `apy_pct` and
   `est_week_usd`. Never invent an "earned so far" figure: the helper does not track it.

3. [ADAPT] Build the transactions. To add money, `supply` with the agreed dollar amount;
   to take money out, `withdraw` with an amount or the word `all`:

   ```sh
   python3 earn_helper.py supply <ADDRESS> <AMOUNT>
   python3 earn_helper.py withdraw <ADDRESS> <AMOUNT>
   ```

   On any `error`, stop and use "Failure handling". Otherwise show the owner one line,
   for example "Lend 2,000 USDC on Aave (Base) at about 3.9% variable. Withdraw anytime
   liquidity allows." and get a clear yes before step 4.

4. [FIXED] Send each transaction in `txs`, in order, once. `KEY` is
   `earn-<owner's short address>-<UTC yyyymmddHHMM of their yes>`, with the `op` as suffix:

   ```sh
   acp wallet send-transaction --chain-id 8453 --to <tx.to> --data <tx.data> --idempotency-key <KEY>:<op> --json
   ```

   After an `approve`, re-run step 2 until `allowance_usdc` covers the amount before
   sending `supply`. If the answer says `"asked": true`, an approval card is up: tell
   the owner, and send the next transaction only after that request shows executed.

5. [FIXED] Confirm with step 2 that `earning_usdc` (or `wallet_usdc` after a withdrawal)
   moved by about the amount.

## Idempotency and retries

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
| `not_enough_usdc` | Say how much USDC on Base they have; offer that amount, or swapping or bridging in first. |
| `not_enough_liquidity` | The pool is almost fully borrowed. Offer `withdrawable_now_usdc` now and the rest later. Rates rise until borrowers repay, so it usually clears within hours. |
| `market_closed`, `market_paused` | Aave governance has frozen or paused USDC on Base. Do nothing and say so. |
| `supply_cap_reached` | Offer `cap_room_usdc`, or wait. |
| `address_mismatch`, `rpc_unavailable` | Do not send. Tell the owner the market could not be read safely, and try later. |
| The send is refused or returns "Bad Request" | Report it as given. The wallet's policy may not allow Aave's contracts yet. |
| An approval card times out | Nothing moved. Ask if they still want it. |

## Limits

- USDC on Base, Aave V3 only. No other assets, chains, protocols or vaults in v0.1.
- Lending only: this skill never borrows.
- One request at a time. Auto-sweeping idle cash on a schedule is a duty, not this skill.
- Interest accrues as the balance itself grows; there is nothing to claim.
- The approval is for the exact amount, never unlimited.
- Not financial advice and not a bank account.

## Say to the owner

After adding: "Done: 2,000 USDC is now earning about 3.9% (variable) on Aave. That's
roughly $1.50 a week at today's rate. Say 'withdraw from Earn' anytime."

After withdrawing: "500 USDC is back in your wallet. 1,500 USDC is still earning."

When asked how it's going: lead with the balance earning and today's rate, then the
rough weekly figure, and say the rate moves with demand.
