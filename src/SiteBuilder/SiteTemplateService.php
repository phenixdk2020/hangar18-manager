<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use RuntimeException;

/**
 * Shared CRUD/assignment engine for Header and Footer templates.
 */
final class SiteTemplateService
{
    private SiteTemplateRepository $repository;
    private SiteTemplateValidator $validator;

    public function __construct(SiteTemplateRepository $repository, SiteTemplateValidator $validator)
    {
        $this->repository = $repository;
        $this->validator = $validator;
    }

    /** @param list<array<string,mixed>> $sections @return array<string,mixed> */
    public function create(string $kind, string $name, array $sections, ?string $templateId = null): array
    {
        $this->assertKind($kind);
        $id = $templateId !== null && trim($templateId) !== ''
            ? $this->normalizeId($templateId)
            : $kind . '-' . substr(hash('sha256', $name . '|' . microtime(true)), 0, 16);

        if ($this->repository->get($id) !== null) {
            throw new RuntimeException("Site template '{$id}' already exists.");
        }

        $template = [
            'SchemaVersion' => SiteTemplateValidator::SCHEMA_VERSION,
            'Id' => $id,
            'Kind' => $kind,
            'Name' => trim($name),
            'Revision' => 1,
            'UpdatedUtc' => gmdate('c'),
            'Sections' => array_values($sections),
        ];
        $this->validator->assertValid($template);
        return $this->repository->save($template);
    }

    /** @param list<array<string,mixed>> $sections @return array<string,mixed> */
    public function update(string $kind, string $templateId, string $name, array $sections): array
    {
        $this->assertKind($kind);
        $id = $this->normalizeId($templateId);
        $existing = $this->repository->get($id);
        if ($existing === null || ($existing['Kind'] ?? '') !== $kind) {
            throw new RuntimeException("{$kind} template '{$id}' was not found.");
        }

        $template = $existing;
        $template['Name'] = trim($name);
        $template['Revision'] = ((int) ($existing['Revision'] ?? 0)) + 1;
        $template['UpdatedUtc'] = gmdate('c');
        $template['Sections'] = array_values($sections);
        $this->validator->assertValid($template);
        return $this->repository->save($template);
    }

    public function assignGlobal(string $kind, string $templateId): void
    {
        $this->assertKind($kind);
        $id = $this->normalizeId($templateId);
        $template = $this->repository->get($id);
        if ($template === null || ($template['Kind'] ?? '') !== $kind) {
            throw new RuntimeException("{$kind} template '{$id}' was not found.");
        }
        $this->validator->assertValid($template);
        if (empty($template['Sections'])) {
            throw new RuntimeException('An empty site template cannot be assigned globally.');
        }
        $this->repository->assignGlobal($kind, $id);
    }

    public function clearGlobalAssignment(string $kind): void
    {
        $this->assertKind($kind);
        $this->repository->assignGlobal($kind, null);
    }

    /** @return array<string,mixed>|null */
    public function globalTemplate(string $kind): ?array
    {
        $this->assertKind($kind);
        $id = $this->repository->globalAssignment($kind);
        if ($id === null) {
            return null;
        }
        $template = $this->repository->get($id);
        if ($template === null || ($template['Kind'] ?? '') !== $kind) {
            return null;
        }
        $this->validator->assertValid($template);
        return $template;
    }

    /** @return array<string,array<string,mixed>> */
    public function all(string $kind): array
    {
        $this->assertKind($kind);
        return array_filter(
            $this->repository->all(),
            static fn(array $template): bool => ($template['Kind'] ?? '') === $kind
        );
    }

    private function assertKind(string $kind): void
    {
        if (!in_array($kind, [SiteTemplateValidator::KIND_HEADER, SiteTemplateValidator::KIND_FOOTER], true)) {
            throw new RuntimeException('Unsupported site template kind.');
        }
    }

    private function normalizeId(string $id): string
    {
        $id = strtolower(trim($id));
        $id = preg_replace('/[^a-z0-9_-]+/', '-', $id) ?? '';
        return trim($id, '-_');
    }
}
