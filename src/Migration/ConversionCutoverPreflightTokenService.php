<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\Portability\CanonicalJson;
use RuntimeException;

/** Signs an eligible I10 preflight snapshot. The token itself grants no execution capability. */
final class ConversionCutoverPreflightTokenService
{
    private string $secret;
    private CanonicalJson $json;

    public function __construct(string $secret, ?CanonicalJson $json = null)
    {
        $secret = trim($secret);
        if (strlen($secret) < 32) { throw new RuntimeException('Cutover preflight token secret must be at least 32 characters.'); }
        $this->secret = $secret;
        $this->json = $json ?? new CanonicalJson();
    }

    /** @param array<string,mixed> $preflight @return array{token:string,expires:int,preflightHash:string} */
    public function issue(array $preflight, int $ttl = 900): array
    {
        if (empty($preflight['EligibleForFutureCutover']) || !empty($preflight['Blockers'])) {
            throw new RuntimeException('Blocked cutover preflight cannot be signed.');
        }
        if (!empty($preflight['Executable']) || !empty($preflight['PublicMutationAvailable'])) {
            throw new RuntimeException('Only non-executable preflight snapshots may be signed in this phase.');
        }
        $expires = time() + max(60, min(3600, $ttl));
        $hash = $this->preflightHash($preflight);
        $payload = $hash . '|' . $expires;
        $mac = hash_hmac('sha256', $payload, $this->secret);
        return ['token' => self::b64($payload . '|' . $mac), 'expires' => $expires, 'preflightHash' => $hash];
    }

    /** @param array<string,mixed> $preflight */
    public function verify(string $token, array $preflight): bool
    {
        $decoded = self::unb64($token);
        if ($decoded === '') { return false; }
        $parts = explode('|', $decoded);
        if (count($parts) !== 3) { return false; }
        [$hash, $expires, $mac] = $parts;
        if (!ctype_digit($expires) || (int) $expires < time()) { return false; }
        if (!hash_equals($hash, $this->preflightHash($preflight))) { return false; }
        $payload = $hash . '|' . $expires;
        return hash_equals(hash_hmac('sha256', $payload, $this->secret), $mac);
    }

    /** @param array<string,mixed> $preflight */
    public function preflightHash(array $preflight): string
    {
        $stable = [
            'SchemaVersion' => (string) ($preflight['SchemaVersion'] ?? ''),
            'Mode' => (string) ($preflight['Mode'] ?? ''),
            'Slug' => (string) ($preflight['Slug'] ?? ''),
            'PageId' => (int) ($preflight['PageId'] ?? 0),
            'Permalink' => (string) ($preflight['Permalink'] ?? ''),
            'ShadowSourceHash' => (string) ($preflight['ShadowSourceHash'] ?? ''),
            'CurrentLegacyHash' => (string) ($preflight['CurrentLegacyHash'] ?? ''),
            'ManualEvidenceComplete' => (bool) ($preflight['ManualEvidenceComplete'] ?? false),
            'AcceptanceValid' => (bool) ($preflight['AcceptanceValid'] ?? false),
            'SourceDriftFree' => (bool) ($preflight['SourceDriftFree'] ?? false),
            'EligibleForFutureCutover' => (bool) ($preflight['EligibleForFutureCutover'] ?? false),
            'Blockers' => array_values((array) ($preflight['Blockers'] ?? [])),
            'Executable' => (bool) ($preflight['Executable'] ?? false),
            'PublicMutationAvailable' => (bool) ($preflight['PublicMutationAvailable'] ?? false),
        ];
        return $this->json->hash($stable);
    }

    private static function b64(string $value): string { return rtrim(strtr(base64_encode($value), '+/', '-_'), '='); }
    private static function unb64(string $value): string
    {
        $value = strtr(trim($value), '-_', '+/');
        $pad = strlen($value) % 4;
        if ($pad) { $value .= str_repeat('=', 4 - $pad); }
        $decoded = base64_decode($value, true);
        return is_string($decoded) ? $decoded : '';
    }
}
