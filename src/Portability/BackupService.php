<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use Hangar18\UltimateDesigner\Contracts\RevisionRepository;
use RuntimeException;

/** UD-112 immutable pre-import/pre-publish backup records. */
final class BackupService
{
    private RevisionRepository $repository;
    private CanonicalJson $json;

    public function __construct(RevisionRepository $repository, ?CanonicalJson $json = null)
    {
        $this->repository = $repository;
        $this->json = $json ?? new CanonicalJson();
    }

    /** @param array<string,mixed> $state @return array<string,mixed> */
    public function create(string $resourceKey, array $state, int $userId, string $note): array
    {
        $key = $this->key($resourceKey);
        $history = $this->repository->history($key);
        $sequence = count($history) + 1;
        $revision = [
            'SchemaVersion'=>'1.0',
            'Id'=>'backup-'.$sequence.'-'.substr(hash('sha256',$key.'|'.microtime(true)),0,12),
            'Sequence'=>$sequence,
            'UserId'=>max(0,$userId),
            'CreatedUtc'=>gmdate('c'),
            'Note'=>mb_substr(trim($note),0,500),
            'BackupKind'=>'portability',
            'StateHash'=>$this->json->hash($state),
            'State'=>$state,
        ];
        return $this->repository->append($key,$revision);
    }

    /** @return array<string,mixed> */
    public function restoreState(string $resourceKey, string $revisionId): array
    {
        $revision = $this->repository->get($this->key($resourceKey),trim($revisionId));
        if ($revision === null || !is_array($revision['State'] ?? null)) { throw new RuntimeException('Backup revision was not found.'); }
        $state = $revision['State'];
        if (($revision['StateHash'] ?? '') !== $this->json->hash($state)) { throw new RuntimeException('Backup checksum validation failed.'); }
        return $state;
    }

    private function key(string $resourceKey): string
    {
        $key = strtolower(trim($resourceKey));
        if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9:._-]{1,159}$/',$key)) { throw new RuntimeException('Invalid backup resource key.'); }
        return $key;
    }
}
