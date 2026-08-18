<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use RuntimeException;

/**
 * UD-061 application service for header templates.
 *
 * The service stores the same Sections tree used by the page editor and can
 * persist a global assignment. It does not replace the legacy shell renderer;
 * activation is intentionally deferred to the conversion/cutover phase.
 */
final class HeaderTemplateService
{
    private SiteTemplateRepository $repository;
    private SiteTemplateValidator $validator;

    public function __construct(SiteTemplateRepository $repository, SiteTemplateValidator $validator)
    {
        $this->repository = $repository;
        $this->validator = $validator;
    }

    /** @param list<array<string,mixed>> $sections @return array<string,mixed> */
    public function create(string $name, array $sections, ?string $templateId = null): array
    {
        $id = $templateId !== null && trim($templateId) !== ''
            ? $this->normalizeId($templateId)
            : 'header-' . substr(hash('sha256', $name . '|' . microtime(true)), 0, 16);

        if ($this->repository->get($id) !== null) {
            throw new RuntimeException("Header template '{$id}' already exists.");
        }

        $template = [
            'SchemaVersion' => SiteTemplateValidator::SCHEMA_VERSION,
            'Id' => $id,
            'Kind' => SiteTemplateValidator::KIND_HEADER,
            'Name' => trim($name),
            'Revision' => 1,
            'UpdatedUtc' => gmdate('c'),
            'Sections' => array_values($sections),
        ];
        $this->validator->assertValid($template);

        return $this->repository->save($template);
    }

    /** @param list<array<string,mixed>> $sections @return array<string,mixed> */
    public function update(string $templateId, string $name, array $sections): array
    {
        $id = $this->normalizeId($templateId);
        $existing = $this->repository->get($id);
        if ($existing === null || ($existing['Kind'] ?? '') !== SiteTemplateValidator::KIND_HEADER) {
            throw new RuntimeException("Header template '{$id}' was not found.");
        }

        $template = $existing;
        $template['Name'] = trim($name);
        $template['Revision'] = ((int) ($existing['Revision'] ?? 0)) + 1;
        $template['UpdatedUtc'] = gmdate('c');
        $template['Sections'] = array_values($sections);
        $this->validator->assertValid($template);

        return $this->repository->save($template);
    }

    public function assignGlobal(string $templateId): void
    {
        $id = $this->normalizeId($templateId);
        $template = $this->repository->get($id);
        if ($template === null || ($template['Kind'] ?? '') !== SiteTemplateValidator::KIND_HEADER) {
            throw new RuntimeException("Header template '{$id}' was not found.");
        }
        $this->validator->assertValid($template);
        if (empty($template['Sections'])) {
            throw new RuntimeException('An empty header template cannot be assigned globally.');
        }

        $this->repository->assignGlobal(SiteTemplateValidator::KIND_HEADER, $id);
    }

    public function clearGlobalAssignment(): void
    {
        $this->repository->assignGlobal(SiteTemplateValidator::KIND_HEADER, null);
    }

    /** @return array<string,mixed>|null */
    public function globalHeader(): ?array
    {
        $id = $this->repository->globalAssignment(SiteTemplateValidator::KIND_HEADER);
        if ($id === null) {
            return null;
        }

        $template = $this->repository->get($id);
        if ($template === null || ($template['Kind'] ?? '') !== SiteTemplateValidator::KIND_HEADER) {
            return null;
        }
        $this->validator->assertValid($template);

        return $template;
    }

    /** @return array<string,array<string,mixed>> */
    public function all(): array
    {
        return array_filter(
            $this->repository->all(),
            static fn(array $template): bool => ($template['Kind'] ?? '') === SiteTemplateValidator::KIND_HEADER
        );
    }

    private function normalizeId(string $id): string
    {
        $id = strtolower(trim($id));
        $id = preg_replace('/[^a-z0-9_-]+/', '-', $id) ?? '';
        return trim($id, '-_');
    }
}
