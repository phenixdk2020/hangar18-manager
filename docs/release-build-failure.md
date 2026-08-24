# Hangar18 release build failure

- Version: 0.8.81
- Source commit: 4960b447ee1b122a9ff95c4313743a809aa91897
- UTC: 2026-08-24T05:34:20Z
- Step: guarded WhatIf source cleanup

## stderr
```text
ERROR: Active WhatIf runtime remains:
hangar18-manager.php:4135:<div class="h18-safe-badge">WhatIf er FRA som standard</div>
hangar18-manager.php:4157:['hangar18-log', 'dashicons-list-view', 'Log', 'Web-managerens checkpoints, WhatIf, fejl og succeser.', 'Aktiv'],
hangar18-manager.php:4392:Vælg et eksisterende køretøj eller opret et nyt. WhatIf er slået fra som standard.
hangar18-manager.php:11168:<p>Hver rigtig gemning får sit eget versionsnummer og en beskrivelse. WhatIf opretter ingen historik.</p>
hangar18-manager.php:12789:Først når WhatIf slås fra og du trykker <strong>Gem menu</strong>,
assets/admin.js:4346:$pageWhatIf.on('change', syncPageChangeNoteRequirement);
assets/admin.js:4352:editorDraftSaveNow(!$pageWhatIf.is(':checked'));
```

## stdout
```text
```
