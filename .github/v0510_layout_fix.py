from pathlib import Path

p = Path('hangar18-manager.php')
text = p.read_text()

start_marker = '                            <div class="h18-section-type-field h18-field-wide h18-image-design-fields" data-types="text_image image">\n'
if text.count(start_marker) != 1:
    raise SystemExit(f'image-design block start count={text.count(start_marker)}')
start = text.index(start_marker)

wrong_end_marker = '                            <div class="h18-field"><label><strong>Kolonner mobil</strong></label>'
end = text.find(wrong_end_marker, start)
if end < 0:
    raise SystemExit('could not find Card Grid block end anchor')
block = text[start:end]
if '<h4>Billedudsnit og fokus</h4>' not in block or '[MobileImageHeightPx]' not in block:
    raise SystemExit('extracted block is not the expected image-design block')
text = text[:start] + text[end:]

position_block = '''                            <div class="h18-field h18-section-type-field" data-types="text_image">
                                <label><strong>Billedplacering på desktop</strong></label>
                                <select name="<?php echo esc_attr($prefix); ?>[ImagePosition]"><option value="Left" <?php selected($section['ImagePosition'], 'Left'); ?>>Venstre</option><option value="Right" <?php selected($section['ImagePosition'], 'Right'); ?>>Højre</option></select>
                                <p class="description">På mobil vises billedet automatisk over teksten.</p>
                            </div>
'''
if text.count(position_block) != 1:
    raise SystemExit(f'image-position block count={text.count(position_block)}')
text = text.replace(position_block, position_block + block, 1)

# Structural QA: exactly one image control block, next to image controls and before Card Grid.
if text.count('h18-image-design-fields') != 1:
    raise SystemExit('image-design block must occur exactly once')
pos_position = text.index('Billedplacering på desktop')
pos_image = text.index('Billedudsnit og fokus')
pos_card_grid = text.index('<h4>Kort-række / kolonner</h4>')
pos_mobile_columns = text.index('<strong>Kolonner mobil</strong>')
if not (pos_position < pos_image < pos_card_grid < pos_mobile_columns):
    raise SystemExit(f'bad control ordering: position={pos_position}, image={pos_image}, card_grid={pos_card_grid}, mobile_columns={pos_mobile_columns}')
if pos_image - pos_position > 9000:
    raise SystemExit('image controls are not adjacent enough to image-position controls')
card_start = text.rfind('h18-card-grid-editor', 0, pos_mobile_columns)
if card_start >= 0 and card_start < pos_image < pos_mobile_columns:
    raise SystemExit('image controls are still inside Card Grid editor')

p.write_text(text)
print('v0.5.10 image inspector placement fixed')
