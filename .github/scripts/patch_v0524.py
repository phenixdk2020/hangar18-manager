from pathlib import Path

php_path=Path('hangar18-manager.php')
js_path=Path('assets/admin.js')
css_path=Path('assets/admin.css')
readme_path=Path('readme.txt')
php=php_path.read_text()
js=js_path.read_text()
css=css_path.read_text()
readme=readme_path.read_text()

def once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old,new,1)

# Version + page-editor schema.
php=once(php,' * Version: 0.5.23',' * Version: 0.5.24','plugin header version')
php=once(php,"    const VERSION = '0.5.23';","    const VERSION = '0.5.24';",'plugin const version')
php=php.replace("'1.18'", "'1.19'")

# Runtime current-data context state.
php=once(php,
"""    private static $instance = null;

    public static function instance() {
""",
"""    private static $instance = null;
    private $active_dynamic_data_context = null;

    public static function instance() {
""",'dynamic context runtime property')

# Generic dynamic binding helpers before Page Editor block.
binding_engine=r'''

    /* ================================================================
       DYNAMIC BINDING ENGINE — v0.5.24 / E5 UD-053
       ================================================================ */

    private function dynamic_binding_property_types() {
        return [
            'Title' => ['text','number','bool','date'],
            'Content' => ['text','number','bool','date'],
            'MediaId' => ['media'],
            'Button1Label' => ['text','number','bool','date'],
            'Button1Url' => ['text'],
            'Button2Label' => ['text','number','bool','date'],
            'Button2Url' => ['text'],
        ];
    }

    private function normalize_dynamic_bindings($raw) {
        if (is_string($raw) && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) { $raw = $decoded; }
        }
        if (!is_array($raw)) { return []; }
        $allowed = $this->dynamic_binding_property_types();
        $bindings = [];
        foreach ($raw as $property => $field_key) {
            $property = (string) $property;
            if (!isset($allowed[$property])) { continue; }
            $field_key = sanitize_key((string) $field_key);
            if ($field_key === '') { continue; }
            $bindings[$property] = $field_key;
        }
        return $bindings;
    }

    private function dynamic_data_context_catalog_for_editor() {
        $types = $this->get_custom_data_types();
        $catalog = [];
        foreach ($types as $type_key => $type) {
            $catalog[$type_key] = [
                'Key' => $type_key,
                'SingularLabel' => (string) $type['SingularLabel'],
                'PluralLabel' => (string) $type['PluralLabel'],
                'Fields' => array_values((array) $type['Fields']),
                'Entries' => [],
            ];
        }
        if (!$catalog) { return []; }
        $entries = get_posts([
            'post_type' => self::DATA_ENTRY_POST_TYPE,
            'post_status' => ['publish','draft','private'],
            'posts_per_page' => 500,
            'orderby' => 'modified',
            'order' => 'DESC',
            'no_found_rows' => true,
        ]);
        foreach ($entries as $entry) {
            if (!$entry instanceof WP_Post) { continue; }
            $type_key = sanitize_key((string) get_post_meta($entry->ID, '_h18_data_type', true));
            if ($type_key === '' || !isset($catalog[$type_key]) || count($catalog[$type_key]['Entries']) >= 100) { continue; }
            $schema = $types[$type_key];
            $values = $this->custom_data_entry_values($entry->ID, $schema);
            $media_urls = [];
            foreach ($schema['Fields'] as $field) {
                if (($field['Type'] ?? '') !== 'media') { continue; }
                $field_key = (string) $field['Key'];
                $media_id = absint($values[$field_key] ?? 0);
                $url = $media_id ? wp_get_attachment_image_url($media_id, 'medium') : '';
                $media_urls[$field_key] = $url ? esc_url_raw($url) : '';
            }
            $catalog[$type_key]['Entries'][] = [
                'Id' => (int) $entry->ID,
                'Title' => (string) $entry->post_title,
                'Values' => $values,
                'MediaUrls' => $media_urls,
            ];
        }
        return array_values($catalog);
    }

    private function resolve_dynamic_data_context($type_key, $entry_id) {
        $type_key = sanitize_key((string) $type_key);
        $entry_id = absint($entry_id);
        if ($type_key === '' || $entry_id <= 0) { return null; }
        $types = $this->get_custom_data_types();
        if (!isset($types[$type_key])) { return null; }
        $entry = $this->custom_data_entry_for_type($entry_id, $type_key);
        if (!$entry instanceof WP_Post) { return null; }
        $field_map = [];
        foreach ($types[$type_key]['Fields'] as $field) {
            $field_map[(string) $field['Key']] = $field;
        }
        return [
            'TypeKey' => $type_key,
            'EntryId' => $entry_id,
            'EntryTitle' => (string) $entry->post_title,
            'Schema' => $types[$type_key],
            'Fields' => $field_map,
            'Values' => $this->custom_data_entry_values($entry_id, $types[$type_key]),
        ];
    }

    private function dynamic_binding_text_value($value) {
        if (is_bool($value)) { return $value ? 'Ja' : 'Nej'; }
        if (is_scalar($value)) { return (string) $value; }
        return '';
    }

    private function apply_dynamic_bindings_to_section(array $section, array $context) {
        $bindings = $this->normalize_dynamic_bindings($section['Bindings'] ?? []);
        if (!$bindings) { return $section; }
        $property_types = $this->dynamic_binding_property_types();
        $fields = isset($context['Fields']) && is_array($context['Fields']) ? $context['Fields'] : [];
        $values = isset($context['Values']) && is_array($context['Values']) ? $context['Values'] : [];
        foreach ($bindings as $property => $field_key) {
            if (!isset($fields[$field_key]) || !array_key_exists($field_key, $values)) { continue; }
            $field_type = (string) ($fields[$field_key]['Type'] ?? '');
            if (!in_array($field_type, $property_types[$property] ?? [], true)) { continue; }
            $value = $values[$field_key];
            if ($property === 'MediaId') {
                $section[$property] = absint($value);
                continue;
            }
            $text = $this->dynamic_binding_text_value($value);
            if (in_array($property, ['Button1Url','Button2Url'], true)) {
                $section[$property] = esc_url_raw($text);
            } elseif ($property === 'Content') {
                $section[$property] = wp_kses_post($text);
            } else {
                $section[$property] = sanitize_text_field($text);
            }
        }
        return $section;
    }
'''
php=once(php,
"""    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */
""",
binding_engine+"""

    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */
""",'insert dynamic binding engine')

# Section data model: static values remain untouched, Bindings is separate metadata.
php=once(php,
"""            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'Order'                 => (int) $order,
""",
"""            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
            'Bindings'              => [],
            'Order'                 => (int) $order,
""",'default section bindings')
php=once(php,
"""        $component_overrides = [];
        if (is_array($component_overrides_raw)) {
            foreach (array_slice($component_overrides_raw, 0, 40, true) as $override_id => $override_value) {
                $override_id = sanitize_key((string) $override_id);
                if ($override_id === '' || is_array($override_value) || is_object($override_value)) { continue; }
                $override_value = (string) $override_value;
                if (strlen($override_value) > 20000) { $override_value = substr($override_value, 0, 20000); }
                $component_overrides[$override_id] = wp_kses_post($override_value);
            }
        }

        $alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
""",
"""        $component_overrides = [];
        if (is_array($component_overrides_raw)) {
            foreach (array_slice($component_overrides_raw, 0, 40, true) as $override_id => $override_value) {
                $override_id = sanitize_key((string) $override_id);
                if ($override_id === '' || is_array($override_value) || is_object($override_value)) { continue; }
                $override_value = (string) $override_value;
                if (strlen($override_value) > 20000) { $override_value = substr($override_value, 0, 20000); }
                $component_overrides[$override_id] = wp_kses_post($override_value);
            }
        }
        $bindings = $this->normalize_dynamic_bindings($raw['Bindings'] ?? []);

        $alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
""",'normalize bindings')
php=once(php,
"""            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
""",
"""            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
            'Bindings'              => $bindings,
            'Order'                 => $this->clamp_int($raw['Order'] ?? $section['Order'], 1, 10000, $section['Order']),
""",'normalized section bindings return')

# Page-level current data context. Invalid or cross-type entry clears context.
php=once(php,
"""        $content_version = $this->clamp_int($raw['ContentVersion'] ?? 0, 0, 9999, 0);
        if (
            $content_version === 0 &&
            $page instanceof WP_Post &&
            strpos((string) $page->post_content, self::PAGE_EDITOR_MARKER) !== false
        ) {
            $content_version = 1;
        }

        return [
            'Version'        => '1.19',
            'PageSlug'       => $slug,
            'PageTitle'      => $title,
            'ContentVersion' => $content_version,
            'Sections'       => $sections,
        ];
""",
"""        $content_version = $this->clamp_int($raw['ContentVersion'] ?? 0, 0, 9999, 0);
        if (
            $content_version === 0 &&
            $page instanceof WP_Post &&
            strpos((string) $page->post_content, self::PAGE_EDITOR_MARKER) !== false
        ) {
            $content_version = 1;
        }
        $data_context_type = sanitize_key((string) ($raw['DataContextType'] ?? ''));
        $data_context_entry_id = absint($raw['DataContextEntryId'] ?? 0);
        if ($data_context_type === '' || $data_context_entry_id <= 0 || !$this->resolve_dynamic_data_context($data_context_type, $data_context_entry_id)) {
            $data_context_type = '';
            $data_context_entry_id = 0;
        }

        return [
            'Version'            => '1.19',
            'PageSlug'           => $slug,
            'PageTitle'          => $title,
            'ContentVersion'     => $content_version,
            'DataContextType'    => $data_context_type,
            'DataContextEntryId' => $data_context_entry_id,
            'Sections'           => $sections,
        ];
""",'page context normalization')

# Preserve page context through admin conversion normalization.
php=once(php,
"""            'PageTitle'      => $data['PageTitle'],
            'ContentVersion' => $data['ContentVersion'] ?? 0,
            'Sections'       => array_slice($sections, 0, 25),
""",
"""            'PageTitle'          => $data['PageTitle'],
            'ContentVersion'     => $data['ContentVersion'] ?? 0,
            'DataContextType'    => $data['DataContextType'] ?? '',
            'DataContextEntryId' => $data['DataContextEntryId'] ?? 0,
            'Sections'           => array_slice($sections, 0, 25),
""",'admin context preservation')

# Save page context.
php=once(php,
"""            'PageTitle'      => $this->post_text('editor_page_title'),
            'ContentVersion' => $next_content_version,
            'Sections'       => $sections,
""",
"""            'PageTitle'          => $this->post_text('editor_page_title'),
            'ContentVersion'     => $next_content_version,
            'DataContextType'    => sanitize_key((string) wp_unslash($_POST['data_context_type'] ?? '')),
            'DataContextEntryId' => absint($_POST['data_context_entry_id'] ?? 0),
            'Sections'           => $sections,
""",'save page context')

# Resolve context once per page render, then apply bindings per section.
php=once(php,
"""    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
        if (empty($section['Active'])) {
            return '';
        }
        if ($section['Type'] === 'component') {
""",
"""    private function render_page_editor_section_front($page_id, array $section, $layout_children = '') {
        if (empty($section['Active'])) {
            return '';
        }
        if (is_array($this->active_dynamic_data_context)) {
            $section = $this->apply_dynamic_bindings_to_section($section, $this->active_dynamic_data_context);
        }
        if ($section['Type'] === 'component') {
""",'runtime section binding')
php=once(php,
"""    private function render_page_editor_front($page_id, array $data) {
        $html = $this->page_editor_frontend_css($page_id) . '<div class=\"h18-editor-page\">';
""",
"""    private function render_page_editor_front($page_id, array $data) {
        $this->active_dynamic_data_context = $this->resolve_dynamic_data_context(
            (string) ($data['DataContextType'] ?? ''),
            (int) ($data['DataContextEntryId'] ?? 0)
        );
        $html = $this->page_editor_frontend_css($page_id) . '<div class=\"h18-editor-page\">';
""",'runtime page context')

# Admin catalog and context UI.
php=once(php,
"""        $page_presets = $this->get_page_presets();
        $page_components = $this->get_page_components_for_editor();
        $page_templates = $this->get_page_templates_for_editor();
        ?>
""",
"""        $page_presets = $this->get_page_presets();
        $page_components = $this->get_page_components_for_editor();
        $page_templates = $this->get_page_templates_for_editor();
        $dynamic_data_catalog = $this->dynamic_data_context_catalog_for_editor();
        ?>
""",'admin data catalog')
context_card=r'''
                    <div class="h18-page-data-context h18-layout-card">
                        <div class="h18-field">
                            <label><strong>Current data context – datatype</strong></label>
                            <select id="h18-page-data-context-type" name="data_context_type">
                                <option value="">Ingen – brug statiske værdier</option>
                                <?php foreach ($dynamic_data_catalog as $context_type) : ?>
                                    <option value="<?php echo esc_attr($context_type['Key']); ?>" <?php selected((string) ($data['DataContextType'] ?? ''), (string) $context_type['Key']); ?>><?php echo esc_html($context_type['PluralLabel']); ?></option>
                                <?php endforeach; ?>
                            </select>
                            <p class="description">Bindings bruger kun den valgte entry. Static elementværdier bevares som fallback.</p>
                        </div>
                        <div class="h18-field">
                            <label><strong>Current data context – entry</strong></label>
                            <select id="h18-page-data-context-entry" name="data_context_entry_id" data-current-entry="<?php echo esc_attr((int) ($data['DataContextEntryId'] ?? 0)); ?>"><option value="0">Ingen entry</option></select>
                        </div>
                    </div>

'''
php=once(php,
"""                    </div>

                    <div class=\"h18-page-preview-toolbar\">
""",
"""                    </div>

"""+context_card+"""                    <div class=\"h18-page-preview-toolbar\">
""",'page context card')
php=once(php,
"""                <script id=\"h18-page-templates-data\" type=\"application/json\"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id=\"h18-page-section-template\">
""",
"""                <script id=\"h18-page-templates-data\" type=\"application/json\"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id=\"h18-dynamic-data-catalog\" type=\"application/json\"><?php echo wp_json_encode(array_values($dynamic_data_catalog), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id=\"h18-page-section-template\">
""",'dynamic catalog JSON')

# Binding controls in Inspector. Values are options populated client-side from selected datatype.
binding_box=r'''

                    <div class="h18-section-module-box h18-dynamic-binding-box">
                        <h4>Dynamic data binding</h4>
                        <p class="description">Bind sikre elementegenskaber til current data context. Hvis context/field ikke findes, bruges elementets statiske værdi.</p>
                        <?php
                        $binding_rows = [
                            'Title' => ['Overskrift', 'hero text text_image image buttons card card_grid tabs accordion carousel container flex grid highlight icon list badge quote mail_form poll', 'text number bool date'],
                            'Content' => ['Tekst / indhold', 'hero text text_image buttons card card_grid tabs accordion carousel container flex grid highlight icon list quote mail_form poll', 'text number bool date'],
                            'MediaId' => ['Billede', 'hero text_image image', 'media'],
                            'Button1Label' => ['Knap 1 – tekst', 'hero buttons', 'text number bool date'],
                            'Button1Url' => ['Knap 1 – link', 'hero buttons', 'text'],
                            'Button2Label' => ['Knap 2 – tekst', 'hero buttons', 'text number bool date'],
                            'Button2Url' => ['Knap 2 – link', 'hero buttons', 'text'],
                        ];
                        foreach ($binding_rows as $binding_property => $binding_config) :
                            $binding_value = (string) (($section['Bindings'][$binding_property] ?? ''));
                        ?>
                            <div class="h18-field h18-dynamic-binding-row" data-types="<?php echo esc_attr($binding_config[1]); ?>">
                                <label><strong><?php echo esc_html($binding_config[0]); ?></strong></label>
                                <select class="h18-dynamic-binding-select" name="<?php echo esc_attr($prefix); ?>[Bindings][<?php echo esc_attr($binding_property); ?>]" data-binding-property="<?php echo esc_attr($binding_property); ?>" data-allowed-types="<?php echo esc_attr($binding_config[2]); ?>" data-binding-value="<?php echo esc_attr($binding_value); ?>"><option value="">Statisk værdi</option></select>
                            </div>
                        <?php endforeach; ?>
                    </div>
'''
php=once(php,
"""                        <input class=\"h18-advanced-content-authorized\" type=\"hidden\" name=\"<?php echo esc_attr($prefix); ?>[AdvancedContentAuthorized]\" value=\"<?php echo !empty($section['AdvancedContentAuthorized']) ? '1' : '0'; ?>\" />
                    </div>

                    <div class=\"h18-section-type-field h18-section-module-box h18-component-instance-editor\" data-types=\"component\">
""",
"""                        <input class=\"h18-advanced-content-authorized\" type=\"hidden\" name=\"<?php echo esc_attr($prefix); ?>[AdvancedContentAuthorized]\" value=\"<?php echo !empty($section['AdvancedContentAuthorized']) ? '1' : '0'; ?>\" />
                    </div>
"""+binding_box+"""
                    <div class=\"h18-section-type-field h18-section-module-box h18-component-instance-editor\" data-types=\"component\">
""",'binding inspector box')

# JS state/catalog parse.
js=once(js,
"""    const $pageTemplatesList = $('#h18-page-templates-list');
    let pageSectionNextIndex = 0;
""",
"""    const $pageTemplatesList = $('#h18-page-templates-list');
    const $pageDataContextTypeV0524 = $('#h18-page-data-context-type');
    const $pageDataContextEntryV0524 = $('#h18-page-data-context-entry');
    let pageSectionNextIndex = 0;
""",'JS context refs')
js=once(js,
"""    const pageLinkedComponents = {};
    const pageTemplatesV0522 = {};
    let navigatorLockedOrderSnapshotV0521 = null;
""",
"""    const pageLinkedComponents = {};
    const pageTemplatesV0522 = {};
    const pageDynamicDataCatalogV0524 = {};
    let navigatorLockedOrderSnapshotV0521 = null;
""",'JS catalog state')
parse_anchor="""    } catch(templateError){ window.console&&console.warn('Hangar18: kunne ikke læse Page Templates.',templateError); }

    const builtInSectionPresets = {
"""
parse_new="""    } catch(templateError){ window.console&&console.warn('Hangar18: kunne ikke læse Page Templates.',templateError); }
    try {
        const dataNode = document.getElementById('h18-dynamic-data-catalog');
        const parsedDataTypes = dataNode ? JSON.parse(dataNode.textContent || '[]') : [];
        (Array.isArray(parsedDataTypes) ? parsedDataTypes : []).forEach(function (type) {
            if (type && type.Key) { pageDynamicDataCatalogV0524[String(type.Key)] = type; }
        });
    } catch (dynamicDataError) {
        window.console && console.warn('Hangar18: kunne ikke læse dynamic data catalog.', dynamicDataError);
    }

    const builtInSectionPresets = {
"""
js=once(js,parse_anchor,parse_new,'dynamic catalog parse')

# Dynamic context/binding client helpers, before built-in presets.
js_helpers=r'''

    function dynamicContextDefinitionV0524() {
        return pageDynamicDataCatalogV0524[String($pageDataContextTypeV0524.val() || '')] || null;
    }
    function dynamicContextEntryV0524() {
        const definition = dynamicContextDefinitionV0524();
        const id = parseInt($pageDataContextEntryV0524.val(), 10) || 0;
        if (!definition || !Array.isArray(definition.Entries) || !id) { return null; }
        return definition.Entries.find(function (entry) { return parseInt(entry.Id,10) === id; }) || null;
    }
    function refreshPageDataContextEntriesV0524(preserveCurrent) {
        if (!$pageDataContextEntryV0524.length) { return; }
        const definition = dynamicContextDefinitionV0524();
        let current = preserveCurrent ? (parseInt($pageDataContextEntryV0524.attr('data-current-entry'),10) || parseInt($pageDataContextEntryV0524.val(),10) || 0) : 0;
        $pageDataContextEntryV0524.empty().append($('<option>', { value: '0', text: 'Ingen entry' }));
        if (definition && Array.isArray(definition.Entries)) {
            definition.Entries.forEach(function (entry) { $pageDataContextEntryV0524.append($('<option>', { value: String(entry.Id), text: String(entry.Title || ('Entry ' + entry.Id)) })); });
        }
        if (!$pageDataContextEntryV0524.find('option[value="' + String(current) + '"]').length) { current = 0; }
        $pageDataContextEntryV0524.val(String(current)).attr('data-current-entry', String(current));
    }
    function refreshDynamicBindingsV0524($scope) {
        const definition = dynamicContextDefinitionV0524();
        const fields = definition && Array.isArray(definition.Fields) ? definition.Fields : [];
        const $selects = $scope && $scope.length ? $scope.find('.h18-dynamic-binding-select').addBack('.h18-dynamic-binding-select') : $('.h18-dynamic-binding-select');
        $selects.each(function () {
            const $select = $(this);
            const $row = pageSectionForElement($select);
            const sectionType = String($row.attr('data-section-type') || 'text');
            const $bindingRow = $select.closest('.h18-dynamic-binding-row');
            const sectionTypes = String($bindingRow.attr('data-types') || '').split(/\s+/).filter(Boolean);
            $bindingRow.toggle(sectionTypes.includes(sectionType));
            const allowedTypes = String($select.attr('data-allowed-types') || '').split(/\s+/).filter(Boolean);
            let current = String($select.attr('data-binding-value') || $select.val() || '');
            $select.empty().append($('<option>', { value: '', text: 'Statisk værdi' }));
            fields.forEach(function (field) {
                if (!field || !allowedTypes.includes(String(field.Type || ''))) { return; }
                $select.append($('<option>', { value: String(field.Key || ''), text: String(field.Label || field.Key) + ' · ' + String(field.Type || '') }));
            });
            if (current && !$select.find('option[value="' + current.replace(/"/g,'\\"') + '"]').length) {
                $select.append($('<option>', { value: current, text: current + ' · felt mangler/er inkompatibelt', disabled: true }));
            }
            $select.val(current).attr('data-binding-value', current);
        });
    }
    function dynamicPreviewBindingV0524($row, property) {
        const $select = pageSectionControls($row, '.h18-dynamic-binding-select[data-binding-property="' + property + '"]').first();
        const fieldKey = String($select.val() || $select.attr('data-binding-value') || '');
        if (!$select.length || !fieldKey) { return { bound:false }; }
        const definition = dynamicContextDefinitionV0524();
        const entry = dynamicContextEntryV0524();
        if (!definition || !entry) { return { bound:false }; }
        const field = (Array.isArray(definition.Fields) ? definition.Fields : []).find(function (item) { return String(item.Key || '') === fieldKey; });
        if (!field) { return { bound:false }; }
        const allowed = String($select.attr('data-allowed-types') || '').split(/\s+/).filter(Boolean);
        if (!allowed.includes(String(field.Type || ''))) { return { bound:false }; }
        const values = entry.Values && typeof entry.Values === 'object' ? entry.Values : {};
        if (!Object.prototype.hasOwnProperty.call(values, fieldKey)) { return { bound:false }; }
        let value = values[fieldKey];
        if (typeof value === 'boolean' && property !== 'MediaId') { value = value ? 'Ja' : 'Nej'; }
        const mediaUrls = entry.MediaUrls && typeof entry.MediaUrls === 'object' ? entry.MediaUrls : {};
        return { bound:true, value:value == null ? '' : value, mediaUrl:String(mediaUrls[fieldKey] || '') };
    }
    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($pageSections); refreshAllCanvasPreviews(); scheduleEditorHistoryCapture(0); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || 0)); refreshAllCanvasPreviews(); scheduleEditorHistoryCapture(0); });
    $(document).on('change', '.h18-dynamic-binding-select', function () { $(this).attr('data-binding-value', String($(this).val() || '')); renderCanvasPreview(pageSectionForElement(this)); scheduleEditorHistoryCapture(0); });
    refreshPageDataContextEntriesV0524(true);
    refreshDynamicBindingsV0524($pageSections);
'''
js=once(js,"\n    const builtInSectionPresets = {",js_helpers+"\n    const builtInSectionPresets = {",'dynamic JS helpers')

# Preserve Bindings in Patterns/Components/Templates serialization.
js=once(js,
"""        if (data.Type === 'component') { return null; }
        const cards = {};
        pageSectionControls($row, '[name]').each(function () {
            const $field = $(this);
            const name = String($field.attr('name') || '');
            let match = name.match(/^sections\\[[^\\]]+\\]\\[Cards\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
""",
"""        if (data.Type === 'component') { return null; }
        const cards = {};
        const bindings = {};
        pageSectionControls($row, '[name]').each(function () {
            const $field = $(this);
            const name = String($field.attr('name') || '');
            let match = name.match(/^sections\\[[^\\]]+\\]\\[Bindings\\]\\[([^\\]]+)\\]$/);
            const value = $field.is(':checkbox') ? $field.is(':checked') : $field.val();
            if (match) {
                if (value) { bindings[String(match[1])] = String(value); }
                return;
            }
            match = name.match(/^sections\\[[^\\]]+\\]\\[Cards\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
""",'serialize bindings')
# Remove duplicate const value introduced by replacement (old block contains it immediately after regex).
js=once(js,
"""            match = name.match(/^sections\\[[^\\]]+\\]\\[Cards\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
            const value = $field.is(':checkbox') ? $field.is(':checked') : $field.val();
            if (match) {
""",
"""            match = name.match(/^sections\\[[^\\]]+\\]\\[Cards\\]\\[([^\\]]+)\\]\\[([^\\]]+)\\]$/);
            if (match) {
""",'deduplicate serialization value')
js=once(js,
"""        data.Cards = Object.keys(cards).sort(function (a, b) { return Number(a) - Number(b); }).map(function (index) { return cards[index]; });
        return data;
""",
"""        data.Cards = Object.keys(cards).sort(function (a, b) { return Number(a) - Number(b); }).map(function (index) { return cards[index]; });
        data.Bindings = bindings;
        return data;
""",'serialized bindings output')
js=once(js,
"""            if (['Type', 'Cards', 'Key', 'Order', 'Remove', 'LayoutParentKey'].includes(fieldName)) {
""",
"""            if (['Type', 'Cards', 'Bindings', 'Key', 'Order', 'Remove', 'LayoutParentKey'].includes(fieldName)) {
""",'skip nested bindings in standard preset apply')
js=once(js,
"""        $row.find('.h18-page-section-type').val(type);
        if (Array.isArray(presetData.Cards) && ['card_grid', 'tabs', 'accordion', 'carousel'].includes(type)) {
""",
"""        $row.find('.h18-page-section-type').val(type);
        if (presetData.Bindings && typeof presetData.Bindings === 'object') {
            Object.keys(presetData.Bindings).forEach(function (property) {
                pageSectionControls($row, '.h18-dynamic-binding-select[data-binding-property="' + property + '"]').attr('data-binding-value', String(presetData.Bindings[property] || ''));
            });
        }
        if (Array.isArray(presetData.Cards) && ['card_grid', 'tabs', 'accordion', 'carousel'].includes(type)) {
""",'restore preset bindings')

# Inspector type refresh updates binding rows/options.
js=once(js,
"""        if (type === 'component') { renderComponentInstanceEditorV0521($row); }
        rebuildPageNavigator();
""",
"""        if (type === 'component') { renderComponentInstanceEditorV0521($row); }
        refreshDynamicBindingsV0524($row);
        rebuildPageNavigator();
""",'refresh binding inspector')

# Canvas preview resolves bindings before static DOM values, including media URL preview.
js=once(js,
"""    function canvasFieldValue($row, fieldName, fallback) {
        const $field = pageSectionControls($row, '[name$=\"[' + fieldName + ']\"]').first();
""",
"""    function canvasFieldValue($row, fieldName, fallback) {
        if (fieldName === 'MediaUrl') {
            const mediaBinding = dynamicPreviewBindingV0524($row, 'MediaId');
            if (mediaBinding.bound) { return mediaBinding.mediaUrl || ''; }
        }
        const dynamicBinding = dynamicPreviewBindingV0524($row, fieldName);
        if (dynamicBinding.bound) { return dynamicBinding.value; }
        const $field = pageSectionControls($row, '[name$=\"[' + fieldName + ']\"]').first();
""",'canvas dynamic value')

css_block=r'''

/* v0.5.24 – Dynamic data context + bindings */
.h18-page-data-context{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:12px}.h18-dynamic-binding-box{border-left:3px solid #2271b1}.h18-dynamic-binding-row{margin-bottom:10px}.h18-dynamic-binding-row select{width:100%}.h18-dynamic-binding-row[style*="display: none"]{margin:0}@media(max-width:782px){.h18-page-data-context{grid-template-columns:1fr}}
'''
if '/* v0.5.24 – Dynamic data context + bindings */' in css: raise SystemExit('v0.5.24 CSS already present')
css=css.rstrip()+css_block+'\n'

# Readme.
readme=once(readme,'Version: 0.5.23','Version: 0.5.24','readme version')
anchor='== Version 0.5.23 – E5 Dynamic CMS foundation ==\n'
notes="""== Version 0.5.24 – E5 Dynamic binding ==

Nyt:
- UD-053: hver Hangar18-side kan vælge en current data context som datatype + konkret entry
- elementegenskaber kan bindes til current context: Title, Content, MediaId og begge knappers tekst/link
- bindinger er typevaliderede: media kan kun drive billeder, links kun text fields, mens text/number/bool/date kan drive sikre tekstegenskaber
- static elementværdier ændres ikke og bruges som fallback, hvis context eller felt ikke længere findes
- runtime validerer altid datatype, entry og field-type igen; admin-UI er ikke sikkerhedsgrænsen
- canvas-preview bruger samme current context og viser også dynamiske WordPress-medier
- Bindings serialiseres med Patterns, linked component definitions og Page Templates uden at introducere ny delt identitet
- page-editor schema løftes bagudkompatibelt til 1.19
- foundation er klar til UD-057 Repeater/Query list, der senere kan skifte current context pr. resultat

"""+anchor
readme=once(readme,anchor,notes,'readme v0.5.24 anchor')

php_path.write_text(php)
js_path.write_text(js)
css_path.write_text(css)
readme_path.write_text(readme)
print('v0.5.24 dynamic binding patch applied')
