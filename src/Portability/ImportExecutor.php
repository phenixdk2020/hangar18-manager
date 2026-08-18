<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use Hangar18\UltimateDesigner\Contracts\ArtifactRepository;
use RuntimeException;

/** UD-109/111/112 executes only a confirmed non-dry-run plan and always backs up first. */
final class ImportExecutor
{
    private ArtifactRepository $repository;
    private BackupService $backups;
    private ReferenceRemapper $remapper;

    public function __construct(ArtifactRepository $repository, BackupService $backups, ?ReferenceRemapper $remapper = null)
    {
        $this->repository = $repository;
        $this->backups = $backups;
        $this->remapper = $remapper ?? new ReferenceRemapper();
    }

    /**
     * @param array<string,mixed> $plan
     * @param array<string,int> $assetMappings
     * @return array<string,mixed>
     */
    public function execute(array $plan, array $assetMappings, int $userId, bool $confirmed): array
    {
        if (!$confirmed) { throw new RuntimeException('Import requires explicit confirmation.'); }
        if (!empty($plan['DryRun']) || empty($plan['MutationAllowed']) || empty($plan['Valid'])) {
            throw new RuntimeException('Dry-run/invalid import plan cannot mutate target state.');
        }
        $mappings = is_array($plan['Mappings'] ?? null) ? $plan['Mappings'] : [];
        $actions = is_array($plan['Actions'] ?? null) ? array_values($plan['Actions']) : [];

        $snapshot = $this->repository->snapshot();
        $backup = $this->backups->create('portability:artifact-import',$snapshot,$userId,'Automatic pre-import backup');

        $written = $this->repository->transaction(function () use ($actions,$mappings,$assetMappings): array {
            $saved = [];
            foreach ($actions as $action) {
                if (!is_array($action)) { throw new RuntimeException('Invalid import action.'); }
                $mode = (string) ($action['Action'] ?? '');
                if ($mode === 'skip') { continue; }
                if (!in_array($mode,['create','remap'],true)) { throw new RuntimeException('Blocked/unknown import action cannot execute.'); }
                $type = strtolower(trim((string) ($action['Type'] ?? '')));
                $targetId = trim((string) ($action['TargetId'] ?? ''));
                if ($type === '' || $targetId === '') { throw new RuntimeException('Import action target is incomplete.'); }
                $data = is_array($action['Data'] ?? null) ? $action['Data'] : [];
                $remapped = $this->remapper->remap($data,$mappings,$assetMappings);
                if (!is_array($remapped)) { throw new RuntimeException('Remapped artifact data is invalid.'); }
                $this->repository->save($type,$targetId,$remapped);
                $saved[] = ['Type'=>$type,'Id'=>$targetId,'ExportId'=>(string) ($action['ExportId'] ?? '')];
            }
            return $saved;
        });

        return [
            'BackupId'=>(string) ($backup['Id'] ?? ''),
            'BackupHash'=>(string) ($backup['StateHash'] ?? ''),
            'Written'=>$written,
            'Mappings'=>$mappings,
            'AssetMappings'=>$assetMappings,
        ];
    }
}
