(function () {
    'use strict';

    const cfg = window.H18UpdaterSupportV0879 || {};

    function disableInstallWhenCurrent() {
        if (cfg.updateAvailable === true) { return; }
        document.querySelectorAll('form input[name="action"][value="h18_install_update"]').forEach(function (input) {
            const form = input.closest('form');
            if (!form) { return; }
            form.querySelectorAll('button[type="submit"],input[type="submit"]').forEach(function (button) {
                button.disabled = true;
                button.setAttribute('aria-disabled', 'true');
                button.title = 'Ingen nyere version er tilgængelig.';
            });
        });
    }

    function copyDiagnosis() {
        const value = JSON.stringify(cfg.diagnosis || {}, null, 2);
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(value).then(function () {
                const status = document.getElementById('h18-updater-copy-status');
                if (status) { status.textContent = 'Updater-diagnose kopieret.'; }
            });
            return;
        }
        const area = document.createElement('textarea');
        area.value = value;
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        document.execCommand('copy');
        area.remove();
        const status = document.getElementById('h18-updater-copy-status');
        if (status) { status.textContent = 'Updater-diagnose kopieret.'; }
    }

    function install() {
        disableInstallWhenCurrent();
        const button = document.getElementById('h18-copy-updater-diagnosis');
        if (button) { button.addEventListener('click', copyDiagnosis); }
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); } else { install(); }
}());
