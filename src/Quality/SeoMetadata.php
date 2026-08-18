<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** UD-101 normalized model behind the SEO metadata panel. */
final class SeoMetadata
{
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function normalize(array $raw): array
    {
        $canonical = trim((string) ($raw['CanonicalUrl'] ?? ''));
        if ($canonical !== '') {
            $parts = parse_url($canonical);
            if (!is_array($parts) || strtolower((string) ($parts['scheme'] ?? '')) !== 'https' || empty($parts['host'])) { $canonical = ''; }
        }
        return [
            'Title'=>mb_substr(trim((string) ($raw['Title'] ?? '')),0,120),
            'MetaDescription'=>mb_substr(trim((string) ($raw['MetaDescription'] ?? '')),0,320),
            'CanonicalUrl'=>$canonical,
            'Index'=>array_key_exists('Index',$raw) ? (bool) $raw['Index'] : true,
            'Follow'=>array_key_exists('Follow',$raw) ? (bool) $raw['Follow'] : true,
            'SocialTitle'=>mb_substr(trim((string) ($raw['SocialTitle'] ?? '')),0,120),
            'SocialDescription'=>mb_substr(trim((string) ($raw['SocialDescription'] ?? '')),0,320),
            'SocialImageMediaId'=>max(0,(int) ($raw['SocialImageMediaId'] ?? 0)),
        ];
    }
}
