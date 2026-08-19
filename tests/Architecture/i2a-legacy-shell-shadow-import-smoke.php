<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\SiteBuilder\LegacyShellShadowImportService;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateValidator;
use RuntimeException;

function i2aAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$repo = new class implements SiteTemplateRepository {
    public array $templates = [];
    public array $assignments = ['header' => 'current-header', 'footer' => 'current-footer'];
    public function all(): array { return $this->templates; }
    public function get(string $templateId): ?array { return $this->templates[$templateId] ?? null; }
    public function save(array $template): array { $this->templates[(string) $template['Id']] = $template; return $template; }
    public function delete(string $templateId): void { unset($this->templates[$templateId]); }
    public function assignGlobal(string $kind, ?string $templateId): void { if ($templateId === null) unset($this->assignments[$kind]); else $this->assignments[$kind] = $templateId; }
    public function globalAssignment(string $kind): ?string { return $this->assignments[$kind] ?? null; }
};

$service = new LegacyShellShadowImportService(
    $repo,
    new SiteTemplateValidator(new PageSchemaValidator())
);

$snapshot = [
    'ReadyForShadowImport' => true,
    'SourceHash' => str_repeat('a', 64),
    'SourcePostId' => 9,
    'SourcePostTitle' => 'Hjem',
    'RuntimeVersion' => '0.8.10',
    'HeaderOption' => 'hangar18_manager_header_design_v25',
    'HeaderHtml' => '<header><strong>Legacy header</strong></header>',
    'FooterHtml' => '<footer>Legacy footer</footer>',
];

$plan = $service->plan($snapshot);
i2aAssert(($plan['Ready'] ?? false) === true, 'Complete legacy snapshot must be ready for shadow import.');
i2aAssert(($plan['AlreadyImported'] ?? true) === false, 'Fresh source hash must not be reported as imported.');
i2aAssert(($plan['PublicMutationAvailable'] ?? true) === false, 'I2A must never expose public mutation.');
i2aAssert(($plan['HeaderTemplateId'] ?? '') === 'legacy-header-aaaaaaaaaaaa', 'Header shadow id must be source-hash bound.');
i2aAssert(($plan['FooterTemplateId'] ?? '') === 'legacy-footer-aaaaaaaaaaaa', 'Footer shadow id must be source-hash bound.');

$result = $service->import($snapshot);
i2aAssert(($result['AlreadyImported'] ?? false) === true, 'Imported baseline pair must verify as imported.');
i2aAssert(count((array) ($result['Created'] ?? [])) === 2, 'First import must create exactly Header and Footer shadow templates.');
i2aAssert(count($repo->templates) === 2, 'Exactly two templates must exist after first import.');
i2aAssert(($repo->assignments['header'] ?? '') === 'current-header', 'Header assignment must remain unchanged.');
i2aAssert(($repo->assignments['footer'] ?? '') === 'current-footer', 'Footer assignment must remain unchanged.');

$header = $repo->templates['legacy-header-aaaaaaaaaaaa'] ?? [];
$footer = $repo->templates['legacy-footer-aaaaaaaaaaaa'] ?? [];
i2aAssert(($header['LegacyImportMode'] ?? '') === 'shadow-only', 'Imported Header must be marked shadow-only.');
i2aAssert(($footer['LegacyImportMode'] ?? '') === 'shadow-only', 'Imported Footer must be marked shadow-only.');
i2aAssert(($header['LegacySourceHash'] ?? '') === str_repeat('a', 64), 'Imported Header must retain exact source hash.');
i2aAssert(($header['Sections'][1]['Content'] ?? '') === $snapshot['HeaderHtml'], 'Imported Header must preserve baseline HTML in the editable shadow section.');

$idempotent = $service->import($snapshot);
i2aAssert(($idempotent['Idempotent'] ?? false) === true, 'Re-importing the same source hash must be idempotent.');
i2aAssert(count((array) ($idempotent['Created'] ?? [])) === 0, 'Idempotent import must not create new templates.');
i2aAssert(count($repo->templates) === 2, 'Idempotent import must not duplicate templates.');

$changed = $snapshot;
$changed['SourceHash'] = str_repeat('b', 64);
$changed['HeaderHtml'] = '<header>Changed legacy header</header>';
$changedResult = $service->import($changed);
i2aAssert(count((array) ($changedResult['Created'] ?? [])) === 2, 'Changed source hash must create a new comparison pair.');
i2aAssert(count($repo->templates) === 4, 'Changed source must preserve the previous imported baseline.');
i2aAssert(isset($repo->templates['legacy-header-bbbbbbbbbbbb']), 'Changed Header baseline must use a new hash-bound id.');
i2aAssert(isset($repo->templates['legacy-footer-bbbbbbbbbbbb']), 'Changed Footer baseline must use a new hash-bound id.');
i2aAssert(($repo->assignments['header'] ?? '') === 'current-header' && ($repo->assignments['footer'] ?? '') === 'current-footer', 'Assignments must remain untouched after changed-baseline import.');

$conflictRepo = new class implements SiteTemplateRepository {
    public array $templates = ['legacy-header-cccccccccccc' => ['Id'=>'legacy-header-cccccccccccc','Kind'=>'header','LegacySourceHash'=>'other']];
    public function all(): array { return $this->templates; }
    public function get(string $templateId): ?array { return $this->templates[$templateId] ?? null; }
    public function save(array $template): array { $this->templates[(string) $template['Id']] = $template; return $template; }
    public function delete(string $templateId): void { unset($this->templates[$templateId]); }
    public function assignGlobal(string $kind, ?string $templateId): void {}
    public function globalAssignment(string $kind): ?string { return null; }
};
$conflictService = new LegacyShellShadowImportService($conflictRepo, new SiteTemplateValidator(new PageSchemaValidator()));
$conflictSnapshot = $snapshot;
$conflictSnapshot['SourceHash'] = str_repeat('c', 64);
$conflictRejected = false;
try {
    $conflictService->import($conflictSnapshot);
} catch (RuntimeException $exception) {
    $conflictRejected = true;
}
i2aAssert($conflictRejected, 'Hash-bound id collision with a foreign template must be rejected instead of overwritten.');

fwrite(STDOUT, "I2A legacy Header/Footer shadow import: PASS\n");
