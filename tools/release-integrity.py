#!/usr/bin/env python3
"""Hangar18 release integrity checks and release-manifest generation."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile

ALLOWED_CHANNELS = {"test", "staging", "production"}
DENY_PARTS = {
    ".git", ".github", "node_modules", "tests", "test", "tools", "docs",
    "build", ".idea", ".vscode", "__pycache__", ".pytest_cache",
}
DENY_SUFFIXES = {".ps1", ".log", ".tmp", ".bak", ".orig", ".patch", ".pyc"}
DENY_FILENAMES = {"release-config.json", "package.json", "package-lock.json", "composer.json", "composer.lock"}
VERSION_HEADER_RE = re.compile(r"(?m)^ \* Version: (\d+\.\d+\.\d+)\s*$")
VERSION_CONST_RE = re.compile(r"const VERSION = '(\d+\.\d+\.\d+)';")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def read_json(path: pathlib.Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def zip_version(zip_path: pathlib.Path) -> tuple[str, str]:
    with zipfile.ZipFile(zip_path) as archive:
        php = archive.read("hangar18-manager/hangar18-manager.php").decode("utf-8")
    header = VERSION_HEADER_RE.search(php)
    const = VERSION_CONST_RE.search(php)
    return (header.group(1) if header else "", const.group(1) if const else "")


def zip_tree_errors(zip_path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
    if not names:
        errors.append("ZIP is empty")
        return errors
    for name in names:
        p = pathlib.PurePosixPath(name)
        if not p.parts or p.parts[0] != "hangar18-manager":
            errors.append(f"ZIP entry outside plugin root: {name}")
            continue
        relative = p.parts[1:]
        if any(part in DENY_PARTS for part in relative):
            errors.append(f"denied directory in ZIP: {name}")
        if p.name in DENY_FILENAMES:
            errors.append(f"denied build/source file in ZIP: {name}")
        if p.suffix.lower() in DENY_SUFFIXES:
            errors.append(f"denied file type in ZIP: {name}")
        if "VehicleRegister" in p.name or "vehicle-register.json" in p.name.lower():
            errors.append(f"legacy bootstrap artifact in ZIP: {name}")
    return errors


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []
    version = str(config.get("version", "")).strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("release-config version is invalid")
    channel = str(config.get("channel", "")).strip()
    if channel not in ALLOWED_CHANNELS:
        errors.append(f"release-config channel must be one of {sorted(ALLOWED_CHANNELS)}")
    backlog_ids = config.get("backlog_ids")
    if not isinstance(backlog_ids, list) or not backlog_ids or any(not str(x).strip() for x in backlog_ids):
        errors.append("release-config backlog_ids must be a non-empty list")
    changelog = config.get("changelog")
    if not isinstance(changelog, list) or not changelog:
        errors.append("release-config changelog must be a non-empty list")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="release-config.json")
    parser.add_argument("--update", default="update.json")
    parser.add_argument("--zip", dest="zip_path", default="dist/hangar18-manager.zip")
    parser.add_argument("--manifest", default="release-manifest.json")
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()

    config_path = pathlib.Path(args.config)
    update_path = pathlib.Path(args.update)
    zip_path = pathlib.Path(args.zip_path)
    manifest_path = pathlib.Path(args.manifest)
    config = read_json(config_path)
    errors = validate_config(config)

    if not update_path.is_file():
        errors.append(f"missing update manifest: {update_path}")
        update = {}
    else:
        update = read_json(update_path)

    if not zip_path.is_file():
        errors.append(f"missing release ZIP: {zip_path}")
    else:
        errors.extend(zip_tree_errors(zip_path))

    version = str(config.get("version", "")).strip()
    update_version = str(update.get("version", "")).strip()
    if update_version and update_version != version:
        errors.append(f"update.json version {update_version} != release-config {version}")

    package_sha = ""
    header_version = ""
    const_version = ""
    if zip_path.is_file():
        package_sha = sha256(zip_path)
        header_version, const_version = zip_version(zip_path)
        if header_version != version:
            errors.append(f"ZIP plugin header version {header_version or '-'} != {version}")
        if const_version != version:
            errors.append(f"ZIP VERSION constant {const_version or '-'} != {version}")
        expected_sha = str(update.get("package_sha256", "")).strip().lower()
        if expected_sha and expected_sha != package_sha:
            errors.append("ZIP SHA-256 does not match update.json")

    backlog_ids = [str(x).strip() for x in config.get("backlog_ids", []) if str(x).strip()]
    channel = str(config.get("channel", "")).strip()
    manifest = {
        "schema_version": "1.0",
        "version": version,
        "channel": channel,
        "source_commit": git_head(),
        "built_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "package_path": zip_path.as_posix(),
        "package_sha256": package_sha,
        "plugin_header_version": header_version,
        "plugin_constant_version": const_version,
        "backlog_ids": backlog_ids,
        "qa": {
            "version_match": bool(version and version == update_version == header_version == const_version),
            "package_sha_match": bool(package_sha and package_sha == str(update.get("package_sha256", "")).strip().lower()),
            "zip_tree_policy": not any("ZIP" in e or "denied" in e or "legacy bootstrap" in e for e in errors),
        },
    }

    if args.write_manifest:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {manifest_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Release integrity PASS: v{version} channel={channel} backlog={','.join(backlog_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
