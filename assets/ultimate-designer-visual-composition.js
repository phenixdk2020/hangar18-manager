jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    if (!$sections.length) {
        return;
    }

    const AUTO_LABEL = 'Auto-kasser';
    const BOX_LABEL = 'Kasse';
    let refreshTimer = null;
    let proxyDrag = null;
    let newBoxBeforeKeys = new Set();
    let newBoxSideTarget = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($('#h18-page-inspector-target').find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '');
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '');
    }

    function rowByKey(key) {
        key = String(key || '');
        if (!key) { return $(); }
        return activeRows().filter(function () {
            return rowKey($(this)) === key;
        }).first();
    }

    function isBox($row) {
        return !!($row && $row.length && rowType($row) === 'container' && rowLabel($row).indexOf(BOX_LABEL) === 0);
    }

    function isAutoRow($row) {
        return !!($row && $row.length && rowType($row) === 'grid' && rowLabel($row) === AUTO_LABEL);
    }

    function directChildren($parent) {
        const key = rowKey($parent);
        if (!key) { return $(); }
        return activeRows().filter(function () {
            return parentKey($(this)) === key;
        });
    }

    function childBoxes($autoRow) {
        return directChildren($autoRow).filter(function () {
            return isBox($(this));
        });
    }

    function parentRow($row) {
        return rowByKey(parentKey($row));
    }

    function parentAuto($row) {
        const $parent = parentRow($row);
        return isAutoRow($parent) ? $parent : $();
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
        let $found = $();
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (key && !beforeKeys.has(key) && (!type || rowType($row) === type)) {
                $found = $row;
            }
        });
        return $found;
    }

    function setParent($row, key) {
        if (!$row || !$row.length) { return false; }
        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if (!$hidden.length) { return false; }
        $hidden.val(String(key || '')).trigger('change');
        if ($select.length) {
            $select.val(String(key || '')).trigger('change');
        }
        return true;
    }

    function syncFlatOrder() {
        let visibleIndex = 0;
        $sections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            visibleIndex += 1;
            $row.find('.h18-page-section-order').val(visibleIndex * 10);
        });
        if ($sections.hasClass('ui-sortable')) {
            $sections.sortable('refresh');
        }
    }

    function syncAutoColumns($autoRow) {
        if (!isAutoRow($autoRow)) { return; }
        const count = childBoxes($autoRow).length;
        const columns = Math.max(1, Math.min(6, count || 1));
        const $desktop = controls($autoRow, '[name$="[LayoutColumns]"]').first();
        const $mobile = controls($autoRow, '[name$="[MobileLayoutColumns]"]').first();
        if ($desktop.length && String($desktop.val()) !== String(columns)) {
            $desktop.val(String(columns)).trigger('input').trigger('change');
        }
        if ($mobile.length && !String($mobile.val() || '').trim()) {
            $mobile.val('1').trigger('change');
        }
    }

    function displayName($row) {
        const nav = rowLabel($row);
        if (nav && nav !== BOX_LABEL) { return nav; }
        const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
        if (title) { return title; }
        const map = {
            text: 'Tekst', image: 'Billede', buttons: 'Knap', hero: 'Hero', text_image: 'Tekst + billede',
            container: 'Kasse', grid: 'Grid', flex: 'Flex', html: 'HTML', shortcode: 'Shortcode', embed: 'Embed',
            divider: 'Skillelinje', spacer: 'Spacer', list: 'Liste', quote: 'Citat', card: 'Kort', card_grid: 'Kort-grid'
        };
        return map[rowType($row)] || rowType($row) || 'Element';
    }

    function cleanPreviewClone($row) {
        const $source = $row.children('.h18-canvas-preview').first();
        if (!$source.length) { return $(); }
        const $clone = $source.clone(false, false);
        $clone.removeAttr('id');
        $clone.find('[id]').removeAttr('id');
        $clone.find('[name]').removeAttr('name');
        $clone.find('.h18-ud-auto-box-canvas').remove();
        $clone.find('input,select,textarea,button').prop('disabled', true).attr('tabindex', '-1');
        $clone.find('a').attr('tabindex', '-1');
        $clone.addClass('h18-ud-vc-preview-clone');
        return $clone;
    }

    function editRow(key) {
        const $row = rowByKey(key);
        if (!$row.length) { return; }
        const $header = $row.children('.h18-page-section-header').first();
        if ($header.length) {
            $header.trigger('click');
        } else {
            $row.trigger('click');
        }
    }

    function renderBoxComposition($box) {
        if (!isBox($box)) { return; }
        const key = rowKey($box);
        const $preview = $box.children('.h18-canvas-preview').first();
        const $native = $preview.find('.h18-ud-box-contents-preview').first();
        if (!$native.length) { return; }

        const $children = directChildren($box);
        const signature = $children.map(function () { return rowKey($(this)); }).get().join('|');
        const $items = $native.find('.h18-ud-box-contents-items').first();
        if (!$items.length) { return; }

        $native.find('.h18-ud-box-drop-zone').attr('data-h18-vc-box-key', key);
        if ($items.attr('data-h18-vc-signature') === signature && $items.hasClass('h18-ud-vc-owned-root')) {
            return;
        }

        $items.empty().addClass('h18-ud-vc-owned-root h18-ud-vc-box-child-list').attr('data-h18-vc-signature', signature);
        if (!$children.length) {
            $items.append($('<div>', {
                class: 'h18-ud-vc-empty h18-ud-vc-owned',
                text: 'Kassen er tom. Træk et element ned på feltet herunder.'
            }));
            return;
        }

        $children.each(function () {
            const $child = $(this);
            const childKey = rowKey($child);
            const $card = $('<section>', {
                class: 'h18-ud-vc-child-card h18-ud-vc-owned',
                draggable: 'true',
                'data-h18-vc-child-key': childKey
            });
            const $bar = $('<div>', { class: 'h18-ud-vc-card-bar' }).append(
                $('<span>', { class: 'dashicons dashicons-move h18-ud-vc-drag-icon', 'aria-hidden': 'true' }),
                $('<strong>', { text: displayName($child) }),
                $('<small>', { text: rowType($child) || 'element' }),
                $('<button>', { type: 'button', class: 'button button-small h18-ud-vc-edit', 'data-h18-vc-edit-key': childKey, text: 'Rediger' })
            );
            const $body = $('<div>', { class: 'h18-ud-vc-card-preview' });
            const $clone = cleanPreviewClone($child);
            if ($clone.length) {
                $body.append($clone);
            } else {
                $body.append($('<div>', { class: 'h18-ud-vc-empty', text: displayName($child) }));
            }
            $card.append($bar, $body);
            $items.append($card);
        });
    }

    function renderAutoComposition($autoRow) {
        if (!isAutoRow($autoRow)) { return; }
        syncAutoColumns($autoRow);
        const $boxes = childBoxes($autoRow);
        const signature = $boxes.map(function () { return rowKey($(this)); }).get().join('|');
        const $preview = $autoRow.children('.h18-canvas-preview').first();
        const $grid = $preview.find('.h18-ud-auto-box-grid').first();
        if (!$grid.length) { return; }

        if ($grid.attr('data-h18-vc-signature') === signature && $grid.hasClass('h18-ud-vc-owned-root')) {
            return;
        }

        $grid.empty().addClass('h18-ud-vc-owned-root h18-ud-vc-auto-grid').attr({
            'data-h18-vc-signature': signature,
            'data-h18-vc-auto-key': rowKey($autoRow)
        });

        if (!$boxes.length) {
            $grid.append($('<div>', {
                class: 'h18-ud-vc-empty h18-ud-vc-owned',
                text: 'Ingen Kasser i rækken endnu. Træk en Kasse ind i Auto-kasser.'
            }));
            return;
        }

        $boxes.each(function (index) {
            const $box = $(this);
            const key = rowKey($box);
            const $tile = $('<section>', {
                class: 'h18-ud-vc-box-tile h18-ud-vc-owned',
                draggable: 'true',
                'data-h18-box-key': key
            });
            const $bar = $('<div>', { class: 'h18-ud-vc-card-bar h18-ud-vc-box-bar' }).append(
                $('<span>', { class: 'dashicons dashicons-move h18-ud-vc-drag-icon', 'aria-hidden': 'true' }),
                $('<strong>', { text: rowLabel($box) === BOX_LABEL ? ('Kasse ' + (index + 1)) : displayName($box) }),
                $('<small>', { text: directChildren($box).length + ' element' + (directChildren($box).length === 1 ? '' : 'er') }),
                $('<button>', { type: 'button', class: 'button button-small h18-ud-vc-edit', 'data-h18-vc-edit-key': key, text: 'Rediger Kasse' })
            );
            const $body = $('<div>', { class: 'h18-ud-vc-box-preview' });
            const $clone = cleanPreviewClone($box);
            if ($clone.length) {
                $body.append($clone);
            }
            $tile.append($bar, $body);
            $grid.append($tile);
        });
    }

    function decorateTopLevelBoxDropZones($box) {
        if (!isBox($box) || parentKey($box)) { return; }
        const $preview = $box.children('.h18-canvas-preview').first();
        if (!$preview.length || $preview.children('.h18-ud-vc-side-drop-zones').length) { return; }
        $preview.append($('<div>', { class: 'h18-ud-vc-side-drop-zones h18-ud-vc-owned' }).append(
            $('<div>', { class: 'h18-ud-vc-side-drop-zone is-left', 'data-h18-vc-side': 'left', 'data-h18-vc-target-box': rowKey($box), text: '← Sæt Kasse ved siden af' }),
            $('<div>', { class: 'h18-ud-vc-side-drop-zone is-right', 'data-h18-vc-side': 'right', 'data-h18-vc-target-box': rowKey($box), text: 'Sæt Kasse ved siden af →' })
        ));
    }

    function normalizeAutoRowPosition($autoRow) {
        const $boxes = childBoxes($autoRow);
        if (!$boxes.length) { return false; }
        const autoIndex = $autoRow.index();
        let minIndex = Number.POSITIVE_INFINITY;
        let $first = $();
        $boxes.each(function () {
            const $box = $(this);
            if ($box.index() < minIndex) {
                minIndex = $box.index();
                $first = $box;
            }
        });
        if ($first.length && autoIndex > minIndex) {
            $autoRow.insertBefore($first);
            return true;
        }
        return false;
    }

    function applySourceVisibility() {
        activeRows().removeClass('h18-ud-vc-source-hidden');
        activeRows().each(function () {
            const $row = $(this);
            const $parent = parentRow($row);
            if (isBox($parent) || isAutoRow($parent)) {
                $row.addClass('h18-ud-vc-source-hidden');
            }
        });
    }

    function refreshComposition() {
        refreshTimer = null;
        let moved = false;

        activeRows().removeClass('h18-ud-vc-source-hidden');

        activeRows().each(function () {
            const $row = $(this);
            if (isBox($row)) {
                renderBoxComposition($row);
                decorateTopLevelBoxDropZones($row);
            }
        });

        activeRows().each(function () {
            const $row = $(this);
            if (isAutoRow($row)) {
                moved = normalizeAutoRowPosition($row) || moved;
                renderAutoComposition($row);
            }
        });

        if (moved) {
            syncFlatOrder();
        }
        applySourceVisibility();
    }

    function scheduleRefresh(delay) {
        if (refreshTimer) {
            window.clearTimeout(refreshTimer);
        }
        refreshTimer = window.setTimeout(refreshComposition, typeof delay === 'number' ? delay : 90);
    }

    function targetBoxFromElement(element) {
        if (!element || !element.closest) { return $(); }
        const proxy = element.closest('[data-h18-box-key]');
        if (proxy) {
            const $proxyBox = rowByKey(proxy.getAttribute('data-h18-box-key'));
            if (isBox($proxyBox)) { return $proxyBox; }
        }
        const zone = element.closest('[data-h18-vc-box-key]');
        if (zone) {
            const $zoneBox = rowByKey(zone.getAttribute('data-h18-vc-box-key'));
            if (isBox($zoneBox)) { return $zoneBox; }
        }
        const row = element.closest('.h18-page-section-row');
        if (!row) { return $(); }
        const $row = $(row);
        return isBox($row) ? $row : $();
    }

    function moveChildToBox(childKey, boxKey) {
        const $child = rowByKey(childKey);
        const $box = rowByKey(boxKey);
        if (!$child.length || !isBox($box) || isBox($child) || rowKey($child) === rowKey($box)) { return; }

        const $existing = directChildren($box).not($child);
        const $anchor = $existing.length ? $existing.last() : $box;
        $child.insertAfter($anchor);
        setParent($child, boxKey);
        syncFlatOrder();
        $child.addClass('h18-ud-just-nested');
        window.setTimeout(function () { $child.removeClass('h18-ud-just-nested'); }, 900);
        scheduleRefresh(30);
    }

    function reorderBoxWithinAuto(boxKey, targetKey, side) {
        const $box = rowByKey(boxKey);
        const $target = rowByKey(targetKey);
        if (!isBox($box) || !isBox($target) || rowKey($box) === rowKey($target)) { return; }
        const $targetAuto = parentAuto($target);
        if (!$targetAuto.length) { return; }
        setParent($box, rowKey($targetAuto));
        if (side === 'left') {
            $box.insertBefore($target);
        } else {
            $box.insertAfter($target);
        }
        syncAutoColumns($targetAuto);
        syncFlatOrder();
        scheduleRefresh(30);
    }

    $(document).on('click', '.h18-ud-vc-edit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        editRow(String($(this).attr('data-h18-vc-edit-key') || ''));
    });

    $(document).on('dragstart', '.h18-ud-vc-child-card', function (event) {
        const key = String($(this).attr('data-h18-vc-child-key') || '');
        if (!key) { return; }
        proxyDrag = { kind: 'child', key: key };
        const original = event.originalEvent;
        if (original && original.dataTransfer) {
            original.dataTransfer.effectAllowed = 'move';
            original.dataTransfer.setData('text/plain', key);
        }
        $sections.addClass('h18-ud-vc-proxy-dragging');
    });

    $(document).on('dragstart', '.h18-ud-vc-box-tile', function (event) {
        const key = String($(this).attr('data-h18-box-key') || '');
        if (!key) { return; }
        proxyDrag = { kind: 'box', key: key };
        const original = event.originalEvent;
        if (original && original.dataTransfer) {
            original.dataTransfer.effectAllowed = 'move';
            original.dataTransfer.setData('text/plain', key);
        }
        $sections.addClass('h18-ud-vc-proxy-dragging');
    });

    $(document).on('dragover', '.h18-ud-vc-box-tile, .h18-ud-box-drop-zone', function (event) {
        if (!proxyDrag) { return; }
        const $target = targetBoxFromElement(event.target);
        if (!$target.length || rowKey($target) === proxyDrag.key) { return; }
        event.preventDefault();
        $('.h18-ud-vc-drop-active').removeClass('h18-ud-vc-drop-active');
        $(this).addClass('h18-ud-vc-drop-active');
    });

    $(document).on('drop', '.h18-ud-vc-box-tile, .h18-ud-box-drop-zone', function (event) {
        if (!proxyDrag) { return; }
        const current = proxyDrag;
        const $target = targetBoxFromElement(event.target);
        if (!$target.length || rowKey($target) === current.key) { return; }
        event.preventDefault();
        event.stopPropagation();
        if (current.kind === 'child') {
            moveChildToBox(current.key, rowKey($target));
        } else if (current.kind === 'box') {
            const rect = this.getBoundingClientRect ? this.getBoundingClientRect() : null;
            const original = event.originalEvent;
            const x = original ? original.clientX : 0;
            const side = rect && x < rect.left + (rect.width / 2) ? 'left' : 'right';
            reorderBoxWithinAuto(current.key, rowKey($target), side);
        }
        proxyDrag = null;
        $('.h18-ud-vc-drop-active').removeClass('h18-ud-vc-drop-active');
        $sections.removeClass('h18-ud-vc-proxy-dragging');
    });

    $(document).on('dragend', '.h18-ud-vc-child-card, .h18-ud-vc-box-tile', function () {
        proxyDrag = null;
        $('.h18-ud-vc-drop-active').removeClass('h18-ud-vc-drop-active');
        $sections.removeClass('h18-ud-vc-proxy-dragging');
        scheduleRefresh(30);
    });

    document.addEventListener('dragstart', function (event) {
        const item = event.target.closest && event.target.closest('.h18-builder-palette-item[data-h18-layout-tool="box"]');
        if (!item) { return; }
        newBoxBeforeKeys = snapshotKeys();
        newBoxSideTarget = null;
        $sections.addClass('h18-ud-vc-new-box-dragging');
    }, true);

    document.addEventListener('dragover', function (event) {
        if (!$sections.hasClass('h18-ud-vc-new-box-dragging')) { return; }
        const zone = event.target.closest && event.target.closest('.h18-ud-vc-side-drop-zone');
        $('.h18-ud-vc-side-drop-zone').removeClass('is-active');
        if (zone) {
            zone.classList.add('is-active');
            newBoxSideTarget = {
                key: String(zone.getAttribute('data-h18-vc-target-box') || ''),
                side: String(zone.getAttribute('data-h18-vc-side') || 'right')
            };
        }
    }, true);

    document.addEventListener('drop', function (event) {
        if (!$sections.hasClass('h18-ud-vc-new-box-dragging')) { return; }
        const zone = event.target.closest && event.target.closest('.h18-ud-vc-side-drop-zone');
        if (zone) {
            newBoxSideTarget = {
                key: String(zone.getAttribute('data-h18-vc-target-box') || ''),
                side: String(zone.getAttribute('data-h18-vc-side') || 'right')
            };
        }
        window.setTimeout(function () {
            const $newBox = findNewRow(newBoxBeforeKeys, 'container');
            if ($newBox.length && newBoxSideTarget && newBoxSideTarget.key) {
                const $target = rowByKey(newBoxSideTarget.key);
                const $auto = parentAuto($target);
                if ($auto.length && parentKey($newBox) === rowKey($auto)) {
                    if (newBoxSideTarget.side === 'left') {
                        $newBox.insertBefore($target);
                    } else {
                        $newBox.insertAfter($target);
                    }
                    syncFlatOrder();
                }
            }
            $sections.removeClass('h18-ud-vc-new-box-dragging');
            $('.h18-ud-vc-side-drop-zone').removeClass('is-active');
            newBoxSideTarget = null;
            scheduleRefresh(40);
        }, 140);
    }, true);

    document.addEventListener('dragend', function () {
        if (!$sections.hasClass('h18-ud-vc-new-box-dragging')) { return; }
        $sections.removeClass('h18-ud-vc-new-box-dragging');
        $('.h18-ud-vc-side-drop-zone').removeClass('is-active');
        newBoxSideTarget = null;
        scheduleRefresh(50);
    }, true);

    $(document).on('input change', '#h18-page-sections-sortable input, #h18-page-sections-sortable select, #h18-page-sections-sortable textarea, #h18-page-inspector-target input, #h18-page-inspector-target select, #h18-page-inspector-target textarea', function () {
        scheduleRefresh(110);
    });
    $(document).on('click', '.h18-page-section-delete, .h18-page-section-duplicate, .h18-builder-palette-item, .h18-layout-parent-select', function () {
        scheduleRefresh(140);
    });

    const observer = new MutationObserver(function (mutations) {
        let externalChange = false;
        mutations.forEach(function (mutation) {
            const $target = $(mutation.target);
            if (!$target.closest('.h18-ud-vc-owned-root, .h18-ud-vc-owned').length) {
                externalChange = true;
            }
        });
        if (externalChange) {
            scheduleRefresh(90);
        }
    });
    observer.observe($sections.get(0), { childList: true, subtree: true });

    scheduleRefresh(160);
});
