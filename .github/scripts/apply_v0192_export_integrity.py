from pathlib import Path
import json

ROOT=Path('.')
PLUGIN=ROOT/'clean/hangar18-manager/hangar18-manager.php'
EXPORT=ROOT/'clean/hangar18-manager/src/Admin/ExportController.php'
TRANSFER=ROOT/'clean/hangar18-manager/src/Admin/PortableTransferController.php'
HISTORY=ROOT/'clean/hangar18-manager/release-history.json'
NOTES=ROOT/'clean-release-notes.html'
STATUS=ROOT/'docs/v0192-status.md'


def read(p): return p.read_text(encoding='utf-8')
def write(p,s): p.write_text(s,encoding='utf-8')
def rep(text,old,new,label):
    if old not in text: raise SystemExit('Missing marker: '+label)
    return text.replace(old,new,1)

plugin=read(PLUGIN)
plugin=rep(plugin,'Version: 0.1.91','Version: 0.1.92','plugin header')
plugin=rep(plugin,"define('VDM_VERSION', '0.1.91');","define('VDM_VERSION', '0.1.92');",'VDM_VERSION')
plugin=rep(plugin,"define('H18_CLEAN_VERSION', '0.1.91');","define('H18_CLEAN_VERSION', '0.1.92');",'compat version')
write(PLUGIN,plugin)

# Portable site packages now self-verify after build and expose a reusable verifier.
transfer=read(TRANSFER)
old="""        $sha = hash_file('sha256', $targetPath);
        if (!is_string($sha) || $sha === '') {
            @unlink($targetPath);
            throw new \\RuntimeException('SHA-256 kunne ikke beregnes for den portable sitepakke.');
        }

        return [
            'sha256' => $sha,
            'filename' => self::downloadName(),
            'counts' => $counts,
        ];
    }

    public static function preflightImport(): void
"""
new="""        $sha = hash_file('sha256', $targetPath);
        if (!is_string($sha) || $sha === '') {
            @unlink($targetPath);
            throw new \\RuntimeException('SHA-256 kunne ikke beregnes for den portable sitepakke.');
        }

        // v0.1.92: every newly built portable package passes the same full
        // schema/path/hash inspection that is used before import.
        $verification = self::inspectPackage($targetPath, true);

        return [
            'sha256' => $sha,
            'filename' => self::downloadName(),
            'counts' => $counts,
            'verification' => $verification,
        ];
    }

    /** @return array<string,mixed> */
    public static function verifyPortablePackage(string $path): array
    {
        if ($path === '' || !is_file($path)) {
            throw new \\RuntimeException('Den portable sitepakke findes ikke.');
        }
        return self::inspectPackage($path, true);
    }

    public static function preflightImport(): void
"""
transfer=rep(transfer,old,new,'portable self verification')
write(TRANSFER,transfer)

export=read(EXPORT)
export=rep(export,
"""        echo '<p class=\"h18-manager-description\">Eksportér hele installationens VDM-indhold eller vælg enkelte dele. <strong>Eksporter alt</strong> samler plugin, aktivt tema og en komplet portabel sitepakke i én ZIP.</p>';
""",
"""        echo '<p class=\"h18-manager-description\">Eksportér hele installationens VDM-indhold eller vælg enkelte dele. <strong>Eksporter alt</strong> samler plugin, aktivt tema og en komplet portabel sitepakke i én ZIP og verificerer begge ZIP-lag før download.</p>';
""",'export description')
export=rep(export,
"""        echo '<li>Hver pakke indeholder <code>visual-designer-export.json</code> med filmanifest, content-digest og SHA-256 pr. fil.</li>';
        echo '<li>Den færdige ZIPs SHA-256 sendes desuden i HTTP-headeren <code>X-Visual-Designer-SHA256</code>.</li>';
""",
"""        echo '<li>Hver pakke indeholder <code>visual-designer-export.json</code> med filmanifest, content-digest og SHA-256 pr. fil.</li>';
        echo '<li><strong>Eksporter alt</strong> indeholder desuden <code>export-summary.json</code> og <code>README.txt</code> med indhold, antal og præcis sti til den portable recovery-ZIP.</li>';
        echo '<li>Efter ZIP-oprettelsen genåbnes pakken og alle manifest-filer SHA-256-verificeres. Ved <strong>Eksporter alt</strong> verificeres den indlejrede portable ZIP også med den fulde import-preflight.</li>';
        echo '<li>Den færdige ZIPs SHA-256 sendes desuden i HTTP-headeren <code>X-Visual-Designer-SHA256</code>, og <code>X-Visual-Designer-Verified: sha256</code> markerer bestået serverkontrol.</li>';
""",'integrity UI')

old_all="""                    $portable = PortableTransferController::buildPortablePackage($portableTmp);
                    self::addFile($zip, $portableTmp, 'portable-site/' . sanitize_file_name((string) $portable['filename']), $files);
                    $portableCounts = isset($portable['counts']) && is_array($portable['counts']) ? $portable['counts'] : [];
                    $recordCount += array_sum(array_map('intval', $portableCounts));
                    self::addJson($zip, 'all.json', [
                        'schemaVersion' => self::SCHEMA,
                        'type' => 'all',
                        'portableSite' => [
                            'filename' => (string) $portable['filename'],
                            'sha256' => (string) $portable['sha256'],
                            'counts' => $portableCounts,
                        ],
                        'includes' => ['plugin', 'active-theme', 'parent-theme-when-used', 'portable-site'],
                    ], $files);
                    break;
"""
new_all="""                    $portable = PortableTransferController::buildPortablePackage($portableTmp);
                    $portableFilename = sanitize_file_name((string) $portable['filename']);
                    $portableArchivePath = 'portable-site/' . $portableFilename;
                    self::addFile($zip, $portableTmp, $portableArchivePath, $files);
                    $portableCounts = isset($portable['counts']) && is_array($portable['counts']) ? $portable['counts'] : [];
                    $portableVerification = isset($portable['verification']) && is_array($portable['verification']) ? $portable['verification'] : [];
                    $recordCount += array_sum(array_map('intval', $portableCounts));
                    $includes = ['plugin', 'active-theme', 'parent-theme-when-used', 'portable-site'];
                    self::addJson($zip, 'all.json', [
                        'schemaVersion' => self::SCHEMA,
                        'type' => 'all',
                        'portableSite' => [
                            'filename' => $portableFilename,
                            'archivePath' => $portableArchivePath,
                            'sha256' => (string) $portable['sha256'],
                            'counts' => $portableCounts,
                            'verifiedSchema' => (string) ($portableVerification['schemaVersion'] ?? ''),
                        ],
                        'includes' => $includes,
                    ], $files);
                    self::addJson($zip, 'export-summary.json', [
                        'format' => 'Visual Designer Manager Complete Export',
                        'schemaVersion' => self::SCHEMA,
                        'managerVersion' => VDM_VERSION,
                        'createdUtc' => gmdate('c'),
                        'site' => [
                            'name' => (string) get_bloginfo('name'),
                            'url' => home_url('/'),
                        ],
                        'includes' => $includes,
                        'portableSite' => [
                            'archivePath' => $portableArchivePath,
                            'filename' => $portableFilename,
                            'sha256' => (string) $portable['sha256'],
                            'counts' => $portableCounts,
                            'schemaVersion' => (string) ($portableVerification['schemaVersion'] ?? ''),
                            'managerVersion' => (string) ($portableVerification['managerVersion'] ?? VDM_VERSION),
                        ],
                        'restoreHint' => 'Ved VDM recovery/import bruges ZIP-filen under portable-site/. Den ydre ZIP er et komplet arkiv og skal ikke uploades direkte til VDM-importen.',
                    ], $files);
                    $readme = "Visual Designer Manager - komplet eksport\\n"
                        . "==========================================\\n\\n"
                        . "Site: " . (string) get_bloginfo('name') . "\\n"
                        . "URL: " . home_url('/') . "\\n"
                        . "VDM-version: " . VDM_VERSION . "\\n"
                        . "Oprettet UTC: " . gmdate('c') . "\\n\\n"
                        . "Denne ZIP indeholder plugin, aktivt tema/parent-theme og en portabel VDM-sitepakke.\\n"
                        . "Recovery/import-fil: " . $portableArchivePath . "\\n"
                        . "Recovery SHA-256: " . (string) $portable['sha256'] . "\\n\\n"
                        . "Brug den indlejrede ZIP under portable-site/ ved VDM recovery/import.\\n"
                        . "Alle filer i den ydre ZIP og den indlejrede portable ZIP verificeres før download.\\n";
                    self::addText($zip, 'README.txt', $readme, $files);
                    break;
"""
export=rep(export,old_all,new_all,'Export All summary/readme')

# Verify closed output before any bytes are sent to the browser.
old_post="""        if (is_string($portableTmp) && $portableTmp !== '') { @unlink($portableTmp); }

        if (!is_file($tmp) || filesize($tmp) === 0) {
            @unlink($tmp);
            wp_die(esc_html__('Exportpakken blev ikke oprettet korrekt.', 'visual-designer-manager'));
        }

        $filename = self::downloadName($kind);
"""
new_post="""        if (is_string($portableTmp) && $portableTmp !== '') { @unlink($portableTmp); }

        if (!is_file($tmp) || filesize($tmp) === 0) {
            @unlink($tmp);
            wp_die(esc_html__('Exportpakken blev ikke oprettet korrekt.', 'visual-designer-manager'));
        }

        try {
            self::verifyExportPackage($tmp, $kind);
        } catch (\\Throwable $error) {
            @unlink($tmp);
            wp_die(esc_html('Eksportens integritetskontrol fejlede: ' . $error->getMessage()));
        }

        $filename = self::downloadName($kind);
"""
export=rep(export,old_post,new_post,'post-build verification')
export=rep(export,
"""        if (is_string($packageSha) && $packageSha !== '') {
            header('X-Visual-Designer-SHA256: ' . $packageSha);
        }

        readfile($tmp);
""",
"""        if (is_string($packageSha) && $packageSha !== '') {
            header('X-Visual-Designer-SHA256: ' . $packageSha);
        }
        header('X-Visual-Designer-Verified: sha256');

        readfile($tmp);
""",'verified header')

# Add reusable text writer and robust outer/nested verification helpers before addFile().
marker="""    /** @param array<int,array<string,mixed>> $files */
    private static function addFile(\\ZipArchive $zip, string $source, string $archivePath, array &$files): void
"""
helpers=r'''    /** @param array<int,array<string,mixed>> $files */
    private static function addText(\ZipArchive $zip, string $archivePath, string $payload, array &$files): void
    {
        if (!self::safeArchivePath($archivePath) || !$zip->addFromString($archivePath, $payload)) {
            throw new \RuntimeException('Tekstfilen kunne ikke tilføjes: ' . $archivePath);
        }
        $files[] = [
            'path' => $archivePath,
            'size' => strlen($payload),
            'sha256' => hash('sha256', $payload),
        ];
    }

    /** @return array<string,mixed> */
    private static function verifyExportPackage(string $path, string $kind): array
    {
        if ($path === '' || !is_file($path)) {
            throw new \RuntimeException('Eksportpakken findes ikke.');
        }
        $zip = new \ZipArchive();
        $opened = $zip->open($path, \ZipArchive::RDONLY);
        if ($opened !== true) {
            throw new \RuntimeException('Eksportpakken kan ikke genåbnes til kontrol.');
        }
        $nestedTmp = null;
        try {
            $manifest = self::readZipJson($zip, 'visual-designer-export.json');
            if ((int) ($manifest['schemaVersion'] ?? 0) !== self::SCHEMA || (string) ($manifest['exportType'] ?? '') !== $kind) {
                throw new \RuntimeException('Eksportmanifestets type/schema matcher ikke pakken.');
            }
            $manifestFiles = isset($manifest['files']) && is_array($manifest['files']) ? array_values($manifest['files']) : [];
            $sortedFiles = $manifestFiles;
            usort($sortedFiles, static fn(array $a, array $b): int => strcmp((string) ($a['path'] ?? ''), (string) ($b['path'] ?? '')));
            $digestJson = wp_json_encode($sortedFiles, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            $actualDigest = is_string($digestJson) ? hash('sha256', $digestJson) : '';
            $expectedDigest = strtolower((string) ($manifest['contentSha256'] ?? ''));
            if ($expectedDigest === '' || !hash_equals($expectedDigest, $actualDigest)) {
                throw new \RuntimeException('Eksportmanifestets content SHA-256 matcher ikke.');
            }
            foreach ($manifestFiles as $file) {
                if (!is_array($file)) {
                    throw new \RuntimeException('Ugyldig filpost i eksportmanifestet.');
                }
                $entry = (string) ($file['path'] ?? '');
                $expectedHash = strtolower((string) ($file['sha256'] ?? ''));
                $expectedSize = max(0, (int) ($file['size'] ?? 0));
                if (!self::safeArchivePath($entry) || !preg_match('/^[a-f0-9]{64}$/', $expectedHash)) {
                    throw new \RuntimeException('Ugyldig filsignatur i eksportmanifestet.');
                }
                $stat = $zip->statName($entry);
                if (!is_array($stat)) {
                    throw new \RuntimeException('Manifestfil mangler i ZIP: ' . $entry);
                }
                if ((int) ($stat['size'] ?? -1) !== $expectedSize) {
                    throw new \RuntimeException('Filstørrelsen matcher ikke for ' . $entry . '.');
                }
                $actualHash = self::hashZipEntry($zip, $entry);
                if (!hash_equals($expectedHash, $actualHash)) {
                    throw new \RuntimeException('SHA-256 matcher ikke for ' . $entry . '.');
                }
            }

            $result = [
                'verified' => true,
                'fileCount' => count($manifestFiles),
                'contentSha256' => $actualDigest,
            ];
            if ($kind === 'all') {
                $all = self::readZipJson($zip, 'all.json');
                $summary = self::readZipJson($zip, 'export-summary.json');
                if ($zip->locateName('README.txt') === false) {
                    throw new \RuntimeException('README.txt mangler i komplet eksport.');
                }
                $portable = isset($all['portableSite']) && is_array($all['portableSite']) ? $all['portableSite'] : [];
                $nestedPath = (string) ($portable['archivePath'] ?? '');
                $expectedNestedHash = strtolower((string) ($portable['sha256'] ?? ''));
                if (!self::safeArchivePath($nestedPath) || strpos($nestedPath, 'portable-site/') !== 0 || !preg_match('/^[a-f0-9]{64}$/', $expectedNestedHash)) {
                    throw new \RuntimeException('Portable site-referencen i all.json er ugyldig.');
                }
                $summaryPath = (string) (($summary['portableSite']['archivePath'] ?? ''));
                if ($summaryPath !== $nestedPath) {
                    throw new \RuntimeException('export-summary.json peger ikke på samme portable sitepakke som all.json.');
                }
                $actualNestedHash = self::hashZipEntry($zip, $nestedPath);
                if (!hash_equals($expectedNestedHash, $actualNestedHash)) {
                    throw new \RuntimeException('Den indlejrede portable ZIP har forkert SHA-256.');
                }

                $nestedTmp = tempnam(get_temp_dir(), 'vdm-verify-portable-');
                if (!is_string($nestedTmp) || $nestedTmp === '') {
                    throw new \RuntimeException('Kunne ikke oprette midlertidig fil til nested ZIP-kontrol.');
                }
                self::copyZipEntryToFile($zip, $nestedPath, $nestedTmp);
                $nestedVerification = PortableTransferController::verifyPortablePackage($nestedTmp);
                $result['portableSite'] = [
                    'archivePath' => $nestedPath,
                    'sha256' => $actualNestedHash,
                    'schemaVersion' => (string) ($nestedVerification['schemaVersion'] ?? ''),
                    'managerVersion' => (string) ($nestedVerification['managerVersion'] ?? ''),
                    'counts' => isset($nestedVerification['counts']) && is_array($nestedVerification['counts']) ? $nestedVerification['counts'] : [],
                ];
            }
            return $result;
        } finally {
            $zip->close();
            if (is_string($nestedTmp) && $nestedTmp !== '') { @unlink($nestedTmp); }
        }
    }

    /** @return array<string,mixed> */
    private static function readZipJson(\ZipArchive $zip, string $name): array
    {
        $payload = $zip->getFromName($name);
        if (!is_string($payload) || $payload === '') {
            throw new \RuntimeException($name . ' mangler eller er tom.');
        }
        $decoded = json_decode($payload, true);
        if (!is_array($decoded)) {
            throw new \RuntimeException($name . ' indeholder ugyldig JSON.');
        }
        return $decoded;
    }

    private static function hashZipEntry(\ZipArchive $zip, string $name): string
    {
        $stream = $zip->getStream($name);
        if (!is_resource($stream)) {
            throw new \RuntimeException('ZIP-filen mangler: ' . $name);
        }
        $hash = hash_init('sha256');
        try {
            while (!feof($stream)) {
                $chunk = fread($stream, 1048576);
                if ($chunk === false) {
                    throw new \RuntimeException('ZIP-fil kunne ikke hashes: ' . $name);
                }
                if ($chunk !== '') { hash_update($hash, $chunk); }
            }
        } finally {
            fclose($stream);
        }
        return hash_final($hash);
    }

    private static function copyZipEntryToFile(\ZipArchive $zip, string $name, string $target): void
    {
        $in = $zip->getStream($name);
        if (!is_resource($in)) {
            throw new \RuntimeException('ZIP-filen kan ikke læses: ' . $name);
        }
        $out = fopen($target, 'wb');
        if (!is_resource($out)) {
            fclose($in);
            throw new \RuntimeException('Midlertidig kontrolfil kan ikke skrives.');
        }
        try {
            while (!feof($in)) {
                $chunk = fread($in, 1048576);
                if ($chunk === false) {
                    throw new \RuntimeException('Fejl under kopiering af ZIP-entry.');
                }
                if ($chunk !== '' && fwrite($out, $chunk) === false) {
                    throw new \RuntimeException('Fejl under skrivning af ZIP-entry.');
                }
            }
        } finally {
            fclose($in);
            fclose($out);
        }
    }

    private static function safeArchivePath(string $path): bool
    {
        if ($path === '' || strpos($path, "\0") !== false || str_contains($path, '\\') || str_starts_with($path, '/') || preg_match('/^[A-Za-z]:/', $path)) {
            return false;
        }
        foreach (explode('/', $path) as $part) {
            if ($part === '..') { return false; }
        }
        return true;
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addFile(\ZipArchive $zip, string $source, string $archivePath, array &$files): void
'''
export=rep(export,marker,helpers,'export verification helpers')
write(EXPORT,export)

history=json.loads(read(HISTORY))
history['versions'].insert(0,{
 'version':'0.1.92','date':'2026-09-03','items':[
  'VDM-EXPORT-INTEGRITY-002: alle nybyggede portable sitepakker kører fuld schema/path/SHA-256-inspektion før de returneres.',
  'Eksporter alt får export-summary.json og README.txt med indhold, site, version, portable archive path, counts og SHA-256.',
  'Den færdige ydre eksport-ZIP genåbnes før download; content digest, filstørrelser og SHA-256 verificeres for alle manifestposter.',
  'Ved Eksporter alt udtrækkes den indlejrede portable ZIP til midlertidig kontrol og valideres med samme preflight-motor som import.',
  'Download sendes kun efter bestået kontrol og mærkes med X-Visual-Designer-Verified: sha256.'
 ]
})
write(HISTORY,json.dumps(history,ensure_ascii=False,indent=2)+'\n')
notes=read(NOTES)
section='<section data-version="0.1.92"><h2>0.1.92</h2><ul><li><strong>Dobbelt eksportkontrol:</strong> både total-ZIP og den indlejrede portable site-ZIP verificeres før download.</li><li>Alle filer kontrolleres mod manifestets størrelse og SHA-256, og content-digest genberegnes.</li><li><strong>Eksporter alt</strong> indeholder nu <code>export-summary.json</code> og <code>README.txt</code> med præcis recovery-fil, counts og SHA-256.</li><li>Den portable ZIP testes med samme fulde preflight som ved import.</li></ul></section>\n'
anchor='<section data-version="0.1.91">'
if anchor not in notes: raise SystemExit('release note anchor missing')
notes=notes.replace(anchor,section+anchor,1)
write(NOTES,notes)
write(STATUS,'''# Visual Designer Manager v0.1.92 status\n\n- Candidate: two-layer Export All integrity verification.\n- Outer export manifest is rehashed after ZIP close.\n- Nested portable site ZIP is validated through the canonical import preflight inspector.\n- Export All contains machine-readable summary plus human README.\n- Release only after v0.1.92 QA and historical regressions pass.\n''')
print('Applied v0.1.92 candidate')
