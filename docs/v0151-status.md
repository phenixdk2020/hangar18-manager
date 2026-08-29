# Visual Designer Manager 0.1.51 – status

## Scope
- CONV-02 ekstern sidekonvertering.
- Første autoritative kilde: `https://test2.hangar18.dk/` for Hjem.
- Eksisterende lokal konvertering fra 0.1.50 bevares.
- AKVPK theme slug-migration timing repareres.

## Kontrakter
1. Ekstern kilde er read-only og skal være offentlig HTTPS.
2. Import opretter kun en QA-kandidat; frontend ændres først ved eksplicit Godkend og aktivér.
3. Lokal `post_content` overskrives aldrig af konverteringen.
4. Scripts/styles fra ekstern side køres/importeres ikke. Relative links og billed-URL'er absolutgøres mod kilden.
5. Ved godkendelse hentes kilden igen og source hash skal fortsat matche kandidaten.
6. En ekstern URL kan målrettes en eksisterende side eller oprette en ny WordPress-kladde.
7. Header/Footer-preview bruger fortsat de aktive canonical templates.

## Begrænsning
0.1.51 kopierer ikke eksterne billeder ind i målsiteets mediebibliotek. Kandidaten markerer dette som QA-warning. Første pass er fortsat HTML-bevarende og er ikke en automatisk semantisk opsplitning i alle Visual Designer-elementtyper.
