<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/InMemoryRevisionRepository.php';

use Hangar18\UltimateDesigner\Contracts\SchemaMigration;
use Hangar18\UltimateDesigner\Migration\MigrationRegistry;
use Hangar18\UltimateDesigner\Portability\BackupService;
use RuntimeException;

function e14MigrationAssert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$original = ['Version'=>'1.0','Title'=>'Migration fixture','Sections'=>[['Key'=>'a','Type'=>'text','Content'=>'Original']]];
$revisions = new InMemoryRevisionRepository();
$backups = new BackupService($revisions);
$backup = $backups->create('migration:fixture',$original,7,'Automatic pre-migration backup');

$registry = new MigrationRegistry();
$registry->register(new class implements SchemaMigration {
    public function fromVersion(): string { return '1.0'; }
    public function toVersion(): string { return '1.1'; }
    public function migrate(array $state): array { $state['Version']='1.1'; $state['FeatureFlag']=true; return $state; }
});
$registry->register(new class implements SchemaMigration {
    public function fromVersion(): string { return '1.1'; }
    public function toVersion(): string { return '1.2'; }
    public function migrate(array $state): array { $state['Version']='1.2'; $state['Sections'][0]['NewProperty']='value'; return $state; }
});
$migrated = $registry->migrate($original,'1.0','1.2');
e14MigrationAssert(($migrated['Version'] ?? '') === '1.2' && !empty($migrated['FeatureFlag']), 'Migration path must reach target state.');
e14MigrationAssert(($migrated['Sections'][0]['NewProperty'] ?? '') === 'value', 'Migration must transform nested state.');
$restored = $backups->restoreState('migration:fixture',(string) $backup['Id']);
e14MigrationAssert($restored === $original, 'Rollback backup must restore byte-semantic pre-migration state without data loss.');

$pathBlocked = false;
try { $registry->migrate($original,'1.0','9.9'); } catch (RuntimeException $e) { $pathBlocked = true; }
e14MigrationAssert($pathBlocked, 'Unknown migration target must fail rather than partially guessing a path.');

fwrite(STDOUT, "E14 migration/rollback UD-117: PASS\n");
