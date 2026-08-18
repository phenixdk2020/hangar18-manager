<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

/** UD-075 server-side validation with field-scoped messages. */
final class FormSubmissionValidator
{
    private FormDefinitionValidator $definitions;

    public function __construct(FormDefinitionValidator $definitions)
    {
        $this->definitions = $definitions;
    }

    /**
     * @param array<string,mixed> $form
     * @param array<string,mixed> $input
     * @return array{valid:bool,values:array<string,mixed>,errors:array<string,string>}
     */
    public function validate(array $form, array $input): array
    {
        $this->definitions->assertValid($form);
        $values = [];
        $errors = [];
        foreach ($form['Fields'] as $field) {
            $key = (string) $field['Key'];
            $type = (string) $field['Type'];
            $rules = is_array($field['Validation'] ?? null) ? $field['Validation'] : [];
            $raw = $input[$key] ?? null;
            $value = $this->normalize($type, $raw);
            $values[$key] = $value;
            $empty = $value === '' || $value === null || $value === false || $value === [];
            $message = trim((string) ($rules['Message'] ?? ''));
            $fallback = static fn(string $text): string => $message !== '' ? $message : $text;

            if (!empty($rules['Required']) && $empty) {
                $errors[$key] = $fallback('Feltet skal udfyldes.');
                continue;
            }
            if ($empty) { continue; }

            if ($type === 'email' && (!is_string($value) || filter_var($value, FILTER_VALIDATE_EMAIL) === false)) {
                $errors[$key] = $fallback('Indtast en gyldig e-mailadresse.');
                continue;
            }
            if ($type === 'date' && (!$this->isDate((string) $value))) {
                $errors[$key] = $fallback('Indtast en gyldig dato.');
                continue;
            }
            if (is_string($value)) {
                $length = mb_strlen($value);
                if (isset($rules['MinLength']) && $length < (int) $rules['MinLength']) {
                    $errors[$key] = $fallback('Værdien er for kort.');
                    continue;
                }
                if (isset($rules['MaxLength']) && $length > (int) $rules['MaxLength']) {
                    $errors[$key] = $fallback('Værdien er for lang.');
                    continue;
                }
                $pattern = (string) ($rules['Pattern'] ?? '');
                if ($pattern !== '' && !$this->matchesPattern($value, $pattern)) {
                    $errors[$key] = $fallback('Værdien har ikke det forventede format.');
                    continue;
                }
            }
            if (in_array($type, ['select','radio'], true)) {
                $allowed = [];
                foreach ((array) ($field['Options'] ?? []) as $option) {
                    if (is_array($option)) { $allowed[] = (string) ($option['Value'] ?? ''); }
                    else { $allowed[] = (string) $option; }
                }
                if (!in_array((string) $value, $allowed, true)) {
                    $errors[$key] = $fallback('Den valgte værdi er ikke tilladt.');
                }
            }
        }
        return ['valid'=>$errors === [], 'values'=>$values, 'errors'=>$errors];
    }

    /** @return mixed */
    private function normalize(string $type, $raw)
    {
        if ($type === 'checkbox') { return !empty($raw); }
        if ($type === 'file') { return is_array($raw) ? $raw : []; }
        if (is_array($raw)) { return array_map(static fn($item): string => trim((string) $item), $raw); }
        return trim((string) ($raw ?? ''));
    }

    private function isDate(string $value): bool
    {
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $value);
        return $date !== false && $date->format('Y-m-d') === $value;
    }

    private function matchesPattern(string $value, string $pattern): bool
    {
        $pattern = str_replace('~', '\\~', $pattern);
        $result = @preg_match('~' . $pattern . '~u', $value);
        return $result === 1;
    }
}
