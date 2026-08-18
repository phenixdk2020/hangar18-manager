<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\AI;

/** Provider-neutral settings. Credentials are deliberately not part of this model. */
final class AiSettings
{
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(array $raw): array
    {
        $providerId=strtolower(trim((string)($raw['ProviderId']??'')));
        if($providerId!==''&&!preg_match('/^[a-z0-9][a-z0-9._-]{0,79}$/',$providerId)){$providerId='';}
        $enabled=!empty($raw['Enabled'])&&$providerId!=='';
        return [
            'SchemaVersion'=>'1.0',
            'Enabled'=>$enabled,
            'ProviderId'=>$providerId,
            'UpdatedUtc'=>gmdate('c'),
        ];
    }
}
