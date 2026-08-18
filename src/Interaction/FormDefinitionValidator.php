<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use RuntimeException;

/** UD-074/075 schema validator for generic forms. */
final class FormDefinitionValidator
{
    public const SCHEMA_VERSION = '1.0';
    /** @var list<string> */
    private const FIELD_TYPES = ['text','email','textarea','select','checkbox','radio','date','file','hidden'];
    /** @var list<string> */
    private const ACTION_TYPES = ['mail','save','redirect','webhook'];

    /** @param array<string,mixed> $form @return list<string> */
    public function validate(array $form): array
    {
        $errors = [];
        if (($form['SchemaVersion'] ?? null) !== self::SCHEMA_VERSION) {
            $errors[] = 'SchemaVersion must be ' . self::SCHEMA_VERSION . '.';
        }
        $id = trim((string) ($form['Id'] ?? ''));
        if ($id === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{2,79}$/', $id)) {
            $errors[] = 'Form Id is invalid.';
        }
        $fields = $form['Fields'] ?? null;
        if (!is_array($fields)) {
            $errors[] = 'Fields must be an array.';
            return $errors;
        }
        if (count($fields) > 100) {
            $errors[] = 'Form exceeds maximum field count.';
        }
        $seen = [];
        foreach (array_values($fields) as $index => $field) {
            if (!is_array($field)) {
                $errors[] = "Field {$index} must be an object/array.";
                continue;
            }
            $key = trim((string) ($field['Key'] ?? ''));
            $type = strtolower(trim((string) ($field['Type'] ?? '')));
            if ($key === '' || !preg_match('/^[a-z][a-z0-9_]{0,63}$/', $key)) {
                $errors[] = "Field {$index} has invalid Key.";
                continue;
            }
            if (isset($seen[$key])) {
                $errors[] = "Field Key '{$key}' is duplicated.";
            }
            $seen[$key] = true;
            if (!in_array($type, self::FIELD_TYPES, true)) {
                $errors[] = "Field '{$key}' has unsupported Type.";
            }
            if ($type !== 'hidden' && trim((string) ($field['Label'] ?? '')) === '') {
                $errors[] = "Field '{$key}' requires Label.";
            }
            $rules = $field['Validation'] ?? [];
            if (!is_array($rules)) {
                $errors[] = "Field '{$key}' Validation must be an object/array.";
                continue;
            }
            foreach (['MinLength','MaxLength'] as $rule) {
                if (isset($rules[$rule]) && (!is_int($rules[$rule]) || $rules[$rule] < 0 || $rules[$rule] > 100000)) {
                    $errors[] = "Field '{$key}' {$rule} is invalid.";
                }
            }
            if (isset($rules['Pattern']) && (!is_string($rules['Pattern']) || strlen($rules['Pattern']) > 200)) {
                $errors[] = "Field '{$key}' Pattern is invalid.";
            }
            if (isset($rules['Message']) && (!is_string($rules['Message']) || mb_strlen($rules['Message']) > 300)) {
                $errors[] = "Field '{$key}' validation Message is invalid.";
            }
            if (in_array($type, ['select','radio'], true)) {
                $options = $field['Options'] ?? null;
                if (!is_array($options) || $options === []) {
                    $errors[] = "Field '{$key}' requires Options.";
                }
            }
        }

        $actions = $form['Actions'] ?? [];
        if (!is_array($actions) || count($actions) > 10) {
            $errors[] = 'Actions must be an array with at most 10 entries.';
        } else {
            foreach (array_values($actions) as $index => $action) {
                if (!is_array($action)) {
                    $errors[] = "Action {$index} must be an object/array.";
                    continue;
                }
                $type = strtolower(trim((string) ($action['Type'] ?? '')));
                if (!in_array($type, self::ACTION_TYPES, true)) {
                    $errors[] = "Action {$index} has unsupported Type.";
                }
            }
        }
        return array_values(array_unique($errors));
    }

    /** @param array<string,mixed> $form */
    public function assertValid(array $form): void
    {
        $errors = $this->validate($form);
        if ($errors !== []) {
            throw new RuntimeException('Invalid form definition: ' . implode(' ', $errors));
        }
    }
}
