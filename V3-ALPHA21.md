# Visual Designer Manager V3 — 3.0.0-alpha.21

## Scope

Alpha.21 retter den grundlæggende datakilde-fejl omkring navigationen.

Alpha.20 viste to Menu-administrationer på samme VDM-side. Den øverste CRUD-visning og den eksisterende avancerede Menu-editor ejede samme WordPress admin-hook. Samtidig var dropdownen `Aktuel menu` kun et redigeringsvalg og blev derfor ikke husket som hjemmesidens aktive menu.

Alpha.21 samler dette til én entydig model:

- **Website-menu** = den persistente menu som websitet bruger.
- **Redigér menu** = den menu der aktuelt redigeres i VDM; dette valg ændrer ikke websitet.
- **Gem menu** = gemmer menupunkter, rækkefølge og undermenuer.
- **Gem website-menu** = gemmer det site-wide menuvalg.

## Menuadministration

- NavigationController er igen eneste ejer af VDM → Menu; Alpha.20s dobbelte AdminController-callback fjernes.
- Website-menu gemmes i option `vdm_website_menu_id` med eksplicit nonce/capability-kontrolleret handling.
- Opret menu og Slet menu er integreret i den eksisterende avancerede Menu-editor.
- Den aktive website-menu er tydeligt markeret `Aktiv på website`.
- Den aktive website-menu kan ikke slettes, før en anden website-menu er valgt og gemt.
- Website-menu indgår i navigationens snapshot/fingerprint og gendannes sammen med menuerne.

## Header / Footer

Menu-elementet får en eksplicit datakilde:

- `Website-menu` — standard og anbefalet. Bruger den gemte site-wide menu.
- `Specifik menu` — låser det enkelte Menu-element til et bestemt WordPress-menu-ID.

Eksisterende V3 Menu-elementer uden `menuSource` normaliseres til `Website-menu`.

Hvis Alpha.21-optionen endnu ikke er oprettet, bruges eksisterende Header-menu-ID kun som migration/bootstrap. Når Website-menu én gang er gemt, gætter frontenden ikke på en anden menu, hvis ID'et senere bliver ugyldigt.

Footerens delte genvejsmenu følger samme Website-menu-option.

## Designer

Inspector for Menu viser nu `Datakilde` først. Ved Website-menu vises navnet på den aktive website-menu og link til VDM → Menu. Ved Specifik menu vises den eksisterende WordPress-menu-dropdown.

Preview bruger samme website-menu-ID som den live frontend.

## Bevares

- V1 0.1.93 source baseline ændres ikke.
- Alpha.14 mobile details/summary navigation bevares.
- Alpha.17 Eventlist sizing controls bevares.
- Alpha.19/20 mobile edge-parity rettelser bevares.
- Menupunkternes aktuelle indhold/rækkefølge kommer fortsat fra V3/WordPress og kopieres ikke fra den gamle V1-menu.

## Acceptance

1. VDM → Menu viser kun én Menu-administration.
2. Website-menu kan vælges og gemmes eksplicit.
3. Genindlæsning af Menu-siden husker Website-menuen.
4. `Redigér menu` kan skiftes uden at ændre Website-menuen.
5. Headerens Menu-element med `Website-menu` viser den gemte menu på Hjem og øvrige sider.
6. En Menu-node kan alternativt låses til `Specifik menu` i Designer.
7. Aktiv Website-menu kan ikke slettes ved en fejl.

Automatiseret QA er release-gate; frontendens faktiske visuelle menu kontrolleres efterfølgende på test4.