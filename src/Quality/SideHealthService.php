<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Quality;

/** Orchestrates UD-098..103 analyzers into one editor-friendly report. */
final class SideHealthService
{
    private AccessibilityAnalyzer $accessibility;
    private ResponsiveAnalyzer $responsive;
    private DesignConsistencyAnalyzer $design;
    private SeoAnalyzer $seo;
    private PerformanceAnalyzer $performance;
    private SideHealthAggregator $aggregator;

    public function __construct()
    {
        $inspector = new StateInspector();
        $this->accessibility = new AccessibilityAnalyzer($inspector);
        $this->responsive = new ResponsiveAnalyzer($inspector);
        $this->design = new DesignConsistencyAnalyzer($inspector);
        $this->seo = new SeoAnalyzer($inspector);
        $this->performance = new PerformanceAnalyzer($inspector);
        $this->aggregator = new SideHealthAggregator();
    }

    /**
     * @param array<string,mixed> $state
     * @param array<string,mixed> $seoMetadata
     * @param array<int,int> $assetBytes
     * @return array<string,mixed>
     */
    public function analyze(array $state, array $seoMetadata = [], array $assetBytes = []): array
    {
        $issues = array_merge(
            $this->accessibility->analyze($state),
            $this->responsive->analyze($state),
            $this->design->analyze($state),
            $this->seo->analyze($state,$seoMetadata),
            $this->performance->analyze($state,$assetBytes)
        );
        return $this->aggregator->aggregate($issues);
    }
}
