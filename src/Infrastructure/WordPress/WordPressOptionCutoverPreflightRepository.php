<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use RuntimeException;

/** Stores signed non-executable I10 preflight snapshots; never mutates page/public state. */
final class WordPressOptionCutoverPreflightRepository
{
    public const OPTION = 'hangar18_ud_cutover_preflight_v1';

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        $stored = get_option(self::OPTION, []);
        if (!is_array($stored)) { return []; }
        $out = [];
        foreach ($stored as $slug => $record) {
            if (is_string($slug) && is_array($record)) { $out[$slug] = $record; }
        }
        ksort($out, SORT_STRING);
        return $out;
    }

    /** @param array<string,mixed> $preflight @param array<string,mixed> $signed @return array<string,mixed> */
    public function save(string $slug, array $preflight, array $signed, int $userId): array
    {
        $slug = strtolower(trim($slug));
        if ($slug === '' || ($preflight['Slug'] ?? '') !== $slug) { throw new RuntimeException('Cutover preflight slug mismatch.'); }
        if (empty($preflight['EligibleForFutureCutover']) || !empty($preflight['Blockers'])) { throw new RuntimeException('Blocked cutover preflight cannot be persisted as ready.'); }
        if (!empty($preflight['Executable']) || !empty($preflight['PublicMutationAvailable'])) { throw new RuntimeException('Preflight repository only accepts non-executable snapshots.'); }
        $token = trim((string) ($signed['token'] ?? ''));
        $hash = trim((string) ($signed['preflightHash'] ?? ''));
        $expires = (int) ($signed['expires'] ?? 0);
        if ($token === '' || $hash === '' || $expires <= time()) { throw new RuntimeException('Signed cutover preflight metadata is invalid or expired.'); }
        $record = [
            'SchemaVersion' => '1.0',
            'Slug' => $slug,
            'Mode' => 'signed-cutover-preflight-only',
            'Preflight' => $preflight,
            'PreflightHash' => $hash,
            'Token' => $token,
            'TokenExpires' => $expires,
            'Executable' => false,
            'UserId' => max(0, $userId),
            'CreatedUtc' => gmdate('c'),
        ];
        $all = $this->all();
        $all[$slug] = $record;
        ksort($all, SORT_STRING);
        $ok = update_option(self::OPTION, $all, false);
        if ($ok === false && get_option(self::OPTION, []) !== $all) { throw new RuntimeException('Cutover preflight could not be persisted.'); }
        return $record;
    }
}
