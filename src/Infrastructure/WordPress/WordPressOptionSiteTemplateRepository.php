<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use RuntimeException;

/**
 * Option-backed Site Builder template persistence, isolated from legacy pages/header.
 */
final class WordPressOptionSiteTemplateRepository implements SiteTemplateRepository
{
    public const TEMPLATES_OPTION = 'hangar18_manager_site_templates_v1';
    public const ASSIGNMENTS_OPTION = 'hangar18_manager_site_template_assignments_v1';
    private const MAX_TEMPLATES = 100;

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        $stored = get_option(self::TEMPLATES_OPTION, []);
        if (!is_array($stored)) {
            return [];
        }
        $result = [];
        foreach ($stored as $id => $template) {
            if (!is_array($template)) {
                continue;
            }
            $key = (string) ($template['Id'] ?? $id);
            if ($key !== '') {
                $result[$key] = $template;
            }
        }
        return $result;
    }

    /** @return array<string,mixed>|null */
    public function get(string $templateId): ?array
    {
        $all = $this->all();
        return $all[$templateId] ?? null;
    }

    /** @param array<string,mixed> $template @return array<string,mixed> */
    public function save(array $template): array
    {
        $id = (string) ($template['Id'] ?? '');
        if ($id === '') {
            throw new RuntimeException('Site template Id is required.');
        }
        $all = $this->all();
        if (!isset($all[$id]) && count($all) >= self::MAX_TEMPLATES) {
            throw new RuntimeException('Maximum number of Site Builder templates reached.');
        }
        $all[$id] = $template;
        update_option(self::TEMPLATES_OPTION, $all, false);
        return $template;
    }

    public function delete(string $templateId): void
    {
        $all = $this->all();
        if (!isset($all[$templateId])) {
            return;
        }
        foreach ($this->assignments() as $kind => $assignedId) {
            if ($assignedId === $templateId) {
                throw new RuntimeException("Template '{$templateId}' is globally assigned as {$kind}.");
            }
        }
        unset($all[$templateId]);
        update_option(self::TEMPLATES_OPTION, $all, false);
    }

    public function assignGlobal(string $kind, ?string $templateId): void
    {
        if (!in_array($kind, ['header', 'footer'], true)) {
            throw new RuntimeException('Unsupported global site template kind.');
        }
        $assignments = $this->assignments();
        if ($templateId === null || $templateId === '') {
            unset($assignments[$kind]);
        } else {
            if ($this->get($templateId) === null) {
                throw new RuntimeException("Site template '{$templateId}' does not exist.");
            }
            $assignments[$kind] = $templateId;
        }
        update_option(self::ASSIGNMENTS_OPTION, $assignments, false);
    }

    public function globalAssignment(string $kind): ?string
    {
        $assignments = $this->assignments();
        $id = (string) ($assignments[$kind] ?? '');
        return $id !== '' ? $id : null;
    }

    /** @return array<string,string> */
    private function assignments(): array
    {
        $stored = get_option(self::ASSIGNMENTS_OPTION, []);
        if (!is_array($stored)) {
            return [];
        }
        $result = [];
        foreach (['header', 'footer'] as $kind) {
            $id = (string) ($stored[$kind] ?? '');
            if ($id !== '') {
                $result[$kind] = $id;
            }
        }
        return $result;
    }
}
