from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
UX = ROOT / 'clean/hangar18-manager/assets/editor-v0123-ux.css'


def patch(path, old, new, expected=1):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'{path}: expected {expected}, found {count}: {old[:120]!r}')
    path.write_text(text.replace(old, new), encoding='utf-8')
    print('patched', path)

# Firefox/browser robust node unwrapping in rich text sanitizer.
patch(CORE,
"            if (!allowed.has(el.tagName)) { el.replaceWith(...Array.from(el.childNodes)); return; }",
"            if (!allowed.has(el.tagName)) {\n                const parent = el.parentNode;\n                if (parent) { while (el.firstChild) { parent.insertBefore(el.firstChild, el); } parent.removeChild(el); }\n                return;\n            }")

# A rendering error in one child must never blank its parent Section/Kasse or the whole canvas.
patch(CORE,
"            card.appendChild(header);\n            card.appendChild(cardContent(node));\n\n            if (PARENT_TYPES.includes(node.type)) {",
"            card.appendChild(header);\n            try {\n                card.appendChild(cardContent(node));\n            } catch (error) {\n                const failed = document.createElement('div');\n                failed.className = 'h18-clean-render-error';\n                failed.textContent = 'Elementet kunne ikke vises: ' + (error && error.message ? error.message : 'ukendt render-fejl');\n                card.appendChild(failed);\n                diag('node_render_error', { id: node.id, type: node.type, message: String(error && error.message || error || 'unknown') });\n            }\n\n            if (PARENT_TYPES.includes(node.type)) {")

patch(CORE,
"                renderSurface(node.id, inner);\n                card.appendChild(inner);",
"                try {\n                    renderSurface(node.id, inner);\n                } catch (error) {\n                    const failed = document.createElement('div');\n                    failed.className = 'h18-clean-render-error';\n                    failed.textContent = 'Indholdet i denne ' + typeLabel(node.type) + ' kunne ikke vises fuldt: ' + (error && error.message ? error.message : 'ukendt render-fejl');\n                    inner.appendChild(failed);\n                    diag('surface_render_error', { id: node.id, type: node.type, message: String(error && error.message || error || 'unknown') });\n                }\n                card.appendChild(inner);")

# Root failsafe: preserve canvas usability and show the concrete error instead of a blank white canvas.
patch(CORE,
"        if (canvas) {\n            renderSurface('', canvas);\n            reconcileLayoutAfterRender(canvas);\n        }",
"        if (canvas) {\n            try {\n                renderSurface('', canvas);\n                reconcileLayoutAfterRender(canvas);\n                canvas.removeAttribute('data-render-failed');\n            } catch (error) {\n                canvas.setAttribute('data-render-failed', '1');\n                if (!canvas.querySelector('.h18-clean-root-render-error')) {\n                    const failed = document.createElement('div');\n                    failed.className = 'h18-clean-root-render-error';\n                    failed.textContent = 'Designer-rendering fejlede, men layoutdata er bevaret: ' + (error && error.message ? error.message : 'ukendt fejl');\n                    canvas.appendChild(failed);\n                }\n                diag('root_render_error', { message: String(error && error.message || error || 'unknown'), state: structuralSummary() });\n            }\n        }")

with UX.open('a', encoding='utf-8') as f:
    f.write("\n/* 0.1.27 canvas recovery: never fail silently. */\n.h18-clean-render-error,.h18-clean-root-render-error{box-sizing:border-box;margin:8px;padding:10px 12px;border:2px solid #d63638;border-radius:4px;background:#fcf0f1;color:#8a2424;font-weight:600;white-space:normal;overflow-wrap:anywhere}\n.h18-clean-root-render-error{grid-column:1 / -1;min-height:52px}\n")

print('0.1.27 canvas recovery patch prepared')
