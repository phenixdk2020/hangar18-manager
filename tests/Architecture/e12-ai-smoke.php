<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/FakeAiProvider.php';

use Hangar18\UltimateDesigner\AI\AccessibilitySuggestionAssistant;
use Hangar18\UltimateDesigner\AI\DesignReviewAssistant;
use Hangar18\UltimateDesigner\AI\PromptLayoutService;
use Hangar18\UltimateDesigner\AI\SuggestionGuard;
use Hangar18\UltimateDesigner\AI\TextAssistant;
use Hangar18\UltimateDesigner\Core\Version;
use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use Hangar18\UltimateDesigner\Permissions\RoleDefinitionCatalog;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use RuntimeException;

function e12Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$provider = new FakeAiProvider([
    'text_suggestion'=>['SuggestedText'=>'Ny forbedret tekst','Reason'=>'Kortere og tydeligere'],
    'layout_proposal'=>['State'=>[
        'Version'=>Version::PAGE_SCHEMA,'PageSlug'=>'ai-test','PageTitle'=>'AI test','ContentVersion'=>0,
        'DataContextType'=>'','DataContextEntryId'=>0,
        'Sections'=>[['Key'=>'hero','Type'=>'text','LayoutParentKey'=>'','Title'=>'AI layout']],
    ]],
    'design_review'=>['Suggestions'=>[
        ['ElementKey'=>'box','Property'=>'CustomBackgroundColor','SuggestedValue'=>'#ffffff','Reason'=>'Brug lysere surface'],
        ['ElementKey'=>'missing','Property'=>'Foo','SuggestedValue'=>'bar','Reason'=>'invalid element'],
    ]],
    'accessibility_text_suggestions'=>['Suggestions'=>[
        ['ElementKey'=>'photo','Property'=>'AltText','SuggestedValue'=>'Restaureret militærkøretøj på Aalborg Kaserne','Reason'=>'Beskriv billedets indhold'],
    ]],
]);

$text = (new TextAssistant($provider))->suggest('intro','Content','Gammel tekst','Gør teksten tydeligere');
e12Assert(($text['Status'] ?? '') === 'pending' && ($text['Before'] ?? '') === 'Gammel tekst' && ($text['After'] ?? '') === 'Ny forbedret tekst', 'Text assistant must return a pending proposal without mutating content.');
$guard = new SuggestionGuard();
$blocked = false;
try { $guard->accept($text,false); } catch (RuntimeException $e) { $blocked = true; }
e12Assert($blocked, 'AI proposal must not apply without explicit acceptance.');
$accepted = $guard->accept($text,true);
e12Assert(($accepted['Apply']['Value'] ?? '') === 'Ny forbedret tekst' && ($accepted['Undo']['Value'] ?? '') === 'Gammel tekst', 'Accepted AI proposal must carry reversible apply/undo data.');

$layout = (new PromptLayoutService($provider,new PageSchemaValidator()))->propose('Lav en enkel introsektion');
e12Assert($layout['Valid'] === true && $layout['PreviewAllowed'] === true && $layout['InsertAllowed'] === true, 'Valid AI layout must pass schema gate before preview/insert.');
$invalidProvider = new FakeAiProvider(['layout_proposal'=>['State'=>['Sections'=>[]]]]);
$invalidLayout = (new PromptLayoutService($invalidProvider,new PageSchemaValidator()))->propose('Ugyldig');
e12Assert($invalidLayout['Valid'] === false && $invalidLayout['InsertAllowed'] === false && count($invalidLayout['Errors']) > 0, 'Invalid AI layout must be blocked before insert.');

$designState = ['Sections'=>[['Key'=>'box','Type'=>'card','CustomBackgroundColor'=>'#111111','LayoutParentKey'=>'']]];
$designSuggestions = (new DesignReviewAssistant($provider))->review($designState);
e12Assert(count($designSuggestions) === 1 && ($designSuggestions[0]['ElementKey'] ?? '') === 'box' && ($designSuggestions[0]['Property'] ?? '') === 'CustomBackgroundColor', 'Design AI must link suggestion to a real element/property and discard invalid references.');
e12Assert(($designSuggestions[0]['Status'] ?? '') === 'pending', 'Design AI suggestion must require acceptance.');

$a11yState = ['Sections'=>[['Key'=>'photo','Type'=>'image','MediaId'=>12,'LayoutParentKey'=>'']]];
$a11ySuggestions = (new AccessibilitySuggestionAssistant($provider))->suggest($a11yState);
e12Assert(count($a11ySuggestions) === 1 && ($a11ySuggestions[0]['Property'] ?? '') === 'AltText', 'Accessibility AI must return an alt-text proposal for the concrete element.');
e12Assert(($a11ySuggestions[0]['Status'] ?? '') === 'pending', 'Accessibility suggestion must remain rejectable/pending.');

$caps = new CapabilityCatalog();
e12Assert($caps->forAction('ai.use') === CapabilityCatalog::USE_AI, 'AI features must have a dedicated named capability.');
$roles = (new RoleDefinitionCatalog())->definitions();
e12Assert(in_array(CapabilityCatalog::USE_AI,$roles['hangar18_designer']['Capabilities'],true), 'Designer recipe must explicitly grant AI capability.');
e12Assert(!in_array(CapabilityCatalog::USE_AI,$roles['hangar18_event_manager']['Capabilities'],true), 'Domain role must not receive AI privilege implicitly.');

fwrite(STDOUT, "E12 AI core UD-104..107: PASS\n");
