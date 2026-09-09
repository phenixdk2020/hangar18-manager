(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    if (!CFG.legacyMobileFlow) { return; }

    var WIDTHS = { laptop: 1180, tablet: 980, mobile: 390 };
    var HOST_ID = 'h18-vd-canonical-responsive-preview';
    var FRAME_ID = 'h18-vd-canonical-responsive-frame';
    var FRAME_NAME = 'h18_vd_canonical_responsive_frame';
    var scheduled = 0;
    var lastSubmitted = '';
    var loadCount = 0;
    var scrollByDevice = Object.create(null);
    var currentDevice = '';

    function activeDevice() {
        if (window.H18CleanResponsive && typeof window.H18CleanResponsive.device === 'function') {
            var responsiveDevice = String(window.H18CleanResponsive.device() || '');
            if (responsiveDevice) { return responsiveDevice; }
        }
        return document.body ? String(document.body.getAttribute('data-h18-clean-device') || 'desktop') : 'desktop';
    }

    function modelField() {
        return document.getElementById('h18-clean-model-json');
    }

    function previewButton() {
        return document.getElementById('h18-clean-preview');
    }

    function hidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
    }

    function modelNodeIds() {
        var field = modelField();
        if (!field) { return Object.create(null); }
        try {
            var model = JSON.parse(field.value || '{}');
            var ids = Object.create(null);
            (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
                if (node && node.id) { ids[String(node.id)] = true; }
            });
            return ids;
        } catch (ignore) {
            return Object.create(null);
        }
    }

    function ensureHost() {
        var existing = document.getElementById(HOST_ID);
        if (existing) { return existing; }
        var canvas = document.getElementById('h18-clean-canvas');
        if (!canvas) { return null; }
        var column = canvas.closest('.h18-clean-canvas-column') || canvas.parentElement;
        if (!column) { return null; }

        var host = document.createElement('div');
        host.id = HOST_ID;
        host.className = 'h18-vd-canonical-responsive-preview';
        host.innerHTML = '' +
            '<div class="h18-vd-canonical-responsive-head">' +
                '<strong>Frontend-paritet</strong>' +
                '<span id="h18-vd-canonical-responsive-status">Indlæser…</span>' +
                '<button type="button" class="button button-small" id="h18-vd-canonical-responsive-refresh">Opdater preview</button>' +
            '</div>' +
            '<div class="h18-vd-canonical-responsive-scroll">' +
                '<div class="h18-vd-canonical-responsive-stage">' +
                    '<iframe id="' + FRAME_ID + '" name="' + FRAME_NAME + '" title="Kanonisk frontend-preview" loading="eager"></iframe>' +
                '</div>' +
            '</div>';

        var viewportStage = canvas.parentElement && canvas.parentElement.classList.contains('h18-vd-viewport-stage')
            ? canvas.parentElement
            : null;
        if (viewportStage && viewportStage.parentElement === column) {
            viewportStage.insertAdjacentElement('afterend', host);
        } else {
            column.appendChild(host);
        }

        var frame = host.querySelector('#' + FRAME_ID);
        if (frame) { frame.addEventListener('load', onFrameLoad); }
        var refresh = host.querySelector('#h18-vd-canonical-responsive-refresh');
        if (refresh) {
            refresh.addEventListener('click', function () {
                lastSubmitted = '';
                submitPreview(true);
            });
        }
        return host;
    }

    function canvasColumn() {
        var canvas = document.getElementById('h18-clean-canvas');
        return canvas ? (canvas.closest('.h18-clean-canvas-column') || canvas.parentElement) : null;
    }

    function availableWidth() {
        var column = canvasColumn();
        if (!column) { return 390; }
        var style = window.getComputedStyle(column);
        var left = parseFloat(style.paddingLeft || '0') || 0;
        var right = parseFloat(style.paddingRight || '0') || 0;
        return Math.max(120, column.clientWidth - left - right - 2);
    }

    function fitFrame() {
        var host = ensureHost();
        if (!host || !currentDevice || !WIDTHS[currentDevice]) { return; }
        var frame = host.querySelector('#' + FRAME_ID);
        var stage = host.querySelector('.h18-vd-canonical-responsive-stage');
        if (!frame || !stage) { return; }

        var width = WIDTHS[currentDevice];
        var contentHeight = Math.max(480, parseInt(frame.getAttribute('data-content-height') || '900', 10) || 900);
        var scale = Math.min(1, availableWidth() / width);
        scale = Math.max(0.15, Math.round(scale * 100) / 100);

        frame.style.width = width + 'px';
        frame.style.height = contentHeight + 'px';
        frame.style.transformOrigin = '0 0';
        frame.style.transform = 'scale(' + scale + ')';
        stage.style.width = Math.ceil(width * scale) + 'px';
        stage.style.height = Math.ceil(contentHeight * scale) + 'px';
        host.style.setProperty('--h18-vd-canonical-scale', String(scale));

        var status = host.querySelector('#h18-vd-canonical-responsive-status');
        if (status) {
            var label = ({ laptop: 'Laptop', tablet: 'Tablet', mobile: 'Mobil' })[currentDevice] || currentDevice;
            status.textContent = label + ' · ' + width + ' px · frontend-renderer · ' + Math.round(scale * 100) + '% visning';
        }
    }

    function rememberScroll() {
        var host = document.getElementById(HOST_ID);
        var frame = host ? host.querySelector('#' + FRAME_ID) : null;
        if (!frame || !currentDevice) { return; }
        try {
            scrollByDevice[currentDevice] = Math.max(0, frame.contentWindow ? frame.contentWindow.scrollY || 0 : 0);
        } catch (ignore) {}
    }

    function syncModel() {
        if (window.H18CleanResponsive && typeof window.H18CleanResponsive.sync === 'function') {
            window.H18CleanResponsive.sync();
        } else if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') {
            window.H18CleanV0120.sync();
        }
    }

    function submitPreview(force) {
        var device = activeDevice();
        if (!WIDTHS[device]) { return; }
        var host = ensureHost();
        var button = previewButton();
        var field = modelField();
        if (!host || !button || !field) { return; }

        syncModel();
        var modelJson = field.value || '{}';
        var key = device + '\n' + modelJson;
        if (!force && key === lastSubmitted) {
            fitFrame();
            return;
        }

        rememberScroll();
        lastSubmitted = key;
        currentDevice = device;
        host.classList.add('is-loading');

        var form = document.createElement('form');
        form.method = 'post';
        form.action = button.getAttribute('data-url') || '';
        form.target = FRAME_NAME;
        form.style.display = 'none';
        hidden(form, 'action', 'h18_clean_preview');
        hidden(form, '_wpnonce', button.getAttribute('data-nonce') || '');
        hidden(form, 'post_id', button.getAttribute('data-post-id') || '0');
        hidden(form, 'model_json', modelJson);
        document.body.appendChild(form);
        form.submit();
        window.setTimeout(function () { form.remove(); }, 1200);
    }

    function pageNodeFromTarget(target, ids) {
        var element = target && target.nodeType === 1 ? target : target && target.parentElement;
        while (element && element.nodeType === 1) {
            var rawId = String(element.id || '');
            if (rawId.indexOf('h18-clean-') === 0) {
                var candidate = rawId.slice('h18-clean-'.length);
                if (ids[candidate]) { return candidate; }
            }
            element = element.parentElement;
        }
        return '';
    }

    function highlightFrameSelection(doc, id) {
        if (!doc) { return; }
        try {
            doc.querySelectorAll('[data-h18-vd-selected="1"]').forEach(function (element) {
                element.removeAttribute('data-h18-vd-selected');
            });
            if (!id) { return; }
            var target = doc.getElementById('h18-clean-' + id);
            if (target) { target.setAttribute('data-h18-vd-selected', '1'); }
        } catch (ignore) {}
    }

    function installFrameBridge(frame) {
        var doc;
        try { doc = frame.contentDocument; } catch (ignore) { return; }
        if (!doc || !doc.documentElement || !doc.body) { return; }

        try {
            var style = doc.createElement('style');
            style.setAttribute('data-h18-vd-designer-bridge', '1');
            style.textContent = '' +
                '#wpadminbar{display:none!important}html{margin-top:0!important}' +
                '[data-h18-vd-selectable="1"]{cursor:pointer!important}' +
                '[data-h18-vd-selected="1"]{outline:3px solid #2271b1!important;outline-offset:2px!important;position:relative!important;z-index:2147483000!important}';
            doc.head.appendChild(style);
        } catch (ignoreStyle) {}

        try {
            Array.prototype.forEach.call(doc.body.children, function (child) {
                if (child && child.textContent && /^Forhåndsvisning · ikke gemt\s*$/.test(String(child.textContent).trim())) {
                    child.style.display = 'none';
                }
            });
        } catch (ignoreBadge) {}

        var ids = modelNodeIds();
        Object.keys(ids).forEach(function (id) {
            var element = doc.getElementById('h18-clean-' + id);
            if (element) { element.setAttribute('data-h18-vd-selectable', '1'); }
        });

        doc.addEventListener('click', function (event) {
            var id = pageNodeFromTarget(event.target, ids);
            if (id) {
                event.preventDefault();
                event.stopPropagation();
                if (window.H18VDDesigner && typeof window.H18VDDesigner.selectNode === 'function') {
                    window.H18VDDesigner.selectNode(id);
                }
                highlightFrameSelection(doc, id);
                return;
            }
            var link = event.target && event.target.closest ? event.target.closest('a') : null;
            if (link) { event.preventDefault(); }
        }, true);

        var selected = window.H18VDDesigner && typeof window.H18VDDesigner.selectedId === 'function'
            ? String(window.H18VDDesigner.selectedId() || '')
            : '';
        highlightFrameSelection(doc, selected);
    }

    function frameDocumentHeight(frame) {
        try {
            var doc = frame.contentDocument;
            if (!doc || !doc.documentElement || !doc.body) { return 900; }
            return Math.max(
                480,
                doc.documentElement.scrollHeight || 0,
                doc.documentElement.offsetHeight || 0,
                doc.body.scrollHeight || 0,
                doc.body.offsetHeight || 0
            );
        } catch (ignore) {
            return 900;
        }
    }

    function onFrameLoad(event) {
        var frame = event.currentTarget;
        if (!frame) { return; }
        loadCount += 1;
        if (loadCount === 1) {
            try {
                if (!frame.contentWindow || frame.contentWindow.location.href === 'about:blank') { return; }
            } catch (ignoreBlank) {}
        }
        var host = document.getElementById(HOST_ID);
        if (host) { host.classList.remove('is-loading'); }
        installFrameBridge(frame);

        window.setTimeout(function () {
            var height = frameDocumentHeight(frame);
            frame.setAttribute('data-content-height', String(height));
            fitFrame();
            try {
                var y = Math.max(0, scrollByDevice[currentDevice] || 0);
                if (frame.contentWindow && y > 0) { frame.contentWindow.scrollTo(0, y); }
            } catch (ignoreScroll) {}
        }, 40);
        window.setTimeout(function () {
            var height = frameDocumentHeight(frame);
            frame.setAttribute('data-content-height', String(height));
            fitFrame();
        }, 350);
    }

    function activate(device) {
        var host = ensureHost();
        if (!host) { return; }
        if (!WIDTHS[device]) {
            rememberScroll();
            currentDevice = '';
            document.body.classList.remove('h18-vd-canonical-responsive-active');
            host.hidden = true;
            return;
        }
        currentDevice = device;
        document.body.classList.add('h18-vd-canonical-responsive-active');
        host.hidden = false;
        fitFrame();
        submitPreview(false);
    }

    function scheduleSubmit(delay) {
        window.clearTimeout(scheduled);
        scheduled = window.setTimeout(function () {
            scheduled = 0;
            if (WIDTHS[activeDevice()]) { submitPreview(false); }
        }, Math.max(0, delay == null ? 700 : delay));
    }

    function install() {
        ensureHost();
        activate(activeDevice());

        if (window.MutationObserver && document.body) {
            new MutationObserver(function () { activate(activeDevice()); }).observe(document.body, {
                attributes: true,
                attributeFilter: ['data-h18-clean-device']
            });
        }

        document.addEventListener('h18-clean-model-changed', function () {
            if (WIDTHS[activeDevice()]) { scheduleSubmit(650); }
        });
        document.addEventListener('change', function (event) {
            if (!WIDTHS[activeDevice()] || !event.target) { return; }
            if (event.target.closest && event.target.closest('.h18-clean-inspector,[data-page-spacing-key]')) { scheduleSubmit(400); }
        }, true);
        window.addEventListener('resize', fitFrame, { passive: true });

        var column = canvasColumn();
        if (window.ResizeObserver && column) {
            new ResizeObserver(fitFrame).observe(column);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
