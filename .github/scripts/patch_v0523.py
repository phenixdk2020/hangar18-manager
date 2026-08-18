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

# Version only; page-editor schema is unchanged in this data-engine release.
php=once(php,' * Version: 0.5.22',' * Version: 0.5.23','plugin header version')
php=once(php,"    const VERSION = '0.5.22';","    const VERSION = '0.5.23';",'plugin const version')

# Stores / post type.
php=once(php,
"""    const PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1';
    const PAGE_TEMPLATES_OPTION       = 'hangar18_manager_page_templates_v1';
    const FORM_SUBMISSIONS_OPTION   = 'hangar18_manager_form_submissions_v1';
""",
"""    const PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1';
    const PAGE_TEMPLATES_OPTION       = 'hangar18_manager_page_templates_v1';
    const CUSTOM_DATA_TYPES_OPTION    = 'hangar18_manager_custom_data_types_v1';
    const DATA_ENTRY_POST_TYPE        = 'h18_data_entry';
    const FORM_SUBMISSIONS_OPTION   = 'hangar18_manager_form_submissions_v1';
""",'data constants')

# Register post type and handlers.
php=once(php,
"""    private function __construct() {
        add_action('admin_init', [$this, 'maybe_run_frontend_repair_046'], 15);
""",
"""    private function __construct() {
        add_action('init', [$this, 'register_dynamic_data_post_type'], 5);
        add_action('admin_init', [$this, 'maybe_run_frontend_repair_046'], 15);
""",'data post type init')
php=once(php,
"""        add_action('admin_post_h18_save_static_content', [$this, 'handle_save_static_content']);
        add_action('admin_post_h18_save_page_editor', [$this, 'handle_save_page_editor']);
""",
"""        add_action('admin_post_h18_save_static_content', [$this, 'handle_save_static_content']);
        add_action('admin_post_h18_save_data_type', [$this, 'handle_save_data_type']);
        add_action('admin_post_h18_delete_data_type', [$this, 'handle_delete_data_type']);
        add_action('admin_post_h18_save_data_entry', [$this, 'handle_save_data_entry']);
        add_action('admin_post_h18_delete_data_entry', [$this, 'handle_delete_data_entry']);
        add_action('admin_post_h18_save_page_editor', [$this, 'handle_save_page_editor']);
""",'data handlers')

# Admin navigation and dashboard card.
php=once(php,
"""        add_submenu_page(self::MENU_SLUG, 'Billedgalleri', 'Billedgalleri', $capability, 'hangar18-gallery', [$this, 'render_gallery']);
        add_submenu_page(self::MENU_SLUG, 'Sider', 'Sider', $capability, 'hangar18-pages', [$this, 'render_pages']);
""",
"""        add_submenu_page(self::MENU_SLUG, 'Billedgalleri', 'Billedgalleri', $capability, 'hangar18-gallery', [$this, 'render_gallery']);
        add_submenu_page(self::MENU_SLUG, 'Data', 'Data', $capability, 'hangar18-data', [$this, 'render_data']);
        add_submenu_page(self::MENU_SLUG, 'Sider', 'Sider', $capability, 'hangar18-pages', [$this, 'render_pages']);
""",'data submenu')
php=once(php,
"""                    ['hangar18-gallery', 'dashicons-format-gallery', 'Billedgalleri', 'Opret albums, vælg flere billeder og sortér med drag-and-drop.', 'Aktiv'],
                    ['hangar18-pages', 'dashicons-layout', 'Sider', 'Redigér almindelige sider med indholdssektioner, mailformularer og afstemninger.', 'Aktiv'],
""",
"""                    ['hangar18-gallery', 'dashicons-format-gallery', 'Billedgalleri', 'Opret albums, vælg flere billeder og sortér med drag-and-drop.', 'Aktiv'],
                    ['hangar18-data', 'dashicons-database', 'Data', 'Byg egne datatyper og redigér validerede entries med tekst, tal, bool, dato og medier.', 'Aktiv'],
                    ['hangar18-pages', 'dashicons-layout', 'Sider', 'Redigér almindelige sider med indholdssektioner, mailformularer og afstemninger.', 'Aktiv'],
""",'dashboard data card')

# Generic data engine, inserted before Page Editor section.
data_engine=r'''

    /* ================================================================
       GENERIC DYNAMIC DATA ENGINE — v0.5.23 / E5 UD-051 + UD-052
       ================================================================ */

    public function register_dynamic_data_post_type() {
        register_post_type(self::DATA_ENTRY_POST_TYPE, [
            'labels' => ['name' => 'Hangar18 data', 'singular_name' => 'Hangar18 data-entry'],
            'public' => false,
            'show_ui' => false,
            'show_in_menu' => false,
            'show_in_rest' => false,
            'rewrite' => false,
            'query_var' => false,
            'supports' => ['title'],
            'capability_type' => 'page',
            'map_meta_cap' => true,
        ]);
    }

    private function custom_data_field_types() {
        return [
            'text' => 'Tekst',
            'number' => 'Tal',
            'bool' => 'Ja/nej',
            'date' => 'Dato',
            'media' => 'Medie / billede',
        ];
    }

    private function normalize_custom_data_type(array $raw, $existing_key = '') {
        $key = sanitize_key((string) ($raw['Key'] ?? ''));
        $existing_key = sanitize_key((string) $existing_key);
        if ($existing_key !== '' && $key !== $existing_key) {
            throw new RuntimeException('Datatype-nøglen er permanent og kan ikke ændres efter oprettelse.');
        }
        if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{1,47}$/', $key)) {
            throw new RuntimeException('Datatype-nøglen skal være 2–48 tegn og kun bruge a-z, 0-9, bindestreg eller underscore.');
        }
        $singular = sanitize_text_field((string) ($raw['SingularLabel'] ?? ''));
        $plural = sanitize_text_field((string) ($raw['PluralLabel'] ?? ''));
        if ($singular === '') { throw new RuntimeException('Datatype skal have et navn i ental.'); }
        if ($plural === '') { $plural = $singular; }

        $allowed = $this->custom_data_field_types();
        $fields = [];
        $used = [];
        $raw_fields = isset($raw['Fields']) && is_array($raw['Fields']) ? array_slice($raw['Fields'], 0, 30) : [];
        foreach ($raw_fields as $field) {
            if (!is_array($field) || !empty($field['Remove'])) { continue; }
            $field_key = sanitize_key((string) ($field['Key'] ?? ''));
            $label = sanitize_text_field((string) ($field['Label'] ?? ''));
            $type = sanitize_key((string) ($field['Type'] ?? 'text'));
            if ($field_key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{0,47}$/', $field_key)) {
                throw new RuntimeException('Alle datafelter skal have en gyldig nøgle på højst 48 tegn.');
            }
            if (isset($used[$field_key])) { throw new RuntimeException("Felt-nøglen '{$field_key}' findes mere end én gang."); }
            if ($label === '') { throw new RuntimeException("Feltet '{$field_key}' mangler et navn."); }
            if (!isset($allowed[$type])) { throw new RuntimeException("Feltet '{$field_key}' har en ukendt felttype."); }
            $used[$field_key] = true;
            $fields[] = [
                'Key' => $field_key,
                'Label' => $label,
                'Type' => $type,
                'Required' => !empty($field['Required']),
                'Order' => count($fields) + 1,
            ];
        }
        if (!$fields) { throw new RuntimeException('Datatype skal have mindst ét datafelt.'); }
        return [
            'Key' => $key,
            'SingularLabel' => $singular,
            'PluralLabel' => $plural,
            'Fields' => $fields,
            'SchemaVersion' => 1,
        ];
    }

    private function get_custom_data_types() {
        $stored = get_option(self::CUSTOM_DATA_TYPES_OPTION, []);
        if (!is_array($stored)) { return []; }
        $types = [];
        foreach (array_slice($stored, 0, 50, true) as $id => $raw) {
            if (!is_array($raw)) { continue; }
            $raw['Key'] = $raw['Key'] ?? $id;
            try { $type = $this->normalize_custom_data_type($raw, (string) ($raw['Key'] ?? $id)); }
            catch (Throwable $e) { $this->log('WARN', 'CUSTOM_DATA_TYPE_INVALID', (string) $e->getMessage()); continue; }
            $type['CreatedUtc'] = sanitize_text_field((string) ($raw['CreatedUtc'] ?? ''));
            $type['UpdatedUtc'] = sanitize_text_field((string) ($raw['UpdatedUtc'] ?? ''));
            $types[$type['Key']] = $type;
        }
        ksort($types, SORT_NATURAL | SORT_FLAG_CASE);
        return $types;
    }

    private function custom_data_entry_query($type_key, $limit = 100) {
        return get_posts([
            'post_type' => self::DATA_ENTRY_POST_TYPE,
            'post_status' => ['publish','draft','private'],
            'posts_per_page' => max(1, min(200, (int) $limit)),
            'meta_key' => '_h18_data_type',
            'meta_value' => sanitize_key((string) $type_key),
            'orderby' => 'modified',
            'order' => 'DESC',
        ]);
    }

    private function custom_data_entry_count($type_key) {
        return count($this->custom_data_entry_query($type_key, 200));
    }

    private function custom_data_entry_for_type($entry_id, $type_key) {
        $post = get_post((int) $entry_id);
        if (!$post instanceof WP_Post || $post->post_type !== self::DATA_ENTRY_POST_TYPE) { return null; }
        if (sanitize_key((string) get_post_meta($post->ID, '_h18_data_type', true)) !== sanitize_key((string) $type_key)) { return null; }
        return $post;
    }

    private function custom_data_entry_values($entry_id, array $schema) {
        $stored = get_post_meta((int) $entry_id, '_h18_data_values', true);
        $stored = is_array($stored) ? $stored : [];
        $values = [];
        foreach ($schema['Fields'] as $field) {
            $key = (string) $field['Key'];
            if (array_key_exists($key, $stored)) { $values[$key] = $stored[$key]; continue; }
            $meta = get_post_meta((int) $entry_id, '_h18_field_' . $key, true);
            $values[$key] = $field['Type'] === 'bool' ? ($meta === '1' || $meta === 1 || $meta === true) : $meta;
        }
        return $values;
    }

    private function sanitize_custom_data_value(array $field, $value, array &$errors) {
        $key = (string) $field['Key'];
        $label = (string) $field['Label'];
        $type = (string) $field['Type'];
        $required = !empty($field['Required']);
        if ($type === 'bool') { return !empty($value); }
        $value = is_scalar($value) ? trim((string) $value) : '';
        if ($required && $value === '') { $errors[] = "Feltet '{$label}' er obligatorisk."; return ''; }
        if ($value === '') { return $type === 'media' ? 0 : ''; }
        if ($type === 'text') { return sanitize_text_field($value); }
        if ($type === 'number') {
            if (!is_numeric($value)) { $errors[] = "Feltet '{$label}' skal være et tal."; return ''; }
            $number = (float) $value;
            return rtrim(rtrim(number_format($number, 10, '.', ''), '0'), '.');
        }
        if ($type === 'date') {
            $date = DateTime::createFromFormat('!Y-m-d', $value);
            $valid = $date && $date->format('Y-m-d') === $value;
            if (!$valid) { $errors[] = "Feltet '{$label}' skal være en gyldig dato (ÅÅÅÅ-MM-DD)."; return ''; }
            return $value;
        }
        if ($type === 'media') {
            $media_id = absint($value);
            $attachment = $media_id > 0 ? get_post($media_id) : null;
            if (!$attachment instanceof WP_Post || $attachment->post_type !== 'attachment') {
                $errors[] = "Feltet '{$label}' peger ikke på et gyldigt medie.";
                return 0;
            }
            return $media_id;
        }
        $errors[] = "Feltet '{$key}' har en ukendt felttype.";
        return '';
    }

    private function custom_data_redirect($type_key = '', array $args = []) {
        if ($type_key !== '') { $args['type'] = sanitize_key((string) $type_key); }
        $this->redirect('hangar18-data', $args);
    }

    public function handle_save_data_type() {
        if (!current_user_can('manage_options')) { wp_die('Du har ikke rettigheder til at ændre datatyper.'); }
        check_admin_referer('h18_save_data_type');
        $existing_key = sanitize_key((string) wp_unslash($_POST['existing_key'] ?? ''));
        $raw = [
            'Key' => wp_unslash($_POST['data_type_key'] ?? ''),
            'SingularLabel' => wp_unslash($_POST['data_type_singular'] ?? ''),
            'PluralLabel' => wp_unslash($_POST['data_type_plural'] ?? ''),
            'Fields' => isset($_POST['data_fields']) && is_array($_POST['data_fields']) ? wp_unslash($_POST['data_fields']) : [],
        ];
        try {
            $type = $this->normalize_custom_data_type($raw, $existing_key);
            $types = $this->get_custom_data_types();
            if ($existing_key === '' && isset($types[$type['Key']])) { throw new RuntimeException('Der findes allerede en datatype med denne nøgle.'); }
            $now = gmdate('c');
            $created = $existing_key !== '' && isset($types[$existing_key]) ? (string) ($types[$existing_key]['CreatedUtc'] ?? '') : $now;
            $type['CreatedUtc'] = $created !== '' ? $created : $now;
            $type['UpdatedUtc'] = $now;
            $types[$type['Key']] = $type;
            update_option(self::CUSTOM_DATA_TYPES_OPTION, $types, false);
            $this->log('INFO', 'CUSTOM_DATA_TYPE_SAVED', "Datatype '{$type['Key']}' gemt med " . count($type['Fields']) . ' felter.');
            $this->set_notice('success', "Datatypen '{$type['SingularLabel']}' er gemt.");
            $this->custom_data_redirect($type['Key']);
        } catch (Throwable $e) {
            $this->log('ERROR', 'CUSTOM_DATA_TYPE_SAVE_FAILED', $e->getMessage());
            $this->set_notice('error', 'Datatypen kunne ikke gemmes: ' . $e->getMessage());
            $this->custom_data_redirect($existing_key !== '' ? $existing_key : 'new');
        }
    }

    public function handle_delete_data_type() {
        if (!current_user_can('manage_options')) { wp_die('Du har ikke rettigheder til at slette datatyper.'); }
        check_admin_referer('h18_delete_data_type');
        $key = sanitize_key((string) wp_unslash($_POST['data_type_key'] ?? ''));
        $types = $this->get_custom_data_types();
        if ($key === '' || !isset($types[$key])) { $this->set_notice('error', 'Datatypen blev ikke fundet.'); $this->custom_data_redirect(); }
        $count = $this->custom_data_entry_count($key);
        if ($count > 0) { $this->set_notice('error', "Datatypen kan ikke slettes, fordi den har {$count} entries."); $this->custom_data_redirect($key); }
        $name = (string) $types[$key]['SingularLabel'];
        unset($types[$key]);
        update_option(self::CUSTOM_DATA_TYPES_OPTION, $types, false);
        $this->log('INFO', 'CUSTOM_DATA_TYPE_DELETED', "Datatype '{$key}' blev slettet.");
        $this->set_notice('success', "Datatypen '{$name}' er slettet.");
        $this->custom_data_redirect();
    }

    public function handle_save_data_entry() {
        $this->require_capability();
        check_admin_referer('h18_save_data_entry');
        $type_key = sanitize_key((string) wp_unslash($_POST['data_type_key'] ?? ''));
        $types = $this->get_custom_data_types();
        if ($type_key === '' || !isset($types[$type_key])) { $this->set_notice('error', 'Datatypen blev ikke fundet.'); $this->custom_data_redirect(); }
        $schema = $types[$type_key];
        $entry_id = absint($_POST['entry_id'] ?? 0);
        if ($entry_id > 0 && !$this->custom_data_entry_for_type($entry_id, $type_key)) { $this->set_notice('error', 'Data-entry blev ikke fundet i den valgte datatype.'); $this->custom_data_redirect($type_key); }
        $title = sanitize_text_field((string) wp_unslash($_POST['entry_title'] ?? ''));
        if ($title === '') { $this->set_notice('error', 'Entry skal have en titel.'); $this->custom_data_redirect($type_key, $entry_id ? ['entry_id' => $entry_id] : []); }
        $raw_values = isset($_POST['data_values']) && is_array($_POST['data_values']) ? wp_unslash($_POST['data_values']) : [];
        $values = [];
        $errors = [];
        foreach ($schema['Fields'] as $field) {
            $field_key = (string) $field['Key'];
            $values[$field_key] = $this->sanitize_custom_data_value($field, $raw_values[$field_key] ?? null, $errors);
        }
        if ($errors) { $this->set_notice('error', implode(' ', $errors)); $this->custom_data_redirect($type_key, $entry_id ? ['entry_id' => $entry_id] : []); }
        $postarr = ['post_type' => self::DATA_ENTRY_POST_TYPE, 'post_status' => 'publish', 'post_title' => $title];
        if ($entry_id > 0) { $postarr['ID'] = $entry_id; $result = wp_update_post($postarr, true); }
        else { $result = wp_insert_post($postarr, true); }
        if (is_wp_error($result)) { $this->set_notice('error', 'Entry kunne ikke gemmes: ' . $result->get_error_message()); $this->custom_data_redirect($type_key); }
        $entry_id = (int) $result;
        update_post_meta($entry_id, '_h18_data_type', $type_key);
        update_post_meta($entry_id, '_h18_data_values', $values);
        update_post_meta($entry_id, '_h18_data_schema_version', (int) ($schema['SchemaVersion'] ?? 1));
        $valid_meta = [];
        foreach ($values as $field_key => $value) {
            $meta_key = '_h18_field_' . sanitize_key((string) $field_key);
            $valid_meta[$meta_key] = true;
            update_post_meta($entry_id, $meta_key, is_bool($value) ? ($value ? '1' : '0') : $value);
        }
        foreach (array_keys((array) get_post_meta($entry_id)) as $meta_key) {
            if (strpos((string) $meta_key, '_h18_field_') === 0 && !isset($valid_meta[$meta_key])) { delete_post_meta($entry_id, $meta_key); }
        }
        $this->log('INFO', 'CUSTOM_DATA_ENTRY_SAVED', "Data-entry ID {$entry_id} gemt i '{$type_key}'.");
        $this->set_notice('success', "Entry '{$title}' er gemt.");
        $this->custom_data_redirect($type_key, ['entry_id' => $entry_id]);
    }

    public function handle_delete_data_entry() {
        $this->require_capability();
        check_admin_referer('h18_delete_data_entry');
        $type_key = sanitize_key((string) wp_unslash($_POST['data_type_key'] ?? ''));
        $entry_id = absint($_POST['entry_id'] ?? 0);
        $entry = $this->custom_data_entry_for_type($entry_id, $type_key);
        if (!$entry) { $this->set_notice('error', 'Data-entry blev ikke fundet.'); $this->custom_data_redirect($type_key); }
        $title = (string) $entry->post_title;
        wp_delete_post($entry_id, true);
        $this->log('INFO', 'CUSTOM_DATA_ENTRY_DELETED', "Data-entry ID {$entry_id} slettet fra '{$type_key}'.");
        $this->set_notice('success', "Entry '{$title}' er slettet.");
        $this->custom_data_redirect($type_key);
    }

    private function render_custom_data_field_input(array $field, $value) {
        $key = (string) $field['Key'];
        $name = 'data_values[' . $key . ']';
        $type = (string) $field['Type'];
        if ($type === 'bool') {
            echo '<input type="hidden" name="' . esc_attr($name) . '" value="0" /><label class="h18-data-bool"><input type="checkbox" name="' . esc_attr($name) . '" value="1" ' . checked(!empty($value), true, false) . ' /> Ja</label>';
            return;
        }
        if ($type === 'number') { echo '<input type="number" step="any" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />'; return; }
        if ($type === 'date') { echo '<input type="date" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />'; return; }
        if ($type === 'media') {
            $media_id = absint($value);
            echo '<div class="h18-data-media-field"><input class="h18-data-media-id" type="hidden" name="' . esc_attr($name) . '" value="' . esc_attr($media_id) . '" /><div class="h18-data-media-preview">';
            if ($media_id) { echo wp_get_attachment_image($media_id, 'thumbnail'); }
            echo '</div><button type="button" class="button h18-data-media-pick">Vælg medie</button> <button type="button" class="button-link-delete h18-data-media-clear">Fjern</button></div>';
            return;
        }
        echo '<input type="text" name="' . esc_attr($name) . '" value="' . esc_attr((string) $value) . '" />';
    }

    public function render_data() {
        $this->require_capability();
        $types = $this->get_custom_data_types();
        $requested = isset($_GET['type']) ? sanitize_key((string) wp_unslash($_GET['type'])) : '';
        if ($requested === '' && $types) { $requested = (string) array_key_first($types); }
        $is_new = $requested === 'new' || !$types;
        $selected = !$is_new && isset($types[$requested]) ? $types[$requested] : null;
        if (!$is_new && !$selected && $types) { $requested = (string) array_key_first($types); $selected = $types[$requested]; }
        $entry_id = absint($_GET['entry_id'] ?? 0);
        $entry = $selected && $entry_id ? $this->custom_data_entry_for_type($entry_id, $selected['Key']) : null;
        $entry_values = $entry && $selected ? $this->custom_data_entry_values($entry->ID, $selected) : [];
        $entries = $selected ? $this->custom_data_entry_query($selected['Key'], 100) : [];
        $can_schema = current_user_can('manage_options');
        $blank_field = ['Key'=>'felt','Label'=>'Felt','Type'=>'text','Required'=>false,'Order'=>1];
        ?>
        <div class="wrap h18-admin h18-data-admin">
            <h1>Data</h1>
            <?php $this->render_notice(); ?>
            <div class="h18-help-box"><strong>E5 Dynamic CMS:</strong> Datatyperne her er generiske schemas. v0.5.23 understøtter text, number, bool, date og media samt valideret CRUD. Senere binding/query-funktioner bygges direkte oven på samme datamodel.</div>
            <nav class="h18-page-tabs h18-data-type-tabs" aria-label="Vælg datatype">
                <?php foreach ($types as $type_key => $type) : ?><a class="<?php echo $selected && $selected['Key'] === $type_key ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($type_key))); ?>"><?php echo esc_html($type['PluralLabel']); ?></a><?php endforeach; ?>
                <?php if ($can_schema) : ?><a class="<?php echo $is_new ? 'is-active' : ''; ?>" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=new')); ?>">+ Ny datatype</a><?php endif; ?>
            </nav>

            <?php if ($is_new && !$can_schema) : ?>
                <div class="notice notice-warning"><p>Der er endnu ingen datatyper. En administrator skal oprette den første datatype.</p></div>
            <?php elseif ($is_new) :
                $schema = ['Key'=>'','SingularLabel'=>'','PluralLabel'=>'','Fields'=>[$blank_field]]; ?>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" class="h18-panel h18-data-schema-form">
                    <?php wp_nonce_field('h18_save_data_type'); ?><input type="hidden" name="action" value="h18_save_data_type" /><input type="hidden" name="existing_key" value="" />
                    <h2>Ny datatype</h2>
                    <div class="h18-module-fields-grid h18-module-fields-grid--four">
                        <div class="h18-field"><label><strong>Nøgle</strong></label><input id="h18-data-type-key" type="text" name="data_type_key" value="" placeholder="fx museum_vehicle" required /></div>
                        <div class="h18-field"><label><strong>Navn – ental</strong></label><input id="h18-data-type-singular" type="text" name="data_type_singular" value="" required /></div>
                        <div class="h18-field"><label><strong>Navn – flertal</strong></label><input type="text" name="data_type_plural" value="" /></div>
                    </div>
                    <h3>Felter</h3><div id="h18-data-schema-fields" class="h18-data-schema-fields"><?php $this->render_data_schema_field_row($blank_field, 0); ?></div>
                    <button type="button" class="button" id="h18-data-add-field">+ Tilføj felt</button>
                    <p><button type="submit" class="button button-primary">Opret datatype</button></p>
                </form>
            <?php elseif ($selected) : ?>
                <div class="h18-data-summary"><div><h2><?php echo esc_html($selected['PluralLabel']); ?></h2><p><code><?php echo esc_html($selected['Key']); ?></code> · <?php echo esc_html(count($selected['Fields'])); ?> felter · <?php echo esc_html(count($entries)); ?> viste entries</p></div><a class="button button-primary" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($selected['Key']) . '&entry_id=0#h18-data-entry-form')); ?>">+ Ny <?php echo esc_html($selected['SingularLabel']); ?></a></div>

                <?php if ($can_schema) : ?><details class="h18-panel h18-data-schema-details"><summary><strong>Redigér datatype-schema</strong></summary>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" class="h18-data-schema-form">
                        <?php wp_nonce_field('h18_save_data_type'); ?><input type="hidden" name="action" value="h18_save_data_type" /><input type="hidden" name="existing_key" value="<?php echo esc_attr($selected['Key']); ?>" />
                        <div class="h18-module-fields-grid h18-module-fields-grid--four">
                            <div class="h18-field"><label><strong>Nøgle</strong></label><input type="text" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" readonly /></div>
                            <div class="h18-field"><label><strong>Navn – ental</strong></label><input type="text" name="data_type_singular" value="<?php echo esc_attr($selected['SingularLabel']); ?>" required /></div>
                            <div class="h18-field"><label><strong>Navn – flertal</strong></label><input type="text" name="data_type_plural" value="<?php echo esc_attr($selected['PluralLabel']); ?>" /></div>
                        </div>
                        <h3>Felter</h3><div id="h18-data-schema-fields" class="h18-data-schema-fields"><?php foreach ($selected['Fields'] as $field_index => $field) { $this->render_data_schema_field_row($field, $field_index); } ?></div>
                        <button type="button" class="button" id="h18-data-add-field">+ Tilføj felt</button>
                        <p><button type="submit" class="button button-primary">Gem schema</button></p>
                    </form>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" onsubmit="return confirm('Slet datatypen? Den kan kun slettes uden entries.');"><?php wp_nonce_field('h18_delete_data_type'); ?><input type="hidden" name="action" value="h18_delete_data_type" /><input type="hidden" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" /><button type="submit" class="button-link-delete">Slet datatype</button></form>
                </details><?php endif; ?>

                <div class="h18-data-layout">
                    <section class="h18-panel h18-data-entry-list"><h3><?php echo esc_html($selected['PluralLabel']); ?></h3>
                        <?php if (!$entries) : ?><p class="description">Ingen entries endnu.</p><?php else : ?><table class="widefat striped"><thead><tr><th>Titel</th><th>Ændret</th><th></th></tr></thead><tbody><?php foreach ($entries as $item) : ?><tr><td><strong><?php echo esc_html($item->post_title); ?></strong></td><td><?php echo esc_html(get_post_modified_time('Y-m-d H:i', false, $item)); ?></td><td><a class="button button-small" href="<?php echo esc_url(admin_url('admin.php?page=hangar18-data&type=' . rawurlencode($selected['Key']) . '&entry_id=' . (int) $item->ID . '#h18-data-entry-form')); ?>">Redigér</a></td></tr><?php endforeach; ?></tbody></table><?php endif; ?>
                    </section>
                    <section id="h18-data-entry-form" class="h18-panel h18-data-entry-form"><h3><?php echo $entry ? 'Redigér ' : 'Ny '; ?><?php echo esc_html($selected['SingularLabel']); ?></h3>
                        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>"><?php wp_nonce_field('h18_save_data_entry'); ?><input type="hidden" name="action" value="h18_save_data_entry" /><input type="hidden" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="entry_id" value="<?php echo esc_attr($entry ? $entry->ID : 0); ?>" />
                            <div class="h18-field"><label><strong>Titel</strong></label><input type="text" name="entry_title" value="<?php echo esc_attr($entry ? $entry->post_title : ''); ?>" required /></div>
                            <?php foreach ($selected['Fields'] as $field) : $value = $entry ? ($entry_values[$field['Key']] ?? '') : ''; ?><div class="h18-field"><label><strong><?php echo esc_html($field['Label']); ?><?php echo !empty($field['Required']) && $field['Type'] !== 'bool' ? ' *' : ''; ?></strong><small><?php echo esc_html($this->custom_data_field_types()[$field['Type']] ?? $field['Type']); ?></small></label><?php $this->render_custom_data_field_input($field, $value); ?></div><?php endforeach; ?>
                            <p><button type="submit" class="button button-primary">Gem entry</button></p>
                        </form>
                        <?php if ($entry) : ?><form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" onsubmit="return confirm('Slet denne entry permanent?');"><?php wp_nonce_field('h18_delete_data_entry'); ?><input type="hidden" name="action" value="h18_delete_data_entry" /><input type="hidden" name="data_type_key" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="entry_id" value="<?php echo esc_attr($entry->ID); ?>" /><button type="submit" class="button-link-delete">Slet entry</button></form><?php endif; ?>
                    </section>
                </div>
            <?php endif; ?>
            <template id="h18-data-field-template"><?php $this->render_data_schema_field_row($blank_field, '__INDEX__'); ?></template>
        </div>
        <?php
    }

    private function render_data_schema_field_row(array $field, $index) {
        $prefix = 'data_fields[' . $index . ']';
        ?>
        <div class="h18-data-field-row" data-field-index="<?php echo esc_attr($index); ?>">
            <span class="dashicons dashicons-move h18-data-field-drag" title="Flyt felt"></span>
            <div class="h18-field"><label><strong>Nøgle</strong></label><input class="h18-data-field-key" type="text" name="<?php echo esc_attr($prefix); ?>[Key]" value="<?php echo esc_attr($field['Key']); ?>" required /></div>
            <div class="h18-field"><label><strong>Navn</strong></label><input class="h18-data-field-label" type="text" name="<?php echo esc_attr($prefix); ?>[Label]" value="<?php echo esc_attr($field['Label']); ?>" required /></div>
            <div class="h18-field"><label><strong>Type</strong></label><select name="<?php echo esc_attr($prefix); ?>[Type]"><?php foreach ($this->custom_data_field_types() as $type_key => $type_label) : ?><option value="<?php echo esc_attr($type_key); ?>" <?php selected($field['Type'], $type_key); ?>><?php echo esc_html($type_label); ?></option><?php endforeach; ?></select></div>
            <label class="h18-data-required"><input type="checkbox" name="<?php echo esc_attr($prefix); ?>[Required]" value="1" <?php checked(!empty($field['Required'])); ?> /> Obligatorisk</label>
            <input class="h18-data-field-remove" type="hidden" name="<?php echo esc_attr($prefix); ?>[Remove]" value="0" />
            <button type="button" class="button-link-delete h18-data-remove-field">Fjern</button>
        </div>
        <?php
    }
'''
php=once(php,
"""    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */
""",
data_engine+"""

    /* ================================================================
       PAGE EDITOR AND FUNCTION MODULES
       ================================================================ */
""",'insert data engine')

# Admin JS: schema rows, sorting, stable generated keys and media fields.
js_block=r'''

    /* v0.5.23 – Generic Dynamic Data schema + entry editor */
    const $dataSchemaFields = $('#h18-data-schema-fields');
    const dataFieldTemplate = document.getElementById('h18-data-field-template');
    let dataFieldSerialV0523 = 1000;
    function syncDataFieldRowsV0523(){
        if(!$dataSchemaFields.length)return;
        $dataSchemaFields.children('.h18-data-field-row:not(.is-removed)').each(function(index){$(this).find('.h18-data-field-drag').attr('title','Felt '+(index+1));});
    }
    if($dataSchemaFields.length){$dataSchemaFields.sortable({items:'> .h18-data-field-row:not(.is-removed)',handle:'.h18-data-field-drag',axis:'y',tolerance:'pointer',update:syncDataFieldRowsV0523});syncDataFieldRowsV0523();}
    $('#h18-data-add-field').on('click',function(){
        if(!dataFieldTemplate||!$dataSchemaFields.length)return;
        if($dataSchemaFields.children('.h18-data-field-row:not(.is-removed)').length>=30){window.alert('En datatype kan højst have 30 felter.');return;}
        dataFieldSerialV0523+=1;
        const html=dataFieldTemplate.innerHTML.replaceAll('__INDEX__',String(dataFieldSerialV0523));
        const $row=$(html.trim());$row.find('.h18-data-field-key').val('');$row.find('.h18-data-field-label').val('');$dataSchemaFields.append($row);syncDataFieldRowsV0523();
    });
    $(document).on('click','.h18-data-remove-field',function(){const $row=$(this).closest('.h18-data-field-row');$row.find('.h18-data-field-remove').val('1');$row.addClass('is-removed').hide();syncDataFieldRowsV0523();});
    $(document).on('blur','.h18-data-field-label',function(){const $row=$(this).closest('.h18-data-field-row');const $key=$row.find('.h18-data-field-key');if(!$key.val().trim())$key.val(slugify($(this).val()).replace(/-/g,'_'));});
    $('#h18-data-type-singular').on('blur',function(){const $key=$('#h18-data-type-key');if($key.length&&!$key.val().trim())$key.val(slugify($(this).val()).replace(/-/g,'_'));});
    $(document).on('click','.h18-data-media-pick',function(event){event.preventDefault();const $field=$(this).closest('.h18-data-media-field');const frame=wp.media({title:'Vælg medie',button:{text:'Brug medie'},multiple:false});frame.on('select',function(){const media=frame.state().get('selection').first().toJSON();const thumb=media.sizes&&media.sizes.thumbnail?media.sizes.thumbnail.url:media.url;$field.find('.h18-data-media-id').val(media.id||0);$field.find('.h18-data-media-preview').html($('<img>',{src:thumb,alt:media.alt||''}));});frame.open();});
    $(document).on('click','.h18-data-media-clear',function(event){event.preventDefault();const $field=$(this).closest('.h18-data-media-field');$field.find('.h18-data-media-id').val('0');$field.find('.h18-data-media-preview').empty();});
'''
if '/* v0.5.23 – Generic Dynamic Data schema + entry editor */' in js:
    raise SystemExit('v0.5.23 JS already present')
# Insert before final jQuery wrapper close.
last=js.rfind('\n});')
if last<0: raise SystemExit('admin.js wrapper end not found')
js=js[:last]+js_block+js[last:]

css_block=r'''

/* v0.5.23 – Generic Dynamic Data */
.h18-data-type-tabs{margin-bottom:18px}.h18-data-summary{display:flex;justify-content:space-between;gap:16px;align-items:center;margin:16px 0}.h18-data-summary h2{margin:0 0 4px}.h18-data-summary p{margin:0}.h18-data-schema-details{margin-bottom:18px}.h18-data-schema-details>summary{cursor:pointer;padding:4px 0 12px}.h18-data-schema-fields{display:grid;gap:8px;margin:10px 0 12px}.h18-data-field-row{display:grid;grid-template-columns:auto minmax(120px,.8fr) minmax(180px,1.2fr) minmax(120px,.7fr) auto auto;gap:10px;align-items:end;padding:10px;border:1px solid #dcdcde;border-radius:6px;background:#fff}.h18-data-field-drag{align-self:center;cursor:move;color:#646970}.h18-data-required{align-self:center;white-space:nowrap}.h18-data-layout{display:grid;grid-template-columns:minmax(320px,.9fr) minmax(360px,1.1fr);gap:18px;align-items:start}.h18-data-entry-form .h18-field{margin-bottom:14px}.h18-data-entry-form .h18-field>label{display:flex;justify-content:space-between;gap:8px}.h18-data-entry-form input[type=text],.h18-data-entry-form input[type=number],.h18-data-entry-form input[type=date]{width:100%}.h18-data-media-field{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.h18-data-media-preview img{width:64px;height:64px;object-fit:cover;border-radius:4px}.h18-data-bool{display:inline-flex!important;justify-content:flex-start!important;align-items:center;gap:6px}@media(max-width:1000px){.h18-data-layout{grid-template-columns:1fr}.h18-data-field-row{grid-template-columns:auto 1fr 1fr}.h18-data-required,.h18-data-remove-field{grid-column:auto}}@media(max-width:782px){.h18-data-summary{align-items:flex-start;flex-direction:column}.h18-data-field-row{grid-template-columns:1fr}.h18-data-field-drag{display:none}}
'''
if '/* v0.5.23 – Generic Dynamic Data */' in css: raise SystemExit('v0.5.23 CSS already present')
css=css.rstrip()+css_block+'\n'

# Readme release notes.
readme=once(readme,'Version: 0.5.22','Version: 0.5.23','readme version')
anchor='== Version 0.5.22 – E4 Components completion ==\n'
notes="""== Version 0.5.23 – E5 Dynamic CMS foundation ==

Nyt:
- UD-051: generisk custom datatype schema builder under Hangar18 Manager → Data
- schemas understøtter text, number, bool, date og media fields med stabile keys, labels, required-flag og validering
- schema-struktur kræver manage_options; entry CRUD kræver edit_pages
- datatype-key er immutable efter oprettelse, og datatype-delete blokeres når entries stadig findes
- UD-052: generisk admin entry editor med create/read/update/delete for alle custom datatyper
- entries gemmes som privat Hangar18 custom post type med datatype-meta, samlet values-map og query-klare _h18_field_<key> meta-felter
- number/date/media valideres server-side; media skal pege på et rigtigt WordPress attachment
- media-felter bruger WordPress Media Library direkte i Data-editoren
- datamotoren er foundation for UD-053 dynamic binding og UD-055 Query Builder; Vehicle/Event/Gallery migreres senere via UD-060 presets, ikke via endnu en specialmotor
- page-editor schema forbliver 1.18; denne release ændrer ikke eksisterende side-JSON

"""+anchor
readme=once(readme,anchor,notes,'readme release anchor')

php_path.write_text(php)
js_path.write_text(js)
css_path.write_text(css)
readme_path.write_text(readme)
print('v0.5.23 dynamic data engine patch applied')
