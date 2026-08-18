<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Workflow;

use RuntimeException;

/** UD-085/086 secure preview tokens for unpublished working state. */
final class PreviewTokenService
{
    private string $secret;
    /** @var array<string,true> */
    private array $revoked = [];

    public function __construct(string $secret)
    {
        $secret = trim($secret);
        if (strlen($secret) < 32) {
            throw new RuntimeException('Preview token secret must be at least 32 characters.');
        }
        $this->secret = $secret;
    }

    /** @return array{token:string,expires:int,resource:string,device:string} */
    public function issue(string $resourceKey, string $device = 'desktop', int $ttlSeconds = 3600): array
    {
        $resourceKey = $this->resourceKey($resourceKey);
        $device = $this->device($device);
        $ttlSeconds = max(60, min(86400, $ttlSeconds));
        $expires = time() + $ttlSeconds;
        $nonce = bin2hex(random_bytes(12));
        $payload = $resourceKey . '|' . $device . '|' . $expires . '|' . $nonce;
        $signature = hash_hmac('sha256', $payload, $this->secret);
        $token = $this->base64UrlEncode($payload . '|' . $signature);
        return ['token' => $token, 'expires' => $expires, 'resource' => $resourceKey, 'device' => $device];
    }

    /** @return array{resource:string,device:string,expires:int}|null */
    public function validate(string $token): ?array
    {
        $token = trim($token);
        if ($token === '' || isset($this->revoked[hash('sha256', $token)])) {
            return null;
        }
        $decoded = $this->base64UrlDecode($token);
        if ($decoded === null) {
            return null;
        }
        $parts = explode('|', $decoded);
        if (count($parts) !== 5) {
            return null;
        }
        [$resource, $device, $expiresRaw, $nonce, $signature] = $parts;
        if (!ctype_digit($expiresRaw) || $nonce === '' || strlen($signature) !== 64) {
            return null;
        }
        $expires = (int) $expiresRaw;
        if ($expires < time()) {
            return null;
        }
        try {
            $resource = $this->resourceKey($resource);
            $device = $this->device($device);
        } catch (RuntimeException $e) {
            return null;
        }
        $payload = $resource . '|' . $device . '|' . $expires . '|' . $nonce;
        $expected = hash_hmac('sha256', $payload, $this->secret);
        if (!hash_equals($expected, $signature)) {
            return null;
        }
        return ['resource' => $resource, 'device' => $device, 'expires' => $expires];
    }

    public function revoke(string $token): void
    {
        $token = trim($token);
        if ($token !== '') {
            $this->revoked[hash('sha256', $token)] = true;
        }
    }

    private function resourceKey(string $value): string
    {
        $value = strtolower(trim($value));
        if ($value === '' || !preg_match('/^[a-z0-9][a-z0-9:._-]{1,159}$/', $value)) {
            throw new RuntimeException('Invalid preview resource key.');
        }
        return $value;
    }

    private function device(string $value): string
    {
        $value = strtolower(trim($value));
        if (!in_array($value, ['desktop', 'tablet', 'mobile'], true)) {
            throw new RuntimeException('Invalid preview device.');
        }
        return $value;
    }

    private function base64UrlEncode(string $value): string
    {
        return rtrim(strtr(base64_encode($value), '+/', '-_'), '=');
    }

    private function base64UrlDecode(string $value): ?string
    {
        if (!preg_match('/^[A-Za-z0-9_-]+$/', $value)) {
            return null;
        }
        $padding = strlen($value) % 4;
        if ($padding) {
            $value .= str_repeat('=', 4 - $padding);
        }
        $decoded = base64_decode(strtr($value, '-_', '+/'), true);
        return is_string($decoded) ? $decoded : null;
    }
}
