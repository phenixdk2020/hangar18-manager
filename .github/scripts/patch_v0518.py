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

php = replace_once(php, ' * Version: 0.5.17', ' * Version: 0.5.18', 'plugin header')
php = replace_once(php, "    const VERSION = '0.5.17';", "    const VERSION = '0.5.18';", 'plugin const')

labels_old = """            'tabs'       => 'Faner / tabs',
            'accordion'  => 'Accordion',
            'embed'      => 'Embed / medie-URL',
"""
labels_new = """            'tabs'       => 'Faner / tabs',
            'accordion'  => 'Accordion',
            'carousel'   => 'Carousel / slider',
            'embed'      => 'Embed / medie-URL',
"""
php = replace_once(php, labels_old, labels_new, 'carousel type label')

# Persist carousel behavior in schema 1.14.
default_anchor = """            'Cards'                 => [],
            'TopSpacingPx'          => 0,
"""
default_new = """            'Cards'                 => [],
            'CarouselAutoplay'      => false,
            'CarouselIntervalMs'    => 5000,
            'CarouselLoop'          => true,
            'CarouselShowArrows'    => true,
            'CarouselShowDots'      => true,
            'TopSpacingPx'          => 0,
"""
php = replace_once(php, default_anchor, default_new, 'carousel defaults')

return_cards_anchor = """            'Cards'                  => $cards,
            'TopSpacingPx'           => $this->clamp_int($raw['TopSpacingPx'] ?? 0, 0, 160, 0),
"""
return_cards_new = """            'Cards'                  => $cards,
            'CarouselAutoplay'       => array_key_exists('CarouselAutoplay', $raw) ? $this->bool_value($raw['CarouselAutoplay'], false) : false,
            'CarouselIntervalMs'     => $this->clamp_int($raw['CarouselIntervalMs'] ?? 5000, 2000, 20000, 5000),
            'CarouselLoop'           => array_key_exists('CarouselLoop', $raw) ? $this->bool_value($raw['CarouselLoop'], true) : true,
            'CarouselShowArrows'     => array_key_exists('CarouselShowArrows', $raw) ? $this->bool_value($raw['CarouselShowArrows'], true) : true,
            'CarouselShowDots'       => array_key_exists('CarouselShowDots', $raw) ? $this->bool_value($raw['CarouselShowDots'], true) : true,
            'TopSpacingPx'           => $this->clamp_int($raw['TopSpacingPx'] ?? 0, 0, 160, 0),
"""
php = replace_once(php, return_cards_anchor, return_cards_new, 'carousel normalize fields')

if php.count("'Version'        => '1.13'") != 3:
    raise SystemExit("Expected exactly 3 active page schema 1.13 payloads")
php = php.replace("'Version'        => '1.13'", "'Version'        => '1.14'")
php = php.replace("'Version' => '1.13',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,", "'Version' => '1.14',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php = php.replace("'Version' => '1.13',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,", "'Version' => '1.14',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

# Static, safe carousel behavior helper. Data stays in HTML data attributes.
helper_anchor = """    private function page_editor_tabs_script($section_id) {
"""
carousel_helper = r'''    private function page_editor_carousel_script($section_id) {
        $root_json = wp_json_encode((string) $section_id);
        return '<script>(function(){' .
            'var section=document.getElementById(' . $root_json . ');if(!section)return;var root=section.querySelector(".h18-editor-carousel");if(!root)return;' .
            'var slides=Array.prototype.slice.call(root.querySelectorAll(".h18-editor-carousel-slide"));var dots=Array.prototype.slice.call(root.querySelectorAll(".h18-editor-carousel-dot"));var prev=root.querySelector(".h18-editor-carousel-prev");var next=root.querySelector(".h18-editor-carousel-next");var status=root.querySelector(".h18-editor-carousel-status");if(!slides.length)return;' .
            'var index=0;var timer=null;var startX=null;var loop=root.dataset.loop==="1";var autoplay=root.dataset.autoplay==="1";var interval=Math.max(2000,parseInt(root.dataset.interval||"5000",10)||5000);var reduced=window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;' .
            'function normalize(i){if(loop)return(i+slides.length)%slides.length;return Math.max(0,Math.min(slides.length-1,i));}' .
            'function show(i,user){index=normalize(i);slides.forEach(function(slide,n){var on=n===index;slide.hidden=!on;slide.setAttribute("aria-hidden",on?"false":"true");});dots.forEach(function(dot,n){var on=n===index;dot.setAttribute("aria-current",on?"true":"false");dot.tabIndex=on?0:-1;});if(prev)prev.disabled=!loop&&index===0;if(next)next.disabled=!loop&&index===slides.length-1;if(status)status.textContent=(index+1)+" af "+slides.length;if(user)restart();}' .
            'function advance(step,user){show(index+step,user);}' .
            'function stop(){if(timer){window.clearInterval(timer);timer=null;}}function restart(){stop();if(autoplay&&!reduced&&slides.length>1)timer=window.setInterval(function(){if(loop||index<slides.length-1)advance(1,false);else show(0,false);},interval);}' .
            'if(prev)prev.addEventListener("click",function(){advance(-1,true);});if(next)next.addEventListener("click",function(){advance(1,true);});dots.forEach(function(dot,n){dot.addEventListener("click",function(){show(n,true);});dot.addEventListener("keydown",function(e){var target=n;if(e.key==="ArrowRight")target=n+1;else if(e.key==="ArrowLeft")target=n-1;else if(e.key==="Home")target=0;else if(e.key==="End")target=dots.length-1;else return;e.preventDefault();show(target,true);dots[normalize(target)].focus();});});' .
            'root.addEventListener("keydown",function(e){if(e.target&&e.target.classList.contains("h18-editor-carousel-dot"))return;if(e.key==="ArrowRight"){e.preventDefault();advance(1,true);}else if(e.key==="ArrowLeft"){e.preventDefault();advance(-1,true);}});root.addEventListener("mouseenter",stop);root.addEventListener("mouseleave",restart);root.addEventListener("focusin",stop);root.addEventListener("focusout",function(e){if(!root.contains(e.relatedTarget))restart();});' .
            'root.addEventListener("touchstart",function(e){startX=e.touches&&e.touches[0]?e.touches[0].clientX:null;},{passive:true});root.addEventListener("touchend",function(e){if(startX===null)return;var end=e.changedTouches&&e.changedTouches[0]?e.changedTouches[0].clientX:startX;var dx=end-startX;startX=null;if(Math.abs(dx)>45)advance(dx<0?1:-1,true);},{passive:true});show(0,false);restart();' .
            '})();</script>';
    }

'''
php = replace_once(php, helper_anchor, carousel_helper + helper_anchor, 'carousel script helper')

# Frontend renderer before tabs/accordion branch.
collection_anchor = """        } elseif (in_array($section['Type'], ['tabs', 'accordion'], true)) {
            $border_colors = [
"""
carousel_renderer = r'''        } elseif ($section['Type'] === 'carousel') {
            $border_colors = ['None'=>'transparent','Sand'=>'#c3ae83','Olive'=>'#30382a','Steel'=>'#525a5f'];
            $items = [];
            foreach ((array) $section['Cards'] as $card) { if (!empty($card['Active'])) { $items[] = $card; } }
            $slides = '';
            $dots = '';
            $slide_count = count($items);
            foreach ($items as $item_index => $card) {
                $tone = (string) $card['TextTone'];
                if ($tone === 'Auto') { $tone = in_array($card['Background'], ['Olive','Steel'], true) ? 'Light' : 'Dark'; }
                $card_background = strtolower((string) $card['Background']);
                $card_border = $border_colors[$card['BorderColor']] ?? '#c3ae83';
                $card_style = '--h18-card-pad:' . (int) $card['PaddingPx'] . 'px;' .
                    '--h18-card-mobile-pad:' . (int) $card['MobilePaddingPx'] . 'px;' .
                    '--h18-card-radius:' . (int) $card['RadiusPx'] . 'px;' .
                    '--h18-card-border-width:' . (int) $card['BorderWidthPx'] . 'px;' .
                    '--h18-card-border:' . $card_border . ';' .
                    '--h18-card-align:' . ($card['DesktopAlignment'] === 'Center' ? 'center' : 'left') . ';' .
                    '--h18-card-mobile-align:' . ($card['MobileAlignment'] === 'Center' ? 'center' : 'left') . ';';
                $label = $card['Title'] !== '' ? (string) $card['Title'] : 'Slide ' . ($item_index + 1);
                $slides .= '<article class="h18-editor-carousel-slide h18-editor-grid-card h18-editor-grid-card--' . esc_attr($card_background) . ' h18-editor-grid-card--tone-' . esc_attr(strtolower($tone)) . '" style="' . esc_attr($card_style) . '" role="group" aria-roledescription="slide" aria-label="' . esc_attr(($item_index + 1) . ' af ' . $slide_count . ': ' . $label) . '" aria-hidden="' . ($item_index === 0 ? 'false' : 'true') . '"' . ($item_index === 0 ? '' : ' hidden') . '>' .
                    ($card['Title'] !== '' ? '<h3>' . esc_html($card['Title']) . '</h3>' : '') . $this->format_page_section_content($card['Content']) . '</article>';
                if (!empty($section['CarouselShowDots'])) {
                    $dots .= '<button type="button" class="h18-editor-carousel-dot" aria-label="Gå til slide ' . esc_attr($item_index + 1) . '" aria-current="' . ($item_index === 0 ? 'true' : 'false') . '" tabindex="' . ($item_index === 0 ? '0' : '-1') . '"></button>';
                }
            }
            $controls = '';
            if (!empty($section['CarouselShowArrows']) && $slide_count > 1) {
                $controls = '<button type="button" class="h18-editor-carousel-arrow h18-editor-carousel-prev" aria-label="Forrige slide">‹</button><button type="button" class="h18-editor-carousel-arrow h18-editor-carousel-next" aria-label="Næste slide">›</button>';
            }
            $dots_html = $dots !== '' ? '<div class="h18-editor-carousel-dots" role="group" aria-label="Vælg slide">' . $dots . '</div>' : '';
            $carousel_label = $section['Title'] !== '' ? (string) $section['Title'] : 'Carousel';
            $inner = $title . $content . '<div class="h18-editor-carousel" role="region" aria-roledescription="carousel" aria-label="' . esc_attr($carousel_label) . '" tabindex="0" data-autoplay="' . (!empty($section['CarouselAutoplay']) ? '1' : '0') . '" data-interval="' . (int) $section['CarouselIntervalMs'] . '" data-loop="' . (!empty($section['CarouselLoop']) ? '1' : '0') . '"><div class="h18-editor-carousel-viewport">' . $slides . '</div>' . $controls . $dots_html . '<span class="screen-reader-text h18-editor-carousel-status" aria-live="polite">' . ($slide_count > 0 ? '1 af ' . $slide_count : 'Ingen slides') . '</span></div>' . $this->page_editor_carousel_script($id);
        } elseif (in_array($section['Type'], ['tabs', 'accordion'], true)) {
            $border_colors = [
'''
php = replace_once(php, collection_anchor, carousel_renderer, 'carousel renderer')

# Frontend carousel CSS before tabs CSS.
css_anchor = """            '.h18-editor-tabs{display:grid;gap:0}.h18-editor-tabs-nav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:0;border-bottom:1px solid #c3c4c7}.h18-editor-tab{appearance:none;padding:10px 16px;border:1px solid transparent;border-bottom:0;border-radius:6px 6px 0 0;background:transparent;color:inherit;font:inherit;font-weight:700;cursor:pointer}' .
"""
# Current source has longer whole concatenated string, so replace only prefix.
if css_anchor not in php:
    short = "            '.h18-editor-tabs{display:grid;gap:0}"
    if short not in php:
        raise SystemExit('frontend tabs css anchor missing')
    carousel_css = "            '.h18-editor-carousel{position:relative;outline:none}.h18-editor-carousel:focus-visible{outline:2px solid #2271b1;outline-offset:4px}.h18-editor-carousel-viewport{position:relative;overflow:hidden}.h18-editor-carousel-slide[hidden]{display:none!important}.h18-editor-carousel-arrow{position:absolute;top:50%;z-index:2;display:grid;place-items:center;width:44px;height:44px;margin-top:-22px;border:1px solid rgba(0,0,0,.18);border-radius:999px;background:rgba(255,255,255,.92);color:#30382a;font-size:30px;line-height:1;cursor:pointer}.h18-editor-carousel-arrow:focus-visible{outline:2px solid #2271b1;outline-offset:2px}.h18-editor-carousel-arrow:disabled{opacity:.35;cursor:not-allowed}.h18-editor-carousel-prev{left:12px}.h18-editor-carousel-next{right:12px}.h18-editor-carousel-dots{display:flex;justify-content:center;gap:8px;margin-top:12px}.h18-editor-carousel-dot{width:12px;height:12px;padding:0;border:1px solid currentColor;border-radius:999px;background:transparent;cursor:pointer}.h18-editor-carousel-dot[aria-current=true]{background:currentColor}.h18-editor-carousel-dot:focus-visible{outline:2px solid #2271b1;outline-offset:3px}@media(prefers-reduced-motion:reduce){.h18-editor-carousel *{scroll-behavior:auto!important;animation:none!important;transition:none!important}}' .\n" + short
    php = php.replace(short, carousel_css, 1)
else:
    carousel_css = "            '.h18-editor-carousel{position:relative;outline:none}.h18-editor-carousel:focus-visible{outline:2px solid #2271b1;outline-offset:4px}.h18-editor-carousel-viewport{position:relative;overflow:hidden}.h18-editor-carousel-slide[hidden]{display:none!important}.h18-editor-carousel-arrow{position:absolute;top:50%;z-index:2;display:grid;place-items:center;width:44px;height:44px;margin-top:-22px;border:1px solid rgba(0,0,0,.18);border-radius:999px;background:rgba(255,255,255,.92);color:#30382a;font-size:30px;line-height:1;cursor:pointer}.h18-editor-carousel-arrow:focus-visible{outline:2px solid #2271b1;outline-offset:2px}.h18-editor-carousel-arrow:disabled{opacity:.35;cursor:not-allowed}.h18-editor-carousel-prev{left:12px}.h18-editor-carousel-next{right:12px}.h18-editor-carousel-dots{display:flex;justify-content:center;gap:8px;margin-top:12px}.h18-editor-carousel-dot{width:12px;height:12px;padding:0;border:1px solid currentColor;border-radius:999px;background:transparent;cursor:pointer}.h18-editor-carousel-dot[aria-current=true]{background:currentColor}.h18-editor-carousel-dot:focus-visible{outline:2px solid #2271b1;outline-offset:3px}@media(prefers-reduced-motion:reduce){.h18-editor-carousel *{scroll-behavior:auto!important;animation:none!important;transition:none!important}}' .\n" + css_anchor
    php = php.replace(css_anchor, carousel_css, 1)

# Admin: carousel uses title/content and existing collection editor.
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid tabs accordion highlight icon list badge quote html mail_form poll"',
    'data-types="hero text text_image image buttons card card_grid tabs accordion carousel highlight icon list badge quote html mail_form poll"',
    'admin title types')
php = replace_once(php,
    'data-types="hero text text_image image buttons card card_grid tabs accordion highlight icon list quote embed shortcode html css mail_form poll"',
    'data-types="hero text text_image image buttons card card_grid tabs accordion carousel highlight icon list quote embed shortcode html css mail_form poll"',
    'admin content types')
php = replace_once(php,
    'data-types="card_grid tabs accordion">',
    'data-types="card_grid tabs accordion carousel">',
    'collection admin types')

# Insert behavior controls before collection editor.
collection_admin_anchor = """                    <div class=\"h18-section-type-field h18-section-module-box h18-card-grid-editor h18-collection-editor\" data-types=\"card_grid tabs accordion carousel\">
"""
carousel_admin = """                    <div class=\"h18-section-type-field h18-section-module-box\" data-types=\"carousel\">
                        <h4>Carousel / slider</h4>
                        <p>Autoplay er FRA som standard. Reduced Motion i brugerens system slår automatisk autoplay fra.</p>
                        <div class=\"h18-module-fields-grid h18-module-fields-grid--four\">
                            <label><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[CarouselAutoplay]\" value=\"1\" <?php checked(!empty($section['CarouselAutoplay'])); ?> /> <strong>Autoplay</strong></label>
                            <div class=\"h18-field\"><label><strong>Interval (ms)</strong></label><input type=\"number\" min=\"2000\" max=\"20000\" step=\"250\" name=\"<?php echo esc_attr($prefix); ?>[CarouselIntervalMs]\" value=\"<?php echo esc_attr($section['CarouselIntervalMs']); ?>\" /></div>
                            <label><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[CarouselLoop]\" value=\"1\" <?php checked(!empty($section['CarouselLoop'])); ?> /> <strong>Loop</strong></label>
                            <label><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[CarouselShowArrows]\" value=\"1\" <?php checked(!empty($section['CarouselShowArrows'])); ?> /> <strong>Vis pile</strong></label>
                            <label><input type=\"checkbox\" name=\"<?php echo esc_attr($prefix); ?>[CarouselShowDots]\" value=\"1\" <?php checked(!empty($section['CarouselShowDots'])); ?> /> <strong>Vis priknavigation</strong></label>
                        </div>
                    </div>

""" + collection_admin_anchor
php = replace_once(php, collection_admin_anchor, carousel_admin, 'carousel admin behavior')

# Collection server-side labels include carousel.
php = replace_once(php,
    "<?php echo $section['Type'] === 'tabs' ? 'Faner / tabs' : ($section['Type'] === 'accordion' ? 'Accordion' : 'Kort-række / kolonner'); ?>",
    "<?php echo $section['Type'] === 'tabs' ? 'Faner / tabs' : ($section['Type'] === 'accordion' ? 'Accordion' : ($section['Type'] === 'carousel' ? 'Carousel / slider' : 'Kort-række / kolonner')); ?>",
    'collection heading server')
php = replace_once(php,
    "<?php echo in_array($section['Type'], ['tabs','accordion'], true) ? 'Hvert panel bruger den eksisterende kassemodel og kan flyttes, farves og tilpasses separat.' : 'Hver kasse kan flyttes, farves og tilpasses separat. På mobil placeres kasserne som standard under hinanden.'; ?>",
    "<?php echo in_array($section['Type'], ['tabs','accordion','carousel'], true) ? 'Hvert panel bruger den eksisterende kassemodel og kan flyttes, farves og tilpasses separat.' : 'Hver kasse kan flyttes, farves og tilpasses separat. På mobil placeres kasserne som standard under hinanden.'; ?>",
    'collection desc server')
php = replace_once(php,
    "<?php echo in_array($section['Type'], ['tabs','accordion'], true) ? 'Tilføj panel' : 'Tilføj kasse'; ?>",
    "<?php echo in_array($section['Type'], ['tabs','accordion','carousel'], true) ? 'Tilføj panel' : 'Tilføj kasse'; ?>",
    'collection add label server')

# JS labels.
js = replace_once(js,
    "tabs: 'Faner / tabs', accordion: 'Accordion', embed: 'Embed / medie-URL'",
    "tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', embed: 'Embed / medie-URL'",
    'inspector carousel label')
js = replace_once(js,
    "            accordion: 'Accordion',\n            highlight: 'Fremhævet tekst',",
    "            accordion: 'Accordion',\n            carousel: 'Carousel / slider',\n            highlight: 'Fremhævet tekst',",
    'refresh carousel label')

# Reusable presets include carousel cards.
js = replace_once(js,
    "['card_grid', 'tabs', 'accordion'].includes(type)",
    "['card_grid', 'tabs', 'accordion', 'carousel'].includes(type)",
    'preset carousel cards')

# Collection editor dynamic labels and initialization.
helper_old = """        const isCards = type === 'card_grid';
        const isTabs = type === 'tabs';
        const isAccordion = type === 'accordion';
        $box.find('.h18-card-grid-layout-fields').toggle(isCards);
        $box.find('.h18-collection-editor-title').text(isTabs ? 'Faner / tabs' : (isAccordion ? 'Accordion' : 'Kort-række / kolonner'));
        $box.find('.h18-collection-editor-description').text(isTabs
            ? 'Hvert panel bliver en fane. Titel er fanetekst; indhold er fanens panel.'
            : (isAccordion ? 'Hvert panel bliver et fold-ud punkt med titel og indhold.' : 'Hver kasse kan flyttes, farves og tilpasses separat.'));
        $box.find('.h18-add-page-card-label').text(isCards ? 'Tilføj kasse' : 'Tilføj panel');
"""
helper_new = """        const isCards = type === 'card_grid';
        const isTabs = type === 'tabs';
        const isAccordion = type === 'accordion';
        const isCarousel = type === 'carousel';
        $box.find('.h18-card-grid-layout-fields').toggle(isCards);
        $box.find('.h18-collection-editor-title').text(isTabs ? 'Faner / tabs' : (isAccordion ? 'Accordion' : (isCarousel ? 'Carousel / slider' : 'Kort-række / kolonner')));
        $box.find('.h18-collection-editor-description').text(isTabs
            ? 'Hvert panel bliver en fane. Titel er fanetekst; indhold er fanens panel.'
            : (isAccordion ? 'Hvert panel bliver et fold-ud punkt med titel og indhold.' : (isCarousel ? 'Hvert panel bliver et slide. Titel, indhold og Card-design følger slidet.' : 'Hver kasse kan flyttes, farves og tilpasses separat.')));
        $box.find('.h18-add-page-card-label').text(isCards ? 'Tilføj kasse' : 'Tilføj panel');
"""
js = replace_once(js, helper_old, helper_new, 'collection carousel helper')
js = replace_once(js,
    "if (!['tabs', 'accordion'].includes(type)) { return; }",
    "if (!['tabs', 'accordion', 'carousel'].includes(type)) { return; }",
    'initialize carousel collection')
js = replace_once(js,
    "const prefix = type === 'tabs' ? 'Fane' : 'Punkt';",
    "const prefix = type === 'tabs' ? 'Fane' : (type === 'carousel' ? 'Slide' : 'Punkt');",
    'carousel initial prefix')

# Defaults + type change + add card.
defaults_anchor = """        } else if (type === 'tabs' || type === 'accordion') {
            setValue('Background', 'White');
"""
defaults_new = """        } else if (type === 'carousel') {
            setValue('Background', 'White');
            setValue('PaddingPx', 0);
            setValue('HorizontalPaddingPx', 0);
            setValue('MobilePaddingPx', 0);
            setValue('MobileHorizontalPaddingPx', 0);
            setValue('CarouselIntervalMs', 5000);
            pageSectionControls($row, '[name$=\"[CarouselAutoplay]\"]').prop('checked', false);
            pageSectionControls($row, '[name$=\"[CarouselLoop]\"]').prop('checked', true);
            pageSectionControls($row, '[name$=\"[CarouselShowArrows]\"]').prop('checked', true);
            pageSectionControls($row, '[name$=\"[CarouselShowDots]\"]').prop('checked', true);
            initializeCollectionPanelsV0517($row, type);
        } else if (type === 'tabs' || type === 'accordion') {
            setValue('Background', 'White');
"""
js = replace_once(js, defaults_anchor, defaults_new, 'carousel defaults js')
js = replace_once(js,
    "['card_grid', 'tabs', 'accordion'].includes(type) &&",
    "['card_grid', 'tabs', 'accordion', 'carousel'].includes(type) &&",
    'carousel type change')
js = replace_once(js,
    "const title = type === 'tabs' ? 'Fane ' + current : (type === 'accordion' ? 'Punkt ' + current : 'Ny kasse');",
    "const title = type === 'tabs' ? 'Fane ' + current : (type === 'accordion' ? 'Punkt ' + current : (type === 'carousel' ? 'Slide ' + current : 'Ny kasse'));",
    'carousel add slide label')

# Canvas carousel before tabs.
canvas_anchor = """        } else if (type === 'tabs') {
            addTitle('Faner');
"""
canvas_carousel = r'''        } else if (type === 'carousel') {
            addTitle('Carousel');
            canvasAddBodyText($inner, content);
            const $slides = pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').filter(function () { return $(this).find('[name$="[Active]"]').is(':checked'); });
            const $carousel = $('<div>', { class: 'h18-canvas-carousel' });
            const $stage = $('<div>', { class: 'h18-canvas-carousel-stage' });
            if ($slides.length) {
                const $card = $slides.first();
                const cardTitle = String($card.find('.h18-page-card-title').val() || 'Slide 1');
                $stage.append($('<strong>', { text: cardTitle }), $('<div>', { class: 'h18-canvas-carousel-body' }).html(String($card.find('[name$="[Content]"]').val() || '')));
            } else {
                $stage.text('Tilføj mindst ét slide.');
            }
            const showArrows = Boolean(canvasFieldValue($row, 'CarouselShowArrows', true));
            const showDots = Boolean(canvasFieldValue($row, 'CarouselShowDots', true));
            if (showArrows && $slides.length > 1) { $carousel.append($('<span>', { class: 'h18-canvas-carousel-arrow is-prev', text: '‹' })); }
            $carousel.append($stage);
            if (showArrows && $slides.length > 1) { $carousel.append($('<span>', { class: 'h18-canvas-carousel-arrow is-next', text: '›' })); }
            if (showDots && $slides.length > 1) {
                const $dots = $('<div>', { class: 'h18-canvas-carousel-dots' });
                $slides.each(function (i) { $dots.append($('<span>', { class: 'h18-canvas-carousel-dot' + (i === 0 ? ' is-active' : '') })); });
                $carousel.append($dots);
            }
            $inner.append($carousel);
        } else if (type === 'tabs') {
            addTitle('Faner');
'''
js = replace_once(js, canvas_anchor, canvas_carousel, 'canvas carousel')

css_block = r'''

/* v0.5.18 – Carousel canvas */
.h18-canvas-carousel{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:8px}
.h18-canvas-carousel-stage{min-height:120px;padding:18px;border:1px solid rgba(0,0,0,.16);border-radius:7px;background:rgba(255,255,255,.58)}
.h18-canvas-carousel-body{margin-top:8px}.h18-canvas-carousel-arrow{display:grid;place-items:center;width:32px;height:32px;border:1px solid rgba(0,0,0,.18);border-radius:999px;background:rgba(255,255,255,.9);color:#30382a;font-size:24px}
.h18-canvas-carousel-dots{grid-column:1/-1;display:flex;justify-content:center;gap:6px}.h18-canvas-carousel-dot{width:8px;height:8px;border:1px solid currentColor;border-radius:50%}.h18-canvas-carousel-dot.is-active{background:currentColor}
'''
if '/* v0.5.18 – Carousel canvas */' in css:
    raise SystemExit('v0.5.18 CSS already present')
css = css.rstrip() + css_block + '\n'

readme = replace_once(readme, 'Version: 0.5.17', 'Version: 0.5.18', 'readme version')
readme_anchor = '== Version 0.5.17 – Tabs og Accordion ==\n'
readme_new = """== Version 0.5.18 – Carousel / Slider ==

Nyt:
- UD-031: Carousel/Slider som native sideeditor-element og med den eksisterende Cards-model som slides
- autoplay er FRA som standard og kan aktiveres med justerbart interval 2-20 sekunder
- loop, forrige/næste-pile og priknavigation kan slås til/fra separat
- keyboard-navigation med venstre/højre pil samt Home/End på priknavigationen
- touch swipe på mobil og tablet; swipe kræver mindst ca. 45 px bevægelse
- autoplay pauser ved hover og keyboard-fokus og genstarter først, når brugeren forlader carousellen
- prefers-reduced-motion deaktiverer autoplay og transitions automatisk
- slides bruger role=group/aria-roledescription=slide, live status og skjuler inaktive slides fra fokus/assistive tech
- hvert slide bevarer Card-baggrund, teksttone, kant, padding, radius og responsive indstillinger
- page-editor schema løftes bagudkompatibelt til 1.14 for carousel-adfærd

""" + readme_anchor
readme = replace_once(readme, readme_anchor, readme_new, 'readme v0.5.17 anchor')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
print('v0.5.18 patch applied')
