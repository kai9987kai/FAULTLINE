import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from faultline.core import analyze
from faultline.fixtures import make_dataset
from faultline.receipts import canonical_json_sha256, make_receipt, verify_receipt
from faultline.server import create_server


class TestReceiptsApiCli(unittest.TestCase):
    def test_receipt_replay_catches_hash_tampering_and_rehashed_fabrication(self):
        cfg = {"seed": 4100, "cases": 32, "scenario": "shared", "size": 3}
        ds = make_dataset(**{k: cfg[k] for k in ("seed", "cases", "scenario")})
        res = analyze(ds, size=cfg["size"])
        receipt = make_receipt("demo", cfg, res)

        ver_ok = verify_receipt(receipt)
        self.assertTrue(ver_ok["valid"], ver_ok)

        # 1. Naive tampering without updating hash
        tampered = copy.deepcopy(receipt)
        tampered["result"]["policies"][3]["test"]["worst_group_error"] = 0.0
        ver_tampered = verify_receipt(tampered)
        self.assertFalse(ver_tampered["valid"])
        self.assertIn("payload_sha256", ver_tampered["reason"])

        # 2. Rehashed fabricated metrics: attacker recomputes payload_sha256 after editing metrics
        rehashed = copy.deepcopy(tampered)
        payload = {
            "schema": rehashed["schema"],
            "kind": rehashed["kind"],
            "config": rehashed["config"],
            "source_sha256": rehashed["source_sha256"],
            "input_sha256": rehashed["input_sha256"],
            "result": rehashed["result"],
        }
        rehashed["payload_sha256"] = canonical_json_sha256(payload)
        ver_rehashed = verify_receipt(rehashed)
        self.assertFalse(ver_rehashed["valid"])
        self.assertIn("replay", ver_rehashed["reason"].lower())

        # 3. Source mismatch must be distinguished from payload hash failure
        bad_source = copy.deepcopy(receipt)
        bad_source["source_sha256"] = "0" * 64
        payload_src = {
            "schema": bad_source["schema"],
            "kind": bad_source["kind"],
            "config": bad_source["config"],
            "source_sha256": bad_source["source_sha256"],
            "input_sha256": bad_source["input_sha256"],
            "result": bad_source["result"],
        }
        bad_source["payload_sha256"] = canonical_json_sha256(payload_src)
        ver_source = verify_receipt(bad_source)
        self.assertFalse(ver_source["valid"])
        self.assertIn("source", ver_source["reason"].lower())

    def test_data_bound_analyze_receipt_verifies_and_rejects_data_substitution(self):
        ds1 = make_dataset(seed=4100, cases=16, scenario="shared")
        res1 = analyze(ds1, size=3)
        rec = make_receipt("analyze", {"size": 3}, res1, input_data=ds1)
        self.assertTrue(verify_receipt(rec)["valid"])

        # Substitute a different dataset while keeping original result
        ds2 = make_dataset(seed=4101, cases=16, scenario="shared")
        sub = copy.deepcopy(rec)
        sub["input_data"] = ds2
        self.assertFalse(verify_receipt(sub)["valid"])

    def test_http_endpoints_and_bounded_inputs(self):
        server = create_server("127.0.0.1", 0)
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{port}"
        try:
            # 1. Health
            with urllib.request.urlopen(f"{base_url}/api/health") as resp:
                health = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(health["status"], "ok")

            # 2. Parity
            with urllib.request.urlopen(f"{base_url}/api/parity") as resp:
                parity = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(parity["even"]["majority_error"], 0.75)
                self.assertEqual(parity["odd"]["majority_error"], 0.25)

            # 3. Demo + Verify
            with urllib.request.urlopen(
                f"{base_url}/api/demo?seed=4100&cases=16&scenario=shared&size=3"
            ) as resp:
                demo_rec = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(demo_rec["kind"], "demo")

            req = urllib.request.Request(
                f"{base_url}/api/verify",
                data=json.dumps(demo_rec).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                ver = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(ver["valid"])

            # 4. Study endpoint
            with urllib.request.urlopen(
                f"{base_url}/api/study?seed=4100&replicates=2&cases=16&scenario=shared&size=3"
            ) as resp:
                study_rec = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(study_rec["kind"], "study")
                self.assertEqual(study_rec["result"]["n_seeds"], 2)

            # 5. Analyze endpoint and invalid input rejection
            ds = make_dataset(seed=4102, cases=16, scenario="shared")
            req_an = urllib.request.Request(
                f"{base_url}/api/analyze",
                data=json.dumps({"dataset": ds, "size": 3}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_an) as resp:
                an_rec = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(an_rec["kind"], "analyze")
                self.assertTrue(verify_receipt(an_rec)["valid"])

            # Invalid dataset must return HTTP 400 with explicit JSON error
            bad_req = urllib.request.Request(
                f"{base_url}/api/analyze",
                data=json.dumps({"dataset": {"schema": "bad"}, "size": 3}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(bad_req)
            self.assertEqual(ctx.exception.code, 400)

            # 6. Static browser laboratory files
            for asset_path in ("/", "/styles.css", "/app.js"):
                with urllib.request.urlopen(f"{base_url}{asset_path}") as resp:
                    self.assertEqual(resp.status, 200)
                    self.assertGreater(len(resp.read()), 100)
        finally:
            server.shutdown()
            server.server_close()

    def test_cli_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "demo_receipt.json"
            proc_demo = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "faultline",
                    "demo",
                    "--seed",
                    "4100",
                    "--cases",
                    "16",
                    "--scenario",
                    "shared",
                    "--size",
                    "3",
                    "--out",
                    str(out_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertTrue(out_path.exists())
            proc_verify = subprocess.run(
                [sys.executable, "-m", "faultline", "verify", str(out_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            ver_out = json.loads(proc_verify.stdout)
            self.assertTrue(ver_out["valid"])


if __name__ == "__main__":
    unittest.main()
