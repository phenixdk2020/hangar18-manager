<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Permissions\DesignLockSettings;
use RuntimeException;

final class WordPressOptionDesignLockRepository
{
    public const OPTION='hangar18_ud_design_lock_v1';
    private DesignLockSettings $settings;
    public function __construct(?DesignLockSettings $settings=null){$this->settings=$settings??new DesignLockSettings();}
    /** @return array<string,mixed> */
    public function get(): array{$raw=get_option(self::OPTION,[]);return $this->settings->normalize(is_array($raw)?$raw:[]);}
    /** @param array<string,mixed> $raw @return array<string,mixed> */
    public function save(array $raw): array{$value=$this->settings->normalize($raw);$ok=update_option(self::OPTION,$value,false);if($ok===false&&get_option(self::OPTION,[])!==$value){throw new RuntimeException('Design Lock settings could not be persisted.');}return $value;}
}
