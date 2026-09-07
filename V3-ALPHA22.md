# Visual Designer Manager V3 – Alpha.22

Version: `3.0.0-alpha.22`

## Formål

Alpha.22 retter den resterende desktop-fejl, hvor Headerens menu kunne være usynlig, selv om Website-menuen var korrekt valgt og mobilmenuen virkede.

## Rodårsag

Alpha.21 renderede stadig Menu-elementet gennem et HTML `<details>`-element. Mobilvisningen ændrede aktivt disclosure-state, mens desktop var afhængig af CSS, der forsøgte at tvinge indholdet synligt fra den lukkede disclosure-wrapper. Det er en unødvendig og skrøbelig paint-path for en menu, der altid skal være synlig på desktop.

## Ændring

- Desktop-menuen renderes nu i almindelig DOM/layout via en `div`-wrapper.
- Hamburger-triggeren er en rigtig `button` med `aria-expanded`.
- Mobil hamburger åbner/lukker via den eksplicitte klasse `is-open`.
- Escape, klik udenfor og luk ved menuvalg er bevaret.
- `Website-menu` fra Alpha.21 er fortsat den kanoniske standarddatakilde.
- V1 0.1.93 ændres ikke.

## QA

Alpha.22 QA kontrollerer blandt andet, at `<details>` ikke længere bruges til Menu-elementet, at desktop-panelet ligger i normal DOM, at mobil-controlleren findes, at Alpha.21 Website-menu-binding er bevaret, samt at de eksisterende V1 regression gates fortsat er grønne.
