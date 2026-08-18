<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

/** UD-061 facade for header templates. */
final class HeaderTemplateService
{
    private SiteTemplateService $templates;

    public function __construct(SiteTemplateService $templates)
    {
        $this->templates = $templates;
    }

    /** @param list<array<string,mixed>> $sections @return array<string,mixed> */
    public function create(string $name, array $sections, ?string $templateId = null): array
    {
        return $this->templates->create(SiteTemplateValidator::KIND_HEADER, $name, $sections, $templateId);
    }

    /** @param list<array<string,mixed>> $sections @return array<string,mixed> */
    public function update(string $templateId, string $name, array $sections): array
    {
        return $this->templates->update(SiteTemplateValidator::KIND_HEADER, $templateId, $name, $sections);
    }

    public function assignGlobal(string $templateId): void
    {
        $this->templates->assignGlobal(SiteTemplateValidator::KIND_HEADER, $templateId);
    }

    public function clearGlobalAssignment(): void
    {
        $this->templates->clearGlobalAssignment(SiteTemplateValidator::KIND_HEADER);
    }

    /** @return array<string,mixed>|null */
    public function globalHeader(): ?array
    {
        return $this->templates->globalTemplate(SiteTemplateValidator::KIND_HEADER);
    }

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        return $this->templates->all(SiteTemplateValidator::KIND_HEADER);
    }
}
