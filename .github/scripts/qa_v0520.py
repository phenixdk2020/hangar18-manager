from pathlib import Path

php = Path('hangar18-manager.php').read_text()
js = Path('assets/admin.js').read_text()
readme = Path('readme.txt').read_text()

checks = {
    'version': "Version: 0.5.20" in php and "const VERSION = '0.5.20';" in php,
    'page schema': php.count("'Version'        => '1.16'") == 3,
    'breakpoints': "'BreakpointMobileMaxPx' => 782" in php and "'BreakpointTabletMaxPx' => 1199" in php,
    'motion defaults': all(x in php for x in ["'MotionFastMs' => 120", "'MotionNormalMs' => 220", "'MotionSlowMs' => 420"]),
    'motion tokens': all(x in php for x in ['--h18-motion-fast:', '--h18-motion-normal:', '--h18-motion-slow:']),
    'focus tokens': '--h18-focus-ring:' in php and '--h18-focus-ring-width:' in php,
    'dynamic breakpoints': all(x in php for x in ['$mobile_breakpoint', '$tablet_breakpoint', '$tablet_min', '$desktop_min']),
    'state defaults': all(x in php for x in ["'TransitionPreset'       => 'Inherit'", "'FocusRingStyle'         => 'Global'", "'ActiveEffect'           => 'None'", "'DisabledOpacityPercent' => 55"]),
    'focus css': ':focus-visible{outline:var(--h18-focus-width' in php,
    'active css': 'h18-active-effect-press' in php and 'h18-active-effect-scale' in php,
    'disabled css': '[aria-disabled=true]' in php and '--h18-disabled-opacity' in php,
    'canvas states': all(x in js for x in ["'data-state': 'focus'", "'data-state': 'active'", "'data-state': 'disabled'", "['normal','hover','focus','active','disabled']"]),
    'palette states': "['normal','Normal'],['hover','Hover'],['focus','Focus'],['active','Aktiv'],['disabled','Disabled']" in js,
    'readme': 'page-editor schema til 1.16' in readme,
    'reduced motion': 'prefers-reduced-motion' in php,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Failed v0.5.20 checks: ' + repr(failed))

before_css = php[:php.index('private function page_editor_frontend_css')]
if '$mobile_breakpoint' in before_css or '$tablet_breakpoint' in before_css:
    raise SystemExit('Breakpoint variables leaked outside page-editor CSS function')
if '.h18-editor-section.h18-active-effect-scale:active' in php:
    raise SystemExit('Active effect incorrectly targets whole section')

print('v0.5.20 semantic QA passed')
