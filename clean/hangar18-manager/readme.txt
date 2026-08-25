=== Hangar18 Manager Clean ===
Contributors: hangar18
Requires at least: 6.4
Requires PHP: 8.0
Version: 0.1.2
Ren 120-unit sidebygger til Hangar18 uden legacy editor-runtime.

== 0.1.2 ==
* GitHub-baseret WordPress updater via clean-update.json.
* Normal "Opdater nu" i WordPress Plugins, når en nyere clean-version ligger på GitHub.
* Manuel "Tjek GitHub-opdatering" i Hangar18 Designer.
* Update-pakken SHA-256-verificeres mod manifestet før installation.
* Indeholder palette drag/drop-fix fra 0.1.1.

== 0.1.1 ==
* Palette-elementer kan trækkes direkte til root, Sektion eller Kasse.
* Firefox-robust drag payload via dataTransfer med custom MIME + text fallback.
* Klik på palette bevares som hurtig tilføjelse på root.

== 0.1.0 ==
* Canonical JSON-model gemt pr. WordPress-side.
* 120 layout-units og 8 px lodret snap.
* Fysisk 8-vejs resize.
* Undo/Redo med Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z og Ctrl+Y.
* Eksisterende elementer kan trækkes ind i/ud af Sektion/Kasse.
* Billeder følger elementkassen med Cover, Contain eller Stretch og focal X/Y.
* Save som versionshistorik og Restore som ny sikker version.
* Strukturelle diagnostics med privat read-only support-link.

== 0.1.3 ==
* Drop placeres fysisk venstre/højre efter pointer og nabo.
* Eksisterende element kan omplaceres inden for samme Kasse.
* Root/surface drop-handlers bindes kun én gang og duplikerer ikke elementer efter Undo/Redo.
