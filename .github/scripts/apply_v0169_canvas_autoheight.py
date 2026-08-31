from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f'{rel}: expected exactly one marker, found {count}: {old[:120]!r}')
    write(rel, value.replace(old, new, 1))


def append_once(rel: str, marker: str, block: str) -> None:
    value = read(rel)
    if marker in value:
        return
    if value and not value.endswith('\n'):
        value += '\n'
    write(rel, value + '\n' + block.strip() + '\n')


# Runtime version.
replace_once('clean/hangar18-manager/hangar18-manager.php', ' * Version: 0.1.68', ' * Version: 0.1.69')
replace_once(
    'clean/hangar18-manager/hangar18-manager.php',
    "define('H18_CLEAN_VERSION', '0.1.68');",
    "define('H18_CLEAN_VERSION', '0.1.69');",
)

# Canvas auto-height runtime. It is deliberately DOM-driven: root Sections are the
# canonical page-level elements, and their real editor extents already include the
# current responsive device and any materialized container height.
canvas_js = r'''(function () {
    'use strict';

    var BASE_HEIGHT = 650;
    var BOTTOM_SPACE = 32;
    var root = null;
    var resizeObserver = null;
    var mutationObserver = null;
    var observedSections = [];
    var scheduled = false;
    var lastHeight = 0;

    function directSections() {
        if (!root) { return []; }
        return Array.prototype.filter.call(root.children, function (child) {
            return child && child.classList && child.classList.contains('h18-clean-node--section') && child.hasAttribute('data-node-id');
        });
    }

    function positiveTranslateY(element) {
        if (!element || !element.style || !element.style.transform) { return 0; }
        var match = String(element.style.transform).match(/translate\([^,]+,\s*(-?\d+(?:\.\d+)?)px\)/i);
        if (!match) { return 0; }
        var value = parseFloat(match[1]);
        return Number.isFinite(value) && value > 0 ? value : 0;
    }

    function sectionBottom(section) {
        return Math.max(0, Number(section.offsetTop || 0)) +
            Math.max(0, Number(section.offsetHeight || 0)) +
            positiveTranslateY(section);
    }

    function desiredHeight() {
        var bottom = 0;
        directSections().forEach(function (section) {
            bottom = Math.max(bottom, sectionBottom(section));
        });
        return Math.max(BASE_HEIGHT, Math.ceil(bottom + (bottom > 0 ? BOTTOM_SPACE : 0)));
    }

    function observeSections() {
        if (!resizeObserver) { return; }
        observedSections.forEach(function (section) {
            try { resizeObserver.unobserve(section); } catch (ignore) {}
        });
        observedSections = directSections();
        observedSections.forEach(function (section) { resizeObserver.observe(section); });
    }

    function sync() {
        scheduled = false;
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return; }
        observeSections();
        var next = desiredHeight();
        if (next !== lastHeight || root.style.minHeight !== String(next) + 'px') {
            lastHeight = next;
            root.style.height = 'auto';
            root.style.minHeight = String(next) + 'px';
            root.setAttribute('data-vd-auto-height', '1');
            root.setAttribute('data-vd-auto-height-px', String(next));
            window.dispatchEvent(new CustomEvent('h18-vd-canvas-height', { detail: { height: next } }));
        }
    }

    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(sync);
    }

    function install() {
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return; }
        if (window.ResizeObserver) {
            resizeObserver = new ResizeObserver(schedule);
            observeSections();
        }
        if (window.MutationObserver) {
            mutationObserver = new MutationObserver(schedule);
            mutationObserver.observe(root, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class', 'data-geometry']
            });
        }
        window.addEventListener('h18-vd-viewport-fit', schedule);
        window.addEventListener('resize', schedule, { passive: true });
        document.addEventListener('click', function (event) {
            if (!event.target || !event.target.closest) { return; }
            if (event.target.closest('.h18-clean-device-button,#h18-clean-undo,#h18-clean-redo,#h18-clean-delete,#h18-clean-paste,#h18-clean-duplicate')) {
                schedule();
            }
        }, true);
        schedule();
    }

    window.H18VDCanvasAutoHeight = {
        refresh: schedule,
        height: function () { return lastHeight || desiredHeight(); },
        baseHeight: BASE_HEIGHT,
        bottomSpace: BOTTOM_SPACE
    };

    if (document.getElementById('h18-clean-canvas')) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
'''
write('clean/hangar18-manager/assets/editor-v0169-canvas-height.js', canvas_js)

# Shared Page + Header/Footer bootstrap: one runtime for both contexts.
enqueue_marker = "    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */\n"
enqueue_block = """    wp_enqueue_script(\n        'h18-clean-editor-v0169-canvas-height',\n        H18_CLEAN_URL . 'assets/editor-v0169-canvas-height.js',\n        ['h18-clean-editor-v0148-layers'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */\n"""
replace_once('clean/hangar18-manager/hangar18-manager.php', enqueue_marker, enqueue_block)

# Release history.
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
if not any(str(item.get('version', '')) == '0.1.69' for item in versions if isinstance(item, dict)):
    versions.insert(0, {
        'version': '0.1.69',
        'date': '2026-08-31',
        'items': [
            'VD-CANVAS-AUTOHEIGHT-001: Webside-canvas følger automatisk nederste kant på root-Sektionerne.',
            'Canvas vokser og krymper igen efter flytning, resize, add, paste/duplicate, delete, Undo/Redo og responsive skift.',
            'Kun direkte root-Sektioner bestemmer sidehøjden; child-elementer påvirker siden gennem deres Sektion.',
            'Viewport-stage følger via eksisterende ResizeObserver uden at skrive layoutgeometri eller frontend z-index.'
        ],
    })
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

append_once('CLEAN-TECHNICAL-MANUAL.md', 'VD-CANVAS-AUTOHEIGHT-001', r'''
## VD-CANVAS-AUTOHEIGHT-001 – Automatisk Webside-højde

Visual Designerens Webside/canvas er en visuel editor-ramme og må aldrig ende over eller midt i en canonical root-Sektion. `editor-v0169-canvas-height.js` måler kun direkte `Sektion`-børn af `#h18-clean-canvas` og sætter canvas `min-height` til nederste sektionskant + 32 px, dog mindst 650 px.

Kontrakten er dynamisk og tovejs: højden skal både kunne vokse og krympe efter flytning, resize, tilføjelse, paste/duplicate, sletning, Undo/Redo, indlæsning og responsive/viewport-skift. Beregningen er DOM-baseret, så den følger den aktive responsive editorvisning uden at ændre canonical node-geometri. Viewport-stage følger via den eksisterende ResizeObserver. Header/Footer bruger samme runtime.
''')
append_once('CLEAN-DESIGN-MANUAL.md', 'Canvas Auto Height', r'''
## Canvas Auto Height

Websiden er den yderste Designer-ramme omkring alle Sektioner. Den skal automatisk udvide sig til mindst 32 px under den nederste root-Sektion og må tilsvarende krympe igen, når indhold flyttes op eller slettes. Kun Sektioner ligger direkte på Websiden; derfor beregnes Webside-højden ud fra disse og ikke ud fra hvert enkelt child-element.
''')
append_once('CLEAN-USER-MANUAL.md', 'Websiden følger Sektionerne automatisk', r'''
## Websiden følger Sektionerne automatisk

Når du flytter eller ændrer størrelse på en Sektion, udvider den blå Webside/canvas sig automatisk, så Sektionen fortsat ligger inde på Websiden. Flytter du den nederste Sektion op eller sletter den, bliver Websiden tilsvarende kortere igen. Du skal ikke selv ændre Websidens højde.
''')

write('clean-release-notes.html', '''<h4>0.1.69 – Canvas Auto Height</h4>\n<ul>\n<li>Webside/canvas udvider sig automatisk under den nederste root-Sektion.</li>\n<li>Canvas krymper igen, når Sektioner flyttes op eller slettes.</li>\n<li>Synkronisering gælder flytning, resize, add, paste/duplicate, delete, Undo/Redo og responsive skift.</li>\n<li>Ingen canonical geometri eller frontend z-index ændres af auto-height.</li>\n</ul>\n''')
write('docs/v0169-status.md', '''# Visual Designer Manager v0.1.69\n\nStatus: release candidate\n\n- VD-CANVAS-AUTOHEIGHT-001 implementeret som delt Page/Header/Footer runtime.\n- Root canvas følger nederste direkte Sektion med 32 px bundluft og minimum 650 px.\n- Højden kan både vokse og krympe.\n- Viewport-stage følger eksisterende ResizeObserver.\n- Ingen modelmutation i auto-height runtime.\n''')

print('Applied Visual Designer Manager v0.1.69 canvas auto height')
