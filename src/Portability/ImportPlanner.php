<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use Hangar18\UltimateDesigner\Contracts\ArtifactRepository;
use RuntimeException;

/** UD-109/111 plans artifact imports before any mutation. */
final class ImportPlanner
{
    private ArtifactRepository $repository;

    public function __construct(ArtifactRepository $repository)
    {
        $this->repository = $repository;
    }

    /**
     * @param list<array<string,mixed>> $artifacts
     * @return array<string,mixed>
     */
    public function plan(array $artifacts, string $strategy = 'remap', bool $dryRun = true): array
    {
        $strategy = strtolower(trim($strategy));
        if (!in_array($strategy,['remap','skip','reject'],true)) { throw new RuntimeException('Unsupported import conflict strategy.'); }
        $mappings = [];
        $actions = [];
        $conflicts = [];
        $reserved = [];

        foreach ($artifacts as $artifact) {
            if (!is_array($artifact)) { throw new RuntimeException('Invalid artifact in import plan.'); }
            $type = strtolower(trim((string) ($artifact['Type'] ?? '')));
            $sourceId = trim((string) ($artifact['SourceId'] ?? ''));
            $exportId = trim((string) ($artifact['ExportId'] ?? ''));
            if ($type === '' || $sourceId === '' || $exportId === '') { throw new RuntimeException('Artifact identity is incomplete.'); }
            $targetId = $sourceId;
            $collision = $this->repository->exists($type,$targetId) || isset($reserved[$type.':'.$targetId]);
            $action = 'create';
            if ($collision) {
                $conflict = ['ExportId'=>$exportId,'Type'=>$type,'SourceId'=>$sourceId,'Reason'=>'target-id-exists','Strategy'=>$strategy];
                if ($strategy === 'reject') {
                    $action = 'blocked';
                    $targetId = '';
                    $conflicts[] = $conflict;
                } elseif ($strategy === 'skip') {
                    $action = 'skip';
                    $targetId = $sourceId;
                    $conflicts[] = $conflict;
                } else {
                    $targetId = $this->nextId($type,$sourceId,$reserved);
                    $action = 'remap';
                    $conflict['TargetId'] = $targetId;
                    $conflicts[] = $conflict;
                }
            }
            if ($targetId !== '') { $reserved[$type.':'.$targetId] = true; }
            $mappings[$exportId] = $targetId;
            $actions[] = ['ExportId'=>$exportId,'Type'=>$type,'SourceId'=>$sourceId,'TargetId'=>$targetId,'Action'=>$action,'Data'=>$artifact['Data'] ?? []];
        }

        return [
            'SchemaVersion'=>'1.0',
            'DryRun'=>$dryRun,
            'Strategy'=>$strategy,
            'Valid'=>!in_array('blocked',array_column($actions,'Action'),true),
            'Mappings'=>$mappings,
            'Conflicts'=>$conflicts,
            'Actions'=>$actions,
            'MutationAllowed'=>!$dryRun && !in_array('blocked',array_column($actions,'Action'),true),
        ];
    }

    /** @param array<string,true> $reserved */
    private function nextId(string $type, string $sourceId, array $reserved): string
    {
        for ($i=2;$i<=10000;$i++) {
            $candidate = $sourceId . '-import-' . $i;
            if (!$this->repository->exists($type,$candidate) && !isset($reserved[$type.':'.$candidate])) { return $candidate; }
        }
        throw new RuntimeException('Could not allocate a collision-free artifact ID.');
    }
}
