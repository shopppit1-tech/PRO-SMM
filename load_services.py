#!/usr/bin/env python3
"""Load Peakerr services into data/services.json."""

import argparse
import json
import os
import sys

from peakerr_client import PeakerrAPIError, PeakerrClient, save_services


def main() -> int:
    parser = argparse.ArgumentParser(description="Load Peakerr service catalog")
    parser.add_argument(
        "--output",
        default="data/services.json",
        help="Output JSON path (default: data/services.json)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact category/count summary after loading",
    )
    args = parser.parse_args()

    try:
        client = PeakerrClient.from_environment()
        services = client.list_services()
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as file:
            json.dump(services, file, ensure_ascii=False, indent=2)
            file.write("\n")
    except (PeakerrAPIError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Loaded {len(services)} Peakerr services into {args.output}")
    if args.summary:
        categories = {}
        for service in services:
            category = str(service.get("category", "Uncategorized"))
            categories[category] = categories.get(category, 0) + 1
        for category, count in sorted(categories.items()):
            print(f"- {category}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
