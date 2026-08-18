from pathlib import Path

plugin=Path('hangar18-manager.php')
text=plugin.read_text(encoding='utf-8')
text=text.replace(' * Version: 0.8.2',' * Version: 0.8.3',1)
text=text.replace("const VERSION = '0.8.2';","const VERSION = '0.8.3';",1)
if ' * Version: 0.8.3' not in text or "const VERSION = '0.8.3';" not in text:
    raise SystemExit('version replacement failed')
plugin.write_text(text,encoding='utf-8')

readme=Path('readme.txt')
r=readme.read_text(encoding='utf-8')
r=r.replace('Version: 0.8.2','Version: 0.8.3',1)
section='''== Version 0.8.3 – I10 Conversion Planner ==

Nyt:
- Kontrolleret I10 conversion planner med fast rækkefølge: sammenligningsside, Hjem, Om, Kontakt, Bliv medlem og til sidst Vehicle/Event/Gallery.
- Alle manglende I9 manuelle gates vises som eksplicitte blockers for fremtidig cutover.
- Shadow workspace kan kopiere ikke-beskyttede legacy editor-states med deterministisk source hash uden at ændre originalen.
- Planner-fasen har PublicMutationAvailable=false; shadow-records har PublicActivation=false og Accepted=false.
- Der registreres ingen activate/cutover/publish-handler i denne version, og WordPress-posts, URLs samt hangar18_manager_pages_v1 ændres ikke.
- Vehicle/Event/Gallery forbliver eksplicit blokeret af CompatibilityPolicy og legacy v0.5.30-runtime.


'''
marker='== Version 0.8.2 – I9 Manual QA & rollback rehearsal =='
if section.strip() not in r:
    if marker not in r:
        raise SystemExit('readme insertion marker missing')
    r=r.replace(marker,section+marker,1)
readme.write_text(r,encoding='utf-8')
