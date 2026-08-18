<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

/** UD-074..076 orchestration: validate first, then execute ordered actions. */
final class FormSubmissionService
{
    private FormSubmissionValidator $validator;
    private ActionChainEngine $actions;

    public function __construct(FormSubmissionValidator $validator, ActionChainEngine $actions)
    {
        $this->validator = $validator;
        $this->actions = $actions;
    }

    /**
     * @param array<string,mixed> $form
     * @param array<string,mixed> $input
     * @param array<string,mixed> $meta
     * @return array<string,mixed>
     */
    public function submit(array $form, array $input, array $meta = []): array
    {
        $validation = $this->validator->validate($form, $input);
        if (!$validation['valid']) {
            return [
                'success' => false,
                'stage' => 'validation',
                'errors' => $validation['errors'],
                'values' => $validation['values'],
                'actions' => [],
            ];
        }

        $chain = $this->actions->execute(
            is_array($form['Actions'] ?? null) ? array_values($form['Actions']) : [],
            ['values' => $validation['values'], 'meta' => $meta, 'form' => $form]
        );
        return [
            'success' => $chain['success'],
            'stage' => $chain['success'] ? 'complete' : 'actions',
            'errors' => [],
            'values' => $validation['values'],
            'actions' => $chain['results'],
            'failed_action_index' => $chain['failed_index'],
        ];
    }
}
