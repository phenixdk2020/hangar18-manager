jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $canvas = $('.h18-builder-canvas').first();
    if (!$sections.length || !$canvas.length) {
        return;
    }

    const BOX_LABEL = 'Kasse';
    const typeLabels = {
        hero: 'Hero', text: 'Tekst', text_image: 'Tekst + billede', image: 'Billede', buttons: 'Knapper',
        card: 'Kort', card_grid: 'Kort-grid', highlight: 'Fremhævning', icon: 'Ikon', list: 'Liste', badge: 'Badge',
        quote: 'Citat', spacer: 'Spacer', divider: 'Skillelinje', tabs: 'Faner', accordion: 'Accordion',
        carousel: 'Carousel', mail_form: 'Formular', poll: 'Afstemning', query_list: 'Dynamisk liste',
        component: 'Komponent', embed: 'Embed', shortcode: 'Shortcode', html: 'HTML', css: 'CSS',
        container: 'Container', flex: 'Flex', grid: 'Grid'
    };

    let pendingType = '';
    let pendingKeys = new Set();
    let pendingBoxKey = '';
    let clickBoxKey = '';
    let clickKeys = new Set();
    let refreshTimer = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($('#h18-page-inspector-target').find(selector));
        }
        return $result;
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '');
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function rowByKey(key) {
        key = String(key || '');
        if (!key) { return $(); }
        return activeRows().filter(function () { return rowKey($(this)) === key; }).first();
    }

    function isBox($row) {
        return !!($row && $row.length && rowType($row) === 'container' && rowLabel($row).indexOf(BOX_LABEL) === 0);
    }

    function selectedBox() {
        const $row = activeRows().filter('.is-selected').first();
        return isBox($row) ? $row : $();
    }

    function snapshotKeys() {
        const keys = new Set();
        activeRows().each(function () {
            const key = rowKey($(this));
            if (key) { keys.add(key); }
        });
        return keys;
    }

    function findNewRow(beforeKeys, type) {
        let $match = $();
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (key && !beforeKeys.has(key) && (!type || rowType($row) === type)) {
                $match = $row;
            }
        });
        return $match;
    }

    function setParent($row, key) {
        if (!$row || !$row.length || !key) { return false; }
        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if (!$hidden.length) { return false; }
        $hidden.val(String(key)).trigger('change');
        if ($select.length) {
            $select.val(String(key)).trigger('change');
        }
        $row.attr('data-h18-nested-in-box', String(key));
        return true;
    }

    function targetBoxForElement(element) {
        const target = element && element.closest ? element.closest('.h18-page-section-row') : null;
        if (!target) { return $(); }
        const $target = $(target);
        if (isBox($target)) { return $target; }
        const $parent = rowByKey(parentKey($target));
        return isBox($parent) ? $parent : $();
    }

    function directChildren($box) {
        const key = rowKey($box);
        if (!key) { return $(); }
        return activeRows().filter(function () { return parentKey($(this)) === key; });
    }

    function childDisplayName($row) {
        const nav = rowLabel($row);
        if (nav && nav !== BOX_LABEL) { return nav; }
        const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
        return title || typeLabels[rowType($row)] || rowType($row) || 'Element';
    }

    function clearDropTarget() {
        activeRows().removeClass('h18-ud-nesting-drop-target');
    }

    function showDropTarget($box) {
        clearDropTarget();
        if ($box && $box.length) { $box.addClass('h18-ud-nesting-drop-target'); }
    }

    function decorateBox($box) {
        if (!isBox($box)) { return; }
        const $preview = $box.children('.h18-canvas-preview').first();
        if (!$preview.length) { return; }
        $preview.find('.h18-ud-box-contents-preview').remove();
        const $children = directChildren($box);
        const $wrap = $('<div>', { class: 'h18-ud-box-contents-preview' });
        const $head = $('<div>', { class: 'h18-ud-box-contents-head' }).append(
            $('<strong>', { text: 'Indhold i kassen' }),
            $('<span>', { text: $children.length + ' element' + ($children.length === 1 ? '' : 'er') })
        );
        const $items = $('<div>', { class: 'h18-ud-box-contents-items' });
        if (!$children.length) {
            $items.append($('<div>', {
                class: 'h18-ud-box-empty-drop',
                text: 'Træk Tekst, Billede, Knap eller et andet element ind i kassen.'
            }));
        } else {
            $children.each(function () {
                const $child = $(this);
                const key = rowKey($child);
                $items.append($('<button>', {
                    type: 'button',
                    class: 'h18-ud-box-child-chip',
                    'data-h18-box-child-key': key,
                    title: 'Redigér ' + childDisplayName($child)
                }).append(
                    $('<span>', { class: 'dashicons dashicons-arrow-right-alt2', 'aria-hidden': 'true' }),
                    $('<span>', { text: childDisplayName($child) }),
                    $('<small>', { text: typeLabels[rowType($child)] || rowType($child) })
                ));
            });
        }
        $wrap.append($head, $items);
        $preview.append($wrap);
    }

    function refreshBoxes() {
        activeRows().each(function () {
            const $row = $(this);
            if (isBox($row)) { decorateBox($row); }
        });
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(refreshBoxes, typeof delay === 'number' ? delay : 30);
    }

    function finishNest(beforeKeys, type, boxKey) {
        window.setTimeout(function () {
            const $box = rowByKey(boxKey);
            const $newRow = findNewRow(beforeKeys, type);
            if ($box.length && isBox($box) && $newRow.length && !isBox($newRow)) {
                setParent($newRow, boxKey);
                $newRow.addClass('h18-ud-just-nested');
                window.setTimeout(function () { $newRow.removeClass('h18-ud-just-nested'); }, 900);
            }
            clearDropTarget();
            scheduleRefresh(20);
        }, 60);
    }

    document.addEventListener('dragstart', function (event) {
        const item = event.target.closest && event.target.closest('.h18-builder-palette-item');
        if (!item || item.hasAttribute('data-h18-layout-tool')) { return; }
        pendingType = String(item.getAttribute('data-section-type') || 'text');
        pendingKeys = snapshotKeys();
        pendingBoxKey = '';
    }, true);

    document.addEventListener('dragover', function (event) {
        if (!pendingType) { return; }
        const $box = targetBoxForElement(event.target);
        pendingBoxKey = $box.length ? rowKey($box) : '';
        showDropTarget($box);
    }, true);

    document.addEventListener('drop', function (event) {
        if (!pendingType) { return; }
        const $box = targetBoxForElement(event.target);
        const boxKey = $box.length ? rowKey($box) : pendingBoxKey;
        const type = pendingType;
        const beforeKeys = pendingKeys;
        pendingType = '';
        pendingBoxKey = '';
        if (boxKey) { finishNest(beforeKeys, type, boxKey); }
        else { clearDropTarget(); scheduleRefresh(80); }
    }, true);

    document.addEventListener('dragend', function () {
        pendingType = '';
        pendingBoxKey = '';
        clearDropTarget();
        scheduleRefresh(40);
    }, true);

    document.addEventListener('click', function (event) {
        const item = event.target.closest && event.target.closest('.h18-builder-palette-item');
        if (!item || item.hasAttribute('data-h18-layout-tool')) { return; }
        const $box = selectedBox();
        if (!$box.length) { return; }
        clickBoxKey = rowKey($box);
        clickKeys = snapshotKeys();
        finishNest(clickKeys, String(item.getAttribute('data-section-type') || 'text'), clickBoxKey);
    }, true);

    $(document).on('click', '.h18-ud-box-child-chip', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $row = rowByKey($(this).attr('data-h18-box-child-key'));
        if ($row.length) { $row.children('.h18-page-section-header').trigger('click'); }
    });

    $(document).on('change', '.h18-layout-parent-key, .h18-layout-parent-select, .h18-section-navigator-label', function () {
        scheduleRefresh(20);
    });
    $(document).on('input', '.h18-section-navigator-label', function () { scheduleRefresh(30); });
    $(document).on('click', '.h18-page-section-delete', function () { scheduleRefresh(80); });

    const observer = new MutationObserver(function () { scheduleRefresh(40); });
    observer.observe($sections.get(0), { childList: true, subtree: false });

    scheduleRefresh(80);
});
