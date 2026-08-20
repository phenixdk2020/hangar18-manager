#!/usr/bin/env bash
set -euo pipefail

BUILD='src/Backup/SiteBackupManifestService.php'
VALIDATE='src/Backup/SiteBackupManifestValidator.php'

for file in "$BUILD" "$VALIDATE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

grep -E "public const SCHEMA_VERSION[[:space:]]*=[[:space:]]*'1\.0';" "$BUILD" >/dev/null
grep -F "H18-BACKUP-(\\d{6})" "$BUILD" >/dev/null
grep -F "ManifestSha256" "$BUILD" >/dev/null
grep -F "IdentitySha256" "$BUILD" >/dev/null
grep -F "hash('sha256'" "$BUILD" >/dev/null
grep -E "'FullRestore'[[:space:]]*=>[[:space:]]*false" "$BUILD" >/dev/null
grep -E "'SelectiveRestore'[[:space:]]*=>[[:space:]]*false" "$BUILD" >/dev/null
grep -E "'ZipExport'[[:space:]]*=>[[:space:]]*false" "$BUILD" >/dev/null
grep -E "'DryRunValidation'[[:space:]]*=>[[:space:]]*true" "$BUILD" >/dev/null
grep -E "'DryRunOnly'[[:space:]]*=>[[:space:]]*true" "$VALIDATE" >/dev/null

# B2-A remains the pure manifest/checksum foundation even though higher B2 layers now persist packages and restore them.
if grep -Ei 'update_option\s*\(|add_option\s*\(|delete_option\s*\(|wp_update_post\s*\(|wp_insert_post\s*\(|update_post_meta\s*\(|file_put_contents\s*\(|fopen\s*\(|ZipArchive|unlink\s*\(|rename\s*\(|copy\s*\(|admin_post_|wp_ajax_' "$BUILD" "$VALIDATE" >/dev/null; then
  echo 'FAIL: B2-A pure manifest/validator foundation introduced persistence, ZIP or restore mutation'
  exit 1
fi

echo 'B2-A pure manifest/dry-run foundation contract: PASS'
