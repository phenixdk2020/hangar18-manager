<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

use Hangar18\UltimateDesigner\Compatibility\CompatibilityPolicy;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;

/**
 * Pure decision service. It can say whether a future cutover would be eligible,
 * but it performs no writes and exposes no activation mechanism.
 */
final class ConversionReadinessGate
{
    private ConversionTargetCatalog $targets;
    public function __construct(?ConversionTargetCatalog $targets=null){$this->targets=$targets??new ConversionTargetCatalog();}

    /**
     * @param array<string,bool> $manualEvidence
     * @param list<string> $acceptedSlugs
     * @return array<string,mixed>
     */
    public function evaluate(string $slug,array $manualEvidence,array $acceptedSlugs=[],string $comparisonSlug=''): array
    {
        $slug=strtolower(trim($slug));$comparisonSlug=strtolower(trim($comparisonSlug));$accepted=array_values(array_unique(array_map(static fn($v): string=>strtolower(trim((string)$v)),$acceptedSlugs)));$blockers=[];
        $required=(new ReleaseReadiness())->requiredManualEvidence();
        foreach(array_keys($required) as $gate){if(empty($manualEvidence[$gate])){$blockers[]='manual-gate:'.$gate;}}
        if($slug===''){$blockers[]='target-empty';}

        $kind='comparison';$domain='';
        if($this->targets->isCore($slug)){
            $kind='core';
            if($comparisonSlug===''||!in_array($comparisonSlug,$accepted,true)){$blockers[]='comparison-page-not-accepted';}
            $order=$this->targets->coreOrder();$index=array_search($slug,$order,true);
            if(is_int($index)){for($i=0;$i<$index;$i++){if(!in_array($order[$i],$accepted,true)){$blockers[]='prior-core-not-accepted:'.$order[$i];}}}
        }elseif($this->targets->isProtected($slug)){
            $kind='protected';$domain=$this->targets->protectedDomain($slug);
            foreach($this->targets->coreOrder() as $core){if(!in_array($core,$accepted,true)){$blockers[]='core-not-accepted:'.$core;}}
            if(CompatibilityPolicy::mustUseLegacyRuntime($domain)){$blockers[]='protected-legacy-runtime-policy:'.$domain;}
        }else{
            if($comparisonSlug===''||$slug!==$comparisonSlug||!$this->targets->isComparisonCandidate($slug)){$blockers[]='not-approved-comparison-target';}
        }

        $blockers=array_values(array_unique($blockers));sort($blockers,SORT_STRING);
        return ['SchemaVersion'=>'1.0','Slug'=>$slug,'Kind'=>$kind,'ProtectedDomain'=>$domain,'EligibleForFutureCutover'=>$blockers===[],'Blockers'=>$blockers,'ManualEvidenceComplete'=>!array_filter(array_keys($required),static fn(string $gate): bool=>empty($manualEvidence[$gate]))];
    }
}
