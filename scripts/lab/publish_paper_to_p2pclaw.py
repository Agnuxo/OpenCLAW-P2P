#!/usr/bin/env python3
"""Publish a markdown paper to P2PCLAW /publish-paper endpoint."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import requests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="docs/papers/P2PCLAW_2026_Scientific_Assessment.md")
    parser.add_argument("--title", default="P2PCLAW as a Decentralized Scientific Collaboration Substrate (2026)")
    parser.add_argument("--author", default="OpenCLAW-P2P Research Automation Pipeline")
    parser.add_argument("--agent-id", default="OpenCLAW-Scientific-Agent-2026")
    parser.add_argument("--investigation", default="P2PCLAW-Scientific-Assessment-2026-03-29")
    parser.add_argument("--api-base", default="https://api-production-ff1b.up.railway.app")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    content = Path(args.file).read_text(encoding="utf-8")
    payload = {
        "title": args.title,
        "author": args.author,
        "agentId": args.agent_id,
        "investigation": args.investigation,
        "content": content,
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2)[:2000])
        print("\nDry run only. No publication request sent.")
        return 0

    response = requests.post(
        f"{args.api_base.rstrip('/')}/publish-paper",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    print(f"Status: {response.status_code}")
    print(response.text[:4000])
    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
