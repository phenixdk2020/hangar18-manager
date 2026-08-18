<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Migration;

/** Builds the I10 order and blockers without performing migration or activation. */
final class ConversionPlanService
{
    private ConversionTargetCatalog $targets;
    private ConversionReadinessGate $gate;
    public function __construct(?ConversionTargetCatalog $targets=null,?ConversionReadinessGate $gate=null){$this->targets=$targets??new ConversionTargetCatalog();$this->gate=$gate??new ConversionReadinessGate($this->targets);}

    /**
     * @param list<array<string,mixed>> $pages
     * @param array<string,bool> $manualEvidence
     * @param list<string> $acceptedSlugs
     * @return array<string,mixed>
     */
    public function plan(array $pages,array $manualEvidence,array $acceptedSlugs=[]): array
    {
        $normalized=[];
        foreach($pages as $page){if(!is_array($page)){continue;}$slug=strtolower(trim((string)($page['Slug']??$page['slug']??'')));if($slug===''){continue;}$normalized[$slug]=['Slug'=>$slug,'Title'=>trim((string)($page['Title']??$page['title']??$slug))];}
        ksort($normalized,SORT_STRING);
        $comparison=$this->chooseComparison(array_values($normalized));$comparisonSlug=(string)($comparison['Slug']??'');
        $stages=[];
        if($comparisonSlug!==''){$stages[]=$this->row(1,'comparison',$comparisonSlug,(string)$comparison['Title'],$manualEvidence,$acceptedSlugs,$comparisonSlug);}
        else{$stages[]=['Stage'=>1,'Kind'=>'comparison','Slug'=>'','Title'=>'Ingen sikker sammenligningsside fundet','Exists'=>false,'EligibleForFutureCutover'=>false,'Blockers'=>['comparison-page-missing']];}
        $stage=2;
        foreach($this->targets->coreOrder() as $slug){$page=$normalized[$slug]??['Slug'=>$slug,'Title'=>$slug];$row=$this->row($stage++,'core',$slug,(string)$page['Title'],$manualEvidence,$acceptedSlugs,$comparisonSlug);$row['Exists']=isset($normalized[$slug]);if(!$row['Exists']){$row['Blockers'][]='wordpress-page-missing';$row['EligibleForFutureCutover']=false;}$stages[]=$row;}
        foreach($this->targets->protectedSlugs() as $slug=>$domain){$page=$normalized[$slug]??['Slug'=>$slug,'Title'=>$slug];$row=$this->row($stage++,'protected',$slug,(string)$page['Title'],$manualEvidence,$acceptedSlugs,$comparisonSlug);$row['ProtectedDomain']=$domain;$row['Exists']=isset($normalized[$slug]);if(!$row['Exists']){$row['Blockers'][]='wordpress-page-missing';$row['EligibleForFutureCutover']=false;}$stages[]=$row;}
        return ['SchemaVersion'=>'1.0','Mode'=>'plan-only','ComparisonSlug'=>$comparisonSlug,'ManualGateCount'=>count($manualEvidence),'Stages'=>$stages,'PublicMutationAvailable'=>false];
    }

    /** @param list<array<string,mixed>> $pages @return array<string,mixed>|null */
    private function chooseComparison(array $pages): ?array
    {
        foreach($pages as $page){if($this->targets->isComparisonCandidate((string)($page['Slug']??''))){return $page;}}
        return null;
    }

    /** @param array<string,bool> $manualEvidence @param list<string> $acceptedSlugs @return array<string,mixed> */
    private function row(int $stage,string $kind,string $slug,string $title,array $manualEvidence,array $acceptedSlugs,string $comparisonSlug): array
    {
        $decision=$this->gate->evaluate($slug,$manualEvidence,$acceptedSlugs,$comparisonSlug);
        return ['Stage'=>$stage,'Kind'=>$kind,'Slug'=>$slug,'Title'=>$title,'Exists'=>true,'EligibleForFutureCutover'=>(bool)$decision['EligibleForFutureCutover'],'Blockers'=>(array)$decision['Blockers'],'ProtectedDomain'=>(string)($decision['ProtectedDomain']??'')];
    }
}
