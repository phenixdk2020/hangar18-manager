from pathlib import Path
import re

readme = Path('clean/hangar18-manager/readme.txt')
text = readme.read_text(encoding='utf-8')
text = re.sub(r'(?m)^Version:\s*\d+\.\d+\.\d+\s*$', 'Version: 0.1.31', text, count=1)

if '== 0.1.31 ==' not in text:
    marker = '== 0.1.29 =='
    block = '''== 0.1.31 ==
* Flydende Knap flyttes med et separat parent-relativt overlay-flow og går ikke gennem normal celle-split drag/drop.
* Floating reserverer ingen grid-række, påvirker ikke parent auto-grow og bevarer canonical X/Y/W/H.
* Rich-text Fed og Kursiv bevarer selection efter formattering via tekst-offset-baseret Range-gendannelse; samme mekanisme gælder toolbaren generelt.
* Theme Shell-fundament er tilføjet med cutover slået fra som standard, så eksisterende frontend forbliver fallback indtil parity-QA.
* Header/Footer-template resolution er klar som fundament for den senere 1:1-konvertering af Hangar18-header/footer.

== 0.1.30 ==
* Inspector er viewport-bundet med egen scrollbar.
* Rich-text-editoren arver ikke Inspector-labelens font-weight.
* Floating Button kan bruges som parent-relativt overlay på Side-root, Sektion og Kasse og er aldrig position:fixed.
* Update-checkpoint gemmer plugin-ZIP og Designer-data før opdatering.
* Opdateringer viser update-checkpoints og versionshistorik.

'''
    if marker not in text:
        raise SystemExit('Could not find readme insertion marker')
    text = text.replace(marker, block + marker, 1)

readme.write_text(text, encoding='utf-8')
