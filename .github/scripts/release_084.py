from pathlib import Path

plugin = Path('hangar18-manager.php')
text = plugin.read_text(encoding='utf-8')
old_header = ' * Version: 0.8.3'
old_const = "    const VERSION = '0.8.3';"
if text.count(old_header) != 1 or text.count(old_const) != 1:
    raise SystemExit('Expected v0.8.3 plugin version markers were not found exactly once.')
text = text.replace(old_header, ' * Version: 0.8.4', 1)
text = text.replace(old_const, "    const VERSION = '0.8.4';", 1)
plugin.write_text(text, encoding='utf-8')

readme = Path('readme.txt')
text = readme.read_text(encoding='utf-8')
if not text.startswith('=== Hangar18 Manager ===\nVersion: 0.8.3\n'):
    raise SystemExit('Unexpected readme version header.')
text = text.replace('Version: 0.8.3', 'Version: 0.8.4', 1)
marker = '== Version 0.8.3 – I10 Conversion Planner =='
if marker not in text:
    raise SystemExit('v0.8.3 readme section marker not found.')
section = '''== Version 0.8.4 – I10 Shadow Acceptance Ledger ==\n\nNyt:\n- Side-specifik shadow acceptance kræver syv manuelle checks: desktop, tablet, mobile, save, preview, revision og rollback.\n- Acceptance kræver miljø/browser/device, evidensreference og eksplicit human confirmation.\n- AcceptedForSequence beregnes server-side og kan ikke sættes direkte fra request.\n- Acceptance bindes til den aktuelle shadow SourceHash; en genskabt/ændret shadow gør gammel acceptance automatisk stale.\n- Acceptance lukker ikke de globale I9-gates og aktiverer ikke en offentlig side.\n- Ingen activate/cutover/publish-handler tilføjes; WordPress-posts, URLs og hangar18_manager_pages_v1 forbliver uændrede.\n- Vehicle/Event/Gallery forbliver låst af CompatibilityPolicy på legacy v0.5.30-runtime.\n\n\n'''
text = text.replace(marker, section + marker, 1)
readme.write_text(text, encoding='utf-8')
