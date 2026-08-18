<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use RuntimeException;

/**
 * Stores AI proposals only. It never receives page repositories or page-write access.
 */
final class WordPressOptionAiProposalRepository
{
    public const OPTION='hangar18_ud_ai_proposals_v1';
    private const MAX_ITEMS=50;

    /** @return list<array<string,mixed>> */
    public function all(): array
    {
        $stored=get_option(self::OPTION,[]);
        if(!is_array($stored)){return [];}
        $items=[];
        foreach($stored as $item){if(is_array($item)&&trim((string)($item['Id']??''))!==''){$items[]=$item;}}
        usort($items,static fn(array $a,array $b): int => strcmp((string)($b['CreatedUtc']??''),(string)($a['CreatedUtc']??'')));
        return array_slice($items,0,self::MAX_ITEMS);
    }

    /** @return array<string,mixed>|null */
    public function get(string $id): ?array
    {
        $id=trim($id);if($id===''){return null;}
        foreach($this->all() as $item){if((string)($item['Id']??'')===$id){return $item;}}
        return null;
    }

    /** @param array<string,mixed> $proposal */
    public function save(array $proposal): void
    {
        $id=trim((string)($proposal['Id']??''));
        if($id===''||strlen($id)>100){throw new RuntimeException('AI proposal ID is invalid.');}
        $items=$this->all();$next=[];$replaced=false;
        foreach($items as $item){if((string)($item['Id']??'')===$id){$next[]=$proposal;$replaced=true;}else{$next[]=$item;}}
        if(!$replaced){array_unshift($next,$proposal);}
        $next=array_slice($next,0,self::MAX_ITEMS);
        $ok=update_option(self::OPTION,$next,false);
        if($ok===false){$after=get_option(self::OPTION,[]);if(!is_array($after)||$after!==$next){throw new RuntimeException('AI proposal workspace could not be persisted.');}}
    }
}
