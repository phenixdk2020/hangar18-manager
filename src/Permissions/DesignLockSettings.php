<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

final class DesignLockSettings
{
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(array $raw): array
    {
        $released=$raw['ReleasedProperties']??['Title','Content','AltText','Label','Url'];if(is_string($released)){$released=preg_split('/[,;\n]+/',$released)?:[];}if(!is_array($released)){$released=[];}$clean=[];
        foreach($released as $property){$property=trim((string)$property);if($property!==''&&preg_match('/^[A-Za-z][A-Za-z0-9_]{0,79}$/',$property)){$clean[$property]=true;}}
        $released=array_keys($clean);sort($released,SORT_STRING);
        return ['SchemaVersion'=>'1.0','Enabled'=>!empty($raw['Enabled']),'LockStructure'=>array_key_exists('LockStructure',$raw)?(bool)$raw['LockStructure']:true,'LockDesign'=>array_key_exists('LockDesign',$raw)?(bool)$raw['LockDesign']:true,'ReleasedProperties'=>$released,'UpdatedUtc'=>gmdate('c')];
    }

    /** @param array<string,mixed> $settings @return array<string,true> */
    public function releasedMap(array $settings): array{$out=[];foreach((array)($settings['ReleasedProperties']??[]) as $property){$property=(string)$property;if($property!==''){$out[$property]=true;}}return $out;}
}
