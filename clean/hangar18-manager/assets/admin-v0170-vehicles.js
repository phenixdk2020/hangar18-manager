(function () {
    'use strict';

    function ids(value) {
        return String(value || '').split(/[^0-9]+/).map(function (v) { return parseInt(v || '0', 10) || 0; }).filter(Boolean);
    }

    function preview(target, attachments) {
        var box = document.querySelector('[data-media-preview="' + target.id + '"]');
        if (!box) { return; }
        box.replaceChildren();
        if (!attachments.length) {
            var empty = document.createElement('span'); empty.className = 'description'; empty.textContent = 'Ingen billeder valgt'; box.appendChild(empty); return;
        }
        attachments.slice(0,20).forEach(function (attachment) {
            var data = attachment.toJSON ? attachment.toJSON() : attachment;
            var img = document.createElement('img');
            img.src = (data.sizes && data.sizes.thumbnail && data.sizes.thumbnail.url) || data.url || '';
            img.alt = '';
            if (img.src) { box.appendChild(img); }
        });
    }

    document.addEventListener('click', function (event) {
        var pick = event.target && event.target.closest ? event.target.closest('.h18-vd-media-pick') : null;
        if (pick) {
            event.preventDefault();
            var target = document.getElementById(String(pick.getAttribute('data-target') || ''));
            if (!target || !window.wp || !wp.media) { return; }
            var multiple = pick.getAttribute('data-multiple') === '1';
            var frame = wp.media({title: multiple ? 'Vælg galleribilleder' : 'Vælg primært billede',button:{text:'Brug billeder'},multiple:multiple,library:{type:'image'}});
            frame.on('select', function () {
                var selection = frame.state().get('selection');
                var items = selection.toArray();
                target.value = items.map(function (item) { return String(item.id || (item.get && item.get('id')) || ''); }).filter(Boolean).join(',');
                preview(target, items);
            });
            frame.open();
            return;
        }
        var clear = event.target && event.target.closest ? event.target.closest('.h18-vd-media-clear') : null;
        if (clear) {
            event.preventDefault();
            var clearTarget = document.getElementById(String(clear.getAttribute('data-target') || ''));
            if (clearTarget) { clearTarget.value = ''; preview(clearTarget, []); }
            return;
        }
        var add = event.target && event.target.closest ? event.target.closest('#h18-vd-add-vehicle-field') : null;
        if (add) {
            event.preventDefault();
            var host = document.getElementById('h18-vd-vehicle-field-rows'); if (!host) { return; }
            var row = document.createElement('div'); row.className = 'h18-vd-field-row'; row.setAttribute('data-vehicle-field-row','');
            row.innerHTML = '<input type="hidden" name="field_id[]" value=""><label>Navn<input required type="text" name="field_label[]" value=""></label><label>Type<select name="field_type[]"><option value="text">Tekst</option><option value="textarea">Flere linjer</option><option value="number">Tal</option><option value="integer">Heltal</option><option value="boolean">Ja/nej</option><option value="date">Dato</option></select></label><label>Enhed<input type="text" name="field_unit[]" value="" placeholder="fx kg"></label><label>Rækkefølge<input type="number" name="field_order[]" value="' + String((host.children.length + 1) * 10) + '"></label><label class="h18-clean-checkbox"><input type="checkbox" name="field_enabled[]" value="1" checked> Aktiv</label><button type="button" class="button-link-delete h18-vd-remove-vehicle-field">Fjern</button>';
            host.appendChild(row); row.querySelector('input[name="field_label[]"]').focus();
            return;
        }
        var remove = event.target && event.target.closest ? event.target.closest('.h18-vd-remove-vehicle-field') : null;
        if (remove) { event.preventDefault(); var fieldRow = remove.closest('[data-vehicle-field-row]'); if (fieldRow) { fieldRow.remove(); } }
    });
}());
