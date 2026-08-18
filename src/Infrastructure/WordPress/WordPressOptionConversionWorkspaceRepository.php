<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Portability\CanonicalJson;
use RuntimeException;

/** Stores copy-only I10 rehearsal snapshots; never replaces legacy/public page state. */
final class WordPressOptionConversionWorkspaceRepository
{
    public const OPTION='hangar18_ud_conversion_workspace_v1';
    private CanonicalJson $json;
    public function __construct(?CanonicalJson $json=null){$this->json=$json??new CanonicalJson();}

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        $stored=get_option(self::OPTION,[]);if(!is_array($stored)){return [];}$out=[];
        foreach($stored as $slug=>$record){if(is_string($slug)&&is_array($record)){$out[$slug]=$record;}}
        ksort($out,SORT_STRING);return $out;
    }

    /** @param array<string,mixed> $sourceState @return array<string,mixed> */
    public function createShadow(string $slug,array $sourceState,int $userId): array
    {
        $slug=strtolower(trim($slug));if($slug===''||strlen($slug)>200){throw new RuntimeException('Conversion shadow slug is invalid.');}
        $record=['SchemaVersion'=>'1.0','Slug'=>$slug,'Mode'=>'shadow-copy-only','SourceHash'=>$this->json->hash($sourceState),'SourceState'=>$sourceState,'CreatedUtc'=>gmdate('c'),'UserId'=>max(0,$userId),'PublicActivation'=>false,'Accepted'=>false];
        $all=$this->all();$all[$slug]=$record;ksort($all,SORT_STRING);$ok=update_option(self::OPTION,$all,false);
        if($ok===false&&get_option(self::OPTION,[])!==$all){throw new RuntimeException('Conversion shadow workspace could not be persisted.');}
        return $record;
    }
}
