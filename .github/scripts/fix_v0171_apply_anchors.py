from pathlib import Path

path = Path(__file__).with_name('apply_v0171_event_module.py')
value = path.read_text(encoding='utf-8')

# AdminController in v0.1.70 uses the local $cap variable.
old = "replace_once(ADMIN, \"add_submenu_page(self::MENU, 'Events', 'Events', 'edit_pages', 'h18-clean-events', [self::class, 'events']);\", \"add_submenu_page(self::MENU, 'Events', 'Events', 'edit_pages', 'h18-clean-events', [EventAdminController::class, 'render']);\")"
new = "replace_once(ADMIN, \"add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [self::class, 'events']);\", \"add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [EventAdminController::class, 'render']);\")"
if new not in value:
    if old not in value:
        raise SystemExit('v0.1.71 apply AdminController anchor not found')
    value = value.replace(old, new, 1)

# Designer v0.1.70 keeps spaces in the defaultRows object literal.
old_rows = "replace_once(CORE, 'vehiclelist:42,vehicledetail:54', 'vehiclelist:42,vehicledetail:54,eventlist:38,eventdetail:46')"
new_rows = "replace_once(CORE, 'vehiclelist: 42, vehicledetail: 54', 'vehiclelist: 42, vehicledetail: 54, eventlist: 38, eventdetail: 46')"
if new_rows not in value:
    if old_rows not in value:
        raise SystemExit('v0.1.71 apply Designer defaultRows anchor not found')
    value = value.replace(old_rows, new_rows, 1)

path.write_text(value, encoding='utf-8')
print('v0.1.71 apply anchor fixes: ready')
