"""CLI entry point for FAULTLINE (`python -m faultline ...`)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from faultline.core import analyze
from faultline.fixtures import SCENARIOS, make_dataset, parity_demo
from faultline.receipts import make_receipt, verify_receipt
from faultline.server import serve
from faultline.study import run_study


def _emit_output(payload: dict[str, Any], out_path: str | None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=True)
    if out_path:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="faultline",
        description="FAULTLINE: Joint-failure ensemble selection laboratory",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_demo = sub.add_parser("demo", help="Run single-seed synthetic experiment and emit receipt")
    p_demo.add_argument("--seed", type=int, default=4100)
    p_demo.add_argument("--cases", type=int, default=64)
    p_demo.add_argument("--scenario", choices=SCENARIOS, default="shared")
    p_demo.add_argument("--size", type=int, default=3)
    p_demo.add_argument("--out", type=str, default=None)

    p_study = sub.add_parser("study", help="Run paired multi-seed study and emit receipt")
    p_study.add_argument("--seed", type=int, default=4100)
    p_study.add_argument("--replicates", type=int, default=8)
    p_study.add_argument("--cases", type=int, default=64)
    p_study.add_argument("--scenario", choices=SCENARIOS, default="shared")
    p_study.add_argument("--size", type=int, default=3)
    p_study.add_argument("--out", type=str, default=None)

    p_parity = sub.add_parser("parity", help="Emit exact 3-bit even/odd parity demonstration receipt")
    p_parity.add_argument("--out", type=str, default=None)

    p_analyze = sub.add_parser("analyze", help="Analyze a faultline-dataset-v1 JSON file")
    p_analyze.add_argument("path", type=str, help="Path to dataset JSON file")
    p_analyze.add_argument("--size", type=int, default=3)
    p_analyze.add_argument("--out", type=str, default=None)

    p_verify = sub.add_parser("verify", help="Verify and replay a FAULTLINE receipt JSON file")
    p_verify.add_argument("path", type=str, help="Path to receipt JSON file")
    p_verify.add_argument("--out", type=str, default=None)

    p_serve = sub.add_parser("serve", help="Run loopback HTTP server and browser laboratory")
    p_serve.add_argument("--host", type=str, default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8786)

    args = parser.parse_args(argv)

    if args.command == "demo":
        cfg = {
            "seed": args.seed,
            "cases": args.cases,
            "scenario": args.scenario,
            "size": args.size,
        }
        ds = make_dataset(seed=args.seed, cases=args.cases, scenario=args.scenario)
        res = analyze(ds, size=args.size)
        rec = make_receipt("demo", cfg, res)
        _emit_output(rec, args.out)
        return 0

    if args.command == "study":
        if args.replicates < 1 or args.replicates > 64:
            raise ValueError("--replicates must be between 1 and 64.")
        seeds = list(range(args.seed, args.seed + args.replicates))
        cfg = {
            "seeds": seeds,
            "cases": args.cases,
            "scenario": args.scenario,
            "size": args.size,
        }
        res = run_study(seeds=seeds, cases=args.cases, size=args.size, scenario=args.scenario)
        rec = make_receipt("study", cfg, res)
        _emit_output(rec, args.out)
        return 0

    if args.command == "parity":
        demo = parity_demo()
        rec = make_receipt("parity", {}, demo)
        _emit_output(rec, args.out)
        return 0

    if args.command == "analyze":
        raw = Path(args.path).read_text(encoding="utf-8")
        dataset = json.loads(raw)
        res = analyze(dataset, size=args.size)
        rec = make_receipt("analyze", {"size": args.size}, res, input_data=dataset)
        _emit_output(rec, args.out)
        return 0

    if args.command == "verify":
        raw = Path(args.path).read_text(encoding="utf-8")
        receipt = json.loads(raw)
        ver = verify_receipt(receipt)
        _emit_output(ver, args.out)
        return 0 if ver.get("valid") else 1

    if args.command == "serve":
        serve(host=args.host, port=args.port)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
