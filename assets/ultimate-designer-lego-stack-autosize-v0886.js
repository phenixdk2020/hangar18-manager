(function () {
    'use strict';

    if (window.__h18LegoStackAutosizeV0886) { return; }

    const VERSION = '0.8.86';
    let frame = 0;

    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas ? canvas.getAttribute('data-canvas-device') || 'desktop' : 'desktop').toLowerCase();
    }

    function stateForKey(key) {
        const api = window.__h18LegoFixesV0851;
        if (!api || typeof api.stackStateForKey !== 'function') { return null; }
        try { return api.stackStateForKey(String(key || '')); }
        catch (ignore) { return null; }
    }

    function percent(value) {
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) && parsed > 0 ? Math.max(10, Math.min(90, parsed)) : 0;
    }

    function effectivePercent(state, device) {
        state = state && typeof state === 'object' ? state : {};
        const desktop = percent(state.DesktopPercent);
        if (device === 'desktop') { return desktop; }
        const own = device === 'mobile' ? percent(state.MobilePercent) : percent(state.TabletPercent);
        return own || desktop;
    }

    function segmentKey(segment) {
        return String(segment.getAttribute('data-h18-v0851-stack-key') || '').trim();
    }

    function naturalizeColumn(column) {
        const segments = Array.from(column.querySelectorAll(':scope > .h18-v0851-stack-segment'));
        if (segments.length < 2) { return; }
        const device = canvasDevice();
        const values = segments.map(function (segment) {
            return effectivePercent(stateForKey(segmentKey(segment)), device);
        });
        const explicit = values.some(function (value) { return value > 0; });

        if (explicit) {
            column.removeAttribute('data-h18-v0886-natural-stack');
            return;
        }

        column.setAttribute('data-h18-v0886-natural-stack', '1');
        segments.forEach(function (segment) {
            segment.style.flex = '0 0 auto';
            segment.style.minHeight = '48px';
            const preview = segment.querySelector(':scope > .h18-v0811-auto-box-preview,:scope > .h18-v0811-child-preview');
            if (preview) {
                preview.style.flex = '0 0 auto';
                preview.style.minHeight = '0';
                preview.style.overflow = 'visible';
            }
        });
    }

    function fitVisibleImages() {
        document.querySelectorAll('.h18-builder-canvas .h18-v0851-stack-segment img').forEach(function (image) {
            image.style.boxSizing = 'border-box';
            const raw = String(image.style.maxWidth || '').trim();
            if (!raw || raw === 'none') {
                image.style.maxWidth = '100%';
            }
        });
    }

    function apply() {
        frame = 0;
        document.querySelectorAll('.h18-builder-canvas .h18-v0851-stack-column').forEach(naturalizeColumn);
        fitVisibleImages();
        document.documentElement.setAttribute('data-h18-lego-stack-autosize', VERSION);
    }

    function schedule() {
        if (frame) { return; }
        frame = window.requestAnimationFrame(apply);
    }

    function install() {
        const canvas = document.querySelector('.h18-builder-canvas');
        const sections = document.getElementById('h18-page-sections-sortable');
        if (!canvas || !sections) { return; }

        if (window.MutationObserver) {
            new MutationObserver(function (mutations) {
                if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) { schedule(); }
            }).observe(sections, { childList: true, subtree: true });
            new MutationObserver(schedule).observe(canvas, { attributes: true, attributeFilter: ['data-canvas-device'] });
        }

        document.addEventListener('input', schedule, true);
        document.addEventListener('change', schedule, true);
        [0, 60, 180, 500].forEach(function (delay) { window.setTimeout(schedule, delay); });
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }

    window.__h18LegoStackAutosizeV0886 = { version: VERSION, refresh: apply };
}());
