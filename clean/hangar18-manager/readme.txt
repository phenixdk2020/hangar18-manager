=== Hangar18 Manager Clean ===
Contributors: hangar18
Requires at least: 6.4
Requires PHP: 8.0
Version: 0.1.14
Ren 120-unit sidebygger til Hangar18 uden legacy editor-runtime.

== 0.1.14 ==
* Kasse-/barn-labels kolliderer ikke længere: labels er kontekstuelle og ancestor-label skjules, når et barn er det direkte hover/valgte element.
* Forhåndsvis åbner den aktuelle ikke-gemte canonical model i den rigtige frontend/theme via et 10-minutters brugerspecifikt preview-token.
* Gem & vis gemmer en ny version og åbner den offentlige side i en ny fane.
* Save læser canonical model tilbage og verificerer fuld digest før success.
* Structural digest dækker nu hele den normaliserede model inkl. tekst, gaps og style props.

== 0.1.13 ==
* Direkte opdatering fra Hangar18 Manager husker om pluginet var aktivt eller netværksaktivt før opdateringen og genaktiverer/verificerer samme tilstand før redirect.
* Hvis genaktivering mod forventning fejler, sendes administratoren sikkert til Plugins i stedet for en ikke-registreret Manager-side.
* Nye Tekst-elementer starter med 80 px / 10 grid-rækker, samme grundhøjde som Billede.
* Celle-split kan stadig ændre højden efterfølgende, og eksisterende elementer ændres ikke automatisk.

== 0.1.12 ==
* Blå markering betyder valgt/aktivt element; overlap-advarsel er en separat rød diagnostisk markering.
* Kasse og Sektion er layout-wrappers og tæller ikke selv som OVERLAP.
* Editorlabels vises på dansk som KASSE, SEKTION, TEKST og BILLEDE; canonical type keys ændres ikke.
* Elementlabel og drag-håndtag er fortsat editor-chrome og tæller aldrig med i fysisk x/y/w/h eller containerens auto-grow.

== 0.1.11 ==
* Border er nu en native Clean-egenskab på Tekst, Billede, Kasse og Sektion: tykkelse 0-20 px, farve og standard 0 px.
* Alle elementer har Afstand X og Afstand Y (0-200 px, standard 0) som trailing layoutafstand til næste element.
* Afstand Y indgår i canonical højdematerialisering, så container auto-grow fortsat matcher editor og frontend.
* Det gamle v0.1.6 border/autogrow-JS er pensioneret; Inspector og rendering bruger nu samme canonical props.
* Hangar18 Manager > Opdateringer kan både tjekke GitHub og installere Opdater nu direkte uden at gå via WordPress Plugins.
* Direkte update bruger WordPress Plugin_Upgrader og den eksisterende SHA-256-verifikation.

== 0.1.10 ==
* Elementer med naturlig h=0 materialiseres nu til deres faktiske højde i hele 8-px-rækker, så gridet reserverer den plads der faktisk tegnes.
* Kasse/Sektion beregner effektiv højde rekursivt ud fra alle direkte børn og vokser automatisk efter drop, reparent, resize, delete og reload.
* Manuel højde på Kasse/Sektion gemmes separat som minHeightRows og fungerer som minimum; indhold kan gøre kassen højere, og den kan krympe tilbage til minimum når indhold fjernes.
* Kollisions-heal flytter kun elementer der kolliderer som følge af automatisk materialisering af tidligere h=0-geometri.
* Bevidst/manuelt overlap er foreløbig stadig tilladt, men markeres tydeligt med OVERLAP-advarsel i editoren, så vi kan beslutte den endelige policy efter test.
* Frontend har fallback-højder for ældre h=0-layouts, indtil de er gemt igen med canonical 0.1.10-geometri.

== 0.1.9 ==
* Nyt samlet Hangar18 Manager-adminmenu inspireret af 0.9.2: Dashboard, Designer, Køretøjer, Køretøjsfelter, Events, Billedgalleri, Data, Sider, Menu, Header/Footer, Backup, Opdateringer og Log.
* Designer er flyttet ind som undermenu uden at ændre Clean-editorens canonical runtime.
* Dashboard viser sideantal, Clean-sider, nodeantal og samlet versionshistorik med hurtige genveje.
* Sider viser Clean-version, nodeantal, seneste gemning samt direkte links til Designer, WordPress og frontend.
* Køretøjer, Events og Billedgalleri viser de eksisterende WordPress-hovedsider/undersider og deres Clean-status uden legacy dataruntime.
* Menu viser klassiske WordPress-menuer og registrerede theme locations.
* Header/Footer viser aktivt tema og holder global shell adskilt fra side-layoutversioner.
* Backup kan downloade alle Clean-layouts og deres versionshistorik som én JSON-fil; diagnostics/tokens eksporteres ikke.
* Opdateringer bruger fortsat den SHA-256-verificerede GitHub updater.
* Log viser Clean diagnostics pr. side, support-link og mulighed for at rydde side-loggen.
* Køretøjsfelter og custom Data er bevidst administrationspladser; gammel 0.9.x felt/data-runtime aktiveres ikke automatisk.

== 0.1.8 ==
* Over/Under deler nu kun den valgte celles højde i stedet for altid at oprette en fuldbredde-række.
* Venstre/Højre deler kun den valgte celles bredde; øvrige celler i layoutet ændres ikke unødigt.
* Naboceller i samme bånd materialiseres med fælles højde, så en nabocelle kan spænde over begge nye under-rækker.
* Eksempel: Billede øverst til venstre + Tekst nederst til venstre kan dele samme højde som ét Tekst-element til højre, der spænder over begge rækker.
* Sektion/Kasse beholder central Ind i Kassen-zone; kantzonerne deler parentens egen celle.
* Elementets canonical x/y/w/h renderes som eksplicit 120-kolonne/8-px grid både i editor og frontend, når højden er fastlagt.
* Flyttes et element ud af en celle, forsøger editoren kun en lokal, sikker sammensmeltning med én direkte nabocelle frem for at omfordele hele rækken.
* Label/type/ID/drag-håndtag er fortsat editor-overlay og tæller ikke med i fysisk geometri.

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
