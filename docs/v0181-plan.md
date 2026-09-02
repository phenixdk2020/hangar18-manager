# Visual Designer Manager v0.1.81 – plan

**Status:** Implementeret kandidat – afventer verificeret release  
**Grundlag:** v0.1.80

## Scope

### STATUS-READY-001 — Manager-status

- **Sider** ændres fra `Under udvikling` til `Klar` i Manager-menuens statusbadge.
- **Eventfelter** vises som `Klar` i Manager-menuens statusbadge.
- Statusændringerne må ikke ændre side-, event- eller frontenddata.

### VD-COLOR-PICKER-001 — Én fælles farvevælger med temafarver + fri farve

Visual Designer skal have én ensartet webbaseret farvevælger til relevante designfelter.

Den eksisterende picker-type med farveflade, farvepreview og direkte HEX-felt bruges som UX-reference. Visual Designer skal ikke have forskellige farvevælgere afhængigt af felt/browser/operativsystem, og en Windows/system-picker må ikke være den primære Designer-oplevelse.

Krav:

- Vis **temafarver / Visual Designer-paletten** som hurtige farvefelter i den fælles picker.
- Temafarver er kun genveje og må **ikke begrænse farvevalget**.
- Bevar mulighed for at vælge **alle farver** via fri farveflade/farvevælger.
- Bevar direkte **HEX-indtastning**, fx `#6A6963`, i selve pickeren.
- HEX-felt og visuel farvevælger skal være synkroniserede begge veje.
- RGB/fri farvevalg skal fortsat være muligt gennem den normale picker.
- Klik på en temafarve skal sætte den valgte farve i det samme canonical farvefelt og opdatere HEX-felt/preview med det samme.
- Vis et tydeligt preview/swatch af den aktuelle farve ved feltet i Inspector.
- Understøt **Gennemsigtig / ingen farve** på egenskaber hvor det er semantisk gyldigt.
- Tilføj gerne **senest brugte farver** som hurtigvalg, uden at ændre den canonical model unødigt.
- Paletten skal hentes fra den aktive Visual Designer-/temakonfiguration og må ikke hardcodes til de nuværende AKVPK-farver.
- Samme picker-komponent skal genbruges konsekvent for bl.a.:
  - Baggrund
  - Tekstfarve
  - Rammefarve
  - Knapbaggrund
  - Knaptekst
  - Hover-baggrund
  - Hover-tekst
  - Focus-farve
  - Andre eksisterende farveprops
- Eksisterende gemte HEX-farver skal fortsat kunne læses og redigeres uden migrationstab.
- Designer-preview og frontend skal fortsat bruge samme canonical farveværdi.
- Pickeren skal fungere ens på Windows/macOS/Linux og i understøttede browsere; udseendet må ikke afhænge af operativsystemets native farvedialog.

## QA-gate

1. Vælg en temafarve og verificér identisk farve i Designer-preview og frontend.
2. Vælg en vilkårlig farve, som **ikke** findes i temapaletten, og verificér at den kan gemmes og reloades.
3. Indtast en HEX-værdi manuelt og verificér at farveflade/preview opdateres samt canonical round-trip efter Gem/Reload.
4. Vælg en farve visuelt og verificér at HEX-feltet opdateres med den valgte værdi.
5. Test Gennemsigtig på mindst én understøttet baggrundsegenskab.
6. Test samme picker på baggrund, tekst, ramme og en hover/focus-egenskab.
7. Verificér at ingen af de testede Designer-farvefelter falder tilbage til en separat Windows/system-farvedialog som den normale redigeringsvej.
8. Verificér at eksisterende layouts med gemte HEX-farver er byte-/værdi-kompatible efter opdatering.
9. PHP/JavaScript syntax og alle eksisterende regression-gates skal forblive grønne.


### FORM-WYSIWYG-001 — Kontakt og Bliv medlem

- Designer-preview skal bruge samme feltorden og layoutkontrakt som frontend.
- Preview skal vise labels, inputs, textarea, samtykke og knap – ikke simplificerede labelbokse.
- Kontakt respekterer `showPhone`; medlemsformularen viser altid Telefon som obligatorisk.
- Mobil skifter til én kolonne ved 782 px.
- Previewfelter er deaktiverede og må aldrig indsende data fra Designer.

### DOC-VISUAL-001 — Grafiske manualer

- `CLEAN-USER-MANUAL.md` og `CLEAN-DESIGN-MANUAL.md` opdateres i samme release.
- Manualerne indeholder SVG-illustrationer, elementtabel, arbejdsgange, responsive regler samt godt/dårligt-eksempler.
