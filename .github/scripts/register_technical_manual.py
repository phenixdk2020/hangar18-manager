from pathlib import Path

handover_path = Path('docs/CLEAN-HANDOVER.md')
design_path = Path('CLEAN-DESIGN-MANUAL.md')
user_path = Path('CLEAN-USER-MANUAL.md')

handover = handover_path.read_text(encoding='utf-8')
old = '''1. `docs/CLEAN-HANDOVER.md` – denne fil; aktuel status, aftaler, næste opgave og ikke-forhandlingsbare regler.
2. `CLEAN-DESIGN-MANUAL.md` – autoritativ design- og arkitekturmålmodel.
3. `docs/clean-backlog-v0120.md` – operativ backlog.'''
new = '''1. `docs/CLEAN-HANDOVER.md` – denne fil; aktuel status, aftaler, næste opgave og ikke-forhandlingsbare regler.
2. `CLEAN-DESIGN-MANUAL.md` – autoritativ design- og arkitekturmålmodel.
3. `CLEAN-TECHNICAL-MANUAL.md` – autoritativ reference for konkrete UX-kontrakter, tekniske adfærdsregler og godkendte implementeringsvalg.
4. `docs/clean-backlog-v0120.md` – operativ backlog.'''
if old in handover:
    handover = handover.replace(old, new, 1)
    handover = handover.replace('4. `clean-update.json`', '5. `clean-update.json`', 1)
    handover = handover.replace('5. `clean-release-notes.html`', '6. `clean-release-notes.html`', 1)
    handover = handover.replace('6. `CLEAN-USER-MANUAL.md`', '7. `CLEAN-USER-MANUAL.md`', 1)
    handover = handover.replace('7. `DESIGN-MANUAL.md`', '8. `DESIGN-MANUAL.md`', 1)

old_conflict = '''1. Aktuel kode + `clean-update.json` afgør hvad der faktisk er implementeret.
2. `CLEAN-DESIGN-MANUAL.md` afgør godkendt målarkitektur.
3. `docs/clean-backlog-v0120.md` + denne handover afgør godkendte kommende funktioner og rækkefølge.
4. `CLEAN-USER-MANUAL.md` beskriver brugerflow, men kan være versionsmæssigt bagefter.
5. `DESIGN-MANUAL.md` er legacy/reference, ikke Visual Designer canonical runtime.'''
new_conflict = '''1. Aktuel kode + `clean-update.json` afgør hvad der faktisk er implementeret.
2. `CLEAN-DESIGN-MANUAL.md` afgør godkendt målarkitektur.
3. `CLEAN-TECHNICAL-MANUAL.md` afgør konkrete godkendte UX-kontrakter, tekniske adfærdsregler og implementeringsvalg. Hvis et nyt ønske strider mod en fast kontrakt, skal konflikten afklares før implementering.
4. `docs/clean-backlog-v0120.md` + denne handover afgør godkendte kommende funktioner og rækkefølge.
5. `CLEAN-USER-MANUAL.md` beskriver brugerflow, men kan være versionsmæssigt bagefter.
6. `DESIGN-MANUAL.md` er legacy/reference, ikke Visual Designer canonical runtime.'''
if old_conflict in handover:
    handover = handover.replace(old_conflict, new_conflict, 1)
handover_path.write_text(handover, encoding='utf-8')

design = design_path.read_text(encoding='utf-8')
needle = '3. Opdatér `CLEAN-USER-MANUAL.md`, når ændringen er synlig eller relevant for en redaktør/administrator.\n4. Tilføj ændringen til release-notes/changelog.'
replacement = '3. Opdatér `CLEAN-TECHNICAL-MANUAL.md`, når beslutningen påvirker en konkret UX-kontrakt, teknisk adfærd eller implementeringsregel.\n4. Opdatér `CLEAN-USER-MANUAL.md`, når ændringen er synlig eller relevant for en redaktør/administrator.\n5. Tilføj ændringen til release-notes/changelog.'
if needle in design:
    design = design.replace(needle, replacement, 1)
    design = design.replace('5. Kør QA på editor, Save/Reload, Preview og frontend.\n6. Byg først', '6. Kør QA på editor, Save/Reload, Preview og frontend.\n7. Byg først', 1)
design_path.write_text(design, encoding='utf-8')

user = user_path.read_text(encoding='utf-8')
related = '- `CLEAN-DESIGN-MANUAL.md` – teknisk design- og arkitekturmanual for Clean.'
if related in user and 'CLEAN-TECHNICAL-MANUAL.md' not in user:
    user = user.replace(related, related + '\n- `CLEAN-TECHNICAL-MANUAL.md` – konkrete UX-kontrakter, tekniske adfærdsregler, beslutningsregister og reviewforslag.', 1)
user_path.write_text(user, encoding='utf-8')
