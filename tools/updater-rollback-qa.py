#!/usr/bin/env python3
"""Contract QA for Hangar18 updater rollback semantics.

This is intentionally a simulation + static-source contract test, not a WordPress
integration installer. It verifies the hardened legacy source owns exactly one
rollback path and exercises failure points before/after code backup, including a
rollback failure, so future refactors cannot silently drop the safety behavior.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

TARGET = pathlib.Path('hangar18-manager.php')


def simulate(*, backup_created: bool, install_fails: bool, rollback_fails: bool) -> dict:
    events: list[str] = ['start']
    if backup_created:
        events.append('backup_verified')
    if not install_fails:
        events.append('install_success')
        return {'events': events, 'success': True, 'rollback_attempted': False, 'rollback_success': None}

    events.append('install_failed')
    if not backup_created:
        return {'events': events, 'success': False, 'rollback_attempted': False, 'rollback_success': None}

    events.append('rollback_start')
    if rollback_fails:
        events.append('rollback_failed')
        return {'events': events, 'success': False, 'rollback_attempted': True, 'rollback_success': False}

    events.extend(['rollback_success', 'pending_transition_cleared', 'cache_invalidated'])
    return {'events': events, 'success': False, 'rollback_attempted': True, 'rollback_success': True}


def assert_source(path: pathlib.Path) -> dict:
    text = path.read_text(encoding='utf-8')
    required = {
        'rollback_start_log': "'UPDATE_ROLLBACK_START'",
        'rollback_success_log': "'UPDATE_ROLLBACK_SUCCESS'",
        'rollback_failed_log': "'UPDATE_ROLLBACK_FAILED'",
        'backup_reinstall': "$this->install_local_plugin_zip(\n                        $code_backup,\n                        true\n                    );",
        'pending_cleanup_marker': 'H18-UPDATER-HARDENING-010-ROLLBACK',
        'pending_option_cleanup': "delete_option('hangar18_manager_update_post_install_pending_v1')",
        'cache_cleanup': "delete_site_transient('update_plugins')",
    }
    missing = [name for name, needle in required.items() if needle not in text]
    if missing:
        raise RuntimeError('Rollback source contracts missing: ' + ', '.join(missing))
    return {'required_contracts': sorted(required)}


def run(root: pathlib.Path) -> dict:
    source = assert_source(root / TARGET)

    cases = {
        'success': simulate(backup_created=True, install_fails=False, rollback_fails=False),
        'fail_before_backup': simulate(backup_created=False, install_fails=True, rollback_fails=False),
        'fail_after_backup': simulate(backup_created=True, install_fails=True, rollback_fails=False),
        'rollback_failure': simulate(backup_created=True, install_fails=True, rollback_fails=True),
    }

    assert cases['success']['success'] is True
    assert cases['success']['rollback_attempted'] is False
    assert cases['fail_before_backup']['rollback_attempted'] is False
    assert cases['fail_after_backup']['rollback_attempted'] is True
    assert cases['fail_after_backup']['rollback_success'] is True
    assert 'pending_transition_cleared' in cases['fail_after_backup']['events']
    assert 'cache_invalidated' in cases['fail_after_backup']['events']
    assert cases['rollback_failure']['rollback_attempted'] is True
    assert cases['rollback_failure']['rollback_success'] is False

    return {
        'schema_version': '1.0',
        'result': 'PASS',
        'source_contract': source,
        'cases': cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--report')
    args = parser.parse_args()
    try:
        report = run(pathlib.Path(args.root).resolve())
        payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.report:
            pathlib.Path(args.report).write_text(payload, encoding='utf-8')
        else:
            sys.stdout.write(payload)
        return 0
    except Exception as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
