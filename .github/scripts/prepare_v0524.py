from pathlib import Path

p=Path('.github/scripts/patch_v0524.py')
t=p.read_text()
old='''php=once(php,\n"""                <script id=\\"h18-page-templates-data\\" type=\\"application/json\\"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>\n                <template id=\\"h18-page-section-template\\">\n""",\n"""                <script id=\\"h18-page-templates-data\\" type=\\"application/json\\"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>\n                <script id=\\"h18-dynamic-data-catalog\\" type=\\"application/json\\"><?php echo wp_json_encode(array_values($dynamic_data_catalog), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>\n                <template id=\\"h18-page-section-template\\">\n""",'dynamic catalog JSON')'''
new='''php=once(php,\n"""                <script id=\\"h18-page-templates-data\\" type=\\"application/json\\"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>\n""",\n"""                <script id=\\"h18-page-templates-data\\" type=\\"application/json\\"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>\n                <script id=\\"h18-dynamic-data-catalog\\" type=\\"application/json\\"><?php echo wp_json_encode(array_values($dynamic_data_catalog), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>\n""",'dynamic catalog JSON')'''
if old not in t:
    raise SystemExit('v0.5.24 catalog patch definition not found')
p.write_text(t.replace(old,new,1))
print('v0.5.24 catalog anchor prepared')
