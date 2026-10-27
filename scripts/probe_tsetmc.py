#!/usr/bin/env python3

import json
import ssl
import urllib.request
from datetime import datetime, timezone


TEST_URLS = {
    "index_b1_last_all_1": (
        "https://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/SelectedIndexes/1"
    ),
    "index_b1_last_all_2": (
        "https://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/SelectedIndexes/2"
    ),
    "instrument_search": (
        "https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/%D8%B6"
    ),
    "market_watch_excel": (
        "https://old.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0"
    ),
}


def fetch(url, timeout=20):
    started = datetime.now(timezone.utc)

    result = {
        "url": url,
        "ok": False,
        "status": None,
        "content_type": None,
        "bytes": 0,
        "elapsed_seconds": None,
        "error": None,
        "preview": None,
    }

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; TSETMC-Free-Bridge/1.0; +https://github.com)"
                ),
                "Accept": "*/*",
            },
        )

        # Do not disable TLS verification.
        context = ssl.create_default_context()

        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=context,
        ) as response:
            body = response.read()

            result["status"] = response.status
            result["content_type"] = response.headers.get("Content-Type")
            result["bytes"] = len(body)
            result["ok"] = 200 <= response.status < 300

            # Only keep a small diagnostic preview.
            preview = body[:500]

            try:
                result["preview"] = preview.decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                result["preview"] = repr(preview)

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    finished = datetime.now(timezone.utc)
    result["elapsed_seconds"] = round(
        (finished - started).total_seconds(),
        3,
    )

    return result


def main():
    started = datetime.now(timezone.utc)

    report = {
        "bridge": "tsetmc-free-bridge",
        "probe_version": "1.0",
        "timestamp_utc": started.isoformat(),
        "results": {},
    }

    for name, url in TEST_URLS.items():
        print(f"Testing: {name}")
        report["results"][name] = fetch(url)

        result = report["results"][name]

        if result["ok"]:
            print(
                f"  OK: HTTP {result['status']} "
                f"({result['bytes']} bytes)"
            )
        else:
            print(
                f"  FAILED: {result['status']} "
                f"{result['error']}"
            )

    print("\n" + json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
