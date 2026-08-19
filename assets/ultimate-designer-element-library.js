jQuery(function ($) {
    'use strict';

    const $panel = $('.h18-builder-sidebar-panel[data-builder-panel="elements"]');
    const $list = $panel.find('.h18-builder-palette-list').first();
    if (!$panel.length || !$list.length) {
        return;
    }

    const storageKey = 'hangar18UltimateDesignerElementFavoritesV087';
    const recentStorageKey = 'hangar18UltimateDesignerElementRecentV087';
    const recentLimit = 8;
    const categories = {
        hero: 'content', text: 'content', text_image: 'content', image: 'content', buttons: 'content',
        card: 'content', card_grid: 'content', highlight: 'content', icon: 'content', list: 'content',
        badge: 'content', quote: 'content',
        container: 'layout', flex: 'layout', grid: 'layout', spacer: 'layout', divider: 'layout',
        tabs: 'interactive', accordion: 'interactive', carousel: 'interactive', mail_form: 'interactive', poll: 'interactive',
        query_list: 'dynamic', component: 'dynamic', embed: 'dynamic', shortcode: 'dynamic',
        html: 'advanced', css: 'advanced'
    };
    const categoryLabels = {
        content: 'Indhold', layout: 'Layout', interactive: 'Interaktiv', dynamic: 'Dynamisk', advanced: 'Avanceret', other: 'Andet'
    };
    const descriptions = {
        hero: 'Stor introsektion med overskrift og call-to-action.',
        text: 'Tekstblok til afsnit, overskrifter og almindeligt indhold.',
        text_image: 'Kombinér tekst og billede i samme element.',
        image: 'Indsæt og tilpas et billede.',
        buttons: 'En eller flere handlingsknapper.',
        card: 'Indholdskort med eget visuelt udtryk.',
        card_grid: 'Flere kort i et responsivt grid.',
        highlight: 'Fremhæv vigtig tekst eller et budskab.',
        icon: 'Ikon med valgfri tekst.',
        list: 'Vis punkter eller struktureret indhold som liste.',
        badge: 'Lille mærkat eller statuslabel.',
        quote: 'Citat eller fremhævet udsagn.',
        container: 'Kasse/container som kan indeholde andre elementer.',
        flex: 'Fleksibel række eller kolonne til under-elementer.',
        grid: 'Responsivt kolonne-layout til under-elementer.',
        spacer: 'Kontrollerbar tom afstand mellem elementer.',
        divider: 'Visuel skillelinje mellem sektioner.',
        tabs: 'Indhold fordelt i klikbare faner.',
        accordion: 'Sammenklappelige indholdssektioner.',
        carousel: 'Bladr mellem flere indholdselementer.',
        mail_form: 'Formular til kontakt eller mailhenvendelser.',
        poll: 'Afstemning med valgmuligheder.',
        query_list: 'Dynamisk liste fra en datakilde.',
        component: 'Genbrugelig komponent med definerede inputs.',
        embed: 'Indlejret eksternt indhold.',
        shortcode: 'Kør et WordPress-shortcode.',
        html: 'Avanceret HTML-indhold.',
        css: 'Avanceret CSS til målrettet styling.'
    };
    const toolDescriptions = {
        'auto-row': 'Række med automatisk lige brede kasser og styrbar spacing.',
        box: 'Individuel kasse med egne farver, skrift, padding og hjørner.',
        table: 'Visuel tabel med rækker, kolonner, farver og mobiladfærd.'
    };
    const iconClasses = {
        hero: 'dashicons-cover-image', text: 'dashicons-text', text_image: 'dashicons-format-image', image: 'dashicons-format-image',
        buttons: 'dashicons-button', card: 'dashicons-index-card', card_grid: 'dashicons-grid-view', highlight: 'dashicons-star-filled',
        icon: 'dashicons-marker', list: 'dashicons-list-view', badge: 'dashicons-tag', quote: 'dashicons-format-quote',
        container: 'dashicons-align-wide', flex: 'dashicons-editor-justify', grid: 'dashicons-columns', spacer: 'dashicons-editor-expand',
        divider: 'dashicons-minus', tabs: 'dashicons-index-card', accordion: 'dashicons-menu-alt3', carousel: 'dashicons-images-alt2',
        mail_form: 'dashicons-email', poll: 'dashicons-chart-bar', query_list: 'dashicons-database-view', component: 'dashicons-screenoptions',
        embed: 'dashicons-embed-generic', shortcode: 'dashicons-shortcode', html: 'dashicons-editor-code', css: 'dashicons-editor-code'
    };
    const toolIcons = { 'auto-row': 'dashicons-columns', box: 'dashicons-align-wide', table: 'dashicons-editor-table' };

    let activeCategory = 'all';
    let favorites = new Set();
    let recent = [];
    let dragGhost = null;

    function normalize(value) {
        return String(value || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function itemType($item) {
        return String($item.attr('data-section-type') || '');
    }

    function itemTool($item) {
        return String($item.attr('data-h18-layout-tool') || '');
    }

    function itemKey($item) {
        const tool = itemTool($item);
        return tool ? 'tool:' + tool : 'type:' + itemType($item);
    }

    function categoryFor(type, tool) {
        return tool ? 'layout' : (categories[String(type || '')] || 'other');
    }

    function descriptionFor(type, tool) {
        return toolDescriptions[tool] || descriptions[type] || 'Element til sidebyggeren.';
    }

    function iconFor(type, tool) {
        return toolIcons[tool] || iconClasses[type] || 'dashicons-admin-generic';
    }

    function readFavorites() {
        try {
            const parsed = JSON.parse(window.localStorage ? window.localStorage.getItem(storageKey) || '[]' : '[]');
            favorites = new Set(Array.isArray(parsed) ? parsed.map(String) : []);
        } catch (error) {
            favorites = new Set();
        }
    }

    function writeFavorites() {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(storageKey, JSON.stringify(Array.from(favorites).sort()));
            }
        } catch (error) {}
    }

    function readRecent() {
        try {
            const parsed = JSON.parse(window.localStorage ? window.localStorage.getItem(recentStorageKey) || '[]' : '[]');
            recent = Array.isArray(parsed) ? parsed.map(String).filter(Boolean).slice(0, recentLimit) : [];
        } catch (error) {
            recent = [];
        }
    }

    function writeRecent() {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(recentStorageKey, JSON.stringify(recent.slice(0, recentLimit)));
            }
        } catch (error) {}
    }

    function isFavoriteKey(key, type) {
        return favorites.has(key) || favorites.has(type);
    }

    function markRecent($item) {
        const key = itemKey($item);
        if (!key) { return; }
        recent = [key].concat(recent.filter(function (entry) { return entry !== key; })).slice(0, recentLimit);
        writeRecent();
        refreshRecentUi();
        if (activeCategory === 'recent') {
            applyFilter();
        }
    }

    function decorateItem($item, label, type, tool) {
        if ($item.attr('data-library-card') === '1') { return; }
        const description = descriptionFor(type, tool);
        const category = categoryFor(type, tool);
        if (!$item.find('.dashicons').length) {
            $item.prepend($('<span>', { class: 'dashicons ' + iconFor(type, tool), 'aria-hidden': 'true' }));
        }
        $item.attr({
            'data-library-card': '1',
            'data-library-description': description,
            title: label + ' — ' + description
        }).addClass('h18-library-card-button');
        $item.append($('<small>', { class: 'h18-library-card-description', text: description }));
        $item.append($('<span>', { class: 'h18-library-card-category', text: categoryLabels[category] || 'Andet' }));
    }

    function shellFor($item) {
        const $existing = $item.closest('.h18-library-item-shell');
        if ($existing.length) {
            return $existing;
        }
        const type = itemType($item);
        const tool = itemTool($item);
        const key = itemKey($item);
        const label = String($item.text() || type).replace(/\s+/g, ' ').trim();
        const category = categoryFor(type, tool);
        const $shell = $('<div>', {
            class: 'h18-library-item-shell',
            'data-library-key': key,
            'data-library-type': type,
            'data-library-tool': tool,
            'data-library-category': category,
            'data-library-label': normalize(label),
            'data-library-description': normalize(descriptionFor(type, tool))
        });
        $item.before($shell);
        $shell.append($item);
        decorateItem($item, label, type, tool);
        const $favorite = $('<button>', {
            type: 'button',
            class: 'h18-library-favorite',
            'data-library-favorite': key,
            'data-library-favorite-legacy': type,
            title: 'Markér som favorit',
            'aria-label': 'Markér ' + label + ' som favorit',
            'aria-pressed': 'false'
        }).append($('<span>', { class: 'dashicons dashicons-star-empty', 'aria-hidden': 'true' }));
        $shell.append($favorite);
        return $shell;
    }

    function ensureItems() {
        $panel.find('.h18-builder-palette-item').each(function () {
            const $item = $(this);
            const $shell = shellFor($item);
            if ($shell.length && $item.attr('data-library-card') !== '1') {
                decorateItem($item, String($shell.attr('data-library-label') || itemType($item)), itemType($item), itemTool($item));
            }
        });
    }

    function refreshFavoriteUi() {
        $panel.find('.h18-library-item-shell').each(function () {
            const $shell = $(this);
            const key = String($shell.attr('data-library-key') || '');
            const type = String($shell.attr('data-library-type') || '');
            const isFavorite = isFavoriteKey(key, type);
            $shell.toggleClass('is-favorite', isFavorite);
            $shell.find('.h18-library-favorite')
                .attr('aria-pressed', isFavorite ? 'true' : 'false')
                .attr('title', isFavorite ? 'Fjern fra favoritter' : 'Markér som favorit')
                .find('.dashicons')
                .toggleClass('dashicons-star-empty', !isFavorite)
                .toggleClass('dashicons-star-filled', isFavorite);
        });
    }

    function refreshRecentUi() {
        $panel.find('.h18-library-item-shell').each(function () {
            const $shell = $(this);
            const key = String($shell.attr('data-library-key') || '');
            const rank = recent.indexOf(key);
            $shell.toggleClass('is-recent', rank >= 0).attr('data-library-recent-rank', rank >= 0 ? String(rank + 1) : '');
            $shell.find('.h18-library-recent-badge').remove();
            if (rank >= 0) {
                $shell.append($('<span>', {
                    class: 'h18-library-recent-badge',
                    text: rank === 0 ? 'Senest' : '#' + (rank + 1),
                    title: 'Senest brugt nr. ' + (rank + 1)
                }));
            }
        });
    }

    function applyFilter() {
        ensureItems();
        const query = normalize($('#h18-element-library-search').val());
        let visible = 0;
        $panel.find('.h18-library-item-shell').each(function () {
            const $shell = $(this);
            const key = String($shell.attr('data-library-key') || '');
            const type = String($shell.attr('data-library-type') || '');
            const category = String($shell.attr('data-library-category') || 'other');
            const label = String($shell.attr('data-library-label') || '');
            const description = String($shell.attr('data-library-description') || '');
            const matchesQuery = !query || label.includes(query) || description.includes(query) || normalize(type).includes(query);
            const matchesCategory = activeCategory === 'all' ||
                (activeCategory === 'favorites' ? isFavoriteKey(key, type) :
                    (activeCategory === 'recent' ? recent.includes(key) : category === activeCategory));
            const show = matchesQuery && matchesCategory;
            $shell.prop('hidden', !show);
            if (show) { visible += 1; }
        });
        $('#h18-element-library-count').text(visible + ' element' + (visible === 1 ? '' : 'er'));
        $('#h18-element-library-empty').prop('hidden', visible > 0);
    }

    function setCategory(category) {
        activeCategory = String(category || 'all');
        $('#h18-element-library-filters .h18-library-filter')
            .removeClass('is-active')
            .attr('aria-pressed', 'false')
            .filter('[data-library-filter="' + activeCategory + '"]')
            .addClass('is-active')
            .attr('aria-pressed', 'true');
        applyFilter();
    }

    function buildControls() {
        if ($('#h18-element-library-tools').length) { return; }
        const $tools = $('<section>', { id: 'h18-element-library-tools', class: 'h18-element-library-tools', 'aria-label': 'Filtrér elementbibliotek' });
        const $searchRow = $('<div>', { class: 'h18-library-search-row' }).append(
            $('<label>', { for: 'h18-element-library-search', class: 'screen-reader-text', text: 'Søg i elementer' }),
            $('<input>', {
                id: 'h18-element-library-search', type: 'search', class: 'regular-text',
                placeholder: 'Søg elementer…', autocomplete: 'off', 'aria-controls': 'h18-element-library-results'
            }),
            $('<span>', { id: 'h18-element-library-count', class: 'h18-library-count', 'aria-live': 'polite' })
        );
        const labels = [
            ['all', 'Alle'], ['recent', '↻ Seneste'], ['favorites', '★ Favoritter'], ['content', 'Indhold'], ['layout', 'Layout'],
            ['interactive', 'Interaktiv'], ['dynamic', 'Dynamisk'], ['advanced', 'Avanceret']
        ];
        const $filters = $('<div>', { id: 'h18-element-library-filters', class: 'h18-library-filters', role: 'group', 'aria-label': 'Elementkategorier' });
        labels.forEach(function (entry) {
            $filters.append($('<button>', {
                type: 'button', class: 'button button-small h18-library-filter' + (entry[0] === 'all' ? ' is-active' : ''),
                'data-library-filter': entry[0], 'aria-pressed': entry[0] === 'all' ? 'true' : 'false', text: entry[1]
            }));
        });
        $tools.append($searchRow, $filters);
        $list.attr('id', 'h18-element-library-results').before($tools);
        $list.after($('<p>', {
            id: 'h18-element-library-empty', class: 'h18-library-empty description', hidden: true,
            text: 'Ingen elementer matcher søgningen eller filteret.'
        }));
    }

    function removeDragGhost() {
        if (dragGhost && dragGhost.parentNode) {
            dragGhost.parentNode.removeChild(dragGhost);
        }
        dragGhost = null;
    }

    function installDragPreview(event, $item) {
        const nativeEvent = event.originalEvent || event;
        const transfer = nativeEvent && nativeEvent.dataTransfer;
        if (!transfer || typeof transfer.setDragImage !== 'function') { return; }
        removeDragGhost();
        const $shell = $item.closest('.h18-library-item-shell');
        const label = String($item.clone().children('.h18-library-card-description,.h18-library-card-category').remove().end().text() || itemType($item)).replace(/\s+/g, ' ').trim();
        const description = descriptionFor(itemType($item), itemTool($item));
        const $ghost = $('<div>', { class: 'h18-library-drag-ghost', 'aria-hidden': 'true' }).append(
            $('<span>', { class: 'dashicons ' + iconFor(itemType($item), itemTool($item)) }),
            $('<span>', { class: 'h18-library-drag-ghost-copy' }).append(
                $('<strong>', { text: label }),
                $('<small>', { text: description })
            )
        );
        $('body').append($ghost);
        dragGhost = $ghost.get(0);
        transfer.setDragImage(dragGhost, 24, 24);
        $shell.addClass('is-dragging');
        window.setTimeout(function () {
            if (dragGhost) { $(dragGhost).addClass('is-ready'); }
        }, 0);
    }

    readFavorites();
    readRecent();
    buildControls();
    ensureItems();
    refreshFavoriteUi();
    refreshRecentUi();
    applyFilter();

    $(document).on('input', '#h18-element-library-search', applyFilter);
    $(document).on('click', '.h18-library-filter', function () {
        setCategory($(this).attr('data-library-filter'));
    });
    $(document).on('click', '.h18-library-favorite', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const key = String($(this).attr('data-library-favorite') || '');
        const legacy = String($(this).attr('data-library-favorite-legacy') || '');
        if (!key) { return; }
        if (isFavoriteKey(key, legacy)) {
            favorites.delete(key);
            if (legacy) { favorites.delete(legacy); }
        } else {
            favorites.add(key);
        }
        writeFavorites();
        refreshFavoriteUi();
        applyFilter();
    });
    $(document).on('click', '.h18-builder-palette-item', function () {
        markRecent($(this));
    });
    $(document).on('dragstart.h18ElementLibrary', '.h18-builder-palette-item', function (event) {
        installDragPreview(event, $(this));
    });
    $(document).on('dragend.h18ElementLibrary', '.h18-builder-palette-item', function () {
        markRecent($(this));
        $(this).closest('.h18-library-item-shell').removeClass('is-dragging');
        removeDragGhost();
    });
    $(document).on('drop.h18ElementLibrary', function () {
        window.setTimeout(removeDragGhost, 0);
    });

    $(document).on('keydown.h18ElementLibrary', function (event) {
        if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) { return; }
        const $target = $(event.target);
        if ($target.is('input,textarea,select') || $target.closest('[contenteditable="true"]').length || !$('.h18-builder-sidebar-panel[data-builder-panel="elements"]').hasClass('is-active')) {
            return;
        }
        event.preventDefault();
        $('#h18-element-library-search').trigger('focus').trigger('select');
    });
});
