<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Compatibility\CompatibilityPolicy;
use Hangar18\UltimateDesigner\Compatibility\ProtectedDomainContractCatalog;
use Hangar18\UltimateDesigner\DynamicData\StarterSchemaPresetCatalog;
use Hangar18\UltimateDesigner\DynamicData\StarterSchemaPresetValidator;

function ud060Assert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new \RuntimeException($message);
    }
}

$presets = StarterSchemaPresetCatalog::all();
$validator = new StarterSchemaPresetValidator();
$validator->assertCatalogValid($presets);

ud060Assert(array_keys($presets) === ['vehicle', 'event', 'gallery'], 'UD-060 must expose exactly three starter presets.');
ud060Assert(array_keys($presets) === CompatibilityPolicy::PROTECTED_DOMAINS, 'Starter presets must match protected legacy domains exactly.');

foreach ($presets as $domain => $preset) {
    $schema = StarterSchemaPresetCatalog::installableSchema($domain);
    ud060Assert($schema['Key'] === $domain, "Preset '{$domain}' schema key mismatch.");
    ud060Assert($schema['SchemaVersion'] === 2, "Preset '{$domain}' must target generic schema v2.");
    ud060Assert($preset['LegacyCompatibility']['ParentSlug'] === ProtectedDomainContractCatalog::slug($domain), "Preset '{$domain}' legacy slug mismatch.");
    ud060Assert($preset['LegacyCompatibility']['Marker'] === ProtectedDomainContractCatalog::marker($domain), "Preset '{$domain}' legacy marker mismatch.");
    ud060Assert($preset['EntryTitle']['Required'] === true, "Preset '{$domain}' must preserve required entry title semantics.");
}

$fieldMap = static function (array $schema): array {
    $map = [];
    foreach ($schema['Fields'] as $field) {
        $map[$field['Key']] = $field;
    }
    return $map;
};

$vehicle = $fieldMap(StarterSchemaPresetCatalog::installableSchema('vehicle'));
foreach (['description','image','manufacturer','model','year','engine','weight','color','active'] as $requiredDesignField) {
    ud060Assert(isset($vehicle[$requiredDesignField]), "Vehicle preset is missing design field '{$requiredDesignField}'.");
}
ud060Assert($vehicle['image']['Type'] === 'media', 'Vehicle image must use generic media field.');
ud060Assert($vehicle['year']['Type'] === 'number', 'Vehicle year must use generic number field.');
ud060Assert($vehicle['active']['Type'] === 'bool', 'Vehicle active must use generic bool field.');
foreach (['type','crew','service_period','restoration_status','history','aalborg_service','restoration_text','technical_source_url'] as $legacyCoverageField) {
    ud060Assert(isset($vehicle[$legacyCoverageField]), "Vehicle preset is missing legacy-coverage field '{$legacyCoverageField}'.");
}

$event = $fieldMap(StarterSchemaPresetCatalog::installableSchema('event'));
foreach (['short_description','event_date','start_time','end_time','venue','address','contact','description','program','practical','image','gallery_album'] as $eventField) {
    ud060Assert(isset($event[$eventField]), "Event preset is missing legacy field '{$eventField}'.");
}
ud060Assert($event['event_date']['Type'] === 'date' && $event['event_date']['Required'] === true, 'Event date must be a required generic date field.');
ud060Assert($event['image']['Type'] === 'media', 'Event image must use generic media field.');
ud060Assert($event['gallery_album']['Type'] === 'relation', 'Event gallery link must use generic relation field.');
ud060Assert($event['gallery_album']['RelationTargetType'] === 'gallery', 'Event gallery relation must target gallery preset.');
ud060Assert(in_array('gallery_album', $presets['event']['LegacyCompatibility']['RelationRemapRequired'], true), 'Legacy Event album page ID must be explicitly marked for relation remap.');

$gallery = $fieldMap(StarterSchemaPresetCatalog::installableSchema('gallery'));
ud060Assert($gallery['cover_image']['Type'] === 'media', 'Gallery cover must use generic media field.');
ud060Assert($gallery['items']['Type'] === 'repeater', 'Gallery images must use generic repeater field.');
ud060Assert($gallery['items']['RepeaterMaxItems'] === 20, 'Gallery repeater must stay within current generic engine limit.');
$nestedMap = [];
foreach ($gallery['items']['NestedFields'] as $nested) {
    $nestedMap[$nested['Key']] = $nested;
}
ud060Assert(isset($nestedMap['image']) && $nestedMap['image']['Type'] === 'media' && $nestedMap['image']['Required'] === true, 'Gallery item image must be required media.');
ud060Assert(isset($nestedMap['title']) && $nestedMap['title']['Type'] === 'text', 'Gallery item title must be text.');
ud060Assert(isset($nestedMap['description']) && $nestedMap['description']['Type'] === 'text', 'Gallery item description must be text.');

// Presets are definitions only: this test intentionally performs no WordPress mutation.
fwrite(STDOUT, "UD-060 starter schema presets: PASS\n");
