jQuery(function ($) {
    'use strict';

    const $panel = $('.h18-builder-sidebar-panel[data-builder-panel="elements"]');
    const $list = $panel.find('.h18-builder-palette-list').first();
    if (!$panel.length || !$list.length) {
        return;
    }

    const storageKey = 'hangar18UltimateDesignerElementFavoritesV087';
    const categories = {
        hero: 'content', text: 'content', text_image: 'content', image: 'content', buttons: 'content',
        card: 'content', card_grid: 'content', highlight: 'content', icon: 'content', list: 'content',
        badge: 'content', quote: 'content',
        container: 'layout', flex: 'layout', grid: 'layout', spacer: 'layout', divider: 'layout',
        tabs: 'interactive', accordion: 'interactive', carousel: 'interactive', mail_form: 'interactive', poll: 'interactive',
        query_list: 'dynamic', component: 'dynamic', embed: 'dynamic', shortcode: 'dynamic',
        html: 'advanced', css: 'advanced'
    };

    let activeCategory = 'all';
    let favorites = new Set();

    function normalize(value) {
        return String(value || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/\s+/g, ' ')
            .trim();
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

    function categoryFor(type) {
        return categories[String(type || '')] || 'other';
    }

    function shellFor($item) {
        const $existing = $item.closest('.h18-library-item-shell');
        if ($existing.length) {
            return $existing;
        }
        const type = String($item.attr('data-section-type') || '');
        const label = String($item.text() || type).replace(/\s+/g, ' ').trim();
        const $shell = $('<div>', {
            class: 'h18-library-item-shell',
            'data-library-type': type,
            'data-library-category': categoryFor(type),
            'data-library-label': normalize(label)
        });
        $item.before($shell);
        $shell.append($item);
        const $favorite = $('<button>', {
            type: 'button',
            class: 'h18-library-favorite',
            'data-library-favorite': type,
            title: 'Markér som favorit',
            'aria-label': 'Markér ' + label + ' som favorit',
            'aria-pressed': 'false'
        }).append($('<span>', { class: 'dashicons dashicons-star-empty', 'aria-hidden': 'true' }));
        $shell.append($favorite);
        return $shell;
    }

    function ensureItems() {
        $panel.find('.h18-builder-palette-item').each(function () {
            shellFor($(this));
        });
    }

    function refreshFavoriteUi() {
        $panel.find('.h18-library-item-shell').each(function () {
            const $shell = $(this);
            const type = String($shell.attr('data-library-type') || '');
            const isFavorite = favorites.has(type);
            $shell.toggleClass('is-favorite', isFavorite);
            $shell.find('.h18-library-favorite')
                .attr('aria-pressed', isFavorite ? 'true' : 'false')
                .attr('title', isFavorite ? 'Fjern fra favoritter' : 'Markér som favorit')
                .find('.dashicons')
                .toggleClass('dashicons-star-empty', !isFavorite)
                .toggleClass('dashicons-star-filled', isFavorite);
        });
    }

    function applyFilter() {
        ensureItems();
        const query = normalize($('#h18-element-library-search').val());
        let visible = 0;
        $panel.find('.h18-library-item-shell').each(function () {
            const $shell = $(this);
            const type = String($shell.attr('data-library-type') || '');
            const category = String($shell.attr('data-library-category') || 'other');
            const label = String($shell.attr('data-library-label') || '');
            const matchesQuery = !query || label.includes(query) || normalize(type).includes(query);
            const matchesCategory = activeCategory === 'all' ||
                (activeCategory === 'favorites' ? favorites.has(type) : category === activeCategory);
            const show = matchesQuery && matchesCategory;
            $shell.prop('hidden', !show);
            if (show) {
                visible += 1;
            }
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
        if ($('#h18-element-library-tools').length) {
            return;
        }
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
            ['all', 'Alle'], ['favorites', '★ Favoritter'], ['content', 'Indhold'], ['layout', 'Layout'],
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

    readFavorites();
    buildControls();
    ensureItems();
    refreshFavoriteUi();
    applyFilter();

    $(document).on('input', '#h18-element-library-search', applyFilter);
    $(document).on('click', '.h18-library-filter', function () {
        setCategory($(this).attr('data-library-filter'));
    });
    $(document).on('click', '.h18-library-favorite', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const type = String($(this).attr('data-library-favorite') || '');
        if (!type) {
            return;
        }
        if (favorites.has(type)) {
            favorites.delete(type);
        } else {
            favorites.add(type);
        }
        writeFavorites();
        refreshFavoriteUi();
        applyFilter();
    });

    $(document).on('keydown.h18ElementLibrary', function (event) {
        if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) {
            return;
        }
        const $target = $(event.target);
        if ($target.is('input,textarea,select') || $target.closest('[contenteditable="true"]').length || !$('.h18-builder-sidebar-panel[data-builder-panel="elements"]').hasClass('is-active')) {
            return;
        }
        event.preventDefault();
        $('#h18-element-library-search').trigger('focus').trigger('select');
    });
});
