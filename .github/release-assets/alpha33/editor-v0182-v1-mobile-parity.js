(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    if (!CFG.legacyMobileFlow) { return; }

    var scheduled = false;
    var ROOT_ID = 'h18-clean-canvas';
    var FIELD_ID = 'h18-clean-model-json';
    var SEMANTIC_CLASSES = [
        'h18-vd-parity-hero',
        'h18-vd-parity-tagline',
        'h18-vd-parity-major-band',
        'h18-vd-parity-feature-band',
        'h18-vd-parity-feature-text',
        'h18-vd-parity-feature-bevaring',
        'h18-vd-parity-feature-formidling',
        'h18-vd-parity-feature-faellesskab',
        'h18-vd-parity-structural-path'
    ];

    function n(value, fallback) {
        var parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function activeDevice() {
        if (window.H18CleanResponsive && typeof window.H18CleanResponsive.device === 'function') {
            return String(window.H18CleanResponsive.device() || 'desktop');
        }
        return String(document.body.getAttribute('data-h18-clean-device') || 'desktop');
    }

    function readModel() {
        var field = document.getElementById(FIELD_ID);
        if (!field) { return { nodes: [] }; }
        try {
            var model = JSON.parse(field.value || '{}');
            return model && typeof model === 'object' ? model : { nodes: [] };
        } catch (ignore) {
            return { nodes: [] };
        }
    }

    function desktopGeometry(node) {
        var raw = node && node.geometry && node.geometry.desktop && typeof node.geometry.desktop === 'object'
            ? node.geometry.desktop
            : {};
        return {
            x: Math.max(0, n(raw.x, 0)),
            y: n(raw.y, 0),
            w: Math.max(1, n(raw.w, 120)),
            h: Math.max(0, n(raw.h, 0))
        };
    }

    function plain(value) {
        var host = document.createElement('div');
        host.innerHTML = String(value || '');
        return String(host.textContent || host.innerText || '').replace(/\s+/g, ' ').trim();
    }

    function heading(node) {
        return String(node && node.props && node.props.heading || '').trim();
    }

    function haystack(node) {
        var props = node && node.props && typeof node.props === 'object' ? node.props : {};
        return (plain(props.heading) + ' ' + plain(props.text)).toLocaleLowerCase('da-DK');
    }

    function cardFor(id, root) {
        if (!root) { return null; }
        var cards = root.querySelectorAll('.h18-clean-node[data-node-id]');
        for (var i = 0; i < cards.length; i++) {
            if (String(cards[i].getAttribute('data-node-id') || '') === String(id)) { return cards[i]; }
        }
        return null;
    }

    function clearParity(root) {
        document.body.classList.remove('h18-vd-v1-mobile-parity');
        if (!root) { return; }
        root.style.removeProperty('--h18-vd-parity-section-gap');
        root.style.removeProperty('--h18-vd-parity-element-gap');
        root.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {
            card.style.removeProperty('--h18-vd-parity-order');
            card.style.removeProperty('--h18-vd-parity-node-gap');
            SEMANTIC_CLASSES.forEach(function (name) { card.classList.remove(name); });
        });
    }

    function pageGap(model, key, fallback) {
        var raw = model && model.pageSettings && model.pageSettings[key];
        if (raw && typeof raw === 'object') {
            return Math.max(0, n(raw.mobile, fallback));
        }
        return fallback;
    }

    function buildMaps(model) {
        var byId = Object.create(null);
        var children = Object.create(null);
        var nodes = Array.isArray(model && model.nodes) ? model.nodes : [];
        nodes.forEach(function (node) {
            if (!node || !node.id) { return; }
            var id = String(node.id);
            var parent = String(node.parentId || '');
            byId[id] = node;
            if (!children[parent]) { children[parent] = []; }
            children[parent].push(node);
        });
        Object.keys(children).forEach(function (parent) {
            children[parent].sort(function (a, b) {
                var ag = desktopGeometry(a);
                var bg = desktopGeometry(b);
                return (ag.y - bg.y) || (ag.x - bg.x) || (n(a.order, 0) - n(b.order, 0));
            });
        });
        return { byId: byId, children: children };
    }

    function nearestBand(id, byId) {
        var node = byId[id];
        if (!node) { return id; }
        var parent = String(node.parentId || '');
        var guard = 0;
        while (parent && byId[parent] && guard++ < 32) {
            var candidate = byId[parent];
            if (candidate.type === 'section' || candidate.type === 'container') { return parent; }
            parent = String(candidate.parentId || '');
        }
        return id;
    }

    function ancestors(id, byId) {
        var result = [];
        var node = byId[id];
        var parent = node ? String(node.parentId || '') : '';
        var guard = 0;
        while (parent && byId[parent] && guard++ < 32) {
            result.push(parent);
            parent = String(byId[parent].parentId || '');
        }
        return result;
    }

    function markStructuralPath(ids, byId, root) {
        var seen = Object.create(null);
        ids.filter(Boolean).forEach(function (id) {
            ancestors(id, byId).forEach(function (ancestorId) { seen[ancestorId] = true; });
        });
        Object.keys(seen).forEach(function (id) {
            var node = byId[id];
            if (!node || (node.type !== 'section' && node.type !== 'container')) { return; }
            var card = cardFor(id, root);
            if (card) { card.classList.add('h18-vd-parity-structural-path'); }
        });
    }

    function applyOrderAndRootGaps(maps, root, sectionGap, elementGap) {
        Object.keys(maps.children).forEach(function (parent) {
            var previousFeature = false;
            var visible = 0;
            maps.children[parent].forEach(function (node, index) {
                var id = String(node.id || '');
                var card = cardFor(id, root);
                if (!card) { return; }
                card.style.setProperty('--h18-vd-parity-order', String(index));
                card.style.setProperty('--h18-vd-parity-node-gap', '0px');

                if (parent !== '' || node.type === 'spacer') { return; }
                var feature = node.type === 'text' && ['Bevaring', 'Formidling', 'Fællesskab'].indexOf(heading(node)) !== -1;
                var gap = visible === 0 ? 0 : ((feature && previousFeature) ? elementGap : sectionGap);
                card.style.setProperty('--h18-vd-parity-node-gap', String(gap) + 'px');
                visible += 1;
                previousFeature = feature;
            });
        });
    }

    function applySemanticParity(maps, root) {
        var byId = maps.byId;
        var heroId = '';
        var heroY = Number.MAX_SAFE_INTEGER;
        var taglineId = '';
        var majorIds = [];
        var featureIds = [];
        var majorHeadings = ['Om foreningen', 'Køretøjer og materiel', 'Events', 'Billedgalleri', 'Bliv en del af foreningen', 'Kontakt os'];

        Object.keys(byId).forEach(function (id) {
            var node = byId[id];
            var type = String(node.type || '');
            var title = heading(node);
            var hay = haystack(node);

            if (type === 'text' && hay.indexOf('bevaring, restaurering og levende') !== -1 && hay.indexOf('militærhistorie') !== -1) {
                taglineId = id;
            }
            if (type === 'text' && majorHeadings.indexOf(title) !== -1) {
                majorIds.push(id);
            }
            if (type === 'text' && ['Bevaring', 'Formidling', 'Fællesskab'].indexOf(title) !== -1) {
                featureIds.push({ id: id, heading: title });
            }
            if (type === 'image') {
                var g = desktopGeometry(node);
                if (g.w >= 100 && g.y < heroY) {
                    heroId = id;
                    heroY = g.y;
                }
            }
        });

        markStructuralPath([heroId, taglineId], byId, root);

        if (heroId) {
            var hero = cardFor(heroId, root);
            if (hero) {
                hero.classList.add('h18-vd-parity-hero');
                hero.style.setProperty('--h18-vd-parity-node-gap', '0px');
            }
        }
        if (taglineId) {
            var tagline = cardFor(taglineId, root);
            if (tagline) { tagline.classList.add('h18-vd-parity-tagline'); }
        }

        var majorBands = [];
        majorIds.forEach(function (id) {
            var bandId = nearestBand(id, byId);
            majorBands.push(bandId);
            var band = cardFor(bandId, root);
            if (band) { band.classList.add('h18-vd-parity-major-band'); }
        });
        markStructuralPath(majorBands, byId, root);

        featureIds.forEach(function (entry) {
            var bandId = nearestBand(entry.id, byId);
            var band = cardFor(bandId, root);
            var text = cardFor(entry.id, root);
            if (band) {
                band.classList.add('h18-vd-parity-feature-band');
                if (entry.heading === 'Bevaring') { band.classList.add('h18-vd-parity-feature-bevaring'); }
                else if (entry.heading === 'Formidling') { band.classList.add('h18-vd-parity-feature-formidling'); }
                else { band.classList.add('h18-vd-parity-feature-faellesskab'); }
            }
            if (text) { text.classList.add('h18-vd-parity-feature-text'); }
        });
    }

    function apply() {
        var root = document.getElementById(ROOT_ID);
        if (!root) { return; }
        clearParity(root);
        if (activeDevice() !== 'mobile') { return; }

        var model = readModel();
        var maps = buildMaps(model);
        var sectionGap = pageGap(model, 'sectionGap', 24);
        var elementGap = pageGap(model, 'elementGap', 14);

        document.body.classList.add('h18-vd-v1-mobile-parity');
        root.style.setProperty('--h18-vd-parity-section-gap', String(sectionGap) + 'px');
        root.style.setProperty('--h18-vd-parity-element-gap', String(elementGap) + 'px');

        applyOrderAndRootGaps(maps, root, sectionGap, elementGap);
        applySemanticParity(maps, root);
    }

    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () {
            scheduled = false;
            apply();
        });
    }

    function install() {
        var root = document.getElementById(ROOT_ID);
        var field = document.getElementById(FIELD_ID);
        if (!root) { return; }

        var bodyObserver = new MutationObserver(schedule);
        bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['data-h18-clean-device'] });

        var canvasObserver = new MutationObserver(schedule);
        canvasObserver.observe(root, { childList: true, subtree: true });

        if (field) {
            field.addEventListener('change', schedule);
            field.addEventListener('input', schedule);
        }
        window.addEventListener('resize', schedule);
        document.addEventListener('h18-clean-model-changed', schedule);

        schedule();
        window.setTimeout(schedule, 50);
        window.setTimeout(schedule, 180);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
