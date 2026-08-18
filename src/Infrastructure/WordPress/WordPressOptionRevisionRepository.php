<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\RevisionRepository;
use RuntimeException;

/** Small option-backed revision store used by the pre-conversion portability workspace. */
final class WordPressOptionRevisionRepository implements RevisionRepository
{
    public const OPTION='hangar18_ud_revisions_v1';
    public const AUTOSAVE_OPTION='hangar18_ud_autosaves_v1';
    private const MAX_HISTORY=50;

    public function append(string $resourceKey,array $revision): array
    {
        $key=$this->key($resourceKey);$id=trim((string)($revision['Id']??''));if($id===''){throw new RuntimeException('Revision ID is required.');}
        $all=$this->store(self::OPTION);$history=is_array($all[$key]??null)?array_values($all[$key]):[];$history[]=$revision;
        if(count($history)>self::MAX_HISTORY){$history=array_slice($history,-self::MAX_HISTORY);}$all[$key]=$history;$this->persist(self::OPTION,$all);return $revision;
    }
    public function history(string $resourceKey): array{$key=$this->key($resourceKey);$all=$this->store(self::OPTION);return is_array($all[$key]??null)?array_values(array_filter($all[$key],'is_array')):[];}
    public function get(string $resourceKey,string $revisionId): ?array{$revisionId=trim($revisionId);foreach($this->history($resourceKey) as $revision){if((string)($revision['Id']??'')===$revisionId){return $revision;}}return null;}
    public function saveAutosave(string $resourceKey,?array $snapshot): void{$key=$this->key($resourceKey);$all=$this->store(self::AUTOSAVE_OPTION);if($snapshot===null){unset($all[$key]);}else{$all[$key]=$snapshot;}$this->persist(self::AUTOSAVE_OPTION,$all);}
    public function autosave(string $resourceKey): ?array{$key=$this->key($resourceKey);$all=$this->store(self::AUTOSAVE_OPTION);return is_array($all[$key]??null)?$all[$key]:null;}
    private function store(string $option): array{$raw=get_option($option,[]);return is_array($raw)?$raw:[];}
    private function persist(string $option,array $value): void{$ok=update_option($option,$value,false);if($ok===false&&get_option($option,[])!==$value){throw new RuntimeException('Revision store could not be persisted.');}}
    private function key(string $key): string{$key=strtolower(trim($key));if($key===''||strlen($key)>160||!preg_match('/^[a-z0-9][a-z0-9:._-]*$/',$key)){throw new RuntimeException('Invalid revision resource key.');}return $key;}
}
