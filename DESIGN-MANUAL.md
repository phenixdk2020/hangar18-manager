# Designmanual for Hangar18

Senest opdateret: 16. august 2026  
Gælder fra: Hangar18 Manager 0.4.23

## Formål

Denne manual samler de designvalg, der er godkendt for Aalborg Kaserners Veteran Panser- og Køretøjsforenings hjemmeside. Den skal bruges, når sider, sektioner eller funktioner ændres, så desktop- og mobilversionen fortsat opleves som én sammenhængende hjemmeside.

De aktive værdier i **Hangar18 Manager** er den tekniske sandhed på hjemmesiden. Manualen dokumenterer de godkendte valg og standarder. Når et designvalg ændres, skal både web-managerens indstilling og denne manual opdateres.

## Visuel identitet

| Rolle | Farve | Anvendelse |
|---|---:|---|
| Mørk olivengrøn | `#30382A` | Header, footer, overskrifter og mørke flader |
| Sand/guld | `#C3AE83` | Accenter, knapper og overkant på indholdskort |
| Stålgrå | `#525A5F` | Sekundær tekst og diskrete elementer |
| Knækket hvid | `#F2F0E8` | Indholdskort og lyse paneler |
| Rustbrun | `#8B4A2B` | Links eller særlige fremhævelser |
| Hvid | `#FFFFFF` | Sidens primære baggrund |

Farverne skal bruges med god kontrast. Brødtekst må ikke placeres på en baggrund, hvor den bliver vanskelig at læse.

## Typografi

- Primær skrifttype: `Segoe UI`, med `Arial` og systemets sans-serif som reserve.
- Overskrifter skal være tydelige og bruge den mørke olivengrønne farve.
- Menutekst er som udgangspunkt 15 px og semibold.
- Menupunkter skrives normalt med almindelig brug af store og små bogstaver, ikke med tvungne versaler.
- Brødtekst skal have rolig linjeafstand og korte, læsbare afsnit.

## Sidebredde og hovedramme

| Enhed | Godkendt bredde | Resultat |
|---|---:|---|
| Desktop og laptop | 90 % | 5 % luft i hver side |
| Mobil | 100 % | Hele den tilgængelige bredde bruges |

- Headeren starter ved **0 px fra toppen**. Der må ikke indsættes Astra-luft eller anden tom topmargin over headeren.
- Header, hovedindhold og footer skal følge samme overordnede breddeprincip.
- Headeren kan gøres sticky via indstillingen i **Header / Footer**, men topplaceringen skal stadig være 0 px.
- Desktopindhold må ikke begrænses af en ekstra maksimumsbredde, der gør den synligt smallere end de valgte 90 %, medmindre det er et bevidst valg for et bestemt element.

## Afstande

De generelle standarder er:

| Afstand | Desktop | Mobil |
|---|---:|---:|
| Luft over og under hovedindhold | 32 px | 24 px |
| Luft mellem større sidesektioner | 32 px | 24 px |
| Luft før første indholdskort på Om foreningen | 24 px | 18 px |
| Luft mellem indholdskort på Om foreningen | 20 px | 14 px |
| Indvendig luft i indholdskort | 26 px | 20 px |

De generelle afstande styres under **Header / Footer → Indhold / bredde / footer**. Afstande for den enkelte redigerbare sektion styres under **Sider → Luft, baggrund og placering**.

I sideeditoren opdeles den indvendige luft i **lodret** og **vandret** luft. Dermed kan en sektion eksempelvis have 64 px over/under indholdet og 24 px i siderne uden at påvirke hele sidens 90 %-bredde.

### Hjem-sidens sektionsdesign

Den godkendte Hjem-side bruger 32 px luft før hver hovedsektion på desktop og 24 px på mobil. Hovedsektionerne har 64 px lodret og 24 px vandret indvendig luft på desktop samt 38 px lodret og 18 px vandret luft på mobil.

| Sektion | Baggrund | Desktopplacering | Mobilplacering |
|---|---|---|---|
| Om foreningen | Knækket hvid | Venstre | Midtstillet |
| Bevaring, Formidling og Fællesskab | Hvid | Venstre | Midtstillet |
| Køretøjer og materiel | Mørk olivengrøn | Venstre | Midtstillet |
| Events og Billedgalleri | Hvid | Venstre | Midtstillet |
| Bliv en del af foreningen | Sandfarvet | Venstre | Midtstillet |
| Kontakt os | Knækket hvid | Venstre | Midtstillet |

Topbanneret er 260 px højt på desktop og 180 px på mobil. Det samme bannerbillede må kun vises én gang.

## Indholdssektioner og kort

De lyse kasser på Om foreningen kaldes **indholdssektioner**. Standardudseendet er:

- én kolonne på både desktop og mobil;
- knækket hvid baggrund (`#F2F0E8`);
- 4 px sandfarvet overkant (`#C3AE83`);
- 7 px afrundede hjørner;
- overskrift og tekst venstrestilles inde i kortet.

I **Sider** kan en redaktør:

- slå **Vis på siden** fra for at skjule en sektion uden at miste teksten;
- trække sektioner for at ændre rækkefølgen;
- tilføje en ny sektion;
- vælge **Fjern permanent**, når sektionen ikke længere skal kunne genaktiveres;
- styre luft før første kort, mellem kortene og inde i kortene separat for desktop og mobil.

En rigtig gemning tager backup først. **WhatIf / simulering** bruges til at afprøve handlingen uden at gemme eller ændre siden.

## Hangar18 sideeditor

De almindelige sider **Hjem**, **Om foreningen**, **Bliv medlem** og **Kontakt** redigeres under **Hangar18 Manager → Sider**. Køretøjer, Events og Billedgalleri beholder deres specialiserede editorer.

Editoren arbejder med følgende indholdssektioner:

- Topbanner / hero
- Tekst
- Tekst og billede
- Stort billede
- Handlingsknapper
- Indholdskort
- Fremhævet tekst
- Afstand
- Importeret blok / HTML
- Side-CSS (avanceret)

Sektioner kan vises eller skjules, duplikeres, flyttes med musen og fjernes. Desktop- og mobilplacering samt luft før, efter og inde i sektionen styres separat. Indvendig luft kan styres særskilt lodret og vandret.

Indhold fra før sideeditoren indlæses automatisk som en **ikke-gemt redigerbar kladde**. Kendte Gutenberg-blokke opdeles i passende sektionstyper. Designgrupper med egne klasser bevares samlet som **Importeret blok / HTML**, så kolonner, kort og wrappers ikke skilles ad. Eksisterende sidespecifikke regler bevares som **Side-CSS (avanceret)** og må ikke vises som tekst på siden. Den offentlige side ændres først, når redaktøren aktivt vælger **Gem siden**. Før gemningen oprettes en fuld backup og en WordPress-revision.

Header og footer ligger uden for sideeditoren og kan ikke slettes fra en almindelig side.

## Funktionsmoduler

Funktionsmoduler er dynamiske sektioner, der udfører en handling og samtidig følger designmanualens farver, bredde og mobilregler.

### Mailformular

- Standardfelter er navn, e-mail, emne og besked.
- Modtageradressen gemmes i WordPress og må aldrig sendes som et skjult felt til besøgeren.
- Formularen bruger nonce-kontrol, skjult spamfelt og hastighedsbegrænsning.
- Henvendelser gemmes kun i WordPress, når redaktøren aktivt vælger det.
- Gemte henvendelser begrænses til de seneste 200 pr. formular og kan eksporteres som semikolonsepareret CSV.
- SMTP-adgangsoplysninger må aldrig lægges i kildekoden eller GitHub.

### Afstemning

- Afstemningen kan have 2–20 unikke svarmuligheder.
- Redaktøren vælger enkelt eller flere svar, tidsrum og hvornår resultatet vises.
- Dobbeltstemmer begrænses med browsercookie og en saltet envejs-hash; rå IP-adresser gemmes ikke.
- Resultater kan nulstilles fra editoren og eksporteres som semikolonsepareret CSV.
- En offentlig anonym afstemning kan begrænse almindelig dobbeltstemning, men er ikke en juridisk identitetskontrol.

## Placering på desktop og mobil

Placering skal kunne vælges separat, fordi et layout, der fungerer på en bred skærm, ikke altid fungerer på en telefon.

| Indholdstype | Desktop-standard | Mobil-standard | Ændres under |
|---|---|---|---|
| Køretøjsoversigt | Venstre | Midtstillet | Køretøjer |
| Køretøjsdetaljer | Venstre | Midtstillet | Køretøjer |
| Eventsoversigt | Venstre | Midtstillet | Events |
| Eventdetaljer | Venstre | Midtstillet | Events |
| Billedgallerioversigt | Venstre | Midtstillet | Billedgalleri |
| Albumsider | Venstre | Midtstillet | Billedgalleri |

Tekniske tabeller og længere tekstblokke kan fortsat være venstrestillede inde i en ellers midterstillet mobilside, hvis det giver bedre læsbarhed.

## Billeder

- Billeder skal være responsive og må ikke løbe uden for deres kort eller sektion.
- Oversigtskort bruger som udgangspunkt billedformatet 16:10.
- Billeder i albumvisning bruger som udgangspunkt 4:3.
- Kortbilleder beskæres med `object-fit: cover`, så kortene står ens.
- Meningsbærende billeder skal have en beskrivende alternativ tekst i WordPress' mediebibliotek.

## Mobilprincipper

- Mobilbreakpointet er 782 px.
- Indstillinger og indholdskort vises i én kolonne, når flere kolonner bliver for smalle.
- Klikbare knapper og links skal have tilstrækkelig størrelse og afstand.
- Vandret rulning på hele siden skal undgås.
- Mobilvisningen skal kontrolleres efter ændringer af bredde, luft, billeder eller rækkefølge.

## Web-managerens administrationsdesign

- Relaterede indstillinger samles i tydelige kort.
- Desktop- og mobilvalg står i hver sin navngivne gruppe.
- Hver vigtig knap forklarer både, hvad den gør, og hvornår den bør bruges.
- Primære knapper gemmer eller anvender redaktørens ændringer.
- Sekundære knapper bruges til genbygning, synkronisering eller reparation.
- Reparationsknapper bruges kun, når en oversigt eller side står forkert eller mangler indhold.
- WhatIf er frivillig simulering og er som udgangspunkt slået fra.

## Tilgængelighed og kvalitetstjek

Før en designændring godkendes, kontrolleres:

1. Headeren starter ved 0 px på både desktop og mobil.
2. Desktopbredden er 90 %, med cirka 5 % luft i hver side.
3. Mobilversionen bruger bredden korrekt uden vandret rulning.
4. Tekst og knapper har tydelig kontrast.
5. Fokus, links og knapper kan genkendes og betjenes.
6. Billeder har passende beskæring og alternativ tekst.
7. Luft før, mellem og inde i sektioner ser ensartet ud.
8. Header, indhold og footer overlapper ikke hinanden.

## Ændringshistorik

| Version | Godkendt ændring |
|---|---|
| 0.4.10 | Sidebredden blev rettet, og headerens udvendige topafstand blev fjernet. |
| 0.4.11 | Sektionsafstand blev gjort justerbar, og gamle Astra-sideskabeloner blev ryddet op. |
| 0.4.12 | Headerens topplacering blev fastholdt ved 0 px, også for indloggede brugere. |
| 0.4.13 | Luft over og under hovedindholdet blev gjort justerbar. |
| 0.4.14 | Events og billedgalleri fik særskilt mobilplacering. |
| 0.4.15 | Køretøjer fik særskilt mobilplacering, og ældre PowerShell-/baselineflow blev ryddet op. |
| 0.4.16 | Administrationslayout og knapforklaringer blev gjort ensartede. |
| 0.4.17 | Sideindhold, indholdssektioner og deres afstande blev gjort redigerbare; designmanualen blev oprettet. |
| 0.4.18 | Sideindhold blev udvidet til en samlet sideeditor med genbrugelige sektioner, mailformular, afstemning og responsive editorvisninger. |
| 0.4.19 | Nuværende Gutenberg- og HTML-sideindhold blev gjort direkte redigerbart gennem sikker konvertering til sektionskladder. |
| 0.4.20 | Importeret CSS, Gutenberg-grupper, kolonner og eksisterende sektionsafstande blev bevaret og repareret. |
| 0.4.21 | Forsidens hero blev sikret mod et gentaget Cover-billede, ældre CSS-tekstsektioner blev genkendt som side-CSS, og sektionernes valgte desktop-/mobilplacering blev gjort autoritativ. |
| 0.4.22 | Backupoversigten fik sikker oprettelse af en separat Hjem-sammenligningskladde fra den oprindelige JSON-backup uden ændring af aktiv forside eller menu. |
| 0.4.23 | Hjem-sidens sektionsfarver, 32/24 px sektionsafstand, lodrette/vandrette indvendige luft, oprindelige runde knapper og 180 px mobilbanner blev gendannet i den nye editor. |

## Sådan opdateres manualen

Når et nyt designvalg godkendes:

1. Opdatér den relevante indstilling i Hangar18 Manager.
2. Kontrollér resultatet på desktop og mobil.
3. Ret den relevante regel eller tabel i denne fil.
4. Tilføj ændringen til versionsrækken ovenfor.
5. Udgiv kode, updaterpakke og manual i samme GitHub-version.
