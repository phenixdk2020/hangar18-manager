# Hangar18 Manager — canonical backlog delta v0.8.87

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.86 installeret og manuelt testet  
**Extends:** `docs/active-backlog-v0886.md`

Denne delta registrerer den manuelle v0.8.86-test af Række- og kolonne-kasse med Tekst + Billede. Stack-pariteten er tydeligt forbedret, men Billede-elementets interne sizing er endnu ikke 1:1 mellem canvas og frontend-preview. Derudover er den tidligere backlog for direkte lodret element-resize nu konkretiseret til både almindelige elementer og Række-/kolonne-kasser.

## Manuel evidens fra v0.8.86

- **FORBEDRET:** Frontend-forhåndsvisning viser ikke længere den tidligere ekstreme 1/12-billedstribe; stack/kolonne-geometrien er markant tættere på editoren.
- **FAIL:** Når Billede-elementets kolonne ændres mellem fx 8/12 og 4/12, kan billedet blive beskåret i canvas. Udsnittet ændrer sig med elementets bredde.
- **FAIL:** I frontend-forhåndsvisningen kan samme billede blive højere/længere end det vises inde i Billede-elementet i canvas.
- **Årsag:** Pure `image` bruger fortsat `ImageFit=Cover` som normaliseret standard, og v0.8.86 begrænser kun `max-width:100%`. Den fælles regel for Auto/original-aspect mangler: billedet skal holde sig inden for elementets bredde/højde uden Cover-beskæring.
- **FAIL:** Række- og kolonne-kassen har ikke et selvstændigt bund-håndtag til at gøre selve elementet højere/lavere.

# I. Billede-element sizing

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| IMAGE-FIT-PARITY-100 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.87 | Et rent Billede-element med `Format = Auto / original` skal skaleres proportionalt inde i sin aktuelle elementkasse. Canvas og frontend-preview skal bruge samme geometri. `Cover` må ikke beskære Auto/original-billedet; runtime bruger `contain`. Ved fast valgt aspect-ratio beholdes det eksplicit valgte `ImageFit`. `figure` og `img` må aldrig blive bredere end elementet. |

# R. Direkte højde-resize

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| VERTICAL-ELEMENT-RESIZE-099 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.87 | Det valgte element får ét bund-håndtag med ↕. For Billede ændrer håndtaget `ImageHeightPx` / `MobileImageHeightPx`, og Auto/original bruger `contain`, så billedet kan gøres både lavere og højere uden crop. For Tekst/Kasse/Grid/Flex/Række- og kolonne-kasse ændres `ElementMinHeightPx` / responsive overrides. Trækkes tilbage til naturlig indholdshøjde, nulstilles værdien til Auto (`0`) i stedet for at klippe indhold. Funktionen må ikke ændre horisontal span eller StackRootKey. |

# L. Stack / frontend parity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| FRONTEND-STACK-096 | Kritisk | 🟠 FORBEDRET / FORTSAT MANUEL TEST v0.8.87 | v0.8.86 fjernede den ekstreme stack-span-fejl. Endelig PASS kræver nu, at Billede-elementets størrelse også er 1:1 med canvas efter 4/12↔8/12-resize og i live-preview. |
| CANVAS-STACK-AUTOHEIGHT-097 | Høj | 🟠 FORBEDRET / FORTSAT MANUEL TEST v0.8.87 | Naturlig stack-højde er indført, men endelig PASS kræver at pure Image ikke visuelt afviger pga. Cover/fixed-height-adfærd. |

# S. Save / reload diagnostics

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| SAVE-RELOAD-HIERARCHY-098 | Kritisk | 🔴 ÅBEN / LOG-DIAGNOSE | Uændret: Gem/genindlæsning med Række- og kolonne-kasse → 2×Tekst + 1×Billede skal fortsat testes separat med trace/log. |

# Manuel v0.8.87 testmatrix

1. Opret Række- og kolonne-kasse med venstre Tekst og højre Tekst + Billede under højre Tekst.
2. Sæt 4/12 + 8/12. Med Billede på `Auto / original` skal hele motivet være synligt uden beskæring.
3. Træk fordelingen til 8/12 + 4/12. Billedet skal blive smallere og proportionalt lavere/tilpasset uden at ændre udsnit via Cover-crop.
4. Vælg Billede og brug det nye bund-håndtag ↕. Træk både ned og op. Hele billedet skal fortsat være synligt og følge elementhøjden.
5. Vælg selve Række- og kolonne-kassen og træk bund-håndtaget ned. Kassen skal blive højere. Træk op igen; ved naturlig indholdshøjde skal den gå tilbage til Auto frem for at klippe børnene.
6. Tryk **Forhåndsvis side** uden at gemme. Billedets bredde/højde og udsnit skal matche Billede-elementet i canvas væsentligt tættere end v0.8.86.
7. Gentag punkt 2–6 med 6/12 + 6/12.
8. Regression: højre/venstre/over/under placement og Billede-insert må ikke fryse.
9. Regression: Inspector-rækkefølgen skal være uændret.
10. Gem/reload holdes fortsat separat under `SAVE-RELOAD-HIERARCHY-098`.
