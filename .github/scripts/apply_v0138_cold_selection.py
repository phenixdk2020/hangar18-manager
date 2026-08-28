from pathlib import Path
import json

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(path, old, new):
    text = read(path)
    if old not in text:
        raise SystemExit(f'Missing expected text in {path}: {old[:180]!r}')
    write(path, text.replace(old, new, 1))


# Version
replace_once('clean/hangar18-manager/hangar18-manager.php', 'Version: 0.1.37', 'Version: 0.1.38')
replace_once("clean/hangar18-manager/hangar18-manager.php", "define('H18_CLEAN_VERSION', '0.1.37');", "define('H18_CLEAN_VERSION', '0.1.38');")

# ---------------------------------------------------------------------------
# VD-TEXT-SEL-001 / 0.1.38
# User QA of 0.1.37 showed a cold-start defect: the first 2-3 toolbar uses
# could lose selection, then the same editor became stable. In 0.1.37 the
# persistent selection markers were only installed on toolbar pointerdown.
# 0.1.38 pre-arms the marker session when the user finishes selecting text.
# ---------------------------------------------------------------------------
editor_path = 'clean/hangar18-manager/assets/editor-v0125.js'
editor = read(editor_path)

anchor = """    function captureToolbarSelection() {
        if (!active || !active.editor) { return; }
        if (markerSelectionValid()) {
            restoreMarkerSelection();
            return;
        }
        var logical = captureLogicalSelection(active.editor);
        if (logical) { active.savedLogical = logical; }
        rememberSelection();
        installSelectionMarkers();
    }
"""
if anchor not in editor:
    raise SystemExit('captureToolbarSelection anchor missing')

replacement = """    function primeSelectionSession(snapshot) {
        if (!active || !active.editor || active.formatting) { return false; }
        var logical = snapshot || captureLogicalSelection(active.editor);
        clearSelectionMarkers();
        selectionGeneration += 1;

        if (!logical || logical.editor !== active.editor || logical.end <= logical.start) {
            active.savedLogical = null;
            rememberSelection();
            return false;
        }

        active.savedLogical = logical;
        if (!restoreLogicalSelection(logical)) {
            rememberSelection();
            return false;
        }
        if (!installSelectionMarkers()) {
            restoreLogicalSelection(logical);
            rememberSelection();
            return false;
        }
        reinforceMarkerSelection();
        return true;
    }

    function schedulePrimeSelectionSession() {
        if (!active || !active.editor || active.formatting) { return; }
        var editor = active.editor;
        var logical = captureLogicalSelection(editor);
        if (!logical) {
            primeSelectionSession(null);
            return;
        }
        active.savedLogical = logical;
        window.setTimeout(function () {
            if (!active || active.editor !== editor || active.formatting || !editor.isConnected) { return; }
            primeSelectionSession(logical);
        }, 0);
    }

    function captureToolbarSelection() {
        if (!active || !active.editor) { return; }
        if (markerSelectionValid()) {
            restoreMarkerSelection();
            return;
        }
        var logical = captureLogicalSelection(active.editor) || active.savedLogical;
        if (logical) {
            active.savedLogical = logical;
            if (primeSelectionSession(logical)) { return; }
        }
        rememberSelection();
    }
"""
editor = editor.replace(anchor, replacement, 1)

old_handler = """        ['mouseup','keyup'].forEach(function (eventName) {
            editor.addEventListener(eventName, function () {
                if (!active || active.editor !== editor || active.formatting) { return; }
                clearSelectionMarkers();
                selectionGeneration += 1;
                rememberSelection();
            });
        });
"""
new_handler = """        ['mouseup','keyup'].forEach(function (eventName) {
            editor.addEventListener(eventName, function () {
                if (!active || active.editor !== editor || active.formatting) { return; }
                schedulePrimeSelectionSession();
            });
        });
"""
if old_handler not in editor:
    raise SystemExit('mouseup/keyup cold-start anchor missing')
editor = editor.replace(old_handler, new_handler, 1)

old_export = """        selectionOwner: 'v0125-authoritative',
        selectionMode: 'boundary-markers-v0137-single-owner',
"""
new_export = """        selectionOwner: 'v0125-authoritative',
        selectionMode: 'boundary-markers-v0137-single-owner',
        selectionSessionMode: 'prearmed-v0138',
"""
if old_export not in editor:
    raise SystemExit('selection export anchor missing')
editor = editor.replace(old_export, new_export, 1)
write(editor_path, editor)

# Release history
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
if not any(str(row.get('version')) == '0.1.38' for row in history if isinstance(row, dict)):
    history.insert(0, {
        'version': '0.1.38',
        'date': '2026-08-28',
        'items': [
            'BUG-02 cold-start rettelse: selection-sessionen oprettes nu, når tekstmarkeringen afsluttes, ikke først ved toolbar-klikket.',
            'Mouseup/keyup pre-armer start/slut-boundary-markørerne før første Fed/Kursiv/Understregning-klik.',
            'Toolbarens pointerdown er nu kun fallback, hvis en pre-armed selection-session mangler.',
            'Single-owner-reglen fra 0.1.37 bevares; v0131/v0132 må fortsat ikke køre konkurrerende selection restore-loops.',
            'Ingen ændringer til Billede-adfærd i denne release.'
        ]
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

# Technical manual
tech_path = 'CLEAN-TECHNICAL-MANUAL.md'
tech = read(tech_path)
tech = tech.replace('## 21. Kontraktstatus for 0.1.37', '## 21. Kontraktstatus for 0.1.38', 1)
old_para = "**BUGFIX i 0.1.37 – afventer bruger-QA.** Bruger-QA af 0.1.36 viste fortsat tab af selection ved Fed/Kursiv. Den konkrete regressionsårsag er identificeret: `v0131` og `v0132` deaktiverede kun deres gamle restore-loops, når `v0125.selectionOwner === 'v0134'`. Da den aktive owner-label senere blev ændret, blev legacy-loopene utilsigtet aktiveret igen og konkurrerede med den autoritative formatteringsmotor. I 0.1.37 er `v0125` permanent autoritativ ejer, og legacy-lag delegerer ved enhver truthy `selectionOwner`; kontrakten er dermed ikke versionsbundet. Boundary-marker motoren fra 0.1.36 bevares uændret som den eneste aktive selection-motor."
new_para = "**BUGFIX i 0.1.38 – afventer bruger-QA.** Bruger-QA af 0.1.37 viste et tydeligt cold-start-mønster: de første 2–3 formatteringer kunne miste selection, hvorefter samme editor-session blev stabil. 0.1.38 flytter derfor oprettelsen af boundary-marker-sessionen fra toolbar-pointerdown til afslutningen af selve tekstmarkeringen (`mouseup`/`keyup`). Når brugeren klikker Fed, Kursiv eller Understregning første gang, skal selection-sessionen allerede være etableret. Toolbar-pointerdown er kun fallback. Single-owner-kontrakten fra 0.1.37 bevares uændret."
if old_para not in tech:
    raise SystemExit('Technical manual 0.1.37 rich-text paragraph missing')
tech = tech.replace(old_para, new_para, 1)
qa = "Godkendelsestest: 20/20 gentagelser for Fed, Kursiv og Understregning samt kæderne Fed → Kursiv → Understregning og Kursiv → Fed → Understregning uden ny markering."
new_qa = qa + "\n\n**Cold-start-test er obligatorisk:** efter frisk reload vælges et Tekst-element, tekst markeres én gang, og første klik på Fed/Kursiv/Understregning skal både formatere og bevare samme selection. Testen gentages efter frisk reload i mindst Firefox og Chrome, før BUG-02 kan lukkes."
if qa not in tech:
    raise SystemExit('Technical manual QA anchor missing')
tech = tech.replace(qa, new_qa, 1)
write(tech_path, tech)

write('docs/v0138-status.md', """# Visual Designer Manager 0.1.38 – status

Dato: 28. august 2026

## Scope
- VD-TEXT-SEL-001 / BUG-02 cold-start only.
- Ingen Billede-rettelse i denne release.

## Observation fra 0.1.37
Bruger-QA i både Firefox/Chrome viste tidligere samme grundfejl, og 0.1.37 forbedrede adfærden: de første 2–3 forsøg kunne fortsat miste selection, mens formattering derefter blev stabil i samme editor-session.

## Fix
- selection-sessionen pre-armes ved afsluttet markering (`mouseup`/`keyup`);
- boundary-markører installeres før brugeren går til toolbaren;
- toolbar pointerdown bruger eksisterende marker-session og initialiserer kun som fallback;
- v0125 forbliver eneste autoritative selection-ejer;
- v0131/v0132 legacy restore-loops forbliver deaktiveret via versionsuafhængig delegation.

## Acceptance
Cold start efter frisk reload: første klik på Fed, Kursiv og Understregning skal bevare samme selection. Derefter 20/20 gentagelser og chaining. Minimum Firefox + Chrome før lukning af BUG-02.
""")

write('clean-release-notes.html', """<h4>0.1.38</h4><ul><li><strong>BUG-02 cold start:</strong> selection-sessionen etableres nu allerede, når tekstmarkeringen afsluttes.</li><li><strong>Første klik:</strong> Fed/Kursiv/Understregning skal ikke længere både initialisere selection og formatere i samme pointer-sekvens.</li><li><strong>Fallback:</strong> toolbar-pointerdown kan stadig genetablere sessionen, hvis den mangler.</li><li><strong>Single owner:</strong> den permanente v0125-ejer fra 0.1.37 bevares.</li><li><strong>QA:</strong> cold-start efter frisk reload er nu obligatorisk i Firefox og Chrome.</li><li><strong>Scope:</strong> ingen ændring til Billede-adfærd.</li></ul>""")

print('0.1.38 cold-start selection patch applied')
