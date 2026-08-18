from pathlib import Path

plugin=Path('hangar18-manager.php')
text=plugin.read_text(encoding='utf-8')
text=text.replace(' * Version: 0.8.1',' * Version: 0.8.2',1)
text=text.replace("const VERSION = '0.8.1';","const VERSION = '0.8.2';",1)
if ' * Version: 0.8.2' not in text or "const VERSION = '0.8.2';" not in text:
    raise SystemExit('version replacement failed')
plugin.write_text(text,encoding='utf-8')

readme=Path('readme.txt')
r=readme.read_text(encoding='utf-8')
r=r.replace('Version: 0.8.1','Version: 0.8.2',1)
section='''== Version 0.8.2 – I9 Manual QA & rollback rehearsal ==

Nyt:
- Manual QA Dashboard viser alle otte obligatoriske I10-gates og deres dokumenterede status.
- Manuel PASS kræver eksplicit bekræftelse, miljø/browser/device og evidensreference; bruger-ID og UTC-tid gemmes.
- Automatisk test/preflight kan ikke udgive sig for manuel evidens eller lukke en manuel gate.
- Rollback preflight kører kun på en in-memory kopi af legacy page-store og verificerer original/mutated/restored hashes.
- Preflight skriver ikke til hangar18_manager_pages_v1 og kan aldrig sætte migration-rollback-live-copy til PASS.
- I10 forbliver blokeret indtil de krævede manuelle/live gates faktisk er gennemført. Frontend og Vehicle/Event/Gallery ændres ikke.


'''
marker='== Version 0.8.1 – I8 AI forslag =='
if section.strip() not in r:
    if marker not in r:
        raise SystemExit('readme insertion marker missing')
    r=r.replace(marker,section+marker,1)
readme.write_text(r,encoding='utf-8')
