from pathlib import Path
import re

DESIGN = Path('CLEAN-DESIGN-MANUAL.md')
USER = Path('CLEAN-USER-MANUAL.md')


def update_design_manual() -> None:
    text = DESIGN.read_text(encoding='utf-8')
    text = text.replace('Senest opdateret: 25. august 2026', 'Senest opdateret: 27. august 2026', 1)

    start_marker = '## 24. Dokumentationsregel'
    end_marker = '## 0.1.23 – Global Header/Footer Designer'
    start = text.index(start_marker)
    end = text.index(end_marker)

    replacement = '''## 24. Dokumentationsregel

Når et nyt Visual Designer-designvalg godkendes:

1. Opdatér den canonical Visual Designer-model eller relevante globale indstilling.
2. Opdatér denne design- og arkitekturmanual.
3. Opdatér `CLEAN-USER-MANUAL.md`, når ændringen er synlig eller relevant for en redaktør/administrator.
4. Tilføj ændringen til release-notes/changelog.
5. Kør QA på editor, Save/Reload, Preview og frontend.
6. Byg først en verificeret GitHub-releasepakke, når den aftalte release skal publiceres.

### 24.1 Krav til brugermanualens grafiske dokumentation

Brugermanualen må ikke kun beskrive Visual Designer med tekst. Når et begreb, en arbejdsgang eller et layout forstås bedre visuelt, skal manualen suppleres med **grafiske eksempler og illustrationer**.

Som minimum skal følgende områder dokumenteres visuelt:

- en komplet websides anatomi med **Tema/Shell → Header → Side → Footer**;
- forskellen mellem **Header/Footer** og en sides **Hero/Topbanner**;
- LEGO-hierarkiet **Side → Sektion → Kasse → indholdselement**;
- typiske kolonne-, celle-split- og nested-Kasse-layouts;
- drag-and-drop med Over/Under/Venstre/Højre/Ind i;
- Desktop/Laptop/Mobil og responsive overrides;
- billedboks kontra selve billedet;
- normal kontra flydende Knap;
- Tabel, herunder cellemarkering og Excel-lignende rammevalg;
- Menu, Galleri, Formular og andre større elementtyper, når de frigives.

Grafiske eksempler skal følge disse regler:

- Illustrationer lagres som vedligeholdelige dokumentationsassets, fortrinsvis SVG til diagrammer og PNG/JPG til relevante screenshots.
- Hver illustration skal have en kort forklaring/caption og meningsfuld alt-tekst.
- Diagrammer skal vise det samme hierarki og de samme begreber som den canonical model; de må ikke introducere en alternativ layoutlogik.
- Screenshots og UI-illustrationer skal opdateres, hvis Designerens brugerflade ændres væsentligt.
- En illustration af en planlagt funktion skal tydeligt mærkes **Planlagt** og må ikke præsenteres som allerede frigivet funktionalitet.
- Før/efter-illustrationer anvendes, når de gør drag/drop, responsive ændringer, formattering eller migration lettere at forstå.
- Grafikken skal være læsbar både på almindelig desktop og ved nedskalering i dokumentation.
- Visuelle eksempler skal, hvor relevant, vise realistiske kombinationer af flere elementer frem for kun isolerede kontrolfelter.

Dokumentationen skal derfor forklare både **hvad et element er**, **hvor det kan ligge**, **hvordan det kombineres med andre elementer**, og **hvordan resultatet ser ud i en rigtig sideopbygning**.

`CLEAN-DESIGN-MANUAL.md` er fremover den autoritative arkitekturbeskrivelse for den nye Visual Designer. Den ældre `DESIGN-MANUAL.md` bevares som reference for eksisterende designstandarder og legacy 0.4.x-adfærd, indtil de relevante regler er migreret til Clean.

'''

    text = text[:start] + replacement + text[end:]
    DESIGN.write_text(text, encoding='utf-8')


def update_user_manual() -> None:
    text = USER.read_text(encoding='utf-8')
    text = text.replace('Senest opdateret: 25. august 2026', 'Senest opdateret: 27. august 2026', 1)
    text = text.replace(
        'Gælder fra: Visual Designer Manager 0.1.18',
        'Gælder for: Visual Designer Manager 0.1.31 og nyere; planlagte funktioner er mærket **Planlagt**',
        1,
    )

    marker = '## 2. Sådan er en webside bygget op'
    if marker not in text:
        def renumber(match: re.Match) -> str:
            n = int(match.group(1))
            return f'## {n + 1}. ' if n >= 2 else match.group(0)

        text = re.sub(r'^## (\d+)\. ', renumber, text, flags=re.M)

        chapter = '''## 2. Sådan er en webside bygget op

Visual Designer bygger en webside som LEGO. Nogle elementer skaber **struktur**, mens andre er **indhold**. Header og Footer er globale, mens den enkelte sides indhold bygges af Sektioner, Kasser og indholdselementer.

![Grafisk oversigt over Header, Hero, sideindhold og Footer](docs/user-manual-assets/page-anatomy.svg)

*Figur 1 – En typisk Visual Designer-side. Header og Footer er globale. Hero/Topbanner og resten af indholdet tilhører selve siden.*

### 2.1 Det overordnede princip

```text
WORDPRESS
└── TEMA / SHELL
    ├── GLOBAL HEADER
    │   ├── Logo
    │   ├── Menu
    │   ├── Knap
    │   └── Icon/Tekst
    │
    ├── SIDE
    │   ├── Hero / Topbanner
    │   ├── Sektion
    │   │   ├── Kasse
    │   │   │   ├── Billede
    │   │   │   └── Tekst
    │   │   └── Kasse
    │   │       ├── Tekst
    │   │       └── Knap
    │   ├── Divider
    │   ├── Sektion → Tabel
    │   ├── Sektion → Galleri
    │   └── Sektion → Formular / FAQ
    │
    └── GLOBAL FOOTER
        ├── Logo
        ├── Menu / Links
        ├── Kontakt
        ├── Icons
        └── Copyright
```

### 2.2 Tema / Shell

Temaet er den tekniske WordPress-ramme omkring Visual Designer. Det skal primært håndtere WordPress-lifecycle, hooks, `wp_head()`, `wp_footer()`, nødvendige wrappers, integration og fallback. Det visuelle design skal ligge i Visual Designer frem for i parallelle theme-regler.

**Status:** Theme Shell-konverteringen er under udvikling. Hangar18 Base Theme bruges fortsat som fallback/baseline, indtil visuel parity er godkendt.

### 2.3 Header

Header er et **globalt design** over den enkelte side. Den kan indeholde Logo, Menu, Tekst, Knap og Icon og har sin egen globale model og versionshistorik.

```text
┌──────────────────────────────────────────────────────┐
│ [LOGO]   Hjem  Køretøjer  Events  Galleri  [Kontakt]│
└──────────────────────────────────────────────────────┘
```

### 2.4 Menu

Menu skal være et selvstændigt visuelt element, som kan bruge en WordPress-menu som datakilde, mens Visual Designer styrer fx skrifttype, størrelse, farve, afstand, hover, aktiv side og mobil/hamburger-visning.

**Status: Planlagt som native Visual Designer-element.** WordPress-menuadministration findes allerede separat i Manageren.

### 2.5 Hero / Topbanner

Hero/Topbanner er normalt den første store **Sektion inde i selve siden** og er derfor ikke det samme som Headeren. Hero er typisk stor og markant; Topbanner er samme idé i en lavere variant.

```text
GLOBAL HEADER
────────────────────────
HERO / TOPBANNER
  Baggrundsbillede
  Overskrift
  Undertekst
  [ Knap ]
────────────────────────
RESTEN AF SIDEN
────────────────────────
GLOBAL FOOTER
```

Hero/Topbanner bør være en Sektion-preset/specialisering med fx baggrundsbillede, focal point, overlay, højde og responsive overrides – ikke en separat layoutmotor.

**Status: Planlagt.**

### 2.6 Sektion, Kasse og LEGO-hierarkiet

![Grafisk illustration af Side, Sektion, Kasse og indholdselementer](docs/user-manual-assets/lego-hierarchy.svg)

*Figur 2 – Sektion er sidens hovedblok. Kasse er den fleksible lokale container. Kasser kan indeholde Kasser, men Sektioner nestes ikke som almindelige Kasser.*

```text
SIDE
└── SEKTION
    ├── KASSE
    │   ├── Billede
    │   └── Tekst
    └── KASSE
        ├── Tekst
        └── Knap
```

**Huskeregel:** Sektion = stort område. Kasse = lokal LEGO-klods.

### 2.7 Tekst

Tekst bruges til overskrift, brødtekst, lister og links. Et Tekst-element kan have H2-H6 og brødtekst i samme fysiske boks og kan styles med typografi, farver, alignment, baggrund, padding, ramme, radius og Afstand X/Y.

### 2.8 Billede

Billede består af **billedboksen** og **selve billedet**. Billedet kan fx vises som Contain, Cover, Original, Stretch eller Manuel inde i boksen.

Billede skal også kunne fungere som link med samme fælles linkmodel som Knap og Icon: Ingen, Intern side, Ekstern URL, Anker, E-mail eller Telefon samt *Åbn i ny fane* hvor relevant.

**Status for billede som link: Planlagt udvidelse.**

### 2.9 Knap

Knap er et selvstændigt element og skal ikke behandles som Tekst. En normal Knap deltager i LEGO-layoutet. En **Flydende Knap** er et parent-relativt overlay, som kan ligge over andet indhold uden at reservere en normal grid-celle.

### 2.10 Icon

Icon bruges fx til telefon, mail, lokation, sociale medier, pil, download eller information og skal kunne styles og eventuelt fungere som link.

**Status: Planlagt.**

### 2.11 Divider

Divider er en visuel skillelinje med fx bredde, tykkelse, farve, alignment, afstand og solid/dashed/dotted streg.

**Status: Planlagt.**

### 2.12 Spacer

Spacer er en bevidst tom layoutblok. Den bruges kun, når fysisk tom plads skal være et selvstændigt element; normal afstand styres ellers med Afstand X/Y.

**Status: Planlagt.**

### 2.13 Tabel

Tabel bruges til strukturerede data med rækker, kolonner, overskriftsrække, kolonnebredder, tekst, links, farver, padding og alignment.

![Grafisk eksempel på cellemarkering og Excel-lignende tabelrammer](docs/user-manual-assets/table-borders.svg)

*Figur 3 – Planlagt Tabel-element. En eller flere celler kan markeres, hvorefter rammer vælges på samme måde som i et regneark.*

Rammer skal kunne vælges som **Ydre, Indre, Vandret, Lodret, Top, Bund, Venstre, Højre, Alle eller Ingen**. For valgte rammer skal tykkelse, farve og senere stregtype kunne styres. Flere celler skal kunne markeres samtidig. På mobil skal relevante strategier som vandret scroll, skjulte kolonner eller stablet label/værdi-visning kunne vælges.

**Status: Planlagt.**

### 2.14 Galleri

Galleri kan senere tilbyde Grid, Masonry, Slider/Carousel og Lightbox og kan efter fælles dataarkitektur kobles til Managerens galleri-data.

**Status: Native Visual Designer-element er planlagt.**

### 2.15 Video

Video kan bruges til fx YouTube, Vimeo eller lokal video med URL, controls, autoplay/mute, poster og aspect ratio.

**Status: Planlagt.**

### 2.16 Accordion / FAQ

Accordion/FAQ bruges til indhold, der åbnes og lukkes efter behov, fx ofte stillede spørgsmål.

**Status: Planlagt.**

### 2.17 Tabs

Tabs opdeler beslægtet indhold i faner, fx *Tekniske data*, *Historie* og *Billeder*.

**Status: Planlagt.**

### 2.18 Formular

Formular bruges til fx Kontakt, Bliv medlem og eventtilmelding og kan bestå af tekst-, e-mail-, telefon-, textarea-, valg- og submit-felter.

**Status: Planlagt.**

### 2.19 Dynamiske elementer

Dynamiske elementer kombinerer Manager-data med Visual Designer-layout. Planlagte typer omfatter Køretøj, Event og dynamisk Billedgalleri.

**Status: Planlagt efter fælles dataarkitektur.**

### 2.20 Footer

Footer er ligesom Header et **globalt design** uden for den enkelte sides model. Den kan indeholde Logo, Tekst, Menu/Links, Kasser, Icons, kontaktinformation og copyright og har sin egen versionshistorik.

```text
┌────────────────────────────────────────────────────────┐
│ [LOGO]     LINKS             KONTAKT                   │
│             Hjem              Telefon                  │
│ Foreningen  Køretøjer         E-mail                   │
│             Events            Sociale ikoner           │
│                                                        │
│ © Foreningen                                           │
└────────────────────────────────────────────────────────┘
```

### 2.21 Et komplet sideeksempel

```text
GLOBAL HEADER
├── Logo
├── Menu
└── Knap "Bliv medlem"

SIDE: Køretøjer og materiel
├── HERO / TOPBANNER
│   ├── Baggrundsbillede
│   ├── Tekst "Køretøjer og materiel"
│   └── Knap "Se samlingen"
├── SEKTION
│   ├── Kasse → Billede som link
│   └── Kasse → Tekst + Knap
├── Divider
├── SEKTION → Tekst + Tabel
├── Spacer
├── SEKTION → Tekst + Galleri
├── SEKTION → Accordion / FAQ
└── SEKTION → Formular

GLOBAL FOOTER
├── Logo
├── Menu / Links
├── Kontakt
├── Icons
└── Copyright
```

### 2.22 Globalt kontra sideindhold

| Del | Global | Del af den enkelte side |
|---|---:|---:|
| Tema/Shell | Ja, teknisk ramme | Nej |
| Header | Ja | Nej |
| Menu i Header/Footer | Global placering | Nej |
| Hero/Topbanner | Nej | Ja |
| Sektion | Nej | Ja |
| Kasse | Nej | Ja |
| Tekst/Billede/Knap | Normalt nej | Ja |
| Footer | Ja | Nej |

**Den vigtigste regel:** Header og Footer er globale. Selve siden består af Sektioner. Sektioner indeholder Kasser og indholdselementer. Kasser kan igen indeholde andre Kasser og elementer. Hero/Topbanner er en særlig Sektion øverst på selve siden.

---

'''
        anchor = '## 3. Hvor findes funktionerne?'
        if anchor not in text:
            raise RuntimeError('Expected renumbered chapter anchor not found')
        text = text.replace(anchor, chapter + anchor, 1)

    history = '| 1.0 | Første Visual Designer-brugermanual baseret på funktionerne gennem 0.1.18 og den godkendte målarkitektur. |'
    if '| 1.1 |' not in text and history in text:
        text = text.replace(
            history,
            history + '\n| 1.1 | Nyt kapitel om websides anatomi, Header/Footer kontra Hero, elementoversigt samt grafiske illustrationer og tydelig markering af planlagt funktionalitet. |',
            1,
        )

    USER.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    update_design_manual()
    update_user_manual()
