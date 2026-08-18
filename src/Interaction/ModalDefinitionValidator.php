<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Interaction;

use Hangar18\UltimateDesigner\Contracts\SchemaValidator;
use Hangar18\UltimateDesigner\Core\Version;
use RuntimeException;

/** UD-078 modal builder definition using the shared Sections element tree. */
final class ModalDefinitionValidator
{
    public const SCHEMA_VERSION = '1.0';
    private SchemaValidator $pageSchema;

    public function __construct(SchemaValidator $pageSchema) { $this->pageSchema = $pageSchema; }

    /** @param array<string,mixed> $modal @return list<string> */
    public function validate(array $modal): array
    {
        $errors = [];
        if (($modal['SchemaVersion'] ?? null) !== self::SCHEMA_VERSION) { $errors[] = 'SchemaVersion must be 1.0.'; }
        $id = trim((string) ($modal['Id'] ?? ''));
        $title = trim((string) ($modal['Title'] ?? ''));
        if ($id === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{2,79}$/', $id)) { $errors[] = 'Modal Id is invalid.'; }
        if ($title === '' || mb_strlen($title) > 160) { $errors[] = 'Modal Title must be 1-160 characters.'; }
        if (($modal['TrapFocus'] ?? true) !== true) { $errors[] = 'Modal TrapFocus must be enabled.'; }
        if (($modal['CloseOnEscape'] ?? true) !== true) { $errors[] = 'Modal CloseOnEscape must be enabled.'; }
        $sections = $modal['Sections'] ?? null;
        if (!is_array($sections)) { $errors[] = 'Sections must be an array.'; return $errors; }
        $page = [
            'Version'=>Version::PAGE_SCHEMA,
            'PageSlug'=>'__modal__',
            'PageTitle'=>$title,
            'ContentVersion'=>max(1,(int) ($modal['Revision'] ?? 1)),
            'DataContextType'=>'',
            'DataContextEntryId'=>0,
            'Sections'=>array_values($sections),
        ];
        foreach ($this->pageSchema->validate($page) as $error) { $errors[] = 'Sections: ' . $error; }
        return array_values(array_unique($errors));
    }

    /** @param array<string,mixed> $modal */
    public function assertValid(array $modal): void
    {
        $errors = $this->validate($modal);
        if ($errors !== []) { throw new RuntimeException('Invalid modal definition: ' . implode(' ', $errors)); }
    }
}
