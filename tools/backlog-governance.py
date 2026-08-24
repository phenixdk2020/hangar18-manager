#!/usr/bin/env python3
"""Validate layered Hangar18 backlogs and build a machine-readable index."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from collections import Counter
from typing import Any

ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:[-.][A-Z0-9]+)*(?:[-.][0-9A-Z]+)*$")
ID_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:[-.][A-Z0-9]+)+\b")
HEADING_RE = re.compile(r"^#\s+([A-Z])\.\s+(.+?)\s*$")
EXTENDS_RE = re.compile(r"^\*\*Extends:\*\*\s+`?([^`\s]+)`?\s*$", re.I)
BLOCKED_BY_RE = re.compile(r"BLOKERET\s+AF\s+(.+)$", re.I)
EXPLICIT_DEP_RE = re.compile(r"(?:Dependencies|Depends\s+on|Afhænger\s+af)\s*:\s*([^.;|]+)", re.I)


def extract_dependencies(item_id: str, status: str, dod: str) -> list[str]:
    """Extract only explicitly declared backlog dependencies.

    Ordinary cross-references in DoD text are not dependencies. Dependencies are
    recognized from a `BLOKERET AF ...` status or an explicit
    `Dependencies:` / `Depends on:` / `Afhænger af:` marker.
    """
    candidates: list[str] = []
    blocked = BLOCKED_BY_RE.search(status)
    if blocked:
        candidates.extend(ID_TOKEN_RE.findall(blocked.group(1).upper()))
    for match in EXPLICIT_DEP_RE.finditer(dod):
        candidates.extend(ID_TOKEN_RE.findall(match.group(1).upper()))

    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate == item_id or not ID_RE.fullmatch(candidate) or candidate in seen:
            continue
        seen.add(candidate)
        result.append(candidate)
    return result


def parse_single(path: pathlib.Path) -> tuple[list[dict[str, Any]], str | None]:
    area_code = ""
    area = ""
    items: list[dict[str, Any]] = []
    extends: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        ext = EXTENDS_RE.match(stripped)
        if ext:
            extends = ext.group(1).strip()
            continue
        heading = HEADING_RE.match(stripped)
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
            "dependencies": extract_dependencies(item_id, status, dod),
            "definition_of_done": dod,
            "area_code": area_code,
            "area": area,
            "source_file": path.as_posix(),
        })
    return items, extends


def parse_backlog(path: pathlib.Path, seen: set[pathlib.Path] | None = None) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    seen = set() if seen is None else seen
    resolved = path.resolve()
    if resolved in seen:
        return [], [], [f"backlog extends cycle detected at {path}"]
    seen.add(resolved)

    current, extends = parse_single(path)
    errors: list[str] = []
    chain: list[str] = []
    counts = Counter(item["id"] for item in current)
    for item_id, count in sorted(counts.items()):
        if count > 1:
            errors.append(f"duplicate backlog id in {path}: {item_id} ({count} occurrences)")

    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    if extends:
        base = pathlib.Path(extends)
        if not base.is_absolute():
            # Extends values are repository-root relative by convention.
            base = pathlib.Path(extends)
        if not base.is_file():
            errors.append(f"extends target not found: {extends}")
        else:
            base_items, base_chain, base_errors = parse_backlog(base, seen)
            errors.extend(base_errors)
            chain.extend(base_chain)
            for item in base_items:
                merged[str(item["id"])] = item
                order.append(str(item["id"]))

    for item in current:
        item_id = str(item["id"])
        if item_id not in merged:
            order.append(item_id)
        merged[item_id] = item

    chain.append(path.as_posix())
    return [merged[item_id] for item_id in order], chain, errors


def validate(items: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    counts = Counter(str(item["id"]) for item in items)
    known_ids = set(counts)
    for item_id, count in sorted(counts.items()):
        if count > 1:
            errors.append(f"duplicate merged backlog id: {item_id} ({count} occurrences)")
    for item in items:
        item_id = str(item["id"])
        for key in ("priority", "status", "definition_of_done", "area"):
            if not item.get(key):
                errors.append(f"{item_id} missing {key}")
        if len(str(item.get("definition_of_done", ""))) < 12:
            errors.append(f"{item_id} Definition of done is too short")
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list):
            errors.append(f"{item_id} dependencies must be a list")
            continue
        for dependency in dependencies:
            if not isinstance(dependency, str) or not ID_RE.fullmatch(dependency):
                errors.append(f"{item_id} has invalid dependency: {dependency!r}")
            elif dependency not in known_ids:
                errors.append(f"{item_id} depends on unknown backlog id: {dependency}")
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

    items, chain, parse_errors = parse_backlog(backlog)
    errors = parse_errors + validate(items)
    if not items:
        errors.append("no backlog items parsed")

    payload = {
        "schema_version": "1.2",
        "canonical_backlog": backlog.as_posix(),
        "extends_chain": chain,
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
                existing_items = {item.get("id"): item for item in existing.get("items", [])}
                for item in items:
                    old = existing_items.get(item["id"])
                    if (
                        not old
                        or old.get("status") != item["status"]
                        or old.get("dependencies", []) != item["dependencies"]
                        or old.get("definition_of_done") != item["definition_of_done"]
                    ):
                        errors.append("backlog-index is stale; regenerate tools/backlog-governance.py")
                        break
            except Exception as exc:  # noqa: BLE001
                errors.append(f"cannot parse backlog-index: {exc}")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {output} with {len(items)} merged items from {len(chain)} backlog layer(s)")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Backlog QA PASS: {len(items)} unique merged items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
