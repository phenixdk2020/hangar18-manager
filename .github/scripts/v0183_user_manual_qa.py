from pathlib import Path
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit('FAIL missing ' + rel)
    return p.read_text(encoding='utf-8')


def req(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit('FAIL: ' + message)
    print('PASS:', message)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
admin = text('clean/hangar18-manager/src/Admin/AdminController.php')
manual_controller = text('clean/hangar18-manager/src/Admin/ManualController.php')
admin_js = text('clean/hangar18-manager/assets/admin-v0123.js')
manual_css = text('clean/hangar18-manager/assets/manual-v0183.css')
manual = text('CLEAN-USER-MANUAL.md')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
notes = text('clean-release-notes.html')
status = text('docs/v0183-status.md')

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
req(header is not None and const is not None and header.group(1) == const.group(1) == '0.1.83', 'runtime/header version is exactly v0.1.83')
req("require_once H18_CLEAN_DIR . 'src/Admin/ManualController.php';" in plugin, 'ManualController is bootstrapped')
req('\\VisualDesignerManager\\Admin\\ManualController::register();' in plugin, 'ManualController is registered')

req("'h18-clean-manual'" in admin and 'Brugermanual' in admin, 'Manager has a Brugermanual submenu')
req("self::card('Brugermanual'" in admin, 'Dashboard has a Brugermanual card')
req("'h18-clean-manual': ['Klar', 'ready']" in admin_js, 'Brugermanual menu status is Klar')

req("public const PAGE_SLUG = 'visual-designer-brugermanual';" in manual_controller, 'manual has stable public page slug')
req("public const SHORTCODE = 'visual_designer_manager_manual';" in manual_controller, 'manual page uses a dedicated shortcode')
req("wp_insert_post" in manual_controller and "'post_status' => 'publish'" in manual_controller, 'manual WordPress page is auto-provisioned as published')
req("docs/user-manual.html" in manual_controller, 'website renderer uses the packaged HTML artifact')
req("docs/visual-designer-manager-brugermanual.docx" in manual_controller, 'Word download uses the packaged DOCX artifact')
req('Download som Word (.docx)' in manual_controller, 'website/admin manual exposes Word download action')
req('Åbn Visual Designer Manager' in manual_controller, 'website manual links back to the Manager')
req("str_replace('src=\"docs/user-manual-assets/" in manual_controller, 'manual rewrites bundled illustration URLs')
req("str_replace('src=\\\"docs/user-manual-assets/" not in manual_controller, 'manual image rewrite does not look for escaped HTML quotes')
req('.h18-vd-manual' in manual_css and '.h18-vd-manual-toolbar' in manual_css, 'manual has responsive website styling')

req('Brugermanualen på websitet' in manual, 'canonical user manual documents website access')
req('Download som Word (.docx)' in manual, 'canonical user manual documents Word download')
req('CLEAN-USER-MANUAL.md' in manual, 'canonical manual names its single source of truth')

artifact_md = ROOT / 'clean/hangar18-manager/docs/user-manual.md'
artifact_html = ROOT / 'clean/hangar18-manager/docs/user-manual.html'
artifact_docx = ROOT / 'clean/hangar18-manager/docs/visual-designer-manager-brugermanual.docx'
artifact_assets = ROOT / 'clean/hangar18-manager/docs/user-manual-assets'
req(artifact_md.is_file() and artifact_md.read_text(encoding='utf-8') == manual, 'packaged Markdown is byte-for-byte the canonical user manual')
req(artifact_html.is_file() and artifact_html.stat().st_size > 1000, 'packaged website HTML exists')
html = artifact_html.read_text(encoding='utf-8')
req('Visual Designer Manager' in html and 'Brugermanual' in html, 'packaged website HTML contains the manual')
req(artifact_docx.is_file() and artifact_docx.stat().st_size > 1000, 'packaged Word DOCX exists')
req(zipfile.is_zipfile(artifact_docx), 'Word artifact is a valid OOXML ZIP container')
with zipfile.ZipFile(artifact_docx) as zf:
    req('word/document.xml' in zf.namelist(), 'Word artifact contains word/document.xml')
for asset in ['page-anatomy.svg', 'lego-hierarchy.svg', 'table-borders.svg']:
    req((artifact_assets / asset).is_file(), 'packaged manual illustration exists: ' + asset)

versions = history.get('versions', []) if isinstance(history, dict) else []
req(bool(versions) and isinstance(versions[0], dict) and str(versions[0].get('version', '')) == '0.1.83', 'release history starts with v0.1.83')
req('VD-USER-MANUAL-WEB-001' in json.dumps(history, ensure_ascii=False), 'release history records web/Word manual contract')
req('data-version="0.1.83"' in notes and 'Word' in notes and 'Brugermanual' in notes, 'release notes document v0.1.83 manual feature')
req('VD-USER-MANUAL-WEB-001' in status and '0.1.83' in status, 'v0.1.83 status document exists and records contract')

print('Visual Designer Manager v0.1.83 user manual web/Word static QA: PASS')
