<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use Hangar18\UltimateDesigner\Contracts\TemplateAssignmentRepository;
use RuntimeException;

/** UD-073 priority-based single/archive/system template assignment resolver. */
final class TemplateAssignmentService
{
    public const SCHEMA_VERSION = '1.0';
    /** @var list<string> */
    private const KINDS = ['single', 'archive', 'system'];
    /** @var list<string> */
    private const CONTEXT_TYPES = ['global', 'datatype', 'taxonomy', 'context'];

    private TemplateAssignmentRepository $repository;

    public function __construct(TemplateAssignmentRepository $repository)
    {
        $this->repository = $repository;
    }

    /** @return array<string,mixed> */
    public function assign(string $templateId, string $kind, string $contextType = 'global', string $contextKey = '*', int $priority = 10, ?string $assignmentId = null): array
    {
        $kind = strtolower(trim($kind));
        $contextType = strtolower(trim($contextType));
        $contextKey = trim($contextKey) !== '' ? trim($contextKey) : '*';
        if (!in_array($kind, self::KINDS, true)) {
            throw new RuntimeException('Unsupported template assignment kind.');
        }
        if (!in_array($contextType, self::CONTEXT_TYPES, true)) {
            throw new RuntimeException('Unsupported template assignment context type.');
        }
        if (trim($templateId) === '') {
            throw new RuntimeException('TemplateId is required.');
        }

        $id = $assignmentId !== null && trim($assignmentId) !== ''
            ? $this->normalizeId($assignmentId)
            : 'assign-' . substr(hash('sha256', implode('|', [$templateId, $kind, $contextType, $contextKey, (string) microtime(true)])), 0, 16);
        $assignment = [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Id' => $id,
            'TemplateId' => trim($templateId),
            'Kind' => $kind,
            'ContextType' => $contextType,
            'ContextKey' => $contextKey,
            'Priority' => max(-1000, min(1000, $priority)),
            'Active' => true,
            'UpdatedUtc' => gmdate('c'),
        ];
        return $this->repository->save($assignment);
    }

    /**
     * @param array<string,string> $context e.g. ['datatype'=>'vehicle','taxonomy'=>'category:featured','context'=>'search']
     * @return array<string,mixed>|null
     */
    public function resolve(string $kind, array $context): ?array
    {
        $kind = strtolower(trim($kind));
        if (!in_array($kind, self::KINDS, true)) {
            throw new RuntimeException('Unsupported template assignment kind.');
        }
        $candidates = array_values(array_filter($this->repository->all(), static function (array $assignment) use ($kind, $context): bool {
            if (empty($assignment['Active']) || ($assignment['Kind'] ?? '') !== $kind) {
                return false;
            }
            $type = (string) ($assignment['ContextType'] ?? 'global');
            $key = (string) ($assignment['ContextKey'] ?? '*');
            if ($type === 'global') {
                return true;
            }
            $actual = (string) ($context[$type] ?? '');
            return $actual !== '' && ($key === '*' || $key === $actual);
        }));

        usort($candidates, static function (array $a, array $b): int {
            $priority = ((int) ($b['Priority'] ?? 0)) <=> ((int) ($a['Priority'] ?? 0));
            if ($priority !== 0) {
                return $priority;
            }
            $specificity = static function (array $item): int {
                $score = ($item['ContextType'] ?? 'global') === 'global' ? 0 : 10;
                if (($item['ContextKey'] ?? '*') !== '*') { $score += 5; }
                return $score;
            };
            return $specificity($b) <=> $specificity($a);
        });

        return $candidates[0] ?? null;
    }

    public function delete(string $assignmentId): void
    {
        $this->repository->delete($this->normalizeId($assignmentId));
    }

    /** @return list<array<string,mixed>> */
    public function all(): array
    {
        return $this->repository->all();
    }

    private function normalizeId(string $id): string
    {
        $id = strtolower(trim($id));
        $id = preg_replace('/[^a-z0-9_-]+/', '-', $id) ?? '';
        return trim($id, '-_');
    }
}
