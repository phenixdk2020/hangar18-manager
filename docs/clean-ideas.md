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

### IDEA-HOME-MEMBERSHIP-CTA-001 — Bred “Bliv medlem”-CTA på forsiden
- Placer en bred CTA-sektion **under de tre teaser-kort** på forsiden.
- CTA'en skal ikke være et fjerde almindeligt teaser-kort; den skal visuelt fungere som en tydelig afsluttende handlingsbjælke.
- Forslag til indhold: kort tekst om medlemskab + tydelig **Bliv medlem**-knap til siden `bliv-medlem`.
- Designet skal følge samme farver, typografi og spacing som resten af sitet, men have nok kontrast til at være let at få øje på.
- På mobil vises CTA'en i fuld bredde under de stablede teaser-kort.

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
