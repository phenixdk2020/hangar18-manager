<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

use Hangar18\UltimateDesigner\Contracts\AiProvider;
use RuntimeException;

final class AiProviderRegistry
{
    /** @var array<string,array{Label:string,Provider:AiProvider}> */
    private array $providers=[];

    public function register(string $id,string $label,AiProvider $provider): void
    {
        $id=strtolower(trim($id));$label=trim($label);
        if($id===''||!preg_match('/^[a-z0-9][a-z0-9._-]{0,79}$/',$id)){throw new RuntimeException('Invalid AI provider ID.');}
        if($label===''){throw new RuntimeException('AI provider label is required.');}
        $this->providers[$id]=['Label'=>mb_substr($label,0,120),'Provider'=>$provider];ksort($this->providers,SORT_STRING);
    }

    /** @return array<string,string> */
    public function labels(): array{$out=[];foreach($this->providers as $id=>$entry){$out[$id]=$entry['Label'];}return $out;}
    public function has(string $id): bool{return isset($this->providers[strtolower(trim($id))]);}
    public function get(string $id): AiProvider{$id=strtolower(trim($id));if(!isset($this->providers[$id])){throw new RuntimeException('Configured AI provider is not registered.');}return $this->providers[$id]['Provider'];}
}
