<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

use Hangar18\UltimateDesigner\Contracts\ImageOptimizer;

/** UD-092 determines safe derivative formats while always preserving the original. */
final class ImageOptimizationPlanner
{
    private ImageOptimizer $optimizer;

    public function __construct(ImageOptimizer $optimizer)
    {
        $this->optimizer = $optimizer;
    }

    /**
     * @return array{PreserveOriginal:bool,Targets:list<array{Format:string,Mime:string,Suffix:string}>,Skipped:list<string>}
     */
    public function plan(string $sourceMime): array
    {
        $sourceMime = strtolower(trim($sourceMime));
        $targets = [];
        $skipped = [];
        foreach ([
            ['Format'=>'webp','Mime'=>'image/webp','Suffix'=>'.h18.webp'],
            ['Format'=>'avif','Mime'=>'image/avif','Suffix'=>'.h18.avif'],
        ] as $candidate) {
            if ($sourceMime === $candidate['Mime']) {
                $skipped[] = $candidate['Format'] . ':already-source';
                continue;
            }
            if (!$this->optimizer->supports($candidate['Format'])) {
                $skipped[] = $candidate['Format'] . ':unsupported';
                continue;
            }
            $targets[] = $candidate;
        }
        return ['PreserveOriginal'=>true,'Targets'=>$targets,'Skipped'=>$skipped];
    }
}
