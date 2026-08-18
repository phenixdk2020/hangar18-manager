from pathlib import Path
p=Path('.github/scripts/patch_v0529.py')
t=p.read_text()
marker="php=once(php,\"\"\"                            <div class=\\\"h18-field\\\"><label><strong>Titel</strong>"
start=t.index(marker)
end=t.index("# Current entry form is actually", start)
title="                            <div class=\\\"h18-field\\\"><label><strong>Titel</strong></label><input type=\\\"text\\\" name=\\\"entry_title\\\" value=\\\"<?php echo esc_attr($entry ? $entry->post_title : ''); ?>\\\" required /></div>\\n"
tag="                            <div class=\\\"h18-field\\\"><label><strong>Data Tags</strong><small>Taxonomy · kommasepareret</small></label><input type=\\\"text\\\" name=\\\"data_tags\\\" value=\\\"<?php echo esc_attr(implode(', ', array_map('strval',(array)$entry_tags))); ?>\\\" placeholder=\\\"fx aktiv, nordjylland\\\" /></div>\\n"
block="php=once(php,\"\"\""+title+"\"\"\",\"\"\""+title+tag+"\"\"\",'entry tag input')\n"
t=t[:start]+block+t[end:]
p.write_text(t)
print('v0.5.29 Data Tags title-line anchor prepared')
