<?php

declare(strict_types=1);

$h18AiOptions=[];
function get_option(string $key,$default=false){global $h18AiOptions;return $h18AiOptions[$key]??$default;}
function update_option(string $key,$value,$autoload=null): bool{global $h18AiOptions;$h18AiOptions[$key]=$value;return true;}

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__.'/FakeAiProvider.php';

use Hangar18\UltimateDesigner\AI\AiProposalTokenService;
use Hangar18\UltimateDesigner\AI\AiProviderRegistry;
use Hangar18\UltimateDesigner\AI\SuggestionGuard;
use Hangar18\UltimateDesigner\AI\TextAssistant;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAiProposalRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAiSettingsRepository;
use RuntimeException;

function i8Assert(bool $condition,string $message): void{if(!$condition){throw new RuntimeException($message);}}

$provider=new FakeAiProvider(['text_suggestion'=>['SuggestedText'=>'Forbedret tekst','Reason'=>'Mere tydelig']]);
$registry=new AiProviderRegistry();$registry->register('fake','Fake provider',$provider);
i8Assert($registry->has('fake')&&$registry->get('fake')===$provider,'Provider registry must resolve registered provider instances.');

$settingsRepo=new WordPressOptionAiSettingsRepository();
$saved=$settingsRepo->save(['Enabled'=>true,'ProviderId'=>'fake','api_key'=>'SHOULD-NOT-BE-STORED','secret'=>'NOPE']);
i8Assert(($saved['Enabled']??false)===true&&($saved['ProviderId']??'')==='fake','AI settings must preserve enabled/provider ID.');
$stored=$h18AiOptions[WordPressOptionAiSettingsRepository::OPTION]??[];
i8Assert(!array_key_exists('api_key',$stored)&&!array_key_exists('secret',$stored),'AI settings option must not persist credential-like extra fields.');

$proposal=(new TextAssistant($registry->get('fake')))->suggest('intro','Content','Gammel tekst','Gør teksten bedre');
i8Assert(($proposal['Status']??'')==='pending','Provider output must remain pending.');
$tokenService=new AiProposalTokenService(str_repeat('x',64));$issued=$tokenService->issue($proposal,600);
i8Assert($tokenService->verify($issued['token'],$proposal),'Proposal token must verify exact proposal.');
$tampered=$proposal;$tampered['After']='Manipuleret';
i8Assert(!$tokenService->verify($issued['token'],$tampered),'Proposal token must reject modified proposal.');

$proposal['Token']=$issued['token'];$proposal['TokenExpires']=$issued['expires'];$repo=new WordPressOptionAiProposalRepository();$repo->save($proposal);
$loaded=$repo->get((string)$proposal['Id']);i8Assert(is_array($loaded)&&($loaded['Status']??'')==='pending','AI proposal workspace must persist pending proposal independently of pages.');
$base=$loaded;unset($base['Token'],$base['TokenExpires']);
$accepted=(new SuggestionGuard())->accept($base,true);$repo->save($accepted);
i8Assert(($accepted['Apply']['Value']??'')==='Forbedret tekst'&&($accepted['Undo']['Value']??'')==='Gammel tekst','Accepted proposal must produce reversible Apply/Undo plan.');
i8Assert(($repo->get((string)$proposal['Id'])['Status']??'')==='accepted','Proposal workspace must persist accepted state.');

fwrite(STDOUT,"I8 AI provider/settings/proposal workspace: PASS\n");
