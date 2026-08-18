<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\Logger;

/**
 * Compatibility adapter for the existing Hangar18 Manager log option.
 *
 * Entry shape and 750-entry retention match v0.5.30 so the existing admin log
 * can continue to consume entries written through the new architecture layer.
 */
final class LegacyOptionLogger implements Logger
{
    public const DEFAULT_OPTION = 'hangar18_manager_log';
    public const MAX_ENTRIES = 750;

    private string $optionName;

    public function __construct(string $optionName = self::DEFAULT_OPTION)
    {
        $this->optionName = trim($optionName) !== '' ? trim($optionName) : self::DEFAULT_OPTION;
    }

    public function log(string $level, string $checkpoint, string $message): void
    {
        $entries = get_option($this->optionName, []);
        if (!is_array($entries)) {
            $entries = [];
        }

        $user = wp_get_current_user();
        $entries[] = [
            'time' => current_time('mysql'),
            'level' => strtoupper($level),
            'checkpoint' => $checkpoint,
            'message' => $message,
            'user' => ($user && $user->exists()) ? $user->user_login : '',
        ];

        if (count($entries) > self::MAX_ENTRIES) {
            $entries = array_slice($entries, -self::MAX_ENTRIES);
        }

        update_option($this->optionName, $entries, false);
    }
}
