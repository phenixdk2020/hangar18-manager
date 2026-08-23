#!/usr/bin/env python3
"""Validate the canonical Hangar18 backlog and build a machine-readable index."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from collections import Counter

ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:[-.][A-Z0-9]+)*(?:[-.][0-9A-Z]+)*$")
HEADING_RE = re.compile(r"^#\s+([A-Z])\.\s+(.+?)\s*$")


def parse_backlog(path: pathlib.Path) -> list[dict[str, str]]:
    area_code = ""
    area = ""
    items: list[dict[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.match(raw.strip())
        if heading:
            area_code, area = heading.groups()
            continue
        match = ROW_RE.match(raw)
        if not match:
            continue
        item_id, priority, status, dod = [part.strip() for part in match.groups()]
        if item_id in {"ID", "---"} or item_id.startswith("---"):
            continue
        if not ID_RE.fullmatch(item_id):
            continue
        items.append({
            "id": item_id,
            "priority": priority,
            "status": status,
            "definition_of_done": dod,
            "area_code": area_code,
            "area": area,
        })
    return items


def validate(items: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    counts = Counter(item["id"] for item in items)
    for item_id, count in sorted(counts.items()):
        if count > 1:
            errors.append(f"duplicate backlog id: {item_id} ({count} occurrences)")
    for item in items:
        for key in ("priority", "status", "definition_of_done", "area"):
            if not item[key]:
                errors.append(f"{item['id']} missing {key}")
        if len(item["definition_of_done"]) < 12:
            errors.append(f"{item['id']} Definition of done is too short")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backlog", default="docs/active-backlog-v0878.md")
    parser.add_argument("--output", default="docs/backlog-index.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    backlog = pathlib.Path(args.backlog)
    output = pathlib.Path(args.output)
    if not backlog.is_file():
        print(f"ERROR: canonical backlog not found: {backlog}", file=sys.stderr)
        return 2

    items = parse_backlog(backlog)
    errors = validate(items)
    if not items:
        errors.append("no backlog items parsed")

    payload = {
        "schema_version": "1.0",
        "canonical_backlog": backlog.as_posix(),
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "item_count": len(items),
        "items": items,
    }

    if args.check:
        if not output.is_file():
            errors.append(f"index missing: {output}")
        else:
            try:
                existing = json.loads(output.read_text(encoding="utf-8"))
                if existing.get("canonical_backlog") != payload["canonical_backlog"]:
                    errors.append("backlog-index points at wrong canonical backlog")
                existing_ids = [item.get("id") for item in existing.get("items", [])]
                current_ids = [item["id"] for item in items]
                if existing_ids != current_ids:
                    errors.append("backlog-index is stale; regenerate tools/backlog-governance.py")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"cannot parse backlog-index: {exc}")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {output} with {len(items)} items")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Backlog QA PASS: {len(items)} unique items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
