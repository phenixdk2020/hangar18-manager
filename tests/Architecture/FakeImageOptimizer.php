<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\ImageOptimizer;

final class FakeImageOptimizer implements ImageOptimizer
{
    /** @var list<string> */
    private array $formats;

    /** @param list<string> $formats */
    public function __construct(array $formats = ['webp','avif'])
    {
        $this->formats = $formats;
    }

    public function supports(string $format): bool
    {
        return in_array(strtolower($format), $this->formats, true);
    }

    public function optimize(string $sourcePath, string $targetPath, string $format, array $options = []): array
    {
        if (!$this->supports($format)) {
            return ['success'=>false,'path'=>'','mime'=>'','message'=>'unsupported'];
        }
        $content = file_get_contents($sourcePath);
        if (!is_string($content) || file_put_contents($targetPath, $content . ':' . $format) === false) {
            return ['success'=>false,'path'=>'','mime'=>'','message'=>'write failed'];
        }
        return [
            'success'=>true,
            'path'=>$targetPath,
            'mime'=>$format === 'avif' ? 'image/avif' : 'image/webp',
            'message'=>'ok',
        ];
    }
}
