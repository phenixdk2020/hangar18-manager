# Visual Designer Manager V3 – Alpha.23

Version: `3.0.0-alpha.23`

## Formål

Alpha.23 lukker de tydelige mobile forskelle mod den fungerende V1-reference uden at ændre den nu fungerende Alpha.22-menu.

## Mobil V1-paritet

- Headeren bruger et kompakt trekolonne-layout: logo, brandtekst og hamburger.
- Brandteksten bruger en V1-lignende mobil størrelse, så navnet kan ligge på to linjer i den normale telefonbredde.
- Hero-billedet går full-bleed og bruger 160 px mobilhøjde i den V1-konverterede forside.
- Strukturelle Section/Container-wrappers omkring hero/tagline bidrager ikke længere med skjult top/bund-padding.
- Tagline og større semantiske sektioner bruger én kontrolleret `sectionGap` i stedet for flere stablede afstandsmekanismer.
- Bevaring/Formidling/Fællesskab beholder deres inset-kort og bruger `elementGap` mellem kortene.

## Sider → Sideindstillinger → Afstande

Den enkelte side får tre canonical responsive indstillinger:

- **Afstand mellem sektioner**
- **Standard afstand mellem elementer**
- **Afstand til Footer**

Alle tre kan styres separat for Desktop, Laptop, Tablet og Mobil fra 0–200 px.

V1-lignende standarder:

| Indstilling | Desktop | Laptop | Tablet | Mobil |
| --- | ---: | ---: | ---: | ---: |
| Afstand mellem sektioner | 32 | 32 | 24 | 24 |
| Standard afstand mellem elementer | 16 | 16 | 14 | 14 |
| Afstand til Footer | 32 | 32 | 24 | 24 |

Indstillingerne ligger i sidens canonical `pageSettings`, indgår i versionshistorik/digest og følger dermed Gem/Gendan på samme måde som resten af siden.

## Ikke ændret

- Alpha.22 Website-menu og desktop/mobil Header-menu.
- V1 0.1.93 source baseline.
- Eventkortkontroller fra Alpha.17.
- Gemte node-geometrier omskrives ikke.

## Visuel acceptance

Automatiseret QA kan bevise kontrakt, build og regressioner, men den endelige mobilgodkendelse foretages fortsat mod V1-screenshot på den rigtige iPhone/testside.
