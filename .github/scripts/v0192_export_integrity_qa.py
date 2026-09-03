from pathlib import Path
import json,re

ROOT=Path('.')
plugin=(ROOT/'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
export=(ROOT/'clean/hangar18-manager/src/Admin/ExportController.php').read_text(encoding='utf-8')
transfer=(ROOT/'clean/hangar18-manager/src/Admin/PortableTransferController.php').read_text(encoding='utf-8')
history=json.loads((ROOT/'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
notes=(ROOT/'clean-release-notes.html').read_text(encoding='utf-8')

m=re.search(r"define\('VDM_VERSION',\s*'([^']+)'\);",plugin)
assert m and tuple(map(int,m.group(1).split('.'))) >= (0,1,92)
assert 'self::inspectPackage($targetPath, true)' in transfer
assert 'public static function verifyPortablePackage(string $path): array' in transfer
assert "'verification' => $verification" in transfer
assert "self::addJson($zip, 'export-summary.json'" in export
assert "self::addText($zip, 'README.txt'" in export
assert "'archivePath' => $portableArchivePath" in export
assert 'private static function verifyExportPackage(string $path, string $kind): array' in export
assert "self::verifyExportPackage($tmp, $kind)" in export
assert 'visual-designer-export.json' in export
assert "hash_equals($expectedDigest, $actualDigest)" in export
assert "hash_equals($expectedHash, $actualHash)" in export
assert "(int) ($stat['size'] ?? -1) !== $expectedSize" in export
assert "PortableTransferController::verifyPortablePackage($nestedTmp)" in export
assert "self::copyZipEntryToFile($zip, $nestedPath, $nestedTmp)" in export
assert "hash_equals($expectedNestedHash, $actualNestedHash)" in export
assert "header('X-Visual-Designer-Verified: sha256')" in export
assert 'begge ZIP-lag før download' in export
assert any(str(row.get('version'))=='0.1.92' for row in history.get('versions',[]))
assert 'data-version="0.1.92"' in notes
assert (ROOT/'docs/v0192-status.md').is_file()
print('v0.1.92 export integrity QA: PASS on runtime '+m.group(1))
