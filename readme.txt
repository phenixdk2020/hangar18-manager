=== Hangar18 Manager ===
Version: 0.8.35
Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.


== Version 0.8.35 – Designer — LEGO consolidation og primary-editor readiness ==

Nyt:
- Konsoliderer LEGO-editorens eksisterende spacing-, responsive design-, interaction-state- og nesting-lag uden at introducere en ny renderer, persistence-store, drag/drop-motor eller Undo/Redo-stack.
- Verificerer den eksisterende LayoutParentKey-model i kombinationen Auto-kasser → Kasse → Kasse + element inden for den eksisterende maksimale nesting-dybde på 2.
- Kasse-i-Auto-kasser, Kasse-i-Kasse og element-i-Kasse fungerer samtidigt med responsive X/Y-spacing, farver/radius og Focus/Active/Disabled på den samme valgte Kasse.
- Spacing, responsive design og interaction states forbliver uafhængige canonical state-lag, men bruger den samme eksisterende section-row og history-motor.
- En ny sekventiel Undo/Redo-gate beviser baseline + præcis ét checkpoint for spacing, design og interaction state: Undo fjerner state, derefter design, derefter spacing, og Redo gendanner dem i korrekt rækkefølge.
- LayoutParentKey og nested composition bevares gennem kombineret Undo/Redo og full-DOM history restore.
- v0.8.35 er en readiness- og regressionsrelease; den ændrer ikke public renderer eller aktiverer public sidekonvertering.
- LEGO Editor QA er bestået på PHP 8.0/8.2/8.3 og system Chrome; Editor Runtime Fast QA er bestået.
- Fuld Architecture QA er bestået på PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.34 – Designer — responsive LEGO interaction states ==

Nyt:
- Udvider den fælles LEGO-designmodel til schema 2 med Transition, Focus, Active og Disabled oven på de eksisterende legacy-backed designfelter.
- Focus understøtter Global, Tilpasset eller Ingen ring samt farve, bredde og offset; Active understøtter Tryk 1 px og Scale 97%, og Disabled har egen opacity.
- Almindelige elementer og Kasse/Grid/Flex bruger præcis samme interaction-state model og Inspector-kontroller.
- Desktop forbliver gemt i de eksisterende page-section felter; Tablet/Mobil interaction overrides ligger i den eksisterende responsive LEGO-designstate og kræver ingen ny WordPress-option.
- Aktiv override og bevaret snapshot er separate, så Arv fra Desktop kan slås til/fra uden at tidligere Tablet/Mobil Focus/Active/Disabled-værdier går tabt.
- Canvas preview følger Normal, Hover, Focus, Aktiv og Disabled på den valgte Desktop/Tablet/Mobil device.
- Responsive state-ændringer sender ét canonical row input-checkpoint; admin.js/history-v0.8.23 er fortsat eneste Undo/Redo-ejer, og select-event guard forhindrer dobbelt input/change.
- B2 selective page restore gendanner interaction snapshots som del af den valgte sides responsive LEGO-designstate og bevarer andre sider.
- Historiske v0.8.32 design-tests er gjort additive-schema kompatible uden at svække mapping-, persistence-, history- eller protected-domain-kontrakterne.
- LEGO Editor QA, Editor Runtime Fast QA og B2 QA er bestået; fuld Architecture QA er bestået på PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.33 – Designer — responsive LEGO-design ==

Nyt:
- Udvider den fælles LEGO-designmodel med Desktop som canonical basis og responsive Tablet/Mobil design-state.
- Tablet og Mobil starter med Arv fra Desktop; første gang arv slås fra uden et tidligere override, seedes designet fra den aktuelle Desktop-state.
- Eksisterende Tablet/Mobil-overrides bevares gennem arv til/fra via et eksplicit HasOverride-flag, så tidligere design ikke slettes.
- Almindelige elementer og Kasse/Grid/Flex bruger den samme responsive designmodel for farver, border, radius, typografi, opacity, shadow og hover.
- Inspector følger aktiv Desktop/Tablet/Mobil-preview og viser inherited kontra eksplicit design uden at introducere en ny drag/drop-, parent/child- eller history-motor.
- Hover-effekter som Lift, Scale og Shadow fungerer uafhængigt af om hover-farverne arver Normal eller er tilpassede.
- Responsive dropdowns har en snæver DOM input/change-guard, så én brugerhandling fortsat giver ét eksisterende Undo/Redo-checkpoint.
- Responsive design gemmes som et additivt admin-only overlay; Desktop og den eksisterende public renderer forbliver legacy-backed og autoritative.
- B2 selective page restore gendanner nu også kun den valgte sides responsive LEGO-designstate og bevarer andre sider; ældre backups uden overlay sletter ikke nyere state.
- LEGO Editor QA, Editor Runtime Fast QA og B2 QA er bestået; fuld Architecture QA er bestået på PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.32 – Designer — fælles LEGO-designmodel ==

Nyt:
- Introducerer én canonical, renderer-neutral LEGO-designmodel som view over de eksisterende page-section designfelter; der oprettes ingen ny design-option eller parallel persistence-store.
- Almindelige elementer og Kasse/Grid/Flex bruger nu samme design-sprog for baggrund, tekst, overskrift, kant, border width, radius, typografi, opacity, shadow og hover-state.
- Samlet radius og alle fire individuelle hjørner er samlet i samme model; -1 på et individuelt hjørne bevarer den eksisterende arv fra samlet radius.
- Normal-state understøtter Global/Tilpasset, og hover understøtter Arv Normal/Tilpasset uden at overskrive normal-state.
- LEGO-designpanelet skriver direkte til de eksisterende gemte section-felter, så legacy save/public renderer fortsat er autoritativ og eksisterende sider kræver ingen datamigration.
- admin.js/history-v0.8.23 er fortsat eneste Undo/Redo-ejer; companion-mode ændringer udføres i samme DOM-transaction, og hvert LEGO-designgreb udsender kun ét eksisterende input/change-checkpoint.
- En snæver select-event guard forhindrer native input+change-dobling i LEGO-designpanelets dropdowns, så ét dropdown-valg svarer til én logisk history-handling.
- Responsive LEGO spacing fra v0.8.31 er uændret og fortsat samme separate canonical spacing-model; ingen ny drag/drop- eller parent/child-motor introduceres.
- LEGO Editor QA og Editor Runtime Fast QA er bestået; fuld Architecture QA er bestået på PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.31 – Designer — responsive LEGO spacing og selektiv backup-restore ==

Nyt:
- Udvider den canonical LEGO spacing-model til schema 2 med Desktop som basis og Tablet som eksplicit responsive device.
- Tablet starter med Arv fra Desktop; Tablet og Mobil kan slå inheritance til/fra uden at de gemte X/Y override-værdier slettes.
- Eksisterende v0.8.30 Mobile Margin/Gap-værdier migreres som eksplicitte overrides, så opgraderingen ikke ændrer eksisterende mobil-layout.
- Inspector viser Desktop/Tablet/Mobil med tydelig inheritance-status, og editor-preview anvender effektive device-værdier gennem den samme canonical section-row state.
- Den eksisterende admin.js/history-v0.8.23-motor er fortsat eneste Undo/Redo-ejer; responsive LEGO introducerer ingen parallel history-, drag/drop- eller parent/child-motor.
- Selective B2 page restore gendanner nu kun den valgte sides LEGO-spacing og bevarer andre siders spacing; ældre backups uden LEGO-state sletter ikke nyere spacing.
- Retter en B2 stale-lock edge case: restore-koordinationsstate ekskluderes nu fra portable snapshot/current-state hash, så stale-lock recovery ikke kan invalidere sit eget dry-run.
- B2 QA og LEGO QA er bestået på PHP 8.0/8.2/8.3; system Chrome, Editor Runtime Fast QA samt fuld Architecture QA inklusive Chromium, Firefox og WebKit er bestået.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.30 – Designer — LEGO X/Y spacing foundation ==

Nyt:
- Tilføjer én canonical Desktop/Mobile spacing-model, som deles af almindelige elementer og Kasse/Grid/Flex-layout.
- Eksisterende LayoutGapPx og MobileLayoutGapPx bruges som backward-compatible startværdi for både X og Y, så eksisterende sider kræver ingen migration.
- Inspector får separate Element X/Y-marginer på alle elementer samt separate Indhold X/Y-gap på Kasse, Grid og Flex.
- LEGO-state ligger som ét canonical felt i den eksisterende section-row og bruger fortsat admin.js/history-v0.8.23 som eneste Undo/Redo-ejer; der oprettes ingen parallel historikmotor.
- Editor-preview anvender separate column-gap/row-gap samt Desktop/Mobile spacing uden at aktivere en ny offentlig renderer.
- Spacing-state gemmes admin-only i en versioneret Hangar18-option og indgår automatisk i B2 fuld site-backup.
- LEGO Spacing QA er bestået på PHP 8.0/8.2/8.3 og system Chrome; Editor Runtime Fast QA samt fuld Architecture QA inklusive Chromium, Firefox og WebKit er bestået.
- Vehicle/Event/Gallery, public cutover og den eksisterende drag/drop-, parent/child- og history-arkitektur er uændret.


== Version 0.8.29 – Backup — versioneret site-backup, ZIP og sikker restore ==

Nyt:
- Tilføjer B2 med immutable H18-BACKUP-xxxxxx ID'er, canonical JSON og SHA-256 checksums for manifest, payloads og refererede mediefiler.
- Den portable Hangar18-backup omfatter administrerede sider, sideversioner, Site Builder-data, formularer/polls/data, relevante Hangar18-options samt refererede originalbilleder og nødvendige derivatives.
- Tilføjer ZIP export/import med preflight mod path traversal, ZIP-bombs, aktive serverkonfigurationsfiler og eksekverbare filtyper før pakken installeres.
- Restore bruger en signeret og state-bundet dry-run-plan; både fuld og selektiv side-restore opretter automatisk en ny B2 safety backup før første mutation.
- Tilføjer collision-safe media/ID/URL mapping, stale restore-lock recovery samt audit af både gennemførte restores og fejl med reference til safety-backuppen.
- B2 create/import/restore kræver manage_options og nonce; fuld restore kræver den eksplicitte bekræftelsesfrase GENDAN HANGAR18.
- B2 Site Backup QA er bestået på PHP 8.0/8.2/8.3, og Architecture QA inklusive Chromium, Firefox, WebKit og security audit er bestået.
- Standard-B2 er application-aware og indeholder ikke rå database-, plugin- eller theme-disaster-recovery; Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.28 – Backup — sikker gendannelse af enkelte sider ==

Nyt:
- Tilføjer B1: eksisterende Hangar18 JSON-sidebackups kan gendannes fra Ultimate Designer-administrationen.
- Erstat original opretter altid en ny sikkerhedsbackup af den aktuelle side før første write og bevarer originalt WordPress-ID og slug/URL.
- Opret som kopi laver en separat draft med collision-safe slug og ændrer ikke originalside eller menu.
- Page Editor-backups uden den centrale page_editor-state låses for replace-original og kan fortsat åbnes sikkert som kopi.
- Restore er capability- og nonce-gated, anvender path-containment og skriver audit for restore/copy-handlinger.
- B1 Backup Restore QA er bestået på PHP 8.0/8.2/8.3 og Architecture QA er bestået.
- UX-4 preview-hotfix v0.8.27, EVENT-001 og den manuelt godkendte Undo/Redo-motor er bevaret.


== Version 0.8.27 – Designer — rent ugemt preview uden editor-overlays ==

Nyt:
- Retter UX-4 ugemt forhåndsvisning, så transient editor-chrome ikke klones med ind i previewet.
- Fjerner Billede-kontrolpanelet, DIREKTE DESIGN, box-model P/M badges, padding/margin-handles og focal-point fra preview-klonen.
- Bevarer selve live canvas-indholdet, herunder ugemt tekst, billeder og layout, uden at gemme eller publicere siden.
- Playwright-regression dækker valgt billede med image-tools, direct-controls, box-model overlay og editor-handles.
- Fast QA og Architecture QA er bestået inklusive Chromium/Firefox/WebKit.
- EVENT-001 fra v0.8.26 og Undo/Redo v0.8.23 er bevaret.


== Version 0.8.26 – Events — automatisk arkiv efter dato og sluttid ==

Nyt:
- Tilføjer EVENT-001: Events-overblikket klassificeres dynamisk ved visning efter WordPress' lokale dato og tid, så manuel Gem eller Genbyg eventregister ikke længere er nødvendig for arkivering.
- Events med en dato før dags dato vises automatisk under Tidligere arrangementer.
- På selve eventdatoen forbliver eventet under Kommende arrangementer indtil en angivet sluttid er passeret; derefter flyttes det automatisk til arkivet.
- Hvis et event ikke har en sluttid, forbliver det kommende resten af eventdagen og flyttes automatisk til Tidligere arrangementer efter midnat.
- Kommende arrangementer sorteres kronologisk, mens Tidligere arrangementer viser de nyeste afsluttede events først.
- Den eksisterende Event-side, eventkort, HANGAR18-EVENT-DATA og eventskabelon genbruges; runtime udfører ingen frontend save, post-write eller option-write.
- Eventklassificeringen kører før WordPress do_blocks, så det eksisterende wp:html-eventregister kan omfordeles sikkert og derefter rendres normalt.
- Dedikeret Event Auto Archive QA er bestået på PHP 8.0/8.2/8.3, og Architecture QA er bestået inklusive protected-domain samt Chromium/Firefox/WebKit.
- UX-3, UX-4 og den manuelt godkendte v0.8.23 Undo/Redo-historik er bevaret uændret.


== Version 0.8.25 – Designer — forhåndsvis ugemte ændringer ==

Nyt:
- Tilføjer UX-4: Forhåndsvis side viser den aktuelle levende editor-state uden at gemme eller versionere siden.
- Preview bygges browser-lokalt fra Sideopbygning og ændrer ikke den offentlige side, menu eller WordPress post-data.
- Desktop, Tablet og Mobil kan skiftes direkte i preview-dialogen.
- Editor-knapper, drag/drop-zoner, formularfelter og runtime-badges fjernes fra preview-klonen.
- Dialogen understøtter Escape, focus restore og keyboard focus trap.
- UX-3 foldbare paneler og v0.8.21-v0.8.23 Undo/Redo-runtime er bevaret.
- Fast QA og Architecture QA er bestået inklusive Chromium/Firefox/WebKit.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.24 – Designer — foldbare Elementer/Funktioner og Inspector ==

Nyt:
- Tilføjer UX-3: venstre Elementer/Funktioner-panel og højre Inspector kan foldes ind uafhængigt på desktop.
- Begge paneler kan være foldet ind samtidig til 44 px rails, så Sideopbygning får næsten hele arbejdsbredden.
- Foldetilstanden gemmes kun i browserens localStorage og ændrer ikke sideindhold, schema eller public rendering.
- Tablet og mobil beholder det eksisterende stacked editor-layout uden tvungne rails.
- Collapse/expand-knapper har ARIA-state, keyboard-adgang og reduced-motion-understøttelse.
- v0.8.21/v0.8.22/v0.8.23 Undo/Redo-stakken er uændret og fortsat autoritativ.
- Fast QA og Architecture QA er bestået inklusive protected-domain samt Chromium/Firefox/WebKit.
- Vehicle/Event/Gallery og public cutover er uændrede.


== Version 0.8.23 – Designer — Undo/Redo for tekst, farver og billeder ==

Nyt:
- Udvider den stabiliserede Undo/Redo-historik, så ændringer inde i eksisterende elementer behandles som rigtige historiktrin — ikke kun indsættelse, flytning og fjernelse af selve elementerne.
- Tekst- og formularfelter gemmes med normal debounce, så en sammenhængende skrivehandling bliver et logisk Undo-trin frem for ét trin pr. tastetryk.
- Farver og øvrige Direkte design-felter registreres i historikken og kan fortrydes/gendannes sammen med deres gemte feltværdi.
- Billedevalg registrerer MediaId og MediaUrl som samme logiske ændring, så Undo kan gendanne det tidligere billede og Redo kan sætte det valgte billede tilbage.
- Den første tekst-, farve- eller billedeændring umiddelbart efter en Undo/Redo-kæde bliver nu bevaret som et nyt checkpoint i stedet for at blive undertrykt af restore-latchen.
- v0.8.21 forbliver den autoritative history-owner, v0.8.22 håndterer strukturelle post-restore-handlinger, og v0.8.23 tilføjer en snæver content-history bridge uden en ekstra history-stack eller nye persistence-veje.
- Nye regressioner verificerer tekst → farve → billede som tre separate Undo/Redo-trin samt første tekst-, farve- og billedeændring direkte efter Redo.
- Runtime-markøren ved historikstatus viser H0.8.23, så manuel QA kan verificere at den aktive content-history bridge er leveret til browseren.
- Editor Runtime Fast QA og Architecture QA er bestået, inklusive isolation/protected-domain, PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery, offentlig rendering, URL'er og persistence/cutover er uændrede; LEGO/X-Y-layout afventer fortsat manuel accept af Undo/Redo.


== Version 0.8.22 – Designer — registrér nye ændringer efter fuld Undo/Redo ==

Nyt:
- Retter den resterende Undo/Redo-fejl fra v0.8.21, hvor tre eksisterende elementer kunne fortrydes og gendannes korrekt, men den første nye indsættelse efter en komplet Redo-kæde ikke blev registreret som et nyt historiktrin.
- Rodårsagen var restore-latchens korte trusted-release guard: en ny palette-/drag/drop-gestus kunne starte mens historikken stadig betragtede editoren som værende i restore-mode, så DOM-ændringen blev udført men dens strukturelle 0–120 ms checkpoint blev suppressed.
- v0.8.21 forbliver den autoritative history-owner og bevarer snapshot/clone-fixet, så Billede-elementer fortsat forbliver Billede gennem Undo og Redo.
- v0.8.22 tilføjer en snæver post-restore intent bridge, som genkender nye strukturelle brugerhandlinger som paletteindsættelse, drag/drop, duplicate, delete og reorder og sikrer, at den første nye handling efter Undo/Redo bliver sit eget checkpoint.
- Den konkrete regression er nu: 3 elementer → Undo ×3 → Redo ×3 → indsæt element 4 → historiktrin 4 → Undo fjerner kun element 4.
- Runtime-markøren ved historikstatus viser H0.8.22, så manuel QA kan verificere at den nye post-restore bridge faktisk kører.
- Editor Runtime Fast QA og Architecture QA er bestået, inklusive isolation/protected-domain, PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery, offentlig rendering, URL'er og persistence/cutover er uændrede; LEGO/X-Y-layout afventer fortsat manuel accept af Undo/Redo.


== Version 0.8.21 – Designer — bevar elementtype gennem Undo/Redo ==

Nyt:
- Retter den resterende Undo/Redo-fejl fra v0.8.20, hvor historiktrinene nu bevægede sig korrekt, men et Billede-element kunne blive gendannet som Tekst efter Undo og Redo.
- Rodårsagen var snapshot-cloning af formular-state: nye elementer oprettes fra en fælles template med text som markup-standard, mens den aktuelle elementtype som image ligger i SELECT-feltets live browser-state. jQuery cloning kunne falde tilbage til markup-standarden.
- Den aktive history-runtime er nu assets/ultimate-designer-history-preload-v0821.js og indlæses fortsat som header-asset før legacy assets/admin.js initialiserer editorhistorikken.
- v0.8.21 kopierer live state for SELECT, INPUT og TEXTAREA fra original DOM til history-klonen før core editorHistoryNormalizeClone serialiserer snapshot'et.
- Clone-broen er snævert afgrænset til de to kilder som editorHistorySnapshot bruger: #h18-page-sections-sortable og den midlertidigt inspicerede section body i Inspector.
- Den konkrete regression bruger nu samme jQuery clone-path som den rigtige editor og verificerer Billede 1 + Billede 2 → Undo = Billede 1 samt Redo = begge elementer fortsat af typen Billede.
- De tidligere v0.8.20-rettelser til 2→1→0 / 0→1→2, pending history-timer, restore-latch og rydning af historisk Direkte design-selection bevares.
- Et lille admin-only badge H0.8.21 vises ved historikstatus, så manuel QA kan verificere at den korrekte runtime faktisk kører i browseren.
- Editor Runtime Fast QA og Architecture QA er bestået, inklusive isolation/protected-domain, PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Event/Vehicle/Gallery, offentlig rendering, URL'er, persistence/cutover samt LEGO-layout er uændrede; LEGO/X-Y arbejdet afventer fortsat manuel accept af Undo/Redo.


== Version 0.8.20 – Designer — sikker history-runtime load-order ==

Nyt:
- Retter en reel load-order-fejl i v0.8.19: history-runtime blev forsøgt tilføjet inline til hangar18-manager-admin før dette script-handle nødvendigvis var lagt i WordPress-køen, så pluginet kunne vise v0.8.19 uden at den nye historikmotor faktisk nåede browseren.
- Historik-ejeren leveres nu som den dedikerede asset assets/ultimate-designer-history-preload-v0820.js og indlæses i wp-admin-headeren med jQuery som dependency; legacy assets/admin.js forbliver footer-script og kan derfor ikke initialisere historikken først.
- Strukturelle editorændringer på 0–120 ms capture-path registreres fortsat som separate checkpoints, mens almindelige tekst-/feltændringer beholder debounce og flushes præcis én gang før Undo/Redo eller næste strukturelle checkpoint.
- Den konkrete regression Tekst → Billede 1 → Billede 2 → Fortryd kører nu direkte mod den faktiske v0.8.20 assetfil og verificerer at ét Undo kun fjerner Billede 2 og ikke efterfølgende hopper tilbage til trin 2.
- Undo/Redo rydder fortsat historisk Inspector-selection og Direkte design efter restore, så et gammelt Tekst-element ikke vælges som bivirkning når et Billede-element fjernes.
- Et lille admin-only badge H0.8.20 vises ved historikstatus. Badget er en manuel QA-markør, der beviser at den aktive v0.8.20 history-runtime faktisk er leveret og eksekveret i browseren.
- v0.8.17–v0.8.19 history-implementationer er rollback-reference og enqueues ikke parallelt med v0.8.20.
- Editor Runtime Fast QA og Architecture QA er bestået, inklusive isolation/protected-domain, PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Kasse/Auto-kasser, Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er samt persistence/cutover er uændrede og beskyttede.
- LEGO-layout og X/Y-spacing afventer fortsat manuel accept af Undo/Redo-stabiliteten i den installerede editor.


== Version 0.8.19 – Designer — preloaded historikejer og strukturelle checkpoints ==

Nyt:
- Historik-ejeren indlæses nu inline før assets/admin.js initialiserer sideeditorens historik, så alle efterfølgende editorHistoryRecordNow-planlægninger går gennem én autoritativ runtime fra første editor-tick.
- Strukturændringer og eksplicitte checkpoints fra legacy-editorens 0–120 ms capture-path registreres nu straks i stedet for at dele debounce-kø med almindelig tekst- og feltredigering.
- Den konkrete manuelle sekvens Tekst → Billede 1 → Billede 2 → Fortryd er dækket direkte: Billede 1 og Billede 2 bliver separate historiktrin, ét Undo fjerner kun Billede 2, og historikken må ikke hoppe 2 → 1 → 2 efterfølgende.
- Almindelig tekst- og feltredigering beholder debounce, men en pending ændring flushes præcis én gang før et strukturelt checkpoint eller Undo/Redo.
- Legacy editorHistoryTimer får altid et ikke-pending handle på 0 for historik-callbacks, så editorHistoryFlushPending ikke kan genafspille et allerede udført timer-id.
- Undo/Redo rydder transient Inspector-selection og Direkte design efter restore, så et historisk Tekst-element ikke vælges som bivirkning når et Billede-element fjernes.
- v0.8.17 og v0.8.18 beholdes kun som rollback-assets og enqueues ikke parallelt med v0.8.19.
- Editor Runtime Fast QA er bestået 12/12, og Architecture QA er bestået på PHP 8.0/8.2/8.3 samt Chromium, Firefox og WebKit.
- Kasse/Auto-kasser, Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er samt persistence/cutover er uændrede og beskyttede.
- LEGO-layout og X/Y-spacing afventer fortsat manuel accept af Undo/Redo-stabiliteten i den installerede editor.


== Version 0.8.18 – Designer — stabil pending-historik og neutral Inspector-selection ==

Nyt:
- Fortryd/Gendan bruger nu én autoritativ pending history-timer omkring den eksisterende editorHistoryRecordNow-callback, så et allerede afsluttet timer-id ikke kan blive genafspillet under næste Undo/Redo.
- Den konkrete manuelle fejl 2 → 1 → 2 efter indsættelse af Billede-elementer er reproduceret i en målrettet browser-regression og er rettet ved at returnere et ikke-stale core timer-handle og nulstille den faktiske pending callback efter execution.
- Hvis Undo/Redo startes mens en ægte brugerændring stadig venter på history-capture, flushes den præcis én gang før restore; core kan derefter ikke flush'e den samme ændring igen.
- Syntetiske history-captures fra restore, preview-rebuild og hjælpe-runtimes kasseres fortsat mens restore-latchen er aktiv.
- Inspector-selection behandles nu som transient UI-state: hvis det valgte element stadig findes efter Undo/Redo, bevares det; hvis elementet blev fjernet af Undo, ryddes selection i stedet for at falde tilbage til et historisk selectedKey.
- Fejlen hvor et gammelt Tekst-element blev valgt og viste Direkte design efter Undo af Billede-elementer er dækket af den nye regressionstest.
- v0.8.17 history-runtime beholdes kun som rollback-reference og enqueues ikke parallelt med v0.8.18.
- Editor Runtime Fast QA og Architecture QA er bestået, inklusive PHP 8.0/8.2/8.3, protected-domain/isolation checks samt Chromium, Firefox og WebKit.
- Kasse/Auto-kasser, Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og persistence/cutover er uændrede og beskyttede.
- LEGO-layout og X/Y-spacing afventer fortsat manuel accept af Undo/Redo-stabiliteten.


== Version 0.8.17 – Designer — deterministisk Undo/Redo restore-latch ==

Nyt:
- Fortryd/Gendan bruger nu en eksplicit restore-latch, som har højere prioritet end trusted-state fra den brugerhandling, der netop bliver fortrudt.
- Fejlen hvor historikken kort gik 4 → 3 og straks tilbage til 4 er dækket af en målrettet regressionstest og må ikke længere kunne skabes af syntetiske restore/preview-events.
- Ctrl/Cmd+Z og Ctrl/Cmd+Shift+Z går gennem samme restore-latch; browser-events fra selve Undo/Redo-tastaturgestussen kan ikke frigive latchen som en falsk ny brugerændring.
- Restore-latchen frigives først af en efterfølgende, ægte brugerændring eller kendt strukturhandling, så en rigtig ændring umiddelbart efter Undo stadig kan oprette et nyt historiktrin.
- Det element, der er valgt når Undo/Redo startes, bevares som UI-selection efter restore, hvis elementet stadig findes; historisk selectedKey må derfor ikke åbne Direkte design/Inspector på et uvedkommende element.
- Lokal kladde-gendannelse er fortsat beskyttet mod syntetiske history-captures, men beholder sin egen draft-selection-adfærd.
- Editor Runtime Fast QA og Architecture QA er bestået, inklusive PHP 8.0/8.2/8.3, isolation/protected-domain checks samt Chromium, Firefox og WebKit.
- Kasse/Auto-kasser-runtime, Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er uændrede og beskyttede.
- Denne release indeholder fortsat ingen LEGO-layout- eller X/Y-spacing-funktioner; de afventer manuel accept af Undo/Redo-stabiliteten.


== Version 0.8.16 – Designer — stabil Undo/Redo og direkte Auto-kasser drop ==

Nyt:
- Fortryd/Gendan bruger nu samme restore-transaction fra toolbar, tastatur, kommandopalet og lokal kladde-gendannelse.
- Syntetiske input/change-events fra restore og preview-rebuild undertrykkes fortsat, så de ikke opretter falske historiktrin.
- Ægte brugerinput og kendte strukturhandlinger umiddelbart efter Undo er igen history-eligible og må derfor oprette et nyt historiktrin.
- Redo-kæden afbrydes fortsat korrekt, når brugeren laver en ny ændring efter Undo, fordi den eksisterende history stack genbruges uændret.
- Direkte Kasse-drop på selve Auto-kasser/Grid-canvaset bruger nu hele den synlige Grid-flade som hitområde under drag i stedet for kun det lille footer-dropfelt.
- Nested source rows skjules kun, når den autoritative Kasse-runtime har markeret dem som child-source; LayoutParentKey/data-h18-nested-in-box alene må ikke få en Kasse til at forsvinde.
- Den målrettede browser-QA dækker toolbar/kommandopalet/keyboard/lokal kladde, syntetisk kontra ægte input, hurtig strukturændring efter Undo samt to eksisterende Kasser droppet direkte på Auto-kasser-canvaset.
- Editor Runtime Fast QA og Architecture QA er bestået på hotfix-PR'en; Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.
- Denne release indeholder ingen LEGO-layout-, X/Y-spacing- eller øvrige nye designerfunktioner; de afventer manuel accept af Undo/Redo-stabiliteten.


== Version 0.8.15 – Designer — én Auto-kasser runtime og deterministisk Fortryd/Gendan ==

Nyt:
- Auto-kasser oprettes fortsat som én tom Grid-container uden automatisk ekstra Kasse.
- Den direkte nesting-runtime er nu eneste aktive Kasse/Auto-kasser placeringsautoritet; den tidligere v0.8.14 Auto-kasser-adapter er pensioneret fra aktiv enqueue.
- Nye og eksisterende Kasser kan parent'es direkte til Auto-kasser via den eksisterende LayoutParentKey-model; den målrettede Chrome-reproducer flytter to eksisterende topniveau-Kasser ind i en tom Auto-kasser og verificerer, at begge forbliver synlige.
- Kasse/Auto-kasser-kompositionen overvåger nu base-editorens preview-rebuilds og genrenderer den synlige komposition, hvis de skjulte source rows stadig er parentede men Grid/Kasse-previewet er blevet fjernet.
- Kasse-preview viser v0.8.15-badge, så den aktive runtime kan verificeres direkte ved manuel test.
- Fortryd/Gendan kasserer nu restore-afledte editorHistoryRecordNow-captures i stedet for at afvikle dem efter settle-perioden; den kasserede capture returnerer 0, så editorHistoryTimer ikke efterlades som et falsk pending trin.
- Den målrettede system-Chrome QA verificerer, at Undo-capture fortsat er 0 efter restore-spærringen, så 4→3→4-oscillation og stale snapshot-genindlæsning ikke genopstår via denne kodevej.
- Produktionskoden passerede Architecture QA på PHP 8.0, 8.2 og 8.3 inklusive protected Vehicle/Event/Gallery og alle v0.8.15 Kasse/Undo-kontrakter; den endelige PR-head passerede desuden den målrettede system-Chrome Kasse/Undo-regression.
- Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.


== Version 0.8.14 – Designer — stabil Auto-kasser, Kasse-drop og Fortryd/Gendan ==

Nyt:
- Auto-kasser oprettes nu som selve Grid-containeren uden automatisk at oprette en ekstra Container/Kasse ved samme handling.
- Auto-kasser har nu et eksplicit synligt Kasse-dropfelt, så nye og eksisterende Kasser kan slippes direkte ind i rækken via den eksisterende LayoutParentKey-model.
- Kasse i Kasse og venstre/højre side-drop bevares med cycle-guard og maksimal nesting-dybde 2; side-drop er fortsat den handling der kan oprette en ny Auto-kasser/Grid-komposition omkring topniveau-Kasser.
- Den forsinkede legacy Kasse-default-writer i box-content-layout ejer ikke længere drag/drop og kan derfor ikke efterbehandle samme drop eller oprette ekstra historikændringer.
- Kasse-preview viser v0.8.14-badge, så den aktive runtime kan verificeres direkte under manuel test.
- Fortryd/Gendan kører nu gennem en restore-transaktion, der holder editorens MutationObserver og afledte editorHistoryRecordNow-captures ude gennem settle-perioden, så en Undo ikke straks optager sin egen restore som et nyt trin.
- Et palette-drop forbliver idempotent med dropHandled og post-drag click-suppression; ét element-drop må kun oprette ét element.
- QA #357 passerede PHP 8.0, 8.2 og 8.3, alle Kasse-kontrakter inkl. v0.8.14, samlet Node-syntaxcheck samt Chromium, Firefox og WebKit.
- Protected Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.


== Version 0.8.13 – Designer — én Kasse-runtime, Kasse i Kasse og lineær Fortryd/Gendan ==

Nyt:
- En enkelt Kasse opretter nu kun én Container. Grid/Auto-kasser oprettes kun, når en Kasse eksplicit slippes i venstre/højre side-dropzonen ved en anden topniveau-Kasse.
- Kasser kan nu trækkes IND I andre Kasser inden for den eksisterende cycle-guard og maksimale nesting-dybde på 2.
- Den direkte nesting-runtime er nu eneste aktive Kasse-placeringsautoritet; den gamle v0.8.10 inline Kasse-composer er pensioneret, så flere runtimes ikke længere behandler samme drop.
- Et palette-drag/drop kan kun fuldføres én gang via dropHandled, og et efterfølgende browser-click efter drag undertrykkes, så ét Tekst-drop ikke kan oprette flere Tekst-elementer.
- En nested Kasse beholder sit eget synlige Indhold i kassen-preview og sin indvendige dropzone, så målområdet kan aktiveres og bruges direkte.
- Fortryd/Gendan bruger fortsat den eksisterende 50-trins editorhistorik, men restore-mutationen undertrykkes kortvarigt fra historikkens MutationObserver, så en gendannet tilstand ikke registrerer sig selv som et nyt trin og skaber A/B-oscillation.
- LayoutParentKey/Order er fortsat eneste lagringsmodel; der er ikke indført parallel persistence eller offentlig runtime-cutover.
- Architecture QA #352 passerede PHP 8.0, 8.2 og 8.3, protected Vehicle/Event/Gallery, alle Kasse-kontrakter inkl. v0.8.13, samlet Node-syntaxcheck samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.


== Version 0.8.12 – Designer — drop ind i Kasser under Auto-kasser ==

Nyt:
- Kasser, der ligger side om side i Grid/Auto-kasser, viser nu deres rigtige Indhold i kassen-preview og indvendige dropzone i den synlige Kasse-flise.
- Et element, der trækkes fra Elementer-panelet ned i en synlig Kasse under Auto-kasser, mappes nu tilbage til den korrekte skjulte source-Kasse via LayoutParentKey.
- Eksisterende elementer, der flyttes med sortable-håndtaget, hit-testes nu mod den synlige Kasse i Auto-kasser og kan derfor også flyttes ind i den.
- Drop-target markering vises på den synlige Kasse-flise, så det er tydeligt hvilken Kasse modtager elementet.
- Kasse-source-rækker forbliver skjult i Auto-kasser, mens deres child-elementer gengives synligt inde i Kassen i stedet for at se ud til at forsvinde.
- Den eksisterende LayoutParentKey/Order-model er fortsat eneste lagringsmodel; der er ikke indført parallel persistence.
- Architecture QA #344 passerede PHP 8.0, 8.2 og 8.3, v0.8.11-regressionskontrakten, den nye v0.8.12 Auto-kasse drop-kontrakt, samlet Node-syntaxcheck samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.


== Version 0.8.11 – Designer — direkte Kasse-komposition og sikre side-dropzoner ==

Nyt:
- Kasse-kompositionen ligger nu direkte i den aktive nesting-runtime i Sider-editoren i stedet for at være endnu et parallelt visuelt overlay.
- Tekst, billeder, knapper og andre elementer med LayoutParentKey til en Kasse beholder deres source-række til lagring/versionering, men source-rækken skjules altid fra den flade canvas — også mens elementet er valgt.
- Under-elementer vises som rigtige klonede canvas-previews inde i Indhold i kassen og kan åbnes i Inspector via Rediger.
- Et synligt v0.8.11-badge i Kassen viser, at den nye runtime faktisk er aktiv på testinstallationen.
- Topniveau-Kasser viser altid tydelige venstre/højre dropzoner, så en anden Kasse kan placeres ved siden af i stedet for over eller under.
- Både nye Kasser fra Elementer-panelet og eksisterende Kasser flyttet med sortable-håndtaget bruger samme side-placement-flow.
- Side-by-side genbruger den eksisterende Grid/Auto-kasser-model og LayoutParentKey/Order; der er ikke indført en ny persistence-model.
- Cycle guard og ordre-synkronisering er bevaret for eksisterende elementer, der flyttes ind i en Kasse.
- Architecture QA #338 passerede PHP 8.0, 8.2 og 8.3, alle Kasse-kontrakter, samlet Node-syntaxcheck samt Chromium, Firefox og WebKit.
- Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.


== Version 0.8.10 – Designer — aktiv Kasse-runtime og side-by-side ==

Nyt:
- Kasse-kompositionen er nu bundet direkte til de allerede aktive nesting/box-content handles i Sider-editoren i stedet for at afhænge af det separate v0.8.9-addon.
- Kasser viser et synligt v0.8.10-badge i editoren, så manuel QA straks kan bekræfte at den nye runtime faktisk er indlæst.
- Elementer med LayoutParentKey til en Kasse skjules fra den flade canvas-række via en dedikeret data-attribut og vises som rigtige previews inde i Indhold i kassen.
- Child-markering ændrer ikke længere topniveau-rækkens CSS-klasser og vækker derfor ikke den ældre box-tools observer, som kunne overskrive Auto-kasser-previewet.
- Både den dedikerede Kasse og et almindeligt Container-element genkendes ved drag fra Elementer-panelet.
- Nye Kasser/Containere får tydelige venstre/højre Sæt Kasse ved siden af drop-zoner og grupperes i den eksisterende Auto-kasser/Grid-model.
- Allerede eksisterende Kasser kan nu også trækkes med det normale rækkehåndtag til venstre eller højre for en anden Kasse.
- Composition observeren er ikke-recursiv og Inspector/preview ændringer har eksplicit refresh, så runtime ikke kan trigge sin egen redraw i loop.
- Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URL'er og I10 public cutover er fortsat uændrede og beskyttede.
- v0.8.10 udgives som manuel testkandidat; GitHub Architecture QA #322 står fortsat i runner-kø, mens den præcise inline JavaScript-blok er valideret separat med node --check.


== Version 0.8.9 – Designer — visuel Kasse-komposition og Auto-kasser ==

Nyt:
- Elementer med LayoutParentKey til en Kasse vises nu visuelt inde i Kassen i editoren i stedet for som en separat række over eller under den.
- De oprindelige child-rækker bevares skjult i DOM'en, så eksisterende gemning, versionshistorik og schema fortsat er autoritative uden datamigrering.
- Indhold i en Kasse vises som rigtige canvas-previews med en Rediger-handling, og elementer kan flyttes mellem Kasser fra den visuelle komposition.
- Auto-kasser viser nu de faktiske Kasser side om side i editoren i stedet for at lade deres source-rækker stå lodret under hinanden.
- Antallet af desktop-kolonner i Auto-kasser synkroniseres med antallet af Kasser; på smallere editorbredder stables den visuelle komposition i én kolonne.
- Når en ny Kasse trækkes fra Layout+-biblioteket, vises tydelige venstre/højre drop-zoner på en eksisterende Kasse til placering ved siden af.
- Kasser i en eksisterende Auto-kasser-række kan omarrangeres via deres visuelle proxy uden et nyt storage-format.
- Vehicle/Event/Gallery, offentlig Header/Footer-rendering, URLs og I10 public cutover er fortsat uændrede og beskyttede.


== Version 0.8.8 – Designer UX — scrollbar, rigtig Kasse-nesting og Header/Footer baseline ==

Nyt:
- Elementer/Funktioner-panelet har nu sin egen lodrette scrollbar, uafhængigt af canvas og Inspector.
- Kasser har en tydelig indvendig drop-zone, så elementer kan trækkes IND I en Kasse i stedet for kun før eller efter den.
- Både nye elementer fra elementbiblioteket og allerede oprettede elementer kan nestes i Kasser via den eksisterende LayoutParentKey-model.
- Eksisterende elementer kan flyttes ind i Kasser via den eksisterende jQuery UI-sortering, og rækkefølgen synkroniseres efter drop.
- Header/Footer-migrationen har fået en read-only legacy baseline med marker-kontrol og deterministisk source hash som fundament for senere shadow-import.
- Den nuværende offentlige Header/Footer-rendering ændres ikke, og Vehicle/Event/Gallery forbliver på den beskyttede runtime.
- Public Header/Footer/I10 cutover er fortsat låst; v0.8.8 er beregnet til manuel test af Designer-funktionerne.


== Version 0.8.7 – Ultimate Designer UX — visuelle elementer, kasser og nesting ==

Nyt:
- Nyt visuelt elementbibliotek med søgning, kategorier, favoritter, Seneste, beskrivelser og drag-preview.
- Auto-kasser vises tydeligt side om side i editoren med separat desktop- og mobil-spacing.
- En Kasse kan indeholde flere almindelige elementer som Billede, Tekst, Overskrift og Knap via den eksisterende LayoutParentKey-model.
- Hver Kasse kan styre sit interne child-layout: lodret/vandret retning, justify, align, wrap, desktop/mobile gap og mobil-stacking.
- Hver Kasse kan have egne farver, skrifter, fontstørrelser, padding, kantbredde og hjørneradius; 0 px giver firkantede hjørner.
- Tabel forbliver et semantisk tabelværktøj og kan sættes til 0 px kantbredde for helt usynlige cellekanter.
- Vehicle/Event/Gallery forbliver på den beskyttede legacy runtime, og I10 public cutover er fortsat låst.


== Version 0.8.6 – I10 Signed Cutover Preflight ==

Nyt:
- Source-drift detection sammenligner shadow-copyens SourceHash med den aktuelle legacy editor-state før fremtidig cutover kan godkendes.
- Cutover preflight kræver komplette manuelle I9-gates, korrekt I10-rækkefølge, gyldig shadow acceptance samt WordPress page ID og permalink.
- Eligible preflight snapshots signeres med HMAC og bindes til præcis target-identitet, source hashes og blockers.
- Signerede preflight-records er tidsbegrænsede og bliver stale/ugyldige ved source-drift eller ændret preflight-state.
- Preflight har altid Executable=false og PublicMutationAvailable=false; den giver ingen aktiveringsret.
- Admin-UI viser blockers, source hashes og om et gemt signeret preflight stadig er current.
- Der findes stadig ingen activate/cutover/publish-handler, og WordPress-posts, URLs samt hangar18_manager_pages_v1 ændres ikke.
- Vehicle/Event/Gallery forbliver blokeret af CompatibilityPolicy på legacy runtime.


== Version 0.8.5 – Auto-kasser, Tabel og kompakt Side Health ==

Nyt:
- Auto-kasser genbruger eksisterende Grid/Container: 1 kasse = 100 %, 2 = 50/50, 3 = tre lige kolonner osv. op til 6.
- Antallet af desktop-kolonner følger automatisk direkte under-kasser; mobil starter på én kolonne.
- Afstand mellem kasser styres med eksisterende desktop/mobile LayoutGap-indstillinger.
- Hver Kasse er et normalt Container-element og har derfor egne farver, typografi, fontstørrelser, padding, border, shadow og responsive overrides.
- Nyt visuelt Tabel-værktøj med rækker/kolonner, header-række, zebra, farver, fontstørrelse, celle-padding og direkte celle-redigering.
- Tabel kan bruge vandret scroll på mobil og gemmes gennem det eksisterende sanitiserede HTML-element.
- Side Health starter sammenklappet i Inspector og viser kompakt score + fejl/advarsler, så Indhold/Typografi/Design/Avanceret ikke overskygges.
- Layout-værktøjerne følger Inspectorens valgte element korrekt, også når element-body flyttes ind i Inspector.
- Ingen public cutover eller ny frontend-renderer aktiveres; Vehicle/Event/Gallery forbliver på legacy runtime.


== Version 0.8.4 – I10 Shadow Acceptance Ledger ==

Nyt:
- Side-specifik shadow acceptance kræver syv manuelle checks: desktop, tablet, mobile, save, preview, revision og rollback.
- Acceptance kræver miljø/browser/device, evidensreference og eksplicit human confirmation.
- AcceptedForSequence beregnes server-side og kan ikke sættes direkte fra request.
- Acceptance bindes til den aktuelle shadow SourceHash; en genskabt/ændret shadow gør gammel acceptance automatisk stale.
- Acceptance lukker ikke de globale I9-gates og aktiverer ikke en offentlig side.
- Ingen activate/cutover/publish-handler tilføjes; WordPress-posts, URLs og hangar18_manager_pages_v1 forbliver uændrede.
- Vehicle/Event/Gallery forbliver låst af CompatibilityPolicy på legacy v0.5.30-runtime.


== Version 0.8.3 – I10 Conversion Planner ==

Nyt:
- Kontrolleret I10 conversion planner med fast rækkefølge: sammenligningsside, Hjem, Om, Kontakt, Bliv medlem og til sidst Vehicle/Event/Gallery.
- Alle manglende I9 manuelle gates vises som eksplicitte blockers for fremtidig cutover.
- Shadow workspace kan kopiere ikke-beskyttede legacy editor-states med deterministisk source hash uden at ændre originalen.
- Planner-fasen har PublicMutationAvailable=false; shadow-records har PublicActivation=false og Accepted=false.
- Der registreres ingen activate/cutover/publish-handler i denne version, og WordPress-posts, URLs samt hangar18_manager_pages_v1 ændres ikke.
- Vehicle/Event/Gallery forbliver eksplicit blokeret af CompatibilityPolicy og legacy v0.5.30-runtime.


== Version 0.8.2 – I9 Manual QA & rollback rehearsal ==

Nyt:
- Manual QA Dashboard viser alle otte obligatoriske I10-gates og deres dokumenterede status.
- Manuel PASS kræver eksplicit bekræftelse, miljø/browser/device og evidensreference; bruger-ID og UTC-tid gemmes.
- Automatisk test/preflight kan ikke udgive sig for manuel evidens eller lukke en manuel gate.
- Rollback preflight kører kun på en in-memory kopi af legacy page-store og verificerer original/mutated/restored hashes.
- Preflight skriver ikke til hangar18_manager_pages_v1 og kan aldrig sætte migration-rollback-live-copy til PASS.
- I10 forbliver blokeret indtil de krævede manuelle/live gates faktisk er gennemført. Frontend og Vehicle/Event/Gallery ændres ikke.


== Version 0.8.1 – I8 AI forslag ==

Nyt:
- Provider-neutral AI registry via hangar18_ud_ai_providers; provider adapters håndterer selv credentials.
- AI settings gemmer kun Enabled og ProviderId; API keys/secrets/passwords gemmes ikke i WordPress options.
- Tekstforslag kører i isoleret sandbox og oprettes altid som pending forslag.
- Accept/reject er bundet til et tidsbegrænset HMAC-signeret proposal-token.
- Accept producerer kun reversible Apply/Undo-data; I8 skriver ikke forslag direkte til sider.
- AI kræver hangar18_use_ai eller administrator fallback og ændrer ikke frontend, Vehicle/Event/Gallery eller eksisterende sider.


== Version 0.8.0 – I7 Permissions & Design Lock ==

Nyt:
- Role/capability migration preview viser præcist hvad der vil blive oprettet og tilføjet før installation.
- Rolle-installation er additive-only: ingen eksisterende capability eller rolle fjernes.
- Installation kræver manage_options, nonce og eksplicit confirmation.
- UD Administrator/Designer/Editor/Event/Gallery roller kan oprettes/opdateres via den eksisterende WordPress role API.
- WordPress Administrator beholder sin eksisterende rolle og får kun manglende UD capabilities tilføjet.
- Design Lock policy kan konfigurere struktur/design-lås og frigivne content-properties.
- Design Lock håndhæves ikke i legacy Sider-editoren før I10; edit_pages fallback bevares.
- Ingen bruger får automatisk ændret rolle. Frontend og Vehicle/Event/Gallery ændres ikke.


== Version 0.7.9 – I6 Import / Export ==

Nyt:
- Sidepakker kan eksporteres med schema/checksum og valideres/previewes ved import uden side-write.
- Artifact packages kan eksporteres fra shadow templates/menuer/components og Portability Workspace.
- Artifact import starter altid med dry-run og viser actions, conflicts og ID-remaps.
- Confirmation er bundet til et tidsbegrænset HMAC-signeret dry-run token for præcis package/strategi/plan.
- Uløste asset/artifact references blokerer mutation.
- Bekræftet import går kun til isoleret Portability Workspace og tager automatisk pre-import backup.
- Workspace kan gendannes fra backup; eksisterende sider, frontend og Vehicle/Event/Gallery ændres ikke.


== Version 0.7.8 – I5 Asset Manager + menuvalg ==

Nyt:
- I5 Asset Manager UI oven på native WordPress Media IDs med mapper, collections, tags og metadata.
- Responsive focal point for desktop/tablet/mobil med live preview.
- Usage-inspector finder MediaId-referencer på sider, components, templates og data/meta.
- SHA-256 dubletscan er read-only og sletter/fletter aldrig filer automatisk.
- WebP/AVIF genereres som namespaced .h18.webp/.h18.avif derivater; original og eksisterende derivater overskrives aldrig.
- Menu UI har eksplicit Tilgængelige sider med valg/fravalg; en side kan eksistere uden at være i menuen.
- Frontend og Vehicle/Event/Gallery forbliver uændrede; ingen sider konverteres.


== Version 0.7.7 – I4 Live Side Health ==

Nyt:
- Side Health vises direkte i den eksisterende Sider-editor uden at konvertere siden.
- Analysen bruger den aktuelle DOM/form-state og medregner derfor også ugemte ændringer.
- Samlet score samt Design, Mobile, Accessibility, Performance og SEO delscorer.
- Filtrerbare issues med severity, code og konkrete ElementKey-links til Navigator.
- Klik på et issue vælger/scroller til det konkrete element i den eksisterende editor.
- Read-only AJAX bridge er capability/nonce-beskyttet og begrænser JSON-størrelse og antal elementer.
- Side Health-controlleren indeholder ingen page-save/update/delete primitives.
- Vehicle/Event/Gallery og frontend-rendering er fortsat uændret.


== Version 0.7.6 – I3 Menu UI v2 ==

Nyt:
- Shadow-only Menu UI v2 oven på den generiske MenuService.
- Desktop presets: klassisk, floating pill, mega-menu og side rail.
- Mobil presets: klassisk, off-canvas, fullscreen overlay og bottom navigation.
- Hover/aktiv motion presets med reduced-motion hensyn i preview.
- Nested menu-data med drag/drop, op/ned, indent/outdent, ikon, badge, beskrivelse og ComponentId mega-panel.
- Keyboard-preview med top-level piletaster, submenu åbning og Escape.
- Menu presentation gemmes separat fra menu-data og eksisterende gamle menu-records får sikre defaults.
- Dangerous javascript/data/vbscript URL-schemes afvises, og controlleren kræver capability + nonce + sanitization.
- Den offentlige legacy-menu og eksisterende sider/Vehicle/Event/Gallery er fortsat uændrede.


== Version 0.7.5 – I2 Visual Header/Footer Builder ==

Nyt:
- Ultimate Designer har nu en visuel Header/Footer Builder i shadow mode.
- Header/Footer templates bruger samme Sections-tree og property-navne som sideeditoren.
- Opret, vælg, rediger, slet, tilføj/fjern elementer samt drag/drop og ↑/↓ rækkefølge.
- Parent Key understøtter nested Container/Flex/Grid-struktur med live admin-preview.
- Typografi/design gemmes server-side: body/heading fonts, body/H1/H2/H3 størrelser, alignment, padding samt global/custom farver.
- Dedikeret Ultimate Designer admin-JS/CSS indlæses kun på den nye adminside og cache-bustes med version/filemtime.
- Security QA skelner HTTP-controllerlaget fra service/domain-laget og kræver capability, nonce og sanitization ved mutationer.
- Ingen global/public Header/Footer assignment aktiveres; eksisterende frontend og Vehicle/Event/Gallery forbliver legacy.


== Version 0.7.4 – Ultimate Designer integration dashboard ==

Nyt:
- Den namespacede Ultimate Designer-arkitektur autoloades nu fra pluginet i admin-kontekst.
- Ny Hangar18 Manager → Ultimate Designer-side viser Site Builder templates/menuer, assets, permissions og QA-status.
- I1–I10 integrationsbackloggen er synlig og dokumenteret.
- Manual/live release gates vises separat fra automated QA.
- Integrationen er admin-only: ingen frontend-renderer, side, URL eller Vehicle/Event/Gallery-domain skiftes.
- PHP 8.0/8.2/8.3 integration QA og protected-domain regression er grøn.


== Version 0.7.3 – Valgfri overskrift og linjeskift ==

Rettet:
- Overskrift på almindelige sideelementer er eksplicit valgfri; elementet kan bestå af ren tekst uden overskrift.
- Afstemning beholder sin semantiske Spørgsmål-overskrift.
- Enter i tekstfeltet bevares som synligt linjeskift i canvas-preview; tom linje giver nyt afsnit på frontend via wpautop.
- Den ældre WhatIf-baserede JavaScript-regel kan ikke længere gøre Gem-kommentaren required igen.
- Egen Gem-kommentar forbliver valgfri og automatisk ændringsresumé bruges som standard.
- PHP 8.0/8.2/8.3 QA, workflow/quality E2E og Vehicle/Event/Gallery-kontrakten er grøn.


== Version 0.7.2 – Gem og Typografi rettet ==

Rettet:
- Egen kommentar ved Gem er eksplicit valgfri i markup og JavaScript; stale/custom browser-validity ryddes før submit.
- Admin CSS/JS cache-bustes med pluginversion + filemtime, så en gammel admin.js ikke bliver hængende efter opdatering.
- Editor viser aktiv version direkte i sideeditorens header.
- Typografi-fanen var tom fordi CSS skjulte parent-containeren til typography-panelet. Nesting-reglen er rettet.
- Typografi viser nu de eksisterende funktionelle indstillinger: brødtekst-font, overskrift-font, brødtekst-størrelse samt H1/H2/H3-størrelser.
- PHP 8.0/8.2/8.3 QA, workflow regression og Vehicle/Event/Gallery-kontrakten er grøn.


== Version 0.7.1 – Automatisk gemmeresumé ==

Nyt:
- Håndskrevet ændringsbeskrivelse er ikke længere obligatorisk ved Gem eller Ctrl/Cmd+S.
- Editor sammenligner indlæst og aktuel side og laver automatisk et kort resumé af titel, tilføjede/fjernede/flyttede elementer samt indhold, typografi, design, layout, responsive og dynamic-data ændringer.
- Det automatiske resumé vises før gemning og genberegnes ved submit.
- Serveren laver fallback-resumé, hvis browserresuméet mangler.
- Versionshistorikken gemmer AutoChangeSummary og UserChangeNote separat og bevarer kombineret ChangeNote for bagudkompatibilitet.
- Egen kommentar er valgfri og bruges til fx begrundelse eller oplysninger som ikke kan udledes af side-state.
- Save-summary QA er grøn på PHP 8.0, 8.2 og 8.3, og Vehicle/Event/Gallery-kontrakten er uændret.


== Version 0.7.0 – E14 Automated QA baseline ==

Nyt:
- Automated browser-engine matrix på Chromium, Firefox og WebKit for menu-keyboard, modal focus trap, formularfokus og reduced motion.
- Security gate for den nye arkitektur samt eksplicit capability/preview/import safety checks.
- Performance budgets for public runtime, portability flow og Side Health.
- Migration/rollback fixture med checksum-protected backup og exact restore.
- MVP/v1 end-to-end tests for save/preview/publish/restore, Site Builder, menu, form, quality og portability.
- ReleaseReadiness adskiller automated evidence fra manual/live evidence; grøn CI kan ikke markere live acceptance som færdig.
- Administrator/designer onboarding og endelig migration-rækkefølge er dokumenteret.
- Manual Chrome/Edge/Firefox/Safari brand-test, screen-reader, test2 live E2E, Vehicle/Event/Gallery regression og live-copy migration er stadig pending.
- Ingen eksisterende sider er konverteret.


== Version 0.6.9 – E13 Portability ==

Nyt:
- Page + global styles JSON med package/page schema og SHA-256 checksum samt identisk roundtrip.
- Components/templates/menus/forms kan pakkes med stabile ExportId-referencer.
- Dry-run er standard; collisions vises før write og kan remappes, skips eller blokeres eksplicit.
- artifact:// og asset:// references remappes kun via validerede mapping-tabeller.
- Asset manifest matcher target Media IDs via SHA-256 og rapporterer Broken references i stedet for silent drop.
- Bekræftet import tager automatisk pre-import backup og kører mutationsdelen atomisk med rollback ved referencefejl.
- E8 pre-publish backup regressionstestes fortsat. Ingen eksisterende sider konverteres endnu.


== Version 0.6.8 – E12 AI suggestion layer ==

Nyt:
- Provider-neutral AI integration point uden repository/write-adgang.
- AI tekstforslag ændrer aldrig content uden eksplicit accept og indeholder reversible Apply/Undo-data.
- Prompt-to-layout kandidat skal bestå den normale Page Schema-validering før preview/insert.
- AI design review må kun foreslå ændringer på eksisterende element/property-referencer.
- AI accessibility-forslag begrænses til konkrete alt/label-fund og kan afvises individuelt.
- Dedikeret hangar18_use_ai capability; ingen provider/API credentials konfigureres i denne release.
- PHP 8.0/8.2/8.3 QA og Vehicle/Event/Gallery-kontrakten er grøn.


== Version 0.6.7 – E11 Side Health ==

Nyt:
- Accessibility analyzer for heading order, alt text, labels, focus og målbar kontrast med elementreference.
- Responsive analyzer finder fixed-width overflow, små touch targets, lille tekst og kritisk skjult mobilindhold.
- Design consistency analyzer finder off-token farver, lokale font overrides og spacing/radius outliers.
- SEO metadata-model/analyzer for title, description, H1, canonical/index/follow og social metadata.
- Performance analyzer finder store assets, dyb DOM/layout nesting og unødvendige feature-moduler.
- Side Health samler Design, Mobile, Accessibility, Performance og SEO score og viser HardFailures separat.
- Analyzer-laget er read-only og omskriver aldrig sider automatisk.


== Version 0.6.6 – E10 Permissions ==

Nyt:
- Named least-privilege capabilities for settings, design, components, templates, data schemas, content, assets, publish, custom code, events og galleries.
- Rolleopskrifter for Administrator, Designer, Editor, Eventansvarlig og Gallery Manager.
- Design/structure lock beskytter layout og styling men kan frigive konkrete content fields.
- Component editable inputs begrænser content-only roller til eksplicit frigivne felter.
- Domain scope kan begrænse roller til fx Event eller Gallery data.
- WordPress role installer er eksplicit/passiv og overtager ikke nuværende legacy permissions endnu.
- PHP 8.0/8.2/8.3 QA og Vehicle/Event/Gallery-kontrakten er grøn.


== Version 0.6.5 – E9 Asset Manager ==

Nyt:
- Asset metadata-overlay med mapper, collections og tags uden at ændre native WordPress Media IDs.
- Usage inspector scanner sider, komponenter og data entries for MediaId-referencer før senere sletning.
- Responsive focal points omsættes til object-position for desktop/tablet/mobile.
- WebP/AVIF-optimeringspipeline opretter kun understøttede derivater og bevarer altid originalen.
- SHA-256 dubletdetektion er read-only og sletter/fletter aldrig automatisk.
- PHP 8.0/8.2/8.3 QA og Vehicle/Event/Gallery-kontrakten er grøn.


== Version 0.6.4 – Gem-toolbar og E8 Workflow ==

Nyt og rettet:
- Tydelig Gem-knap i toppen af sideeditoren samt Ctrl/Cmd+S.
- Save-status viser Gemt, Ikke gemt, Gemmer eller valideringsfejl, og browseren advarer ved ugemte ændringer.
- E8 Workflow core: autosave snapshots uden revisionsspam og permanente revisioner med bruger, tidspunkt, note og state hash.
- Restore opretter en ny revision i stedet for at overskrive historikken.
- Structured revision diff for added/removed/moved/property changes.
- Expiring/revocable HMAC-signerede preview tokens for desktop/tablet/mobile working-state preview.
- Working/public staging model med atomisk publish og pre-publish backup.
- PHP 8.0/8.2/8.3 QA er grøn; Vehicle/Event/Gallery legacy-runtime er uændret.


== Version 0.6.1 – Inspector layout hotfix ==

Rettet:
- Sider-editorens Inspector-faner og settings kan ikke længere overlappe hinanden i den smalle højre sidebar.
- Inspector-fanerne bruger et responsivt wrapping grid med tydelig afstand til indstillingerne nedenunder.
- Inputs, selects og tekstfelter holdes inden for Inspector-panelets bredde.
- Vehicle/Event/Gallery runtime, data, markup og CSS hooks er uændret.


== Version 0.6.0 – Architecture Foundation, UD-060 og større sideeditor ==

Nyt:
- Ny ikke-invasiv Ultimate Designer architecture foundation med namespaces, registries, schema validation, repositories, security/logging contracts og passive WordPress adapters.
- Runtime bridge kører fortsat i shadow mode og må ikke overtage eksisterende Vehicle/Event/Gallery handlers.
- UD-060: generiske Vehicle, Event og Gallery starter schemas/presets oven på Dynamic CMS-motoren; ingen specialmotor og ingen automatisk datamigration.
- Sider-modulet udnytter nu hele den tilgængelige WordPress-adminbredde, så sideopbygning/canvas får markant mere arbejdsplads.
- Sider får en tydelig Ny tom side-funktion samt genvej til oprettelse fra Page Template.
- Retter Page Template-oprettelse, så nye managed side-slugs bevares korrekt i stedet for at kunne falde tilbage til Hjem.
- Vehicle/Event/Gallery beholder eksisterende v0.5.30 markup, CSS hooks, URLs, data og legacy runtime-kontrakt.
- Releasepakken indeholder nu src/ med architecture foundation og validerer den ved build/installationspakke-QA.


== Version 0.5.25 – E5 Query Builder v1 ==

Nyt:
- UD-055: generisk Query Builder v1 for custom data med datatype, ét typevalideret filter, sortering, retning og limit
- text understøtter eq/neq/contains; number eq/neq/gt/gte/lt/lte; date eq/before/after; bool og media sikre equality-filtre
- sortering kan ske efter titel, oprettet, ændret eller kompatibelt schemafelt
- limit håndhæves server-side til 1–100 resultater
- admin-preview og frontend-shortcode bruger præcis samme run_custom_data_query()-motor
- frontend-shortcode [hangar18_data_query ...] viser kun publicerede data-entry-titler; drafts/private eksponeres ikke
- Query Builder bygger udelukkende WP_Query/get_posts-argumenter og query-klare _h18_field_<key> meta fra v0.5.23; ingen rå SQL
- generated shortcode vises efter preview, så samme query kan reproduceres på frontend
- page-editor schema forbliver 1.19
- advanced AND/OR, relation og pagination er fortsat UD-056; template-repeat pr. resultat er UD-057

== Version 0.5.24 – E5 Dynamic binding ==

Nyt:
- UD-053: hver Hangar18-side kan vælge en current data context som datatype + konkret entry
- elementegenskaber kan bindes til current context: Title, Content, MediaId og begge knappers tekst/link
- bindinger er typevaliderede: media kan kun drive billeder, links kun text fields, mens text/number/bool/date kan drive sikre tekstegenskaber
- static elementværdier ændres ikke og bruges som fallback, hvis context eller felt ikke længere findes
- runtime validerer altid datatype, entry og field-type igen; admin-UI er ikke sikkerhedsgrænsen
- canvas-preview bruger samme current context og viser også dynamiske WordPress-medier
- Bindings serialiseres med Patterns, linked component definitions og Page Templates uden at introducere ny delt identitet
- page-editor schema løftes bagudkompatibelt til 1.19
- foundation er klar til UD-057 Repeater/Query list, der senere kan skifte current context pr. resultat

== Version 0.5.23 – E5 Dynamic CMS foundation ==

Nyt:
- UD-051: generisk custom datatype schema builder under Hangar18 Manager → Data
- schemas understøtter text, number, bool, date og media fields med stabile keys, labels, required-flag og validering
- schema-struktur kræver manage_options; entry CRUD kræver edit_pages
- datatype-key er immutable efter oprettelse, og datatype-delete blokeres når entries stadig findes
- UD-052: generisk admin entry editor med create/read/update/delete for alle custom datatyper
- entries gemmes som privat Hangar18 custom post type med datatype-meta, samlet values-map og query-klare _h18_field_<key> meta-felter
- number/date/media valideres server-side; media skal pege på et rigtigt WordPress attachment
- media-felter bruger WordPress Media Library direkte i Data-editoren
- datamotoren er foundation for UD-053 dynamic binding og UD-055 Query Builder; Vehicle/Event/Gallery migreres senere via UD-060 presets, ikke via endnu en specialmotor
- page-editor schema forbliver 1.18; denne release ændrer ikke eksisterende side-JSON

== Version 0.5.22 – E4 Components completion ==

Nyt:
- UD-047: linked component variants deler base-definition og gemmer kun kontrollerede værdier for allerede frigivne component inputs
- variant anvendes før lokale instance-overrides, så lokale overrides fortsat har højeste prioritet
- variants oprettes/opdateres direkte fra en component-instance; variant med usage kan ikke slettes
- component revision stiger ved variantændringer, og global definition-update bevarer eksisterende variants
- UD-048: eksisterende presets er nu eksplicit Patterns og kan gemme/indsætte et helt nested subtree med friske keys og bevaret intern parent-struktur
- gamle én-sektions presets migreres transparent til subtree Pattern-format ved læsning
- Patterns forbliver ikke-linked og indeholder aldrig linked component-instanser eller legacy
- UD-049: Page Templates gemmer hele selvstændige sider og kan oprette nye draft WordPress/Hangar18-sider med friske section keys
- template-oprettede sider markeres som Hangar18-managed og bliver automatisk tilgængelige i sideeditorens sidevælger
- Page Template usage spores som origin-metadata til audit, men siden er en fri kopi; senere template-ændringer påvirker den ikke
- Page Templates afviser legacy og linked component-instanser for at garantere ingen skjulte shared-instance side effects
- page-editor schema løftes bagudkompatibelt til 1.18

== Version 0.5.21 – E4 linked component engine foundation ==

Nyt:
- UD-043: Navigator tree får separat lagnavn, rename, hide/show, lock/unlock og realtime reorder-beskyttelse
- låste lag kan ikke trækkes, skjules eller duplikeres ved et uheld i editoren
- UD-044: et valgt layout-subtree kan gemmes som en rigtig linked component med intern nesting bevaret
- linked components gemmes i separat versioneret WordPress-option; eksisterende presets bevares som ikke-linked Patterns
- UD-045: component-instanser gemmer kun ComponentId + lokale overrides og resolver altid den aktuelle globale definition ved render, så én atomisk option-opdatering propagere til alle instanser
- global definition har monotont Revision-nummer; instans-editor viser aktuel revision og usage
- UD-046: ved oprettelse/opdatering vælger designeren eksplicit hvilke Title/Content/Image/Button inputs der frigives; layout/design er ikke overridable lokalt
- risky Content inputs for CSS/HTML/Shortcode/Embed frigives ikke
- linked component kan ikke indeholde legacy eller andre linked components, så recursive component cycles er blokeret i foundation
- UD-050: usage inspector scanner alle gemte Hangar18-sider og viser side + section key; komponent med usage kan ikke slettes
- component-instanser har eget canvas-kort og indgår i responsive visibility/layout som én node
- page-editor schema løftes bagudkompatibelt til 1.17

== Version 0.5.20 – E3 Design System completion ==

Nyt:
- globale redigerbare builder-breakpoints med standard 782 px mobil og 1199 px tablet, så eksisterende sider bevarer nuværende responsive adfærd
- globale motion-tokens: Fast, Normal og Slow samt global focus-ring farve og bredde
- elementer kan vælge Transition: Global, Fast, Normal, Slow eller eksisterende Custom hover-transition
- Focus-state med global, tilpasset eller ingen focus ring samt farve, bredde og offset
- Active-state med Ingen, Tryk 1 px eller Scale 97% for interaktive descendants
- Disabled-state med justerbar opacity for disabled/aria-disabled kontroller
- live canvas og kommandopalette kan nu vise Normal, Hover, Focus, Aktiv og Disabled
- page-editor media queries bruger de globale breakpoints uden at ændre headerens eksisterende responsive legacy-regler
- prefers-reduced-motion bevares; motion-tokens ændrer ikke brugerens reducerede motion-præference
- DesignerSchemaVersion løftes kompatibelt til 1.1 og page-editor schema til 1.16

== Version 0.5.19 – Section/Container/Flex/Grid layout foundation ==

Nyt:
- UD-021–023 layoutfundament: Container, Flex container og Grid container som native builder-elementer
- elementer kan placeres inde i en layout-parent via LayoutParentKey, mens storage fortsat er en flad revisionsvenlig sektionsliste
- frontend omdanner den flade model til et ægte DOM-træ med op til tre niveauer
- server-side validering af parent-type, manglende parent, selvreference, cykler og maksimal dybde
- Flex: row/column, wrap, justify, align, desktop/mobile gap og valgfri mobil-stack
- Grid: 1-6 desktopkolonner, 1-3 mobilkolonner, align og separate gaps
- Canvas og Navigator indrykker children og viser antal under-elementer i layout-containere
- responsive section styling, hover, visibility og typografi virker også for nested children
- retter samtidig checkbox-semantik for Carousel loop/pile/prikker samt nye layout-checkboxes
- page-editor schema løftes bagudkompatibelt til 1.15

== Version 0.5.18 – Carousel / Slider ==

Nyt:
- UD-031: Carousel/Slider som native sideeditor-element og med den eksisterende Cards-model som slides
- autoplay er FRA som standard og kan aktiveres med justerbart interval 2-20 sekunder
- loop, forrige/næste-pile og priknavigation kan slås til/fra separat
- keyboard-navigation med venstre/højre pil samt Home/End på priknavigationen
- touch swipe på mobil og tablet; swipe kræver mindst ca. 45 px bevægelse
- autoplay pauser ved hover og keyboard-fokus og genstarter først, når brugeren forlader carousellen
- prefers-reduced-motion deaktiverer autoplay og transitions automatisk
- slides bruger role=group/aria-roledescription=slide, live status og skjuler inaktive slides fra fokus/assistive tech
- hvert slide bevarer Card-baggrund, teksttone, kant, padding, radius og responsive indstillinger
- page-editor schema løftes bagudkompatibelt til 1.14 for carousel-adfærd

== Version 0.5.17 – Tabs og Accordion ==

Nyt:
- UD-030: nye Faner/Tabs og Accordion-elementer direkte i sidebyggeren
- begge elementer genbruger den eksisterende Cards/panel-model, så komponenter, Undo/Redo, autosave og copy/paste fortsætter uden parallel datamodel
- Tabs har semantisk tablist/tab/tabpanel-markup, roving tabindex og tastaturstyring med pile, Home og End
- Accordion bruger native details/summary for robust keyboard- og skærmlæserunderstøttelse
- paneler kan flyttes, aktiveres/deaktiveres og beholder eksisterende baggrund, teksttone, kant, padding, radius og responsive Card-indstillinger
- nye Tabs/Accordion oprettes med to startpaneler og kan have op til 12 paneler
- live canvas viser den første fane eller det første accordion-panel uden at ændre frontend-state
- page-editor schema forbliver 1.13; ingen ekstra paneldatamigrering er nødvendig

== Version 0.5.16 – E2 element primitives og sikre embeds ==

Nyt:
- UD-028: sikkert Icon/SVG-element med indbygget allowlist-baseret ikonbibliotek uden rå bruger-SVG
- UD-029: nye semantiske elementer for skillelinje, liste, badge og citat
- Divider-varianter: hel, stiplet, prikket og dobbelt; List-varianter: punkter, numre og flueben
- Badge kan være fyldt/outline, og Quote kan være standard/stort citat
- UD-032: separat Embed-element via WordPress oEmbed og separat avanceret Shortcode-element
- Shortcode autoriseres kun ved gemning af brugere med unfiltered_html/manage_options; lavere roller kan ikke ændre eller indsætte ny eksekverbar shortcode
- eksisterende autoriseret shortcode kan bevares af lavere roller, når selve shortcode-indholdet er uændret
- importerede Gutenberg lister/citater/separatorer konverteres til de nye semantiske elementer
- HTML-elementet udfører ikke længere nye shortcodes implicit; eksplicit Shortcode-element er sikkerhedsgrænsen
- page-editor schema løftes bagudkompatibelt til 1.13

== Version 0.5.15 – Multi-select, canvas workspace og context menu ==

Nyt:
- UD-017: Ctrl/Cmd/Shift+klik kan vælge flere sideelementer samtidig i canvas og Navigator
- fælles kompatible egenskaber kan batch-redigeres: baggrund, placering, padding, radius, opacity og synlighed
- Inspector viser tydeligt antal valgte elementer og skjuler batchfelter, som ikke understøttes af alle valgte elementer
- UD-018: canvas zoom 50-150%, 100%-reset, Outline mode og 16 px Guides-grid
- workspace-indstillinger gemmes lokalt i browseren og ændrer aldrig frontend-output
- UD-019: højreklik eller Shift+F10 åbner en keyboard-tilgængelig context menu på canvas/Navigator
- context menu indeholder redigér, multivalg, duplikér, design copy/paste, komponent, vis/skjul, flyt og fjern
- context menu understøtter piletaster, Home/End, Enter/Space, Tab-loop og Escape
- page-editor schema forbliver 1.12; alle funktioner er editor-only

== Version 0.5.14 – Kommandopalette og hurtignavigation ==

Nyt:
- Ctrl/Cmd+K åbner en søgbar kommandopalette uden for aktive tekstfelter
- dynamiske Gå til element-kommandoer bygges fra sidens aktuelle sektioner, overskrifter og elementnøgler
- tilføj alle centrale elementtyper direkte fra paletten
- skift Desktop/Tablet/Mobil og Normal/Hover fra tastaturet
- Fortryd/Gendan, Kopiér/Indsæt design og Gem som komponent er tilgængelige som kommandoer
- Gem-kommandoen navigerer kun til ændringsbeskrivelsen og udfører aldrig en rigtig Gem automatisk
- Alt+Pil op/ned skifter mellem sideelementer uden at overtage genveje inde i tekstfelter
- Escape lukker, piletaster vælger, Enter udfører og Tab holdes inde i dialogen
- page-editor schema forbliver 1.12; funktionen er editor-only og ændrer ikke frontend-data

== Version 0.5.13 – Lokal autosave og crash recovery ==

Nyt:
- lokal browser-autosave af sideeditorens aktuelle recovery-state
- kladden gemmes pr. side og indeholder sideopbygning, Card Grid, design og aktuelle feltværdier
- Gendan kladde / Kassér kladde vises kun, når der faktisk findes en relevant recovery-state
- ældre kladder markeres tydeligt, hvis WordPress-siden er ændret siden kladden blev oprettet
- ingen kladde gendannes automatisk; restore kræver altid et aktivt klik
- autosave flusher ved skjult fane/pagehide og før browserens ugemte-ændringer-advarsel
- permanent Gem, WhatIf, WordPress-revisioner og JSON-backups er uændrede
- page-editor schema forbliver 1.12; ingen datamigrering er nødvendig

== Version 0.5.12 – Undo / Redo og sikker redigeringshistorik ==

Nyt:
- lokal Undo/Redo-historik med op til 50 trin
- Fortryd/Gendan-knapper og Ctrl/Cmd+Z samt Ctrl/Cmd+Shift+Z uden at overtage normal tekst-undo i inputfelter
- historikken dækker live canvas, sektioner, Card Grid og rækkefølge
- status for ugemte ændringer og browseradvarsel ved navigation
- hurtige ændringer flusher før Undo/Redo, og Card Grid i Inspector indgår i historikken
- page-editor schema forbliver 1.12; permanente revisioner og backups er uændrede


== Version 0.5.11 – Elementstørrelse og design-clipboard ==

Nyt:
- elementbredde kan styres separat for desktop, tablet og mobil
- tablet/mobil kan arve desktopbredde med -1
- max-bredde og minimumshøjde kan styres pr. element
- bredde og minimumshøjde kan justeres direkte fra live canvas
- image/text_image får separat billedbredde på desktop/tablet og mobil samt max-bredde
- valgt billedformat kan låses eller frigives; låst format styrer højden når formatet ikke er Auto
- Inspector får Kopiér design / Indsæt design uden at kopiere tekst, links, billeder eller elementnøgle
- design-clipboard gemmes lokalt i browseren og kan bruges mellem elementer/sider i editoren
- page-editor schema 1.12 med bagudkompatible standarder

== Version 0.5.10 – Billeder og box-model i live canvas ==

Nyt:
- klik på image/text_image direkte i canvas for billedkontroller; dobbeltklik åbner WordPress Media Library
- focal point kan trækkes direkte på billedet og gemmes som X/Y-procenter
- billedformat: Auto, 1:1, 4:3, 3:2 og 16:9
- object-fit kan vælges som Fyld/beskær eller Vis hele billedet
- separat billedhøjde for desktop/tablet og mobil; 0 bevarer automatisk højde
- margin top/bund får egne drag-handles, mens eksisterende padding-handles bevares
- valgt element viser en kompakt box-model overlay med margin- og padding-værdier
- page-editor schema 1.11 med bagudkompatible standarder: Auto, Cover, fokus 50/50 og 0 px højde

== Version 0.5.9 – Direkte Card Grid-redigering ==

Nyt:
- hvert kort i Card Grid kan vælges direkte i canvas
- kort kan omarrangeres direkte i canvas med drag-and-drop
- kortets overskrift og rich-text indhold kan redigeres med dobbeltklik
- valgt kort får egne hurtigkontroller for baggrund, teksttone, placering, padding, radius, kant og aktiv-status
- kortdesign følger desktop/mobil-felterne, som allerede fandtes i editorens datamodel
- Card Grid får direkte kontrol over antal kolonner og mellemrum, så kortbredden kan justeres visuelt
- valgt kort fremhæves samtidig i Inspector
- page-editor schema forbliver 1.10; ingen datamigrering er nødvendig


== Version 0.5.8 – Direkte canvas-kontroller ==

Nyt:
- brødtekst kan redigeres direkte som rich text i canvas med dobbeltklik
- Escape annullerer inline-redigering af overskrift/knaptekst
- valgt element får hurtigkontroller for padding, vandret padding, top/bundafstand, radius og opacity
- baggrund, tekst og overskriftsfarve kan vælges direkte fra canvas
- fire drag-handles ændrer indvendig lodret/vandret luft direkte på elementet
- kontrollerne følger Desktop/Tablet/Mobil og Normal/Hover
- page-editor schema forbliver 1.10; ingen eksisterende sidedata migreres


== Version 0.5.7 – Live visuel canvas ==

Nyt:
- midterfeltet i sideeditoren viser nu en live visuel gengivelse af sektionerne
- klik direkte på et element i canvas for at vælge det i Inspector
- Desktop, Tablet og Mobil bruger de faktiske responsive værdier i live preview
- Normal/Hover kan simuleres direkte i editorens toolbar
- designændringer i Inspector opdaterer canvas uden at siden først skal gemmes
- overskrifter og knaptekster kan redigeres direkte med dobbeltklik i canvas
- skjulte elementer forbliver synlige som redigerbare, nedtonede placeholders på det valgte device
- hero, tekst/billede, kort, formularer, afstemninger, spacer, HTML og øvrige sektionstyper har egne visuelle previews
- page-editor schema forbliver 1.10; v0.5.7 ændrer kun editorens visuelle arbejdslag og er derfor bagudkompatibel


== Version 0.5.6 – Normal/Hover states ==

Nyt:
- hover-state kan arve Normal eller have egne farver
- egen hover-baggrund, tekst, overskrift, kant og opacity
- tilpasset hover-baggrund er en solid state og erstatter gradient/billede under hover
- hover state kombineres med v0.5.4-bevægelse/skygge og v0.5.5-device transforms
- page-editor schema 1.10; standarden Arv Normal bevarer eksisterende design


== Version 0.5.5 – Responsiv elementstyring ==

Nyt:
- vis/skjul hvert element separat på desktop, tablet og mobil
- særskilt tablet-placering, luft og indvendig luft
- tablet kan arve desktop med Inherit/-1
- translate X/Y, scale og rotate separat for desktop, tablet og mobil
- eksisterende hover-effekter komponeres med de responsive transforms
- reduced-motion fjerner kun hover-bevægelsen og bevarer statiske transforms
- page-editor schema 1.9 med neutrale bagudkompatible standarder


== Version 0.5.4 – Avanceret visuelt elementdesign ==

Nyt i sideeditoren:
- opacity pr. sektion
- gradientbaggrund med start/slutfarve og vinkel
- baggrundsbillede fra WordPress Media Library eller URL
- baggrundsbilledets placering og skalering
- individuel radius for alle fire hjørner
- hover-effekter: løft, let zoom eller ekstra skygge
- justerbar hover-transition
- schema 1.8 med bagudkompatible standardværdier

Eksisterende sektioner beholder 100% opacity, ingen ekstra baggrundseffekt, deres eksisterende radius og ingen hover-effekt.

== Installation / opdatering ==

1. Tag gerne en WordPress-backup.
2. WordPress -> Plugins -> Tilføj plugin -> Upload plugin.
3. Upload den nyeste hangar18-manager.zip.
4. Hvis v0.1.0 allerede er installeret, vælg at erstatte den eksisterende version.
5. Aktivér Hangar18 Manager.
6. Åbn Hangar18 Manager i venstre wp-admin-menu.

== Sikkerhedsmodel ==

WhatIf / Sikker tilstand er FRA som standard i v0.3.2. Brugeren kan markere WhatIf manuelt for at simulere en write-operation.
Når WhatIf er markeret:
- ingen side oprettes
- ingen side opdateres
- ingen registerside genbygges

Ved rigtig skrivning oprettes automatiske JSON-backups og WordPress-revisioner, hvor det er muligt.

== Køretøjer ==

Hangar18 Manager -> Køretøjer

Funktioner:
- Nyt / eksisterende køretøj
- HANGAR18-VEHICLE-DATA
- hovedbillede
- tekniske data
- historik
- tjeneste ved Aalborg
- restaureringsstatus
- draft / publiceret
- Placering i køretøjsregister: Venstre / Midt, separat på desktop og mobil
- Indholdsjustering på køretøjssiden: Venstre / Midt, separat på desktop og mobil
- automatisk genbygning af Køretøjer og materiel

== Events ==

Hangar18 Manager -> Events

Funktioner:
- HANGAR18-EVENT-DATA
- dato, tid, sted, adresse, kontakt
- hovedbillede
- om arrangementet
- program
- praktiske oplysninger
- draft / publiceret
- Billedalbum-dropdown med publicerede gallerialbums
- eventet linker til albummet i stedet for at have eget galleri
- automatisk genbygning af Events-siden

== Billedgalleri ==

Hangar18 Manager -> Billedgalleri

Struktur:
Billedgalleri -> album -> billeder

Albumtyper:
- Køretøj
- Event
- Restaurering
- Foreningen
- Andet

Funktioner:
- HANGAR18-GALLERY-ALBUM-DATA
- vælg flere billeder fra Media Library
- drag-and-drop rækkefølge
- første billede bliver featured image / album-cover
- automatisk genbygning af Billedgalleri-indekset

== Sider ==

Hangar18 Manager -> Sider

Egen sektionseditor til Hjem, Om foreningen, Bliv medlem og Kontakt:
- nuværende Gutenberg- og HTML-indhold opdeles automatisk i redigerbare sektionskladder
- den offentlige side ændres først, når redaktøren vælger Gem siden
- vis, skjul, duplikér, fjern og drag-and-drop-sortér sektioner
- visuel sidebygger med elementpalette, sideopbygning og særskilt indstillingspanel
- topbanner/hero, tekst, tekst og billede, stort billede, handlingsknapper, indholdskort, kort-rækker, fremhævet tekst, afstand og importeret HTML
- kort-rækker med 1-4 desktopkolonner, 1-2 mobilkolonner og drag-and-drop-sortering af kasser
- individuel baggrund, automatisk tekstkontrast, kant, luft, afrunding og placering for hver kasse
- sikker opdeling af importerede WordPress-kolonner til redigerbare kasser
- separat placering, luft og indvendig luft på desktop og mobil
- editorvisning i desktop-, tablet- og mobilbredde
- billeder vælges fra WordPress Media Library
- header og footer ligger uden for editoren og kan ikke slettes her

Funktionsmoduler:
- Mailformular med modtager, bekræftelse, valgfri samtykketekst, spambegrænsning og testmail
- valgfri lagring af de seneste 200 henvendelser og CSV-eksport
- Afstemning med 2-20 svarmuligheder, enkelt/flere svar, start/slut, resultatvisning, nulstilling og CSV-eksport
- dobbeltstemmer begrænses uden lagring af rå IP-adresser
- dynamisk frontend-rendering, så modulrettelser gælder alle forekomster
- WhatIf-simulering, automatisk backup og WordPress-revision


== Menu ==

Hangar18 Manager -> Menu

Menu-manageren arbejder med WordPress' rigtige nav-menu-system og opdaterer
samtidig den statiske menu-HTML i Hangar18-headeren.

Funktioner:
- vælg eksisterende WordPress-menu
- opret "Hangar18 Hovedmenu", hvis ingen menu findes
- drag-and-drop rækkefølge
- redigér vist menunavn uden at ændre sidetitlen
- vælg "Undermenu under"
- fjern menupunkt
- tilføj publiceret WordPress-side
- dubletbeskyttelse ved tilføjelse
- status for Hjem og dubletter
- "Sikr standardmenu":
  Hjem
  Om foreningen
  Køretøjer og materiel
  Events
  Billedgalleri
  Bliv medlem
  Kontakt
- standardmenu-reparation tilføjer manglende standardsider
- dubletter af samme WordPress-side fjernes
- ukendte/manuelle menupunkter bevares
- valg af temaets menu-location
- aktiv Hangar18-menu gemmes centralt
- menuen anvendes automatisk på alle styrede Hangar18-sider
- desktop-undermenuer vises som dropdown
- mobil-undermenuer vises indrykket

Sikkerhed:
- WhatIf er markeret som standard
- menu-backup før ændringer
- samlet sidebackup før headeren opdateres
- checkpoints i web-loggen

== Header / Footer ==

Hangar18 Manager -> Header / Footer

Designstyring:
- Sticky header
- maksimal hjemmesidebredde
- header top/bund luft
- logo størrelse
- foreningsnavn størrelse
- menutekst størrelse
- placering af logo/navn: venstre/midt/højre
- placering af menu: venstre/midt/højre

"Gem og anvend design":
- gemmer centrale webmanager-indstillinger
- lægger et separat HANGAR18-WEB-OVERRIDE på alle styrede sider
- ændrer ikke den eksisterende Additional CSS

"Synkroniser header/footer":
- bruger Hjem som primær shell-kilde
- kopierer HANGAR18-HEADER, HANGAR18-SHELL-CSS og HANGAR18-FOOTER
- anvender dem på alle styrede hoved- og undersider
- laver samlet backup først

== Backup ==

Hangar18 Manager -> Backup

- automatisk backup før writes
- manuel samlet backup
- backupfiler:
  wp-content/uploads/hangar18-manager-backups/

== Log ==

Hangar18 Manager -> Log

Checkpoints for WhatIf, saves, registeropdateringer, shell/design og fejl.

== Intern lagring og kompatibilitet ==

v0.2.0 bruger fortsat:
HANGAR18-VEHICLE-DATA
HANGAR18-EVENT-DATA
HANGAR18-GALLERY-ALBUM-DATA

Web-manageren bruger fortsat de samme datamarkører på eksisterende sider.
Indstillinger gemmes centralt i WordPress, og JSON anvendes kun internt til konfiguration og backup.
Den tidligere automatiske PowerShell-import og baseline-genindlæsning er fjernet fra den aktive arbejdsgang i v0.4.15.

Bemærk: Versionsafsnittene nedenfor beskriver også historisk funktionalitet i ældre udgaver.


== Version 0.3.0 ==

Nyt:
- fuldt Menu-modul
- aktiv WordPress nav-menu
- drag-and-drop
- ændring af vist navn
- undermenu-parent
- fjern menupunkt
- tilføj side
- Hjem-kontrol
- dubletkontrol og reparation
- standardmenu-reparation
- theme location
- menu-backup
- automatisk Hangar18-header-synkronisering
- desktop/mobile submenu CSS

Alle funktioner fra v0.2.0 er bevaret.


== Version 0.3.1 – 1:1 Configuration Sync ==

Denne version fjerner de selvstændige web-defaults som autoritativ
designkilde.

Ved første wp-admin-load efter opgraderingen forsøger pluginet automatisk
at læse den private WordPress-side:

hangar18-configuration-store

Den er den samme centrale store som PowerShell Manager v2.0.39 bruger.

Følgende filer importeres og SHA-256-valideres:
- Hangar18-HeaderDesign.json
- Hangar18-MenuOrder.json
- Hangar18-VehicleRegister.json

HeaderDesign:
- fuld schema 2.5
- alle felter er med i web-GUI
- samme valideringsgrænser og effektive normaliseringsregler som
  PowerShell v2.0.39
- Identity 100% bruger samme 0.70 identity-base
- VisualBaseScalePercent er med
- responsive fluid font/logo/menu sizing er porteret
- StickyOnScroll er separat fra PositionMode
- den aktuelle v2.0.39 site-width-runtime bevares præcist:
  min(100vw,calc(50vw + 700px))

VehicleRegister:
- schema 1.2
- CardAlignment er global Left/Center
- DetailAlignment er global Left/Center/Auto
- dette erstatter v0.3.0's fejlagtige per-køretøj-layoutmodel

MenuOrder:
- schema 2.0
- Menu-reparation bruger den importerede centrale rækkefølge og Included
- ændringer i WordPress-menuen publiceres tilbage som Hangar18-MenuOrder.json

To-vejs config sync:
Når web-manageren laver en RIGTIG ændring i HeaderDesign,
VehicleRegister eller MenuOrder:
1. lokal WordPress web-option opdateres
2. central hangar18-configuration-store opdateres
3. Base64 manifest schema 1.0 bevares
4. ContentBase64, SHA-256 og Length genereres
5. konfigurationsfilbytes gemmes med UTF-8 BOM for kompatibilitet med
   Windows PowerShell 5.1
6. PowerShell Manager kan hente ændringen igen via sin eksisterende
   CONFIG_SYNC-funktion

Manuel knap:
Header / Footer -> Genindlæs alle settings 1:1 fra central
PowerShell-konfiguration.

Installation af v0.3.1 ændrer ikke frontend automatisk.
Importen ændrer kun web-managerens indlæste settings.
Frontend ændres først, når en write-funktion køres med WhatIf slået FRA.


== Version 0.3.2 ==

Rettet efter test af v0.3.1:

1. Manglende hangar18-configuration-store er ikke længere en fejl.
   Hvis den private Configuration Store ikke findes:
   - web-manageren læser den eksisterende Hangar18 live-header/shell
   - udleder de settings der kan læses direkte fra headerens classes/style/runtime
   - bruger projektets kendte v2.0.39 baseline for de settings der ikke kan
     reverseres entydigt fra genereret CSS
   - læser eksisterende WordPress-menu til Hangar18-MenuOrder.json
   - bruger det globale PowerShell VehicleRegister schema 1.2
   - opretter automatisk den private WordPress-side:
     hangar18-configuration-store
   - skriver alle tre configfiler i manifest schema 1.0 med Base64, SHA-256,
     længde og UTF-8 BOM
   - fremtidig web/PowerShell config sync kan derefter bruge samme store

2. WhatIf er FRA som standard.
   Alle WhatIf-checkboxes er umarkerede ved åbning.
   WhatIf-funktionen er stadig fuldt bevaret og kan slås til manuelt.

3. Frontend ændres IKKE alene fordi Configuration Store bootstrapper.
   Bootstrap opretter/synkroniserer kun central konfiguration.
   Frontend ændres fortsat kun ved de konkrete save/apply-handlinger.

Ny log:
CONFIG_STORE_BOOTSTRAP_SUCCESS


== Version 0.4.0 – GitHub Updater ==

Nyt modul:
Hangar18 Manager -> Opdateringer

Standard repository:
phenixdk2020/hangar18-manager

Standard branch:
main

Standard manifest:
update.json

Standard package:
dist/hangar18-manager.zip

Updater flow:
1. hent update.json fra GitHub Contents API
2. valider schema/version/plugin-id
3. sammenlign version med installeret version
4. kontroller minimum WordPress/PHP
5. ved manuel update:
   - samlet Hangar18 data-backup
   - ZIP-backup af den installerede plugin-kode
   - download update-ZIP fra GitHub Contents API
   - SHA-256 kontrol
   - WordPress Plugin_Upgrader overwrite
   - genaktivering
   - verifikation af versionsnummer i installeret hovedfil
6. ved fejl:
   - log UPDATE_FAILED
   - automatisk rollback fra plugin-kodebackup
   - log rollback-resultat

Privat GitHub repository:
Token gemmes IKKE i WordPress-databasen.
Sæt i wp-config.php:

define('HANGAR18_GITHUB_TOKEN', 'github_pat_...');

Token behøver Contents: Read til repository.

Automatisk versionscheck:
- standard hver 6. time
- kan slås fra
- installation er fortsat manuel i v0.4.0

Update manifest eksempel:

{
  "schema_version": "1.0",
  "plugin": "hangar18-manager",
  "version": "0.4.1",
  "min_wp": "6.4",
  "min_php": "8.0",
  "published_utc": "2026-08-13T20:00:00Z",
  "package_path": "dist/hangar18-manager.zip",
  "package_sha256": "<64 hex characters>",
  "changelog": [
    "Rettelse 1",
    "Ny funktion 2"
  ]
}

Checkpoints:
UPDATE_CHECK_SUCCESS
UPDATE_CHECK_FAILED
UPDATE_SETTINGS_SAVED
UPDATE_START
UPDATE_CODE_BACKUP_SUCCESS
UPDATE_PACKAGE_VERIFIED
UPDATE_SUCCESS
UPDATE_FAILED
UPDATE_ROLLBACK_START
UPDATE_ROLLBACK_SUCCESS
UPDATE_ROLLBACK_FAILED

GitHub repository skal indeholde:
hangar18-manager.php
assets/admin.js
assets/admin.css
readme.txt
update.json
dist/hangar18-manager.zip


== Version 0.4.1 – Authoritative uploaded configuration baseline ==

Denne version korrigerer tidligere antagelser om konfigurationsschemaerne.

Autoritative filer er de tre JSON-filer leveret 2026-08-13:

Hangar18-HeaderDesign.json
- Version 2.3
- VisualBaseScalePercent 90
- MenuAlignment Right
- PositionMode Normal
- StickyOnScroll false
- BackgroundMode None
- WidthMode Contained
- ShowBrand true
- IdentityAlignment Center
- BrandFontSize 22
- BrandSizePercent 100
- ShowLogo false
- LogoWidthPx 52
- LogoSizePercent 100
- MobileStyle Dark
- MenuFontSize 15
- MenuSizePercent 100
- MenuFontFamily Segoe UI
- MenuFontWeight Semibold
- ResponsiveLargeWidthPx 2560
- ResponsiveLaptopWidthPx 1920
- ResponsiveLaptopScalePercent 90
- ResponsiveMinimumScalePercent 90
- DesktopContentWidthPercent 80
- LaptopContentWidthPercent 90
- MaximumDesktopContentWidthPercent 90
- ContentMaxWidth None
- FooterWidthPercent 100

Hangar18-MenuOrder.json
- Version 1.0
- Order:
  1. hjem
  2. koeretoejer-og-materiel
  3. events
  4. billedgalleri
  5. bliv-medlem
  6. kontakt
  7. om-foreningen

Hangar18-VehicleRegister.json
- Version 1.2
- CardAlignment Center
- DetailAlignment Auto

Migration:
På første wp-admin-load efter opgradering til 0.4.1 anvendes denne
autoritative baseline én gang på plugin-options og den centrale
Configuration Store.

Migrationen ændrer IKKE frontend automatisk.
Frontend ændres først ved en konkret Save/Apply/Sync-handling.

Tidligere web-schema MenuOrder 2.0/Items understøttes som input og
konverteres tilbage til det autoritative schema 1.0/Order.

Tidligere HeaderDesign-opgraderinger til schema 2.5 udføres ikke længere.
Web-manageren bevarer schema 2.3 som autoritativt schema.

Checkpoint:
AUTHORITATIVE_BASELINE_APPLIED
AUTHORITATIVE_BASELINE_FAILED


== Version 0.4.2 – GitHub updater diagnostics ==

- Forbedret 404-diagnostik.
- Public repository fungerer uden GitHub-token.
- Privat repository kan fortsat bruge HANGAR18_GITHUB_TOKEN i wp-config.php.
- Opdateringssiden viser adgangstilstand: PUBLIC eller TOKEN.
- Den autoritative PowerShell-konfigurationsbaseline fra v0.4.1 er uændret.
- WhatIf er fortsat FRA som standard.


== Version 0.4.3 – Event/galleri-placering og menu-pinning ==

- Events har nu global placering: Venstre eller Midtstillet.
- Eventplaceringen anvendes på både eventoversigt og eventdetaljer.
- Billedgalleri har nu global placering: Venstre eller Midtstillet.
- Galleriplaceringen anvendes på både albumoversigt og albumsider.
- Ny central Hangar18-ContentLayout.json schema 1.0.
- Menu-siden har nu en tydelig "Pin menu/header ved scroll"-funktion.
- Pinning synkroniserer StickyOnScroll i Hangar18-HeaderDesign.json.
- Web-override indeholder sticky CSS-fallback med korrekt WordPress admin-bar offset.
- Layoutændringer tager fuld backup før eksisterende sider genbygges.
- WhatIf er fortsat FRA som standard.


== Version 0.4.4 – Separate oversigts- og detaljeplaceringer ==

- Køretøjer har nu to uafhængige valg: Køretøjer og materiel-oversigten samt de enkelte køretøjssider.
- Events har nu to uafhængige valg: eventoversigten samt de enkelte eventsider.
- Billedgalleri har nu to uafhængige valg: gallerioversigten samt de enkelte albumsider.
- Alle seks valg er Venstre eller Midtstillet.
- Hangar18-VehicleRegister.json er opgraderet til schema 1.3 og bevarer CardAlignment som legacy-alias.
- Hangar18-ContentLayout.json er opgraderet til schema 1.1.
- Eksisterende v0.4.3 EventAlignment/GalleryAlignment migreres automatisk til begge nye valg.
- Eksisterende Vehicle DetailAlignment=Auto migreres til Center for at bevare desktop-udseendet.
- WhatIf er fortsat FRA som standard.


== Version 0.4.5 – Frontend layoutfix ==

- Fjerner Astra/WordPress' native sidetitel og reserverede topafstand på Hangar18-styrede sider.
- Retter det blå/lilla titel-felt over Hangar18-headeren på Køretøjer, Events og Billedgalleri.
- Events detaljesider respekterer nu reelt Venstre/Midtstillet for hele indholdscontaineren.
- Billedgalleri-albums respekterer nu reelt Venstre/Midtstillet for selve billedgrid'et.
- Køretøjsdetaljer respekterer nu reelt Venstre/Midtstillet for hele detaljeindholdet.
- Eventbilleder er gendannet på Events-oversigten.
- Eventdetaljer bruger featured image som fallback, hvis ældre marker-data mangler MainMediaId.
- Header-knapper omdøbt til tydeligere funktioner.


== Version 0.4.6 – køretøj/galleri frontend-fix ==

- Events er bevidst ikke ændret i denne version.
- Astra/WordPress' native blå/lilla sidetitelbjælke fjernes via wp_head på Hangar18-styrede sider.
- Native entry-title/page-header/advanced-header wrappers får nul højde og ingen margin/padding.
- Køretøjsdetaljer bruger eksplicit h18-align-left/h18-align-center og fuld genbygning ved layoutændring.
- Gutenberg-klassen has-text-align-center fjernes fra køretøjernes leadtekst.
- Gallerialbums bruger eksplicit h18-align-left/h18-align-center på selve billedgrid'et.
- Første wp-admin-side efter opdatering genbygger automatisk køretøjer, køretøjsoversigt, gallerialbums og gallerioversigt.


== Version 0.4.7 – Astra Banner Area ==

- Den resterende lilla/blå bjælke er identificeret som Astra 4.x Banner Area.
- Hangar18 bruger nu Astra's egne frontend-filtre til at deaktivere banner/title-området.
- astra_apply_hero_header_banner sættes false på Hangar18-styrede sider.
- astra_remove_entry_header_content sættes true.
- astra_single_layout_one_banner_visibility sættes false.
- astra_the_title_enabled og astra_advanced_header_title deaktiveres.
- Astra-meta site-post-title, ast-title-bar-display og ast-banner-title-visibility sættes til disabled på styrede sider én gang efter opdatering.
- Ekstra CSS fallback dækker .ast-single-entry-banner og relaterede Astra 4 selectors.
- Events, køretøjer, billedgalleri og deres layoutdata ændres ikke.
- Oversigtssiderne får egne Hangar18-overskrifter: Køretøjer og materiel, Events og Billedgalleri.
- Overskrifterne følger oversigtssidens Venstre/Midtstillet-indstilling.


== Version 0.4.8 – Dynamiske køretøjsfelter ==

- Ny undermenu: Hangar18 Manager -> Køretøjsfelter.
- Tekniske køretøjsfelter kan aktiveres/deaktiveres, omdøbes, flyttes og fjernes fra opsætningen.
- Hvert felt har separat valg for visning på køretøjsoversigten og på den enkelte køretøjsside.
- Nye felter kan tilføjes uden kodeændring.
- Felttyper: kort tekst, lang tekst, tal, ja/nej, dropdown, dato, URL og farvevælger.
- Standardfeltet Farve er oprettet som inaktivt felt og kan aktiveres med ét klik.
- Eksisterende feltværdier slettes ikke, når et felt deaktiveres eller fjernes.
- Eksisterende legacy-felter migreres logisk til CustomFields og spejles fortsat til de gamle nøgler for bagudkompatibilitet.
- Ny central konfigurationsfil: Hangar18-VehicleFields.json schema 1.0.
- Gem af feltopsætning tager backup og genbygger alle køretøjssider samt køretøjsoversigten.


== Version 0.4.9 – Køretøjets billede og tekniske data ==

- Køretøjets detaljeside bruger nu sit eget eksplicitte layout og er ikke afhængig af Astra eller WordPress' blok-CSS.
- På computer står hovedbilledet fast i venstre kolonne og Tekniske data i højre kolonne.
- På mobil stables billedet øverst og Tekniske data nedenunder.
- Venstre/Midtstillet-indstillingen styrer fortsat placeringen af det samlede detaljeindhold.
- Alle eksisterende køretøjssider genbygges automatisk én gang efter opdateringen.


== Version 0.4.10 – Korrekt sidebredde og topplacering ==

- Header, sideindhold og footer bruger nu de gemte Desktop/Laptop-bredder i stedet for den gamle faste v2.0.39-formel.
- MaximumDesktopContentWidthPercent kan ikke længere gøre desktopbredden mindre end DesktopContentWidthPercent.
- Med DesktopContentWidthPercent 90 og MaximumDesktopContentWidthPercent 88 bliver den effektive maksimumsbredde derfor 90 procent.
- På mobil bruges fortsat 100 procent bredde.
- Headeren nulstilles målrettet til 0 topmargin og 0 toppadding på Hangar18 Base Theme og Astra.


== Version 0.4.11 – Sektionsafstand og galleri-skabelonfix ==

- Nye HeaderDesign-felter styrer afstanden mellem sidens hovedsektioner separat på desktop og mobil.
- Astra-lignende standardafstand er 32 px på desktop og 24 px på mobil.
- Første synlige sektion får ingen ekstra topafstand, så headerens placering helt oppe bevares.
- Gamle Astra-sideskabeloner fjernes automatisk fra alle Hangar18-styrede sider og den private Configuration Store én gang efter opdateringen.
- Gallerialbums og Billedgalleri-oversigten gemmes eksplicit med Hangar18 Base Themes standardskabelon.
- Fejlen "Ugyldig sideskabelon" ved gemning af billedgalleri er dermed rettet.
- HeaderDesign kan igen publiceres til Configuration Store uden fejlen "Ugyldig sideskabelon".


== Version 0.4.12 – Header starter ved 0 px for indloggede brugere ==

- Fjerner WordPress' resterende 32 px desktopafstand og 46 px mobilafstand, når admin-baren er skjult.
- En afsluttende CSS-regel i footeren sikrer, at senere WordPress- eller blok-CSS ikke kan flytte headeren ned.
- Headerens top, margin-top og sticky-position fastholdes på 0 px.
- Indstillingen for sektionsafstand påvirker fortsat kun sektionerne inde i indholdsrammen.


== Version 0.4.13 – Styrbar luft omkring sideindholdet ==

- Fire nye HeaderDesign-felter styrer luften fra header til indhold og fra indhold til footer separat på desktop og mobil.
- Standardafstanden er 32 px på desktop og 24 px på mobil.
- Afstanden oprettes som indvendig luft i indholdsrammen, så headeren fortsat starter ved 0 px.
- Den eksisterende sektionsafstand styrer fortsat afstanden mellem indholdets hovedsektioner.


== Version 0.4.14 – Mobilplacering for Events og Billedgalleri ==

- Events har nu separate indstillinger for placering af oversigt og detaljesider på desktop og mobil.
- Billedgalleri har nu separate indstillinger for placering af albumoversigt og billeder i albums på desktop og mobil.
- Mobilstandard er Midtstillet for alle fire visninger; desktopindstillingerne bevares uændret.
- Eksisterende events, albumsider og oversigter genbygges automatisk én gang efter opdateringen.
- Hangar18-ContentLayout.json er opgraderet fra schema 1.1 til 1.2.


== Version 0.4.15 – Oprydning og mobilplacering for køretøjer ==

- Fjerner den gamle PowerShell-import, baseline-genindlæsning, importstatus og importknap fra den aktive web-manager.
- Bevarer den private centrale WordPress-konfiguration og JSON-backups, fordi de bruges til sikker lagring og gendannelse.
- Forenkler administrationssiderne, så tekniske JSON-filnavne og schemanumre ikke vises i den normale arbejdsgang.
- Køretøjsoversigten og de enkelte køretøjssider får separate placeringer på desktop og mobil.
- Mobilstandard er Midtstillet, og eksisterende køretøjssider genbygges automatisk én gang efter opdateringen.
- Den interne køretøjslayout-konfiguration er opgraderet fra schema 1.3 til 1.4.


== Version 0.4.16 – Ensartede layouts og knapforklaringer ==

- Samler layoutindstillinger for Køretøjer, Events og Billedgalleri i ens kort med tydelige Desktop- og Mobil-sektioner.
- Holder relaterede felter i faste kolonner og tilpasser dem automatisk til tablet og mobil.
- Giver layout-, gemme- og reparationsknapper synlige forklaringer om hvad de gør, og hvornår de skal bruges.
- Forklarer WhatIf som en frivillig simulering, der ikke gemmer eller ændrer sider.
- Gør handlingslinjerne ens på Køretøjer, Køretøjsfelter, Events, Billedgalleri, Menu, Header/Footer, Opdateringer og Backup.


== Version 0.4.17 – Sideindhold og designmanual ==

- Tilføjer modulet Sideindhold til styring af indholdssektioner på Om foreningen.
- Sektioner kan vises, skjules, tilføjes, sorteres med musen eller fjernes permanent.
- Luft før første indholdskasse, mellem kasser og inde i kasser kan styres separat på desktop og mobil.
- Hjørneafrunding kan indstilles, og det godkendte kortdesign bruges som standard.
- WhatIf simulerer ændringen uden skrivning, og en rigtig gemning tager automatisk backup først.
- Tilføjer DESIGN-MANUAL.md med de godkendte valg for farver, bredde, typografi, afstande, kort og mobilvisning.


== Version 0.4.18 – Egen sideeditor og funktionsmoduler ==

- Udvider Sideindhold til Sider med en samlet editor til Hjem, Om foreningen, Bliv medlem og Kontakt.
- Bevarer eksisterende ukendt sideindhold som en sikker legacy-sektion, indtil redaktøren selv vælger at fjerne det.
- Tilføjer genbrugelige sektionstyper til tekst, billeder, knapper, kort, fremhævelser og afstand.
- Tilføjer mailformular med servervalidering, nonce, spambegrænsning, testmail, valgfri lagring og CSV-eksport.
- Tilføjer afstemning med svarmuligheder, enkelt/flere svar, tidsrum, resultater, nulstilling og CSV-eksport.
- Begrænser dobbeltstemmer med cookie og saltet hash uden at gemme rå IP-adresser.
- Tilføjer responsive desktop-, tablet- og mobilvisninger samt separat luft og placering.
- Gemmer sider som dynamiske Hangar18-moduler, så en kodeopdatering gælder alle forekomster.
- Opdaterer designmanualen med regler for sideeditor, mailformularer og afstemninger.


== Version 0.4.19 – Redigering af nuværende sider ==

- Retter 0.4.18-fejlen, hvor eksisterende sideindhold kun blev vist som én låst legacy-sektion.
- Indlæser nuværende Gutenberg- og HTML-indhold som en ikke-gemt, redigerbar sektionskladde.
- Genkender overskrifter, tekst, billeder, knapper, afstande, to-kolonneindhold og topbanner/hero.
- Tilføjer en redigerbar Importeret blok / HTML-type til ukendte blokke, så intet indhold kasseres.
- Bevarer den offentlige side uændret, indtil redaktøren aktivt vælger Gem siden.
- Opretter fortsat fuld backup og WordPress-revision før den første konverterede gemning.


== Version 0.4.20 – Bevaring af eksisterende layout ==

- Retter fejlen, hvor importeret side-CSS blev vist som almindelig tekst øverst på siden.
- Genkender og renderer eksisterende side-CSS som CSS i stedet for indhold.
- Bevarer designgrupper med egne Gutenberg-klasser som samlede redigerbare HTML-sektioner ved nye importer.
- Gendanner kolonnelayout for eksisterende kort, Events og Billedgalleri på desktop og stabler dem på mobil.
- Samler tekst og tilhørende handlingsknap i samme luftsektion på allerede konverterede sider.
- Gendanner topbilledets efterfølgende tagline og de oprindelige responsive afstandsregler.
- Reparerer den allerede gemte 0.4.19-forside ved visning uden at kræve en ny konvertering eller automatisk dataskrivning.


== Version 0.4.21 – Ét korrekt hero-billede ==

- Fjerner det gamle Gutenberg Cover-billede fra heroens indhold, når samme billede allerede bruges som hero-baggrund.
- Bevarer heroens godkendte højde, beskæring og responsive baggrundsvisning.
- Genkender også ældre CSS, der blev gemt som en tekstsektion, og renderer den som side-CSS i stedet for synlig tekst.
- Sikrer, at Venstre/Midtstillet for desktop og mobil styrer både overskrifter, tekst og handlingsknapper uden at blive tilsidesat af importerede Gutenberg-klasser.


== Version 0.4.22 – Sammenligningskladde fra backup ==

- Backupoversigten viser nu backupgrund og om filen indeholder den oprindelige Hjem-side eller en nyere sideeditor-version.
- En oprindelig Hjem-backup kan oprettes som en separat WordPress-kladde direkte fra backuplisten.
- Kladden bliver ikke aktiv forside, tilføjes ikke til menuen og kan ikke overskrive Hjem-side ID 9.
- En allerede oprettet sammenligningskladde genbruges, så samme backup ikke opretter dubletter.
- Sidespecifik CSS tilpasses kladdens nye side-ID, så den gamle side kan forhåndsvises retvisende.


== Version 0.4.23 – Gendannet Hjem-design i sideeditoren ==

- Gendanner Hjem-sidens oprindelige sektionsfarver: knækket hvid, hvid, olivengrøn og sandfarvet.
- Gendanner 32 px luft mellem hovedsektionerne på desktop og 24 px på mobil.
- Tilføjer særskilt styring af lodret og vandret indvendig luft på desktop og mobil.
- Gendanner 24 px vandret indvendig luft på desktop samt 18 px på mobil.
- Gendanner de oprindelige runde knapper og deres farver i importerede Hjem-sektioner.
- Sætter mobilbanneret til 180 px og sikrer fortsat, at bannerbilledet kun vises én gang.
- Bevarer venstrestilling på desktop og midterstilling på mobil efter de valgte indstillinger.
- Tager automatisk fuld backup før engangsreparationen af den aktive Hjem-side.


== Version 0.4.24 – Sikre konverteringstests af sider ==

- Tilføjer Opret konverteringstest på ukonverterede sider i Hangar18 sideeditor.
- Opretter Om foreningen, Kontakt eller Bliv medlem som en separat offentlig testkopi uden at ændre originalsiden.
- Genbruger og opdaterer samme testside, så der ikke oprettes dubletter ved gentagne tests.
- Lader testkopien læse sin egen indlejrede sektionskladde i stedet for originalsiden eller den centrale editoropsætning.
- Tilpasser sidespecifik CSS fra originalens side-ID til testkopiens side-ID.
- Føjer ikke testkopier til Hangar18-menuen og udelader dem fra menuens sidevælger.
- Markerer testkopier med noindex, nofollow og noarchive, så de ikke skal optages af søgemaskiner.


== Version 0.4.25 – Fortryd sidekonvertering ==

- Tilføjer Gendan siden fra før editoren på sider, der allerede er gemt i Hangar18 sideeditor.
- Finder først den nyeste WordPress-revision uden sideeditor-data og bruger JSON-backup som sikker reserve.
- Tager både fuld backup og sidebackup af den konverterede version, før gendannelsen udføres.
- Gendanner kun den valgte sides titel, indhold, uddrag og eventuelle fremhævede billede.
- Rydder den valgte side fra editorens centrale lager, så den ikke genindlæses som konverteret ved næste besøg.
- Ændrer ikke menu, header, footer, testkopier eller andre sider.


== Version 0.4.26 – Sideversionering og ændringsbeskrivelser ==

- Kræver en kort ændringsbeskrivelse ved hver rigtig gemning i Hangar18 sideeditor.
- Tildeler hver side sit eget fortløbende versionsnummer.
- Tager automatisk en fuld før-backup og en separat sidekopi af den nye gemte version.
- Gemmer tidspunkt, WordPress-bruger, ændringsbeskrivelse, antal aktive sektioner, backupfiler og indholdshash i versionshistorikken.
- Viser de seneste versioner nederst på den valgte sides editorside.
- WhatIf viser næste versionsnummer, men opretter ingen version, backup eller historikpost.
- Medtager versionshistorikken i fremtidige fulde Hangar18-backups.


== Version 0.4.27 – Visuel sidebygger og redigerbare kasser ==

- Ombygger sideeditoren til en visuel arbejdsflade med elementer til venstre, sideopbygning i midten og indstillinger til højre.
- Elementer og funktionsmoduler kan klikkes eller trækkes ind i sideopbygningen.
- Tilføjer Kort-række / kolonner med 1-4 kolonner på desktop og 1-2 kolonner på mobil.
- Gør hver kasse selvstændigt redigerbar og flytbar med farve, tekstkontrast, kant, luft, afrunding og placering.
- Tilføjer stålgrå til den godkendte farvepalette.
- Tilføjer Opdel importerede kasser, som udskiller WordPress-kolonner uden at ændre den resterende importerede sektion.
- Bevarer den offentlige side, indtil redaktøren gemmer som en ny version med ændringsbeskrivelse og automatisk backup.


== Version 0.5.0 – Designsystem og menueffekter ==

Version 0.5.0 bygger direkte videre på v0.4.27. Den eksisterende visuelle sidebygger, datamodeller, WhatIf, backup og versionshistorik er bevaret.

Nyt i første 0.5.0-fundament:
- Nyt Designer schema 1.0 med globale design tokens, indlejret bagudkompatibelt i HeaderDesign schema 2.3.
- Centrale farver: primær, sekundær, accent, lys flade, baggrund, tekst, lys tekst og action/link.
- Global brødtekst- og overskriftstypografi med H1/H2/H3-størrelser.
- Afstandstokens XS/S/M/L/XL og tre niveauer af hjørneafrunding.
- Sidebyggerens eksisterende farveklasser kobles til de globale farver.
- Menupræsentation: Klassisk, Flydende pill eller Indrammet.
- Hover-effekter: Ingen, animeret understregning, løft eller pill-baggrund.
- Aktiv side: Ingen, understregning, pill eller punkt.
- Undermenu-animation: Ingen, Fade, Fade + slide eller Scale.
- Animationshastighed kan styres centralt.

Kompatibilitet og sikkerhed:
- Standardfarverne er identiske med v0.4.27.
- Alle nye menueffekter er slået fra som standard.
- HeaderDesign forbliver schema 2.3, så den eksisterende centrale konfiguration og ældre PowerShell-klienter fortsat kan læse de kendte felter.
- Ingen sidekonvertering eller datamigration køres automatisk.


== Version 0.5.1 – Navigator, avanceret Inspector og genbrugelige komponenter ==

- Sidebuilderens venstre panel har faner til Elementer, Lag og Komponenter.
- Navigator/Lag viser alle aktive sektioner, synlighedsstatus og understøtter drag-and-drop rækkefølge.
- Inspector er opdelt i Indhold, Design og Avanceret.
- Avanceret Inspector viser elementtype og elementnøgle samt genveje til duplikering og komponentlagring.
- Fem indbyggede komponentpresets: Hero + handling, Tekst + billede, 3 informationskort, CTA-bånd og Kontaktblok.
- Enhver ikke-legacy sektion kan gemmes som egen genbrugelig komponent. Egne komponenter gemmes centralt i WordPress og kan indsættes på alle redigerbare sider.
- Egne komponenter kan slettes direkte fra komponentbiblioteket.
- Eksisterende v0.5.0 sider, HeaderDesign schema 2.3 og Designer schema 1.0 bevares uændret.


== Version 0.5.2 – Individuelt elementdesign ==

- Hver editorsektion kan følge Globalt design eller bruge Tilpasset farvetilstand.
- Tilpasset tilstand giver egne farver for baggrund, tekst og overskrifter.
- Hvert element kan få egen kantbredde, kantfarve og skygge.
- Globalt design er fortsat standard, så eksisterende sider beholder deres udseende efter opdatering.
- Page-editor dataformatet er kompatibelt løftet fra schema 1.5 til 1.6.


== Version 0.5.3 – Typografi pr. element ==

- Hver editorsektion kan vælge egen brødtekstfont og overskriftsfont eller arve de globale fonte.
- Brødtekst samt H1, H2 og H3 kan få egne størrelser pr. element.
- Værdien 0 betyder global størrelse og giver fuld bagudkompatibilitet.
- Typografifelterne gemmes også i genbrugelige komponenter fra v0.5.1.
- Page-editor dataformatet er kompatibelt løftet fra schema 1.6 til 1.7.


== 0.5.12 ==
* Lokal Undo/Redo-historik med op til 50 redigeringstrin i den visuelle editor.
* Fortryd/Gendan-knapper samt Ctrl/Cmd+Z og Ctrl/Cmd+Shift+Z uden at overtage tekstfelters native undo.
* Historikken dækker feltændringer, live-canvas, sektioner, kort og rækkefølge.
* Status viser ugemte ændringer, og browseren advarer ved navigation væk fra en ændret side.
* Ingen page-editor schemaændring; permanente WordPress-revisioner/backups er uændrede.


## v0.5.26 – E5 UD-057 Repeater / Query list
- Nyt `Repeater / Query list`-element i den visuelle sidebygger.
- Genbruger Query Builder v1 til datatype, filter, sortering og limit.
- En linked component fungerer som template og renderes én gang pr. query-resultat.
- Hvert resultat bliver current data context under render, så eksisterende dynamic bindings virker uden en særskilt template-motor.
- Understøtter component variant, desktop/mobil-kolonner, gap og tom-resultattekst.
- Query List-komponentreferencer indgår i Usage Inspector og blokerer sikker sletning af komponent/variant.
- Runtime beskytter mod rekursive Query List/component-loops og gendanner altid det tidligere data context.
- Page-editor schema: 1.20.


## v0.5.27 – E5 UD-058 Conditional Visibility
- Alle page-builder elementer får generiske Conditions med AND/OR mode.
- Data conditions: empty/not-empty/equality/comparison mod current data context.
- User conditions: logged in/out, rolle og capability.
- Date/time conditions: før, efter og mellem i WordPress-site timezone.
- Conditions evalueres server-side før dynamic binding og virker derfor også pr. resultat inde i Query Lists.
- Editor-preview evaluerer samme condition-model og markerer skjulte elementer uden at fjerne dem fra canvas.
- Conditions er præsentationslogik og er eksplicit ikke en authorization/security boundary.
- Maks. 8 conditions pr. element; ukendte typer/operatorer droppes under normalisering.
- Page-editor schema: 1.21.


## v0.5.28 – E5 UD-054 Relation / Group / Repeater fields
- Datatype schema builder understøtter nu Relation, Group og Repeater ud over de fem primitive felttyper.
- Relation kræver en eksisterende mål-datatype og gemmer et valideret entry-ID; mål-datatyper kan ikke slettes mens relationer peger på dem.
- Group og Repeater bruger op til 12 typed underfelter af text/number/bool/date/media.
- Repeater er bounded til 1–20 rækker pr. schemafelt og har add/remove UI i entry-editoren.
- Nested værdier bruger samme server-side sanitizer som primitive felter og Required-validering.
- Query Builder v1 skjuler/rejecter strukturerede felter; relation/advanced query udvides separat i UD-056.
- Data SchemaVersion løftes til 2; page-editor schema forbliver 1.21.


## v0.5.29 – E5 UD-056 Advanced Query
- Advanced Query understøtter op til 4 AND/OR-grupper med op til 6 filtre pr. gruppe.
- Filtre kan blande primitive datafelter, Relation-felter og Data Tags taxonomy.
- Data entries får en privat `h18_data_tag` taxonomy med kommasepareret tag-editor.
- Relation-filter valideres mod relation-feltets scalar target-ID; Group/Repeater kan ikke bruges som direkte query-filter.
- Advanced preview og frontend-shortcode bruger samme normalized evaluator uden rå SQL.
- Pagination: 1–50 resultater pr. side, stabil sortering og separate query-string page keys pr. query.
- Kandidatsættet er bounded til 2000 publicerede entries og markerer `Truncated`, hvis grænsen nås.
- Page-editor schema forbliver 1.21; Data SchemaVersion forbliver 2.


## v0.5.30 – E5 UD-059 Field formatters + fallback
- Dynamic bindings får et separat, bagudkompatibelt `BindingOptions`-lag; den eksisterende `Bindings[property]=field` model ændres ikke.
- Formatters: Auto/Text, upper/lower, tal med 0/1/2 decimaler, kort/ISO/lang dato samt Ja/Nej.
- Fallback modes: behold statisk elementværdi, custom fallback eller tom værdi.
- `FallbackWhenEmpty` er opt-in og default false, så eksisterende bindinger beholder tidligere empty-value adfærd.
- Prefix/suffix kan anvendes på tekstoutput; URL/media springer prefix/suffix over og saniteres fortsat typespecifikt.
- Runtime og canvas-preview anvender samme formatter/fallback-model.
- BindingOptions følger med i Patterns, linked component definitions og Page Templates.
- Page-editor schema løftes bagudkompatibelt til 1.22.


== Version 0.6.2 – Editorfix + Site Builder core ==

- Retter Fed/Kursiv-toggle i mini-editoren, så gentagne til/fra-skift ikke opbygger nestede tags.
- Tilføjer tydelig Typografi-fane i Inspector med font og brødtekst/H1/H2/H3-størrelser.
- Bevarer Inspector-overlap-hotfixet fra 0.6.1.
- E6 Site Builder core: Header/Footer templates, versioneret menu-tree, klassisk accessible menu-renderer, passive runtime assets og Site Builder presets.
- Single/archive/system template assignment kan resolveres efter context og priority.
- Eksisterende sider samt Vehicle/Event/Gallery og legacy header/footer/menu konverteres ikke i denne release.


== Version 0.6.3 – E7 Interaction core ==

- Generic accessible forms og server-side validation.
- Ordered submit action chains med logging og fejlpolitik.
- Mail/save/redirect actions samt signed HTTPS webhook med timeout/retry og wp_safe_remote_post.
- Modal/popup builder-core med shared Sections tree, ARIA, focus trap, ESC og scroll lock i passiv runtime.
- Click/time/scroll/context popup triggers og generiske navigate/scroll/open-modal/toggle actions.
- Eksisterende sider og Vehicle/Event/Gallery forbliver uændret.
