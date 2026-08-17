from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 anchor, found {count}')
    return text.replace(old, new, 1)

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')
readme_path = Path('readme.txt')
php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

php = replace_once(php, ' * Version: 0.5.16', ' * Version: 0.5.17', 'plugin header')
php = replace_once(php, "    const VERSION = '0.5.16';", "    const VERSION = '0.5.17';", 'plugin const')

labels_old = """            'quote'      => 'Citat',
            'embed'      => 'Embed / medie-URL',
            'shortcode'  => 'Shortcode (avanceret)',
"""
labels_new = """            'quote'      => 'Citat',
            'tabs'       => 'Faner / tabs',
            'accordion'  => 'Accordion',
            'embed'      => 'Embed / medie-URL',
            'shortcode'  => 'Shortcode (avanceret)',
"""
php = replace_once(php, labels_old, labels_new, 'type labels')

# Accessible tab keyboard helper. User content never enters the script body.
helper_anchor = """    private function render_page_editor_list_primitive(array $section) {
"""
tab_helper = r'''    private function page_editor_tabs_script($section_id) {
        $root_json = wp_json_encode((string) $section_id);
        return '<script>(function(){' .
            'var root=document.getElementById(' . $root_json . ');if(!root)return;' .
            'var tabs=Array.prototype.slice.call(root.querySelectorAll("[role=tab]"));' .
            'var panels=Array.prototype.slice.call(root.querySelectorAll("[role=tabpanel]"));if(!tabs.length)return;' .
            'function activate(index,focus){index=(index+tabs.length)%tabs.length;tabs.forEach(function(tab,i){var on=i===index;tab.setAttribute("aria-selected",on?"true":"false");tab.tabIndex=on?0:-1;});panels.forEach(function(panel,i){panel.hidden=i!==index;});if(focus)tabs[index].focus();}' .
            'tabs.forEach(function(tab,index){tab.addEventListener("click",function(){activate(index,false);});tab.addEventListener("keydown",function(e){var next=index;if(e.key==="ArrowRight"||e.key==="ArrowDown")next=index+1;else if(e.key==="ArrowLeft"||e.key==="ArrowUp")next=index-1;else if(e.key==="Home")next=0;else if(e.key==="End")next=tabs.length-1;else return;e.preventDefault();activate(next,true);});});activate(0,false);' .
            '})();</script>';
    }

'''
php = replace_once(php, helper_anchor, tab_helper + helper_anchor, 'tabs script helper')

# Frontend renderer branches before card_grid. Cards are the shared panel model.
cardgrid_anchor = """        } elseif ($section['Type'] === 'card_grid') {
            $border_colors = [
"""
collection_branch = r'''        } elseif (in_array($section['Type'], ['tabs', 'accordion'], true)) {
            $border_colors = [
                'None'  => 'transparent',
                'Sand'  => '#c3ae83',
                'Olive' => '#30382a',
                'Steel' => '#525a5f',
            ];
            $items = [];
            foreach ((array) $section['Cards'] as $card) {
                if (empty($card['Active'])) { continue; }
                $items[] = $card;
            }
            if ($section['Type'] === 'tabs') {
                $tabs = '';
                $panels = '';
                foreach ($items as $item_index => $card) {
                    $card_key = sanitize_html_class((string) ($card['Key'] ?? 'panel-' . $item_index));
                    $tab_id = $id . '-tab-' . $card_key;
                    $panel_id = $id . '-panel-' . $card_key;
                    $label = $card['Title'] !== '' ? (string) $card['Title'] : 'Fane ' . ($item_index + 1);
                    $tone = (string) $card['TextTone'];
                    if ($tone === 'Auto') { $tone = in_array($card['Background'], ['Olive', 'Steel'], true) ? 'Light' : 'Dark'; }
                    $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                    $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                        '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                        '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                        '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                        '--h18-card-border:' . $card_border . ';' .
                        '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                        '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                    $card_background = strtolower((string) $card['Background']);
                    $selected = $item_index === 0;
                    $tabs .= '<button type="button" role="tab" id="' . esc_attr($tab_id) . '" aria-controls="' . esc_attr($panel_id) . '" aria-selected="' . ($selected ? 'true' : 'false') . '" tabindex="' . ($selected ? '0' : '-1') . '" class="h18-editor-tab">' . esc_html($label) . '</button>';
                    $panels .= '<div role="tabpanel" id="' . esc_attr($panel_id) . '" aria-labelledby="' . esc_attr($tab_id) . '" class="h18-editor-tab-panel h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '"' . ($selected ? '' : ' hidden') . '>' . $this->format_page_section_content($card['Content']) . '</div>';
                }
                $inner = $title . $content . '<div class="h18-editor-tabs"><div class="h18-editor-tabs-nav" role="tablist" aria-label="' . esc_attr($section['Title'] !== '' ? $section['Title'] : 'Faner') . '">' . $tabs . '</div>' . $panels . '</div>' . $this->page_editor_tabs_script($id);
            } else {
                $details = '';
                foreach ($items as $item_index => $card) {
                    $label = $card['Title'] !== '' ? (string) $card['Title'] : 'Punkt ' . ($item_index + 1);
                    $tone = (string) $card['TextTone'];
                    if ($tone === 'Auto') { $tone = in_array($card['Background'], ['Olive', 'Steel'], true) ? 'Light' : 'Dark'; }
                    $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                    $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                        '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                        '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                        '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                        '--h18-card-border:' . $card_border . ';' .
                        '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                        '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                    $card_background = strtolower((string) $card['Background']);
                    $details .= '<details class="h18-editor-accordion-item h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '"><summary>' . esc_html($label) . '</summary><div class="h18-editor-accordion-body">' . $this->format_page_section_content($card['Content']) . '</div></details>';
                }
                $inner = $title . $content . '<div class="h18-editor-accordion">' . $details . '</div>';
            }
        } elseif ($section['Type'] === 'card_grid') {
            $border_colors = [
'''
php = replace_once(php, cardgrid_anchor, collection_branch, 'tabs/accordion renderer')

# Frontend CSS before card grid.
css_anchor = """            '.h18-editor-card-grid{display:grid;grid-template-columns:repeat(var(--h18-grid-columns,3),minmax(0,1fr));gap:var(--h18-grid-gap,16px);align-items:stretch}.h18-editor-grid-card{box-sizing:border-box;padding:var(--h18-card-pad,26px);border:var(--h18-card-border-width,0) solid var(--h18-card-border,#c3ae83);border-radius:var(--h18-card-radius,7px);text-align:var(--h18-card-align,left)}.h18-editor-grid-card h3{margin:0 0 12px;color:inherit}.h18-editor-grid-card--white{background:#fff}.h18-editor-grid-card--offwhite{background:#f2f0e8}.h18-editor-grid-card--sand{background:#c3ae83}.h18-editor-grid-card--olive{background:#30382a}.h18-editor-grid-card--steel{background:#525a5f}.h18-editor-grid-card--tone-dark{color:#30382a}.h18-editor-grid-card--tone-light{color:#fff}.h18-editor-grid-card--tone-light h3{color:#fff}' .
"""
css_new = """            '.h18-editor-tabs{display:grid;gap:0}.h18-editor-tabs-nav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:0;border-bottom:1px solid #c3c4c7}.h18-editor-tab{appearance:none;padding:10px 16px;border:1px solid transparent;border-bottom:0;border-radius:6px 6px 0 0;background:transparent;color:inherit;font:inherit;font-weight:700;cursor:pointer}.h18-editor-tab:hover{background:rgba(195,174,131,.14)}.h18-editor-tab[aria-selected=true]{border-color:#c3c4c7;background:#fff;color:#30382a}.h18-editor-tab:focus-visible{outline:2px solid #2271b1;outline-offset:2px}.h18-editor-tab-panel{margin-top:-1px;border-top-left-radius:0!important}.h18-editor-tab-panel[hidden]{display:none!important}.h18-editor-accordion{display:grid;gap:10px}.h18-editor-accordion-item{padding:0!important;overflow:hidden}.h18-editor-accordion-item summary{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:var(--h18-card-pad,20px);font-weight:700;cursor:pointer;list-style:none}.h18-editor-accordion-item summary::-webkit-details-marker{display:none}.h18-editor-accordion-item summary:after{content:\"+\";font-size:1.35em;line-height:1}.h18-editor-accordion-item[open] summary:after{content:\"−\"}.h18-editor-accordion-item summary:focus-visible{outline:2px solid #2271b1;outline-offset:-3px}.h18-editor-accordion-body{padding:0 var(--h18-card-pad,20px) var(--h18-card-pad,20px)}' .
            '.h18-editor-card-grid{display:grid;grid-template-columns:repeat(var(--h18-grid-columns,3),minmax(0,1fr));gap:var(--h18-grid-gap,16px);align-items:stretch}.h18-editor-grid-card{box-sizing:border-box;padding:var(--h18-card-pad,26px);border:var(--h18-card-border-width,0) solid var(--h18-card-border,#c3ae83);border-radius:var(--h18-card-radius,7px);text-align:var(--h18-card-align,left)}.h18-editor-grid-card h3{margin:0 0 12px;color:inherit}.h18-editor-grid-card--white{background:#fff}.h18-editor-grid-card--offwhite{background:#f2f0e8}.h18-editor-grid-card--sand{background:#c3ae83}.h18-editor-grid-card--olive{background:#30382a}.h18-editor-grid-card--steel{background:#525a5f}.h18-editor-grid-card--tone-dark{color:#30382a}.h18-editor-grid-card--tone-light{color:#fff}.h18-editor-grid-card--tone-light h3{color:#fff}' .
"""
php = replace_once(php, css_anchor, css_new, 'frontend tabs css')

# Mobile panel/card padding also applies to tabs/accordion because panels reuse grid-card variables.
# Existing grid-card mobile CSS already targets .h18-editor-grid-card, so no extra migration is required.

# Admin title/content support.
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid highlight icon list badge quote html mail_form poll"',
    'data-types="hero text text_image image buttons card card_grid tabs accordion highlight icon list badge quote html mail_form poll"',
    'admin title types')
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid highlight icon list quote embed shortcode html css mail_form poll"',
    'data-types="hero text text_image image buttons card card_grid tabs accordion highlight icon list quote embed shortcode html css mail_form poll"',
    'admin content types')

admin_collection_old = """                    <div class=\"h18-section-type-field h18-section-module-box h18-card-grid-editor\" data-types=\"card_grid\">
                        <h4>Kort-række / kolonner</h4>
                        <p>Hver kasse kan flyttes, farves og tilpasses separat. På mobil placeres kasserne som standard under hinanden.</p>
                        <div class=\"h18-module-fields-grid h18-module-fields-grid--four\">
"""
admin_collection_new = """                    <div class=\"h18-section-type-field h18-section-module-box h18-card-grid-editor h18-collection-editor\" data-types=\"card_grid tabs accordion\">
                        <h4 class=\"h18-collection-editor-title\"><?php echo $section['Type'] === 'tabs' ? 'Faner / tabs' : ($section['Type'] === 'accordion' ? 'Accordion' : 'Kort-række / kolonner'); ?></h4>
                        <p class=\"h18-collection-editor-description\"><?php echo in_array($section['Type'], ['tabs','accordion'], true) ? 'Hvert panel bruger den eksisterende kassemodel og kan flyttes, farves og tilpasses separat.' : 'Hver kasse kan flyttes, farves og tilpasses separat. På mobil placeres kasserne som standard under hinanden.'; ?></p>
                        <div class=\"h18-module-fields-grid h18-module-fields-grid--four h18-card-grid-layout-fields\">
"""
php = replace_once(php, admin_collection_old, admin_collection_new, 'admin collection box')
php = replace_once(php,
    '<button class="button h18-add-page-card" type="button">Tilføj kasse</button>',
    '<button class="button h18-add-page-card" type="button"><span class="h18-add-page-card-label"><?php echo in_array($section[\'Type\'], [\'tabs\',\'accordion\'], true) ? \'Tilføj panel\' : \'Tilføj kasse\'; ?></span></button>',
    'add panel button')

# JS labels and collection helpers.
js_labels_old = """            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',
            spacer: 'Afstand', html: 'Importeret blok / HTML', css: 'Side-CSS', mail_form: 'Mailformular', poll: 'Afstemning', legacy: 'Eksisterende indhold'
"""
js_labels_new = """            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', tabs: 'Faner / tabs', accordion: 'Accordion', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',
            spacer: 'Afstand', html: 'Importeret blok / HTML', css: 'Side-CSS', mail_form: 'Mailformular', poll: 'Afstemning', legacy: 'Eksisterende indhold'
"""
js = replace_once(js, js_labels_old, js_labels_new, 'inspector labels')

refresh_labels_old = """            card_grid: 'Kort-række / kolonner',
            highlight: 'Fremhævet tekst',
            spacer: 'Afstand',
"""
refresh_labels_new = """            card_grid: 'Kort-række / kolonner',
            tabs: 'Faner / tabs',
            accordion: 'Accordion',
            highlight: 'Fremhævet tekst',
            spacer: 'Afstand',
"""
js = replace_once(js, refresh_labels_old, refresh_labels_new, 'refresh labels')

# Reusable presets with Cards work for all collection types.
js = replace_once(js,
    "if (Array.isArray(presetData.Cards) && type === 'card_grid') {",
    "if (Array.isArray(presetData.Cards) && ['card_grid', 'tabs', 'accordion'].includes(type)) {",
    'preset card collections')

collection_helper_anchor = """    function refreshPageSectionType($row) {
"""
collection_helper = r'''    function refreshCollectionEditorV0517($row) {
        if (!$row || !$row.length) { return; }
        const type = String($row.attr('data-section-type') || 'text');
        const $box = pageSectionControls($row, '.h18-collection-editor');
        if (!$box.length) { return; }
        const isCards = type === 'card_grid';
        const isTabs = type === 'tabs';
        const isAccordion = type === 'accordion';
        $box.find('.h18-card-grid-layout-fields').toggle(isCards);
        $box.find('.h18-collection-editor-title').text(isTabs ? 'Faner / tabs' : (isAccordion ? 'Accordion' : 'Kort-række / kolonner'));
        $box.find('.h18-collection-editor-description').text(isTabs
            ? 'Hvert panel bliver en fane. Titel er fanetekst; indhold er fanens panel.'
            : (isAccordion ? 'Hvert panel bliver et fold-ud punkt med titel og indhold.' : 'Hver kasse kan flyttes, farves og tilpasses separat.'));
        $box.find('.h18-add-page-card-label').text(isCards ? 'Tilføj kasse' : 'Tilføj panel');
    }

    function initializeCollectionPanelsV0517($row, type) {
        if (!['tabs', 'accordion'].includes(type)) { return; }
        if (pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) { return; }
        const prefix = type === 'tabs' ? 'Fane' : 'Punkt';
        addPageCard($row, { Title: prefix + ' 1', Content: '<p>Indhold til ' + prefix.toLowerCase() + ' 1.</p>', Background: 'White', TextTone: 'Auto', Active: true });
        addPageCard($row, { Title: prefix + ' 2', Content: '<p>Indhold til ' + prefix.toLowerCase() + ' 2.</p>', Background: 'OffWhite', TextTone: 'Auto', Active: true });
    }

'''
js = replace_once(js, collection_helper_anchor, collection_helper + collection_helper_anchor, 'collection helpers')

refresh_tail_old = """        refreshHoverStyleMode($row);
        refreshPrimitiveVariantV0516($row);
        rebuildPageNavigator();
"""
refresh_tail_new = """        refreshHoverStyleMode($row);
        refreshPrimitiveVariantV0516($row);
        refreshCollectionEditorV0517($row);
        rebuildPageNavigator();
"""
js = replace_once(js, refresh_tail_old, refresh_tail_new, 'collection refresh hook')

# New defaults and type-change initialization.
defaults_anchor = """        } else if (type === 'card_grid') {
            setValue('Background', 'White');
"""
defaults_new = """        } else if (type === 'tabs' || type === 'accordion') {
            setValue('Background', 'White');
            setValue('PaddingPx', 0);
            setValue('HorizontalPaddingPx', 0);
            setValue('MobilePaddingPx', 0);
            setValue('MobileHorizontalPaddingPx', 0);
            initializeCollectionPanelsV0517($row, type);
        } else if (type === 'card_grid') {
            setValue('Background', 'White');
"""
js = replace_once(js, defaults_anchor, defaults_new, 'collection defaults')

change_old = """        if (type === 'card_grid' && !pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) {
            applyNewSectionDefaults($row, type);
        }
        refreshPageSectionType($row);
"""
change_new = """        if (['card_grid', 'tabs', 'accordion'].includes(type) && !pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length) {
            applyNewSectionDefaults($row, type);
        }
        refreshPageSectionType($row);
"""
js = replace_once(js, change_old, change_new, 'type change init')

add_card_old = """    $(document).on('click', '.h18-add-page-card', function (event) {
        event.preventDefault();
        addPageCard(pageSectionForElement(this), { Title: 'Ny kasse', Background: 'OffWhite', TextTone: 'Auto', Active: true });
    });
"""
add_card_new = """    $(document).on('click', '.h18-add-page-card', function (event) {
        event.preventDefault();
        const $row = pageSectionForElement(this);
        const type = String($row.attr('data-section-type') || 'card_grid');
        const current = pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').length + 1;
        const title = type === 'tabs' ? 'Fane ' + current : (type === 'accordion' ? 'Punkt ' + current : 'Ny kasse');
        addPageCard($row, { Title: title, Background: 'OffWhite', TextTone: 'Auto', Active: true });
    });
"""
js = replace_once(js, add_card_old, add_card_new, 'collection add panel')

# Canvas previews before card_grid. Use current Cards DOM so unsaved edits are shown.
canvas_anchor = """        } else if (type === 'card_grid') {
            addTitle('Kort-række');
"""
canvas_collection = r'''        } else if (type === 'tabs') {
            addTitle('Faner');
            canvasAddBodyText($inner, content);
            const $cards = pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').filter(function () { return $(this).find('[name$="[Active]"]').is(':checked'); });
            const $tabs = $('<div>', { class: 'h18-canvas-tabs-nav' });
            const $panel = $('<div>', { class: 'h18-canvas-tabs-panel' });
            if (!$cards.length) { $panel.text('Tilføj mindst ét panel.'); }
            $cards.each(function (index) {
                const $card = $(this);
                const cardTitle = String($card.find('.h18-page-card-title').val() || ('Fane ' + (index + 1)));
                $tabs.append($('<button>', { type: 'button', class: 'h18-canvas-tab' + (index === 0 ? ' is-active' : ''), text: cardTitle, tabindex: -1 }));
                if (index === 0) { $panel.html(String($card.find('[name$="[Content]"]').val() || '')); }
            });
            $inner.append($tabs, $panel);
        } else if (type === 'accordion') {
            addTitle('Accordion');
            canvasAddBodyText($inner, content);
            const $accordion = $('<div>', { class: 'h18-canvas-accordion' });
            pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').filter(function () { return $(this).find('[name$="[Active]"]').is(':checked'); }).each(function (index) {
                const $card = $(this);
                const cardTitle = String($card.find('.h18-page-card-title').val() || ('Punkt ' + (index + 1)));
                const $item = $('<div>', { class: 'h18-canvas-accordion-item' });
                $item.append($('<strong>', { text: cardTitle }), $('<span>', { text: index === 0 ? '−' : '+' }));
                if (index === 0) { $item.append($('<div>', { class: 'h18-canvas-accordion-body' }).html(String($card.find('[name$="[Content]"]').val() || ''))); }
                $accordion.append($item);
            });
            $inner.append($accordion);
        } else if (type === 'card_grid') {
            addTitle('Kort-række');
'''
js = replace_once(js, canvas_anchor, canvas_collection, 'canvas tabs accordion')

css_block = r'''

/* v0.5.17 – Tabs + Accordion canvas */
.h18-canvas-tabs-nav{display:flex;gap:5px;flex-wrap:wrap;border-bottom:1px solid rgba(0,0,0,.2)}
.h18-canvas-tab{appearance:none;border:1px solid transparent;border-bottom:0;border-radius:5px 5px 0 0;background:transparent;padding:7px 11px;font-weight:700;color:inherit}
.h18-canvas-tab.is-active{background:rgba(255,255,255,.85);color:#30382a;border-color:rgba(0,0,0,.2)}
.h18-canvas-tabs-panel{padding:16px;border:1px solid rgba(0,0,0,.15);border-top:0;background:rgba(255,255,255,.55)}
.h18-canvas-accordion{display:grid;gap:7px}.h18-canvas-accordion-item{display:grid;grid-template-columns:1fr auto;gap:8px;padding:11px 13px;border:1px solid rgba(0,0,0,.16);border-radius:5px}.h18-canvas-accordion-body{grid-column:1/-1;padding-top:8px;border-top:1px solid rgba(0,0,0,.12)}
'''
if '/* v0.5.17 – Tabs + Accordion canvas */' in css:
    raise SystemExit('v0.5.17 CSS already present')
css = css.rstrip() + css_block + '\n'

readme = replace_once(readme, 'Version: 0.5.16', 'Version: 0.5.17', 'readme version')
readme_anchor = '== Version 0.5.16 – E2 element primitives og sikre embeds ==\n'
readme_new = """== Version 0.5.17 – Tabs og Accordion ==

Nyt:
- UD-030: nye Faner/Tabs og Accordion-elementer direkte i sidebyggeren
- begge elementer genbruger den eksisterende Cards/panel-model, så komponenter, Undo/Redo, autosave og copy/paste fortsætter uden parallel datamodel
- Tabs har semantisk tablist/tab/tabpanel-markup, roving tabindex og tastaturstyring med pile, Home og End
- Accordion bruger native details/summary for robust keyboard- og skærmlæserunderstøttelse
- paneler kan flyttes, aktiveres/deaktiveres og beholder eksisterende baggrund, teksttone, kant, padding, radius og responsive Card-indstillinger
- nye Tabs/Accordion oprettes med to startpaneler og kan have op til 12 paneler
- live canvas viser den første fane eller det første accordion-panel uden at ændre frontend-state
- page-editor schema forbliver 1.13; ingen ekstra paneldatamigrering er nødvendig

""" + readme_anchor
readme = replace_once(readme, readme_anchor, readme_new, 'readme v0.5.16 anchor')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
print('v0.5.17 patch applied')
