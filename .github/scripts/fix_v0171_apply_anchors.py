from pathlib import Path

path = Path(__file__).with_name('apply_v0171_event_module.py')
value = path.read_text(encoding='utf-8')
old = "replace_once(ADMIN, \"add_submenu_page(self::MENU, 'Events', 'Events', 'edit_pages', 'h18-clean-events', [self::class, 'events']);\", \"add_submenu_page(self::MENU, 'Events', 'Events', 'edit_pages', 'h18-clean-events', [EventAdminController::class, 'render']);\")"
new = "replace_once(ADMIN, \"add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [self::class, 'events']);\", \"add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [EventAdminController::class, 'render']);\")"
if new not in value:
    if old not in value:
        raise SystemExit('v0.1.71 apply AdminController anchor not found')
    path.write_text(value.replace(old, new, 1), encoding='utf-8')
print('v0.1.71 apply anchor fix: ready')
