jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    if (!$sections.length) { return; }

    const OVERLAY_CLASS = 'h18-v0838-drop-overlay';
    const ZONE_CLASS = 'h18-v0838-drop-zone';
    let dragSourceKey = '';
    let dragSourceType = '';
    let dragMode = '';
    let refreshTimer = null;

    function activeRows() { return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)'); }
    function rowKey($row) { return String($row.find('.h18-page-section-key').first().val() || $row.attr('data-key') || ''); }
    function rowType($row) { return String($row.attr('data-section-type') || $row.find('.h18-page-section-type').first().val() || ''); }
    function parentKey($row) {
        let $field = $row.find('.h18-layout-parent-key').first();
        if (!$field.length && $row.hasClass('is-selected')) { $field = $('#h18-page-inspector-target .h18-layout-parent-key').first(); }
        return String($field.val() || '');
    }
    function rowLabel($row) {
        let $field = $row.find('.h18-section-navigator-label').first();
        if (!$field.length && $row.hasClass('is-selected')) { $field = $('#h18-page-inspector-target .h18-section-navigator-label').first(); }
        return String($field.val() || '').trim();
    }
    function rowByKey(key) {
        const requested = String(key || '');
        return activeRows().filter(function () { return rowKey($(this)) === requested; }).first();
    }
    function isAuto($row) {
        if (!$row || !$row.length || rowType($row) !== 'grid') { return false; }
        return rowLabel($row) === 'Auto-kasser';
    }
    function isBox($row) {
        if (!$row || !$row.length || rowType($row) !== 'container') { return false; }
        return String($row.attr('data-h18-box') || '') === '1' || rowLabel($row).indexOf('Kasse') === 0;
    }
    function clearOverlays() {
        $('.' + OVERLAY_CLASS).remove();
        $sections.removeClass('h18-v0838-drop-zones-active h18-v0838-box-source h18-v0838-element-source');
    }
    function labelFor(position) {
        if (position === 'over') { return 'Over'; }
        if (position === 'under') { return 'Under'; }
        if (position === 'left') { return 'Venstre'; }
        if (position === 'right') { return 'Højre'; }
        if (position === 'inside') { return 'Ind i kassen'; }
        return '';
    }
    function zone(position, targetKey, sideCompatible) {
        const classes = [ZONE_CLASS, 'is-' + position];
        const attrs = {
            class: classes.join(' '),
            'data-h18-v0838-position': position,
            'data-h18-v0838-target': targetKey,
            'aria-label': position === 'inside' ? 'Placér inde i Kassen' : 'Placér ' + labelFor(position).toLowerCase() + ' for målet'
        };
        if ((position === 'left' || position === 'right') && sideCompatible) {
            classes.push('h18-v0811-side-zone');
            attrs.class = classes.join(' ');
            attrs['data-side'] = position;
            attrs['data-box'] = targetKey;
            attrs['data-h18-v0838-existing-placement-contract'] = '1';
            attrs['data-h18-v0840-generic-side-contract'] = '1';
        } else if (position === 'left' || position === 'right') {
            classes.push('is-disabled');
            attrs.class = classes.join(' ');
            attrs['aria-disabled'] = 'true';
        }
        if (position === 'inside') {
            attrs['data-h18-v0870-inside-kasse'] = targetKey;
        }
        return $('<div>', attrs).append($('<span>', { class: 'h18-v0838-drop-zone-label', text: labelFor(position) }));
    }
    function canSideTarget($target) {
        if (!$target || !$target.length || isAuto($target) || dragSourceType === 'grid') { return false; }
        const targetParentKey = parentKey($target);
        if (!targetParentKey) { return true; }
        return isAuto(rowByKey(targetParentKey));
    }
    function addZones($overlay, key, $target, sideCompatible) {
        $overlay.append(zone('over', key, false), zone('under', key, false), zone('left', key, sideCompatible), zone('right', key, sideCompatible));
        if (dragSourceType !== 'container' && dragSourceType !== 'grid' && dragSourceType !== 'flex' && isBox($target)) {
            $overlay.append(zone('inside', key, false));
        }
    }
    function addRowOverlay($row) {
        const key = rowKey($row);
        if (!key || key === dragSourceKey || $row.attr('data-h18-v0811-child-source') === '1') { return; }
        const sideCompatible = canSideTarget($row);
        const $preview = $row.children('.h18-canvas-preview').first();
        const $host = $preview.length ? $preview : $row;
        if (!$host.length || !$host.is(':visible')) { return; }
        $host.css('position', $host.css('position') === 'static' ? 'relative' : $host.css('position'));
        const $overlay = $('<div>', {
            class: OVERLAY_CLASS,
            'data-h18-v0838-target': key,
            'data-h18-v0838-target-kind': rowType($row),
            'aria-hidden': 'true'
        });
        addZones($overlay, key, $row, sideCompatible);
        $host.append($overlay);
    }

    function addNestedProxyOverlays() {
        if (dragSourceType === 'grid') { return; }
        $('.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]').each(function () {
            const $proxy = $(this);
            const key = String($proxy.attr('data-h18-v0811-row') || $proxy.attr('data-h18-v0811-child') || $proxy.attr('data-h18-v0811-box') || '');
            if (!key || key === dragSourceKey || $proxy.children('.' + OVERLAY_CLASS).length) { return; }
            const $target = rowByKey(key);
            if (!$target.length) { return; }
            const sideCompatible = canSideTarget($target);
            $proxy.css('position', $proxy.css('position') === 'static' ? 'relative' : $proxy.css('position'));
            const $overlay = $('<div>', {
                class: OVERLAY_CLASS + ' h18-v0838-auto-proxy-overlay h18-v0851-nested-proxy-overlay',
                'data-h18-v0838-target': key,
                'aria-hidden': 'true'
            });
            addZones($overlay, key, $target, sideCompatible);
            $proxy.append($overlay);
        });
    }

    function renderOverlays() {
        clearOverlays();
        if (!dragSourceKey) { return; }
        $sections.addClass('h18-v0838-drop-zones-active')
            .toggleClass('h18-v0838-box-source', dragSourceType === 'container')
            .toggleClass('h18-v0838-element-source', dragSourceType !== 'container');
        activeRows().each(function () { addRowOverlay($(this)); });
        addNestedProxyOverlays();
    }
    function scheduleRender(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(renderOverlays, typeof delay === 'number' ? delay : 20);
    }
    function hitZone(pageX, pageY) {
        const clientX = Number(pageX) - (window.pageXOffset || document.documentElement.scrollLeft || 0);
        const clientY = Number(pageY) - (window.pageYOffset || document.documentElement.scrollTop || 0);
        let match = null;
        $('.' + ZONE_CLASS + ':not(.is-disabled)').each(function () {
            const rect = this.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) { match = this; }
        });
        return match;
    }
    function highlightAt(pageX, pageY) {
        $('.' + ZONE_CLASS).removeClass('is-active');
        const hit = hitZone(pageX, pageY);
        if (hit) { $(hit).addClass('is-active'); }
    }

    $sections.on('sortstart.h18V0838DropZones', function (event, ui) {
        const $row = ui && ui.item ? ui.item : $();
        dragSourceKey = rowKey($row);
        dragSourceType = rowType($row);
        dragMode = dragSourceKey ? 'existing' : '';
        if (dragSourceKey) { scheduleRender(0); }
    });
    $sections.on('sort.h18V0838DropZones', function (event) {
        if (dragMode === 'existing') { highlightAt(event.pageX, event.pageY); }
    });
    $sections.on('sortstop.h18V0838DropZones', function () {
        dragSourceKey = ''; dragSourceType = ''; dragMode = '';
        window.setTimeout(clearOverlays, 0);
    });

    document.addEventListener('dragstart', function (event) {
        const item = event.target && event.target.closest ? event.target.closest('.h18-builder-palette-item') : null;
        if (!item) { return; }
        const type = String(item.getAttribute('data-section-type') || '');
        const tool = String(item.getAttribute('data-h18-layout-tool') || item.getAttribute('data-h18-v0813-drag-tool') || '');
        const boxSource = type === 'container' && (!tool || tool === 'box');
        if (tool && tool !== 'box') { return; }
        if (type === 'grid') { return; }
        dragSourceKey = boxSource ? '__new_box__' : '__new_element__';
        dragSourceType = boxSource ? 'container' : (type || 'text');
        dragMode = boxSource ? 'palette-box' : 'palette-element';
        scheduleRender(0);
    }, true);
    document.addEventListener('dragover', function (event) {
        if (dragMode !== 'palette-box' && dragMode !== 'palette-element') { return; }
        const x = typeof event.pageX === 'number' ? event.pageX : event.clientX + window.pageXOffset;
        const y = typeof event.pageY === 'number' ? event.pageY : event.clientY + window.pageYOffset;
        highlightAt(x, y);
    }, true);
    document.addEventListener('dragend', function () {
        if (dragMode !== 'palette-box' && dragMode !== 'palette-element') { return; }
        dragSourceKey = ''; dragSourceType = ''; dragMode = '';
        window.setTimeout(clearOverlays, 0);
    }, true);

    document.documentElement.setAttribute('data-h18-lego-drop-zones-runtime', '0.8.38');
    document.documentElement.setAttribute('data-h18-lego-side-by-side-runtime', '0.8.40');
    document.documentElement.setAttribute('data-h18-lego-nested-vertical-targets', '0.8.51');
    document.documentElement.setAttribute('data-h18-lego-inside-kasse-zone', '0.8.70');
    window.__h18LegoDropZonesV0838 = {
        version: '0.8.38', capabilityVersion: '0.8.70', refresh: renderOverlays, clear: clearOverlays,
        activeSource: function () { return { Key: dragSourceKey, Type: dragSourceType, Mode: dragMode }; },
        hitZone: hitZone
    };
    window.__h18LegoSideBySideV0840 = {
        version: '0.8.40', capabilityVersion: '0.8.70', refresh: renderOverlays, clear: clearOverlays,
        activeSource: function () { return { Key: dragSourceKey, Type: dragSourceType, Mode: dragMode }; }
    };
});
