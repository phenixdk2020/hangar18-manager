from pathlib import Path


def once(text, old, new, label):
    c=text.count(old)
    if c != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {c}')
    return text.replace(old,new,1)

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js')
php=php_path.read_text(); js=js_path.read_text()

old="""            $revision = $existing ? ((int) $existing['Revision'] + 1) : 1;
            $entry = [
"""
new="""            if ($existing) {
                $usage_before_update = $this->get_page_component_usage($component_id);
                if ($usage_before_update) {
                    $old_input_ids = array_values(array_filter(array_map(static function($input) { return sanitize_key((string) ($input['InputId'] ?? '')); }, (array) $existing['Inputs'])));
                    $new_input_ids = array_values(array_filter(array_map(static function($input) { return sanitize_key((string) ($input['InputId'] ?? '')); }, (array) $definition['Inputs'])));
                    sort($old_input_ids); sort($new_input_ids);
                    if ($old_input_ids !== $new_input_ids) {
                        throw new RuntimeException('Komponenten er i brug. Frigivne input-ID’er skal bevares ved global opdatering; opdater fra det oprindelige source-subtree eller fjern usage først.');
                    }
                }
            }
            $revision = $existing ? ((int) $existing['Revision'] + 1) : 1;
            $entry = [
"""
php=once(php,old,new,'component input identity guard')

old="""            const locked = String(pageSectionControls($row, '.h18-section-navigator-locked').val() || '0') === '1';
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
"""
new="""            const locked = String(pageSectionControls($row, '.h18-section-navigator-locked').val() || '0') === '1';
            $row.toggleClass('is-navigator-locked', locked);
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
"""
js=once(js,old,new,'locked row class')

old="""    $(document).on('click', '.h18-page-section-delete', function (event) {
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
"""
new="""    $(document).on('click', '.h18-page-section-delete', function (event) {
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        if (rowLockedV0521($row)) { window.alert('Laget er låst. Lås det op før du fjerner det.'); return; }
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
"""
js=once(js,old,new,'locked delete')

old="""    $(document).on('change', '.h18-page-section-type', function () {
        const $row = pageSectionForElement(this);
        const type = String($(this).val() || 'text');
"""
new="""    $(document).on('change', '.h18-page-section-type', function () {
        const $row = pageSectionForElement(this);
        if (rowLockedV0521($row)) {
            const previousType = String($row.attr('data-section-type') || 'text');
            $(this).val(previousType);
            window.alert('Laget er låst. Lås det op før du ændrer elementtype.');
            return;
        }
        const type = String($(this).val() || 'text');
"""
js=once(js,old,new,'locked type change')

old="""        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length) { return; }
        const existing = componentId ? pageLinkedComponents[String(componentId)] : null;
"""
new="""        const subtreeRows = componentSubtreeRowsV0521($inspectedSection);
        if (subtreeRows.some(function($row){ return ['legacy','component'].includes(String($row.attr('data-section-type') || '')); })) {
            window.alert('Subtreeet indeholder legacy eller en linked component. Nested linked components er ikke tilladt i denne version.');
            return;
        }
        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length) { return; }
        const existing = componentId ? pageLinkedComponents[String(componentId)] : null;
"""
js=once(js,old,new,'nested component subtree guard')

old="""    function contextMenuItemsV0515($row) {
        const type = String($row.attr('data-section-type') || 'text');
        const active = pageSectionControls($row, '.h18-section-active').is(':checked');
        const key = sectionKeyV0515($row);
        return [
"""
new="""    function contextMenuItemsV0515($row) {
        const type = String($row.attr('data-section-type') || 'text');
        const active = pageSectionControls($row, '.h18-section-active').is(':checked');
        const key = sectionKeyV0515($row);
        const lockedV0521 = rowLockedV0521($row);
        return [
"""
js=once(js,old,new,'context lock prelude')
repls={
"{ action: 'duplicate', label: 'Duplikér element', disabled: type === 'legacy' },":"{ action: 'duplicate', label: 'Duplikér element', disabled: type === 'legacy' || lockedV0521 },",
"{ action: 'component', label: 'Gem som pattern', disabled: type === 'legacy' },":"{ action: 'component', label: 'Gem som pattern', disabled: type === 'legacy' || type === 'component' || lockedV0521 },",
"{ action: 'toggle-active', label: active ? 'Skjul element' : 'Vis element' },":"{ action: 'toggle-active', label: active ? 'Skjul element' : 'Vis element', disabled: lockedV0521 },",
"{ action: 'move-up', label: 'Flyt op' },":"{ action: 'move-up', label: 'Flyt op', disabled: lockedV0521 },",
"{ action: 'move-down', label: 'Flyt ned' },":"{ action: 'move-down', label: 'Flyt ned', disabled: lockedV0521 },",
"{ action: 'delete', label: 'Fjern element', danger: true, disabled: type === 'legacy' }":"{ action: 'delete', label: 'Fjern element', danger: true, disabled: type === 'legacy' || lockedV0521 }",
}
for a,b in repls.items():
    if a in js: js=js.replace(a,b,1)
    else: raise SystemExit('context action anchor missing: '+a)

php_path.write_text(php); js_path.write_text(js)
print('v0.5.21 hardening applied')
