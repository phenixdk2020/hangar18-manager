# I9 — manual QA evidence runbook

**Status:** Forberedelse komplet / faktisk evidence pending  
**Gælder:** Ultimate Designer gennem LEGO-033  
**Dato:** 21. august 2026

Formålet med denne runbook er at gøre I9 reproducerbar. I9 må først markeres PASS, når de manuelle/live beviser er gennemført og gemt. Automatiseret CI er støttebevis, ikke erstatning.

---

## 1. Evidence-pakke

Opret én evidence-pakke pr. kandidat-build med følgende struktur:

```text
I9-EVIDENCE-YYYYMMDD-HHMM/
├── 00-build-identitet.md
├── 01-chrome/
├── 02-edge/
├── 03-firefox/
├── 04-safari/
├── 05-screen-reader/
├── 06-test2-live-e2e/
├── 07-protected-domains/
└── 08-rollback/
```

`00-build-identitet.md` skal mindst indeholde:

- Git commit SHA;
- pluginversion;
- testdato/tid;
- tester;
- WordPress-version;
- PHP-version;
- browser-/OS-versioner;
- test2 URL/kopi-identitet;
- link til relevante GitHub Actions-runs.

---

## 2. Fælles testside

Brug en ikke-kritisk comparison/testside med mindst:

- Tekst;
- Billede;
- Kasse med barn;
- to almindelige elementer side-by-side;
- Auto-kasser 6/6;
- Desktop-resize til en asymmetrisk fordeling, fx 7/5;
- Tablet-override, fx 8/4;
- Mobil med Desktop-arv;
- mindst én knap/link med Hover og Focus;
- mindst ét billede med alt-tekst.

Siden må ikke være Vehicle/Event/Gallery.

---

## 3. Browser acceptance — fælles flow

Kør samme flow i Chrome, Edge, Firefox og Safari.

### A. Load og canvas

- [ ] Editor åbner uden fatal fejl.
- [ ] Elementpalette, canvas og Inspector vises.
- [ ] Eksisterende elementer er synlige og i korrekt rækkefølge.
- [ ] Direkte Design og Billede-paneler kan foldes ind/ud.
- [ ] Foldning opretter ikke Undo/Redo-history.

### B. Placement

- [ ] Træk et almindeligt element.
- [ ] Over/Under/Venstre/Højre-zoner vises tydeligt.
- [ ] Over/Under flytter elementet korrekt.
- [ ] Venstre/Højre opretter/genbruger Auto-kasser korrekt.
- [ ] Ét side-drop kan fortrydes med ét Undo.
- [ ] Redo gendanner side-drop i ét trin.

### C. Resize

- [ ] To side-by-side-elementer starter med korrekt span.
- [ ] Resize-håndtag kan rammes med musen.
- [ ] Træk 6/6 → 8/4 eller tilsvarende.
- [ ] Naboen kompenserer, så totalen forbliver 12.
- [ ] Ingen span bliver mindre end 1.
- [ ] Ét resize pointerforløb giver ét Undo-trin.
- [ ] Undo/Redo gendanner begge spans samlet.

### D. Responsive span

- [ ] Tablet arver Desktop initialt.
- [ ] Mobil arver Desktop initialt.
- [ ] Tablet-resize ændrer kun Tablet.
- [ ] Desktop forbliver uændret efter Tablet-resize.
- [ ] Mobil forbliver uændret efter Tablet-resize.
- [ ] `Arv Desktop` viser Desktop-span igen.
- [ ] Deaktivering af `Arv Desktop` gendanner det tidligere override-snapshot.

### E. Design og interaction

- [ ] Direkte Design og Inspector viser samme state.
- [ ] Farve/radius/spacing ændres korrekt.
- [ ] Tablet/Mobil designoverride arver korrekt.
- [ ] Hover kan observeres.
- [ ] Focus er tydeligt med keyboard.
- [ ] Disabled-state er visuelt genkendelig, hvor relevant.

### F. Save/reload

- [ ] Gem en permanent version med ændringsnote.
- [ ] Reload editor.
- [ ] Placering/hierarki er bevaret.
- [ ] Desktop-span er bevaret.
- [ ] Tablet/Mobil-arv og overrides er bevaret.
- [ ] Indhold/design er bevaret.

---

## 4. Evidence pr. browser

Gem mindst:

- screenshot af editor efter load;
- screenshot af side-by-side 6/6 eller 7/5;
- screenshot af Tablet override;
- kort notat med PASS/FAIL pr. testblok A–F;
- browser- og OS-version;
- eventuelle fejl med reproduktionstrin.

Navngiv fx:

```text
chrome-01-editor-load.png
chrome-02-desktop-7-5.png
chrome-03-tablet-8-4.png
chrome-results.md
```

---

## 5. Screen-reader core flow

Kør minimum én reel screen-reader-session på den kandidat, der ellers er browsergrøn.

Kontrollér:

- [ ] side-/editorlandmarks kan navigeres;
- [ ] knapper annonceres som knapper;
- [ ] foldbare paneler annoncerer expanded/collapsed;
- [ ] form controls har forståelige labels;
- [ ] focus-rækkefølge er logisk;
- [ ] focus er visuelt synligt samtidig;
- [ ] billeder med betydning har alt-tekst;
- [ ] status/fejl er forståelige uden kun farve;
- [ ] ingen kritisk funktion kræver mus alene.

Gem screen-reader-navn/version samt kort resultatlog.

---

## 6. Protected-domain regression

Vehicle, Event og Gallery skal kontrolleres separat, fordi de fortsat er legacy/public-beskyttede.

For hver af de tre domæner:

- [ ] oversigt loader;
- [ ] detaljeside loader;
- [ ] billeder vises;
- [ ] desktopplacering matcher nuværende accepterede output;
- [ ] mobilplacering matcher nuværende accepterede output;
- [ ] datafelter er intakte;
- [ ] specialeditoren fungerer;
- [ ] Ultimate Designer har ikke konverteret data/output implicit.

Der skal være mindst før/efter-screenshots eller side-by-side dokumentation fra kandidatkopien.

---

## 7. Resultatklassifikation

Brug kun disse resultater:

- `PASS` — kriteriet er demonstreret.
- `FAIL` — reproducerbar afvigelse.
- `BLOCKED` — miljø/adgang forhindrer testen.
- `N/A` — kun hvis kriteriet reelt ikke gælder; begrundelse kræves.

I9 samlet status:

```text
PASS kun hvis:
Chrome PASS
AND Edge PASS
AND Firefox PASS
AND Safari PASS
AND screen-reader PASS
AND test2 live E2E PASS
AND Vehicle/Event/Gallery PASS
AND rollback PASS
```

Ingen gennemsnitsscore kan kompensere for en FAIL i en obligatorisk gate.
