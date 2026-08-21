# I9 — migration/rollback rehearsal

**Status:** Forberedelse komplet / rehearsal evidence pending  
**Dato:** 21. august 2026

Denne runbook dokumenterer den obligatoriske rollback-test før I9 kan markeres PASS og før I10 public conversion må begynde.

---

## 1. Formål

Rollback-testen skal bevise, at en kontrolleret Ultimate Designer-konvertering kan rulles tilbage uden at miste den tidligere public state eller kritiske Hangar18-data.

Testen skal gennemføres på en staging/live-kopi, ikke direkte på produktion som første forsøg.

---

## 2. Scope

Brug én ikke-kritisk comparison-side.

Må ikke bruges som første rollback-test:

- Vehicle;
- Event;
- Gallery;
- en side med ukendt backupstatus;
- en side hvor baseline ikke er dokumenteret.

---

## 3. Før mutation

- [ ] Notér Git commit SHA.
- [ ] Notér pluginversion.
- [ ] Notér side-ID, slug og public URL.
- [ ] Gem screenshot af public Desktop/Tablet/Mobil.
- [ ] Gem relevant side-/versionidentitet.
- [ ] Opret/verify applikationsbackup.
- [ ] Verificér backupens immutable ID/manifest hvor tilgængeligt.
- [ ] Verificér at restore-pointet kan findes igen.
- [ ] Notér Vehicle/Event/Gallery baseline som protected-domain sanity.

Stop hvis backup ikke kan verificeres.

---

## 4. Kontrolleret testændring

På comparison-siden laves en tydelig men reversibel ændring:

1. tilføj eller flyt et almindeligt element;
2. opret side-by-side layout;
3. resize Desktop til en tydelig asymmetrisk span;
4. opret Tablet-override;
5. ændr én synlig designværdi;
6. gem som ny version med en entydig testnote.

Eksempel på ændringsnote:

`I9 rollback rehearsal — temporary candidate state`

Dokumentér den ændrede state med screenshots.

---

## 5. Verificér kandidatstate

Før rollback:

- [ ] public/preview-state svarer til den planlagte kandidatstate;
- [ ] editor reload bevarer placement/span/override;
- [ ] versionhistorikken viser testversionen;
- [ ] ingen protected-domain data er ændret;
- [ ] ingen kritisk fejl er opstået.

---

## 6. Udfør rollback

Brug det officielle restore/versionflow. Undgå direkte databasehåndtering medmindre selve disaster-recovery-laget eksplicit testes.

Rollback skal:

- vælge den identificerede pre-change state;
- oprette den forventede safety backup før mutation, hvis restoreflowet kræver det;
- gendanne sideindhold/state;
- bevare audit/revision-historik frem for at slette spor.

Registrér præcis hvilken restore-/versionshandling der blev brugt.

---

## 7. Verificér efter rollback

### Side

- [ ] public output matcher baseline visuelt;
- [ ] tekst/links er tilbage til baseline;
- [ ] billeder og media references er intakte;
- [ ] hierarchy/order er baseline;
- [ ] spans og responsive overrides er baseline;
- [ ] ingen testdesignværdi hænger tilbage.

### Editor

- [ ] siden kan åbnes igen;
- [ ] editorstate svarer til restored state;
- [ ] versionhistorikken er konsistent;
- [ ] restorehandlingen kan identificeres i audit/revision.

### Protected domains

- [ ] Vehicle sanity PASS;
- [ ] Event sanity PASS;
- [ ] Gallery sanity PASS.

---

## 8. Genåbn kandidatstate hvis relevant

Hvis restoremodellen understøtter det sikkert, kan den midlertidige kandidatversion inspiceres eller gendannes igen som ekstra bevis for revisionernes reversibilitet.

Dette er sekundært; primært I9-kriterium er, at rollback til den dokumenterede baseline virker pålideligt.

---

## 9. Evidence der skal gemmes

Minimum:

- buildidentitet;
- baseline screenshot(s);
- kandidat screenshot(s);
- restored screenshot(s);
- backup-/restore-point-ID;
- side/version-ID før og efter;
- tidslinje for ændring og rollback;
- PASS/FAIL-checklist;
- eventuelle server-/browserfejl.

---

## 10. Failure-regler

Rollback er `FAIL`, hvis én af følgende sker:

- baseline kan ikke gendannes;
- media/data references går tabt;
- den restored public side afviger væsentligt fra baseline;
- editoren kan ikke åbne restored state;
- version/audit-state korrumperes;
- Vehicle/Event/Gallery påvirkes af comparison-side rollback;
- recovery kræver improviseret manuel databaseændring uden for det godkendte flow.

Et FAIL blokerer I10.

---

## 11. I10 gate

Når browser-, screen-reader-, test2-, protected-domain- og rollback-evidence alle er PASS, kan I9 markeres PASS.

Først derefter må I10 begynde i den fastlagte rækkefølge:

1. comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery kun efter særskilt compatibility proof;
7. legacy removal til sidst.
