from pathlib import Path
import json
import re

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
workflow = text('.github/workflows/visual-designer-release.yml')
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
req("docs/user-manual.html" in manual_controller, 'website renderer uses the generated HTML artifact')
req("docs/visual-designer-manager-brugermanual.docx" in manual_controller, 'Word download uses the packaged DOCX artifact')
req('Download som Word (.docx)' in manual_controller, 'website/admin manual exposes Word download action')
req('Åbn Visual Designer Manager' in manual_controller, 'website manual links back to the Manager')
req('user-manual-assets' in manual_controller, 'manual rewrites bundled illustration URLs')
req('.h18-vd-manual' in manual_css and '.h18-vd-manual-toolbar' in manual_css, 'manual has responsive website styling')

req('Brugermanualen på websitet' in manual, 'canonical user manual documents website access')
req('Download som Word (.docx)' in manual, 'canonical user manual documents Word download')
req('CLEAN-USER-MANUAL.md' in manual, 'canonical manual names its single source of truth')

req('Build user manual artifacts' in workflow, 'release workflow builds manual artifacts')
req('pandoc CLEAN-USER-MANUAL.md' in workflow, 'release workflow generates outputs from the canonical Markdown manual')
req('visual-designer-manager-brugermanual.docx' in workflow, 'release workflow generates Word DOCX')
req('user-manual.html' in workflow and 'user-manual-assets' in workflow, 'release workflow packages website HTML and illustrations')
req("hangar18-manager/src/Admin/ManualController.php" in workflow, 'release package verifies ManualController')
req("hangar18-manager/docs/visual-designer-manager-brugermanual.docx" in workflow, 'release package verifies Word artifact')

versions = history.get('versions', []) if isinstance(history, dict) else []
req(bool(versions) and isinstance(versions[0], dict) and str(versions[0].get('version', '')) == '0.1.83', 'release history starts with v0.1.83')
req('VD-USER-MANUAL-WEB-001' in json.dumps(history, ensure_ascii=False), 'release history records web/Word manual contract')
req('data-version="0.1.83"' in notes and 'Word' in notes and 'Brugermanual' in notes, 'release notes document v0.1.83 manual feature')
req('VD-USER-MANUAL-WEB-001' in status and '0.1.83' in status, 'v0.1.83 status document exists and records contract')

print('Visual Designer Manager v0.1.83 user manual web/Word static QA: PASS')
