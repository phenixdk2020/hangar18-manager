# Visual Designer Manager V3 — Alpha.43 Designer+ Productivity Suite

Version: `3.0.0-alpha.43`

## Formål

Alpha.43 samler den store Designer-produktivitetsopgradering i én release. Frontend-rendereren, eksisterende layouts, Header/Footer-kontrakter, modulernes Footer-gap og den stabile updater-kanal bevares.

Designer+ åbnes fra den nye **Designer+**-knap i Visual Designer. `Ctrl+K` åbner Command Palette.

## 1. WYSIWYG og sammenligning med live

- Laptop, Tablet og Mobil fortsætter gennem den canonical frontend-renderer.
- **Sammenlign med live** viser den usavede Designer-model og den publicerede side side-by-side ved den valgte viewport.
- WordPress admin-bar fjernes i same-origin sammenlignings-iframe, så geometrien er sammenlignelig.

## 2. Lag+

- Omdøb elementer med egne lagnavne.
- Typeikon og kort stabilt ID på alle lag.
- Skjul/vis et element i editoren uden at slette det.
- Lås/lås op for at beskytte mod utilsigtet flytning.
- Drag-and-drop ændrer rækkefølge blandt søskende i samme parent.
- Elementer-panelets Alpha.41 fold-ud-knap forbliver permanent tilgængelig.

## 3. Undo/Redo-historik

- Designer+ viser lokale Undo-trin som en klikbar historik.
- Et klik på et ældre trin udfører de nødvendige canonical Undo-operationer.
- Alle Designer+-mutationer bruger den eksisterende normalize/commit/render-model.

## 4. Autosave og crash recovery

- Usavede modeller gemmes lokalt i browseren efter ændringer.
- Hvis editoren genåbnes med en nyere lokal kladde, vises **Gendan** / **Kassér**.
- Recovery opretter ikke en publiceret sideversion; normal Gem/Gem som ny version er fortsat den permanente lagring.

## 5. Responsive inheritance

Designer+ viser for valgt element om Laptop/Tablet/Mobil:

- arver Desktop; eller
- har et lokalt override.

**Nulstil til Desktop** sætter den valgte breakpoint-geometri tilbage til inheritance.

## 6. Visuel box-model / spacing

Designer+ viser en enkel box-model og direkte felter for:

- Padding
- Gap X
- Gap Y

Ændringer går gennem normal Undo/Redo.

## 7–8. Multi-select og alignment

Ctrl/Shift+klik vælger flere elementer.

For elementer med samme parent kan Designer+:

- venstre-, center- og højrejustere
- top-, midt- og bundjustere
- sætte samme bredde
- sætte samme højde
- fordele vandret
- fordele lodret

## 9. Copy/paste mellem sider

Den eksisterende Visual Designer clipboard-model bevares og kan fortsat bruges på tværs af sider. Alpha.43 ændrer ikke clipboard-formatet.

## 10–11. Lokale og globale komponenter

En valgt Sektion kan gemmes som:

- **Lokal komponent** — browserbibliotek; indsættelse laver en uafhængig kopi.
- **Global komponent** — gemmes site-wide i WordPress.

Når en global komponent opdateres fra en linket instans:

- alle gemte sider med samme komponent-ID synkroniseres;
- rootens lokale placering/geometri bevares;
- under-elementer genopbygges med collision-safe ID'er;
- hver ændret side får en ny Visual Designer-version.

## 12. Design Tokens

Site-wide tokens findes for:

- farver
- radius
- spacing
- fonts

Tokens kan linkes til et valgt element. **Gem + synkronisér** opdaterer gemte sider, som bruger tokenreferencen, og opretter versionshistorik på de ændrede sider.

## 13. Vis kun breakpoint-overrides

Responsive-panelet kan filtrere Lag+, så kun elementer med lokal breakpoint-geometri vises.

## 14 og 25. Responsive QA / Test siden

**Test siden** kontrollerer bl.a.:

- manglende alt-tekst
- billede uden kilde
- tom eller `#` linkdestination
- tomme tekstelementer
- elementer uden for 120-unit-bredden
- meget smalle knapper
- overlap mellem søskende på Desktop
- vandret overflow i det aktuelle canonical frontend-preview

Resultatet vises som fejl/advarsler/OK.

## 15–17. Viewport, safe-area, presets og rotation

Device presets:

- iPhone SE · 375 px
- iPhone 15 · 393 px
- Galaxy S24 · 360 px
- iPad · 820 px
- iPad landscape · 980 px
- Laptop · 1100 px
- Desktop · 1920 px

Presetbredden ændrer canonical preview-iframe'ets CSS viewport, ikke frontendens offentlige breakpointkonstanter.

**Rotér** bytter preset bredde/højde. Safe-area-overlay tegnes inde i preview-iframe'et.

## 18. Billedeværktøjer

For et valgt billede:

- Cover
- Contain
- Original
- Zoom + / Zoom −
- manuel X/Y-position
- klikbart fokuspunkt
- centrér fokus
- alt-tekst
- Udskift billede via eksisterende WordPress-medievælger

## 19. Sektionspresets

Designer+ kan indsætte:

1. Hero + CTA
2. Tekst + billede
3. 2 kolonner
4. 3 infokort
5. CTA-bånd
6. FAQ
7. Kontakt
8. Galleri

De indsættes som almindelige canonical Visual Designer-noder og kan redigeres normalt bagefter.

## 20. Sikker sletning

Hvis et element indeholder børn, viser canonical Delete nu antallet af under-elementer før sletning og kræver eksplicit bekræftelse på at slette hele træet.

## 21. Versionssammenligning

To gemte Visual Designer-versioner kan vises side-by-side gennem frontend-preview-rendereren.

Sammenligningen viser også en opsummering af:

- tilføjede elementer
- slettede elementer
- geometriændringer
- tekstændringer
- design/property-ændringer

## 22. Workflow-status

Toolbar viser:

- **Publiceret**
- **Kladde**
- **Ikke gemt**

Ikke-gemt markeres, når canonical model-change event registreres.

## 23. Inspector+

- søgning i Inspector
- favoritfelter
- eksisterende sticky/scroll-bevarelse bevares

## 24. Command Palette

`Ctrl+K` giver hurtig adgang til bl.a.:

- Tilføj Sektion/Tekst/Billede/Knap
- Desktop/Laptop/Tablet/Mobil
- Sammenlign med live
- Test siden
- Gem som ny version
- Komponenter
- Design Tokens

## Regression locks

Alpha.43 bevarer:

- V1 0.1.93 source baseline
- Alpha.41 Elementer-panel recovery
- Alpha.38 valgt viewport for **Vis med Header + Footer**
- Alpha.37 page-only responsive Designer-preview
- Alpha.36 Laptop/Tablet fluid parity
- Alpha.31 Module Footer Gap
- Website-menu/Header/Footer-kontrakter
- eksisterende frontend-rendering og public breakpoints

## Manuel acceptance efter installation

1. Fold Elementer ind/ud og verificér at genåbn-ikonet altid er synligt.
2. Ctrl+klik tre elementer og test alignment + Undo.
3. Omdøb, skjul, lås og drag et lag.
4. Lav en ændring, genindlæs uden at gemme, og test lokal recovery.
5. Test iPhone/iPad presets, rotation og safe-area.
6. Gem en Sektion lokalt og indsæt den igen.
7. Gem en test-Sektion globalt, indsæt den på en anden testside, opdatér den og verificér synkronisering/version.
8. Link et Design Token på en testside og test Gem + synkronisér.
9. Test billedfokus, Zoom, X/Y, alt-tekst og Udskift billede.
10. Indsæt hvert af de otte Sektionspresets på en testsiden.
11. Sammenlign Designer mod live.
12. Sammenlign to gemte versioner og verificér diff-opsummeringen.
13. Kør **Test siden** og kontroller at kendte testfejl registreres.
14. Åbn Ctrl+K og kør mindst tre kommandoer.
