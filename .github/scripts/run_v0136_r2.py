from pathlib import Path

path = Path('.github/scripts/apply_v0136.py')
src = path.read_text(encoding='utf-8')
src = src.replace("tech = tech.replace('## 21. Kontraktstatus for 0.1.34', '## 21. Kontraktstatus for 0.1.36', 1)", "tech = tech.replace('## 21. Kontraktstatus for 0.1.35', '## 21. Kontraktstatus for 0.1.36', 1)")
old = "old_rich = \\\"**BUGFIX i 0.1.34 – afventer bruger-QA.** Bruger-QA af 0.1.33 viste Understregning stabil, Fed ustabil og Kursiv fortsat fejlbehæftet. Årsagen var tre samtidige selection-restore-lag (`v0125`, `v0131`, `v0132`). I 0.1.34 er `v0125` eneste autoritative selection-ejer; de to ældre restore-loops delegerer/returnerer. Selection fanges ved pointerdown som logiske tekst-offsets og bruges af én atomisk command-transaction for Fed, Kursiv og Understregning.\\\""
new = "old_rich = \\\"**BUGFIX i 0.1.35 – afventer bruger-QA.** 0.1.34 løste ikke Fed/Kursiv stabilt. I 0.1.35 bruger Fed, Kursiv og Understregning ikke længere browserens `execCommand()` til selve inline-formatet. De tre udføres som deterministiske DOM-transaktioner, og selection rekonstrueres fra logiske tekst-offsets.\\\""
if old not in src:
    raise SystemExit('Could not patch v0136 technical manual anchor in runner')
src = src.replace(old, new, 1)
exec(compile(src, str(path), 'exec'))
