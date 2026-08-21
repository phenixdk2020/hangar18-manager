# I9 — test2 live E2E checklist

**Status:** Forberedelse komplet / live evidence pending  
**Miljø:** `test2.hangar18.dk`  
**Dato:** 21. august 2026

Denne checklist bruges til den obligatoriske live-/stagingtest på test2. Den er bevidst adskilt fra browser-unit/E2E i GitHub Actions, fordi I9 kræver bevis fra et rigtigt WordPress-miljø med tema, plugins, data, routing og rendering samlet.

---

## 1. Preflight

- [ ] Bekræft kandidatens Git commit SHA.
- [ ] Bekræft pluginfilens versionsheader.
- [ ] Tag/verify fuld applikationsbackup før mutation.
- [ ] Bekræft at test2 er staging/kopi og ikke produktion.
- [ ] Notér aktivt tema og WordPress/PHP-version.
- [ ] Bekræft at Vehicle/Event/Gallery er tilgængelige før testen.
- [ ] Vælg eller opret en ikke-kritisk comparison-side.

Stop testen ved manglende backup eller hvis miljøidentiteten er uklar.

---

## 2. Baseline før editorændringer

Gem screenshots og URL'er for:

- [ ] comparison-siden;
- [ ] Hjem;
- [ ] Om foreningen;
- [ ] Kontakt;
- [ ] Bliv medlem;
- [ ] Køretøjer oversigt + én detalje;
- [ ] Events oversigt + én detalje;
- [ ] Billedgalleri oversigt + ét album.

Notér eventuelle allerede eksisterende afvigelser, så de ikke fejlagtigt tilskrives kandidaten.

---

## 3. Comparison-side — editorflow

På den valgte comparison-side:

1. Åbn Hangar18 Manager → Sider.
2. Tilføj Tekst og Billede.
3. Placér Billede **Højre** for Tekst.
4. Verificér Auto-kasser/side-by-side.
5. Resize Desktop til fx 7/5.
6. Skift Tablet og resize til fx 8/4.
7. Kontrollér Mobil med Desktop-arv.
8. Aktivér/deaktivér `Arv Desktop` på Tablet.
9. Lav én designændring.
10. Test Undo/Redo på placement og resize.
11. Gem som ny version med ændringsnote.
12. Reload editor og verificér persistence.

Evidence:

- [ ] screenshot af Desktop;
- [ ] screenshot af Tablet;
- [ ] screenshot af Mobil;
- [ ] note om Undo/Redo-resultat;
- [ ] note om save/reload-resultat.

---

## 4. Preview/Working-state

- [ ] Preview viser den aktuelle Working state.
- [ ] Preview indeholder ikke editor chrome.
- [ ] Ikke-gemte ændringer håndteres som forventet.
- [ ] Permanent save skaber den forventede version/revision.
- [ ] Public legacy side ændres ikke blot ved editorpreview.

---

## 5. Responsive visuel kontrol

På comparison-siden kontrolleres mindst:

### Desktop

- [ ] ca. 90 % sidebredde hvor designmanualen kræver det;
- [ ] header starter ved 0 px;
- [ ] ingen utilsigtet horisontal overflow;
- [ ] side-by-side spans matcher editoren;
- [ ] billeder er responsive.

### Tablet

- [ ] eksplicit Tablet-span vises korrekt;
- [ ] design/spacing overrides anvendes korrekt;
- [ ] ingen overlap eller klippet indhold.

### Mobil

- [ ] korrekt mobilbredde;
- [ ] ingen vandret scroll på hele siden;
- [ ] knapper/links kan betjenes;
- [ ] billeder holder sig inden for containeren;
- [ ] arvede/overstyrede værdier matcher editorstate.

---

## 6. Formular-/interaction sanity

Hvis comparison- eller Kontakt-siden indeholder en formular:

- [ ] labels er synlige/forståelige;
- [ ] validering fungerer;
- [ ] keyboard focus er synligt;
- [ ] submit giver forståelig status;
- [ ] modtageradresse eksponeres ikke som klientstyret hidden input;
- [ ] testindsendelse påvirker kun testmiljøet.

Interaktive elementer:

- [ ] Hover fungerer med mus;
- [ ] Focus fungerer med keyboard;
- [ ] Active-state skaber ikke layout-hop;
- [ ] Disabled-state er genkendelig.

---

## 7. Protected domains efter ændringer

Efter comparison-sidearbejdet genkontrolleres:

### Vehicle

- [ ] oversigt uændret funktionelt;
- [ ] detalje uændret funktionelt;
- [ ] billeder/data intakte;
- [ ] specialeditor intakt.

### Event

- [ ] Upcoming/Tidligere klassifikation fungerer;
- [ ] oversigt/detalje loader;
- [ ] billeder/data intakte;
- [ ] specialeditor intakt.

### Gallery

- [ ] oversigt loader;
- [ ] album loader;
- [ ] billeder og responsive layout intakte;
- [ ] specialeditor intakt.

Sammenlign med baseline-screenshots fra før testen.

---

## 8. Save/version/restore sanity

- [ ] en permanent save kan identificeres i versionhistorikken;
- [ ] ændringsnoten er bevaret;
- [ ] tidligere version kan inspiceres;
- [ ] restore-flowet kræver den forventede sikkerhedskontekst;
- [ ] restore skaber/efterlader audit/revision efter gældende arkitektur.

Den fulde rollback-rehearsal følger `i9-rollback-rehearsal.md`.

---

## 9. PASS-kriterium

`test2 live E2E = PASS` kræver:

- editorplacement PASS;
- Desktop resize PASS;
- Tablet/Mobil responsive spans PASS;
- Undo/Redo PASS;
- save/reload PASS;
- preview/Working state PASS;
- responsive visuel kontrol PASS;
- relevante interactions PASS;
- Vehicle/Event/Gallery regression PASS;
- ingen ny kritisk konsol-/PHP-fejl observeret under flowet.

Alle afvigelser registreres med URL, tidspunkt, browser, screenshot og reproduktionstrin.
