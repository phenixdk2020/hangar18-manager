from pathlib import Path

plugin = Path('hangar18-manager.php')
text = plugin.read_text(encoding='utf-8')
text = text.replace(' * Version: 0.8.0', ' * Version: 0.8.1', 1)
text = text.replace("const VERSION = '0.8.0';", "const VERSION = '0.8.1';", 1)
if ' * Version: 0.8.1' not in text or "const VERSION = '0.8.1';" not in text:
    raise SystemExit('version replacement failed')
plugin.write_text(text, encoding='utf-8')

readme = Path('readme.txt')
r = readme.read_text(encoding='utf-8')
r = r.replace('Version: 0.8.0', 'Version: 0.8.1', 1)
section = '''== Version 0.8.1 – I8 AI forslag ==

Nyt:
- Provider-neutral AI registry via hangar18_ud_ai_providers; provider adapters håndterer selv credentials.
- AI settings gemmer kun Enabled og ProviderId; API keys/secrets/passwords gemmes ikke i WordPress options.
- Tekstforslag kører i isoleret sandbox og oprettes altid som pending forslag.
- Accept/reject er bundet til et tidsbegrænset HMAC-signeret proposal-token.
- Accept producerer kun reversible Apply/Undo-data; I8 skriver ikke forslag direkte til sider.
- AI kræver hangar18_use_ai eller administrator fallback og ændrer ikke frontend, Vehicle/Event/Gallery eller eksisterende sider.


'''
marker = '== Version 0.8.0 – I7 Permissions & Design Lock =='
if section.strip() not in r:
    if marker not in r:
        raise SystemExit('readme insertion marker missing')
    r = r.replace(marker, section + marker, 1)
readme.write_text(r, encoding='utf-8')
