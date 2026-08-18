<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Quality\SideHealthService;
use RuntimeException;

function e11Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$sections = [
    ['Key'=>'h1','Type'=>'heading','HeadingTag'=>'h1','Title'=>'Side title'],
    ['Key'=>'h3','Type'=>'heading','HeadingTag'=>'h3','Title'=>'Sprunget heading'],
    ['Key'=>'image','Type'=>'image','MediaId'=>99],
    ['Key'=>'button','Type'=>'button','Label'=>'','MobileWidthPx'=>500,'MobileHeightPx'=>30,'CustomTextColor'=>'#777777','CustomBackgroundColor'=>'#888888'],
];
$parent = '';
for ($i=1;$i<=10;$i++) {
    $key='c'.$i;
    $sections[]=['Key'=>$key,'Type'=>'container','LayoutParentKey'=>$parent];
    $parent=$key;
}
$badState = ['Sections'=>$sections,'LoadedModules'=>['carousel']];
$badSeo = ['Title'=>'','MetaDescription'=>'','CanonicalUrl'=>'http://example.test/page','Index'=>true];
$report = (new SideHealthService())->analyze($badState,$badSeo,[99=>2000000]);
e11Assert((int) $report['Score'] < 100, 'Side Health must deduct score for issues.');
e11Assert((int) $report['HardFailureCount'] > 0, 'Hard failures must remain explicit and cannot be hidden by aggregate score.');
$codes = array_map(static fn(array $issue): string => (string) $issue['Code'], $report['Issues']);
foreach (['heading-order','missing-alt','missing-control-label','low-contrast','fixed-width-overflow','small-touch-target','off-token-color','missing-title','invalid-canonical','oversized-image','deep-dom','unused-module'] as $code) {
    e11Assert(in_array($code,$codes,true), 'Expected Side Health issue missing: '.$code);
}
e11Assert(isset($report['Areas']['Design'],$report['Areas']['Mobile'],$report['Areas']['Accessibility'],$report['Areas']['Performance'],$report['Areas']['SEO']), 'Side Health must return the five design-spec score areas.');

$goodState = ['Sections'=>[
    ['Key'=>'title','Type'=>'heading','HeadingTag'=>'h1','Title'=>'God side'],
    ['Key'=>'photo','Type'=>'image','MediaId'=>1,'AltText'=>'Historisk militærkøretøj'],
    ['Key'=>'cta','Type'=>'button','Label'=>'Læs mere','MobileHeightPx'=>48],
]];
$goodSeo = [
    'Title'=>'Aalborg Kaserners Veteran Panser- og Køretøjsforening',
    'MetaDescription'=>'Historisk militærmateriel, restaurering, arrangementer og foreningsarbejde i Aalborg.',
    'CanonicalUrl'=>'https://example.test/god-side/',
    'Index'=>true,'Follow'=>true,
    'SocialTitle'=>'Veteran Panser- og Køretøjsforening',
    'SocialDescription'=>'Historisk militærmateriel og arrangementer.',
    'SocialImageMediaId'=>1,
];
$clean = (new SideHealthService())->analyze($goodState,$goodSeo,[1=>120000]);
e11Assert((int) $clean['Score'] === 100, 'Clean fixture must score 100.');
e11Assert((int) $clean['IssueCount'] === 0, 'Clean fixture must have no quality issues.');

fwrite(STDOUT, "E11 Quality core UD-098..103: PASS\n");
