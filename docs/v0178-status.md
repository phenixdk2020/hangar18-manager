# Visual Designer Manager v0.1.78 – Hybrid modulsider + Eventfelter

**Dato:** 1. september 2026  
**Status:** Release candidate; central ZIP/manifest-build kræves efter grøn QA.

## Scope
- Events, Billedgalleri og Køretøjer kan nu have almindelige Visual Designer-elementer i flow-slots **før / mellem / efter** det dynamiske modulindhold.
- Den dynamiske CollectionPageRenderer bevares, så søgning, sortering, eventarkiv og naturlig indholdshøjde ikke erstattes af faste grid-kort.
- Moduldesign fra v0.1.77 bevares i en separat **Moduldesign**-tilstand; standardtilstanden på de tre sider er almindelig indholdsredigering.
- Detailvisninger får publicerede, genbrugelige Designer-skabelonsider: Eventdetalje, Albumdetalje og Køretøjsdetalje.
- Eventfelter er fleksible og centrale med stabile felt-IDer, type, aktiv/påkrævet, kort/detalje-visning og rækkefølge.
- Standard Eventfelter: **Om arrangementet**, **Program**, **Praktiske oplysninger**.
- Nyt Designer-element **Eventfelt** kan placere et bestemt fleksibelt Eventfelt på Eventdetalje-skabelonen.
- Eksisterende modulrecords ændres ikke; tidligere layout gemmes i v0.1.78-backup-meta før slot-migration.
