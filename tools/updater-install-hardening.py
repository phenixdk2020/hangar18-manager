#!/usr/bin/env python3
"""Deterministically harden the legacy Hangar18 updater before release packaging.

The legacy Hangar18_Manager remains the installation owner. This source migration
adds only missing safety contracts around the existing transaction:
- verify the code-backup ZIP can be reopened and contains the current plugin;
- verify the downloaded package SHA again from the actual on-disk ZIP;
- verify both plugin header and VERSION constant in the installed source;
- write a short-lived pending transition for next-request runtime verification;
- invalidate updater/plugin caches as one post-install operation;
- verify rollback restores the previous version and persist restored main-file SHA;
- clear pending transition after successful verified rollback.

The migration is fail-closed and idempotent. It is intended to run after the
WhatIf source cleanup and before syntax/package QA.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

TARGET = pathlib.Path('hangar18-manager.php')
MARKER_BACKUP = 'H18-UPDATER-HARDENING-009'
MARKER_PACKAGE = 'H18-UPDATER-HARDENING-008'
MARKER_INSTALL = 'H18-UPDATER-HARDENING-006-007'
MARKER_ROLLBACK = 'H18-UPDATER-HARDENING-010-ROLLBACK'


def insert_before_once(text: str, anchor: str, insertion: str, marker: str) -> tuple[str, bool]:
    if marker in text:
        return text, False
    count = text.count(anchor)
    if count != 1:
        raise RuntimeError(f'Expected exactly one anchor for {marker}, got {count}')
    return text.replace(anchor, insertion + anchor, 1), True


def apply(path: pathlib.Path) -> dict:
    text = path.read_text(encoding='utf-8')
    changed: list[str] = []

    backup_anchor = "        $this->log(\n            'INFO',\n            'UPDATE_CODE_BACKUP_SUCCESS',"
    backup_insertion = r'''        // H18-UPDATER-HARDENING-009: verify backup contents before any plugin mutation.
        $verify_backup = new ZipArchive();
        if ($verify_backup->open($file) !== true) {
            throw new RuntimeException('Plugin-kodebackup kunne ikke genåbnes til verifikation.');
        }
        $backup_main = $verify_backup->getFromName('hangar18-manager/hangar18-manager.php');
        $verify_backup->close();
        $backup_expected = preg_quote(self::VERSION, '/');
        if (
            $backup_main === false ||
            !preg_match('/\*\s+Version:\s*' . $backup_expected . '\s*$/m', $backup_main) ||
            !preg_match("/const\\s+VERSION\\s*=\\s*'" . $backup_expected . "';/", $backup_main)
        ) {
            throw new RuntimeException('Plugin-kodebackup indeholder ikke den forventede aktive version.');
        }
        $backup_sha256 = strtolower((string) hash_file('sha256', $file));
        if (!preg_match('/^[a-f0-9]{64}$/', $backup_sha256)) {
            throw new RuntimeException('SHA-256 af plugin-kodebackup kunne ikke beregnes.');
        }
        $this->log(
            'INFO',
            'UPDATE_CODE_BACKUP_VERIFIED',
            'Plugin-kodebackup verificeret. SHA256=' . $backup_sha256 . '.'
        );

'''
    text, did = insert_before_once(text, backup_anchor, backup_insertion, MARKER_BACKUP)
    if did:
        changed.append('code_backup_zip_verified')

    package_anchor = "        $this->log(\n            'INFO',\n            'UPDATE_PACKAGE_VERIFIED',"
    package_insertion = r'''        // H18-UPDATER-HARDENING-008: verify the actual persisted ZIP, not only downloaded bytes.
        $disk_sha256 = strtolower((string) hash_file('sha256', $file));
        if (
            !preg_match('/^[a-f0-9]{64}$/', $disk_sha256) ||
            !hash_equals(strtolower((string) $manifest['package_sha256']), $disk_sha256)
        ) {
            @unlink($file);
            throw new RuntimeException('SHA-256-validering af den gemte update-ZIP fejlede.');
        }

'''
    text, did = insert_before_once(text, package_anchor, package_insertion, MARKER_PACKAGE)
    if did:
        changed.append('persisted_package_sha_verified')

    install_anchor = "            $this->log(\n                'INFO',\n                'UPDATE_SUCCESS',"
    install_insertion = r'''            // H18-UPDATER-HARDENING-006-007: verify installed source and hand off to next-request runtime verification.
            if (!preg_match(
                "/const\\s+VERSION\\s*=\\s*'" . $expected . "';/",
                $installed_source
            )) {
                throw new RuntimeException(
                    'Den installerede Hangar18_Manager::VERSION-kilde har ikke forventet version ' .
                    (string) $manifest['version'] . '.'
                );
            }

            $installed_main_sha256 = strtolower((string) hash_file('sha256', $installed_file));
            if (!preg_match('/^[a-f0-9]{64}$/', $installed_main_sha256)) {
                throw new RuntimeException('SHA-256 af installeret plugin-hovedfil kunne ikke beregnes.');
            }

            update_option(
                'hangar18_manager_update_post_install_pending_v1',
                [
                    'from_version' => self::VERSION,
                    'expected_version' => (string) $manifest['version'],
                    'package_sha256' => strtolower((string) $manifest['package_sha256']),
                    'installed_main_sha256' => $installed_main_sha256,
                    'code_backup_sha256' => ($code_backup && is_file($code_backup))
                        ? strtolower((string) hash_file('sha256', $code_backup))
                        : '',
                    'created_at_utc' => gmdate('c'),
                ],
                false
            );

            // Clear all updater/plugin cache state in one post-install operation.
            delete_option(self::UPDATE_STATE_OPTION);
            if (function_exists('delete_site_transient')) {
                delete_site_transient('update_plugins');
            }
            if (function_exists('wp_clean_plugins_cache')) {
                wp_clean_plugins_cache(true);
            }

'''
    text, did = insert_before_once(text, install_anchor, install_insertion, MARKER_INSTALL)
    if did:
        changed.append('installed_source_and_cache_handoff')

    rollback_anchor = "                    $this->log(\n                        'INFO',\n                        'UPDATE_ROLLBACK_SUCCESS',\n                        'Plugin-kode blev rullet tilbage til backup.'\n                    );"
    rollback_insertion = r'''                    // H18-UPDATER-HARDENING-010-ROLLBACK: verify the restored source and persist rollback evidence.
                    $rollback_main_file = WP_PLUGIN_DIR . '/hangar18-manager/hangar18-manager.php';
                    if (!is_file($rollback_main_file) || !is_readable($rollback_main_file)) {
                        throw new RuntimeException('Rollback gendannede ikke en læsbar plugin-hovedfil.');
                    }
                    $rollback_source = file_get_contents($rollback_main_file);
                    if ($rollback_source === false) {
                        throw new RuntimeException('Rollback-hovedfilen kunne ikke læses til verifikation.');
                    }
                    $rollback_expected = preg_quote(self::VERSION, '/');
                    if (
                        !preg_match('/\*\s+Version:\s*' . $rollback_expected . '\s*$/m', $rollback_source) ||
                        !preg_match("/const\\s+VERSION\\s*=\\s*'" . $rollback_expected . "';/", $rollback_source)
                    ) {
                        throw new RuntimeException(
                            'Rollback gendannede ikke den forventede version ' . self::VERSION . '.'
                        );
                    }
                    $rollback_main_sha256 = strtolower((string) hash_file('sha256', $rollback_main_file));
                    if (!preg_match('/^[a-f0-9]{64}$/', $rollback_main_sha256)) {
                        throw new RuntimeException('SHA-256 af gendannet plugin-hovedfil kunne ikke beregnes.');
                    }
                    $rollback_audit = [
                        'schema_version' => '1.0',
                        'from_version' => (string) ($manifest['version'] ?? ''),
                        'to_version' => self::VERSION,
                        'restored_main_sha256' => $rollback_main_sha256,
                        'code_backup_sha256' => ($code_backup && is_file($code_backup))
                            ? strtolower((string) hash_file('sha256', $code_backup))
                            : '',
                        'verified_at_utc' => gmdate('c'),
                    ];
                    update_option(
                        'hangar18_manager_update_rollback_verification_v1',
                        $rollback_audit,
                        false
                    );
                    $this->log(
                        'INFO',
                        'UPDATE_ROLLBACK_VERIFIED',
                        'Rollback verificeret: FromVersion=' . $rollback_audit['from_version'] .
                        '; ToVersion=' . $rollback_audit['to_version'] .
                        '; RestoredMainSHA256=' . $rollback_main_sha256 . '.'
                    );

                    // A rolled-back install must not leave a pending success transition or stale updater cache.
                    delete_option('hangar18_manager_update_post_install_pending_v1');
                    delete_option(self::UPDATE_STATE_OPTION);
                    if (function_exists('delete_site_transient')) {
                        delete_site_transient('update_plugins');
                    }
                    if (function_exists('wp_clean_plugins_cache')) {
                        wp_clean_plugins_cache(true);
                    }

'''
    text, did = insert_before_once(text, rollback_anchor, rollback_insertion, MARKER_ROLLBACK)
    if did:
        changed.append('rollback_version_sha_verification')

    path.write_text(text, encoding='utf-8')
    return {
        'schema_version': '1.1',
        'target': path.as_posix(),
        'changed': changed,
        'already_hardened': not changed,
        'markers': [MARKER_BACKUP, MARKER_PACKAGE, MARKER_INSTALL, MARKER_ROLLBACK],
    }


def assert_hardened(path: pathlib.Path) -> dict:
    text = path.read_text(encoding='utf-8')
    missing = [m for m in [MARKER_BACKUP, MARKER_PACKAGE, MARKER_INSTALL, MARKER_ROLLBACK] if m not in text]
    if missing:
        raise RuntimeError('Updater hardening markers missing: ' + ', '.join(missing))
    required = [
        'UPDATE_CODE_BACKUP_VERIFIED',
        "hash_file('sha256', $file)",
        'hangar18_manager_update_post_install_pending_v1',
        "delete_site_transient('update_plugins')",
        'wp_clean_plugins_cache(true)',
        'UPDATE_ROLLBACK_VERIFIED',
        'hangar18_manager_update_rollback_verification_v1',
        'restored_main_sha256',
        "'from_version' => (string) ($manifest['version'] ?? '')",
        "'to_version' => self::VERSION",
    ]
    absent = [value for value in required if value not in text]
    if absent:
        raise RuntimeError('Updater hardening contracts missing: ' + ', '.join(absent))
    return {'schema_version': '1.1', 'target': path.as_posix(), 'hardened': True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--assert-hardened', action='store_true')
    parser.add_argument('--report')
    args = parser.parse_args()
    target = pathlib.Path(args.root).resolve() / TARGET

    try:
        if args.apply:
            report = apply(target)
        elif args.assert_hardened:
            report = assert_hardened(target)
        else:
            raise RuntimeError('Use --apply or --assert-hardened')
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
