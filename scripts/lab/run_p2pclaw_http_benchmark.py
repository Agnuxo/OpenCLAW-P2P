#!/usr/bin/env python3
"""HTTP benchmark for key P2PCLAW web surfaces."""
from __future__ import annotations
import csv
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
import requests

ENDPOINTS = [
    "https://www.p2pclaw.com/",
    "https://www.p2pclaw.com/silicon",
    "https://www.p2pclaw.com/lab",
    "https://www.p2pclaw.com/app/simulations",
    "https://www.p2pclaw.com/app/papers",
    "https://api-production-ff1b.up.railway.app/health",
    "https://api-production-ff1b.up.railway.app/swarm-status",
]

RUNS = 5
TIMEOUT_SECONDS = 20


@dataclass
class Result:
    url: str
    status_code: int
    run: int
    latency_ms: float
    bytes: int


def benchmark() -> list[Result]:
    results: list[Result] = []
    for url in ENDPOINTS:
        for run in range(1, RUNS + 1):
            start = time.perf_counter()
            try:
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
                latency = (time.perf_counter() - start) * 1000.0
                results.append(
                    Result(
                        url=url,
                        status_code=response.status_code,
                        run=run,
                        latency_ms=latency,
                        bytes=len(response.content),
                    )
                )
            except Exception:
                latency = (time.perf_counter() - start) * 1000.0
                results.append(
                    Result(
                        url=url,
                        status_code=0,
                        run=run,
                        latency_ms=latency,
                        bytes=0,
                    )
                )
    return results


def write_csv(results: list[Result], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp_utc", "url", "run", "status_code", "latency_ms", "bytes"])
        ts = datetime.now(timezone.utc).isoformat()
        for r in results:
            writer.writerow([ts, r.url, r.run, r.status_code, f"{r.latency_ms:.2f}", r.bytes])


def summarize(results: list[Result]) -> list[dict]:
    grouped = {}
    for r in results:
        grouped.setdefault(r.url, []).append(r)
    summary = []
    for url, rows in grouped.items():
        latencies = [r.latency_ms for r in rows]
        summary.append(
            {
                "url": url,
                "runs": len(rows),
                "status_mode": statistics.mode([r.status_code for r in rows]),
                "latency_mean_ms": round(statistics.mean(latencies), 2),
                "latency_median_ms": round(statistics.median(latencies), 2),
                "latency_p95_ms": round(sorted(latencies)[max(0, int(0.95 * len(latencies)) - 1)], 2),
                "bytes_mean": round(statistics.mean([r.bytes for r in rows]), 2),
            }
        )
    return summary


def write_summary(summary: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("# P2PCLAW HTTP Benchmark Summary\n\n")
        f.write("| Endpoint | Runs | Mode Status | Mean ms | Median ms | P95 ms | Mean bytes |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for row in summary:
            f.write(
                f"| {row['url']} | {row['runs']} | {row['status_mode']} | {row['latency_mean_ms']} | {row['latency_median_ms']} | {row['latency_p95_ms']} | {row['bytes_mean']} |\n"
            )


if __name__ == "__main__":
    out_csv = "docs/data/p2pclaw_http_benchmark_2026-03-29.csv"
    out_summary = "docs/data/p2pclaw_http_benchmark_2026-03-29_summary.md"
    rows = benchmark()
    write_csv(rows, out_csv)
    summary_rows = summarize(rows)
    write_summary(summary_rows, out_summary)
    print(f"Wrote {out_csv} and {out_summary}")
