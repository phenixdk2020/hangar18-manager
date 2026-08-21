<?php

declare(strict_types=1);

function i10DecisionAdminAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$root=dirname(__DIR__,2);
$ctrl=(string)file_get_contents($root.'/src/Admin/DecisionPacketAdminController.php');
$boot=(string)file_get_contents($root.'/src/Admin/IntegrationAdminBootstrap.php');

i10DecisionAdminAssert(str_contains($boot,'DecisionPacketAdminController::renderPanel();'),'Decision packet panel must be composed by existing Ultimate Designer bootstrap.');
foreach([
    'I10 · Decision packet · read-only',
    'READ ONLY · CUTOVER LOCKED',
    'Executable: NO',
    'PublicMutationAvailable: NO',
    'AuthorizesCutover=false',
    'ConversionDecisionPacketService',
    'ConversionDecisionPacketFingerprintService',
] as $needle){
    i10DecisionAdminAssert(str_contains($ctrl,$needle),'Decision packet read-only contract missing: '.$needle);
}

foreach([
    '<form','admin_post_','wp_nonce_field','$_POST','wp_update_post','wp_insert_post','wp_delete_post',
    'update_post_meta','delete_post_meta','update_option','delete_option','->save(','->createShadow(','add_action(','add_filter(','function register('
] as $forbidden){
    i10DecisionAdminAssert(stripos($ctrl,$forbidden)===false,'Read-only decision packet admin introduced forbidden primitive: '.$forbidden);
}

fwrite(STDOUT,"I10 decision packet admin read-only smoke: PASS\n");
