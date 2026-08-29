Hangar18 Base Theme
Version 1.2.0

FORMÅL
------
Et minimalt klassisk WordPress-tema til Hangar18.
Temaet leverer kun det nødvendige WordPress-fundament.

Hangar18 Manager styrer:
- Hangar18-header
- menu
- footer
- køretøjer
- events
- billedgalleri
- sidebredder og de styrede frontend-layouts

TEMAET LEVERER IKKE
-------------------
- Astra Banner Area
- synlig theme-header
- theme-footer
- sidebar
- automatisk sidetitel på WordPress Pages
- ekstra content-containere med faste max-widths

SIKKER OVERGANG FRA ASTRA / TIDLIGERE TEMA
------------------------------------------
Astra eller det tidligere tema slettes IKKE ved aktivering.

Ved aktivering tager Base Theme en permanent kopi af det tidligere temas
"Additional CSS" og gemmer den i sin egen WordPress-option. Den oprindelige
Custom CSS bliver ikke ændret eller slettet. Det betyder, at det tidligere
tema senere kan slettes uden at Base Theme mister overgangs-CSS'en.

Version 1.1.0 indeholder desuden selv de nuværende Hangar18-grundregler for:
- Inter/Segoe UI-typografi
- responsive skriftstørrelser
- overskrifter og knapper
- Gutenberg-blokafstande og bredder
- desktop-, tablet- og mobil-layout

ROLLBACK
--------
Hvis noget ser forkert ud:

1. WordPress -> Udseende -> Temaer.
2. Aktivér Astra igen.
3. Hangar18 Manager-data påvirkes ikke af rollback.

ANBEFALET TEST EFTER AKTIVERING
-------------------------------
1. Hjem
2. Køretøjer og materiel
3. Et enkelt køretøj
4. Events
5. Et enkelt event
6. Billedgalleri
7. Et album
8. Om foreningen
9. Kontakt
10. Desktop og mobil
11. Sticky/pinnet menu hvis aktiveret

Astra bør først slettes, når alle disse sider er godkendt.

ÆNDRINGSLOG 1.1.0
-----------------
- Grundtypografi og blokafstande er flyttet ind i Base Theme.
- Mobil- og desktopværdier følger det eksisterende Hangar18-design.
- Custom CSS fra det tidligere tema gemmes permanent ved aktivering.
- Overgang fra både Astra og Extendable understøttes.

GITHUB-OPDATERINGER FRA 1.2.0
-----------------------------
Temaet kontrollerer sit eget manifest på GitHub gennem WordPress' normale
temaopdateringssystem. Når en nyere version findes, vises den under:

- Kontrolpanel -> Opdateringer
- Udseende -> Temaer

Temaversionen er adskilt fra Hangar18 Manager-pluginets version. Den hentede
pakke kontrolleres med SHA-256, før WordPress får lov til at installere den.

ÆNDRINGSLOG 1.2.0
-----------------
- Automatisk opdatering af Hangar18 Base Theme fra GitHub.
- Separat theme-update.json og temapakke.
- SHA-256-kontrol af den downloadede ZIP.
- Versionsdetaljer og ændringslog vises i WordPress.
