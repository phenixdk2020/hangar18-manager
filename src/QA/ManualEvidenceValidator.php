<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\QA;

use RuntimeException;

/** Validates human evidence. Automated tests are deliberately not accepted as manual proof. */
final class ManualEvidenceValidator
{
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(string $gate,array $raw,int $userId): array
    {
        $gate=trim($gate);$required=(new ReleaseReadiness())->requiredManualEvidence();
        if($gate===''||!array_key_exists($gate,$required)){throw new RuntimeException('Unknown manual QA gate.');}
        $status=strtolower(trim((string)($raw['Status']??'pending')));
        if(!in_array($status,['pending','pass','fail'],true)){throw new RuntimeException('Invalid manual QA status.');}
        $environment=mb_substr(trim((string)($raw['Environment']??'')),0,240);
        $evidenceRef=mb_substr(trim((string)($raw['EvidenceRef']??'')),0,500);
        $notes=mb_substr(trim((string)($raw['Notes']??'')),0,3000);
        $confirmed=!empty($raw['ConfirmedManual']);
        if($status==='pass'&&(!$confirmed||$environment===''||$evidenceRef==='')){
            throw new RuntimeException('PASS requires explicit manual confirmation, environment and evidence reference.');
        }
        return [
            'SchemaVersion'=>'1.0','Gate'=>$gate,'Status'=>$status,'Environment'=>$environment,
            'EvidenceRef'=>$evidenceRef,'Notes'=>$notes,'ConfirmedManual'=>$status==='pass'&&$confirmed,
            'UserId'=>max(0,$userId),'CapturedUtc'=>gmdate('c'),
        ];
    }

    /** @param array<string,array<string,mixed>> $records @return array<string,bool> */
    public function statusMap(array $records): array
    {
        $map=(new ReleaseReadiness())->requiredManualEvidence();
        foreach($map as $gate=>$unused){$record=$records[$gate]??null;$map[$gate]=is_array($record)&&($record['Status']??'')==='pass'&&!empty($record['ConfirmedManual']);}
        return $map;
    }
}
