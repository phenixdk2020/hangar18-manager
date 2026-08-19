<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use RuntimeException;

/**
 * Controlled I2A import from the authoritative legacy shell snapshot into
 * isolated Site Builder shadow templates.
 *
 * This service never assigns templates globally and never writes pages. Template
 * IDs are derived from the immutable source hash so an unchanged baseline is
 * idempotent while a changed baseline creates a new comparison pair.
 */
final class LegacyShellShadowImportService
{
    private SiteTemplateRepository $repository;
    private SiteTemplateValidator $validator;

    public function __construct(SiteTemplateRepository $repository, SiteTemplateValidator $validator)
    {
        $this->repository = $repository;
        $this->validator = $validator;
    }

    /** @param array<string,mixed> $snapshot @return array<string,mixed> */
    public function plan(array $snapshot): array
    {
        $hash = $this->sourceHash($snapshot);
        $ready = !empty($snapshot['ReadyForShadowImport']);
        $suffix = substr($hash, 0, 12);
        $headerId = 'legacy-header-' . $suffix;
        $footerId = 'legacy-footer-' . $suffix;
        $header = $this->repository->get($headerId);
        $footer = $this->repository->get($footerId);

        $conflicts = [];
        if ($header !== null && !$this->matchesImport($header, 'header', $hash)) {
            $conflicts[] = "Template '{$headerId}' findes allerede med en anden oprindelse.";
        }
        if ($footer !== null && !$this->matchesImport($footer, 'footer', $hash)) {
            $conflicts[] = "Template '{$footerId}' findes allerede med en anden oprindelse.";
        }

        $headerImported = $header !== null && $this->matchesImport($header, 'header', $hash);
        $footerImported = $footer !== null && $this->matchesImport($footer, 'footer', $hash);

        return [
            'Ready' => $ready && $conflicts === [],
            'SourceHash' => $hash,
            'HeaderTemplateId' => $headerId,
            'FooterTemplateId' => $footerId,
            'HeaderImported' => $headerImported,
            'FooterImported' => $footerImported,
            'AlreadyImported' => $headerImported && $footerImported,
            'Conflicts' => $conflicts,
            'GlobalHeaderBefore' => $this->repository->globalAssignment('header'),
            'GlobalFooterBefore' => $this->repository->globalAssignment('footer'),
            'PublicMutationAvailable' => false,
        ];
    }

    /**
     * @param array<string,mixed> $snapshot
     * @return array<string,mixed>
     */
    public function import(array $snapshot): array
    {
        $plan = $this->plan($snapshot);
        if (empty($snapshot['ReadyForShadowImport'])) {
            throw new RuntimeException('Legacy Header/Footer baseline er ikke komplet. Shadow-import er blokeret.');
        }
        if (!empty($plan['Conflicts'])) {
            throw new RuntimeException(implode(' ', (array) $plan['Conflicts']));
        }
        if (!empty($plan['AlreadyImported'])) {
            return $plan + ['Created' => [], 'Idempotent' => true];
        }

        $hash = (string) $plan['SourceHash'];
        $headerId = (string) $plan['HeaderTemplateId'];
        $footerId = (string) $plan['FooterTemplateId'];
        $created = [];

        $headerTemplate = $this->buildTemplate('header', $headerId, (string) ($snapshot['HeaderHtml'] ?? ''), $snapshot);
        $footerTemplate = $this->buildTemplate('footer', $footerId, (string) ($snapshot['FooterHtml'] ?? ''), $snapshot);
        $this->validator->assertValid($headerTemplate);
        $this->validator->assertValid($footerTemplate);

        try {
            if (empty($plan['HeaderImported'])) {
                $this->repository->save($headerTemplate);
                $created[] = $headerId;
            }
            if (empty($plan['FooterImported'])) {
                $this->repository->save($footerTemplate);
                $created[] = $footerId;
            }
        } catch (\Throwable $error) {
            foreach (array_reverse($created) as $templateId) {
                try {
                    $this->repository->delete($templateId);
                } catch (\Throwable $rollbackError) {
                    // Best-effort rollback of shadow-only writes. Preserve the original error.
                }
            }
            throw $error;
        }

        if ($this->repository->globalAssignment('header') !== ($plan['GlobalHeaderBefore'] ?? null)
            || $this->repository->globalAssignment('footer') !== ($plan['GlobalFooterBefore'] ?? null)) {
            foreach (array_reverse($created) as $templateId) {
                try {
                    $this->repository->delete($templateId);
                } catch (\Throwable $rollbackError) {
                    // Best effort only; this guard should never trigger with the repository contract.
                }
            }
            throw new RuntimeException('Shadow-import forsøgte at ændre global Header/Footer assignment og blev rullet tilbage.');
        }

        $after = $this->plan($snapshot);
        if (empty($after['AlreadyImported'])) {
            throw new RuntimeException('Shadow-import kunne ikke verificeres efter write.');
        }

        return $after + ['Created' => $created, 'Idempotent' => false, 'ImportedSourceHash' => $hash];
    }

    /** @param array<string,mixed> $snapshot @return array<string,mixed> */
    private function buildTemplate(string $kind, string $id, string $html, array $snapshot): array
    {
        $label = $kind === 'header' ? 'Header' : 'Footer';
        $sourceTitle = trim((string) ($snapshot['SourcePostTitle'] ?? ''));
        $name = 'Legacy ' . $label . ' baseline' . ($sourceTitle !== '' ? ' · ' . $sourceTitle : '');
        $rootKey = 'legacy-' . $kind . '-root';
        $contentKey = 'legacy-' . $kind . '-content';

        return [
            'SchemaVersion' => SiteTemplateValidator::SCHEMA_VERSION,
            'Id' => $id,
            'Kind' => $kind,
            'Name' => $name,
            'Revision' => 1,
            'UpdatedUtc' => gmdate('c'),
            'Sections' => [
                $this->sectionDefaults($rootKey, 'container', '', ''),
                $this->sectionDefaults($contentKey, 'text', $rootKey, $html),
            ],
            'LegacyShadowImport' => true,
            'LegacyImportMode' => 'shadow-only',
            'LegacySourceHash' => (string) ($snapshot['SourceHash'] ?? ''),
            'LegacySourceKind' => $kind,
            'LegacySourcePostId' => (int) ($snapshot['SourcePostId'] ?? 0),
            'LegacySourcePostTitle' => (string) ($snapshot['SourcePostTitle'] ?? ''),
            'LegacyRuntimeVersion' => (string) ($snapshot['RuntimeVersion'] ?? ''),
            'LegacyHeaderOption' => (string) ($snapshot['HeaderOption'] ?? ''),
            'LegacySourceBytes' => strlen($html),
            'LegacyImportedUtc' => gmdate('c'),
        ];
    }

    /** @return array<string,mixed> */
    private function sectionDefaults(string $key, string $type, string $parentKey, string $content): array
    {
        return [
            'Key' => $key,
            'Type' => $type,
            'LayoutParentKey' => $parentKey,
            'Title' => '',
            'Content' => $content,
            'DesignMode' => 'Global',
            'SectionBodyFontFamily' => 'Global',
            'SectionHeadingFontFamily' => 'Global',
            'BodyFontSizePx' => 0,
            'H1FontSizePx' => 0,
            'H2FontSizePx' => 0,
            'H3FontSizePx' => 0,
            'DesktopAlignment' => 'Left',
            'CustomBackgroundColor' => '#ffffff',
            'CustomTextColor' => '#30382a',
            'CustomHeadingColor' => '#30382a',
            'PaddingPx' => 0,
        ];
    }

    /** @param array<string,mixed> $template */
    private function matchesImport(array $template, string $kind, string $hash): bool
    {
        return !empty($template['LegacyShadowImport'])
            && (string) ($template['LegacyImportMode'] ?? '') === 'shadow-only'
            && (string) ($template['Kind'] ?? '') === $kind
            && hash_equals($hash, (string) ($template['LegacySourceHash'] ?? ''));
    }

    /** @param array<string,mixed> $snapshot */
    private function sourceHash(array $snapshot): string
    {
        $hash = strtolower(trim((string) ($snapshot['SourceHash'] ?? '')));
        if (!preg_match('/^[a-f0-9]{64}$/', $hash)) {
            throw new RuntimeException('Legacy shell snapshot mangler en gyldig SourceHash.');
        }
        return $hash;
    }
}
