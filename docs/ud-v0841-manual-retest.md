# Ultimate Designer v0.8.41 — manuel retest på test2

**Status:** PENDING — dette dokument er en testprocedure, ikke PASS-evidence.  
**Kandidat:** Hangar18 Manager **v0.8.41**  
**Release commit:** `1ccfa6b51a4fb1e716e565ba96e2f9d8cf0746ff`  
**Package SHA-256:** `000f01eb9c8ca25881c7b969057175882d25ef1b2eff1fcdef3fed725acae433`  
**Target:** `https://test2.hangar18.dk`

## 1. Før testen

- Bekræft i WordPress, at **Hangar18 Manager 0.8.41** er installeret og aktiv.
- Bekræft at testen foregår på `test2`, ikke production.
- Tag eller identificér et rollback-point før første permanent gem/write-test.
- Notér browser, OS og de anvendte Desktop/Tablet/Mobil-viewports.
- Brug `docs/lego-v0841-manual-acceptance.json` som canonical acceptance-record.

## 2. Første test: reproduktionen fra v0.8.40

Denne test køres først, fordi den tidligere manuelle session fandt fejlen her.

1. Opret eller brug en almindelig testside.
2. Indsæt **Tekst og billede** på canvas.
3. Tag et nyt **Tekst**-element fra **Elementer/Funktioner** i venstre palette.
4. Træk det over målelementet og ind i den synlige **Venstre**-dropzone.
5. Slip elementet.

**PASS-forventning:**

- `Tekst` står til venstre for `Tekst og billede`;
- begge er direkte børn af samme Auto-kasser-layout;
- de må ikke ende som to lodrette siblings;
- ingen dublet opstår;
- ingen console/fatal error;
- Undo én gang gendanner hele drop-handlingen samlet.

Hvis dette fejler, stop A–L-sessionen og registrér FAIL/evidence på A/C/H efter relevans.

## 3. A — Elementbibliotek og drop

- Indsæt mindst Tekst, Billede og Kasse fra paletten.
- Prøv Over og Under.
- Prøv Venstre og Højre fra paletten.
- Bekræft at den visuelle dropzone svarer til den faktiske placering.
- Kontrollér at der ikke oprettes dubletter.

## 4. B — Kasse og nesting

- Træk et almindeligt element **Into** en Kasse.
- Tilføj et andet barn i samme Kasse.
- Flyt et barn ud igen.
- Bekræft parent/child-strukturen visuelt og efter save/reload.

## 5. C — Side-by-side / Auto-kasser

- Opret to almindelige elementer side-by-side med Venstre/Højre.
- Forvent startfordeling cirka 6/6.
- Tilføj eventuelt tredje element; forvent normaliseret række inden for 12 kolonner.
- Flyt et barn til modsatte side og kontrollér rækkefølgen.

## 6. D — Desktop resize

- Brug resize-håndtaget mellem to naboer.
- Ændr fx 6/6 til 8/4.
- Minimum span skal være 1.
- Begge naboer skal kompensere, så række-budgettet bevares.
- Ét drag fra pointerdown til pointerup skal være ét Undo-trin.

## 7. E — Tablet/Mobil + Arv Desktop

- Start med et kendt Desktop-layout.
- Skift til Tablet og lav en anden fordeling.
- Bekræft at Desktop er uændret.
- Aktivér `Arv Desktop`; Tablet skal vise Desktop-layoutet.
- Deaktivér `Arv Desktop`; den tidligere Tablet-override skal vende tilbage.
- Gentag tilsvarende sanity-check på Mobil.

## 8. F — Design og spacing

På et almindeligt element og en Kasse:

- ændr tekstfarve/baggrund;
- ændr border/radius;
- ændr X/Y spacing;
- kontrollér at Direkte Design og Inspector viser samme canonical state;
- kontrollér responsive override uden at Desktop ændres utilsigtet.

## 9. G — Foldbare paneler

- Fold **Direkte Design · LEGO** ind/ud.
- Fold **Billede** ind/ud, hvor relevant.
- Fold venstre/højre workspace rails.
- Foldestatus må ikke ændre page-data eller skabe Undo/Redo-checkpoints.

## 10. H — Undo/Redo

Test mindst:

- et side-drop;
- et resize;
- en design/spacing-ændring;
- en indholdsændring.

Hver logisk handling skal kunne Undo/Redo separat. Et side-drop må ikke kræve flere Undo-trin for wrapper + parent + order.

## 11. I — Save/reload persistence

- Lav en kendt kombination af nesting, side-by-side, spans og design.
- Gem som permanent version med ændringsnote.
- Reload editoren.
- Verificér at placering, parent, spans, responsive overrides og indhold er identiske.

## 12. J — Preview

- Kontrollér Desktop, Tablet og Mobil preview.
- Ingen horisontal overflow.
- Ingen editor-chrome i preview-klonen.
- Working/preview må ikke autorisere eller udføre public I10 cutover.

## 13. K — Backup/restore

- Tag/identificér en B1/B2 backup før en testændring.
- Lav og gem en tydelig, reversibel ændring.
- Gendan via det etablerede restore-flow.
- Verificér sideindhold og editor-state efter restore.

## 14. L — Vehicle/Event/Gallery

Read-only/regression:

- Køretøjer og materiel åbner og vises som før.
- Events åbner og vises som før.
- Billedgalleri åbner og vises som før.
- Ingen generel LEGO-konvertering eller public renderer må have overtaget disse domæner.

## 15. PAGE-DELETE-001 — separat test når den er i en release

Denne funktion er ikke en del af den allerede frigivne v0.8.41-pakke. Test den først i den efterfølgende QA-grønne release, der eksplicit indeholder PAGE-DELETE-001.

Test på en **ny midlertidig almindelig side**, aldrig på Hjem/Vehicle/Event/Gallery:

1. Klik **Slet side** og annullér prompten → siden må være uændret.
2. Klik igen og skriv forkert titel → siden må være uændret.
3. Skriv korrekt titel, men annullér sidste bekræftelse → siden må være uændret.
4. Gennemfør med korrekt titel → siden skal flyttes til WordPress Papirkurv.
5. Bekræft success notice med safety-backup-filnavn.
6. Gendan siden fra det eksisterende B1 backup/restore-panel.
7. Bekræft at titel, status, indhold og Page Editor-state er tilbage.

Beskyttede kernesider skal slet ikke vise/udføre funktionen.

## 16. Evidence

Et scenarie må kun sættes til `PASS`, når der er en konkret reference, fx:

- screenshot;
- kort observation med timestamp;
- browserlog eller testnotat;
- backupfil/recovery-reference.

Efter sessionen kan de eksisterende acceptance-værktøjer validere og rapportere recorden. `overallStatus=PASS` for A–L er kun et LEGO-resultat og må ikke fortolkes som samlet I9 PASS eller I10/public-cutover authorization.
