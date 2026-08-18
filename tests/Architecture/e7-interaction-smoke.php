<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Contracts\InteractionActionHandler;
use Hangar18\UltimateDesigner\Contracts\Logger;
use Hangar18\UltimateDesigner\Interaction\ActionChainEngine;
use Hangar18\UltimateDesigner\Interaction\ClientActionDefinition;
use Hangar18\UltimateDesigner\Interaction\FormDefinitionValidator;
use Hangar18\UltimateDesigner\Interaction\FormRenderer;
use Hangar18\UltimateDesigner\Interaction\FormSubmissionService;
use Hangar18\UltimateDesigner\Interaction\FormSubmissionValidator;
use Hangar18\UltimateDesigner\Interaction\ModalDefinitionValidator;
use Hangar18\UltimateDesigner\Interaction\ModalRenderer;
use Hangar18\UltimateDesigner\Interaction\PopupTriggerValidator;
use Hangar18\UltimateDesigner\Interaction\RedirectActionHandler;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use RuntimeException;

function e7Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$form = [
    'SchemaVersion'=>'1.0','Id'=>'contact-form','SubmitLabel'=>'Send','Fields'=>[
        ['Key'=>'name','Type'=>'text','Label'=>'Navn','Validation'=>['Required'=>true,'MinLength'=>2]],
        ['Key'=>'email','Type'=>'email','Label'=>'E-mail','Validation'=>['Required'=>true]],
        ['Key'=>'topic','Type'=>'select','Label'=>'Emne','Options'=>[['Value'=>'a','Label'=>'A'],['Value'=>'b','Label'=>'B']],'Validation'=>['Required'=>true]],
        ['Key'=>'message','Type'=>'textarea','Label'=>'Besked','Validation'=>['Required'=>true,'MaxLength'=>500]],
    ],
    'Actions'=>[['Type'=>'redirect','Config'=>['Url'=>'/tak']]],
];
$definition = new FormDefinitionValidator();
e7Assert($definition->validate($form) === [], 'Valid form definition must pass.');
$html = (new FormRenderer($definition))->render($form, '/submit');
e7Assert(str_contains($html, '<form') && str_contains($html, 'aria-live="polite"'), 'Form renderer must expose semantic form and live status.');
e7Assert(str_contains($html, 'for="h18-contact-form-email"'), 'Form labels must be associated with controls.');

$submission = new FormSubmissionValidator($definition);
$bad = $submission->validate($form, ['name'=>'A','email'=>'bad','topic'=>'z','message'=>'']);
e7Assert(!$bad['valid'], 'Invalid submission must be rejected.');
e7Assert(isset($bad['errors']['name'],$bad['errors']['email'],$bad['errors']['topic'],$bad['errors']['message']), 'Validation errors must be field-scoped.');
$good = $submission->validate($form, ['name'=>'Allan','email'=>'allan@example.test','topic'=>'a','message'=>'Hej']);
e7Assert($good['valid'], 'Valid submission must pass server validation.');

$logger = new class implements Logger {
    public array $entries=[];
    public function log(string $level,string $checkpoint,string $message): void { $this->entries[]=[$level,$checkpoint,$message]; }
};
$redirect = new RedirectActionHandler();
$chain = new ActionChainEngine([$redirect], $logger);
$service = new FormSubmissionService($submission, $chain);
$result = $service->submit($form, ['name'=>'Allan','email'=>'allan@example.test','topic'=>'a','message'=>'Hej']);
e7Assert($result['success'] && ($result['actions'][0]['data']['redirect_url'] ?? '') === '/tak', 'Valid form must execute ordered submit action.');
e7Assert(!$redirect->execute(['Url'=>'javascript:alert(1)'],[])['success'], 'Unsafe redirect scheme must be rejected.');

$failHandler = new class implements InteractionActionHandler {
    public function type(): string { return 'fail'; }
    public function execute(array $config,array $context): array { return ['success'=>false,'message'=>'failed']; }
};
$okHandler = new class implements InteractionActionHandler {
    public function type(): string { return 'ok'; }
    public function execute(array $config,array $context): array { return ['success'=>true,'message'=>'ok']; }
};
$chain2 = new ActionChainEngine([$failHandler,$okHandler],$logger);
$stopped = $chain2->execute([['Type'=>'fail'],['Type'=>'ok']],[]);
e7Assert(!$stopped['success'] && count($stopped['results'])===1, 'Action chain must stop on failure by default.');
$continued = $chain2->execute([['Type'=>'fail','OnError'=>'continue'],['Type'=>'ok']],[]);
e7Assert($continued['success'] && count($continued['results'])===2, 'Action chain must support explicit continue-on-error.');

$modal = [
    'SchemaVersion'=>'1.0','Id'=>'contact-modal','Title'=>'Kontakt','Revision'=>1,
    'TrapFocus'=>true,'CloseOnEscape'=>true,
    'Sections'=>[['Key'=>'modal-root','Type'=>'container','LayoutParentKey'=>''],['Key'=>'modal-text','Type'=>'text','LayoutParentKey'=>'modal-root']],
];
$modalValidator = new ModalDefinitionValidator(new PageSchemaValidator());
e7Assert($modalValidator->validate($modal) === [], 'Valid shared-tree modal must pass.');
$modalHtml = (new ModalRenderer())->render($modal,'<p>Hej</p>');
e7Assert(str_contains($modalHtml,'role="dialog"') && str_contains($modalHtml,'aria-modal="true"'), 'Modal renderer must expose ARIA dialog semantics.');

$triggers = ['Mode'=>'ALL','Triggers'=>[
    ['Type'=>'time','DelayMs'=>1000],
    ['Type'=>'scroll','Percent'=>50],
    ['Type'=>'context','Key'=>'datatype','Operator'=>'equals','Value'=>'event'],
]];
e7Assert((new PopupTriggerValidator())->validate($triggers) === [], 'Valid popup triggers must pass.');
e7Assert((new PopupTriggerValidator())->validate(['Mode'=>'ANY','Triggers'=>[['Type'=>'scroll','Percent'=>101]]]) !== [], 'Invalid scroll trigger must fail.');

$client = new ClientActionDefinition();
$actions = [['Type'=>'scroll','TargetId'=>'kontakt'],['Type'=>'open-modal','TargetId'=>'contact-modal'],['Type'=>'navigate','Url'=>'/tak']];
e7Assert($client->validate($actions) === [], 'Valid client action chain must pass.');
e7Assert($client->validate([['Type'=>'navigate','Url'=>'javascript:alert(1)']]) !== [], 'Unsafe client navigation must fail.');
e7Assert(str_contains($client->dataAttribute($actions),'open-modal'), 'Client actions must serialize to safe data attribute JSON.');

fwrite(STDOUT,"E7 Interaction core UD-074..080: PASS\n");
