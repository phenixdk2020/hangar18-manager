# Visual Designer Manager – idéliste

**Statusdato:** 1. september 2026  
**Status:** Idéer / ikke en del af v0.1.75 medmindre de senere godkendes eksplicit.

## Relationer mellem moduler

### IDEA-EVENT-VEHICLES-001 — Deltagende køretøjer på event
- Et event kan vælge 0..n køretøjer fra Køretøjsmodulet.
- Eventets frontend kan vise sektionen **Køretøjer ved arrangementet** med billede, navn og link til køretøjets detaljevisning.
- Relationen gemmes som stabile køretøjs-record-IDer, ikke kopier af køretøjsdata.
- Relationerne kan ændres både før og efter eventet.
- Historiske events bevarer relationerne, så gamle event-sider stadig kan vise hvilke køretøjer der deltog.
- Samme princip skal kunne kombineres med eksisterende event → album-relation.

### IDEA-RELATED-CONTENT-001 — Relateret indhold
- Eventdetalje kan samlet vise: eventinfo → deltagende køretøjer → tilknyttet billedalbum.
- Køretøjsdetalje kan senere vise **Har deltaget i disse events**.
- Album kan senere vise **Billeder fra dette event**.

## Forside / teaser-koncept

### IDEA-HOME-TEASERS-001 — “Aktuelt fra foreningen” med tre dynamiske teaser-kort
- Lav en rolig sektion på forsiden med overskriften **Aktuelt fra foreningen**.
- Brug **tre kort i én række på desktop**, ikke slider/carousel.
- Kortene skal være:
  1. **Næste event**.
  2. **Udvalgt køretøj**.
  3. **Seneste billeder**.
- Kortene skal følge samme beige/olivengrønne visuelle stil som resten af sitet, men være lidt mere markante end almindelige informationskasser.
- Brug stort billede øverst, begrænset tekst og én tydelig handling nederst.
- Eksempel på handlinger: **Se event →**, **Se køretøj →**, **Se album →**.
- Undgå lange tekstblokke i teaser-kortene; de skal hurtigt kunne scannes.

### IDEA-HOME-NEXT-EVENT-001 — Automatisk “Næste event”
- Forsiden skal automatisk vælge det førstkommende publicerede event.
- Brug eventets dato som primær information og evt. sted som sekundær information.
- Eventkortet skal have et tydeligt **dato-badge** oven på billedet eller i billedområdet, fx stor dag + kort måned: **14 / MAJ**.
- Brugeren skal ikke manuelt vedligeholde hvilket event der vises på forsiden.
- Når et event er afholdt, skal næste event automatisk overtage teaser-pladsen.

### IDEA-HOME-FEATURED-VEHICLE-001 — Udvalgt køretøj på forsiden
- Teaseren kan vise ét **Udvalgt køretøj** med billede, navn, kort beskrivelse og link.
- Første valg bør være et manuelt flag **Fremhævet**, så foreningen selv bestemmer hvilket køretøj der skal stå på forsiden.
- Som mulig senere funktion kan systemet automatisk rotere mellem publicerede køretøjer, hvis intet køretøj er markeret som fremhævet.

### IDEA-HOME-LATEST-GALLERY-001 — Seneste billeder på forsiden
- Teaseren **Seneste billeder** skal automatisk bruge det senest publicerede album.
- Vis coverbillede, albumnavn og evt. billedantal.
- Klik/handling fører direkte til albummets detaljevisning.
- Ingen manuel vedligeholdelse af forsiden skal være nødvendig, når et nyt album publiceres.

### IDEA-HOME-TEASER-MOBILE-001 — Mobil layout
- På mobil stables de tre teaser-kort lodret i denne rækkefølge:
  1. **Næste event**.
  2. **Udvalgt køretøj**.
  3. **Seneste billeder**.
- Ingen mobil-slider/carousel; almindelig vertikal scrolling foretrækkes for enkelhed, tilgængelighed og robusthed.
- Kortene skal være fuld bredde med samme spacing og billedforhold.

### IDEA-HOME-TEASER-PLACEMENT-001 — Placering på forsiden
- Anbefalet rækkefølge: **Intro/velkomst → Aktuelt fra foreningen → øvrigt forsideindhold**.
- Formålet er hurtigt at vise besøgende **hvad der sker, hvad foreningen har, og hvad foreningen laver**.
- Teaser-sektionen må ikke konkurrere visuelt med hovednavigation/header, men skal ligge højt nok til at være synlig uden lang scrolling.

### IDEA-HOME-MEMBERSHIP-CTA-001 — Bred “Bliv medlem”-CTA på forsiden
- Placer en bred CTA-sektion **under de tre teaser-kort** på forsiden.
- CTA'en skal ikke være et fjerde almindeligt teaser-kort; den skal visuelt fungere som en tydelig afsluttende handlingsbjælke.
- Forslag til indhold: kort tekst om medlemskab + tydelig **Bliv medlem**-knap til siden `bliv-medlem`.
- Designet skal følge samme farver, typografi og spacing som resten af sitet, men have nok kontrast til at være let at få øje på.
- På mobil vises CTA'en i fuld bredde under de stablede teaser-kort.

## UX og frontend-forbedringer

### IDEA-SEARCH-FILTER-001 — Ensartet søgning og sortering
- Samme kompakte søge-/sorteringsbjælke på Events, Køretøjer og Billedgalleri.
- Live filtrering uden sidegenindlæsning, men med almindelig server-renderet fallback.
- Vis antal fund, fx **12 køretøjer** eller **3 events**.
- Knap til **Nulstil** når søgning/filter er aktivt.

### IDEA-VEHICLE-CATEGORIES-001 — Valgfrit kategorifilter
- Bevar kategori som data allerede nu.
- Senere mulighed for kategorifilter som chips/dropdown, fx pansret, hjulkøretøj, trailer, materiel mv.
- Kategorifilter skal kunne slås til/fra i modulets indstillinger.

### IDEA-FEATURED-001 — Fremhævet indhold
- Mulighed for at markere et event, køretøj eller album som **Fremhævet**.
- Et fremhævet element kan vises større øverst uden at ændre den normale sortering.

### IDEA-EVENT-CALENDAR-001 — Kalenderfunktioner
- **Tilføj til kalender** på eventdetaljer med ICS-download.
- Eventkort kan vise et lille dato-badge med dag/måned for hurtigere scanning.

### IDEA-EVENT-STATUS-001 — Tydelige event-statusser
- Automatisk visning af **Kommende**, **I dag**, **I gang** og **Afholdt** ud fra start/slut.
- Status er visuel information; den ændrer ikke det gemte event-record manuelt.

### IDEA-CARD-PARITY-001 — Fælles kortdesign
- Events, køretøjer og album bruger samme overordnede spacing, radius, typografi og hover-adfærd.
- Hvert modul beholder sin egen informationsstruktur, men føles som ét designsystem.

### IDEA-IMAGE-QUALITY-001 — Bedre billedpræsentation
- Ensartede billedforhold og focal point/crop pr. modul.
- Lazy loading og korrekte WordPress image sizes/srcset.
- Albumkort kan få diskret billedantal-overlay på coveret.

### IDEA-EMPTY-STATES-001 — Bedre tomme resultater
- Ved ingen søgeresultater vises en venlig tekst og **Nulstil søgning**.
- Ved ingen kommende events kan seneste tidligere events stadig være let tilgængelige.

### IDEA-BACK-LINK-001 — Tilbage-link på detaljesider
- Brug et enkelt tilbage-link i stedet for breadcrumbs.
- Events: **← Tilbage til Events**.
- Køretøjer: **← Tilbage til Køretøjer**.
- Billedgalleri: **← Tilbage til Billedgalleri**.
- Ingen breadcrumbs på forsiden.

### IDEA-SHARE-001 — Deling
- Valgfri **Del**-funktion på events, køretøjer og album med kopier-link og native share på understøttede enheder.

### IDEA-ADMIN-RELATIONS-001 — Bedre relation-vælger i Manager
- Søgbar multi-select til event → køretøjer og event → album.
- Miniature + titel i valglisten, så man ikke skal kende record-IDer.
- Valgte relationer kan drag-sorteres hvis visningsrækkefølge senere bliver relevant.

## Princip

Idélisten er ikke release-scope. Punkter flyttes først til canonical backlog/release-plan efter eksplicit godkendelse.
