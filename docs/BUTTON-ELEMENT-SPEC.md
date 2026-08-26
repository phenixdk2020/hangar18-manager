# Visual Designer – Knap-element

**Status:** Godkendt designspecifikation  
**Dato:** 26. august 2026  
**Backlog:** `CLEAN-ELEMENT-BUTTON-028`

## Formål

Knap skal være et generelt Visual Designer-element, som kan bruges på almindelige sider samt i Header- og Footer-templates.

Knap starter visuelt som et almindeligt rektangel. Hjørnerne styres med samme `Radius`-princip som Kasse, Tekst og Billede, så brugeren selv kan vælge alt fra helt firkantet til kraftigt afrundet/pilleformet.

Eksempel:

```text
Radius 0 px       = firkantet knap
Radius 6–10 px    = let afrundet knap
Radius 20–30 px   = tydeligt afrundet knap
Radius 999 px     = pilleformet knap
```

Knappen på det eksisterende testsite kan derfor genskabes nativt i Visual Designer uden et særligt site-specifikt element.

## Canonical element

Elementtype:

```text
button
```

Elementet bruger samme fælles geometri som andre leaf-elementer:

- `x`
- `y`
- `w`
- `h`
- `parentId`
- `order`
- responsive Desktop/Laptop/Mobil-geometri

Knap må ligge i Sektion eller Kasse og må ikke ligge direkte på root.

## Indhold

Inspector skal mindst have:

- Knaptekst
- Linktype
- Destination
- Åbn link i ny fane
- Tilgængeligt navn hvis nødvendigt

### Linktyper

Første version skal understøtte:

1. **Intern side** – vælg en WordPress-side fra en liste.
2. **Ekstern URL** – indtast URL.
3. **Anker** – fx `#kontakt`.
4. **E-mail** – `mailto:`.
5. **Telefon** – `tel:`.

Når knappen navigerer til en URL, skal frontend rendere semantisk som `<a>` og ikke som et kunstigt JavaScript-click på en `<div>`.

Hvis der senere kommer egentlige handlinger, fx åbning af modal eller formularhandling, kan elementet rendere som `<button>` for disse action-typer.

## Design

Inspector skal mindst kunne styre:

### Knapboks

- Bredde og højde via Designer-geometrien
- Baggrundsfarve
- Border-tykkelse
- Border-farve
- Radius
- Padding X
- Padding Y
- evt. skygge senere

### Tekst

- Skrifttype/arv fra Global Design
- Skriftstørrelse
- Font weight
- Tekstfarve
- Justering
- Linjehøjde
- evt. bogstavafstand senere

### Placering

Teksten skal som standard være centreret både vandret og lodret i knappen.

Der skal senere kunne vælges venstre/center/højre, især hvis knappen kombineres med ikon.

## Tilstande

Knap skal have separate visuelle tilstande:

- Normal
- Hover
- Focus
- Active/pressed hvor relevant

Hover skal mindst kunne ændre:

- baggrundsfarve
- tekstfarve
- border-farve

Focus må ikke bare fjernes. Der skal være en tydelig keyboard-focus markering af hensyn til accessibility.

## Linksikkerhed

- Eksterne links skal sanitiseres med WordPress URL-funktioner.
- `target="_blank"` skal ledsages af sikker `rel`-værdi, fx `noopener`.
- JavaScript-URL'er må ikke accepteres.
- Intern side-reference bør gemmes med stabil WordPress object/post reference, ikke kun den nuværende URL, så permalinkændringer kan følges.

## Responsive regler

Samme knap-ID og samme tekst/link bruges på Desktop, Laptop og Mobil.

Følgende må kunne variere pr. breakpoint:

- x/y/w/h
- padding
- tekststørrelse hvor responsive overrides er nødvendige
- evt. skjul/vis senere

Indhold og destination må ikke automatisk duplikeres pr. breakpoint.

## Header/Footer

Knap-elementet er et almindeligt genbrugeligt element og skal ikke have en særskilt Header-version.

Eksempler:

```text
Header
└── Sektion
    ├── Logo
    ├── Menu
    └── Knap: "Bliv medlem"

Footer
└── Sektion
    └── Knap: "Kontakt os"
```

Det betyder, at Header/Footer Designer skal genbruge samme Knap-implementation som Side Designer.

## UX

Når `Knap` trækkes ind fra Elementer-paletten, skal den starte i en brugbar størrelse og have en neutral standardtekst, fx:

```text
Knap
```

Inspector skal holde de vigtigste felter øverst:

1. Tekst
2. Link
3. Baggrund/tekstfarve
4. Radius
5. Padding
6. Typografi
7. Hover/Focus
8. Avanceret

## Definition of Done

Knap-elementet er ikke færdigt før:

- kan indsættes i Sektion/Kasse;
- kan flyttes og resize som andre elementer;
- firkantet og afrundet design virker via Radius;
- tekst kan redigeres;
- intern side kan vælges;
- ekstern URL virker;
- anker, mail og telefon virker;
- ny fane virker sikkert;
- normal/hover/focus styling virker;
- Designer, Preview og frontend matcher;
- Desktop/Laptop/Mobil er QA-testet;
- keyboard-focus er tydelig;
- samme element virker i Side, Header og Footer.
