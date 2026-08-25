=== Hangar18 Manager Clean ===
Contributors: hangar18
Requires at least: 6.4
Requires PHP: 8.0
Version: 0.1.7
Ren 120-unit sidebygger til Hangar18 uden legacy editor-runtime.

== 0.1.7 ==
* Drag/drop har nu fire placeringer omkring et almindeligt element: Over, Under, Venstre og Højre.
* Sektion/Kasse har desuden en central Ind i Kassen-zone.
* Venstre/Højre lægger elementer i samme række og fordeler rækken automatisk over 120 units; 2 elementer bliver 60/60, 3 bliver 40/40/40 osv.
* Over/Under opretter en selvstændig fuldbredde-række før/efter den række, der peges på.
* Når et element flyttes ud af en række, fordeles de resterende elementer igen over rækken.
* Drop-zoner vises fysisk under drag med aktiv zone tydeligt markeret.
* Elementlabel og drag-håndtag forbliver editor-overlay og tæller ikke med i fysisk x/y/w/h.

== 0.1.6 ==
* Elementnavn og drag-håndtag er editor-overlay og tæller ikke med i elementets fysiske x/y/w/h.
* Alle elementer kan få ramme med valgfri farve og tykkelse 0-20 px. Standard er 0 px.
* Sektioner og Kasser auto-grow synkroniseres mod deres faktiske børneindhold.
* Frontend bruger samme minimumsprincip for containerhøjde.
* Venstre/højre-drop viser begge halvdele, fremhæver den aktive side og viser en tydelig flydende drop-tekst.

== 0.1.5 ==
* Sektioner og Kasser bruger deres valgte højde som minimum og vokser automatisk, når børn kræver mere plads.
* Samme auto-grow-regel anvendes på offentlig frontend.
* Under drag vises tydelig venstre/højre halvside-guide direkte på nabo-elementet.
* GitHub-updateren er fortsat normal update-kanal.

== 0.1.4 ==
* Hangar18 Base Theme 1.2.x genkender Clean Manager som aktiv via en isoleret kompatibilitetsmarkør.
* Indeholder spatial drag/drop og fix mod duplikerede drop-handlers.

== 0.1.3 ==
* Drop placeres fysisk venstre/højre efter pointer og nabo.
* Eksisterende element kan omplaceres inden for samme Kasse.
* Root/surface drop-handlers bindes kun én gang og duplikerer ikke elementer efter Undo/Redo.

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
* Strukturelle diagnostics med read-only support-link.
