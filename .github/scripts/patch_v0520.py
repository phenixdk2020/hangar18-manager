from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    return text.replace(old, new, 1)

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js'); css_path=Path('assets/admin.css'); readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

php=replace_once(php,' * Version: 0.5.19',' * Version: 0.5.20','plugin header')
php=replace_once(php,"    const VERSION = '0.5.19';","    const VERSION = '0.5.20';",'plugin const')

# Header/design-system defaults: preserve all prior values by using current breakpoints/motion as defaults.
default_old="""            'SpacingLargePx' => 24,
            'SpacingXlPx' => 40,
            'MenuPresentation' => 'Classic',
"""
default_new="""            'SpacingLargePx' => 24,
            'SpacingXlPx' => 40,
            'BreakpointMobileMaxPx' => 782,
            'BreakpointTabletMaxPx' => 1199,
            'MotionFastMs' => 120,
            'MotionNormalMs' => 220,
            'MotionSlowMs' => 420,
            'FocusRingColor' => '#8b4a2b',
            'FocusRingWidthPx' => 3,
            'MenuPresentation' => 'Classic',
"""
php=replace_once(php,default_old,default_new,'design defaults')
php=php.replace("'DesignerSchemaVersion' => '1.0'","'DesignerSchemaVersion' => '1.1'",1)

normalize_old="""            'SpacingLargePx'                    => $this->clamp_int($saved['SpacingLargePx'] ?? $default['SpacingLargePx'], 0, 96, $default['SpacingLargePx']),
            'SpacingXlPx'                       => $this->clamp_int($saved['SpacingXlPx'] ?? $default['SpacingXlPx'], 0, 140, $default['SpacingXlPx']),
            'MenuPresentation'                  => in_array((string) ($saved['MenuPresentation'] ?? ''), $allowed_menu_presentations, true) ? (string) $saved['MenuPresentation'] : $default['MenuPresentation'],
"""
normalize_new="""            'SpacingLargePx'                    => $this->clamp_int($saved['SpacingLargePx'] ?? $default['SpacingLargePx'], 0, 96, $default['SpacingLargePx']),
            'SpacingXlPx'                       => $this->clamp_int($saved['SpacingXlPx'] ?? $default['SpacingXlPx'], 0, 140, $default['SpacingXlPx']),
            'BreakpointMobileMaxPx'             => $this->clamp_int($saved['BreakpointMobileMaxPx'] ?? $default['BreakpointMobileMaxPx'], 480, 900, $default['BreakpointMobileMaxPx']),
            'BreakpointTabletMaxPx'             => $this->clamp_int($saved['BreakpointTabletMaxPx'] ?? $default['BreakpointTabletMaxPx'], 901, 1600, $default['BreakpointTabletMaxPx']),
            'MotionFastMs'                      => $this->clamp_int($saved['MotionFastMs'] ?? $default['MotionFastMs'], 0, 1000, $default['MotionFastMs']),
            'MotionNormalMs'                    => $this->clamp_int($saved['MotionNormalMs'] ?? $default['MotionNormalMs'], 0, 1500, $default['MotionNormalMs']),
            'MotionSlowMs'                      => $this->clamp_int($saved['MotionSlowMs'] ?? $default['MotionSlowMs'], 0, 2500, $default['MotionSlowMs']),
            'FocusRingColor'                    => $normalize_color($saved['FocusRingColor'] ?? $default['FocusRingColor'], $default['FocusRingColor']),
            'FocusRingWidthPx'                  => $this->clamp_int($saved['FocusRingWidthPx'] ?? $default['FocusRingWidthPx'], 1, 8, $default['FocusRingWidthPx']),
            'MenuPresentation'                  => in_array((string) ($saved['MenuPresentation'] ?? ''), $allowed_menu_presentations, true) ? (string) $saved['MenuPresentation'] : $default['MenuPresentation'],
"""
php=replace_once(php,normalize_old,normalize_new,'design normalize')
# normalize return schema occurrence
php=php.replace("'DesignerSchemaVersion'             => '1.0'","'DesignerSchemaVersion'             => '1.1'",1)

post_old="""            'SpacingLargePx'                    => $_POST['SpacingLargePx'] ?? 24,
            'SpacingXlPx'                       => $_POST['SpacingXlPx'] ?? 40,
            'MenuPresentation'                  => $this->post_text('MenuPresentation'),
"""
post_new="""            'SpacingLargePx'                    => $_POST['SpacingLargePx'] ?? 24,
            'SpacingXlPx'                       => $_POST['SpacingXlPx'] ?? 40,
            'BreakpointMobileMaxPx'             => $_POST['BreakpointMobileMaxPx'] ?? 782,
            'BreakpointTabletMaxPx'             => $_POST['BreakpointTabletMaxPx'] ?? 1199,
            'MotionFastMs'                      => $_POST['MotionFastMs'] ?? 120,
            'MotionNormalMs'                    => $_POST['MotionNormalMs'] ?? 220,
            'MotionSlowMs'                      => $_POST['MotionSlowMs'] ?? 420,
            'FocusRingColor'                    => $this->post_text('FocusRingColor'),
            'FocusRingWidthPx'                  => $_POST['FocusRingWidthPx'] ?? 3,
            'MenuPresentation'                  => $this->post_text('MenuPresentation'),
"""
php=replace_once(php,post_old,post_new,'design post')
php=php.replace("'DesignerSchemaVersion'             => '1.0'","'DesignerSchemaVersion'             => '1.1'",1)

# Root design tokens.
tokens_old="""        --h18-space-l:<?php echo esc_html((int) $d['SpacingLargePx']); ?>px;
        --h18-space-xl:<?php echo esc_html((int) $d['SpacingXlPx']); ?>px;
        --h18-menu-transition:<?php echo esc_html($transition); ?>ms;
"""
tokens_new="""        --h18-space-l:<?php echo esc_html((int) $d['SpacingLargePx']); ?>px;
        --h18-space-xl:<?php echo esc_html((int) $d['SpacingXlPx']); ?>px;
        --h18-motion-fast:<?php echo esc_html((int) $d['MotionFastMs']); ?>ms;
        --h18-motion-normal:<?php echo esc_html((int) $d['MotionNormalMs']); ?>ms;
        --h18-motion-slow:<?php echo esc_html((int) $d['MotionSlowMs']); ?>ms;
        --h18-focus-ring:<?php echo esc_html($d['FocusRingColor']); ?>;
        --h18-focus-ring-width:<?php echo esc_html((int) $d['FocusRingWidthPx']); ?>px;
        --h18-menu-transition:<?php echo esc_html($transition); ?>ms;
"""
php=replace_once(php,tokens_old,tokens_new,'root motion tokens')

# Header/Footer design admin panels: add breakpoints and motion after spacing panel.
spacing_panel_tail="""                        $this->field('SpacingLargePx', 'Afstand L (px)', $s['SpacingLargePx'], 'number');
                        $this->field('SpacingXlPx', 'Afstand XL (px)', $s['SpacingXlPx'], 'number');
                        ?>
                    </section>
"""
spacing_panel_new=spacing_panel_tail+"""                    <section class=\"h18-panel\">
                        <h3>Responsive breakpoints</h3>
                        <p class=\"description\">Globale breakpoints for sidebyggerens Desktop/Tablet/Mobil. Standard 782/1199 bevarer det nuværende layout.</p>
                        <?php
                        $this->field('BreakpointMobileMaxPx', 'Mobil maks. bredde (px)', $s['BreakpointMobileMaxPx'], 'number');
                        $this->field('BreakpointTabletMaxPx', 'Tablet maks. bredde (px)', $s['BreakpointTabletMaxPx'], 'number');
                        ?>
                    </section>
                    <section class=\"h18-panel\">
                        <h3>Motion og fokus</h3>
                        <p class=\"description\">Globale tokens for transitioner og keyboard-fokus. Reduced Motion respekteres fortsat.</p>
                        <?php
                        $this->field('MotionFastMs', 'Motion Fast (ms)', $s['MotionFastMs'], 'number');
                        $this->field('MotionNormalMs', 'Motion Normal (ms)', $s['MotionNormalMs'], 'number');
                        $this->field('MotionSlowMs', 'Motion Slow (ms)', $s['MotionSlowMs'], 'number');
                        $this->field('FocusRingColor', 'Global fokusfarve', $s['FocusRingColor'], 'color');
                        $this->field('FocusRingWidthPx', 'Global fokusbredde (px)', $s['FocusRingWidthPx'], 'number');
                        ?>
                    </section>
"""
php=replace_once(php,spacing_panel_tail,spacing_panel_new,'design admin panels')

# Per-section new state defaults.
section_defaults_old="""            'HoverBorderColor'       => '#c3ae83',
            'HoverOpacityPercent'    => 100,
            'ShowDesktop'            => true,
"""
section_defaults_new="""            'HoverBorderColor'       => '#c3ae83',
            'HoverOpacityPercent'    => 100,
            'TransitionPreset'       => 'Inherit',
            'FocusRingStyle'         => 'Global',
            'FocusRingColor'         => '#8b4a2b',
            'FocusRingWidthPx'       => 3,
            'FocusRingOffsetPx'      => 2,
            'ActiveEffect'           => 'None',
            'DisabledOpacityPercent' => 55,
            'ShowDesktop'            => true,
"""
php=replace_once(php,section_defaults_old,section_defaults_new,'section state defaults')

# Normalize state enums after hover colors.
state_norm_anchor="""        $hover_border = sanitize_hex_color((string) ($raw['HoverBorderColor'] ?? '#c3ae83')) ?: '#c3ae83';
"""
state_norm_new=state_norm_anchor+"""        $transition_preset = (string) ($raw['TransitionPreset'] ?? 'Inherit');
        if (!in_array($transition_preset, ['Inherit','Fast','Normal','Slow','Custom'], true)) { $transition_preset = 'Inherit'; }
        $focus_ring_style = (string) ($raw['FocusRingStyle'] ?? 'Global');
        if (!in_array($focus_ring_style, ['Global','Custom','None'], true)) { $focus_ring_style = 'Global'; }
        $focus_ring_color = sanitize_hex_color((string) ($raw['FocusRingColor'] ?? '#8b4a2b')) ?: '#8b4a2b';
        $active_effect = (string) ($raw['ActiveEffect'] ?? 'None');
        if (!in_array($active_effect, ['None','Press','ScaleDown'], true)) { $active_effect = 'None'; }
"""
php=replace_once(php,state_norm_anchor,state_norm_new,'state normalize enums')

section_return_old="""            'HoverBorderColor'       => $hover_border,
            'HoverOpacityPercent'    => $this->clamp_int($raw['HoverOpacityPercent'] ?? 100, 0, 100, 100),
            'ShowDesktop'            => array_key_exists('ShowDesktop', $raw) ? !empty($raw['ShowDesktop']) : true,
"""
section_return_new="""            'HoverBorderColor'       => $hover_border,
            'HoverOpacityPercent'    => $this->clamp_int($raw['HoverOpacityPercent'] ?? 100, 0, 100, 100),
            'TransitionPreset'       => $transition_preset,
            'FocusRingStyle'         => $focus_ring_style,
            'FocusRingColor'         => $focus_ring_color,
            'FocusRingWidthPx'       => $this->clamp_int($raw['FocusRingWidthPx'] ?? 3, 1, 8, 3),
            'FocusRingOffsetPx'      => $this->clamp_int($raw['FocusRingOffsetPx'] ?? 2, 0, 12, 2),
            'ActiveEffect'           => $active_effect,
            'DisabledOpacityPercent' => $this->clamp_int($raw['DisabledOpacityPercent'] ?? 55, 10, 100, 55),
            'ShowDesktop'            => array_key_exists('ShowDesktop', $raw) ? !empty($raw['ShowDesktop']) : true,
"""
php=replace_once(php,section_return_old,section_return_new,'state normalized fields')

# Schema bump 1.15 -> 1.16 in active payloads and central Pages manifest.
if php.count("'Version'        => '1.15'") != 3:
    raise SystemExit('Expected 3 active page schema 1.15 payloads')
php=php.replace("'Version'        => '1.15'","'Version'        => '1.16'")
php=php.replace("'Version' => '1.15',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,","'Version' => '1.16',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php=php.replace("'Version' => '1.15',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,","'Version' => '1.16',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

# Per-section CSS vars: global token inheritance + custom focus/state values.
style_state_anchor="""        $hover_background_image = $hover_style_custom ? 'none' : $effect_image;
"""
style_state_new=style_state_anchor+"""        $transition_preset = (string) ($section['TransitionPreset'] ?? 'Inherit');
        $transition_css = 'var(--h18-motion-normal,220ms)';
        if ($transition_preset === 'Fast') { $transition_css = 'var(--h18-motion-fast,120ms)'; }
        elseif ($transition_preset === 'Slow') { $transition_css = 'var(--h18-motion-slow,420ms)'; }
        elseif ($transition_preset === 'Custom') { $transition_css = (int) ($section['HoverTransitionMs'] ?? 220) . 'ms'; }
        $focus_style = (string) ($section['FocusRingStyle'] ?? 'Global');
        $focus_color = $focus_style === 'Custom' ? (string) ($section['FocusRingColor'] ?? '#8b4a2b') : 'var(--h18-focus-ring,#8b4a2b)';
        $focus_width = $focus_style === 'Custom' ? (int) ($section['FocusRingWidthPx'] ?? 3) . 'px' : 'var(--h18-focus-ring-width,3px)';
        if ($focus_style === 'None') { $focus_width = '0px'; }
        $focus_offset = (int) ($section['FocusRingOffsetPx'] ?? 2) . 'px';
        $disabled_opacity = max(10, min(100, (int) ($section['DisabledOpacityPercent'] ?? 55))) / 100;
"""
php=replace_once(php,style_state_anchor,style_state_new,'section style states')

style_return_old="""            '--h18-hover-opacity:' . $hover_opacity . ';' .
            '--h18-hover-transition:' . (int) ($section['HoverTransitionMs'] ?? 220) . 'ms;';
"""
style_return_new="""            '--h18-hover-opacity:' . $hover_opacity . ';' .
            '--h18-hover-transition:' . (int) ($section['HoverTransitionMs'] ?? 220) . 'ms;' .
            '--h18-state-transition:' . $transition_css . ';' .
            '--h18-focus-color:' . $focus_color . ';' .
            '--h18-focus-width:' . $focus_width . ';' .
            '--h18-focus-offset:' . $focus_offset . ';' .
            '--h18-disabled-opacity:' . $disabled_opacity . ';';
"""
php=replace_once(php,style_return_old,style_return_new,'section state vars')

# State class for active effect.
classes_old="""        if (($section['HoverStyleMode'] ?? 'Inherit') === 'Custom') { $classes[] = 'h18-hover-style-custom'; }
        return implode(' ', $classes);
"""
classes_new="""        if (($section['HoverStyleMode'] ?? 'Inherit') === 'Custom') { $classes[] = 'h18-hover-style-custom'; }
        if (($section['ActiveEffect'] ?? 'None') === 'Press') { $classes[] = 'h18-active-effect-press'; }
        elseif (($section['ActiveEffect'] ?? 'None') === 'ScaleDown') { $classes[] = 'h18-active-effect-scale'; }
        return implode(' ', $classes);
"""
php=replace_once(php,classes_old,classes_new,'active effect classes')

# Dynamic page-editor breakpoints and state CSS. Only patch function substring so legacy/header responsive CSS is untouched.
start=php.index('    private function page_editor_frontend_css($page_id) {')
end=php.index('    private function render_page_editor_imported_group', start)
block=php[start:end]
block=replace_once(block,"""        $id = (int) $page_id;
        return '<style id=\"h18-page-editor-style-' . $id . '\">' .
""","""        $id = (int) $page_id;
        $design = $this->get_header_design_settings();
        $mobile_breakpoint = (int) ($design['BreakpointMobileMaxPx'] ?? 782);
        $tablet_breakpoint = (int) ($design['BreakpointTabletMaxPx'] ?? 1199);
        $tablet_min = $mobile_breakpoint + 1;
        $desktop_min = $tablet_breakpoint + 1;
        return '<style id=\"h18-page-editor-style-' . $id . '\">' .
""",'frontend breakpoint vars')
block=block.replace("@media(max-width:782px)","@media(max-width:' . $mobile_breakpoint . 'px)")
block=block.replace("@media(min-width:783px) and (max-width:1199px)","@media(min-width:' . $tablet_min . 'px) and (max-width:' . $tablet_breakpoint . 'px)")
block=block.replace("@media(min-width:1200px)","@media(min-width:' . $desktop_min . 'px)")
# Insert state CSS near reduced motion rule anchor.
state_css="""            '.h18-editor-section :is(a,button,input,select,textarea,[tabindex]):focus-visible{outline:var(--h18-focus-width,var(--h18-focus-ring-width,3px)) solid var(--h18-focus-color,var(--h18-focus-ring,#8b4a2b));outline-offset:var(--h18-focus-offset,2px);transition:outline-color var(--h18-state-transition,var(--h18-motion-normal,220ms)) ease,box-shadow var(--h18-state-transition,var(--h18-motion-normal,220ms)) ease}.h18-editor-section.h18-active-effect-press :is(a,button,[role=button]):active{transform:translateY(1px)}.h18-editor-section.h18-active-effect-scale :is(a,button,[role=button]):active{transform:scale(.97)}.h18-editor-section :is(button,input,select,textarea):disabled,.h18-editor-section [aria-disabled=true]{opacity:var(--h18-disabled-opacity,.55);cursor:not-allowed}.h18-editor-section :is(a,button,[role=button]){transition-duration:var(--h18-state-transition,var(--h18-motion-normal,220ms))}' .
"""
anchor="            '@media(prefers-reduced-motion:reduce){"
if anchor not in block: raise SystemExit('Reduced motion CSS anchor missing')
block=block.replace(anchor,state_css+anchor,1)
php=php[:start]+block+php[end:]

# Section admin interaction state box after Hover box.
hover_admin_tail="""                                        <div class=\"h18-field\"><label><strong>Opacity (%)</strong></label><input type=\"number\" min=\"0\" max=\"100\" name=\"<?php echo esc_attr($prefix); ?>[HoverOpacityPercent]\" value=\"<?php echo esc_attr($section['HoverOpacityPercent']); ?>\" /></div>
                                    </div>
                                </div>
"""
interaction_admin=hover_admin_tail+"""                                <div class=\"h18-interaction-state-box\">
                                    <h4>Interaktions-states</h4>
                                    <p class=\"description\">Focus, Active og Disabled gælder interaktive kontroller inde i dette element. Standarderne arver det globale designsystem.</p>
                                    <div class=\"h18-module-fields-grid h18-module-fields-grid--four\">
                                        <div class=\"h18-field\"><label><strong>Transition</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[TransitionPreset]\"><option value=\"Inherit\" <?php selected($section['TransitionPreset'],'Inherit'); ?>>Global Normal</option><option value=\"Fast\" <?php selected($section['TransitionPreset'],'Fast'); ?>>Fast</option><option value=\"Normal\" <?php selected($section['TransitionPreset'],'Normal'); ?>>Normal</option><option value=\"Slow\" <?php selected($section['TransitionPreset'],'Slow'); ?>>Slow</option><option value=\"Custom\" <?php selected($section['TransitionPreset'],'Custom'); ?>>Brug Hover-transition</option></select></div>
                                        <div class=\"h18-field\"><label><strong>Focus ring</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[FocusRingStyle]\"><option value=\"Global\" <?php selected($section['FocusRingStyle'],'Global'); ?>>Global</option><option value=\"Custom\" <?php selected($section['FocusRingStyle'],'Custom'); ?>>Tilpasset</option><option value=\"None\" <?php selected($section['FocusRingStyle'],'None'); ?>>Ingen</option></select></div>
                                        <div class=\"h18-field\"><label><strong>Focus farve</strong></label><input type=\"color\" name=\"<?php echo esc_attr($prefix); ?>[FocusRingColor]\" value=\"<?php echo esc_attr($section['FocusRingColor']); ?>\" /></div>
                                        <div class=\"h18-field\"><label><strong>Focus bredde (px)</strong></label><input type=\"number\" min=\"1\" max=\"8\" name=\"<?php echo esc_attr($prefix); ?>[FocusRingWidthPx]\" value=\"<?php echo esc_attr($section['FocusRingWidthPx']); ?>\" /></div>
                                        <div class=\"h18-field\"><label><strong>Focus offset (px)</strong></label><input type=\"number\" min=\"0\" max=\"12\" name=\"<?php echo esc_attr($prefix); ?>[FocusRingOffsetPx]\" value=\"<?php echo esc_attr($section['FocusRingOffsetPx']); ?>\" /></div>
                                        <div class=\"h18-field\"><label><strong>Active-effekt</strong></label><select name=\"<?php echo esc_attr($prefix); ?>[ActiveEffect]\"><option value=\"None\" <?php selected($section['ActiveEffect'],'None'); ?>>Ingen</option><option value=\"Press\" <?php selected($section['ActiveEffect'],'Press'); ?>>Tryk 1 px</option><option value=\"ScaleDown\" <?php selected($section['ActiveEffect'],'ScaleDown'); ?>>Scale 97%</option></select></div>
                                        <div class=\"h18-field\"><label><strong>Disabled opacity (%)</strong></label><input type=\"number\" min=\"10\" max=\"100\" name=\"<?php echo esc_attr($prefix); ?>[DisabledOpacityPercent]\" value=\"<?php echo esc_attr($section['DisabledOpacityPercent']); ?>\" /></div>
                                    </div>
                                </div>
"""
php=replace_once(php,hover_admin_tail,interaction_admin,'interaction admin')

# JS state toolbar: 5 states.
toolbar_old="""            const $normal = $('<button>', { type: 'button', class: 'button h18-preview-state is-active', 'data-state': 'normal', text: 'Normal' });
            const $hover = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'hover', text: 'Hover' });
            $label.insertBefore($hint); $normal.insertBefore($hint); $hover.insertBefore($hint);
"""
toolbar_new="""            const $normal = $('<button>', { type: 'button', class: 'button h18-preview-state is-active', 'data-state': 'normal', text: 'Normal' });
            const $hover = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'hover', text: 'Hover' });
            const $focus = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'focus', text: 'Focus' });
            const $active = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'active', text: 'Aktiv' });
            const $disabled = $('<button>', { type: 'button', class: 'button h18-preview-state', 'data-state': 'disabled', text: 'Disabled' });
            $label.insertBefore($hint); $normal.insertBefore($hint); $hover.insertBefore($hint); $focus.insertBefore($hint); $active.insertBefore($hint); $disabled.insertBefore($hint);
"""
js=replace_once(js,toolbar_old,toolbar_new,'state toolbar buttons')

click_old="""        currentCanvasState = String($(this).data('state') || 'normal') === 'hover' ? 'hover' : 'normal';
"""
click_new="""        const requestedState = String($(this).data('state') || 'normal');
        currentCanvasState = ['normal','hover','focus','active','disabled'].includes(requestedState) ? requestedState : 'normal';
"""
js=replace_once(js,click_old,click_new,'state click validation')

status_old="""        const stateLabel = currentCanvasState === 'hover' ? 'Hover' : 'Normal';
"""
status_new="""        const stateLabels = { normal: 'Normal', hover: 'Hover', focus: 'Focus', active: 'Aktiv', disabled: 'Disabled' };
        const stateLabel = stateLabels[currentCanvasState] || 'Normal';
"""
js=replace_once(js,status_old,status_new,'canvas state status')

history_old="""            currentCanvasState = String(entry.state) === 'hover' ? 'hover' : 'normal';
"""
history_new="""            currentCanvasState = ['normal','hover','focus','active','disabled'].includes(String(entry.state)) ? String(entry.state) : 'normal';
"""
js=replace_once(js,history_old,history_new,'history state restore')

palette_old="""        [['normal','Normal'],['hover','Hover']].forEach(function (entry) {
"""
palette_new="""        [['normal','Normal'],['hover','Hover'],['focus','Focus'],['active','Aktiv'],['disabled','Disabled']].forEach(function (entry) {
"""
js=replace_once(js,palette_old,palette_new,'palette states')

# Canvas color disabled preview and active/focus visual state.
colors_hover_anchor="""        if (currentCanvasState === 'hover' && String(canvasFieldValue($row, 'HoverStyleMode', 'Inherit')) === 'Custom') {
"""
# No replacement necessary for hover; append disabled just before return using known return anchor.
colors_return="""        return { background: background, backgroundImage: backgroundImage, text: text, heading: heading, border: border, opacity: opacity };
"""
colors_return_new="""        if (currentCanvasState === 'disabled') {
            opacity *= Math.max(10, Math.min(100, canvasNumber($row, 'DisabledOpacityPercent', 55))) / 100;
        }
        return { background: background, backgroundImage: backgroundImage, text: text, heading: heading, border: border, opacity: opacity };
"""
js=replace_once(js,colors_return,colors_return_new,'canvas disabled opacity')

hover_effect_anchor="""        if (currentCanvasState === 'hover') {
            const effect = String(canvasFieldValue($row, 'HoverEffect', 'None'));
            if (effect === 'Lift') { translateY -= 6; }
            if (effect === 'Scale') { scale *= 1.025; }
            if (effect === 'Shadow') { shadow = '0 16px 38px rgba(0,0,0,.24)'; }
        }
"""
active_effect_new=hover_effect_anchor+"""        if (currentCanvasState === 'active') {
            const activeEffect = String(canvasFieldValue($row, 'ActiveEffect', 'None'));
            if (activeEffect === 'Press') { translateY += 1; }
            if (activeEffect === 'ScaleDown') { scale *= 0.97; }
        }
        const focusPreview = currentCanvasState === 'focus' && String(canvasFieldValue($row, 'FocusRingStyle', 'Global')) !== 'None';
        const focusColor = String(canvasFieldValue($row, 'FocusRingColor', '#8b4a2b'));
        const focusWidth = Math.max(1, Math.min(8, canvasNumber($row, 'FocusRingWidthPx', 3)));
        const focusOffset = Math.max(0, Math.min(12, canvasNumber($row, 'FocusRingOffsetPx', 2)));
        if (focusPreview) { shadow = '0 0 0 ' + focusOffset + 'px transparent,0 0 0 ' + (focusOffset + focusWidth) + 'px ' + focusColor; }
"""
js=replace_once(js,hover_effect_anchor,active_effect_new,'canvas active focus state')

# Direct controls consider only hover as hover; other states remain normal controls, intentionally.
# CSS admin hint state buttons wrap.
css_block="""

/* v0.5.20 – design-system states */
.h18-interaction-state-box{margin-top:14px;padding-top:12px;border-top:1px solid #dcdcde}.h18-interaction-state-box h4{margin:0 0 6px}.h18-page-preview-toolbar .h18-preview-state{white-space:nowrap}
"""
if '/* v0.5.20 – design-system states */' in css: raise SystemExit('v0.5.20 CSS already present')
css=css.rstrip()+css_block+'\n'

readme=replace_once(readme,'Version: 0.5.19','Version: 0.5.20','readme version')
readme_anchor='== Version 0.5.19 – Section/Container/Flex/Grid layout foundation ==\n'
readme_new="""== Version 0.5.20 – E3 Design System completion ==

Nyt:
- globale redigerbare builder-breakpoints med standard 782 px mobil og 1199 px tablet, så eksisterende sider bevarer nuværende responsive adfærd
- globale motion-tokens: Fast, Normal og Slow samt global focus-ring farve og bredde
- elementer kan vælge Transition: Global, Fast, Normal, Slow eller eksisterende Custom hover-transition
- Focus-state med global, tilpasset eller ingen focus ring samt farve, bredde og offset
- Active-state med Ingen, Tryk 1 px eller Scale 97% for interaktive descendants
- Disabled-state med justerbar opacity for disabled/aria-disabled kontroller
- live canvas og kommandopalette kan nu vise Normal, Hover, Focus, Aktiv og Disabled
- page-editor media queries bruger de globale breakpoints uden at ændre headerens eksisterende responsive legacy-regler
- prefers-reduced-motion bevares; motion-tokens ændrer ikke brugerens reducerede motion-præference
- DesignerSchemaVersion løftes kompatibelt til 1.1 og page-editor schema til 1.16

"""+readme_anchor
readme=replace_once(readme,readme_anchor,readme_new,'readme v0.5.19 anchor')

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.20 patch applied')
