# Visual Designer Manager V3 — 3.0.0-alpha.14

## Scope

Alpha.14 er en målrettet **V1 Mobile Menu Parity**-rettelse.

V1 er rollemodel/reference. V3 er target. Den fungerende V1-mobilmenu bruger en separat mobilnavigation med native `<details>/<summary>` og et dropdown-panel. Alpha.14 flytter V3's hamburger-adfærd til samme princip i stedet for den V3-specifikke `is-open` JavaScript-toggle inde i Header-grid'et.

## Ændringer

- Hamburger-menuen bruger native `<details>/<summary>` som toggle.
- Menuens åbne panel ligger oven på sideindholdet og ændrer ikke Headerens gemte gridhøjde.
- Mobilpanelet bruger V1-referenceudtrykket: lys/off-white baggrund, mørk tekst, afrunding og skygge.
- WordPress-menulinks forbliver almindelige links; runtime kalder ikke `preventDefault()` på navigation.
- Klik udenfor og Escape kan lukke menuen som progressiv enhancement.
- Submenuer vises statisk inde i mobilpanelet efter V1-princippet.
- Designerens mobil-preview bruger samme native details/summary-model.
- Desktop-menuen og Alpha.13's øvrige funktionalitet bevares.

## Acceptance gate

Alpha.14 må først publiceres efter grøn QA, som verificerer V1-referencekontrakten, build, PHP/JS-syntaks, fravær af den gamle `is-open` hamburger-toggle og installationspakkens struktur.

Visuel accept på test4 er fortsat en manuel gate; en grøn kode-QA er ikke i sig selv bevis på pixelmæssig mobilparitet.
