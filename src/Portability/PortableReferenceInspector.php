<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

/** Finds unresolved portable asset/artifact references before import mutation. */
final class PortableReferenceInspector
{
    /** @param mixed $value @return array{Artifacts:list<string>,Assets:list<string>} */
    public function inspect($value): array
    {
        $artifacts=[];$assets=[];$this->walk($value,$artifacts,$assets);ksort($artifacts,SORT_STRING);ksort($assets,SORT_STRING);
        return ['Artifacts'=>array_keys($artifacts),'Assets'=>array_keys($assets)];
    }
    /** @param mixed $value @param array<string,true> $artifacts @param array<string,true> $assets */
    private function walk($value,array &$artifacts,array &$assets): void
    {
        if(is_string($value)){
            if(strncmp($value,'artifact://',11)===0){$id=substr($value,11);if($id!==''){$artifacts[$id]=true;}}
            elseif(strncmp($value,'asset://',8)===0){$id=substr($value,8);if($id!==''){$assets[$id]=true;}}
            return;
        }
        if(!is_array($value)){return;}foreach($value as $child){$this->walk($child,$artifacts,$assets);}
    }
}
