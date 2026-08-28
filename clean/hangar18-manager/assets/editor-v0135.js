(function () {
    'use strict';

    var inspector = null;
    var openPicker = null;

    function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
    function hex(value, fallback) {
        var v = String(value || '').trim();
        if (/^#[0-9a-f]{6}$/i.test(v)) { return v.toLowerCase(); }
        if (/^#[0-9a-f]{3}$/i.test(v)) { return ('#' + v.slice(1).split('').map(function (c) { return c + c; }).join('')).toLowerCase(); }
        return /^#[0-9a-f]{6}$/i.test(String(fallback || '')) ? String(fallback).toLowerCase() : '#000000';
    }
    function rgbFromHex(value) {
        var v = hex(value, '#000000').slice(1);
        return { r: parseInt(v.slice(0, 2), 16), g: parseInt(v.slice(2, 4), 16), b: parseInt(v.slice(4, 6), 16) };
    }
    function toHexByte(v) { return clamp(Math.round(v), 0, 255).toString(16).padStart(2, '0'); }
    function hexFromRgb(rgb) { return '#' + toHexByte(rgb.r) + toHexByte(rgb.g) + toHexByte(rgb.b); }
    function rgbToHsv(rgb) {
        var r = rgb.r / 255, g = rgb.g / 255, b = rgb.b / 255;
        var max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min, h = 0;
        if (d) {
            if (max === r) { h = 60 * (((g - b) / d) % 6); }
            else if (max === g) { h = 60 * (((b - r) / d) + 2); }
            else { h = 60 * (((r - g) / d) + 4); }
        }
        if (h < 0) { h += 360; }
        return { h: h, s: max ? d / max : 0, v: max };
    }
    function hsvToRgb(hsv) {
        var h = ((hsv.h % 360) + 360) % 360, s = clamp(hsv.s, 0, 1), v = clamp(hsv.v, 0, 1);
        var c = v * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = v - c;
        var r = 0, g = 0, b = 0;
        if (h < 60) { r = c; g = x; }
        else if (h < 120) { r = x; g = c; }
        else if (h < 180) { g = c; b = x; }
        else if (h < 240) { g = x; b = c; }
        else if (h < 300) { r = x; b = c; }
        else { r = c; b = x; }
        return { r: (r + m) * 255, g: (g + m) * 255, b: (b + m) * 255 };
    }
    function stateHex(p) { return hexFromRgb(hsvToRgb(p.state)); }

    function render(p) {
        var value = stateHex(p);
        p.sv.style.backgroundColor = 'hsl(' + Math.round(p.state.h) + ' 100% 50%)';
        p.marker.style.left = (p.state.s * 100) + '%';
        p.marker.style.top = ((1 - p.state.v) * 100) + '%';
        p.hue.value = String(Math.round(p.state.h));
        p.hex.value = value.toUpperCase();
        p.swatch.style.backgroundColor = value;
        p.preview.style.backgroundColor = value;
        p.value.textContent = value.toUpperCase();
    }
    function setHex(p, value) {
        var normalized = hex(value, '');
        if (!/^#[0-9a-f]{6}$/i.test(normalized)) { return false; }
        var hsv = rgbToHsv(rgbFromHex(normalized));
        p.state = { h: hsv.h, s: hsv.s, v: hsv.v };
        render(p);
        return true;
    }
    function close(p) {
        if (!p) { return; }
        p.panel.hidden = true;
        p.button.setAttribute('aria-expanded', 'false');
        if (openPicker === p) { openPicker = null; }
    }
    function svPointer(p, event) {
        var r = p.sv.getBoundingClientRect();
        if (!r.width || !r.height) { return; }
        p.state.s = clamp((event.clientX - r.left) / r.width, 0, 1);
        p.state.v = 1 - clamp((event.clientY - r.top) / r.height, 0, 1);
        render(p);
    }

    function enhance(input) {
        if (!input || input.dataset.vdColorEnhanced === '1') { return; }
        input.dataset.vdColorEnhanced = '1';
        var initial = hex(input.value, '#000000');

        // BUG-06: remove the native OS color dialog entirely. The original
        // data-field remains the canonical #RRGGBB change target.
        input.type = 'text';
        input.readOnly = true;
        input.hidden = true;

        var control = document.createElement('div');
        control.className = 'h18-vd-color-control';
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'h18-vd-color-button';
        button.setAttribute('aria-expanded', 'false');
        var swatch = document.createElement('span'); swatch.className = 'h18-vd-color-swatch';
        var value = document.createElement('span'); value.className = 'h18-vd-color-value';
        button.appendChild(swatch); button.appendChild(value);

        var panel = document.createElement('div'); panel.className = 'h18-vd-color-panel'; panel.hidden = true;
        var sv = document.createElement('div'); sv.className = 'h18-vd-color-sv';
        var marker = document.createElement('span'); marker.className = 'h18-vd-color-marker'; sv.appendChild(marker);
        var hue = document.createElement('input'); hue.type = 'range'; hue.min = '0'; hue.max = '359'; hue.className = 'h18-vd-color-hue';
        var values = document.createElement('div'); values.className = 'h18-vd-color-values';
        var preview = document.createElement('span'); preview.className = 'h18-vd-color-preview';
        var hexInput = document.createElement('input'); hexInput.type = 'text'; hexInput.maxLength = 7; hexInput.className = 'h18-vd-color-hex';
        values.appendChild(preview); values.appendChild(hexInput);
        var palette = document.createElement('div'); palette.className = 'h18-vd-color-palette';
        var actions = document.createElement('div'); actions.className = 'h18-vd-color-actions';
        var cancel = document.createElement('button'); cancel.type = 'button'; cancel.className = 'button'; cancel.textContent = 'Annuller';
        var apply = document.createElement('button'); apply.type = 'button'; apply.className = 'button button-primary'; apply.textContent = 'Anvend';
        actions.appendChild(cancel); actions.appendChild(apply);
        panel.appendChild(sv); panel.appendChild(hue); panel.appendChild(values); panel.appendChild(palette); panel.appendChild(actions);
        control.appendChild(button); control.appendChild(panel); input.parentNode.insertBefore(control, input.nextSibling);

        var start = rgbToHsv(rgbFromHex(initial));
        var p = { input: input, button: button, swatch: swatch, value: value, panel: panel, sv: sv, marker: marker, hue: hue, hex: hexInput, preview: preview, palette: palette, state: start, dragging: false, control: control };
        ['#ffffff','#000000','#808080','#c3ae83','#30382a','#d63638','#ff6900','#fcb900','#00a32a','#00a0d2','#2271b1','#3858e9','#8b5cf6','#d946ef','#e11d74'].forEach(function (color) {
            var chip = document.createElement('button'); chip.type = 'button'; chip.className = 'h18-vd-color-chip'; chip.style.backgroundColor = color; chip.title = color.toUpperCase();
            chip.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); setHex(p, color); });
            palette.appendChild(chip);
        });
        render(p);

        button.addEventListener('click', function (e) {
            e.preventDefault(); e.stopPropagation();
            if (openPicker && openPicker !== p) { close(openPicker); }
            if (!panel.hidden) { close(p); return; }
            setHex(p, input.value || initial); panel.hidden = false; button.setAttribute('aria-expanded', 'true'); openPicker = p;
        });
        sv.addEventListener('pointerdown', function (e) { e.preventDefault(); p.dragging = true; try { sv.setPointerCapture(e.pointerId); } catch (ignore) {} svPointer(p, e); });
        sv.addEventListener('pointermove', function (e) { if (p.dragging) { e.preventDefault(); svPointer(p, e); } });
        ['pointerup','pointercancel'].forEach(function (name) { sv.addEventListener(name, function () { p.dragging = false; }); });
        hue.addEventListener('input', function () { p.state.h = clamp(parseInt(hue.value || '0', 10) || 0, 0, 359); render(p); });
        hexInput.addEventListener('change', function () { if (!setHex(p, hexInput.value)) { render(p); } });
        cancel.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); setHex(p, input.value || initial); close(p); });
        apply.addEventListener('click', function (e) {
            e.preventDefault(); e.stopPropagation();
            input.value = stateHex(p); close(p); input.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }

    function enhanceAll() {
        if (!inspector) { inspector = document.getElementById('h18-clean-inspector'); }
        if (!inspector) { return; }
        inspector.querySelectorAll('input[type="color"][data-field]').forEach(enhance);
    }
    function install() {
        inspector = document.getElementById('h18-clean-inspector');
        if (!inspector) { return; }
        enhanceAll();
        if (window.MutationObserver) { new MutationObserver(enhanceAll).observe(inspector, { childList: true, subtree: true }); }
        document.addEventListener('pointerdown', function (e) { if (openPicker && !openPicker.control.contains(e.target)) { close(openPicker); } });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && openPicker) { close(openPicker); } });
    }

    window.H18ColorPickerV0135 = { enhance: enhanceAll, normalizeHex: hex, rgbToHsv: rgbToHsv, hsvToRgb: hsvToRgb };
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); } else { install(); }
}());
