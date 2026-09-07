# Visual Designer Manager V3 — 3.0.0-alpha.20

## Scope

Alpha.20 retter tre fejl fra den seneste test4-gennemgang:

1. Menu-elementet findes i Header-designeren og har `Hovedmenu` valgt, men navigationen kan være væk på den offentlige Header.
2. VDM Menu kan vise eksisterende WordPress-menuer, men kan ikke selv oprette eller slette dem.
3. Mobilvisningen er stadig ikke 1:1 med den godkendte V1-reference, fordi nested full-width bands kan være fanget i Section/Container-wrappers med inherited horizontal padding.

## Menu CRUD

VDM → Menu får nu en direkte `+ Ny menu`-handling samt `Slet` pr. menu. Begge handlinger bruger WordPress' native `wp_create_nav_menu()` / `wp_delete_nav_menu()`, `edit_theme_options` capability og separate nonces. WordPress' egen menu-editor bevares som avanceret redigering af menupunkter og rækkefølge.

## Header live-paritet

Designerens Menu-node er fortsat den canonical kilde. Frontend-rendereren resolver det valgte menu-ID ved runtime. Hvis ID'et er slettet, stale eller ikke længere indeholder punkter, vælges først en ikke-tom menu fra en registreret menu-location og derefter en eksisterende ikke-tom WordPress-menu. Den gemte Header-template omskrives ikke.

På desktop får Header-navigationen desuden en eksplicit visibility/overflow-kontrakt, så et korrekt renderet Menu-element ikke skjules af shell-, Section- eller Container-styling.

## Mobil 1:1 hardening

Alpha.19 fandt de nested semantiske mobile bands korrekt. Alpha.20 udvider dette ved også at rydde inherited horizontal padding på Section/Container-ancestor path for de store V1-bands. Hero/tagline og de store indholdssektioner kan dermed nå den korrekte mobile kant, mens Bevaring/Formidling/Fællesskab fortsat bruger deres eksplicitte inset-card-regler.

## Ikke ændret

- V1 0.1.93 source baseline ændres ikke.
- Gemte side-/template-layoutdata omskrives ikke af Header/menu-fixet.
- Alpha.14 details/summary hamburger-navigation bevares.
- Alpha.17 Eventlist controls og Alpha.19 nested mobile semantics bevares.

## Acceptance

Release må først publiceres efter grøn V1 regression QA, Alpha.19 reproving, PHP/JS syntax check og verificeret installable ZIP. Den endelige 1:1 mobilaccept foretages fortsat visuelt på den rigtige telefon mod de godkendte referencebilleder.