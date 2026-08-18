<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;
use RuntimeException;

final class WordPressOptionManualQaEvidenceRepository
{
    public const OPTION='hangar18_ud_manual_qa_evidence_v1';
    private ManualEvidenceValidator $validator;
    public function __construct(?ManualEvidenceValidator $validator=null){$this->validator=$validator??new ManualEvidenceValidator();}

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        $stored=get_option(self::OPTION,[]);if(!is_array($stored)){return [];}$out=[];
        foreach($stored as $gate=>$record){if(is_string($gate)&&is_array($record)){$out[$gate]=$record;}}
        ksort($out,SORT_STRING);return $out;
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function save(string $gate,array $raw,int $userId): array
    {
        $record=$this->validator->normalize($gate,$raw,$userId);$all=$this->all();$all[$gate]=$record;ksort($all,SORT_STRING);
        $ok=update_option(self::OPTION,$all,false);
        if($ok===false&&get_option(self::OPTION,[])!==$all){throw new RuntimeException('Manual QA evidence could not be persisted.');}
        return $record;
    }
}
