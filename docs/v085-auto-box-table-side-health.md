# v0.8.5 – Auto-kasser, Tabel og kompakt Side Health

## Auto-kasser

Auto-kasser genbruger den eksisterende `grid` + `container`-model. Antallet af direkte under-elementer bestemmer automatisk desktop-kolonnerne:

- 1 kasse = 1 kolonne / 100 %
- 2 kasser = 2 lige kolonner
- 3 kasser = 3 lige kolonner
- op til 6 automatiske kolonner

Afstand styres fortsat med `LayoutGapPx`/`MobileLayoutGapPx`. Mobil starter på én kolonne. Hver Kasse er et normalt Container-element og beholder derfor sine egne eksisterende Inspector-indstillinger for baggrund, tekst-/overskriftsfarve, font, fontstørrelser, padding, border, shadow og responsive overrides.

Layout-værktøjet følger den eksisterende Editors `is-selected`-markering, når elementets body flyttes til Inspector, så felterne læses/skrives fra det korrekte element.

## Tabel

Tabel er et visuelt værktøj oven på det eksisterende `html`-element. Det giver UI til:

- rækker og kolonner
- første række som tabeloverskrift
- zebra-striber
- border-, header-, celle- og tekstfarver
- fontstørrelse og celle-padding
- vandret scroll på mobil eller normal tabel
- direkte redigering af celleindhold

Den gemte HTML passerer fortsat den eksisterende server-side `wp_kses_post()`-sanitering. Der introduceres ingen ny public renderer eller separat tabel-database.

## Side Health

Side Health starter sammenklappet i Inspector. Den kompakte linje viser score og antal fejl/advarsler, mens analysen fortsætter i baggrunden. Klik på Side Health folder scoreområder, filtre og issue-listen ud. Dette frigør Inspector-plads til Indhold, Typografi, Design og Avanceret.

## Sikkerhedsgrænse

- Assets indlæses kun på `Hangar18 → Sider` for brugere med `edit_pages`.
- Layout-scriptet indlæses efter den eksisterende Hangar18 page-editor.
- Vehicle/Event/Gallery-runtime ændres ikke.
- Der tilføjes ingen public activate/cutover/publish-handler.
- Public sidekonvertering er fortsat låst bag I9/I10-gates.
