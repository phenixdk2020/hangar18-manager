<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\ArtifactRepository;
use RuntimeException;
use Throwable;

/**
 * Isolated I6 import workspace. Imported artifacts are deliberately NOT written
 * into active page/menu/template stores during the pre-conversion phase.
 */
final class WordPressOptionArtifactRepository implements ArtifactRepository
{
    public const OPTION='hangar18_ud_portable_artifacts_v1';
    private const TYPES=['component','template','menu','form'];

    public function exists(string $type,string $id): bool
    {
        $type=$this->type($type);$id=$this->id($id);$all=$this->snapshot();
        return isset($all[$type][$id]);
    }

    public function ids(string $type): array
    {
        $type=$this->type($type);$ids=array_keys($this->snapshot()[$type]??[]);sort($ids,SORT_STRING);return array_values($ids);
    }

    public function save(string $type,string $id,array $data): void
    {
        $type=$this->type($type);$id=$this->id($id);$all=$this->snapshot();$all[$type]??=[];$all[$type][$id]=$data;ksort($all[$type],SORT_STRING);$this->persist($all);
    }

    public function snapshot(): array
    {
        $raw=get_option(self::OPTION,[]);if(!is_array($raw)){return [];}$out=[];
        foreach(self::TYPES as $type){if(!is_array($raw[$type]??null)){continue;}foreach($raw[$type] as $id=>$data){$id=trim((string)$id);if($id!==''&&is_array($data)){$out[$type][$id]=$data;}}if(isset($out[$type])){ksort($out[$type],SORT_STRING);}}
        ksort($out,SORT_STRING);return $out;
    }

    public function transaction(callable $callback)
    {
        $before=$this->snapshot();
        try{return $callback();}
        catch(Throwable $e){$this->persist($before);throw $e;}
    }

    /** @param array<string,array<string,array<string,mixed>>> $snapshot */
    public function restoreSnapshot(array $snapshot): void
    {
        $clean=[];
        foreach($snapshot as $type=>$items){$type=$this->type((string)$type);if(!is_array($items)){throw new RuntimeException('Artifact snapshot items must be arrays.');}foreach($items as $id=>$data){$id=$this->id((string)$id);if(!is_array($data)){throw new RuntimeException('Artifact snapshot data must be arrays.');}$clean[$type][$id]=$data;}if(isset($clean[$type])){ksort($clean[$type],SORT_STRING);}}
        ksort($clean,SORT_STRING);$this->persist($clean);
    }

    private function persist(array $value): void
    {
        $ok=update_option(self::OPTION,$value,false);
        if($ok===false&&get_option(self::OPTION,[])!==$value){throw new RuntimeException('Portability workspace could not be persisted.');}
    }
    private function type(string $type): string{$type=strtolower(trim($type));if(!in_array($type,self::TYPES,true)){throw new RuntimeException('Unsupported artifact type.');}return $type;}
    private function id(string $id): string{$id=trim($id);if($id===''||strlen($id)>190||!preg_match('/^[A-Za-z0-9][A-Za-z0-9._:-]*$/',$id)){throw new RuntimeException('Invalid artifact ID.');}return $id;}
}
