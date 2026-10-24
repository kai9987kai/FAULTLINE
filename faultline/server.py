"""Strict loopback HTTP server for the FAULTLINE browser laboratory."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from faultline import __version__
from faultline.core import analyze
from faultline.fixtures import make_dataset, parity_demo
from faultline.receipts import compute_source_sha256, make_receipt, verify_receipt
from faultline.study import run_study

MAX_BODY_BYTES = 4 * 1024 * 1024
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

STATIC_ROUTES: dict[str, tuple[str, str]] = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
}


def _parse_int_param(qs: dict[str, list[str]], key: str, default: int) -> int:
    raw = qs.get(key, [str(default)])[0]
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Query parameter '{key}' must be an integer; got {raw!r}.") from exc


class FaultlineRequestHandler(BaseHTTPRequestHandler):
    server_version = f"FaultlineHTTP/{__version__}"

    def log_message(self, format: str, *args: Any) -> None:
        # Keep console output quiet during automated tests and normal operation
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Any:
        length_str = self.headers.get("Content-Length")
        if not length_str:
            raise ValueError("Missing Content-Length header.")
        try:
            length = int(length_str)
        except ValueError as exc:
            raise ValueError("Invalid Content-Length header.") from exc
        if length < 0 or length > MAX_BODY_BYTES:
            raise OverflowError(f"Request body exceeds maximum of {MAX_BODY_BYTES} bytes.")
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise ValueError(f"Invalid JSON body: {exc}") from exc

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path in STATIC_ROUTES:
            fname, content_type = STATIC_ROUTES[path]
            fpath = WEB_DIR / fname
            if not fpath.is_file():
                self._send_json(404, {"error": f"Static asset '{fname}' not found."})
                return
            data = fpath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        try:
            if path == "/api/health":
                self._send_json(
                    200,
                    {
                        "status": "ok",
                        "service": "faultline",
                        "version": __version__,
                        "source_sha256": compute_source_sha256(),
                    },
                )
                return

            if path == "/api/parity":
                demo = parity_demo()
                rec = make_receipt("parity", {}, demo)
                self._send_json(
                    200,
                    {
                        "even": demo["even"],
                        "odd": demo["odd"],
                        "receipt": rec,
                    },
                )
                return

            if path == "/api/demo":
                seed = _parse_int_param(qs, "seed", 4100)
                cases = _parse_int_param(qs, "cases", 64)
                size = _parse_int_param(qs, "size", 3)
                scenario = qs.get("scenario", ["shared"])[0]
                cfg = {"seed": seed, "cases": cases, "scenario": scenario, "size": size}
                ds = make_dataset(seed=seed, cases=cases, scenario=scenario)
                res = analyze(ds, size=size)
                rec = make_receipt("demo", cfg, res)
                self._send_json(200, rec)
                return

            if path == "/api/study":
                seed = _parse_int_param(qs, "seed", 4100)
                replicates = _parse_int_param(qs, "replicates", 8)
                cases = _parse_int_param(qs, "cases", 64)
                size = _parse_int_param(qs, "size", 3)
                scenario = qs.get("scenario", ["shared"])[0]
                if replicates < 1 or replicates > 64:
                    raise ValueError("Parameter 'replicates' must be in 1..64.")
                seeds = list(range(seed, seed + replicates))
                cfg = {
                    "seeds": seeds,
                    "cases": cases,
                    "scenario": scenario,
                    "size": size,
                }
                res = run_study(seeds=seeds, cases=cases, size=size, scenario=scenario)
                rec = make_receipt("study", cfg, res)
                self._send_json(200, rec)
                return

            self._send_json(404, {"error": f"Unknown endpoint '{path}'."})
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"error": f"Internal server error: {exc}"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json_body()
            if path == "/api/analyze":
                if not isinstance(body, dict):
                    raise ValueError("Expected JSON object with 'dataset' and optional 'size'.")
                dataset = body.get("dataset")
                size = body.get("size", 3)
                if type(size) is not int:
                    raise ValueError("'size' must be an odd integer.")
                res = analyze(dataset, size=size)
                rec = make_receipt("analyze", {"size": size}, res, input_data=dataset)
                self._send_json(200, rec)
                return

            if path == "/api/verify":
                if not isinstance(body, dict):
                    raise ValueError("Expected receipt JSON object.")
                ver = verify_receipt(body)
                self._send_json(200, ver)
                return

            self._send_json(404, {"error": f"Unknown POST endpoint '{path}'."})
        except OverflowError as exc:
            self._send_json(413, {"error": str(exc)})
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"error": f"Internal server error: {exc}"})


def create_server(host: str = "127.0.0.1", port: int = 8786) -> ThreadingHTTPServer:
    """Create a bound ThreadingHTTPServer instance."""
    return ThreadingHTTPServer((host, port), FaultlineRequestHandler)


def serve(host: str = "127.0.0.1", port: int = 8786) -> None:
    """Run the loopback HTTP server until interrupted."""
    server = create_server(host=host, port=port)
    actual_port = server.server_port
    print(f"FAULTLINE laboratory listening on http://{host}:{actual_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
