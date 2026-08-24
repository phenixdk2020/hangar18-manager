(function () {
    'use strict';

    const cfg = window.H18UpdaterSupportV0879 || {};

    /*
     * Install eligibility is owned by PHP/render_updates().
     *
     * Do NOT disable the install form from localized JavaScript state. WordPress
     * localization may serialize scalar values as strings (for example "1"),
     * while PHP already renders the install form only when a newer compatible
     * release exists. A second JS owner previously caused a valid update button
     * to be disabled even though the server-side updater state was JA.
     */

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
        const button = document.getElementById('h18-copy-updater-diagnosis');
        if (button) { button.addEventListener('click', copyDiagnosis); }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
