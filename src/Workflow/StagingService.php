<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Workflow;

use Hangar18\UltimateDesigner\Contracts\RevisionRepository;
use Hangar18\UltimateDesigner\Contracts\StagingRepository;
use RuntimeException;

/** UD-087/088 working/public staging with atomic publish. */
final class StagingService
{
    private StagingRepository $staging;
    private RevisionRepository $revisions;

    public function __construct(StagingRepository $staging, RevisionRepository $revisions)
    {
        $this->staging = $staging;
        $this->revisions = $revisions;
    }

    /** @param array<string,mixed> $state */
    public function saveWorking(string $resourceKey, array $state): void
    {
        $this->staging->saveWorking($this->key($resourceKey), $state);
    }

    /** @return array<string,mixed>|null */
    public function working(string $resourceKey): ?array
    {
        return $this->staging->working($this->key($resourceKey));
    }

    /** @return array<string,mixed>|null */
    public function published(string $resourceKey): ?array
    {
        return $this->staging->published($this->key($resourceKey));
    }

    /**
     * Promote working state atomically. A permanent pre-publish revision is created
     * before the public pointer/state is changed.
     * @return array<string,mixed>
     */
    public function publish(string $resourceKey, int $userId, string $note = ''): array
    {
        $key = $this->key($resourceKey);
        $working = $this->staging->working($key);
        if ($working === null) {
            throw new RuntimeException('No working state exists for publish.');
        }

        return $this->staging->transaction(function () use ($key, $working, $userId, $note): array {
            $publishedBefore = $this->staging->published($key);
            if ($publishedBefore !== null) {
                $history = $this->revisions->history($key);
                $sequence = count($history) + 1;
                $revision = [
                    'SchemaVersion' => RevisionService::SCHEMA_VERSION,
                    'Id' => 'rev-' . $sequence . '-prepublish-' . substr(hash('sha256', $key . '|' . microtime(true)), 0, 8),
                    'Sequence' => $sequence,
                    'UserId' => max(0, $userId),
                    'CreatedUtc' => gmdate('c'),
                    'Note' => mb_substr(trim($note !== '' ? $note : 'Pre-publish backup'), 0, 500),
                    'RestoreOf' => '',
                    'StateHash' => hash('sha256', $this->canonicalJson($publishedBefore)),
                    'State' => $publishedBefore,
                ];
                $this->revisions->append($key, $revision);
            }

            $this->staging->savePublished($key, $working);
            return [
                'ResourceKey' => $key,
                'PublishedUtc' => gmdate('c'),
                'StateHash' => hash('sha256', $this->canonicalJson($working)),
                'State' => $working,
            ];
        });
    }

    private function key(string $value): string
    {
        $value = strtolower(trim($value));
        if ($value === '' || !preg_match('/^[a-z0-9][a-z0-9:._-]{1,159}$/', $value)) {
            throw new RuntimeException('Invalid staging resource key.');
        }
        return $value;
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
