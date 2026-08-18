<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use Hangar18\UltimateDesigner\Contracts\InteractionActionHandler;
use Hangar18\UltimateDesigner\Contracts\InteractionEntryWriter;
use Throwable;

final class SaveEntryActionHandler implements InteractionActionHandler
{
    private InteractionEntryWriter $writer;

    public function __construct(InteractionEntryWriter $writer) { $this->writer = $writer; }
    public function type(): string { return 'save'; }

    public function execute(array $config, array $context): array
    {
        $dataType = trim((string) ($config['DataType'] ?? ''));
        $values = is_array($context['values'] ?? null) ? $context['values'] : [];
        if ($dataType === '') {
            return ['success'=>false,'message'=>'Save action requires DataType.'];
        }
        try {
            $saved = $this->writer->save($dataType, $values);
            return ['success'=>true,'message'=>'Entry saved.','data'=>$saved];
        } catch (Throwable $exception) {
            return ['success'=>false,'message'=>$exception->getMessage()];
        }
    }
}
