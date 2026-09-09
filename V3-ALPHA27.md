# V3 3.0.0-alpha.27 — Responsive Paint Unification

## Mål
Desktop, laptop, tablet og mobil skal bruge de samme kanoniske farver, baggrunde, kanter, kasser og tekster. Responsive regler må ændre geometri og typografi, men må ikke have et separat paint-lag.

## Ændringer
- Fjerner mobile-only `v1PaintCss` fra side, Header og Footer.
- Canonical Designer-model vinder altid over retained legacy paint; legacy bruges kun som fallback til template-surface, hvis modellen mangler farve.
- Engangs `ResponsivePaintUnifier` retter den eksisterende V1-konverterede Hjem-side i selve modellen:
  - hero-sektionens eksponerede separator: `#30382a`
  - tagline-sektion: `#c3ae83`
  - tagline-tekst: transparent baggrund over sandsektionen og `#30382a` tekst
- Ingen geometri, hierarki, rækkefølge eller tekstindhold ændres af paint-migreringen.
- Fremtidige V1-konverteringer opretter hero-sektionen med oliven baggrund direkte i modellen.
- Alpha.26 Header/Footer parity og Website-menu-baserede Footer-genveje bevares.

## Acceptance
På samme side skal desktop og mobil vise samme semantiske paint:
1. Hero-billedets eksponerede stribe er mørkegrøn.
2. Tagline-kassen er sand/lysebrun med mørkegrøn tekst.
3. Header/Footer bruger de samme gemte model-farver på alle breakpoints.
4. En farveændring i Designer må ikke kræve en separat mobilfarve.
5. V1 0.1.93 baseline forbliver byte-identisk.
