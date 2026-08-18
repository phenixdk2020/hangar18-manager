<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use Hangar18\UltimateDesigner\Contracts\InteractionActionHandler;

final class RedirectActionHandler implements InteractionActionHandler
{
    public function type(): string { return 'redirect'; }

    public function execute(array $config, array $context): array
    {
        $url = trim((string) ($config['Url'] ?? ''));
        if ($url === '' || !$this->isSafeUrl($url)) {
            return ['success'=>false,'message'=>'Redirect URL is missing or unsafe.'];
        }
        return ['success'=>true,'message'=>'Redirect prepared.','data'=>['redirect_url'=>$url]];
    }

    private function isSafeUrl(string $url): bool
    {
        if (str_starts_with($url, '/') || str_starts_with($url, '#')) { return true; }
        $scheme = strtolower((string) parse_url($url, PHP_URL_SCHEME));
        return in_array($scheme, ['http','https'], true);
    }
}
