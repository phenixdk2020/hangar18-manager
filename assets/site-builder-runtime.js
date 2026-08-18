(function () {
    'use strict';

    function closeSubmenus(shell, except) {
        shell.querySelectorAll('.h18-menu-item.is-submenu-open').forEach(function (item) {
            if (except && item === except) { return; }
            item.classList.remove('is-submenu-open');
            var button = item.querySelector(':scope > .h18-submenu-toggle');
            if (button) { button.setAttribute('aria-expanded', 'false'); }
        });
    }

    function enhanceMenu(shell) {
        if (!shell || shell.dataset.h18Enhanced === '1') { return; }
        shell.dataset.h18Enhanced = '1';
        shell.classList.add('is-enhanced');
        var mobileToggle = shell.querySelector('.h18-menu-mobile-toggle');
        var nav = shell.querySelector('[data-h18-menu]');

        if (mobileToggle && nav) {
            mobileToggle.addEventListener('click', function () {
                var open = !shell.classList.contains('is-mobile-open');
                shell.classList.toggle('is-mobile-open', open);
                mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
                if (!open) { closeSubmenus(shell); }
            });
        }

        shell.querySelectorAll('.h18-submenu-toggle').forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                var item = button.closest('.h18-menu-item');
                if (!item) { return; }
                var open = !item.classList.contains('is-submenu-open');
                closeSubmenus(shell, open ? item : null);
                item.classList.toggle('is-submenu-open', open);
                button.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
            button.addEventListener('keydown', function (event) {
                if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    button.click();
                    var item = button.closest('.h18-menu-item');
                    var first = item && item.querySelector(':scope > .h18-menu-list--submenu a');
                    if (first) { first.focus(); }
                }
            });
        });

        shell.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                closeSubmenus(shell);
                if (shell.classList.contains('is-mobile-open')) {
                    shell.classList.remove('is-mobile-open');
                    if (mobileToggle) {
                        mobileToggle.setAttribute('aria-expanded', 'false');
                        mobileToggle.focus();
                    }
                }
                return;
            }
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') { return; }
            var link = event.target.closest('.h18-menu-list--root > .h18-menu-item > .h18-menu-link');
            if (!link) { return; }
            var links = Array.prototype.slice.call(shell.querySelectorAll('.h18-menu-list--root > .h18-menu-item > .h18-menu-link'));
            var index = links.indexOf(link);
            if (index < 0 || links.length < 2) { return; }
            event.preventDefault();
            var delta = event.key === 'ArrowRight' ? 1 : -1;
            links[(index + delta + links.length) % links.length].focus();
        });

        document.addEventListener('click', function (event) {
            if (!shell.contains(event.target)) { closeSubmenus(shell); }
        });
    }

    function init() {
        document.querySelectorAll('[data-h18-menu-shell]').forEach(enhanceMenu);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
