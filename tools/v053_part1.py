from pathlib import Path
p=Path('hangar18-manager.php'); t=p.read_text(encoding='utf-8')
def rep(a,b,n):
    global t
    if a not in t: raise SystemExit(n+' anchor missing')
    t=t.replace(a,b,1)
rep(' * Version: 0.5.2',' * Version: 0.5.3','version')
rep("const VERSION = '0.5.2';","const VERSION = '0.5.3';",'constant')
t=t.replace("'Version'        => '1.6'","'Version'        => '1.7'")
t=t.replace("'Version' => '1.6'","'Version' => '1.7'")
rep("            'ShadowStyle'            => 'None',\n            'ImportedGroupType'     => '',","            'ShadowStyle'            => 'None',\n            'SectionBodyFontFamily' => 'Global',\n            'SectionHeadingFontFamily' => 'Global',\n            'BodyFontSizePx'         => 0,\n            'H1FontSizePx'           => 0,\n            'H2FontSizePx'           => 0,\n            'H3FontSizePx'           => 0,\n            'ImportedGroupType'     => '',",'defaults')
rep("        $custom_border = sanitize_hex_color((string) ($raw['CustomBorderColor'] ?? '#c3ae83')) ?: '#c3ae83';\n\n        $cards = [];","        $custom_border = sanitize_hex_color((string) ($raw['CustomBorderColor'] ?? '#c3ae83')) ?: '#c3ae83';\n        $section_fonts = ['Global', 'System', 'Segoe UI', 'Arial', 'Verdana', 'Tahoma', 'Trebuchet MS', 'Georgia', 'Times New Roman', 'Courier New'];\n        $section_body_font = (string) ($raw['SectionBodyFontFamily'] ?? 'Global');\n        if (!in_array($section_body_font, $section_fonts, true)) { $section_body_font = 'Global'; }\n        $section_heading_font = (string) ($raw['SectionHeadingFontFamily'] ?? 'Global');\n        if (!in_array($section_heading_font, $section_fonts, true)) { $section_heading_font = 'Global'; }\n\n        $cards = [];",'normalize')
rep("            'ShadowStyle'            => $shadow_style,\n            'ImportedGroupType'     => $imported_group_type,","            'ShadowStyle'            => $shadow_style,\n            'SectionBodyFontFamily' => $section_body_font,\n            'SectionHeadingFontFamily' => $section_heading_font,\n            'BodyFontSizePx'         => $this->clamp_int($raw['BodyFontSizePx'] ?? 0, 0, 32, 0),\n            'H1FontSizePx'           => $this->clamp_int($raw['H1FontSizePx'] ?? 0, 0, 96, 0),\n            'H2FontSizePx'           => $this->clamp_int($raw['H2FontSizePx'] ?? 0, 0, 80, 0),\n            'H3FontSizePx'           => $this->clamp_int($raw['H3FontSizePx'] ?? 0, 0, 64, 0),\n            'ImportedGroupType'     => $imported_group_type,",'return')
p.write_text(t,encoding='utf-8')
