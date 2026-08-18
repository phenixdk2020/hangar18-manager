<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\AI\AiSettings;
use RuntimeException;

/** Stores only enabled/provider-id. Provider credentials remain outside WordPress options. */
final class WordPressOptionAiSettingsRepository
{
    public const OPTION='hangar18_ud_ai_settings_v1';
    private AiSettings $settings;
    public function __construct(?AiSettings $settings=null){$this->settings=$settings??new AiSettings();}
    /** @return array<string,mixed> */
    public function get(): array{$raw=get_option(self::OPTION,[]);return $this->settings->normalize(is_array($raw)?$raw:[]);}
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function save(array $raw): array{$value=$this->settings->normalize($raw);$ok=update_option(self::OPTION,$value,false);if($ok===false&&get_option(self::OPTION,[])!==$value){throw new RuntimeException('AI settings could not be persisted.');}return $value;}
}
