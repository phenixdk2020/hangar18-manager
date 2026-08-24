#!/usr/bin/env python3
"""Static/logic QA matrix for the Hangar18 updater contract.

This deliberately tests the compatibility boundary that installable legacy
versions depend on. It does not access GitHub or WordPress and is safe in CI.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEGACY_UPDATER = ROOT / 'hangar18-manager.php'
RELEASE_WORKFLOW = ROOT / '.github/workflows/build-plugin-release.yml'
UPDATE_JSON = ROOT / 'update.json'

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')


def version_tuple(value: str) -> tuple[int, int, int]:
    if not SEMVER_RE.fullmatch(value):
        raise ValueError(f'invalid semver: {value!r}')
    return tuple(int(part) for part in value.split('.'))  # type: ignore[return-value]


def update_available(installed: str, latest: str) -> bool:
    return version_tuple(installed) < version_tuple(latest)


def legacy_manifest_valid(manifest: object) -> bool:
    if not isinstance(manifest, dict):
        return False
    if str(manifest.get('schema_version', '')).strip() != '1.0':
        return False
    if str(manifest.get('plugin', '')).strip() != 'hangar18-manager':
        return False
    version = str(manifest.get('version', '')).strip()
    if not SEMVER_RE.fullmatch(version):
        return False
    sha = str(manifest.get('package_sha256', '')).strip().lower()
    if sha and not SHA_RE.fullmatch(sha):
        return False
    return True


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []

    # Core availability truth table.
    cases = [
        ('0.8.79', '0.8.80', True, 'behind => JA'),
        ('0.8.80', '0.8.80', False, 'equal => NEJ'),
        ('0.8.81', '0.8.80', False, 'ahead => NEJ'),
        ('1.0.0', '1.0.1', True, 'patch behind'),
        ('1.1.0', '1.0.99', False, 'minor ahead'),
    ]
    for installed, latest, expected, label in cases:
        require(update_available(installed, latest) is expected, f'{label} failed', errors)

    valid = {
        'schema_version': '1.0',
        'plugin': 'hangar18-manager',
        'version': '0.8.81',
        'package_sha256': 'a' * 64,
    }
    require(legacy_manifest_valid(valid), 'valid legacy manifest rejected', errors)

    invalid_cases = [
        ({**valid, 'schema_version': '1.1'}, 'unknown schema must be rejected by legacy updater'),
        ({**valid, 'version': ''}, 'missing version must be rejected'),
        ({**valid, 'version': '0.8'}, 'invalid version must be rejected'),
        ({**valid, 'plugin': 'other-plugin'}, 'wrong plugin id must be rejected'),
        ({**valid, 'package_sha256': 'bad-sha'}, 'bad SHA shape must be rejected'),
        ([], 'non-object manifest must be rejected'),
    ]
    for manifest, label in invalid_cases:
        require(not legacy_manifest_valid(manifest), label, errors)

    legacy_php = LEGACY_UPDATER.read_text(encoding='utf-8')
    workflow = RELEASE_WORKFLOW.read_text(encoding='utf-8')
    update = json.loads(UPDATE_JSON.read_text(encoding='utf-8'))

    require("if ($schema !== '1.0')" in legacy_php, 'legacy updater schema guard is no longer explicit 1.0', errors)
    require("'schema_version': '1.0'" in workflow, 'release workflow is not generating schema 1.0', errors)
    require('test "$(php -r' in workflow and 'schema_version' in workflow, 'release workflow lacks schema verification', errors)
    require(str(update.get('schema_version', '')) == '1.0', 'current update.json is not schema 1.0', errors)
    require(str(update.get('plugin', '')) == 'hangar18-manager', 'current update.json plugin id mismatch', errors)
    require(bool(SEMVER_RE.fullmatch(str(update.get('version', '')))), 'current update.json version invalid', errors)
    require(bool(SHA_RE.fullmatch(str(update.get('package_sha256', '')).lower())), 'current update.json SHA invalid', errors)

    # Atomic state implementation must compare latest against current, never a cached boolean.
    consistency = (ROOT / 'src/Admin/UpdaterStateConsistencyAdminController.php').read_text(encoding='utf-8')
    require(
        "version_compare($latestVersion, $currentVersion, '>')" in consistency,
        'atomic updater state no longer recomputes availability from latest/current',
        errors,
    )

    if errors:
        for error in errors:
            print('ERROR: ' + error, file=sys.stderr)
        return 1

    print('Updater contract QA PASS: behind/equal/ahead + schema/plugin/version/SHA + atomic state')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
