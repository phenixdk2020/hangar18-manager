from pathlib import Path
import json
import re


def text(path):
    return Path(path).read_text(encoding='utf-8')


def req(ok, label):
    if not ok:
        raise SystemExit('FAIL: ' + label)
    print('PASS:', label)

plugin = text('clean/hangar18-manager/hangar18-manager.php')
layout = text('clean/hangar18-manager/src/Model/LayoutModel.php')
renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
event_admin = text('clean/hangar18-manager/src/Admin/EventAdminController.php')
admin_js = text('clean/hangar18-manager/assets/admin-v0178-events.js')
editor_controller = text('clean/hangar18-manager/src/Admin/EditorController.php')
editor = text('clean/hangar18-manager/assets/editor-v018-core.js')
migration = text('clean/hangar18-manager/src/Migration/EventDetailFactsMigration.php')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
notes = text('clean-release-notes.html')
status = text('docs/v0185-status.md')
manifest = json.loads(text('clean-update.json'))

match = re.search(r'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)', plugin)
req(match is not None, 'runtime version is readable')
runtime = tuple(map(int, match.group(1).split('.'))) if match else (0, 0, 0)
req(runtime >= (0, 1, 85), 'runtime version is v0.1.85 or newer')
req("src/Migration/EventDetailFactsMigration.php" in plugin and 'EventDetailFactsMigration::register();' in plugin, 'migration bootstrapped')
req("'eventfacts'" in layout and "if ($type === 'eventfacts')" in layout, 'LayoutModel accepts Eventfaktabånd')
for token in ['showDate', 'showTime', 'showLocation', 'showAddress', 'showContact', 'minCardWidth', 'cardBackground', 'accentColor', 'labelFontSize', 'valueFontSize']:
    req(token in layout, 'Eventfaktabånd model prop ' + token)
for token in ['showWhenEmpty', 'headingFontSize', 'headingFontWeight', 'headingLineHeight', 'headingGap', "'fontSize'", "'fontWeight'", "'lineHeight'"]:
    req(token in layout, 'Eventfelt typography prop ' + token)

req("if ($type === 'eventfacts')" in renderer, 'frontend Eventfaktabånd renderer')
for label in ["['Dato'", "['Tid'", "['Sted'", "['Adresse'", "['Kontakt'"]:
    req(label in renderer, 'frontend fact ' + label)
req('grid-template-columns:repeat(auto-fit,minmax(' in renderer, 'responsive auto-fit fact strip')
req('eventFactDateLabel' in renderer and 'eventFactTimeLabel' in renderer, 'old-style event date/time labels')
req("empty($props['showWhenEmpty'])" in renderer, 'empty Eventfelt policy')
req('headingFontSize' in renderer and 'headingGap' in renderer and 'h18-clean-front-event-field-heading' in renderer, 'frontend Eventfelt typography')

req('name="address"' in event_admin and 'name="contact"' in event_admin, 'Event admin Address and Contact inputs')
req("'address' => sanitize_text_field" in event_admin and "'contact' => sanitize_text_field" in event_admin, 'Event admin Address and Contact persistence')
req('data-event-field-index' in event_admin and "event_field_enabled['.$index.']" in event_admin, 'existing EventField rows are index keyed')
req('data-event-field-index' in admin_js and 'event_field_required[' in admin_js and 'nextIndex(host)' in admin_js, 'new EventField rows are index keyed')
req("'enabled'=>isset($enabled[$i])" in event_admin and "'showDetail'=>isset($detail[$i])" in event_admin, 'EventField flags save by row index')

req("'eventfacts' => 'Eventfaktabånd'" in editor_controller, 'Eventfaktabånd palette button')
req("'eventfacts'" in editor.split('const PARENT_TYPES', 1)[0], 'editor runtime recognizes Eventfaktabånd')
req("eventfacts:'Eventfaktabånd'" in editor and "eventfacts:'EVENTFAKTABÅND'" in editor, 'editor labels Eventfaktabånd')
req("if (type === 'eventfacts')" in editor and "node.type === 'eventfacts'" in editor, 'editor normalization and preview')
for token in ['eventFactsShowDate', 'eventFactsShowTime', 'eventFactsShowLocation', 'eventFactsShowAddress', 'eventFactsShowContact', 'eventFactsMinCardWidth', 'eventFactsLabelFontSize', 'eventFactsValueFontSize']:
    req(token in editor, 'Eventfaktabånd Inspector control ' + token)
for token in ['eventFieldShowWhenEmpty', 'headingFontFamily', 'headingFontSize', 'headingFontWeight', 'headingLineHeight', 'eventFieldHeadingGap']:
    req(token in editor, 'Eventfelt Inspector control ' + token)

req("get_page_by_path('event-detalje'" in migration, 'migration targets event detail page')
req("'event-date'" in migration and "'event-location'" in migration and "'event-facts'" in migration, 'migration replaces old date/location pair')
req('BACKUP_META' in migration and 'LayoutModel::saveVersion' in migration, 'migration backup and versioned save')
req("'showWhenEmpty'] = true" in migration and "'headingFontSize'] = 40" in migration, 'default content headings recreate old detail look')

versions = [str(row.get('version')) for row in history.get('versions', []) if isinstance(row, dict)]
req('0.1.85' in versions, 'release history includes v0.1.85')
req('data-version="0.1.85"' in notes and 'Eventfaktabånd' in notes, 'release notes include Eventfaktabånd')
req('Status: release candidate' in status and 'Eventfaktabånd' in status, 'v0.1.85 status document')
manifest_version = tuple(map(int, str(manifest.get('version', '0.0.0')).split('.')))
req((0, 1, 84) <= manifest_version <= runtime, 'central updater is compatible with v0.1.85+ runtime')

print('v0.1.85 EVENT FACTS + TYPOGRAPHY QA PASS')
