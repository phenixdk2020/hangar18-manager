<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use Hangar18\UltimateDesigner\Contracts\SchemaValidator;
use Hangar18\UltimateDesigner\Core\Version;
use RuntimeException;

/**
 * Validates Site Builder templates while reusing the page editor element tree.
 *
 * Header/footer templates deliberately use the same Sections payload as pages.
 * This avoids a parallel element schema and keeps Components/Patterns compatible.
 */
final class SiteTemplateValidator
{
    public const SCHEMA_VERSION = '1.0';
    public const KIND_HEADER = 'header';
    public const KIND_FOOTER = 'footer';

    /** @var list<string> */
    private const KINDS = [self::KIND_HEADER, self::KIND_FOOTER];

    private SchemaValidator $pageSchema;

    public function __construct(SchemaValidator $pageSchema)
    {
        $this->pageSchema = $pageSchema;
    }

    /** @param array<string,mixed> $template @return list<string> */
    public function validate(array $template): array
    {
        $errors = [];
        $id = (string) ($template['Id'] ?? '');
        $kind = (string) ($template['Kind'] ?? '');
        $name = trim((string) ($template['Name'] ?? ''));
        $revision = $template['Revision'] ?? null;
        $sections = $template['Sections'] ?? null;

        if (($template['SchemaVersion'] ?? null) !== self::SCHEMA_VERSION) {
            $errors[] = 'SchemaVersion must be ' . self::SCHEMA_VERSION . '.';
        }
        if ($id === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{2,79}$/', $id)) {
            $errors[] = 'Id must be a stable lowercase template key.';
        }
        if (!in_array($kind, self::KINDS, true)) {
            $errors[] = 'Kind must be header or footer.';
        }
        if ($name === '' || mb_strlen($name) > 120) {
            $errors[] = 'Name must be 1-120 characters.';
        }
        if (!is_int($revision) || $revision < 1) {
            $errors[] = 'Revision must be a positive integer.';
        }
        if (!is_array($sections)) {
            $errors[] = 'Sections must be an array.';
            return $errors;
        }

        $pageState = [
            'Version' => Version::PAGE_SCHEMA,
            'PageSlug' => '__site-template__',
            'PageTitle' => $name,
            'ContentVersion' => $revision,
            'DataContextType' => '',
            'DataContextEntryId' => 0,
            'Sections' => array_values($sections),
        ];
        foreach ($this->pageSchema->validate($pageState) as $error) {
            $errors[] = 'Sections: ' . $error;
        }

        return array_values(array_unique($errors));
    }

    /** @param array<string,mixed> $template */
    public function assertValid(array $template): void
    {
        $errors = $this->validate($template);
        if ($errors !== []) {
            throw new RuntimeException('Invalid site template: ' . implode(' ', $errors));
        }
    }
}
