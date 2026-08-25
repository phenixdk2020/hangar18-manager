(function () {
    'use strict';

    function hidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
    }

    function setupChangeNote() {
        var form = document.getElementById('h18-clean-save-form');
        var input = document.getElementById('h18-clean-change-note');
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!form || !input || !toolbar) { return; }

        input.type = 'text';
        input.required = true;
        input.maxLength = 180;
        input.autocomplete = 'off';
        input.placeholder = 'Fx: Flyttet billede og rettet overskrift';
        input.setAttribute('aria-label', 'Ændringer i denne version');

        var wrapper = document.createElement('label');
        wrapper.className = 'h18-clean-change-note-wrap';
        var caption = document.createElement('span');
        caption.textContent = 'Ændringer:';
        caption.className = 'h18-clean-change-note-label';
        wrapper.appendChild(caption);
        wrapper.appendChild(input);

        var firstSave = toolbar.querySelector('.h18-clean-save') || toolbar.lastElementChild;
        toolbar.insertBefore(wrapper, firstSave || null);

        form.addEventListener('submit', function (event) {
            if ((input.value || '').trim() !== '') { return; }
            event.preventDefault();
            window.alert('Skriv en kort ændringsbeskrivelse før siden gemmes som en ny version.');
            input.focus();
        });

        var historyHeaders = document.querySelectorAll('.h18-clean-history th');
        historyHeaders.forEach(function (header) {
            if ((header.textContent || '').trim() === 'Note') {
                header.textContent = 'Ændringer';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        setupChangeNote();

        var button = document.getElementById('h18-clean-preview');
        var model = document.getElementById('h18-clean-model-json');
        if (!button || !model) { return; }
        button.addEventListener('click', function () {
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
