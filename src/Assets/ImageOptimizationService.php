<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

use Hangar18\UltimateDesigner\Contracts\ImageOptimizer;
use RuntimeException;

/** UD-092 creates optional derivatives without replacing or deleting the source file. */
final class ImageOptimizationService
{
    private ImageOptimizer $optimizer;
    private ImageOptimizationPlanner $planner;

    public function __construct(ImageOptimizer $optimizer)
    {
        $this->optimizer = $optimizer;
        $this->planner = new ImageOptimizationPlanner($optimizer);
    }

    /**
     * @param array<string,mixed> $options
     * @return array{source:string,preserved:bool,derivatives:list<array<string,mixed>>,skipped:list<string>}
     */
    public function optimize(string $sourcePath, string $sourceMime, array $options = []): array
    {
        $sourcePath = trim($sourcePath);
        if ($sourcePath === '' || !is_file($sourcePath)) {
            throw new RuntimeException('Image source file does not exist.');
        }
        $plan = $this->planner->plan($sourceMime);
        $directory = dirname($sourcePath);
        $filename = pathinfo($sourcePath, PATHINFO_FILENAME);
        $derivatives = [];
        foreach ($plan['Targets'] as $target) {
            $targetPath = $directory . DIRECTORY_SEPARATOR . $filename . $target['Suffix'];
            if ($targetPath === $sourcePath) { continue; }
            $result = $this->optimizer->optimize($sourcePath, $targetPath, $target['Format'], $options);
            $derivatives[] = [
                'Format'=>$target['Format'],
                'Mime'=>$target['Mime'],
                'Path'=>(string) ($result['path'] ?? $targetPath),
                'Success'=>(bool) ($result['success'] ?? false),
                'Message'=>(string) ($result['message'] ?? ''),
            ];
        }
        return ['source'=>$sourcePath,'preserved'=>is_file($sourcePath),'derivatives'=>$derivatives,'skipped'=>$plan['Skipped']];
    }
}
