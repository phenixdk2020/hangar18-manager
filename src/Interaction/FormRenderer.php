<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

/** UD-074 semantic/keyboard-accessible server-rendered form shell. */
final class FormRenderer
{
    private FormDefinitionValidator $validator;

    public function __construct(FormDefinitionValidator $validator)
    {
        $this->validator = $validator;
    }

    /** @param array<string,mixed> $form */
    public function render(array $form, string $action = ''): string
    {
        $this->validator->assertValid($form);
        $formId = $this->esc((string) $form['Id']);
        $html = '<form class="h18-form" data-h18-form="' . $formId . '" method="post" action="' . $this->esc($action) . '" novalidate>';
        $html .= '<div class="h18-form-status" aria-live="polite" role="status"></div>';
        foreach ($form['Fields'] as $field) {
            $html .= $this->renderField($formId, $field);
        }
        $label = trim((string) ($form['SubmitLabel'] ?? 'Send')) ?: 'Send';
        $html .= '<button type="submit" class="h18-form-submit">' . $this->esc($label) . '</button></form>';
        return $html;
    }

    /** @param array<string,mixed> $field */
    private function renderField(string $formId, array $field): string
    {
        $key = (string) $field['Key'];
        $type = (string) $field['Type'];
        $label = (string) ($field['Label'] ?? '');
        $rules = is_array($field['Validation'] ?? null) ? $field['Validation'] : [];
        $required = !empty($rules['Required']);
        $id = 'h18-' . $formId . '-' . $key;
        $errorId = $id . '-error';
        if ($type === 'hidden') {
            return '<input type="hidden" id="' . $this->esc($id) . '" name="' . $this->esc($key) . '" value="' . $this->esc((string) ($field['Value'] ?? '')) . '">';
        }

        $attrs = ' id="' . $this->esc($id) . '" name="' . $this->esc($key) . '" aria-describedby="' . $this->esc($errorId) . '"' . ($required ? ' required aria-required="true"' : '');
        $html = '<div class="h18-form-field h18-form-field--' . $this->esc($type) . '" data-h18-field="' . $this->esc($key) . '">';
        if (in_array($type, ['radio'], true)) {
            $html .= '<fieldset><legend>' . $this->esc($label) . ($required ? ' <span aria-hidden="true">*</span>' : '') . '</legend>';
            foreach ((array) ($field['Options'] ?? []) as $index => $option) {
                $value = is_array($option) ? (string) ($option['Value'] ?? '') : (string) $option;
                $text = is_array($option) ? (string) ($option['Label'] ?? $value) : (string) $option;
                $optionId = $id . '-' . $index;
                $html .= '<label for="' . $this->esc($optionId) . '"><input type="radio" id="' . $this->esc($optionId) . '" name="' . $this->esc($key) . '" value="' . $this->esc($value) . '"' . ($required ? ' required' : '') . '> ' . $this->esc($text) . '</label>';
            }
            $html .= '</fieldset>';
        } elseif ($type === 'checkbox') {
            $html .= '<label for="' . $this->esc($id) . '"><input type="checkbox"' . $attrs . ' value="1"> ' . $this->esc($label) . '</label>';
        } else {
            $html .= '<label for="' . $this->esc($id) . '">' . $this->esc($label) . ($required ? ' <span aria-hidden="true">*</span>' : '') . '</label>';
            if ($type === 'textarea') {
                $html .= '<textarea' . $attrs . '></textarea>';
            } elseif ($type === 'select') {
                $html .= '<select' . $attrs . '><option value="">Vælg…</option>';
                foreach ((array) ($field['Options'] ?? []) as $option) {
                    $value = is_array($option) ? (string) ($option['Value'] ?? '') : (string) $option;
                    $text = is_array($option) ? (string) ($option['Label'] ?? $value) : (string) $option;
                    $html .= '<option value="' . $this->esc($value) . '">' . $this->esc($text) . '</option>';
                }
                $html .= '</select>';
            } else {
                $inputType = in_array($type, ['email','date','file'], true) ? $type : 'text';
                $html .= '<input type="' . $inputType . '"' . $attrs . '>';
            }
        }
        $html .= '<div id="' . $this->esc($errorId) . '" class="h18-form-error" aria-live="polite"></div></div>';
        return $html;
    }

    private function esc(string $value): string
    {
        return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
