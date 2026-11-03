"""duty.py run against scripted Base reads.

    python3 -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fake_bevo import WALLET, chain, run  # noqa: E402

AAVE_ROW = {"id": "aave-1", "siteHost": "app.aave.com", "account": WALLET}


class Lent(unittest.TestCase):
    def test_one_row_at_what_is_lent_with_its_rate_and_week(self):
        fake = run([chain(2004.12)])
        self.assertEqual(len(fake.rows), 1)
        row = fake.rows[0]
        self.assertEqual((row["site"], row["name"], row["usd"], row["account"]),
                         ("https://app.aave.com", "Aave", 2004.12, WALLET))
        self.assertEqual(row["positions"], [{
            "title": "USDC lent",
            "subtitle": "Aave V3 · Base",
            "valueUsd": 2004.12,
            "details": [{"label": "APY (variable)", "value": "4.58%"},
                        {"label": "About a week", "value": "$1.77"}],
        }])
        self.assertEqual(fake.statuses, [("ok", {"value": 2004.12, "apy": 4.58})])

    def test_checks_at_start_then_on_every_tick(self):
        fake = run([chain(5), chain(5.01), chain(250)], ticks=2)
        self.assertEqual([row["usd"] for row in fake.rows], [5, 5.01, 250])

    def test_reads_base_only(self):
        fake = run([chain(5)])
        self.assertEqual({rpc for rpc in fake.rpcs}, {(8453, "eth_call")})


class NothingLent(unittest.TestCase):
    def test_removes_its_own_row_and_writes_none(self):
        other = {"id": "other", "siteHost": "app.aave.com", "account": "0x" + "b" * 40}
        stake = {"id": "stake", "siteHost": "stake.com", "account": WALLET}
        fake = run([chain(0)], platforms=[AAVE_ROW, other, stake])
        self.assertEqual((fake.rows, fake.removed), ([], ["aave-1"]))
        self.assertEqual(fake.statuses, [("empty", {})])

    def test_dust_counts_as_nothing(self):
        fake = run([chain(0.004)], platforms=[AAVE_ROW])
        self.assertEqual((fake.rows, fake.removed), ([], ["aave-1"]))

    def test_a_full_withdrawal_removes_the_row_on_the_next_check(self):
        fake = run([chain(300), chain(0)], ticks=1, platforms=[AAVE_ROW])
        self.assertEqual([row["usd"] for row in fake.rows], [300])
        self.assertEqual(fake.removed, ["aave-1"])


class NeverAGuess(unittest.TestCase):
    def test_rpc_down_writes_and_removes_nothing(self):
        fake = run([chain(down=True)], platforms=[AAVE_ROW])
        self.assertEqual((fake.rows, fake.removed), ([], []))
        self.assertEqual(fake.statuses, [("unreadable", {})])

    def test_a_pool_that_is_not_the_pinned_one_writes_nothing(self):
        fake = run([chain(pool="0x" + "c" * 40)])
        self.assertEqual(fake.rows, [])
        self.assertEqual(fake.statuses, [("unreadable", {})])

    def test_an_atoken_that_is_not_the_pinned_one_writes_nothing(self):
        fake = run([chain(atoken="0x" + "d" * 40)])
        self.assertEqual(fake.rows, [])
        self.assertEqual(fake.statuses, [("unreadable", {})])

    def test_a_bad_wallet_never_reads(self):
        fake = run([chain(5)], ticks=2, wallet="me")
        self.assertEqual((fake.rpcs, fake.rows), ([], []))
        self.assertEqual(fake.statuses, [("blocked", {})])

    def test_a_checksummed_wallet_reads_its_lowercase(self):
        fake = run([chain(5)], wallet="0x00000000000000000000000000000000000000A1")
        self.assertEqual(fake.rows[0]["account"], WALLET)


if __name__ == "__main__":
    unittest.main()
