<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use RuntimeException;

/** Stores manual I10 shadow acceptance evidence only; never writes page/public state. */
final class WordPressOptionConversionAcceptanceRepository
{
    public const OPTION = 'hangar18_ud_conversion_acceptance_v1';

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        $stored = get_option(self::OPTION, []);
        if (!is_array($stored)) {
            return [];
        }
        $out = [];
        foreach ($stored as $slug => $record) {
            if (is_string($slug) && is_array($record)) {
                $out[$slug] = $record;
            }
        }
        ksort($out, SORT_STRING);
        return $out;
    }

    /** @param array<string,mixed> $record */
    public function save(string $slug, array $record): void
    {
        $slug = strtolower(trim($slug));
        if ($slug === '' || strlen($slug) > 200) {
            throw new RuntimeException('Conversion acceptance slug is invalid.');
        }
        if (($record['Slug'] ?? '') !== $slug) {
            throw new RuntimeException('Conversion acceptance record slug mismatch.');
        }
        $all = $this->all();
        $all[$slug] = $record;
        ksort($all, SORT_STRING);
        $ok = update_option(self::OPTION, $all, false);
        if ($ok === false && get_option(self::OPTION, []) !== $all) {
            throw new RuntimeException('Conversion acceptance evidence could not be persisted.');
        }
    }
}
