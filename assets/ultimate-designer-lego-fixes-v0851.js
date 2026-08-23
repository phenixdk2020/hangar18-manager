(function () {
    'use strict';

    if (window.__h18LegoFixesV0851) { return; }

    const VERSION = '0.8.51';
    const HOTFIX_VERSION = '0.8.52';
    const config = window.H18LegoFixesV0851 || {};
    const STACK_FIELD_CLASS = 'h18-lego-stack-state-v0851-json';
    const STACK_SUBMIT_ATTR = 'data-h18-v0851-stack-submit';
    const CUSTOM_VALUE = '__h18_custom__';
    const LEGACY_PROMPTS = [
        'Træk en Kasse ind i Auto-kasser.',
        'Slip endnu en Kasse her for at tilføje den til Auto-kasser',
        'Slip en Kasse her for at tilføje den til Auto-kasser'
    ];

    let renderFrame = 0;
    let inspectorFrame = 0;
    let verticalDrag = null;
    let suppressObserverUntil = 0;

    function jq() { return window.jQuery || null; }
    function $sections() { const $ = jq(); return $ ? $('#h18-page-sections-sortable') : null; }
    function $form() { const $ = jq(); return $ ? $('#h18-page-editor-form') : null; }
    function $canvas() { const $ = jq(); return $ ? $('.h18-builder-canvas').first() : null; }
    function $inspectorTarget() { const $ = jq(); return $ ? $('#h18-page-inspector-target') : null; }

    function controls($row, selector) {
        const $ = jq();
        if (!$ || !$row || !$row.length) { return $ ? $() : null; }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) { $result = $result.add($inspectorTarget().find(selector)); }
        return $result;
    }

    function activeRows() {
        const $ = jq();
        const $s = $sections();
        return $ && $s && $s.length ? $s.children('.h18-page-section-row:not(.h18-page-section-removed)') : ($ ? $() : null);
    }

    function rowKey($row) {
        if (!$row || !$row.length) { return ''; }
        const $field = controls($row, '.h18-page-section-key').first();
        return String(($field && $field.length ? $field.val() : '') || $row.attr('data-key') || '').trim();
    }

    function rowType($row) {
        if (!$row || !$row.length) { return ''; }
        return String($row.attr('data-section-type') || controls($row, '.h18-page-section-type').first().val() || '').trim();
    }

    function parentKey($row) {
        if (!$row || !$row.length) { return ''; }
        return String(controls($row, '.h18-layout-parent-key').first().val() || '').trim();
    }

    function rowByKey(key) {
        const $ = jq();
        const wanted = String(key || '').trim();
        if (!$ || !wanted) { return $ ? $() : null; }
        return activeRows().filter(function () { return rowKey($(this)) === wanted; }).first();
    }

    function pageSlug() {
        const $f = $form();
        return $f && $f.length ? String($f.find('[name="page_slug"]').first().val() || '').trim() : '';
    }

    function canvasDevice() {
        const $c = $canvas();
        return $c && $c.length ? String($c.attr('data-canvas-device') || 'desktop').toLowerCase() : 'desktop';
    }

    function storedStackSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }

    function clampPercent(value) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed) || parsed <= 0) { return 0; }
        return Math.max(10, Math.min(90, parsed));
    }

    function normalizeStackState(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        return {
            SchemaVersion: 1,
            StackRootKey: String(raw.StackRootKey || '').trim(),
            StackOrder: Math.max(0, parseInt(raw.StackOrder, 10) || 0),
            DesktopPercent: clampPercent(raw.DesktopPercent),
            TabletPercent: clampPercent(raw.TabletPercent),
            MobilePercent: clampPercent(raw.MobilePercent)
        };
    }

    function stackField($row) {
        return controls($row, '.' + STACK_FIELD_CLASS).first();
    }

    function ensureStackField($row, initial) {
        const $ = jq();
        if (!$ || !$row || !$row.length) { return $ ? $() : null; }
        let $field = stackField($row);
        if ($field.length) { return $field; }
        const key = rowKey($row);
        const stored = storedStackSections();
        const state = normalizeStackState(initial || (key && stored[key] ? stored[key] : {}));
        $field = $('<input>', {
            type: 'hidden',
            class: STACK_FIELD_CLASS,
            value: JSON.stringify(state),
            'data-h18-v0851-stack-state': '1'
        });
        let $body = $row.children('.h18-page-section-body').first();
        if (!$body.length) { $body = $row.find('.h18-page-section-body').first(); }
        ($body.length ? $body : $row).append($field);
        return $field;
    }

    function stackState($row) {
        if (!$row || !$row.length) { return normalizeStackState({}); }
        const $field = ensureStackField($row);
        try { return normalizeStackState(JSON.parse(String($field.val() || '{}'))); }
        catch (error) { return normalizeStackState({}); }
    }

    function writeStackState($row, state, captureHistory) {
        if (!$row || !$row.length) { return null; }
        state = normalizeStackState(state);
        const $field = ensureStackField($row, state);
        $field.val(JSON.stringify(state));
        $row.attr('data-h18-v0851-stack-root', state.StackRootKey);
        $row.attr('data-h18-v0851-stack-order', String(state.StackOrder));
        if (captureHistory) { $field.trigger('input'); }
        return state;
    }

    function hydrateStackStates() {
        const $ = jq();
        const $rows = activeRows();
        if (!$ || !$rows) { return; }
        $rows.each(function () {
            const $row = $(this);
            writeStackState($row, stackState($row), false);
        });
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

    function syncFlatOrder() {
        const $ = jq();
        const $s = $sections();
        if (!$ || !$s || !$s.length) { return; }
        let index = 0;
        $s.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            index += 1;
            controls($row, '.h18-page-section-order').val(index * 10);
        });
        if ($s.hasClass('ui-sortable')) { $s.sortable('refresh'); }
    }

    function stackRowsForRoot(rootKey) {
        const $ = jq();
        const result = [];
        const root = String(rootKey || '');
        if (!$ || !root) { return $ ? $() : null; }
        activeRows().each(function () {
            const $row = $(this);
            const state = stackState($row);
            if (state.StackRootKey === root) { result.push($row); }
        });
        result.sort(function (a, b) { return stackState(a).StackOrder - stackState(b).StackOrder; });
        return $(result.map(function ($row) { return $row.get(0); }));
    }

    function clearStack($row, captureHistory) {
        if (!$row || !$row.length) { return; }
        const state = stackState($row);
        state.StackRootKey = '';
        state.StackOrder = 0;
        state.DesktopPercent = 0;
        state.TabletPercent = 0;
        state.MobilePercent = 0;
        writeStackState($row, state, captureHistory === true);
    }

    function nextStackOrder(rootKey) {
        const $ = jq();
        let max = 0;
        stackRowsForRoot(rootKey).each(function () { max = Math.max(max, stackState($(this)).StackOrder); });
        return max + 10;
    }

    function stackUnder(childKey, targetKey) {
        const $child = rowByKey(childKey);
        const $target = rowByKey(targetKey);
        if (!$child.length || !$target.length) { return false; }
        const parent = parentKey($target);
        if (!parent || parentKey($child) !== parent || rowType(rowByKey(parent)) !== 'grid') { return false; }
        const targetState = stackState($target);
        const rootKey = targetState.StackRootKey || rowKey($target);
        const state = stackState($child);
        state.StackRootKey = rootKey;
        state.StackOrder = nextStackOrder(rootKey);
        state.DesktopPercent = 0;
        state.TabletPercent = 0;
        state.MobilePercent = 0;
        writeStackState($child, state, true);
        scheduleRender();
        return true;
    }

    function stackOver(childKey, targetKey) {
        const $ = jq();
        const $child = rowByKey(childKey);
        const $target = rowByKey(targetKey);
        if (!$ || !$child.length || !$target.length) { return false; }
        const parent = parentKey($target);
        if (!parent || parentKey($child) !== parent || rowType(rowByKey(parent)) !== 'grid') { return false; }

        const targetState = stackState($target);
        const oldRootKey = targetState.StackRootKey || rowKey($target);
        const $oldRoot = rowByKey(oldRootKey);
        const existing = [];
        if ($oldRoot.length) { existing.push($oldRoot); }
        stackRowsForRoot(oldRootKey).each(function () { existing.push($(this)); });

        clearStack($child, false);
        let order = 10;
        existing.forEach(function ($row) {
            if (rowKey($row) === rowKey($child)) { return; }
            const state = stackState($row);
            state.StackRootKey = rowKey($child);
            state.StackOrder = order;
            state.DesktopPercent = 0;
            state.TabletPercent = 0;
            state.MobilePercent = 0;
            writeStackState($row, state, false);
            order += 10;
        });
        writeStackState($child, stackState($child), true);
        scheduleRender();
        return true;
    }

    function adoptUnder(newKey, targetKey, position) {
        const $ = jq();
        const $new = rowByKey(newKey);
        const $target = rowByKey(targetKey);
        if (!$ || !$new.length || !$target.length) { return false; }
        const parent = parentKey($target);
        if (!parent) { return false; }
        const $parent = rowByKey(parent);
        if (!$parent.length || ['container', 'flex', 'grid'].indexOf(rowType($parent)) === -1) { return false; }

        setParent($new, parent);
        if (position === 'over') {
            $new.insertBefore($target);
        } else {
            let $after = $target;
            const targetState = stackState($target);
            const rootKey = targetState.StackRootKey || rowKey($target);
            if (rowType($parent) === 'grid') { stackRowsForRoot(rootKey).each(function () { $after = $(this); }); }
            $new.insertAfter($after);
        }
        syncFlatOrder();

        if (rowType($parent) === 'grid') {
            if (position === 'over') { stackOver(rowKey($new), rowKey($target)); }
            else { stackUnder(rowKey($new), rowKey($target)); }
        } else {
            clearStack($new, true);
        }

        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') { nesting.refresh(); }
        scheduleRender();
        return true;
    }

    function removeLegacyPrompts(root) {
        const scope = root && root.querySelectorAll ? root : document;
        scope.querySelectorAll('.h18-v0814-auto-drop-zone,.h18-v0814-auto-kasse-drop,.h18-ud-auto-box-empty-drop').forEach(function (node) {
            const text = String(node.textContent || '').trim();
            if (LEGACY_PROMPTS.indexOf(text) !== -1 || /Auto-kasser/.test(text)) { node.classList.add('h18-v0851-hidden-legacy-drop'); }
        });
        scope.querySelectorAll('.h18-builder-canvas *').forEach(function (node) {
            if (node.children.length) { return; }
            if (LEGACY_PROMPTS.indexOf(String(node.textContent || '').trim()) !== -1) { node.classList.add('h18-v0851-hidden-legacy-drop'); }
        });
    }

    function visualTarget(node) {
        if (!node) { return null; }
        if (node.classList.contains('h18-v0811-auto-box')) {
            return node.querySelector('.h18-v0851-stack-root > .h18-v0811-auto-box-preview') || node.querySelector(':scope > .h18-v0811-auto-box-preview') || node;
        }
        if (node.classList.contains('h18-v0811-child-card')) { return node.querySelector(':scope > .h18-v0811-child-preview') || node; }
        return node;
    }

    function applySelectionOverlay() {
        suppressObserverUntil = Date.now() + 40;
        document.querySelectorAll('.h18-v0851-selection-overlay').forEach(function (node) { node.remove(); });
        document.querySelectorAll('.h18-v0851-selection-target').forEach(function (node) { node.classList.remove('h18-v0851-selection-target'); });
        document.querySelectorAll('.is-h18-v0848-selected-element').forEach(function (selected) {
            const target = visualTarget(selected);
            if (!target) { return; }
            target.classList.add('h18-v0851-selection-target');
            const overlay = document.createElement('span');
            overlay.className = 'h18-v0851-selection-overlay';
            overlay.setAttribute('aria-hidden', 'true');
            target.appendChild(overlay);
        });
    }

    function copyContainerDesign(sourceRow, target) {
        if (!sourceRow || !sourceRow.length || !target || !window.getComputedStyle) { return; }
        const preview = sourceRow.children('.h18-canvas-preview').first().get(0);
        if (!preview) { return; }
        const style = window.getComputedStyle(preview);
        target.style.backgroundColor = style.backgroundColor || 'transparent';
        target.style.backgroundImage = style.backgroundImage || 'none';
        target.style.borderTopWidth = style.borderTopWidth || '0px';
        target.style.borderRightWidth = style.borderRightWidth || '0px';
        target.style.borderBottomWidth = style.borderBottomWidth || '0px';
        target.style.borderLeftWidth = style.borderLeftWidth || '0px';
        target.style.borderStyle = style.borderTopStyle === 'none' && parseFloat(style.borderTopWidth || '0') > 0 ? 'solid' : style.borderTopStyle;
        target.style.borderColor = style.borderTopColor || 'transparent';
        target.style.borderRadius = style.borderRadius || '0px';
        target.setAttribute('data-h18-v0851-kasse-design', '1');
    }

    function clearOuterContainerDesign(tile) {
        if (!tile) { return; }
        tile.style.backgroundColor = 'transparent';
        tile.style.backgroundImage = 'none';
        tile.style.borderWidth = '0';
        tile.style.borderStyle = 'none';
        tile.style.borderColor = 'transparent';
        tile.style.borderRadius = '0';
    }

    function makeStackSegmentFromTile($tile, childKey) {
        const $ = jq();
        const $segment = $('<section>', {
            class: 'h18-v0811-child-card h18-v0851-stack-item h18-v0851-stack-segment',
            'data-h18-v0811-child': childKey,
            'data-h18-v0851-stack-key': childKey
        });
        const $bar = $tile.children('.h18-v0811-child-bar').first().detach();
        const $autoPreview = $tile.children('.h18-v0811-auto-box-preview').first().detach();
        const $preview = $('<div>', { class: 'h18-v0811-child-preview' });
        if ($autoPreview.length) { $preview.append($autoPreview.contents()); }
        $segment.append($bar, $preview);
        $tile.remove();
        return $segment;
    }

    function effectivePercents(rows) {
        const device = canvasDevice();
        const field = device === 'mobile' ? 'MobilePercent' : (device === 'tablet' ? 'TabletPercent' : 'DesktopPercent');
        const raw = rows.map(function ($row) {
            const state = stackState($row);
            return clampPercent(state[field]) || (field !== 'DesktopPercent' ? clampPercent(state.DesktopPercent) : 0);
        });
        if (raw.every(function (value) { return value === 0; })) {
            const base = Math.floor(100 / rows.length);
            let remainder = 100 - (base * rows.length);
            return rows.map(function () {
                const value = base + (remainder > 0 ? 1 : 0);
                if (remainder > 0) { remainder -= 1; }
                return value;
            });
        }
        const filled = raw.map(function (value) { return value || 10; });
        const sum = filled.reduce(function (total, value) { return total + value; }, 0) || 100;
        const normalized = filled.map(function (value) { return Math.max(10, Math.round((value / sum) * 100)); });
        let total = normalized.reduce(function (acc, value) { return acc + value; }, 0);
        while (total > 100) {
            const index = normalized.findIndex(function (value) { return value > 10; });
            if (index < 0) { break; }
            normalized[index] -= 1;
            total -= 1;
        }
        while (total < 100) { normalized[normalized.length - 1] += 1; total += 1; }
        return normalized;
    }

    function writePercent($row, value, capture) {
        const state = stackState($row);
        const device = canvasDevice();
        const field = device === 'mobile' ? 'MobilePercent' : (device === 'tablet' ? 'TabletPercent' : 'DesktopPercent');
        state[field] = Math.max(10, Math.min(90, Math.round(value)));
        writeStackState($row, state, capture === true);
    }

    function addVerticalHandles($column, rows, percents) {
        const $ = jq();
        if (!$ || !$column || !$column.length || rows.length < 2) { return; }
        const $segments = $column.children('.h18-v0851-stack-segment');
        $segments.each(function (index) {
            this.style.flex = '0 0 ' + percents[index] + '%';
            this.style.minHeight = '0';
            if (index >= $segments.length - 1) { return; }
            $(this).append($('<button>', {
                type: 'button',
                class: 'h18-v0851-stack-resize-handle',
                'aria-label': 'Juster højden mellem elementerne',
                title: 'Træk op eller ned for at justere højden',
                'data-h18-v0851-upper': rowKey(rows[index]),
                'data-h18-v0851-lower': rowKey(rows[index + 1])
            }).append($('<span>', { 'aria-hidden': 'true', text: '↕' })));
        });
    }

    function renderGridStacks(grid) {
        const $ = jq();
        if (!$ || !grid) { return; }
        const $grid = $(grid);
        if ($grid.children('.h18-v0811-auto-box').children('.h18-v0851-stack-column').length) { return; }
        const tilesByKey = {};
        $grid.children('.h18-v0811-auto-box').each(function () {
            const key = String($(this).attr('data-h18-v0811-row') || $(this).attr('data-h18-v0840-auto-child') || '');
            if (key) { tilesByKey[key] = $(this); }
        });

        Object.keys(tilesByKey).forEach(function (key) {
            const $row = rowByKey(key);
            if (!$row.length) { return; }
            const state = stackState($row);
            if (state.StackRootKey && state.StackRootKey !== key && tilesByKey[state.StackRootKey]) { return; }
            const $tile = tilesByKey[key];
            const $stackRows = stackRowsForRoot(key);
            const groupRows = [$row];
            $stackRows.each(function () { groupRows.push($(this)); });

            clearOuterContainerDesign($tile.get(0));
            if (!$stackRows.length) {
                $tile.removeClass('h18-v0851-stack-column-tile');
                const target = $tile.children('.h18-v0811-auto-box-preview').first().get(0);
                if (target) {
                    target.classList.add('h18-v0851-kasse-segment');
                    copyContainerDesign($row, target);
                }
                return;
            }

            $tile.addClass('h18-v0851-stack-column-tile');
            const $column = $('<div>', { class: 'h18-v0851-stack-column', 'data-h18-v0851-stack-root': key });
            const $rootSegment = $('<section>', {
                class: 'h18-v0851-stack-root h18-v0851-stack-segment',
                'data-h18-v0851-stack-key': key
            });
            $rootSegment.append(
                $tile.children('.h18-v0811-child-bar').first().detach(),
                $tile.children('.h18-v0811-auto-box-preview').first().detach()
            );
            $column.append($rootSegment);

            $stackRows.each(function () {
                const stackKey = rowKey($(this));
                const $childTile = tilesByKey[stackKey];
                if ($childTile && $childTile.length) { $column.append(makeStackSegmentFromTile($childTile, stackKey)); }
            });
            $tile.prepend($column);

            $column.children('.h18-v0851-stack-segment').each(function (index) {
                const $segment = $(this);
                const preview = $segment.children('.h18-v0811-auto-box-preview,.h18-v0811-child-preview').first().get(0);
                if (preview) {
                    preview.classList.add('h18-v0851-kasse-segment');
                    copyContainerDesign(groupRows[index], preview);
                }
            });
            addVerticalHandles($column, groupRows, effectivePercents(groupRows));
        });

        Object.keys(tilesByKey).forEach(function (key) {
            const $row = rowByKey(key);
            const state = $row.length ? stackState($row) : normalizeStackState({});
            if (state.StackRootKey && state.StackRootKey !== key) {
                const $tile = $grid.children('.h18-v0811-auto-box[data-h18-v0811-row="' + cssEscape(key) + '"]');
                if ($tile.length) { $tile.remove(); }
            }
        });
    }

    function cssEscape(value) {
        const raw = String(value || '');
        if (window.CSS && typeof window.CSS.escape === 'function') { return window.CSS.escape(raw); }
        return raw.replace(/(["\\])/g, '\\$1');
    }

    function applyContainerDesignToAll() {
        const $ = jq();
        if (!$) { return; }
        $('.h18-builder-canvas .h18-v0811-auto-box[data-h18-v0811-row]').each(function () {
            const $tile = $(this);
            const key = String($tile.attr('data-h18-v0811-row') || '');
            const $row = rowByKey(key);
            if (!$row.length) { return; }
            clearOuterContainerDesign(this);
            const target = $tile.find('.h18-v0851-stack-root').first().length
                ? $tile.find('.h18-v0851-stack-root .h18-v0811-auto-box-preview').first().get(0)
                : $tile.children('.h18-v0811-auto-box-preview').first().get(0);
            if (target) { copyContainerDesign($row, target); }
        });
        $('.h18-builder-canvas .h18-v0811-child-card[data-h18-v0811-child]').each(function () {
            const $card = $(this);
            const key = String($card.attr('data-h18-v0811-child') || '');
            const $row = rowByKey(key);
            const target = $card.children('.h18-v0811-child-preview').first().get(0);
            if ($row.length && target) { copyContainerDesign($row, target); }
        });
    }

    function renderDerivedLayout() {
        renderFrame = 0;
        suppressObserverUntil = Date.now() + 100;
        const $ = jq();
        if (!$) { return; }
        hydrateStackStates();
        removeLegacyPrompts(document);
        $('.h18-builder-canvas .h18-v0811-auto-grid[data-h18-v0840-auto-row="1"]').each(function () { renderGridStacks(this); });
        applyContainerDesignToAll();
        const resize = window.__h18LegoResizeV0841;
        if (resize && typeof resize.refresh === 'function') { resize.refresh(); }
        window.setTimeout(function () {
            removeLegacyPrompts(document);
            applyContainerDesignToAll();
            applySelectionOverlay();
        }, 0);
        applySelectionOverlay();
    }

    function scheduleRender() {
        if (renderFrame || verticalDrag) { return; }
        renderFrame = window.requestAnimationFrame(renderDerivedLayout);
    }

    function atomic() {
        const api = window.__h18HistoryAtomicV0840;
        return api && typeof api.begin === 'function' && typeof api.end === 'function' ? api : null;
    }

    function beginVerticalResize(event, handle) {
        const $ = jq();
        if (!$ || event.button !== 0 || verticalDrag) { return; }
        const upperKey = String(handle.getAttribute('data-h18-v0851-upper') || '');
        const lowerKey = String(handle.getAttribute('data-h18-v0851-lower') || '');
        const $upperRow = rowByKey(upperKey);
        const $lowerRow = rowByKey(lowerKey);
        const $upper = $(handle).closest('.h18-v0851-stack-segment');
        const $lower = $upper.next('.h18-v0851-stack-segment');
        if (!$upperRow.length || !$lowerRow.length || !$upper.length || !$lower.length) { return; }
        event.preventDefault();
        event.stopPropagation();
        const upperRect = $upper.get(0).getBoundingClientRect();
        const lowerRect = $lower.get(0).getBoundingClientRect();
        const total = Math.max(96, upperRect.height + lowerRect.height);
        const history = atomic();
        if (history) { history.begin('stack-height-resize'); }
        verticalDrag = {
            pointerId: event.pointerId,
            startY: event.clientY,
            total: total,
            upperStart: upperRect.height,
            $upper: $upper,
            $lower: $lower,
            $upperRow: $upperRow,
            $lowerRow: $lowerRow,
            history: history
        };
        handle.classList.add('is-active');
        if (handle.setPointerCapture) { try { handle.setPointerCapture(event.pointerId); } catch (ignore) {} }
    }

    function moveVerticalResize(event) {
        if (!verticalDrag || event.pointerId !== verticalDrag.pointerId) { return; }
        const delta = event.clientY - verticalDrag.startY;
        const minPx = 48;
        const upperPx = Math.max(minPx, Math.min(verticalDrag.total - minPx, verticalDrag.upperStart + delta));
        const upperPct = Math.round((upperPx / verticalDrag.total) * 100);
        const lowerPct = 100 - upperPct;
        verticalDrag.$upper.css('flex', '0 0 ' + upperPct + '%');
        verticalDrag.$lower.css('flex', '0 0 ' + lowerPct + '%');
        verticalDrag.upperPct = upperPct;
        verticalDrag.lowerPct = lowerPct;
        event.preventDefault();
    }

    function finishVerticalResize(commit) {
        if (!verticalDrag) { return; }
        const drag = verticalDrag;
        verticalDrag = null;
        document.querySelectorAll('.h18-v0851-stack-resize-handle.is-active').forEach(function (node) { node.classList.remove('is-active'); });
        if (commit !== false && drag.upperPct && drag.lowerPct) {
            writePercent(drag.$upperRow, drag.upperPct, false);
            writePercent(drag.$lowerRow, drag.lowerPct, true);
        }
        if (drag.history && drag.history.isActive && drag.history.isActive()) { drag.history.end(commit !== false); }
        scheduleRender();
    }

    function panelByHeading(text) {
        const wanted = String(text || '').toLowerCase();
        return Array.from(document.querySelectorAll('#h18-page-inspector-target .h18-section-module-box,#h18-page-inspector-target details,#h18-page-inspector-target fieldset')).find(function (panel) {
            const heading = panel.querySelector('h3,h4,summary,legend,strong');
            return heading && String(heading.textContent || '').toLowerCase().indexOf(wanted) !== -1;
        }) || null;
    }

    function shortenLegacySpacingLabels(panel) {
        if (!panel) { return; }
        const replacements = [
            [/Placeringsluft\s*før\s*\(px\)/i, 'Luft før'],
            [/Luft\s*efter\s*\(px\)/i, 'Luft efter'],
            [/Indvendig\s*luft\s*[–-]\s*lodret\s*\(px\)/i, 'Lodret luft'],
            [/Indvendig\s*luft\s*[–-]\s*vandret\s*\(px\)/i, 'Vandret luft']
        ];
        panel.querySelectorAll('label,strong').forEach(function (node) {
            let value = String(node.textContent || '').trim();
            replacements.forEach(function (item) { value = value.replace(item[0], item[1]); });
            if (value !== String(node.textContent || '').trim()) { node.textContent = value; }
        });
    }

    function enhanceSpacingPanel() {
        const panel = panelByHeading('luft, baggrund og placering');
        if (!panel || panel.getAttribute('data-h18-v0851-tabs') === '1') { return; }
        const groups = Array.from(panel.querySelectorAll('fieldset')).filter(function (field) {
            const legend = field.querySelector(':scope > legend');
            const title = String(legend ? legend.textContent : '').trim().toLowerCase();
            return title === 'desktop' || title === 'mobil' || title === 'mobile';
        });
        if (groups.length < 2) { shortenLegacySpacingLabels(panel); return; }
        panel.setAttribute('data-h18-v0851-tabs', '1');
        const tabs = document.createElement('div');
        tabs.className = 'h18-v0851-device-tabs';
        groups.forEach(function (group, index) {
            const legend = group.querySelector(':scope > legend');
            const title = String(legend ? legend.textContent : (index === 0 ? 'Desktop' : 'Mobil')).trim();
            const id = 'h18-v0851-device-' + index;
            group.setAttribute('data-h18-v0851-device-panel', id);
            group.classList.toggle('is-active', index === 0);
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'button h18-v0851-device-tab' + (index === 0 ? ' is-active' : '');
            button.textContent = title;
            button.setAttribute('data-h18-v0851-device-target', id);
            tabs.appendChild(button);
        });

        /*
         * LEGO-052: Device controls must not remain direct children of the
         * legacy Inspector grid. On narrow inspector widths the old grid made
         * each fieldset/tab a separate very narrow grid column. Keep the
         * existing fields untouched, but isolate tabs + device fieldsets in a
         * single full-width shell that can span the legacy grid safely.
         */
        const parent = groups[0].parentNode;
        const shell = document.createElement('div');
        shell.className = 'h18-v0852-device-shell';
        shell.setAttribute('data-h18-v0852-device-shell', '1');
        parent.insertBefore(shell, groups[0]);
        shell.appendChild(tabs);
        groups.forEach(function (group) { shell.appendChild(group); });
        shortenLegacySpacingLabels(panel);
    }

    function actualField(name) {
        const $ = jq();
        const $selected = activeRows().filter('.is-selected').first();
        if (!$ || !$selected.length) { return $ ? $() : null; }
        return controls($selected, '[name$="[' + name + ']"]').first();
    }

    function setActualField(name, value, eventType) {
        const $field = actualField(name);
        if (!$field || !$field.length) { return false; }
        $field.val(String(value));
        controls(activeRows().filter('.is-selected').first(), '[name$="[' + name + ']"]').val(String(value));
        $field.trigger(eventType === 'change' ? 'change' : 'input');
        return true;
    }

    function enhanceBackgroundControl() {
        const $ = jq();
        const $target = $inspectorTarget();
        const $selected = activeRows().filter('.is-selected').first();
        if (!$ || !$target.length || !$selected.length) { return; }
        const $background = $target.find('select[name$="[Background]"]').first();
        const $mode = actualField('DesignMode');
        const $custom = actualField('CustomBackgroundColor');
        if (!$background.length || !$mode.length || !$custom.length) { return; }

        if (!$background.find('option[value="' + CUSTOM_VALUE + '"]').length) { $background.append($('<option>', { value: CUSTOM_VALUE, text: 'Custom…' })); }
        if (String($mode.val() || '') === 'Custom') { $background.val(CUSTOM_VALUE); }

        let $box = $target.find('.h18-v0851-custom-background').first();
        if (!$box.length) {
            $box = $('<div>', { class: 'h18-v0851-custom-background' }).append(
                $('<label>').append(
                    $('<strong>', { text: 'Custom baggrund' }),
                    $('<span>', { class: 'h18-v0851-custom-color-row' }).append(
                        $('<input>', { type: 'color', class: 'h18-v0851-custom-bg-color' }),
                        $('<input>', { type: 'text', class: 'h18-v0851-custom-bg-hex', maxlength: 7, placeholder: '#ffffff' })
                    )
                )
            );
            const $host = $background.closest('label,.h18-field').first();
            ($host.length ? $host : $background).after($box);
        }
        const color = /^#[0-9a-f]{6}$/i.test(String($custom.val() || '')) ? String($custom.val()) : '#ffffff';
        $box.find('.h18-v0851-custom-bg-color,.h18-v0851-custom-bg-hex').val(color);
        $box.toggle(String($mode.val() || '') === 'Custom' || String($background.val() || '') === CUSTOM_VALUE);
    }

    function enhanceInspector() {
        inspectorFrame = 0;
        enhanceSpacingPanel();
        enhanceBackgroundControl();
        removeLegacyPrompts(document);
        applySelectionOverlay();
    }

    function queueInspector() {
        if (inspectorFrame) { return; }
        inspectorFrame = window.requestAnimationFrame(enhanceInspector);
    }

    function mutationNodeContainsSectionRow(node) {
        if (!node || node.nodeType !== 1) { return false; }
        if (node.matches && node.matches('.h18-page-section-row')) { return true; }
        return !!(node.querySelector && node.querySelector('.h18-page-section-row'));
    }

    function mutationTouchesInspector(mutation) {
        const target = mutation && mutation.target;
        const element = target && target.nodeType === 1 ? target : (target && target.parentElement ? target.parentElement : null);
        return !!(element && (element.id === 'h18-page-inspector-target' || (element.closest && element.closest('#h18-page-inspector-target'))));
    }

    function mutationChangesSectionRows(mutation) {
        if (!mutation || mutation.type !== 'childList') { return false; }
        const nodes = Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || []));
        return nodes.some(mutationNodeContainsSectionRow);
    }

    function handleObservedMutations(mutations) {
        if (Date.now() < suppressObserverUntil) { return; }
        let inspectorChanged = false;
        let sectionStructureChanged = false;

        (mutations || []).forEach(function (mutation) {
            if (mutationTouchesInspector(mutation)) { inspectorChanged = true; }
            if (mutationChangesSectionRows(mutation)) { sectionStructureChanged = true; }
        });

        /*
         * LEGO-052: Selecting an element physically moves its editor body into
         * #h18-page-inspector-target. v0.8.51 treated that ordinary selection
         * hand-off as a reason to rebuild the complete derived layout. That
         * rebuild moved/repainted the nested canvas again, which could create a
         * render/reconcile loop and prevent the selected proxy/red overlay from
         * stabilising. Only actual section-row add/remove mutations trigger a
         * full render now; Inspector mutations only refresh Inspector helpers.
         */
        if (sectionStructureChanged) { scheduleRender(); }
        if (inspectorChanged || sectionStructureChanged) { queueInspector(); }
    }

    function installEvents() {
        const $ = jq();
        if (!$) { return; }

        $(document).on('pointerdown', '.h18-v0851-stack-resize-handle', function (event) { beginVerticalResize(event.originalEvent || event, this); });
        document.addEventListener('pointermove', moveVerticalResize, true);
        document.addEventListener('pointerup', function (event) { if (verticalDrag && event.pointerId === verticalDrag.pointerId) { finishVerticalResize(true); } }, true);
        document.addEventListener('pointercancel', function (event) { if (verticalDrag && event.pointerId === verticalDrag.pointerId) { finishVerticalResize(false); } }, true);

        $(document).on('click', '.h18-v0851-device-tab', function () {
            const target = String($(this).attr('data-h18-v0851-device-target') || '');
            const $panel = $(this).closest('[data-h18-v0851-tabs="1"]');
            $panel.find('.h18-v0851-device-tab').removeClass('is-active');
            $(this).addClass('is-active');
            $panel.find('[data-h18-v0851-device-panel]').removeClass('is-active');
            $panel.find('[data-h18-v0851-device-panel="' + target + '"]').addClass('is-active');
        });

        $(document).on('change', '#h18-page-inspector-target select[name$="[Background]"]', function () {
            if (String($(this).val() || '') === CUSTOM_VALUE) { setActualField('DesignMode', 'Custom', 'change'); }
            else { setActualField('DesignMode', 'Global', 'change'); }
            queueInspector();
            scheduleRender();
        });

        $(document).on('input change', '.h18-v0851-custom-bg-color,.h18-v0851-custom-bg-hex', function () {
            const value = String($(this).val() || '').trim();
            if (!/^#[0-9a-f]{6}$/i.test(value)) { return; }
            $('.h18-v0851-custom-bg-color,.h18-v0851-custom-bg-hex').val(value);
            setActualField('DesignMode', 'Custom', 'change');
            setActualField('CustomBackgroundColor', value, 'input');
            scheduleRender();
        });

        const $f = $form();
        if ($f && $f.length) {
            $f.on('submit.h18V0851Stack', function () {
                $f.find('[' + STACK_SUBMIT_ATTR + '="1"]').remove();
                let index = 0;
                activeRows().each(function () {
                    const $row = $(this);
                    const key = rowKey($row);
                    if (!key) { return; }
                    const values = { SectionKey: key, StateJson: JSON.stringify(stackState($row)) };
                    Object.keys(values).forEach(function (name) {
                        $('<input>', {
                            type: 'hidden',
                            name: 'h18_lego_stack_v0851[' + index + '][' + name + ']',
                            value: values[name]
                        }).attr(STACK_SUBMIT_ATTR, '1').appendTo($f);
                    });
                    index += 1;
                });
                $f.find('select[name$="[Background]"]').each(function () {
                    if (String($(this).val() || '') === CUSTOM_VALUE) { $(this).val('White'); }
                });
            });
        }

        if (window.MutationObserver) {
            new MutationObserver(handleObservedMutations).observe(document.body, { childList: true, subtree: true });
        }

        document.addEventListener('click', queueInspector, true);
        document.addEventListener('input', function () { scheduleRender(); queueInspector(); }, true);
        document.addEventListener('change', function () { scheduleRender(); queueInspector(); }, true);
    }

    function wrapExistingRefresh() {
        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function' && !nesting.__h18V0851Wrapped) {
            const nativeRefresh = nesting.refresh.bind(nesting);
            nesting.refresh = function () {
                const result = nativeRefresh.apply(null, arguments);
                scheduleRender();
                return result;
            };
            nesting.__h18V0851Wrapped = true;
        }
    }

    function install() {
        hydrateStackStates();
        installEvents();
        wrapExistingRefresh();
        [0, 60, 180, 500].forEach(function (delay) { window.setTimeout(function () { scheduleRender(); queueInspector(); }, delay); });
        document.documentElement.setAttribute('data-h18-lego-fixes', VERSION);
        document.documentElement.setAttribute('data-h18-lego-fixes-hotfix', HOTFIX_VERSION);
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }

    window.__h18LegoFixesV0851 = {
        version: VERSION,
        hotfixVersion: HOTFIX_VERSION,
        refresh: renderDerivedLayout,
        stackUnder: stackUnder,
        stackOver: stackOver,
        adoptUnder: adoptUnder,
        clearStackForKey: function (key, capture) {
            const $row = rowByKey(key);
            if (!$row.length) { return false; }
            clearStack($row, capture === true);
            scheduleRender();
            return true;
        },
        stackStateForKey: function (key) {
            const $row = rowByKey(key);
            return $row.length ? stackState($row) : null;
        },
        applySelectionOverlay: applySelectionOverlay,
        enhanceInspector: enhanceInspector
    };
}());