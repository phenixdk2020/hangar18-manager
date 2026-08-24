# Hangar18 Manager — canonical backlog delta v0.8.86

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.85 installeret og manuelt testet  
**Extends:** `docs/active-backlog-v0885.md`

Denne delta registrerer den resterende stack-fidelity-fejl fundet under manuel v0.8.85-test. Horisontal placement og image-freeze er nu manuelt accepteret, og Inspector-rækkefølgen er accepteret. Den tilbageværende preview-fejl skyldes, at frontend v0.8.85 tæller lodrette stack-medlemmer som selvstændige 12-kolonne-børn.

## Manuel evidens fra v0.8.85

- **PASS:** Tekst → Billede ved siden af hinanden fryser ikke editoren.
- **PASS:** højre/venstre/over/under placement fungerer igen.
- **PASS:** Inspector-halen er Billede/Mediebibliotek → Layout-hierarki → Dynamic data binding → Conditions / synlighed.
- **FAIL:** ved 4/12 venstre Tekst + 8/12 højre Tekst med Billede stablet under højre Tekst viser live-preview Billede som cirka 1/12 bredt.
- **Årsag:** stack-medlemmet har samme `LayoutParentKey` som stack-roden. v0.8.85 frontend-span-runtime løser derfor tre direkte børn mod et 12-kolonne-budget i stedet for to logiske kolonner.
- **FAIL:** når en lodret stack ikke er manuelt højderesizet, kan v0.8.51-rendereren stadig tvinge segmenterne til en ligelig procentfordeling. Et stort billede kan derfor visuelt vokse uden for den røde elementramme i canvas.

# L. Stack / frontend parity

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| FRONTEND-STACK-096 | Kritisk | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.86 | Grid-børn med `StackRootKey` må ikke optage et ekstra horisontalt span. Frontend og live-preview skal gruppere stack-rod + medlemmer som ét 12-kolonne-grid-item med rodens effektive Desktop/Tablet/Mobile-span. Eksempel: 4/12 + 8/12 hvor Billede ligger under højre Tekst skal renderes som **4/12 + én 8/12 stack**, ikke 4/12 + 7/12 + 1/12. Eventuelle eksplicit gemte lodrette procentfordelinger skal fortsat kunne afspejles. |
| CANVAS-STACK-AUTOHEIGHT-097 | Høj | 🟡 FIX-KANDIDAT / MANUEL TEST v0.8.86 | En lodret stack uden eksplicit ↕-resize skal bruge naturlig indholdshøjde. Et Billede må ikke flyde uden for elementets valgte/markerede ramme, fordi stacken automatisk tvinges til 50/50. Når brugeren senere anvender ↕-resize, må de eksplicitte procenter fortsat eje højdefordelingen. |

# S. Save / reload diagnostics

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| SAVE-RELOAD-HIERARCHY-098 | Kritisk | 🔴 ÅBEN / LOG-DIAGNOSE | Reproducer Gem/genindlæsning med Række- og kolonne-kasse → 2×Tekst + 1×Billede og log `Key`, `Type`, `LayoutParentKey`, Order, span og stack-state før submit, i POST/backend-normalisering og efter reload. Ret først når det er dokumenteret, om relationen går tabt i save-payload, normalisering eller visuel reconstruction. Indtil da skal brugeren ikke bruge denne testcase som release-gate for v0.8.86. |

# R. Direkte højde-resize

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| VERTICAL-ELEMENT-RESIZE-099 | Normal | 🔵 BACKLOG | Et enkelt element i en række skal senere kunne trækkes større/mindre lodret via et bund-håndtag. Desktop skriver `ElementMinHeightPx`; Tablet/Mobil bruger de eksisterende responsive min-height overrides. Funktionen skal være separat fra stack ↕-fordeling og må ikke ændre horisontal span/placement. |

# Manuel v0.8.86 testmatrix

1. Opret Række- og kolonne-kasse med venstre Tekst og højre Tekst; sæt 4/12 + 8/12.
2. Læg Billede **under** højre Tekst. Bekræft at editoren fortsat viser venstre 4/12 og højre stack 8/12.
3. Uden at bruge ↕-højderesize: Billede-elementets ramme skal vokse naturligt med billedet; billedet må ikke flyde uden for elementrammen.
4. Tryk **Forhåndsvis side uden at gemme**. Preview skal vise 4/12 + én 8/12 stack med Tekst over Billede; Billede må ikke blive en 1/12-stribe.
5. Gentag med 6/12 + 6/12 og 8/12 + 4/12.
6. Regression: Tekst → Billede side-by-side må ikke fryse.
7. Regression: højre/venstre/over/under placement skal fortsat virke.
8. Regression: Inspector-halen og collapse-adfærd skal være uændret.
9. **Gem/reload testes separat med trace/log under `SAVE-RELOAD-HIERARCHY-098`; den er ikke en v0.8.86 accept-gate.**
