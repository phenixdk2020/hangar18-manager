<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\AI\AiProviderRegistry;
use Hangar18\UltimateDesigner\Contracts\AiProvider;

/**
 * External provider adapters register through `hangar18_ud_ai_providers`.
 * Expected value: id => ['label'=>string,'provider'=>AiProvider].
 * No credentials are read or stored here.
 */
final class WordPressAiProviderRegistryFactory
{
    public function create(): AiProviderRegistry
    {
        $registry=new AiProviderRegistry();
        $entries=function_exists('apply_filters')?apply_filters('hangar18_ud_ai_providers',[]):[];
        if(!is_array($entries)){return $registry;}
        foreach($entries as $id=>$entry){
            if(!is_array($entry)){continue;}$provider=$entry['provider']??null;$label=trim((string)($entry['label']??$id));
            if(!$provider instanceof AiProvider||$label===''){continue;}
            try{$registry->register((string)$id,$label,$provider);}catch(\Throwable $e){continue;}
        }
        return $registry;
    }
}
