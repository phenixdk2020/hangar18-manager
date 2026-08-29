from pathlib import Path
import runpy

runpy.run_path(str(Path('.github/scripts/fix_v0154_apply_anchors.py')), run_name='__main__')
runpy.run_path(str(Path('.github/scripts/apply_v0154_menu_ux_publish.py')), run_name='__main__')
