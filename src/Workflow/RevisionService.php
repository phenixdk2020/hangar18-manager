<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Workflow;

use Hangar18\UltimateDesigner\Contracts\RevisionRepository;
use RuntimeException;

/** UD-081..083 revision/autosave service. */
final class RevisionService
{
    public const SCHEMA_VERSION = '1.0';
    private RevisionRepository $repository;

    public function __construct(RevisionRepository $repository)
    {
        $this->repository = $repository;
    }

    /** @param array<string,mixed> $state @return array<string,mixed> */
    public function save(string $resourceKey, array $state, int $userId, string $note = ''): array
    {
        $key = $this->key($resourceKey);
        $history = $this->repository->history($key);
        $sequence = count($history) + 1;
        $revision = [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Id' => 'rev-' . $sequence . '-' . substr(hash('sha256', $key . '|' . microtime(true)), 0, 12),
            'Sequence' => $sequence,
            'UserId' => max(0, $userId),
            'CreatedUtc' => gmdate('c'),
            'Note' => mb_substr(trim($note), 0, 500),
            'RestoreOf' => '',
            'StateHash' => hash('sha256', $this->canonicalJson($state)),
            'State' => $state,
        ];
        $saved = $this->repository->append($key, $revision);
        $this->repository->saveAutosave($key, null);
        return $saved;
    }

    /** @param array<string,mixed> $state @return array<string,mixed> */
    public function autosave(string $resourceKey, array $state, int $userId): array
    {
        $key = $this->key($resourceKey);
        $snapshot = [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'ResourceKey' => $key,
            'UserId' => max(0, $userId),
            'UpdatedUtc' => gmdate('c'),
            'StateHash' => hash('sha256', $this->canonicalJson($state)),
            'State' => $state,
        ];
        $this->repository->saveAutosave($key, $snapshot);
        return $snapshot;
    }

    /** @return array<string,mixed>|null */
    public function recoverAutosave(string $resourceKey): ?array
    {
        return $this->repository->autosave($this->key($resourceKey));
    }

    /** @return list<array<string,mixed>> */
    public function history(string $resourceKey): array
    {
        return $this->repository->history($this->key($resourceKey));
    }

    /** @return array<string,mixed> */
    public function restore(string $resourceKey, string $revisionId, int $userId, string $note = ''): array
    {
        $key = $this->key($resourceKey);
        $source = $this->repository->get($key, trim($revisionId));
        if ($source === null || !is_array($source['State'] ?? null)) {
            throw new RuntimeException('Revision to restore was not found.');
        }
        $history = $this->repository->history($key);
        $sequence = count($history) + 1;
        $revision = [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Id' => 'rev-' . $sequence . '-' . substr(hash('sha256', $key . '|restore|' . microtime(true)), 0, 12),
            'Sequence' => $sequence,
            'UserId' => max(0, $userId),
            'CreatedUtc' => gmdate('c'),
            'Note' => mb_substr(trim($note !== '' ? $note : 'Restore ' . $revisionId), 0, 500),
            'RestoreOf' => (string) $source['Id'],
            'StateHash' => (string) ($source['StateHash'] ?? hash('sha256', $this->canonicalJson($source['State']))),
            'State' => $source['State'],
        ];
        return $this->repository->append($key, $revision);
    }

    private function key(string $resourceKey): string
    {
        $key = strtolower(trim($resourceKey));
        if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9:._-]{1,159}$/', $key)) {
            throw new RuntimeException('Invalid revision resource key.');
        }
        return $key;
    }

    /** @param array<string,mixed> $state */
    private function canonicalJson(array $state): string
    {
        $normalize = function ($value) use (&$normalize) {
            if (!is_array($value)) { return $value; }
            if ($this->isList($value)) { return array_map($normalize, $value); }
            ksort($value);
            foreach ($value as $key => $item) { $value[$key] = $normalize($item); }
            return $value;
        };
        $json = json_encode($normalize($state), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        return is_string($json) ? $json : '{}';
    }

    /** PHP 8.0-compatible replacement for array_is_list(). */
    private function isList(array $value): bool
    {
        $expected = 0;
        foreach ($value as $key => $_) {
            if ($key !== $expected) { return false; }
            $expected++;
        }
        return true;
    }
}
