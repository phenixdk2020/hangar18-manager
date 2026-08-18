<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface ImageOptimizer
{
    public function supports(string $format): bool;

    /**
     * @param array<string,mixed> $options
     * @return array{success:bool,path:string,mime:string,message:string}
     */
    public function optimize(string $sourcePath, string $targetPath, string $format, array $options = []): array;
}
