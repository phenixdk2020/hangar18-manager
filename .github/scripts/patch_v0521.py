from pathlib import Path


def replace_once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 anchor, found {count}')
    return text.replace(old,new,1)

php_path=Path('hangar18-manager.php'); js_path=Path('assets/admin.js'); css_path=Path('assets/admin.css'); readme_path=Path('readme.txt')
php=php_path.read_text(); js=js_path.read_text(); css=css_path.read_text(); readme=readme_path.read_text()

php=replace_once(php,' * Version: 0.5.20',' * Version: 0.5.21','plugin header')
php=replace_once(php,"    const VERSION = '0.5.20';","    const VERSION = '0.5.21';",'plugin const')

# Component store is separate from legacy non-linked presets/patterns.
php=replace_once(php,
"""    const PAGE_VERSION_HISTORY_OPTION = 'hangar18_manager_page_versions_v1';
    const PAGE_PRESETS_OPTION         = 'hangar18_manager_page_presets_v1';
""",
"""    const PAGE_VERSION_HISTORY_OPTION = 'hangar18_manager_page_versions_v1';
    const PAGE_PRESETS_OPTION         = 'hangar18_manager_page_presets_v1';
    const PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1';
""",'component option constant')

php=replace_once(php,
"""        add_action('wp_ajax_h18_save_page_preset', [$this, 'ajax_save_page_preset']);
        add_action('wp_ajax_h18_delete_page_preset', [$this, 'ajax_delete_page_preset']);
""",
"""        add_action('wp_ajax_h18_save_page_preset', [$this, 'ajax_save_page_preset']);
        add_action('wp_ajax_h18_delete_page_preset', [$this, 'ajax_delete_page_preset']);
        add_action('wp_ajax_h18_save_page_component', [$this, 'ajax_save_page_component']);
        add_action('wp_ajax_h18_delete_page_component', [$this, 'ajax_delete_page_component']);
""",'component ajax actions')

php=replace_once(php,
"""            'ajaxUrl'           => admin_url('admin-ajax.php'),
            'pagePresetNonce'   => wp_create_nonce('h18_page_presets_v051'),
""",
"""            'ajaxUrl'              => admin_url('admin-ajax.php'),
            'pagePresetNonce'      => wp_create_nonce('h18_page_presets_v051'),
            'pageComponentNonce'   => wp_create_nonce('h18_page_components_v0521'),
""",'component nonce')

# Register linked component as a page element type.
php=replace_once(php,
"""            'grid'       => 'Grid container',
            'embed'      => 'Embed / medie-URL',
""",
"""            'grid'       => 'Grid container',
            'component'  => 'Linked component',
            'embed'      => 'Embed / medie-URL',
""",'component type label')

# Instance metadata is versioned with page sections.
php=replace_once(php,
"""            'Key'                   => 'sektion-' . wp_generate_uuid4(),
            'Type'                  => $type,
            'Active'                => true,
""",
"""            'Key'                   => 'sektion-' . wp_generate_uuid4(),
            'Type'                  => $type,
            'Active'                => true,
            'NavigatorLabel'        => '',
            'NavigatorLocked'       => false,
            'ComponentId'           => '',
            'ComponentRevision'     => 0,
            'ComponentOverrides'    => [],
""",'component section defaults')

# Parse navigator/component fields once near the section key.
php=replace_once(php,
"""        if ($key === '') {
            $key = 'sektion-' . substr(md5(wp_generate_uuid4()), 0, 12);
        }

        $alignment = (string) ($raw['DesktopAlignment'] ?? 'Left');
""",
"""        if ($key === '') {
            $key = 'sektion-' . substr(md5(wp_generate_uuid4()), 0, 12);
        }
        $navigator_label = sanitize_text_field((string) ($raw['NavigatorLabel'] ?? ''));
        $navigator_label = function_exists('mb_substr') ? mb_substr($navigator_label, 0, 80) : substr($navigator_label, 0, 80);
        $navigator_locked = array_key_exists('NavigatorLocked', $raw) ? $this->bool_value($raw['NavigatorLocked'], false) : false;
        $component_id = sanitize_key((string) ($raw['ComponentId'] ?? ''));
        $component_revision = max(0, (int) ($raw['ComponentRevision'] ?? 0));
        $component_overrides_raw = $raw['ComponentOverrides'] ?? [];
        if ((!is_array($component_overrides_raw) || !$component_overrides_raw) && isset($raw['ComponentOverridesJson']) && is_string($raw['ComponentOverridesJson'])) {
            $decoded_component_overrides = json_decode((string) $raw['ComponentOverridesJson'], true);
            if (is_array($decoded_component_overrides)) { $component_overrides_raw = $decoded_component_overrides; }
        }
        $component_overrides = [];
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
""",'component normalize prelude')

php=replace_once(php,
"""            'Key'                   => $key,
            'Type'                  => $type,
            'Active'                => array_key_exists('Active', $raw) ? $this->bool_value($raw['Active'], false) : true,
""",
"""            'Key'                   => $key,
            'Type'                  => $type,
            'Active'                => array_key_exists('Active', $raw) ? $this->bool_value($raw['Active'], false) : true,
            'NavigatorLabel'        => $navigator_label,
            'NavigatorLocked'       => $navigator_locked,
            'ComponentId'           => $component_id,
            'ComponentRevision'     => $component_revision,
            'ComponentOverrides'    => $component_overrides,
""",'component normalized section fields')

# Page schema 1.17 because component instance metadata is now persisted.
if php.count("'Version'        => '1.16'") != 3:
    raise SystemExit("Expected exactly 3 active page schema 1.16 payloads")
php=php.replace("'Version'        => '1.16'","'Version'        => '1.17'")
php=php.replace("'Version' => '1.16',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,","'Version' => '1.17',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php=php.replace("'Version' => '1.16',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,","'Version' => '1.17',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

# Linked component engine. Existing PAGE_PRESETS_OPTION remains an independent non-linked pattern store.
component_methods=r'''

    private function page_component_allowed_input_fields() {
        return ['Title', 'Content', 'MediaId', 'Button1Label', 'Button1Url', 'Button2Label', 'Button2Url'];
    }

    private function page_component_input_id($section_key, $field) {
        return 'input-' . substr(hash('sha256', sanitize_key((string) $section_key) . '|' . sanitize_key((string) $field)), 0, 16);
    }

    private function page_component_input_default(array $section, $field) {
        if ($field === 'MediaId') { return (string) absint($section['MediaId'] ?? 0); }
        return (string) ($section[$field] ?? '');
    }

    private function sanitize_page_component_override($field, $value) {
        if ($field === 'MediaId') { return absint($value); }
        if (in_array($field, ['Button1Url', 'Button2Url'], true)) { return esc_url_raw((string) $value); }
        if ($field === 'Content') { return wp_kses_post((string) $value); }
        return sanitize_text_field((string) $value);
    }

    private function normalize_page_component_definition(array $raw) {
        $raw_sections = isset($raw['Sections']) && is_array($raw['Sections']) ? array_slice($raw['Sections'], 0, 25) : [];
        if (!$raw_sections) { throw new RuntimeException('Komponenten skal indeholde mindst ét element.'); }
        foreach ($raw_sections as $raw_section) {
            if (!is_array($raw_section)) { continue; }
            $raw_type = sanitize_key((string) ($raw_section['Type'] ?? 'text'));
            if (in_array($raw_type, ['legacy', 'component'], true)) {
                throw new RuntimeException('Linked components kan ikke indeholde legacy-indhold eller andre linked components.');
            }
        }
        $normalized = $this->normalize_page_editor_data([
            'Version' => '1.17',
            'PageSlug' => self::HOME_SLUG,
            'PageTitle' => 'Linked component',
            'ContentVersion' => 0,
            'Sections' => $raw_sections,
        ], null);
        $sections = array_values((array) $normalized['Sections']);
        $roots = array_values(array_filter($sections, static function($section) {
            return sanitize_key((string) ($section['LayoutParentKey'] ?? '')) === '';
        }));
        if (count($roots) !== 1) {
            throw new RuntimeException('En linked component skal have præcis ét root-element.');
        }
        $section_by_key = [];
        foreach ($sections as &$section) {
            $section['ComponentId'] = '';
            $section['ComponentRevision'] = 0;
            $section['ComponentOverrides'] = [];
            $section_by_key[(string) $section['Key']] = $section;
        }
        unset($section);

        $inputs = [];
        $raw_inputs = isset($raw['Inputs']) && is_array($raw['Inputs']) ? array_slice($raw['Inputs'], 0, 40) : [];
        $allowed = $this->page_component_allowed_input_fields();
        foreach ($raw_inputs as $input) {
            if (!is_array($input)) { continue; }
            $section_key = sanitize_key((string) ($input['SectionKey'] ?? ''));
            $field = (string) ($input['Field'] ?? '');
            if ($section_key === '' || !isset($section_by_key[$section_key]) || !in_array($field, $allowed, true)) { continue; }
            $target = $section_by_key[$section_key];
            $target_type = (string) ($target['Type'] ?? 'text');
            if ($field === 'Content' && in_array($target_type, ['css','html','shortcode','embed'], true)) { continue; }
            if ($field === 'MediaId' && !in_array($target_type, ['hero','text_image','image'], true)) { continue; }
            if (in_array($field, ['Button1Label','Button1Url','Button2Label','Button2Url'], true) && !in_array($target_type, ['hero','buttons'], true)) { continue; }
            $input_id = $this->page_component_input_id($section_key, $field);
            $label = sanitize_text_field((string) ($input['Label'] ?? $field));
            if ($label === '') { $label = $field; }
            $inputs[$input_id] = [
                'InputId' => $input_id,
                'SectionKey' => $section_key,
                'Field' => $field,
                'Label' => $label,
            ];
        }
        return ['Sections' => $sections, 'Inputs' => array_values($inputs)];
    }

    private function get_page_components() {
        $stored = get_option(self::PAGE_COMPONENTS_OPTION, []);
        if (!is_array($stored)) { return []; }
        $components = [];
        foreach (array_slice($stored, 0, 50, true) as $id => $entry) {
            if (!is_array($entry)) { continue; }
            $component_id = sanitize_key((string) ($entry['Id'] ?? $id));
            $name = sanitize_text_field((string) ($entry['Name'] ?? 'Linked component'));
            if ($component_id === '' || $name === '') { continue; }
            try {
                $definition = $this->normalize_page_component_definition([
                    'Sections' => $entry['Sections'] ?? [],
                    'Inputs' => $entry['Inputs'] ?? [],
                ]);
            } catch (Throwable $e) {
                $this->log('WARN', 'PAGE_COMPONENT_INVALID', "{$component_id}: " . $e->getMessage());
                continue;
            }
            $components[$component_id] = [
                'Id' => $component_id,
                'Name' => $name,
                'Revision' => max(1, (int) ($entry['Revision'] ?? 1)),
                'UpdatedUtc' => sanitize_text_field((string) ($entry['UpdatedUtc'] ?? '')),
                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
            ];
        }
        return $components;
    }

    private function get_page_component_usage($component_id) {
        $component_id = sanitize_key((string) $component_id);
        if ($component_id === '') { return []; }
        $usage = [];
        $store = $this->get_page_editor_store();
        $definitions = $this->editable_page_definitions();
        foreach ($store as $slug => $page_data) {
            if (!is_array($page_data) || empty($page_data['Sections']) || !is_array($page_data['Sections'])) { continue; }
            foreach ($page_data['Sections'] as $section) {
                if (!is_array($section) || sanitize_key((string) ($section['Type'] ?? '')) !== 'component') { continue; }
                if (sanitize_key((string) ($section['ComponentId'] ?? '')) !== $component_id) { continue; }
                $usage[] = [
                    'PageSlug' => sanitize_title((string) $slug),
                    'PageTitle' => sanitize_text_field((string) ($page_data['PageTitle'] ?? ($definitions[$slug] ?? $slug))),
                    'SectionKey' => sanitize_key((string) ($section['Key'] ?? '')),
                ];
            }
        }
        return $usage;
    }

    private function get_page_components_for_editor() {
        $components = $this->get_page_components();
        foreach ($components as $id => &$component) {
            $component['Usage'] = $this->get_page_component_usage($id);
            $component['UsageCount'] = count($component['Usage']);
        }
        unset($component);
        return $components;
    }

    public function ajax_save_page_component() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at gemme linked components.'], 403);
        }
        check_ajax_referer('h18_page_components_v0521', 'nonce');
        $name = sanitize_text_field((string) wp_unslash($_POST['name'] ?? ''));
        $name = function_exists('mb_substr') ? mb_substr($name, 0, 80) : substr($name, 0, 80);
        $sections_json = (string) wp_unslash($_POST['sections'] ?? '');
        $inputs_json = (string) wp_unslash($_POST['inputs'] ?? '[]');
        if ($name === '') { wp_send_json_error(['message' => 'Komponenten skal have et navn.'], 400); }
        if ($sections_json === '' || strlen($sections_json) > 350000 || strlen($inputs_json) > 100000) {
            wp_send_json_error(['message' => 'Komponentdata mangler eller er for stor.'], 400);
        }
        $sections = json_decode($sections_json, true);
        $inputs = json_decode($inputs_json, true);
        if (!is_array($sections) || !is_array($inputs) || json_last_error() !== JSON_ERROR_NONE) {
            wp_send_json_error(['message' => 'Komponentdata er ikke gyldig JSON.'], 400);
        }
        try {
            $definition = $this->normalize_page_component_definition(['Sections' => $sections, 'Inputs' => $inputs]);
            $components = $this->get_page_components();
            $component_id = sanitize_key((string) wp_unslash($_POST['component_id'] ?? ''));
            $existing = ($component_id !== '' && isset($components[$component_id])) ? $components[$component_id] : null;
            if (!$existing) { $component_id = 'component-' . sanitize_key(wp_generate_uuid4()); }
            $revision = $existing ? ((int) $existing['Revision'] + 1) : 1;
            $entry = [
                'Id' => $component_id,
                'Name' => $name,
                'Revision' => $revision,
                'UpdatedUtc' => gmdate('c'),
                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
            ];
            $components[$component_id] = $entry;
            if (count($components) > 50) { throw new RuntimeException('Der kan højst gemmes 50 linked components.'); }
            update_option(self::PAGE_COMPONENTS_OPTION, $components, false);
            $entry['Usage'] = $this->get_page_component_usage($component_id);
            $entry['UsageCount'] = count($entry['Usage']);
            $this->log('INFO', 'PAGE_COMPONENT_SAVED', "Linked component '{$name}' {$component_id} revision {$revision} gemt atomisk.");
            wp_send_json_success(['component' => $entry]);
        } catch (Throwable $e) {
            wp_send_json_error(['message' => $e->getMessage()], 400);
        }
    }

    public function ajax_delete_page_component() {
        if (!current_user_can('edit_pages')) {
            wp_send_json_error(['message' => 'Du har ikke rettigheder til at slette linked components.'], 403);
        }
        check_ajax_referer('h18_page_components_v0521', 'nonce');
        $component_id = sanitize_key((string) wp_unslash($_POST['component_id'] ?? ''));
        $components = $this->get_page_components();
        if ($component_id === '' || !isset($components[$component_id])) {
            wp_send_json_error(['message' => 'Komponenten blev ikke fundet.'], 404);
        }
        $usage = $this->get_page_component_usage($component_id);
        if ($usage) {
            wp_send_json_error(['message' => 'Komponenten bruges stadig på ' . count($usage) . ' side(r) og kan ikke slettes.', 'usage' => $usage], 409);
        }
        $name = (string) $components[$component_id]['Name'];
        unset($components[$component_id]);
        update_option(self::PAGE_COMPONENTS_OPTION, $components, false);
        $this->log('INFO', 'PAGE_COMPONENT_DELETED', "Linked component '{$name}' ({$component_id}) blev slettet.");
        wp_send_json_success(['component_id' => $component_id]);
    }

    private function resolve_page_component_instance_sections($page_id, array $instance) {
        $component_id = sanitize_key((string) ($instance['ComponentId'] ?? ''));
        if ($component_id === '') { return [[], null]; }
        $components = $this->get_page_components();
        if (!isset($components[$component_id])) { return [[], null]; }
        $component = $components[$component_id];
        $sections = $component['Sections'];
        $overrides = isset($instance['ComponentOverrides']) && is_array($instance['ComponentOverrides']) ? $instance['ComponentOverrides'] : [];
        $section_index = [];
        foreach ($sections as $index => $section) { $section_index[(string) $section['Key']] = $index; }
        foreach ($component['Inputs'] as $input) {
            $input_id = sanitize_key((string) ($input['InputId'] ?? ''));
            $section_key = sanitize_key((string) ($input['SectionKey'] ?? ''));
            $field = (string) ($input['Field'] ?? '');
            if ($input_id === '' || !array_key_exists($input_id, $overrides) || !isset($section_index[$section_key])) { continue; }
            $value = $this->sanitize_page_component_override($field, $overrides[$input_id]);
            $target = &$sections[$section_index[$section_key]];
            $target[$field] = $value;
            if ($field === 'MediaId' && absint($value) > 0) { $target['MediaUrl'] = ''; }
            unset($target);
        }
        $prefix = 'cmp-' . substr(hash('sha256', (int) $page_id . '|' . sanitize_key((string) ($instance['Key'] ?? '')) . '|' . $component_id), 0, 12) . '-';
        $key_map = [];
        foreach ($sections as $section) { $key_map[(string) $section['Key']] = sanitize_key($prefix . (string) $section['Key']); }
        foreach ($sections as &$section) {
            $old_key = (string) $section['Key'];
            $old_parent = sanitize_key((string) ($section['LayoutParentKey'] ?? ''));
            $section['Key'] = $key_map[$old_key];
            $section['LayoutParentKey'] = $old_parent !== '' && isset($key_map[$old_parent]) ? $key_map[$old_parent] : '';
            $section['ComponentId'] = '';
            $section['ComponentRevision'] = 0;
            $section['ComponentOverrides'] = [];
        }
        unset($section);
        return [$sections, $component];
    }
'''
php=replace_once(php,
"""    private function page_module_storage_key($page_id, $section_key) {
""",
component_methods+"\n    private function page_module_storage_key($page_id, $section_key) {\n",'component methods anchor')

# Frontend resolves linked instances against the current global definition at render time.
php=replace_once(php,
"""        if (empty($section['Active'])) {
            return '';
        }
        if ($section['Type'] === 'legacy') {
""",
"""        if (empty($section['Active'])) {
            return '';
        }
        if ($section['Type'] === 'component') {
            [$component_sections, $component] = $this->resolve_page_component_instance_sections($page_id, $section);
            if (!$component || !$component_sections) { return ''; }
            $classes = trim('h18-editor-component ' . $this->page_editor_visibility_classes($section));
            $id = 'h18-section-' . sanitize_html_class((string) $section['Key']);
            return '<div id="' . esc_attr($id) . '" class="' . esc_attr($classes) . '" data-h18-component="' . esc_attr($component['Id']) . '" data-h18-component-revision="' . esc_attr($component['Revision']) . '">' . $this->render_page_editor_layout_tree($page_id, $component_sections) . '</div>';
        }
        if ($section['Type'] === 'legacy') {
""",'component frontend renderer')

# Admin rows persist Navigator state + component instance payload.
php=replace_once(php,
"""        $prefix = 'sections[' . $index . ']';
        $type_labels = $this->page_section_type_labels();
        $export_poll = '';
""",
"""        $prefix = 'sections[' . $index . ']';
        $type_labels = $this->page_section_type_labels();
        $component_options = $this->get_page_components();
        $export_poll = '';
""",'component admin options')

php=replace_once(php,
"""            <input class="h18-page-section-imported-group" type="hidden" name="<?php echo esc_attr($prefix); ?>[ImportedGroupType]" value="<?php echo esc_attr($section['ImportedGroupType']); ?>" />

            <header class="h18-page-section-header">
""",
"""            <input class="h18-page-section-imported-group" type="hidden" name="<?php echo esc_attr($prefix); ?>[ImportedGroupType]" value="<?php echo esc_attr($section['ImportedGroupType']); ?>" />
            <input class="h18-section-navigator-label" type="hidden" name="<?php echo esc_attr($prefix); ?>[NavigatorLabel]" value="<?php echo esc_attr($section['NavigatorLabel']); ?>" />
            <input class="h18-section-navigator-locked" type="hidden" name="<?php echo esc_attr($prefix); ?>[NavigatorLocked]" value="<?php echo !empty($section['NavigatorLocked']) ? '1' : '0'; ?>" />

            <header class="h18-page-section-header">
""",'navigator admin hidden fields')

# Component instance editor immediately after main grid.
main_grid_tail="""                        <input class="h18-advanced-content-authorized" type="hidden" name="<?php echo esc_attr($prefix); ?>[AdvancedContentAuthorized]" value="<?php echo !empty($section['AdvancedContentAuthorized']) ? '1' : '0'; ?>" />
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="hero text_image image">
"""
component_admin="""                        <input class="h18-advanced-content-authorized" type="hidden" name="<?php echo esc_attr($prefix); ?>[AdvancedContentAuthorized]" value="<?php echo !empty($section['AdvancedContentAuthorized']) ? '1' : '0'; ?>" />
                    </div>

                    <div class="h18-section-type-field h18-section-module-box h18-component-instance-editor" data-types="component">
                        <h4>Linked component</h4>
                        <p class="description">Definitionen er global. Kun eksplicit frigivne inputs kan overskrives lokalt; layout og design forbliver linked.</p>
                        <div class="h18-field">
                            <label><strong>Komponent</strong></label>
                            <select class="h18-component-select" name="<?php echo esc_attr($prefix); ?>[ComponentId]">
                                <option value="">Vælg linked component</option>
                                <?php foreach ($component_options as $component_option) : ?>
                                    <option value="<?php echo esc_attr($component_option['Id']); ?>" <?php selected($section['ComponentId'], $component_option['Id']); ?>><?php echo esc_html($component_option['Name'] . ' · r' . $component_option['Revision']); ?></option>
                                <?php endforeach; ?>
                            </select>
                            <input class="h18-component-revision" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentRevision]" value="<?php echo esc_attr($section['ComponentRevision']); ?>" />
                            <input class="h18-component-overrides-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentOverridesJson]" value="<?php echo esc_attr(wp_json_encode($section['ComponentOverrides'])); ?>" />
                        </div>
                        <div class="h18-component-instance-status"></div>
                        <div class="h18-component-overrides-editor"></div>
                    </div>

                    <div class="h18-section-type-field h18-section-module-box" data-types="hero text_image image">
"""
php=replace_once(php,main_grid_tail,component_admin,'component admin editor')

# render_pages provides linked definitions and usage to JS.
php=replace_once(php,
"""        $versions = $page instanceof WP_Post ? $this->get_page_version_history($slug) : [];
        $page_presets = $this->get_page_presets();
""",
"""        $versions = $page instanceof WP_Post ? $this->get_page_version_history($slug) : [];
        $page_presets = $this->get_page_presets();
        $page_components = $this->get_page_components_for_editor();
""",'render pages components data')

# Re-label old presets and add linked library.
php=replace_once(php,
"""                                <div class="h18-user-components-heading"><h4>Egne komponenter</h4><span>Gemmes i WordPress</span></div>
                                <div id="h18-user-presets-list" class="h18-user-presets-list"><p class="description">Vælg en sektion og brug “Gem som komponent” i Inspector.</p></div>
""",
"""                                <div class="h18-user-components-heading"><h4>Linked components</h4><span>Global definition</span></div>
                                <div id="h18-linked-components-list" class="h18-user-presets-list"><p class="description">Vælg et subtree og brug “Gem som linked component” i Inspector.</p></div>
                                <div class="h18-user-components-heading"><h4>Patterns</h4><span>Ikke-linked kopier</span></div>
                                <div id="h18-user-presets-list" class="h18-user-presets-list"><p class="description">Vælg en sektion og brug “Gem som pattern” i Inspector.</p></div>
""",'linked component library UI')

# Inspector actions: old preset becomes Pattern, new linked action gets its own button.
php=replace_once(php,
"""                                    <button type="button" class="button button-primary" id="h18-save-section-preset" disabled>Gem som komponent</button>
                                </div>
                                <p class="description">Genbrugelige komponenter gemmes centralt i WordPress og kan indsættes på alle sider i Hangar18-editoren.</p>
""",
"""                                    <button type="button" class="button" id="h18-save-section-preset" disabled>Gem som pattern</button>
                                    <button type="button" class="button button-primary" id="h18-save-linked-component" disabled>Gem subtree som linked component</button>
                                </div>
                                <p class="description">Patterns indsættes som frie kopier. Linked components deler én global definition og kan kun overskrives gennem frigivne inputs.</p>
""",'inspector component actions')

# Embed both libraries in the editor document.
php=replace_once(php,
"""                <script id="h18-page-presets-data" type="application/json"><?php echo wp_json_encode(array_values($page_presets), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id="h18-page-section-template">
""",
"""                <script id="h18-page-presets-data" type="application/json"><?php echo wp_json_encode(array_values($page_presets), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id="h18-page-components-data" type="application/json"><?php echo wp_json_encode(array_values($page_components), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <template id="h18-page-section-template">
""",'component data script')

# If actual template is same-line anchor, fix later in QA if needed.

# Save path checkbox + JSON semantics.
php=replace_once(php,
"""            $raw['MobileLayoutStack'] = !empty($raw['MobileLayoutStack']);
            $key = sanitize_key((string) ($raw['Key'] ?? ''));
""",
"""            $raw['MobileLayoutStack'] = !empty($raw['MobileLayoutStack']);
            $raw['NavigatorLocked'] = !empty($raw['NavigatorLocked']);
            $key = sanitize_key((string) ($raw['Key'] ?? ''));
""",'navigator lock save semantics')

# JS state for linked components.
js=replace_once(js,
"""    const $pageUserPresetsList = $('#h18-user-presets-list');
    let pageSectionNextIndex = 0;
""",
"""    const $pageUserPresetsList = $('#h18-user-presets-list');
    const $pageLinkedComponentsList = $('#h18-linked-components-list');
    let pageSectionNextIndex = 0;
""",'linked component list ref')
js=replace_once(js,
"""    const pageUserPresets = {};
    let currentCanvasDevice = 'desktop';
""",
"""    const pageUserPresets = {};
    const pageLinkedComponents = {};
    let navigatorLockedOrderSnapshotV0521 = null;
    let currentCanvasDevice = 'desktop';
""",'linked component state')

# Parse linked component JSON after legacy presets.
parse_anchor="""    } catch (presetError) {
        window.console && console.warn('Hangar18: kunne ikke læse komponentbibliotek.', presetError);
    }

    const builtInSectionPresets = {
"""
parse_new="""    } catch (presetError) {
        window.console && console.warn('Hangar18: kunne ikke læse pattern-bibliotek.', presetError);
    }
    try {
        const componentNode = document.getElementById('h18-page-components-data');
        const parsedComponents = componentNode ? JSON.parse(componentNode.textContent || '[]') : [];
        (Array.isArray(parsedComponents) ? parsedComponents : []).forEach(function (component) {
            if (component && component.Id) { pageLinkedComponents[String(component.Id)] = component; }
        });
    } catch (componentError) {
        window.console && console.warn('Hangar18: kunne ikke læse linked component-bibliotek.', componentError);
    }

    const builtInSectionPresets = {
"""
js=replace_once(js,parse_anchor,parse_new,'component JSON parse')

# Type label.
js=replace_once(js,
"""            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', container: 'Container', flex: 'Flex container', grid: 'Grid container', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',
""",
"""            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', container: 'Container', flex: 'Flex container', grid: 'Grid container', component: 'Linked component', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',
""",'component JS type label')

# Navigator tree: custom label, rename/hide/lock in realtime and locked reorder barrier.
nav_old="""            const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
            const active = $row.find('.h18-section-active').is(':checked');
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
            const sectionKeyV0515 = String($row.find('.h18-page-section-key').val() || '');
            const multiSelectedV0515 = sectionKeyV0515 && multiSelectedSectionKeys.has(sectionKeyV0515);
            const $item = $('<div>', { class: 'h18-navigator-item' + (selected ? ' is-selected' : '') + (multiSelectedV0515 ? ' is-multi-selected' : ''), 'data-section-index': index });
            $item.append($('<span>', { class: 'dashicons dashicons-menu h18-navigator-drag', title: 'Flyt lag' }));
            const $button = $('<button>', { type: 'button', class: 'h18-navigator-select' });
            $button.append($('<strong>', { text: inspectorTypeLabel(type) }));
            $button.append($('<small>', { text: title || 'Uden overskrift' }));
            $item.append($button);
            $item.append($('<span>', { class: 'h18-navigator-visibility ' + (active ? 'is-visible' : 'is-hidden'), title: active ? 'Synlig' : 'Skjult' }).append($('<span>', { class: 'dashicons ' + (active ? 'dashicons-visibility' : 'dashicons-hidden') })));
"""
nav_new="""            const title = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
            const navigatorLabel = String(pageSectionControls($row, '.h18-section-navigator-label').val() || '').trim();
            const active = $row.find('.h18-section-active').is(':checked');
            const locked = String(pageSectionControls($row, '.h18-section-navigator-locked').val() || '0') === '1';
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
            const sectionKeyV0515 = String($row.find('.h18-page-section-key').val() || '');
            const multiSelectedV0515 = sectionKeyV0515 && multiSelectedSectionKeys.has(sectionKeyV0515);
            const $item = $('<div>', { class: 'h18-navigator-item' + (selected ? ' is-selected' : '') + (multiSelectedV0515 ? ' is-multi-selected' : '') + (locked ? ' is-locked' : ''), 'data-section-index': index, 'data-section-key': sectionKeyV0515 });
            $item.append($('<span>', { class: 'dashicons ' + (locked ? 'dashicons-lock' : 'dashicons-menu') + ' h18-navigator-drag', title: locked ? 'Låst lag' : 'Flyt lag' }));
            const $button = $('<button>', { type: 'button', class: 'h18-navigator-select' });
            $button.append($('<strong>', { text: navigatorLabel || inspectorTypeLabel(type) }));
            $button.append($('<small>', { text: title || inspectorTypeLabel(type) }));
            $item.append($button);
            $item.append($('<button>', { type: 'button', class: 'h18-navigator-tool h18-navigator-rename', title: 'Omdøb lag', 'aria-label': 'Omdøb lag' }).append($('<span>', { class: 'dashicons dashicons-edit' })));
            $item.append($('<button>', { type: 'button', class: 'h18-navigator-tool h18-navigator-toggle-lock', title: locked ? 'Lås op' : 'Lås', 'aria-label': locked ? 'Lås op' : 'Lås' }).append($('<span>', { class: 'dashicons ' + (locked ? 'dashicons-lock' : 'dashicons-unlock') })));
            $item.append($('<button>', { type: 'button', class: 'h18-navigator-tool h18-navigator-toggle-visibility ' + (active ? 'is-visible' : 'is-hidden'), title: active ? 'Skjul' : 'Vis', 'aria-label': active ? 'Skjul' : 'Vis' }).append($('<span>', { class: 'dashicons ' + (active ? 'dashicons-visibility' : 'dashicons-hidden') })));
"""
js=replace_once(js,nav_old,nav_new,'navigator tools')

sort_old="""            $pageNavigatorList.sortable({
                items: '> .h18-navigator-item', handle: '.h18-navigator-drag', axis: 'y', tolerance: 'pointer',
                update: function () {
"""
sort_new="""            $pageNavigatorList.sortable({
                items: '> .h18-navigator-item', handle: '.h18-navigator-drag', axis: 'y', tolerance: 'pointer',
                start: function (event, ui) {
                    if (ui.item.hasClass('is-locked')) { $(this).sortable('cancel'); return false; }
                    navigatorLockedOrderSnapshotV0521 = {};
                    $pageNavigatorList.children('.h18-navigator-item.is-locked').each(function (lockedIndex) { navigatorLockedOrderSnapshotV0521[String($(this).attr('data-section-key') || '')] = $(this).index(); });
                },
                update: function () {
                    let lockedMoved = false;
                    if (navigatorLockedOrderSnapshotV0521) {
                        $pageNavigatorList.children('.h18-navigator-item.is-locked').each(function () {
                            const key = String($(this).attr('data-section-key') || '');
                            if (Object.prototype.hasOwnProperty.call(navigatorLockedOrderSnapshotV0521, key) && navigatorLockedOrderSnapshotV0521[key] !== $(this).index()) { lockedMoved = true; }
                        });
                    }
                    if (lockedMoved) { $(this).sortable('cancel'); navigatorLockedOrderSnapshotV0521 = null; return; }
                    navigatorLockedOrderSnapshotV0521 = null;
"""
js=replace_once(js,sort_old,sort_new,'navigator locked sort')

# Navigator action handlers before renderUserPresets.
nav_actions=r'''

    function navigatorRowV0521($item) {
        const index = String($item.attr('data-section-index') || '');
        return $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
    }

    function rowLockedV0521($row) {
        return String(pageSectionControls($row, '.h18-section-navigator-locked').val() || '0') === '1';
    }

    $(document).on('click', '.h18-navigator-rename', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = navigatorRowV0521($(this).closest('.h18-navigator-item'));
        if (!$row.length) { return; }
        const current = String(pageSectionControls($row, '.h18-section-navigator-label').val() || '');
        const value = window.prompt('Navn i Navigator (tomt = brug elementtype):', current);
        if (value === null) { return; }
        pageSectionControls($row, '.h18-section-navigator-label').val(String(value).trim().slice(0,80)).trigger('change');
        rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });

    $(document).on('click', '.h18-navigator-toggle-lock', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = navigatorRowV0521($(this).closest('.h18-navigator-item'));
        if (!$row.length) { return; }
        const $field = pageSectionControls($row, '.h18-section-navigator-locked').first();
        $field.val(String($field.val() || '0') === '1' ? '0' : '1').trigger('change');
        rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });

    $(document).on('click', '.h18-navigator-toggle-visibility', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = navigatorRowV0521($(this).closest('.h18-navigator-item'));
        if (!$row.length || rowLockedV0521($row)) { return; }
        const $active = pageSectionControls($row, '.h18-section-active').first();
        $active.prop('checked', !$active.is(':checked')).trigger('change');
        renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });
'''
js=replace_once(js,"\n    function renderUserPresets() {",nav_actions+"\n    function renderUserPresets() {",'navigator action insertion')

# Old user presets are Patterns; reject linked instance capture.
js=replace_once(js,
"""        const data = { Type: String($row.attr('data-section-type') || 'text') };
""",
"""        const data = { Type: String($row.attr('data-section-type') || 'text') };
        if (data.Type === 'component') { return null; }
""",'pattern component rejection')
js=replace_once(js,
"""            if (['Key', 'Order', 'Remove', 'ResetVotes', 'LayoutParentKey'].includes(fieldName)) {
""",
"""            if (['Key', 'Order', 'Remove', 'ResetVotes', 'LayoutParentKey', 'NavigatorLabel', 'NavigatorLocked', 'ComponentId', 'ComponentRevision', 'ComponentOverridesJson'].includes(fieldName)) {
""",'pattern metadata exclusion')

# Linked component library / subtree serialization / overrides editor.
linked_js=r'''

    function componentDefinitionSectionV0521(component, sectionKey) {
        if (!component || !Array.isArray(component.Sections)) { return null; }
        return component.Sections.find(function (section) { return String(section.Key || '') === String(sectionKey || ''); }) || null;
    }

    function componentInputDefaultV0521(component, input) {
        const section = componentDefinitionSectionV0521(component, input && input.SectionKey);
        if (!section) { return ''; }
        const field = String(input.Field || '');
        return section[field] == null ? '' : section[field];
    }

    function parseComponentOverridesV0521($row) {
        try {
            const raw = String(pageSectionControls($row, '.h18-component-overrides-json').val() || '{}');
            const parsed = JSON.parse(raw);
            return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
        } catch (error) { return {}; }
    }

    function writeComponentOverridesV0521($row, overrides) {
        pageSectionControls($row, '.h18-component-overrides-json').val(JSON.stringify(overrides || {})).trigger('change');
    }

    function renderComponentInstanceEditorV0521($row) {
        if (!$row || !$row.length || String($row.attr('data-section-type') || '') !== 'component') { return; }
        const componentId = String(pageSectionControls($row, '.h18-component-select').val() || '');
        const component = pageLinkedComponents[componentId];
        const $status = pageSectionControls($row, '.h18-component-instance-status').first();
        const $editor = pageSectionControls($row, '.h18-component-overrides-editor').first();
        $editor.empty();
        if (!component) {
            $status.html('<p class="description">Vælg en linked component. Hvis definitionen er slettet, renderes instansen ikke på frontend.</p>');
            return;
        }
        pageSectionControls($row, '.h18-component-revision').val(parseInt(component.Revision,10)||1);
        const usage = parseInt(component.UsageCount,10)||0;
        $status.empty().append($('<p>', { class: 'h18-component-status-line' }).append($('<strong>', { text: String(component.Name || 'Linked component') }), $('<span>', { text: 'Revision ' + String(component.Revision || 1) + ' · bruges ' + usage + ' sted(er)' })));
        const overrides = parseComponentOverridesV0521($row);
        const inputs = Array.isArray(component.Inputs) ? component.Inputs : [];
        if (!inputs.length) {
            $editor.append($('<p>', { class: 'description', text: 'Denne komponent har ingen frigivne lokale inputs. Layout og indhold følger den globale definition.' }));
            return;
        }
        inputs.forEach(function (input) {
            const inputId = String(input.InputId || '');
            const field = String(input.Field || '');
            const defaultValue = componentInputDefaultV0521(component, input);
            const effective = Object.prototype.hasOwnProperty.call(overrides, inputId) ? overrides[inputId] : defaultValue;
            const $field = $('<label>', { class: 'h18-component-override-field' }).append($('<span>', { text: String(input.Label || field) }));
            let $control;
            if (field === 'Content') {
                $control = $('<textarea>', { rows: 4, class: 'h18-component-override-control', 'data-input-id': inputId, 'data-default-value': String(defaultValue == null ? '' : defaultValue), 'data-input-field': field }).val(String(effective == null ? '' : effective));
            } else if (field === 'MediaId') {
                $control = $('<div>', { class: 'h18-component-media-override' });
                const $value = $('<input>', { type: 'hidden', class: 'h18-component-override-control', 'data-input-id': inputId, 'data-default-value': String(defaultValue || 0), 'data-input-field': field }).val(String(effective || 0));
                const $label = $('<span>', { class: 'h18-component-media-id', text: effective ? 'Medie-ID ' + String(effective) : 'Bruger komponentens standardbillede' });
                const $pick = $('<button>', { type: 'button', class: 'button h18-component-override-media', text: 'Vælg billede' });
                const $reset = $('<button>', { type: 'button', class: 'button-link h18-component-override-reset', text: 'Brug global standard' });
                $control.append($value, $label, $pick, $reset);
            } else {
                $control = $('<input>', { type: field.indexOf('Url') !== -1 ? 'url' : 'text', class: 'h18-component-override-control', 'data-input-id': inputId, 'data-default-value': String(defaultValue == null ? '' : defaultValue), 'data-input-field': field }).val(String(effective == null ? '' : effective));
                $field.append($('<button>', { type: 'button', class: 'button-link h18-component-override-reset', text: 'Brug global standard' }));
            }
            $field.prepend($control);
            $editor.append($field);
        });
    }

    function syncComponentOverrideControlV0521($control) {
        const $row = pageSectionForElement($control);
        if (!$row.length) { return; }
        const inputId = String($control.attr('data-input-id') || '');
        const defaultValue = String($control.attr('data-default-value') || '');
        let value = String($control.val() == null ? '' : $control.val());
        const overrides = parseComponentOverridesV0521($row);
        if (value === defaultValue) { delete overrides[inputId]; }
        else { overrides[inputId] = value; }
        writeComponentOverridesV0521($row, overrides);
        renderCanvasPreview($row); scheduleEditorHistoryCapture(250);
    }

    $(document).on('input change', '.h18-component-override-control', function () { syncComponentOverrideControlV0521($(this)); });
    $(document).on('click', '.h18-component-override-reset', function (event) {
        event.preventDefault();
        const $field = $(this).closest('.h18-component-override-field');
        const $control = $field.find('.h18-component-override-control').first();
        $control.val(String($control.attr('data-default-value') || '')).trigger('change');
        const field = String($control.attr('data-input-field') || '');
        if (field === 'MediaId') { $field.find('.h18-component-media-id').text('Bruger komponentens standardbillede'); }
    });
    $(document).on('click', '.h18-component-override-media', function (event) {
        event.preventDefault();
        const $field = $(this).closest('.h18-component-override-field');
        const $control = $field.find('.h18-component-override-control').first();
        const frame = wp.media({ title: 'Vælg komponentbillede', button: { text: 'Brug billede' }, multiple: false, library: { type: 'image' } });
        frame.on('select', function () {
            const media = frame.state().get('selection').first().toJSON();
            $control.val(String(media.id || 0)).trigger('change');
            $field.find('.h18-component-media-id').text(media.id ? 'Medie-ID ' + media.id : 'Bruger komponentens standardbillede');
        });
        frame.open();
    });
    $(document).on('change', '.h18-component-select', function () {
        const $row = pageSectionForElement(this);
        writeComponentOverridesV0521($row, {});
        renderComponentInstanceEditorV0521($row); renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
    });

    function componentSubtreeRowsV0521($root) {
        if (!$root || !$root.length) { return []; }
        const rootKey = String($root.find('.h18-page-section-key').val() || '');
        if (!rootKey) { return []; }
        const ordered = [];
        const wanted = new Set([rootKey]);
        let changed = true;
        while (changed && wanted.size < 25) {
            changed = false;
            $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
                const $row = $(this);
                const key = String($row.find('.h18-page-section-key').val() || '');
                const parent = String(pageSectionControls($row, '.h18-layout-parent-key').val() || '');
                if (key && parent && wanted.has(parent) && !wanted.has(key)) { wanted.add(key); changed = true; }
            });
        }
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const key = String($(this).find('.h18-page-section-key').val() || '');
            if (wanted.has(key)) { ordered.push($(this)); }
        });
        return ordered;
    }

    function componentSubtreeDataV0521($root) {
        const rows = componentSubtreeRowsV0521($root);
        if (!rows.length) { return []; }
        const rootKey = String($root.find('.h18-page-section-key').val() || '');
        const keys = new Set(rows.map(function ($row) { return String($row.find('.h18-page-section-key').val() || ''); }));
        return rows.map(function ($row, index) {
            const data = sectionPresetData($row);
            if (!data) { return null; }
            const key = String($row.find('.h18-page-section-key').val() || '');
            const parent = String(pageSectionControls($row, '.h18-layout-parent-key').val() || '');
            data.Key = key;
            data.Order = (index + 1) * 10;
            data.LayoutParentKey = key === rootKey ? '' : (keys.has(parent) ? parent : '');
            delete data.NavigatorLabel; delete data.NavigatorLocked; delete data.ComponentId; delete data.ComponentRevision; delete data.ComponentOverridesJson;
            return data;
        }).filter(Boolean);
    }

    function componentCandidateInputsV0521(sections) {
        const inputs = [];
        (sections || []).forEach(function (section) {
            const key = String(section.Key || '');
            const type = String(section.Type || 'text');
            const sectionName = String(section.Title || inspectorTypeLabel(type));
            function add(field, label) { inputs.push({ SectionKey: key, Field: field, Label: sectionName + ' · ' + label }); }
            if (!['css','html','shortcode','embed','legacy','component','spacer','divider'].includes(type)) {
                add('Title','Overskrift');
            }
            if (!['css','html','shortcode','embed','legacy','component','spacer','divider','image','badge','icon'].includes(type)) {
                add('Content','Tekst');
            }
            if (['hero','text_image','image'].includes(type)) { add('MediaId','Billede'); }
            if (['hero','buttons'].includes(type)) {
                add('Button1Label','Knap 1 tekst'); add('Button1Url','Knap 1 link'); add('Button2Label','Knap 2 tekst'); add('Button2Url','Knap 2 link');
            }
        });
        return inputs.slice(0,40);
    }

    function openSaveLinkedComponentDialogV0521(componentId) {
        if (!$inspectedSection.length) { return; }
        if (rowLockedV0521($inspectedSection)) { window.alert('Laget er låst. Lås det op før det gemmes som en linked component.'); return; }
        const type = String($inspectedSection.attr('data-section-type') || '');
        if (['legacy','component'].includes(type)) { window.alert('Vælg et almindeligt element eller layout-subtree.'); return; }
        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length) { return; }
        const existing = componentId ? pageLinkedComponents[String(componentId)] : null;
        const candidates = componentCandidateInputsV0521(sections);
        const selectedIds = new Set((existing && Array.isArray(existing.Inputs) ? existing.Inputs : []).map(function (input) { return String(input.SectionKey) + '|' + String(input.Field); }));
        const $overlay = $('<div>', { class: 'h18-component-dialog-overlay' });
        const $dialog = $('<div>', { class: 'h18-component-dialog', role: 'dialog', 'aria-modal': 'true', 'aria-label': existing ? 'Opdater linked component' : 'Gem linked component' });
        $dialog.append($('<h3>', { text: existing ? 'Opdater linked component' : 'Gem subtree som linked component' }));
        const $name = $('<input>', { type: 'text', class: 'regular-text h18-component-dialog-name', maxlength: 80, placeholder: 'Komponentnavn' }).val(existing ? String(existing.Name || '') : String(pageSectionControls($inspectedSection,'.h18-section-navigator-label').val() || setSectionTitleSummary($inspectedSection) || inspectorTypeLabel(type)));
        $dialog.append($('<label>').append($('<strong>', { text: 'Navn' }), $name));
        $dialog.append($('<p>', { class: 'description', text: 'Vælg hvilke indholdsfelter instanser må overskrive lokalt. Layout/design er altid låst til den globale definition.' }));
        const $choices = $('<div>', { class: 'h18-component-input-choices' });
        candidates.forEach(function (candidate) {
            const token = String(candidate.SectionKey) + '|' + String(candidate.Field);
            const checked = existing ? selectedIds.has(token) : ['Title','Content','MediaId','Button1Label','Button1Url'].includes(String(candidate.Field));
            const $check = $('<input>', { type: 'checkbox', value: token }).prop('checked', checked).data('input', candidate);
            $choices.append($('<label>', { class: 'h18-component-input-choice' }).append($check, $('<span>', { text: String(candidate.Label) })));
        });
        if (!candidates.length) { $choices.append($('<p>', { class: 'description', text: 'Subtreeet har ingen sikre felter, der kan frigives. Det kan stadig gemmes med helt låst indhold.' })); }
        $dialog.append($choices);
        const $actions = $('<div>', { class: 'h18-component-dialog-actions' });
        const $cancel = $('<button>', { type: 'button', class: 'button', text: 'Annuller' });
        const $save = $('<button>', { type: 'button', class: 'button button-primary', text: existing ? 'Opdater global definition' : 'Gem linked component' });
        $actions.append($cancel,$save); $dialog.append($actions); $overlay.append($dialog); $('body').append($overlay); $name.trigger('focus');
        function close(){ $overlay.remove(); }
        $cancel.on('click',close); $overlay.on('click',function(e){ if(e.target === $overlay.get(0)) close(); });
        $save.on('click',function(){
            const name = String($name.val() || '').trim(); if(!name){ $name.trigger('focus'); return; }
            const inputs=[]; $choices.find('input:checked').each(function(){ const input=$(this).data('input'); if(input) inputs.push(input); });
            $save.prop('disabled',true).text('Gemmer…');
            $.post(Hangar18Manager.ajaxUrl || window.ajaxurl, { action:'h18_save_page_component', nonce:Hangar18Manager.pageComponentNonce, name:name, component_id:existing ? String(existing.Id) : '', sections:JSON.stringify(sections), inputs:JSON.stringify(inputs) })
                .done(function(response){
                    if(!response || !response.success || !response.data || !response.data.component){ window.alert((response&&response.data&&response.data.message)||'Linked component kunne ikke gemmes.'); return; }
                    const component=response.data.component; pageLinkedComponents[String(component.Id)]=component; renderLinkedComponentsV0521(); refreshAllComponentEditorsV0521(); close();
                }).fail(function(xhr){ window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Linked component kunne ikke gemmes.'); })
                .always(function(){ $save.prop('disabled',false).text(existing ? 'Opdater global definition' : 'Gem linked component'); });
        });
    }

    function renderLinkedComponentsV0521() {
        if (!$pageLinkedComponentsList.length) { return; }
        const components = Object.values(pageLinkedComponents).sort(function(a,b){ return String(a.Name||'').localeCompare(String(b.Name||''),'da'); });
        $pageLinkedComponentsList.empty();
        if(!components.length){ $pageLinkedComponentsList.html('<p class="description">Ingen linked components endnu.</p>'); return; }
        components.forEach(function(component){
            const usage=parseInt(component.UsageCount,10)||0;
            const $row=$('<div>',{class:'h18-user-preset-row h18-linked-component-row','data-component-id':String(component.Id)});
            $row.append($('<button>',{type:'button',class:'h18-linked-component-insert'}).append($('<strong>',{text:String(component.Name||'Linked component')}),$('<small>',{text:'r'+String(component.Revision||1)+' · '+usage+' brug'})));
            $row.append($('<button>',{type:'button',class:'h18-linked-component-usage',title:'Vis brug','aria-label':'Vis brug'}).append($('<span>',{class:'dashicons dashicons-admin-links'})));
            $row.append($('<button>',{type:'button',class:'h18-linked-component-update',title:'Opdater fra valgt subtree','aria-label':'Opdater fra valgt subtree'}).append($('<span>',{class:'dashicons dashicons-update'})));
            $row.append($('<button>',{type:'button',class:'h18-linked-component-delete',title:'Slet linked component','aria-label':'Slet linked component'}).append($('<span>',{class:'dashicons dashicons-trash'})));
            $pageLinkedComponentsList.append($row);
        });
    }

    function applyLinkedComponentV0521(component) {
        if(!component || !component.Id){ return $(); }
        const $row=addPageSection('component');
        if(!$row.length){ return $row; }
        pageSectionControls($row,'.h18-component-select').val(String(component.Id));
        pageSectionControls($row,'.h18-component-revision').val(parseInt(component.Revision,10)||1);
        pageSectionControls($row,'.h18-component-overrides-json').val('{}');
        pageSectionControls($row,'.h18-section-navigator-label').val(String(component.Name||'Linked component'));
        refreshPageSectionType($row); renderComponentInstanceEditorV0521($row); setSectionTitleSummary($row); syncPageSectionOrder(); inspectPageSection($row); scheduleEditorHistoryCapture(0); return $row;
    }

    function refreshAllComponentEditorsV0521(){ $pageSections.children('.h18-page-section-row[data-section-type="component"]').each(function(){ renderComponentInstanceEditorV0521($(this)); renderCanvasPreview($(this)); }); }

    $(document).on('click','.h18-linked-component-insert',function(){ const component=pageLinkedComponents[String($(this).closest('.h18-linked-component-row').attr('data-component-id')||'')]; applyLinkedComponentV0521(component); });
    $(document).on('click','.h18-linked-component-usage',function(){
        const component=pageLinkedComponents[String($(this).closest('.h18-linked-component-row').attr('data-component-id')||'')]; if(!component)return;
        const usage=Array.isArray(component.Usage)?component.Usage:[];
        window.alert(usage.length ? 'Brug af “'+String(component.Name||'Component')+'”:\n\n'+usage.map(function(item){return '• '+String(item.PageTitle||item.PageSlug)+' / '+String(item.SectionKey||'');}).join('\n') : 'Komponenten bruges ikke på gemte sider endnu.');
    });
    $(document).on('click','.h18-linked-component-update',function(){
        const id=String($(this).closest('.h18-linked-component-row').attr('data-component-id')||'');
        if(!$inspectedSection.length){window.alert('Vælg først det subtree, der skal være den nye globale definition.');return;}
        openSaveLinkedComponentDialogV0521(id);
    });
    $(document).on('click','.h18-linked-component-delete',function(){
        const id=String($(this).closest('.h18-linked-component-row').attr('data-component-id')||''); const component=pageLinkedComponents[id]; if(!component)return;
        const usage=parseInt(component.UsageCount,10)||0; if(usage>0){window.alert('Komponenten bruges '+usage+' sted(er). Vis brug og fjern instanserne først.');return;}
        if(!window.confirm('Slet linked component “'+String(component.Name||'Component')+'”?'))return;
        $.post(Hangar18Manager.ajaxUrl || window.ajaxurl,{action:'h18_delete_page_component',nonce:Hangar18Manager.pageComponentNonce,component_id:id}).done(function(response){if(response&&response.success){delete pageLinkedComponents[id];renderLinkedComponentsV0521();}else{window.alert((response&&response.data&&response.data.message)||'Komponenten kunne ikke slettes.');}});
    });
    $('#h18-save-linked-component').on('click',function(){ if($inspectedSection.length)openSaveLinkedComponentDialogV0521(''); });
'''
js=replace_once(js,"\n    function restoreInspectedSection() {",linked_js+"\n    function restoreInspectedSection() {",'linked component JS insertion')

# Refresh component editor when type changes.
refresh_anchor="""        refreshCollectionEditorV0517($row);
        rebuildPageNavigator();
        refreshLayoutHierarchyV0519();
"""
refresh_new="""        refreshCollectionEditorV0517($row);
        if (type === 'component') { renderComponentInstanceEditorV0521($row); }
        rebuildPageNavigator();
        refreshLayoutHierarchyV0519();
"""
js=replace_once(js,refresh_anchor,refresh_new,'component type refresh')

# Canvas summary for component before carousel case.
canvas_anchor="""        } else if (type === 'carousel') {
            addTitle('Carousel');
"""
canvas_new="""        } else if (type === 'component') {
            const componentId = String(canvasFieldValue($row, 'ComponentId', ''));
            const component = pageLinkedComponents[componentId];
            const overrides = parseComponentOverridesV0521($row);
            $inner.append($('<div>', { class: 'h18-canvas-linked-component' }).append(
                $('<span>', { class: 'dashicons dashicons-admin-links' }),
                $('<div>').append($('<strong>', { text: component ? String(component.Name || 'Linked component') : 'Vælg linked component' }), $('<small>', { text: component ? 'Global revision ' + String(component.Revision || 1) + ' · ' + Object.keys(overrides).length + ' lokal(e) override(s)' : 'Ingen definition valgt' }))
            ));
        } else if (type === 'carousel') {
            addTitle('Carousel');
"""
js=replace_once(js,canvas_anchor,canvas_new,'component canvas preview')

# Locked canvas rows cannot be dragged, duplicated or deleted accidentally.
page_sort_old="""        $pageSections.sortable({
            items: '> .h18-page-section-row:not(.h18-page-section-removed)',
            handle: '.h18-page-section-drag',
            axis: 'y',
            tolerance: 'pointer',
            update: syncPageSectionOrder
        });
"""
page_sort_new="""        $pageSections.sortable({
            items: '> .h18-page-section-row:not(.h18-page-section-removed)',
            handle: '.h18-page-section-drag',
            axis: 'y',
            tolerance: 'pointer',
            start: function(event,ui){ if(rowLockedV0521(ui.item)){ $(this).sortable('cancel'); return false; } },
            update: syncPageSectionOrder
        });
"""
js=replace_once(js,page_sort_old,page_sort_new,'locked canvas sortable')

dup_anchor="""        const $source = $(this).closest('.h18-page-section-row');
        if ($inspectedSection.length && $inspectedSection.get(0) === $source.get(0)) {
"""
dup_new="""        const $source = $(this).closest('.h18-page-section-row');
        if (rowLockedV0521($source)) { window.alert('Laget er låst. Lås det op før du duplikerer det.'); return; }
        if ($inspectedSection.length && $inspectedSection.get(0) === $source.get(0)) {
"""
js=replace_once(js,dup_anchor,dup_new,'locked duplicate')

# Pattern messages/labels and linked initial render.
js=js.replace('Gem som komponent','Gem som pattern')
js=js.replace('Komponenten kunne ikke gemmes.','Pattern kunne ikke gemmes.')
js=js.replace('Slet komponenten “','Slet pattern “')

# Existing preset save handler should not operate on linked instances.
preset_click_anchor="""    $('#h18-save-section-preset').on('click', function () {
        if (!$inspectedSection.length) {
            return;
        }
"""
preset_click_new="""    $('#h18-save-section-preset').on('click', function () {
        if (!$inspectedSection.length) {
            return;
        }
        if (String($inspectedSection.attr('data-section-type') || '') === 'component') { window.alert('Linked component-instanser gemmes ikke som patterns.'); return; }
"""
js=replace_once(js,preset_click_anchor,preset_click_new,'pattern linked rejection handler')

# Ensure inspector action enabled/disabled tracks selected section. Existing refreshInspectorMeta toggles preset button; add linked button there by mirroring.
js=js.replace("$('#h18-save-section-preset').prop('disabled', !hasSection || type === 'legacy');","$('#h18-save-section-preset').prop('disabled', !hasSection || type === 'legacy' || type === 'component');\n        $('#h18-save-linked-component').prop('disabled', !hasSection || type === 'legacy' || type === 'component');")

# Initial render linked library/editors alongside presets.
js=replace_once(js,
"""        renderUserPresets();
        rebuildPageNavigator();
""",
"""        renderUserPresets();
        renderLinkedComponentsV0521();
        refreshAllComponentEditorsV0521();
        rebuildPageNavigator();
""",'initial component render')

# CSS.
css_block=r'''

/* v0.5.21 – Navigator tree + linked components */
.h18-navigator-item{grid-template-columns:auto minmax(0,1fr) auto auto auto}.h18-navigator-tool{appearance:none;border:0;background:transparent;padding:3px;color:#646970;cursor:pointer}.h18-navigator-tool:hover,.h18-navigator-tool:focus{color:#2271b1}.h18-navigator-item.is-locked{background:#f6f7f7}.h18-navigator-item.is-locked .h18-navigator-drag{cursor:not-allowed;color:#8c8f94}.h18-page-section-row:has(.h18-section-navigator-locked[value="1"]) .h18-page-section-drag{opacity:.35;cursor:not-allowed}.h18-linked-component-row{grid-template-columns:minmax(0,1fr) auto auto auto}.h18-component-status-line{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:8px 10px;background:#f0f6fc;border-left:3px solid #2271b1}.h18-component-overrides-editor{display:grid;gap:10px;margin-top:12px}.h18-component-override-field{display:grid;gap:5px;padding:10px;border:1px solid #dcdcde;border-radius:6px;background:#fff}.h18-component-override-field>span{font-weight:600}.h18-component-media-override{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.h18-editor-component{min-width:0;width:100%}.h18-canvas-linked-component{display:flex;align-items:center;gap:12px;padding:18px;border:2px dashed rgba(34,113,177,.35);border-radius:7px;background:rgba(240,246,252,.72)}.h18-canvas-linked-component .dashicons{font-size:28px;width:28px;height:28px}.h18-canvas-linked-component strong,.h18-canvas-linked-component small{display:block}.h18-component-dialog-overlay{position:fixed;inset:0;z-index:100200;display:grid;place-items:center;padding:24px;background:rgba(0,0,0,.48)}.h18-component-dialog{width:min(760px,calc(100vw - 32px));max-height:calc(100vh - 48px);overflow:auto;padding:22px;border-radius:10px;background:#fff;box-shadow:0 24px 70px rgba(0,0,0,.28)}.h18-component-dialog h3{margin-top:0}.h18-component-dialog>label{display:grid;gap:5px}.h18-component-input-choices{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin:14px 0}.h18-component-input-choice{display:flex;gap:8px;align-items:flex-start;padding:8px;border:1px solid #dcdcde;border-radius:5px}.h18-component-dialog-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:16px}@media(max-width:782px){.h18-component-input-choices{grid-template-columns:1fr}}
'''
if '/* v0.5.21 – Navigator tree + linked components */' in css: raise SystemExit('v0.5.21 CSS already present')
css=css.rstrip()+css_block+'\n'

# Readme.
readme=replace_once(readme,'Version: 0.5.20','Version: 0.5.21','readme version')
anchor='== Version 0.5.20 – E3 Design System completion ==\n'
new="""== Version 0.5.21 – E4 linked component engine foundation ==

Nyt:
- UD-043: Navigator tree får separat lagnavn, rename, hide/show, lock/unlock og realtime reorder-beskyttelse
- låste lag kan ikke trækkes, skjules eller duplikeres ved et uheld i editoren
- UD-044: et valgt layout-subtree kan gemmes som en rigtig linked component med intern nesting bevaret
- linked components gemmes i separat versioneret WordPress-option; eksisterende presets bevares som ikke-linked Patterns
- UD-045: component-instanser gemmer kun ComponentId + lokale overrides og resolver altid den aktuelle globale definition ved render, så én atomisk option-opdatering propagere til alle instanser
- global definition har monotont Revision-nummer; instans-editor viser aktuel revision og usage
- UD-046: ved oprettelse/opdatering vælger designeren eksplicit hvilke Title/Content/Image/Button inputs der frigives; layout/design er ikke overridable lokalt
- risky Content inputs for CSS/HTML/Shortcode/Embed frigives ikke
- linked component kan ikke indeholde legacy eller andre linked components, så recursive component cycles er blokeret i foundation
- UD-050: usage inspector scanner alle gemte Hangar18-sider og viser side + section key; komponent med usage kan ikke slettes
- component-instanser har eget canvas-kort og indgår i responsive visibility/layout som én node
- page-editor schema løftes bagudkompatibelt til 1.17

"""+anchor
readme=replace_once(readme,anchor,new,'readme v0.5.20 anchor')

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.21 patch applied')
