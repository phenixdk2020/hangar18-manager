(function () {
    'use strict';

    var modalState = new WeakMap();

    function focusable(root) {
        return Array.prototype.slice.call(root.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])')).filter(function (node) {
            return !node.hidden && node.offsetParent !== null;
        });
    }

    function modalById(id) {
        return document.querySelector('[data-h18-modal="' + CSS.escape(String(id || '')) + '"]');
    }

    function openModal(modal, opener) {
        if (!modal) { return; }
        modalState.set(modal, { opener: opener || document.activeElement, previousOverflow: document.body.style.overflow });
        modal.hidden = false;
        document.body.style.overflow = 'hidden';
        var dialog = modal.querySelector('.h18-modal-dialog');
        var targets = dialog ? focusable(dialog) : [];
        (targets[0] || dialog || modal).focus();
        modal.dispatchEvent(new CustomEvent('h18:modal-opened', { bubbles: true }));
    }

    function closeModal(modal) {
        if (!modal || modal.hidden) { return; }
        var state = modalState.get(modal) || {};
        modal.hidden = true;
        document.body.style.overflow = state.previousOverflow || '';
        if (state.opener && typeof state.opener.focus === 'function') { state.opener.focus(); }
        modal.dispatchEvent(new CustomEvent('h18:modal-closed', { bubbles: true }));
    }

    function trapModalKeydown(event) {
        var modal = event.target.closest('[data-h18-modal]');
        if (!modal || modal.hidden) { return; }
        if (event.key === 'Escape') {
            event.preventDefault();
            closeModal(modal);
            return;
        }
        if (event.key !== 'Tab') { return; }
        var dialog = modal.querySelector('.h18-modal-dialog');
        var targets = dialog ? focusable(dialog) : [];
        if (!targets.length) {
            event.preventDefault();
            if (dialog) { dialog.focus(); }
            return;
        }
        var first = targets[0], last = targets[targets.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }

    function executeClientActions(actions, trigger) {
        (Array.isArray(actions) ? actions : []).forEach(function (action) {
            var type = String(action.Type || '').toLowerCase();
            if (type === 'navigate') {
                var url = String(action.Url || '');
                if (/^(https?:\/\/|\/|#)/i.test(url)) { window.location.assign(url); }
            } else if (type === 'scroll') {
                var scrollTarget = document.getElementById(String(action.TargetId || ''));
                if (scrollTarget) { scrollTarget.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); }
            } else if (type === 'open-modal') {
                openModal(modalById(action.TargetId), trigger);
            } else if (type === 'toggle') {
                var target = document.getElementById(String(action.TargetId || ''));
                if (target) {
                    var hidden = target.hasAttribute('hidden');
                    if (hidden) { target.removeAttribute('hidden'); } else { target.setAttribute('hidden', ''); }
                    trigger && trigger.setAttribute && trigger.setAttribute('aria-expanded', hidden ? 'true' : 'false');
                }
            }
        });
    }

    function parseActions(node) {
        var raw = node.getAttribute('data-h18-actions') || '[]';
        try { var parsed = JSON.parse(raw); return Array.isArray(parsed) ? parsed : []; } catch (error) { return []; }
    }

    function formClientValidation(form) {
        var valid = true;
        form.querySelectorAll('[data-h18-field]').forEach(function (wrap) {
            var input = wrap.querySelector('input,select,textarea');
            var error = wrap.querySelector('.h18-form-error');
            if (!input || !error) { return; }
            error.textContent = '';
            input.removeAttribute('aria-invalid');
            if (!input.checkValidity()) {
                valid = false;
                error.textContent = input.validationMessage || 'Kontrollér feltet.';
                input.setAttribute('aria-invalid', 'true');
            }
        });
        return valid;
    }

    function initForms() {
        document.querySelectorAll('[data-h18-form]').forEach(function (form) {
            if (form.dataset.h18Enhanced === '1') { return; }
            form.dataset.h18Enhanced = '1';
            form.addEventListener('submit', function (event) {
                if (!formClientValidation(form)) {
                    event.preventDefault();
                    var invalid = form.querySelector('[aria-invalid="true"]');
                    if (invalid) { invalid.focus(); }
                }
            });
        });
    }

    function contextValue(key) {
        var root = document.documentElement;
        var attr = 'data-h18-context-' + String(key || '').replace(/[^a-z0-9_-]/gi, '-').toLowerCase();
        return root.getAttribute(attr);
    }

    function triggerSatisfied(trigger) {
        var type = String(trigger.Type || '').toLowerCase();
        if (type === 'context') {
            var actual = contextValue(trigger.Key);
            var op = String(trigger.Operator || 'equals');
            if (op === 'exists') { return actual !== null; }
            if (op === 'not_equals') { return String(actual) !== String(trigger.Value || ''); }
            return String(actual) === String(trigger.Value || '');
        }
        return false;
    }

    function activatePopup(definition, modalId) {
        var triggers = Array.isArray(definition.Triggers) ? definition.Triggers : [];
        var mode = String(definition.Mode || 'ANY').toUpperCase();
        var state = new Array(triggers.length).fill(false);
        var opened = false;
        function evaluate(index) {
            if (index >= 0) { state[index] = true; }
            var pass = mode === 'ALL' ? state.every(Boolean) : state.some(Boolean);
            if (pass && !opened) { opened = true; openModal(modalById(modalId), null); }
        }
        triggers.forEach(function (trigger, index) {
            var type = String(trigger.Type || '').toLowerCase();
            if (type === 'click') {
                var node = document.getElementById(String(trigger.ElementId || ''));
                if (node) { node.addEventListener('click', function () { evaluate(index); }, { once: mode === 'ANY' }); }
            } else if (type === 'time') {
                window.setTimeout(function () { evaluate(index); }, Math.max(0, Math.min(600000, parseInt(trigger.DelayMs, 10) || 0)));
            } else if (type === 'scroll') {
                var targetPercent = Math.max(0, Math.min(100, parseInt(trigger.Percent, 10) || 0));
                var handler = function () {
                    var doc = document.documentElement;
                    var max = Math.max(1, doc.scrollHeight - window.innerHeight);
                    if ((window.scrollY / max) * 100 >= targetPercent) { window.removeEventListener('scroll', handler); evaluate(index); }
                };
                window.addEventListener('scroll', handler, { passive: true }); handler();
            } else if (type === 'context' && triggerSatisfied(trigger)) { evaluate(index); }
        });
    }

    function init() {
        document.addEventListener('keydown', trapModalKeydown);
        document.addEventListener('click', function (event) {
            var close = event.target.closest('[data-h18-modal-close]');
            if (close) { closeModal(close.closest('[data-h18-modal]')); return; }
            var actionNode = event.target.closest('[data-h18-actions]');
            if (actionNode) { executeClientActions(parseActions(actionNode), actionNode); }
        });
        document.querySelectorAll('[data-h18-popup-triggers]').forEach(function (node) {
            try {
                var definition = JSON.parse(node.getAttribute('data-h18-popup-triggers') || '{}');
                activatePopup(definition, node.getAttribute('data-h18-popup-modal'));
            } catch (error) { /* invalid data remains inert */ }
        });
        initForms();
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); } else { init(); }
})();
