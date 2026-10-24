"""Source-bound cryptographic receipts and deterministic replay verification for FAULTLINE."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from faultline.core import analyze
from faultline.fixtures import make_dataset, parity_demo
from faultline.study import run_study

RECEIPT_SCHEMA = "faultline-receipt-v1"
VALID_KINDS: tuple[str, ...] = ("demo", "study", "parity", "analyze")
SOURCE_FILES: tuple[str, ...] = ("core.py", "fixtures.py", "study.py", "receipts.py")


def canonical_json_sha256(obj: Any) -> str:
    """Return SHA-256 hex digest of canonical JSON representation."""
    encoded = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_source_sha256() -> str:
    """Compute SHA-256 over normalized FAULTLINE computation source files."""
    pkg_dir = Path(__file__).resolve().parent
    hasher = hashlib.sha256()
    for fname in SOURCE_FILES:
        fpath = pkg_dir / fname
        raw = fpath.read_bytes().replace(b"\r\n", b"\n")
        hasher.update(f"file:{fname}:{len(raw)}\n".encode("utf-8"))
        hasher.update(raw)
        hasher.update(b"\n")
    return hasher.hexdigest()


def _payload_dict(
    schema: str,
    kind: str,
    config: dict[str, Any],
    source_sha256: str,
    input_sha256: str | None,
    result: Any,
) -> dict[str, Any]:
    return {
        "schema": schema,
        "kind": kind,
        "config": config,
        "source_sha256": source_sha256,
        "input_sha256": input_sha256,
        "result": result,
    }


def make_receipt(
    kind: str,
    config: dict[str, Any],
    result: dict[str, Any],
    input_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a source-bound, replayable FAULTLINE receipt."""
    if kind not in VALID_KINDS:
        raise ValueError(f"Unknown receipt kind '{kind}'; expected one of {VALID_KINDS}.")
    if not isinstance(config, dict):
        raise ValueError("Receipt 'config' must be a dict.")
    if not isinstance(result, dict):
        raise ValueError("Receipt 'result' must be a dict.")

    source_sha = compute_source_sha256()
    input_sha = canonical_json_sha256(input_data) if input_data is not None else None
    payload = _payload_dict(RECEIPT_SCHEMA, kind, config, source_sha, input_sha, result)
    payload_sha = canonical_json_sha256(payload)

    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "kind": kind,
        "config": config,
        "source_sha256": source_sha,
        "input_sha256": input_sha,
        "payload_sha256": payload_sha,
        "result": result,
    }
    if input_data is not None:
        receipt["input_data"] = input_data
    return receipt


def _recompute_from_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    kind = receipt.get("kind")
    cfg = receipt.get("config")
    if not isinstance(cfg, dict):
        raise ValueError("Receipt 'config' must be an object.")

    if kind == "demo":
        ds = make_dataset(
            seed=cfg.get("seed"),
            cases=cfg.get("cases"),
            scenario=cfg.get("scenario"),
        )
        return analyze(ds, size=cfg.get("size", 3))

    if kind == "study":
        return run_study(
            seeds=cfg.get("seeds", []),
            cases=cfg.get("cases", 64),
            size=cfg.get("size", 3),
            scenario=cfg.get("scenario", "shared"),
        )

    if kind == "parity":
        return parity_demo()

    if kind == "analyze":
        input_data = receipt.get("input_data")
        if not isinstance(input_data, dict):
            raise ValueError("Analyze receipt is missing 'input_data' required for replay.")
        return analyze(input_data, size=cfg.get("size", 3))

    raise ValueError(f"Unsupported receipt kind '{kind}'.")


def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Verify hash integrity, source identity, input binding, and full deterministic replay."""
    if not isinstance(receipt, dict):
        return {"valid": False, "reason": "Receipt must be a JSON object."}
    if receipt.get("schema") != RECEIPT_SCHEMA:
        return {
            "valid": False,
            "reason": f"Unknown receipt schema '{receipt.get('schema')}'; expected '{RECEIPT_SCHEMA}'.",
        }
    kind = receipt.get("kind")
    if kind not in VALID_KINDS:
        return {"valid": False, "reason": f"Unsupported receipt kind '{kind}'."}

    try:
        expected_payload = _payload_dict(
            schema=receipt["schema"],
            kind=kind,
            config=receipt.get("config"),
            source_sha256=receipt.get("source_sha256"),
            input_sha256=receipt.get("input_sha256"),
            result=receipt.get("result"),
        )
        computed_payload_sha = canonical_json_sha256(expected_payload)
    except Exception as exc:
        return {"valid": False, "reason": f"Invalid receipt structure: {exc}"}

    if receipt.get("payload_sha256") != computed_payload_sha:
        return {
            "valid": False,
            "reason": "payload_sha256 mismatch: receipt content was modified after signing.",
        }

    current_source_sha = compute_source_sha256()
    if receipt.get("source_sha256") != current_source_sha:
        return {
            "valid": False,
            "reason": "source_sha256 mismatch: local source code differs from receipt producer.",
        }

    if kind == "analyze":
        input_data = receipt.get("input_data")
        if not isinstance(input_data, dict):
            return {"valid": False, "reason": "input_sha256 mismatch: missing input_data for analyze replay."}
        if canonical_json_sha256(input_data) != receipt.get("input_sha256"):
            return {
                "valid": False,
                "reason": "input_sha256 mismatch: input_data does not match signed input hash.",
            }

    try:
        recomputed = _recompute_from_receipt(receipt)
    except Exception as exc:
        return {"valid": False, "reason": f"Replay execution failed: {exc}"}

    if canonical_json_sha256(recomputed) != canonical_json_sha256(receipt.get("result")):
        return {
            "valid": False,
            "reason": "Replay verification failed: recomputed result does not match receipt result (rehashed fabrication).",
        }

    return {
        "valid": True,
        "reason": "Verified: payload_sha256, source_sha256, and deterministic replay match.",
        "kind": kind,
        "payload_sha256": computed_payload_sha,
        "source_sha256": current_source_sha,
    }
