<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** UD-101 SEO checks for metadata and one-H1 policy. */
final class SeoAnalyzer
{
    private StateInspector $inspector;
    private SeoMetadata $metadata;

    public function __construct(?StateInspector $inspector = null, ?SeoMetadata $metadata = null)
    {
        $this->inspector = $inspector ?? new StateInspector();
        $this->metadata = $metadata ?? new SeoMetadata();
    }

    /** @param array<string,mixed> $state @param array<string,mixed> $rawMetadata @return list<array<string,mixed>> */
    public function analyze(array $state, array $rawMetadata): array
    {
        $issues = [];
        $meta = $this->metadata->normalize($rawMetadata);
        $titleLength = mb_strlen((string) $meta['Title']);
        if ($titleLength === 0) {
            $issues[] = QualityIssue::make('seo','missing-title','error','SEO title mangler.');
        } elseif ($titleLength > 60) {
            $issues[] = QualityIssue::make('seo','long-title','warning','SEO title er længere end 60 tegn.','',['length'=>$titleLength]);
        }
        $descriptionLength = mb_strlen((string) $meta['MetaDescription']);
        if ($descriptionLength === 0) {
            $issues[] = QualityIssue::make('seo','missing-meta-description','warning','Meta description mangler.');
        } elseif ($descriptionLength > 160) {
            $issues[] = QualityIssue::make('seo','long-meta-description','warning','Meta description er længere end 160 tegn.','',['length'=>$descriptionLength]);
        }

        $h1 = [];
        foreach ($this->inspector->sections($state) as $section) {
            if ($this->inspector->headingLevel($section) === 1) { $h1[] = $this->inspector->key($section); }
        }
        if (count($h1) !== 1) {
            $issues[] = QualityIssue::make('seo','h1-policy','error','Siden skal have præcis én H1.','',['count'=>count($h1),'elements'=>$h1]);
        }
        if ((string) $meta['CanonicalUrl'] === '' && !empty($rawMetadata['CanonicalUrl'])) {
            $issues[] = QualityIssue::make('seo','invalid-canonical','error','Canonical URL skal være en gyldig HTTPS-adresse.');
        }
        if ((bool) $meta['Index'] && (string) $meta['SocialTitle'] === '') {
            $issues[] = QualityIssue::make('seo','missing-social-title','info','Social title er ikke udfyldt; frontend kan falde tilbage til SEO title.');
        }
        if ((bool) $meta['Index'] && (int) $meta['SocialImageMediaId'] <= 0) {
            $issues[] = QualityIssue::make('seo','missing-social-image','info','Socialt delingsbillede er ikke valgt.');
        }
        return $issues;
    }
}
