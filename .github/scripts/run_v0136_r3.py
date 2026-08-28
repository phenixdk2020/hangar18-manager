from pathlib import Path

tech_path = Path('CLEAN-TECHNICAL-MANUAL.md')
tech = tech_path.read_text(encoding='utf-8')
current = "**BUGFIX i 0.1.35 – afventer bruger-QA.** 0.1.34 løste ikke Fed/Kursiv stabilt. I 0.1.35 bruger Fed, Kursiv og Understregning ikke længere browserens `execCommand()` til selve inline-formatet. De tre udføres som deterministiske DOM-transaktioner, og selection rekonstrueres fra logiske tekst-offsets."
expected = "**BUGFIX i 0.1.34 – afventer bruger-QA.** Bruger-QA af 0.1.33 viste Understregning stabil, Fed ustabil og Kursiv fortsat fejlbehæftet. Årsagen var tre samtidige selection-restore-lag (`v0125`, `v0131`, `v0132`). I 0.1.34 er `v0125` eneste autoritative selection-ejer; de to ældre restore-loops delegerer/returnerer. Selection fanges ved pointerdown som logiske tekst-offsets og bruges af én atomisk command-transaction for Fed, Kursiv og Understregning."
if '## 21. Kontraktstatus for 0.1.35' not in tech or current not in tech:
    raise SystemExit('Current 0.1.35 technical status not found')
tech = tech.replace('## 21. Kontraktstatus for 0.1.35', '## 21. Kontraktstatus for 0.1.34', 1)
tech = tech.replace(current, expected, 1)
tech_path.write_text(tech, encoding='utf-8')

code = Path('.github/scripts/apply_v0136.py').read_text(encoding='utf-8')
exec(compile(code, '.github/scripts/apply_v0136.py', 'exec'))
