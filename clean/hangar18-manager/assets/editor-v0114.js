(function () {
    'use strict';

    function hidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
        return input;
    }

    function setupChangeNote() {
        var form = document.getElementById('h18-clean-save-form');
        var input = document.getElementById('h18-clean-change-note');
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!form || !input || !toolbar) { return; }

        input.type = 'text';
        input.required = false;
        input.removeAttribute('required');
        input.maxLength = 180;
        input.autocomplete = 'off';
        input.placeholder = 'Valgfri – ellers beskriver systemet automatisk ændringen';
        input.setAttribute('aria-label', 'Ændringer i denne version, valgfri');

        var userEntered = hidden(form, 'change_note_user_entered', '0');
        input.addEventListener('input', function () {
            userEntered.value = (input.value || '').trim() !== '' ? '1' : '0';
        });

        var wrapper = document.createElement('label');
        wrapper.className = 'h18-clean-change-note-wrap';
        var caption = document.createElement('span');
        caption.textContent = 'Ændringer (valgfri):';
        caption.className = 'h18-clean-change-note-label';
        wrapper.appendChild(caption);
        wrapper.appendChild(input);

        var firstSave = toolbar.querySelector('.h18-clean-save') || toolbar.lastElementChild;
        toolbar.insertBefore(wrapper, firstSave || null);

        var historyHeaders = document.querySelectorAll('.h18-clean-history th');
        historyHeaders.forEach(function (header) {
            if ((header.textContent || '').trim() === 'Note') {
                header.textContent = 'Ændringer';
            }
        });
    }

    function setupInspectorScrollPreservation() {
        var panel = document.querySelector('.h18-clean-inspector');
        var host = document.getElementById('h18-clean-inspector');
        if (!panel || !host || panel.dataset.vdScrollGuard === '1') { return; }
        panel.dataset.vdScrollGuard = '1';

        var pending = null;
        var restoreScheduled = false;

        function fieldKey(element) {
            if (!element || !host.contains(element)) { return null; }
            var attrs = ['id', 'name', 'data-field', 'data-prop', 'data-responsive-field', 'data-v0120-field', 'data-border-field'];
            for (var i = 0; i < attrs.length; i += 1) {
                var value = element.getAttribute && element.getAttribute(attrs[i]);
                if (value) { return { attr: attrs[i], value: value, tag: String(element.tagName || '').toLowerCase() }; }
            }
            var label = element.closest && element.closest('label');
            if (label) {
                var labels = Array.prototype.slice.call(host.querySelectorAll('label'));
                var index = labels.indexOf(label);
                if (index >= 0) { return { labelIndex: index, tag: String(element.tagName || '').toLowerCase() }; }
            }
            return null;
        }

        function capture(event) {
            var target = event && event.target;
            if (!target || !host.contains(target) || !target.matches('input,select,textarea,button')) { return; }
            pending = {
                scrollTop: panel.scrollTop,
                key: fieldKey(target)
            };
        }

        function findField(key) {
            if (!key) { return null; }
            if (key.attr && key.value) {
                var candidates = host.querySelectorAll(key.tag || 'input,select,textarea,button');
                for (var i = 0; i < candidates.length; i += 1) {
                    if (candidates[i].getAttribute(key.attr) === key.value) { return candidates[i]; }
                }
            }
            if (typeof key.labelIndex === 'number') {
                var labels = host.querySelectorAll('label');
                var label = labels[key.labelIndex];
                if (label) { return label.querySelector(key.tag || 'input,select,textarea,button'); }
            }
            return null;
        }

        function scheduleRestore() {
            if (!pending || restoreScheduled) { return; }
            restoreScheduled = true;
            window.requestAnimationFrame(function () {
                window.requestAnimationFrame(function () {
                    restoreScheduled = false;
                    if (!pending) { return; }
                    var state = pending;
                    pending = null;
                    panel.scrollTop = state.scrollTop;
                    var replacement = findField(state.key);
                    if (replacement && typeof replacement.focus === 'function') {
                        try { replacement.focus({ preventScroll: true }); }
                        catch (ignore) { replacement.focus(); panel.scrollTop = state.scrollTop; }
                    }
                    panel.scrollTop = state.scrollTop;
                });
            });
        }

        host.addEventListener('input', capture, true);
        host.addEventListener('change', capture, true);
        host.addEventListener('click', capture, true);

        new MutationObserver(function () {
            if (pending) { scheduleRestore(); }
        }).observe(host, { childList: true, subtree: true });
    }

    document.addEventListener('DOMContentLoaded', function () {
        setupChangeNote();
        setupInspectorScrollPreservation();

        var button = document.getElementById('h18-clean-preview');
        var model = document.getElementById('h18-clean-model-json');
        if (!button || !model) { return; }
        button.addEventListener('click', function () {
            if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') {
                window.H18CleanV0120.sync();
            }
            var form = document.createElement('form');
            form.method = 'post';
            form.action = button.getAttribute('data-url') || '';
            form.target = '_blank';
            form.style.display = 'none';
            hidden(form, 'action', 'h18_clean_preview');
            hidden(form, '_wpnonce', button.getAttribute('data-nonce') || '');
            hidden(form, 'post_id', button.getAttribute('data-post-id') || '0');
            hidden(form, 'model_json', model.value || '{}');
            document.body.appendChild(form);
            form.submit();
            window.setTimeout(function () { form.remove(); }, 1000);
        });
    });
})();
