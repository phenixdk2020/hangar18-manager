(function () {
    'use strict';
    function hidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden'; input.name = name; input.value = value;
        form.appendChild(input);
    }
    document.addEventListener('DOMContentLoaded', function () {
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
