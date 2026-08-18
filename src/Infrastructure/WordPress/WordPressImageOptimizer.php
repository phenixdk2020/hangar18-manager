<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\ImageOptimizer;

/** Uses WordPress' image editor for optional derivatives; source is never deleted or replaced. */
final class WordPressImageOptimizer implements ImageOptimizer
{
    public function supports(string $format): bool
    {
        $mime = $this->mime($format);
        return $mime !== '' && function_exists('wp_image_editor_supports') && wp_image_editor_supports(['mime_type'=>$mime]);
    }

    public function optimize(string $sourcePath, string $targetPath, string $format, array $options = []): array
    {
        $mime = $this->mime($format);
        if ($mime === '' || !$this->supports($format)) {
            return ['success'=>false,'path'=>'','mime'=>$mime,'message'=>'Format is not supported by the WordPress image editor.'];
        }
        $sourcePath = wp_normalize_path($sourcePath);
        $targetPath = wp_normalize_path($targetPath);
        if (!is_file($sourcePath) || dirname($sourcePath) !== dirname($targetPath)) {
            return ['success'=>false,'path'=>'','mime'=>$mime,'message'=>'Source/target path is invalid.'];
        }
        $editor = wp_get_image_editor($sourcePath);
        if (is_wp_error($editor)) {
            return ['success'=>false,'path'=>'','mime'=>$mime,'message'=>$editor->get_error_message()];
        }
        $quality = max(1, min(100, (int) ($options['Quality'] ?? 82)));
        if (method_exists($editor, 'set_quality')) { $editor->set_quality($quality); }
        $maxWidth = max(0, (int) ($options['MaxWidth'] ?? 0));
        $maxHeight = max(0, (int) ($options['MaxHeight'] ?? 0));
        if ($maxWidth > 0 || $maxHeight > 0) {
            $size = $editor->get_size();
            if (is_array($size)) {
                $width = max(1, (int) ($size['width'] ?? 1));
                $height = max(1, (int) ($size['height'] ?? 1));
                $limitWidth = $maxWidth > 0 ? min($width, $maxWidth) : $width;
                $limitHeight = $maxHeight > 0 ? min($height, $maxHeight) : $height;
                if ($limitWidth < $width || $limitHeight < $height) {
                    $editor->resize($limitWidth, $limitHeight, false);
                }
            }
        }
        $saved = $editor->save($targetPath, $mime);
        if (is_wp_error($saved)) {
            return ['success'=>false,'path'=>'','mime'=>$mime,'message'=>$saved->get_error_message()];
        }
        return [
            'success'=>is_file((string) ($saved['path'] ?? $targetPath)),
            'path'=>(string) ($saved['path'] ?? $targetPath),
            'mime'=>(string) ($saved['mime-type'] ?? $mime),
            'message'=>'Derivative generated; original preserved.',
        ];
    }

    private function mime(string $format): string
    {
        switch (strtolower(trim($format))) {
            case 'webp': return 'image/webp';
            case 'avif': return 'image/avif';
            default: return '';
        }
    }
}
