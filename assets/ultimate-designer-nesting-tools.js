jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $canvas = $('.h18-builder-canvas').first();
    const $inspector = $('#h18-page-inspector-target');
    if (!$sections.length || !$canvas.length) {
        return;
    }

    const BOX_LABEL = 'Kasse';
    const AUTO_LABEL = 'Auto-kasser';
    const MAX_NESTING_DEPTH = 2;
    const typeLabels = {
        hero: 'Hero', text: 'Tekst', text_image: 'Tekst + billede', image: 'Billede', buttons: 'Knapper',
        card: 'Kort', card_grid: 'Kort-grid', highlight: 'Fremhævning', icon: 'Ikon', list: 'Liste', badge: 'Badge',
        quote: 'Citat', spacer: 'Spacer', divider: 'Skillelinje', tabs: 'Faner', accordion: 'Accordion',
        carousel: 'Carousel', mail_form: 'Formular', poll: 'Afstemning', query_list: 'Dynamisk liste',
        component: 'Komponent', embed: 'Embed', shortcode: 'Shortcode', html: 'HTML', css: 'CSS',
        container: 'Kasse', flex: 'Flex', grid: 'Auto-kasser'
    };

    let pendingDrag = null;
    let refreshTimer = null;
    let existingDragRow = $();
    let existingDropBoxKey = '';
    let paletteBoxDrag = null;
    let existingBoxDrag = null;
    let renderGuard = false;
    let suppressPaletteClickUntil = 0;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($inspector.find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '');
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

    function isAuto($row) {
        return !!($row && $row.length && rowType($row) === 'grid' && rowLabel($row) === AUTO_LABEL);
    }

    function directChildren($row) {
        const key = rowKey($row);
        if (!key) { return $(); }
        return activeRows().filter(function () { return parentKey($(this)) === key; });
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
        if (!$row || !$row.length) { return false; }
        const value = String(key || '');
        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if (!$hidden.length) { return false; }
        $hidden.val(value).trigger('change');
        if ($select.length) { $select.val(value).trigger('change'); }
        if (value) { $row.attr('data-h18-nested-in-box', value); }
        else { $row.removeAttr('data-h18-nested-in-box'); }
        return true;
    }

    function setLabel($row, value) {
        const $field = controls($row, '.h18-section-navigator-label').first();
        if ($field.length && String($field.val() || '') !== String(value)) {
            $field.val(String(value)).trigger('input').trigger('change');
        }
    }

    function setField($row, name, value) {
        const $field = controls($row, '[name$="[' + name + ']"]').first();
        if (!$field.length) { return; }
        if ($field.is(':checkbox')) {
            if ($field.is(':checked') !== !!value) { $field.prop('checked', !!value).trigger('change'); }
        } else if (String($field.val() || '') !== String(value)) {
            $field.val(String(value)).trigger('input').trigger('change');
        }
    }

    function configureBox($row) {
        if (!$row.length || rowType($row) !== 'container') { return; }
        setLabel($row, BOX_LABEL);
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'LayoutDirection', 'Column');
        setField($row, 'LayoutWrap', true);
        setField($row, 'LayoutAlign', 'Stretch');
        setField($row, 'LayoutGapPx', 12);
        setField($row, 'MobileLayoutGapPx', 10);
        setField($row, 'MobileLayoutStack', true);
        $row.attr('data-h18-box', '1');
    }

    function configureAuto($row) {
        if (!$row.length || rowType($row) !== 'grid') { return; }
        setLabel($row, AUTO_LABEL);
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'LayoutColumns', 1);
        setField($row, 'MobileLayoutColumns', 1);
        setField($row, 'LayoutGapPx', 16);
        setField($row, 'MobileLayoutGapPx', 12);
        setField($row, 'LayoutAlign', 'Stretch');
        setParent($row, '');
        $row.attr('data-h18-auto-box-row', '1');
    }

    function syncFlatOrder() {
        let index = 0;
        $sections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            index += 1;
            $row.find('.h18-page-section-order').val(index * 10);
        });
        if ($sections.hasClass('ui-sortable')) { $sections.sortable('refresh'); }
    }

    function childDisplayName($row) {
        const nav = rowLabel($row);
        if (nav && nav !== BOX_LABEL) { return nav; }
        const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
        return title || typeLabels[rowType($row)] || rowType($row) || 'Element';
    }

    function clonePreview($row, preserveBoxContents) {
        const $preview = $row.children('.h18-canvas-preview').first();
        if (!$preview.length) { return $(); }
        const $clone = $preview.clone(false, false);
        $clone.removeAttr('id');
        $clone.find('[id]').removeAttr('id');
        $clone.find('[name]').removeAttr('name');
        if (preserveBoxContents) {
            $clone.find('.h18-ud-auto-box-grid,.h18-v0810-side-zones,.h18-v0811-side-zones,.h18-v0814-auto-drop-zone').remove();
        } else {
            $clone.find('.h18-ud-box-contents-preview,.h18-ud-auto-box-grid,.h18-v0810-side-zones,.h18-v0811-side-zones,.h18-v0814-auto-drop-zone').remove();
        }
        $clone.find('input,select,textarea,button').prop('disabled', true).attr('tabindex', '-1');
        if (preserveBoxContents) {
            $clone.find('button.h18-v0811-edit-child').prop('disabled', false).removeAttr('tabindex');
        }
        $clone.find('a').attr('tabindex', '-1');
        return $clone;
    }

    function renderBox($box) {
        if (!isBox($box)) { return; }
        const $preview = $box.children('.h18-canvas-preview').first();
        if (!$preview.length) { return; }
        $box.attr('data-h18-box', '1');
        $preview.find('.h18-ud-box-contents-preview,.h18-v0810-side-zones,.h18-v0811-side-zones').remove();

        const $children = directChildren($box);
        const $wrap = $('<div>', { class: 'h18-ud-box-contents-preview h18-v0811-box-contents' });
        const $head = $('<div>', { class: 'h18-ud-box-contents-head' }).append(
            $('<strong>', { text: 'Indhold i kassen' }),
            $('<span>', { text: $children.length + ' element' + ($children.length === 1 ? '' : 'er') }),
            $('<em>', { class: 'h18-v0811-runtime-badge', text: 'v0.8.14' })
        );
        const $items = $('<div>', { class: 'h18-ud-box-contents-items h18-v0811-child-list' });
        if (!$children.length) {
            $items.append($('<div>', { class: 'h18-ud-box-empty-drop', text: 'Kassen er tom.' }));
        } else {
            $children.each(function () {
                const $child = $(this);
                const childKey = rowKey($child);
                const nestedBox = isBox($child);
                const $card = $('<section>', {
                    class: 'h18-v0811-child-card' + (nestedBox ? ' h18-v0813-nested-box' : ''),
                    'data-h18-v0811-child': childKey
                });
                if (nestedBox) { $card.attr('data-h18-v0811-box', childKey); }
                const $bar = $('<div>', { class: 'h18-v0811-child-bar' }).append(
                    $('<strong>', { text: childDisplayName($child) }),
                    $('<button>', { type: 'button', class: 'button button-small h18-v0811-edit-child', 'data-h18-v0811-edit-child': childKey, text: 'Rediger' })
                );
                const $body = $('<div>', { class: 'h18-v0811-child-preview' });
                const $clone = clonePreview($child, isBox($child));
                if ($clone.length) { $body.append($clone); }
                else { $body.text(childDisplayName($child)); }
                $card.append($bar, $body);
                $items.append($card);
            });
        }
        const $dropZone = $('<div>', { class: 'h18-ud-box-drop-zone', 'data-h18-v0813-box-drop': rowKey($box), text: 'Træk et element eller en Kasse hertil for at lægge det IND I kassen' });
        $wrap.append($head, $items, $dropZone);
        $preview.append($wrap);

        if (!parentKey($box)) {
            const boxKey = rowKey($box);
            const $zones = $('<div>', { class: 'h18-v0811-side-zones' }).append(
                $('<div>', { class: 'h18-v0811-side-zone', 'data-side': 'left', 'data-box': boxKey, text: '← Slip Kasse til venstre' }),
                $('<div>', { class: 'h18-v0811-side-zone', 'data-side': 'right', 'data-box': boxKey, text: 'Slip Kasse til højre →' })
            );
            $preview.append($zones);
        }
    }

    function renderAuto($auto) {
        if (!isAuto($auto)) { return; }
        const autoKey = rowKey($auto);
        const $boxes = directChildren($auto).filter(function () { return isBox($(this)); });
        const count = $boxes.length;
        const cols = Math.max(1, Math.min(6, count || 1));
        setField($auto, 'LayoutColumns', cols);
        const gap = parseInt(String(controls($auto, '[name$="[LayoutGapPx]"]').first().val() || 16), 10) || 16;
        const $preview = $auto.children('.h18-canvas-preview').first();
        if (!$preview.length) { return; }
        $preview.find('.h18-ud-auto-box-grid,.h18-v0814-auto-drop-zone').remove();
        const $grid = $('<div>', {
            class: 'h18-ud-auto-box-grid h18-v0811-auto-grid',
            'data-h18-v0812-auto-kasse-drop': '1',
            'data-h18-v0814-auto-key': autoKey
        }).css({
            '--h18-v0811-cols': String(cols),
            '--h18-v0811-gap': gap + 'px'
        });
        $boxes.each(function (index) {
            const $box = $(this);
            const boxKey = rowKey($box);
            const $tile = $('<section>', { class: 'h18-v0811-auto-box', 'data-h18-v0811-box': boxKey });
            const $bar = $('<div>', { class: 'h18-v0811-child-bar' }).append(
                $('<strong>', { text: 'Kasse ' + (index + 1) }),
                $('<button>', { type: 'button', class: 'button button-small h18-v0811-edit-child', 'data-h18-v0811-edit-child': boxKey, text: 'Rediger Kasse' })
            );
            const $body = $('<div>', { class: 'h18-v0811-auto-box-preview' });
            const $clone = clonePreview($box, true);
            if ($clone.length) { $body.append($clone); }
            $tile.append($bar, $body);
            $grid.append($tile);
        });
        const $dropZone = $('<div>', {
            class: 'h18-v0814-auto-drop-zone',
            'data-h18-v0814-auto-drop': autoKey,
            text: count ? 'Slip endnu en Kasse her for at tilføje den til Auto-kasser' : 'Slip en Kasse her for at tilføje den til Auto-kasser'
        });
        $preview.append($grid, $dropZone);
    }

    function syncSourceVisibility() {
        activeRows().each(function () {
            const $row = $(this);
            const $parent = rowByKey(parentKey($row));
            const nested = isBox($parent) || isAuto($parent);
            $row.attr('data-h18-v0811-child-source', nested ? '1' : '0');
        });
    }

    function refreshComposition() {
        if (renderGuard) { return; }
        renderGuard = true;
        $sections.attr('data-h18-v0811-kasse-runtime', '1').attr('data-h18-v0813-kasse-runtime', '1').attr('data-h18-v0814-kasse-runtime', '1');
        activeRows().each(function () { if (isBox($(this))) { renderBox($(this)); } });
        activeRows().each(function () { if (isAuto($(this))) { renderAuto($(this)); } });
        syncSourceVisibility();
        renderGuard = false;
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(refreshComposition, typeof delay === 'number' ? delay : 180);
    }

    function parentDepth($row) {
        let depth = 0;
        let cursor = parentKey($row);
        const seen = new Set();
        while (cursor) {
            if (seen.has(cursor)) { return MAX_NESTING_DEPTH + 1; }
            seen.add(cursor);
            depth += 1;
            if (depth > MAX_NESTING_DEPTH) { return depth; }
            const $parent = rowByKey(cursor);
            if (!$parent.length) { break; }
            cursor = parentKey($parent);
        }
        return depth;
    }

    function subtreeDepth($row) {
        const rootKey = rowKey($row);
        if (!rootKey) { return 0; }
        let maxDepth = 0;
        const walk = function (key, depth, seen) {
            if (depth > maxDepth) { maxDepth = depth; }
            if (depth > MAX_NESTING_DEPTH) { return; }
            activeRows().each(function () {
                const $child = $(this);
                const childKey = rowKey($child);
                if (!childKey || parentKey($child) !== key || seen.has(childKey)) { return; }
                const nextSeen = new Set(seen);
                nextSeen.add(childKey);
                walk(childKey, depth + 1, nextSeen);
            });
        };
        walk(rootKey, 0, new Set([rootKey]));
        return maxDepth;
    }

    function wouldCreateCycle($row, $box) {
        const sourceKey = rowKey($row);
        let cursor = rowKey($box);
        const seen = new Set();
        while (cursor) {
            if (cursor === sourceKey || seen.has(cursor)) { return true; }
            seen.add(cursor);
            const $cursor = rowByKey(cursor);
            if (!$cursor.length) { break; }
            cursor = parentKey($cursor);
        }
        return false;
    }

    function canMoveIntoBox($row, $box) {
        if (!$row.length || !$box.length || !isBox($box) || isAuto($row)) { return false; }
        if (rowKey($row) === rowKey($box) || wouldCreateCycle($row, $box)) { return false; }
        const deepestAfterMove = parentDepth($box) + 1 + subtreeDepth($row);
        return deepestAfterMove <= MAX_NESTING_DEPTH;
    }

    function canAcceptNewBox($box) {
        return !!($box && $box.length && isBox($box) && (parentDepth($box) + 1) <= MAX_NESTING_DEPTH);
    }

    function canMoveBoxIntoAuto($row, $auto) {
        if (!$row || !$row.length || !$auto || !$auto.length || !isBox($row) || !isAuto($auto)) { return false; }
        const deepestAfterMove = parentDepth($auto) + 1 + subtreeDepth($row);
        return deepestAfterMove <= MAX_NESTING_DEPTH;
    }

    function moveRowIntoBox($row, $box) {
        if (!canMoveIntoBox($row, $box)) { return false; }
        const boxKey = rowKey($box);
        const $children = directChildren($box).not($row);
        const $anchor = $children.length ? $children.last() : $box;
        $row.insertAfter($anchor);
        if (!setParent($row, boxKey)) { return false; }
        syncFlatOrder();
        $row.attr('data-h18-v0811-child-source', '1');
        scheduleRefresh(80);
        return true;
    }

    function moveBoxIntoAuto($row, $auto) {
        if (!canMoveBoxIntoAuto($row, $auto)) { return false; }
        const autoKey = rowKey($auto);
        const $children = directChildren($auto).not($row);
        const $anchor = $children.length ? $children.last() : $auto;
        $row.insertAfter($anchor);
        if (!setParent($row, autoKey)) { return false; }
        syncFlatOrder();
        $row.attr('data-h18-v0811-child-source', '1');
        scheduleRefresh(80);
        return true;
    }

    function targetBoxForElement(element) {
        const proxy = element && element.closest ? element.closest('.h18-v0811-auto-box[data-h18-v0811-box],.h18-v0813-nested-box[data-h18-v0811-box]') : null;
        if (proxy) {
            const $proxyBox = rowByKey(String(proxy.getAttribute('data-h18-v0811-box') || ''));
            if (isBox($proxyBox)) { return $proxyBox; }
        }
        const zone = element && element.closest ? element.closest('.h18-ud-box-drop-zone[data-h18-v0813-box-drop]') : null;
        if (zone) {
            const explicit = String(zone.getAttribute('data-h18-v0813-box-drop') || '');
            const $explicitBox = rowByKey(explicit);
            if (isBox($explicitBox)) { return $explicitBox; }
        }
        const row = element && element.closest ? element.closest('.h18-page-section-row') : null;
        if (row) {
            const $row = $(row);
            if (isBox($row)) { return $row; }
            const $parent = rowByKey(parentKey($row));
            if (isBox($parent)) { return $parent; }
        }
        return $();
    }

    function targetAutoForElement(element) {
        if (!element || !element.closest) { return $(); }
        if (element.closest('.h18-v0811-auto-box[data-h18-v0811-box],.h18-ud-box-drop-zone[data-h18-v0813-box-drop]')) {
            return $();
        }
        const zone = element.closest('.h18-v0814-auto-drop-zone[data-h18-v0814-auto-drop]');
        if (zone) {
            const $auto = rowByKey(String(zone.getAttribute('data-h18-v0814-auto-drop') || ''));
            if (isAuto($auto)) { return $auto; }
        }
        const grid = element.closest('.h18-ud-auto-box-grid[data-h18-v0814-auto-key]');
        if (grid) {
            const $auto = rowByKey(String(grid.getAttribute('data-h18-v0814-auto-key') || ''));
            if (isAuto($auto)) { return $auto; }
        }
        const row = element.closest('.h18-page-section-row');
        if (row && isAuto($(row))) { return $(row); }
        return $();
    }

    function boxAtPoint(pageX, pageY, $draggedRow) {
        const clientX = Number(pageX) - (window.pageXOffset || document.documentElement.scrollLeft || 0);
        const clientY = Number(pageY) - (window.pageYOffset || document.documentElement.scrollTop || 0);
        let $match = $();

        $('.h18-v0811-auto-box[data-h18-v0811-box],.h18-v0813-nested-box[data-h18-v0811-box]').each(function () {
            const $proxy = $(this);
            const $box = rowByKey(String($proxy.attr('data-h18-v0811-box') || ''));
            if (!canMoveIntoBox($draggedRow, $box)) { return; }
            const zone = $proxy.find('.h18-ud-box-drop-zone[data-h18-v0813-box-drop]').get(0) || this;
            const rect = zone.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
                $match = $box;
            }
        });
        if ($match.length) { return $match; }

        activeRows().each(function () {
            const $box = $(this);
            if (!canMoveIntoBox($draggedRow, $box)) { return; }
            const zone = $box.find('.h18-ud-box-drop-zone[data-h18-v0813-box-drop]').get(0);
            if (!zone) { return; }
            const rect = zone.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
                $match = $box;
            }
        });
        return $match;
    }

    function autoAtPoint(pageX, pageY, $draggedRow) {
        if (!$draggedRow || !$draggedRow.length || !isBox($draggedRow)) { return $(); }
        const clientX = Number(pageX) - (window.pageXOffset || document.documentElement.scrollLeft || 0);
        const clientY = Number(pageY) - (window.pageYOffset || document.documentElement.scrollTop || 0);
        let $match = $();
        $('.h18-v0814-auto-drop-zone[data-h18-v0814-auto-drop],.h18-ud-auto-box-grid[data-h18-v0814-auto-key]').each(function () {
            const key = String(this.getAttribute('data-h18-v0814-auto-drop') || this.getAttribute('data-h18-v0814-auto-key') || '');
            const $auto = rowByKey(key);
            if (!canMoveBoxIntoAuto($draggedRow, $auto)) { return; }
            const rect = this.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
                $match = $auto;
            }
        });
        return $match;
    }

    function sideZoneAtPoint(pageX, pageY, sourceKey) {
        const clientX = Number(pageX) - (window.pageXOffset || document.documentElement.scrollLeft || 0);
        const clientY = Number(pageY) - (window.pageYOffset || document.documentElement.scrollTop || 0);
        let match = null;
        $('.h18-v0811-side-zone').each(function () {
            const target = String(this.getAttribute('data-box') || '');
            if (!target || target === sourceKey) { return; }
            const rect = this.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
                match = { target: target, side: String(this.getAttribute('data-side') || 'right'), node: this };
            }
        });
        return match;
    }

    function createAutoForBoxes($source, $target, side) {
        const before = snapshotKeys();
        const $gridButton = $('.h18-builder-palette-item[data-section-type="grid"]').not('[data-h18-layout-tool]').first();
        if (!$gridButton.length) { return; }
        $gridButton.trigger('click');
        window.setTimeout(function () {
            const $grid = findNewRow(before, 'grid');
            if (!$grid.length) { scheduleRefresh(120); return; }
            configureAuto($grid);
            const gridKey = rowKey($grid);
            setParent($source, gridKey);
            setParent($target, gridKey);
            $grid.insertBefore($target);
            if (side === 'left') {
                $source.insertAfter($grid);
                $target.insertAfter($source);
            } else {
                $target.insertAfter($grid);
                $source.insertAfter($target);
            }
            syncFlatOrder();
            scheduleRefresh(120);
        }, 100);
    }

    function placeBoxBeside($source, $target, side) {
        if (!$source.length || !$target.length || !isBox($source) || !isBox($target) || rowKey($source) === rowKey($target)) { return; }
        const $targetParent = rowByKey(parentKey($target));
        if (isAuto($targetParent)) {
            setParent($source, rowKey($targetParent));
            if (side === 'left') { $source.insertBefore($target); }
            else { $source.insertAfter($target); }
            syncFlatOrder();
            scheduleRefresh(100);
            return;
        }
        createAutoForBoxes($source, $target, side);
    }

    function clearTargets() {
        activeRows().removeClass('h18-ud-nesting-drop-target h18-v0814-auto-drop-target');
        $('.h18-v0811-auto-box,.h18-v0813-nested-box').removeClass('h18-ud-nesting-drop-target');
        $('.h18-ud-box-drop-zone,.h18-v0811-side-zone,.h18-v0814-auto-drop-zone,.h18-ud-auto-box-grid').removeClass('is-active h18-v0814-auto-drop-active');
    }

    function showBoxTarget($box) {
        clearTargets();
        if ($box.length) {
            const key = rowKey($box);
            $box.addClass('h18-ud-nesting-drop-target');
            $box.find('.h18-ud-box-drop-zone[data-h18-v0813-box-drop="' + key + '"]').first().addClass('is-active');
            const $proxy = $('.h18-v0811-auto-box[data-h18-v0811-box="' + key + '"],.h18-v0813-nested-box[data-h18-v0811-box="' + key + '"]');
            $proxy.addClass('h18-ud-nesting-drop-target');
            $proxy.find('.h18-ud-box-drop-zone[data-h18-v0813-box-drop="' + key + '"]').first().addClass('is-active');
        }
    }

    function showAutoTarget($auto) {
        clearTargets();
        if (!$auto || !$auto.length) { return; }
        const key = rowKey($auto);
        $auto.addClass('h18-v0814-auto-drop-target');
        $auto.find('.h18-v0814-auto-drop-zone[data-h18-v0814-auto-drop="' + key + '"]').addClass('is-active');
        $auto.find('.h18-ud-auto-box-grid[data-h18-v0814-auto-key="' + key + '"]').addClass('h18-v0814-auto-drop-active');
    }

    function showSideTarget(zone) {
        clearTargets();
        if (zone) { $(zone).addClass('is-active'); }
    }

    function finishNewNested(beforeKeys, type, boxKey) {
        window.setTimeout(function () {
            const $box = rowByKey(boxKey);
            const $newRow = findNewRow(beforeKeys, type);
            if ($box.length && $newRow.length) { moveRowIntoBox($newRow, $box); }
            clearTargets();
            scheduleRefresh(100);
        }, 70);
    }

    function finishNewBoxStandalone(beforeKeys) {
        window.setTimeout(function () {
            const $newBox = findNewRow(beforeKeys, 'container');
            if ($newBox.length && !isBox($newBox)) { configureBox($newBox); }
            clearTargets();
            scheduleRefresh(100);
        }, 80);
    }

    function finishNewBoxInside(beforeKeys, targetKey) {
        window.setTimeout(function () {
            const $newBox = findNewRow(beforeKeys, 'container');
            const $target = rowByKey(targetKey);
            if (!$newBox.length) { scheduleRefresh(100); return; }
            if (!isBox($newBox)) { configureBox($newBox); }
            if ($target.length && canMoveIntoBox($newBox, $target)) {
                moveRowIntoBox($newBox, $target);
            } else {
                scheduleRefresh(100);
            }
        }, 80);
    }

    function finishNewBoxInAuto(beforeKeys, targetKey) {
        window.setTimeout(function () {
            const $newBox = findNewRow(beforeKeys, 'container');
            const $target = rowByKey(targetKey);
            if (!$newBox.length) { scheduleRefresh(100); return; }
            if (!isBox($newBox)) { configureBox($newBox); }
            if ($target.length && canMoveBoxIntoAuto($newBox, $target)) {
                moveBoxIntoAuto($newBox, $target);
            } else {
                scheduleRefresh(100);
            }
        }, 80);
    }

    function finishNewBoxBeside(beforeKeys, targetKey, side) {
        window.setTimeout(function () {
            const $newBox = findNewRow(beforeKeys, 'container');
            if (!$newBox.length) { scheduleRefresh(100); return; }
            if (!isBox($newBox)) { configureBox($newBox); }
            const $target = rowByKey(targetKey);
            if ($target.length) { placeBoxBeside($newBox, $target, side); }
            else { scheduleRefresh(100); }
        }, 80);
    }

    function resolveNewBoxDrop(event, state) {
        const sideZone = event.target && event.target.closest ? event.target.closest('.h18-v0811-side-zone') : null;
        if (sideZone) {
            state.mode = 'side';
            state.target = String(sideZone.getAttribute('data-box') || '');
            state.side = String(sideZone.getAttribute('data-side') || 'right');
            return;
        }
        const $box = targetBoxForElement(event.target);
        if ($box.length && canAcceptNewBox($box)) {
            state.mode = 'inside';
            state.target = rowKey($box);
            return;
        }
        const $auto = targetAutoForElement(event.target);
        if ($auto.length) {
            state.mode = 'auto';
            state.target = rowKey($auto);
            return;
        }
        state.mode = '';
        state.target = '';
    }

    document.addEventListener('dragstart', function (event) {
        const item = event.target.closest && event.target.closest('.h18-builder-palette-item');
        if (!item) { return; }
        suppressPaletteClickUntil = Date.now() + 500;
        const tool = String(item.getAttribute('data-h18-layout-tool') || item.getAttribute('data-h18-v0813-drag-tool') || '');
        const type = String(item.getAttribute('data-section-type') || 'text');
        if (tool === 'box' || (type === 'container' && (!tool || tool === 'box'))) {
            paletteBoxDrag = { before: snapshotKeys(), mode: '', target: '', side: 'right', dropHandled: false };
            $sections.addClass('h18-v0811-box-drag');
            scheduleRefresh(0);
            return;
        }
        if (tool) { return; }
        pendingDrag = { type: type, before: snapshotKeys(), boxKey: '', dropHandled: false };
    }, true);

    document.addEventListener('dragover', function (event) {
        if (paletteBoxDrag) {
            resolveNewBoxDrop(event, paletteBoxDrag);
            if (paletteBoxDrag.mode === 'side') {
                const zone = event.target.closest && event.target.closest('.h18-v0811-side-zone');
                if (zone) { event.preventDefault(); showSideTarget(zone); }
            } else if (paletteBoxDrag.mode === 'inside') {
                const $box = rowByKey(paletteBoxDrag.target);
                if ($box.length) { event.preventDefault(); showBoxTarget($box); }
            } else if (paletteBoxDrag.mode === 'auto') {
                const $auto = rowByKey(paletteBoxDrag.target);
                if ($auto.length) { event.preventDefault(); showAutoTarget($auto); }
            } else {
                clearTargets();
            }
            return;
        }
        if (!pendingDrag) { return; }
        const $box = targetBoxForElement(event.target);
        pendingDrag.boxKey = $box.length ? rowKey($box) : '';
        if ($box.length) { event.preventDefault(); }
        showBoxTarget($box);
    }, true);

    document.addEventListener('drop', function (event) {
        if (paletteBoxDrag) {
            const state = paletteBoxDrag;
            resolveNewBoxDrop(event, state);
            state.dropHandled = true;
            if (state.mode === 'side' || state.mode === 'inside' || state.mode === 'auto') { event.preventDefault(); }
            if (state.mode === 'side' && state.target) {
                finishNewBoxBeside(state.before, state.target, state.side);
            } else if (state.mode === 'inside' && state.target) {
                finishNewBoxInside(state.before, state.target);
            } else if (state.mode === 'auto' && state.target) {
                finishNewBoxInAuto(state.before, state.target);
            } else {
                finishNewBoxStandalone(state.before);
            }
            clearTargets();
            return;
        }
        if (!pendingDrag) { return; }
        const state = pendingDrag;
        const $box = targetBoxForElement(event.target);
        const boxKey = $box.length ? rowKey($box) : state.boxKey;
        state.dropHandled = true;
        if (boxKey) {
            event.preventDefault();
            finishNewNested(state.before, state.type, boxKey);
        } else {
            clearTargets();
            scheduleRefresh(100);
        }
    }, true);

    document.addEventListener('dragend', function () {
        if (paletteBoxDrag) {
            const state = paletteBoxDrag;
            paletteBoxDrag = null;
            $sections.removeClass('h18-v0811-box-drag');
            if (!state.dropHandled) {
                finishNewBoxStandalone(state.before);
            }
        }
        if (pendingDrag) {
            const state = pendingDrag;
            pendingDrag = null;
            if (!state.dropHandled) { clearTargets(); }
        }
        clearTargets();
        scheduleRefresh(100);
    }, true);

    document.addEventListener('click', function (event) {
        const item = event.target.closest && event.target.closest('.h18-builder-palette-item');
        if (!item) { return; }
        if (Date.now() < suppressPaletteClickUntil) {
            event.preventDefault();
            event.stopPropagation();
            if (typeof event.stopImmediatePropagation === 'function') { event.stopImmediatePropagation(); }
            return;
        }
        if (item.hasAttribute('data-h18-layout-tool')) { return; }
        const $selected = activeRows().filter('.is-selected').first();
        if (!isBox($selected)) { return; }
        finishNewNested(snapshotKeys(), String(item.getAttribute('data-section-type') || 'text'), rowKey($selected));
    }, true);

    $sections.on('sortstart.h18V0811Kasse', function (event, ui) {
        const $row = ui && ui.item ? ui.item : $();
        existingDragRow = $row;
        existingDropBoxKey = '';
        if (isBox($row)) {
            existingBoxDrag = { source: rowKey($row), mode: '', target: '', side: 'right' };
            $sections.addClass('h18-v0811-box-drag');
            scheduleRefresh(0);
        } else if ($row.length) {
            $sections.addClass('h18-ud-existing-row-drag');
        }
    });

    $sections.on('sort.h18V0811Kasse', function (event) {
        if (existingBoxDrag) {
            const $source = rowByKey(existingBoxDrag.source);
            const sideHit = sideZoneAtPoint(event.pageX, event.pageY, existingBoxDrag.source);
            if (sideHit) {
                existingBoxDrag.mode = 'side';
                existingBoxDrag.target = sideHit.target;
                existingBoxDrag.side = sideHit.side;
                showSideTarget(sideHit.node);
                return;
            }
            const $box = boxAtPoint(event.pageX, event.pageY, $source);
            if ($box.length) {
                existingBoxDrag.mode = 'inside';
                existingBoxDrag.target = rowKey($box);
                showBoxTarget($box);
                return;
            }
            const $auto = autoAtPoint(event.pageX, event.pageY, $source);
            if ($auto.length) {
                existingBoxDrag.mode = 'auto';
                existingBoxDrag.target = rowKey($auto);
                showAutoTarget($auto);
            } else {
                existingBoxDrag.mode = '';
                existingBoxDrag.target = '';
                clearTargets();
            }
            return;
        }
        if (!existingDragRow.length) { return; }
        const $box = boxAtPoint(event.pageX, event.pageY, existingDragRow);
        existingDropBoxKey = $box.length ? rowKey($box) : '';
        showBoxTarget($box);
    });

    $sections.on('sortstop.h18V0811Kasse', function () {
        if (existingBoxDrag) {
            const state = existingBoxDrag;
            existingBoxDrag = null;
            $sections.removeClass('h18-v0811-box-drag');
            clearTargets();
            const $source = rowByKey(state.source);
            const $target = rowByKey(state.target);
            if (state.mode === 'side' && $target.length) {
                placeBoxBeside($source, $target, state.side);
            } else if (state.mode === 'inside' && $target.length) {
                moveRowIntoBox($source, $target);
            } else if (state.mode === 'auto' && $target.length) {
                moveBoxIntoAuto($source, $target);
            } else {
                scheduleRefresh(100);
            }
            existingDragRow = $();
            return;
        }
        const $row = existingDragRow;
        const boxKey = existingDropBoxKey;
        existingDragRow = $();
        existingDropBoxKey = '';
        $sections.removeClass('h18-ud-existing-row-drag');
        if ($row.length && boxKey) {
            const $box = rowByKey(boxKey);
            if ($box.length) { moveRowIntoBox($row, $box); }
        }
        clearTargets();
        scheduleRefresh(100);
    });

    $(document).on('click', '.h18-v0811-edit-child', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $row = rowByKey($(this).attr('data-h18-v0811-edit-child'));
        if ($row.length) { $row.children('.h18-page-section-header').trigger('click'); }
        scheduleRefresh(100);
    });

    $(document).on('change input', '.h18-layout-parent-key,.h18-layout-parent-select,.h18-section-navigator-label', function () { scheduleRefresh(100); });
    $(document).on('input change', '#h18-page-inspector-target :input', function () { scheduleRefresh(120); });
    $(document).on('click', '.h18-preview-device,.h18-preview-state,.h18-page-section-delete,.h18-page-section-duplicate,.h18-page-section-header,.h18-page-section-edit', function () { scheduleRefresh(120); });

    const observer = new MutationObserver(function () {
        if (!renderGuard) { scheduleRefresh(100); }
    });
    observer.observe($sections.get(0), { childList: true, subtree: false });

    scheduleRefresh(140);
});
