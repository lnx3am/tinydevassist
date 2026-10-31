"""Check a running TinyDevAssist HTTP API without printing generated content."""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    if not args.url.startswith(("http://", "https://")) or args.timeout < 1:
        parser.error("provide an HTTP(S) URL and a positive timeout")
    base = args.url.rstrip("/")
    try:
        with urlopen(f"{base}/healthz", timeout=min(args.timeout, 10)) as response:  # noqa: S310
            if response.status != 200:
                raise RuntimeError(f"health returned HTTP {response.status}")
        headers = {"Content-Type": "application/json"}
        api_key = os.environ.get("TINYDEVASSIST_API_KEY")
        if api_key:
            headers["X-API-Key"] = api_key
        request = Request(  # noqa: S310 - explicit operator URL
            f"{base}/generate",
            data=json.dumps(
                {"prompt": "How do I inspect my Git working tree?", "max_new_tokens": 32}
            ).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urlopen(request, timeout=args.timeout) as response:  # noqa: S310
            payload = json.load(response)
            if (
                response.status != 200
                or not isinstance(payload, dict)
                or not isinstance(payload.get("response"), str)
            ):
                raise RuntimeError("generation returned an invalid response")
            if not payload["response"].strip():
                raise RuntimeError("generation returned an empty response")
        print("HTTP 200; API inference returned a nonempty response")
        return 0
    except (HTTPError, URLError, OSError, RuntimeError, ValueError) as exc:
        print(f"API smoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
