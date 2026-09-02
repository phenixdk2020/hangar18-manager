# Visual Designer Manager v0.1.81 – plan

**Status:** Planlagt – ikke frigivet  
**Grundlag:** v0.1.80

## Scope

### STATUS-READY-001 — Manager-status

- **Sider** ændres fra `Under udvikling` til `Klar` i Manager-menuens statusbadge.
- **Eventfelter** vises som `Klar` i Manager-menuens statusbadge.
- Statusændringerne må ikke ændre side-, event- eller frontenddata.

### VD-COLOR-PICKER-001 — Temafarver + fri farvevælger

Visual Designer skal have én fælles forbedret farvevælger til relevante designfelter.

Krav:

- Vis **temafarver / Visual Designer-paletten** som hurtige farvefelter øverst.
- Temafarver er kun genveje og må **ikke begrænse farvevalget**.
- Bevar mulighed for at vælge **alle farver** via normal fuld farvevælger.
- Bevar/tilføj direkte **HEX-indtastning**, fx `#6A6963`.
- RGB/fri farvevalg skal fortsat være muligt gennem den normale picker.
- Klik på en temafarve skal sætte den valgte farve i det almindelige canonical farvefelt.
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

## QA-gate

1. Vælg en temafarve og verificér identisk farve i Designer-preview og frontend.
2. Vælg en vilkårlig farve, som **ikke** findes i temapaletten, og verificér at den kan gemmes og reloades.
3. Indtast en HEX-værdi manuelt og verificér canonical round-trip efter Gem/Reload.
4. Test Gennemsigtig på mindst én understøttet baggrundsegenskab.
5. Test farvevælgeren på baggrund, tekst, ramme og en hover/focus-egenskab.
6. Verificér at eksisterende layouts med gemte HEX-farver er byte-/værdi-kompatible efter opdatering.
7. PHP/JavaScript syntax og alle eksisterende regression-gates skal forblive grønne.
