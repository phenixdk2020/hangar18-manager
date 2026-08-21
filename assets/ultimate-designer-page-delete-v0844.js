(function () {
    'use strict';

    var config = window.H18PageDeleteV0844 || {};
    var protectedSlugs = ['hjem', 'koeretoejer-og-materiel', 'events', 'billedgalleri'];

    function valueOf(selector, root) {
        var element = (root || document).querySelector(selector);
        return element && typeof element.value === 'string' ? element.value.trim() : '';
    }

    function findEditorForm() {
        var slugInput = document.querySelector('input[name="page_slug"]');
        return slugInput ? slugInput.closest('form') : null;
    }

    function pageTitle(form) {
        var selectors = [
            'input[name="page_title"]',
            'input[name="post_title"]',
            'input[name="title"]',
            'textarea[name="page_title"]'
        ];
        for (var i = 0; i < selectors.length; i += 1) {
            var title = valueOf(selectors[i], form);
            if (title) {
                return title;
            }
        }
        var heading = document.querySelector('.h18-page-editor h2, .h18-page-editor h1, .wrap h2');
        return heading ? heading.textContent.trim() : '';
    }

    function hidden(form, name, value) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
    }

    function submitDelete(slug, title) {
        var form = document.createElement('form');
        form.method = 'post';
        form.action = String(config.actionUrl || '');
        form.style.display = 'none';
        hidden(form, 'action', String(config.action || 'h18_ud_trash_page'));
        hidden(form, '_wpnonce', String(config.nonce || ''));
        hidden(form, 'page_slug', slug);
        hidden(form, 'confirm_title', title);
        document.body.appendChild(form);
        form.submit();
    }

    function mount() {
        if (!config.actionUrl || !config.nonce || document.querySelector('.h18-page-delete-button')) {
            return;
        }

        var editorForm = findEditorForm();
        if (!editorForm) {
            return;
        }
        var slug = valueOf('input[name="page_slug"]', editorForm);
        if (!slug || protectedSlugs.indexOf(slug) !== -1) {
            return;
        }

        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'button button-link-delete h18-page-delete-button';
        button.textContent = String(config.buttonLabel || 'Slet side');
        button.style.marginLeft = '8px';
        button.setAttribute('aria-label', 'Slet den valgte side sikkert');

        button.addEventListener('click', function () {
            var title = pageTitle(editorForm);
            if (!title) {
                window.alert('Siden kan ikke slettes sikkert, fordi sidens titel ikke kunne findes.');
                return;
            }

            var confirmed = window.prompt(
                'Skriv sidens titel præcist for at flytte den til WordPress Papirkurv:\n\n' + title,
                ''
            );
            if (confirmed === null) {
                return;
            }
            if (confirmed.trim() !== title) {
                window.alert('Titlen matcher ikke. Siden blev ikke slettet.');
                return;
            }
            if (!window.confirm('Flyt "' + title + '" til Papirkurv? Der oprettes en sikkerhedsbackup først.')) {
                return;
            }
            submitDelete(slug, title);
        });

        var submit = editorForm.querySelector('button[type="submit"], input[type="submit"]');
        if (submit && submit.parentNode) {
            submit.parentNode.insertBefore(button, submit.nextSibling);
        } else {
            editorForm.appendChild(button);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mount);
    } else {
        mount();
    }
}());
