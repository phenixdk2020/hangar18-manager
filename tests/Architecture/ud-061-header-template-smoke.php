<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';

\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\SiteBuilder\HeaderTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateValidator;
use RuntimeException;

function ud061Assert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$repository = new class implements SiteTemplateRepository {
    /** @var array<string,array<string,mixed>> */
    private array $templates = [];
    /** @var array<string,string> */
    private array $assignments = [];

    public function all(): array { return $this->templates; }
    public function get(string $templateId): ?array { return $this->templates[$templateId] ?? null; }
    public function save(array $template): array { $this->templates[(string) $template['Id']] = $template; return $template; }
    public function delete(string $templateId): void { unset($this->templates[$templateId]); }
    public function assignGlobal(string $kind, ?string $templateId): void {
        if ($templateId === null) { unset($this->assignments[$kind]); return; }
        $this->assignments[$kind] = $templateId;
    }
    public function globalAssignment(string $kind): ?string { return $this->assignments[$kind] ?? null; }
};

$validator = new SiteTemplateValidator(new PageSchemaValidator());
$service = new HeaderTemplateService($repository, $validator);

$sections = [
    [
        'Key' => 'header-container',
        'Type' => 'container',
        'LayoutParentKey' => '',
    ],
    [
        'Key' => 'header-title',
        'Type' => 'text',
        'LayoutParentKey' => 'header-container',
        'Title' => 'Hangar18',
    ],
];

$created = $service->create('Global header', $sections, 'header-main');
ud061Assert($created['Kind'] === 'header', 'Header template kind must be header.');
ud061Assert($created['Revision'] === 1, 'New header template must start at revision 1.');
ud061Assert($created['Sections'] === $sections, 'Header template must preserve the page editor Sections tree.');

$service->assignGlobal('header-main');
$global = $service->globalHeader();
ud061Assert($global !== null && $global['Id'] === 'header-main', 'Global header assignment must resolve the saved template.');

$updatedSections = $sections;
$updatedSections[] = [
    'Key' => 'header-cta',
    'Type' => 'buttons',
    'LayoutParentKey' => 'header-container',
];
$updated = $service->update('header-main', 'Global header v2', $updatedSections);
ud061Assert($updated['Revision'] === 2, 'Header update must increment revision.');
ud061Assert(count($updated['Sections']) === 3, 'Header update must preserve new element tree content.');

$empty = $service->create('Empty draft', [], 'header-empty');
ud061Assert($empty['Sections'] === [], 'Empty header draft may be stored before it is ready.');
$emptyRejected = false;
try {
    $service->assignGlobal('header-empty');
} catch (RuntimeException $exception) {
    $emptyRejected = true;
}
ud061Assert($emptyRejected, 'Empty header template must not be globally assignable.');

$invalidRejected = false;
try {
    $service->create('Invalid nesting', [[
        'Key' => 'bad-child',
        'Type' => 'text',
        'LayoutParentKey' => 'missing-parent',
    ]], 'header-invalid');
} catch (RuntimeException $exception) {
    $invalidRejected = true;
}
ud061Assert($invalidRejected, 'Header template must be rejected when its shared page element tree is invalid.');

$service->clearGlobalAssignment();
ud061Assert($service->globalHeader() === null, 'Global header assignment must be clearable.');

fwrite(STDOUT, "UD-061 header template builder foundation: PASS\n");
