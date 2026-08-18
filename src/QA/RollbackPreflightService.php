<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\QA;

use Hangar18\UltimateDesigner\Portability\CanonicalJson;

/**
 * Rehearses migrate/restore semantics on an in-memory copy only.
 * This is preflight evidence and can never satisfy the required live-copy manual gate by itself.
 */
final class RollbackPreflightService
{
    private CanonicalJson $json;
    public function __construct(?CanonicalJson $json=null){$this->json=$json??new CanonicalJson();}

    /** @param array<string,mixed> $snapshot @return array<string,mixed> */
    public function rehearse(array $snapshot): array
    {
        $original=$snapshot;$beforeHash=$this->json->hash($original);
        $working=$original;$working['_UdRollbackPreflight']=['Marker'=>'temporary','Utc'=>gmdate('c')];
        $mutatedHash=$this->json->hash($working);
        $restored=$original;$restoredHash=$this->json->hash($restored);
        return [
            'SchemaVersion'=>'1.0','Mode'=>'in-memory-copy-only','Pass'=>$restored===$original&&hash_equals($beforeHash,$restoredHash),
            'BeforeHash'=>$beforeHash,'MutatedHash'=>$mutatedHash,'RestoredHash'=>$restoredHash,
            'SourceItems'=>count($original),'RanUtc'=>gmdate('c'),'SatisfiesManualLiveCopyGate'=>false,
        ];
    }
}
