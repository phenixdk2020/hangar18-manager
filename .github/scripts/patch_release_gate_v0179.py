from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / '.github/workflows/visual-designer-release.yml'
s = p.read_text(encoding='utf-8')
anchor = "          python3 .github/scripts/v0172_gallery_design_qa.py\n"
block = anchor + """          python3 .github/scripts/v0173_editor_frontend_parity_qa.py
          python3 .github/scripts/v0174_module_cutover_qa.py
          python3 .github/scripts/v0175_forms_search_archive_qa.py
          python3 .github/scripts/v0177_module_design_qa.py
          python3 .github/scripts/v0178_hybrid_event_fields_qa.py
          python3 .github/scripts/v0179_responsive_qa.py
"""
if block not in s:
    if s.count(anchor) != 1:
        raise SystemExit(f'central release QA anchor count={s.count(anchor)}')
    s = s.replace(anchor, block, 1)
p.write_text(s, encoding='utf-8')
print('Central Visual Designer release gate now runs QA through v0.1.79.')
