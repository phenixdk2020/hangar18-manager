<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionSiteTemplateRepository;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateValidator;
use RuntimeException;

/**
 * I2 shadow-only Header/Footer template editor.
 *
 * Uses the same Sections tree/property names as the page editor, but stores in
 * the extracted Site Builder options. It never activates frontend rendering.
 */
final class SiteTemplateAdminController
{
    private const NONCE_ACTION = 'h18_ud_site_template';
    private const SUPPORTED_TYPES = ['container','flex','grid','text','image','menu','buttons','spacer'];
    private const FONTS = ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'];
    private const ALIGNMENTS = ['Left','Center','Right'];

    public static function register(): void
    {
        add_action('admin_post_h18_ud_create_site_template', [self::class, 'create']);
        add_action('admin_post_h18_ud_save_site_template', [self::class, 'save']);
        add_action('admin_post_h18_ud_delete_site_template', [self::class, 'delete']);
        add_action('admin_enqueue_scripts', [self::class, 'enqueueAssets']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== IntegrationAdminBootstrap::PAGE_SLUG && strpos((string) $hook, IntegrationAdminBootstrap::PAGE_SLUG) === false) {
            return;
        }

        $pluginFile = dirname(__DIR__, 2) . '/hangar18-manager.php';
        $cssPath = dirname(__DIR__, 2) . '/assets/ultimate-designer-admin.css';
        $jsPath = dirname(__DIR__, 2) . '/assets/ultimate-designer-admin.js';
        $baseVersion = class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '0';
        $cssVersion = $baseVersion . '-' . (string) (@filemtime($cssPath) ?: 0);
        $jsVersion = $baseVersion . '-' . (string) (@filemtime($jsPath) ?: 0);

        wp_enqueue_style(
            'hangar18-ultimate-designer-admin',
            plugins_url('assets/ultimate-designer-admin.css', $pluginFile),
            [],
            $cssVersion
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-admin',
            plugins_url('assets/ultimate-designer-admin.js', $pluginFile),
            [],
            $jsVersion,
            true
        );
    }

    public static function renderPanel(): void
    {
        $service = self::service();
        $headers = $service->all('header');
        $footers = $service->all('footer');
        $selectedId = isset($_GET['ud_template']) ? sanitize_key((string) wp_unslash($_GET['ud_template'])) : '';
        $selected = $selectedId !== '' ? (new WordPressOptionSiteTemplateRepository())->get($selectedId) : null;

        echo '<section class="h18-ud-builder-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I2 · Visual Header/Footer Builder</h2><p>Shadow mode: templates gemmes separat og bliver ikke vist på frontend endnu.</p></div><span class="h18-ud-shadow-badge">SHADOW · ingen cutover</span></div>';

        self::renderCreateForms();
        echo '<div class="h18-ud-template-columns">';
        self::renderTemplateList('Header templates', $headers, $selectedId);
        self::renderTemplateList('Footer templates', $footers, $selectedId);
        echo '</div>';

        if (is_array($selected)) {
            self::renderEditor($selected);
        } else {
            echo '<div class="h18-ud-empty-editor"><strong>Vælg eller opret en Header/Footer template.</strong><p>Du kan bygge den nu uden at påvirke den eksisterende hjemmeside.</p></div>';
        }
        echo '</section>';
    }

    public static function create(): void
    {
        self::guard();
        $kind = sanitize_key((string) ($_POST['template_kind'] ?? ''));
        if (!in_array($kind, ['header','footer'], true)) {
            self::redirect('', 'error', 'Ugyldig template-type.');
        }
        $name = sanitize_text_field((string) ($_POST['template_name'] ?? ''));
        if ($name === '') {
            $name = $kind === 'header' ? 'Ny header' : 'Ny footer';
        }
        try {
            $template = self::service()->create($kind, $name, self::starterSections($kind));
            self::redirect((string) $template['Id'], 'created', 'Template oprettet i shadow mode.');
        } catch (\Throwable $e) {
            self::redirect('', 'error', $e->getMessage());
        }
    }

    public static function save(): void
    {
        self::guard();
        $id = sanitize_key((string) ($_POST['template_id'] ?? ''));
        $kind = sanitize_key((string) ($_POST['template_kind'] ?? ''));
        $name = sanitize_text_field((string) ($_POST['template_name'] ?? ''));
        try {
            if ($id === '' || !in_array($kind, ['header','footer'], true)) {
                throw new RuntimeException('Template-identitet mangler.');
            }
            $sections = self::postedSections();
            self::service()->update($kind, $id, $name !== '' ? $name : $id, $sections);
            self::redirect($id, 'saved', 'Template gemt. Frontend er stadig uændret.');
        } catch (\Throwable $e) {
            self::redirect($id, 'error', $e->getMessage());
        }
    }

    public static function delete(): void
    {
        self::guard();
        $id = sanitize_key((string) ($_POST['template_id'] ?? ''));
        try {
            if ($id === '') {
                throw new RuntimeException('Template-id mangler.');
            }
            (new WordPressOptionSiteTemplateRepository())->delete($id);
            self::redirect('', 'deleted', 'Template slettet fra shadow storage.');
        } catch (\Throwable $e) {
            self::redirect($id, 'error', $e->getMessage());
        }
    }

    /** @return list<array<string,mixed>> */
    private static function postedSections(): array
    {
        $raw = isset($_POST['sections']) && is_array($_POST['sections']) ? wp_unslash($_POST['sections']) : [];
        $sections = [];
        $seen = [];
        foreach (array_slice($raw, 0, 25) as $index => $row) {
            if (!is_array($row) || !empty($row['Remove'])) {
                continue;
            }
            $key = sanitize_key((string) ($row['Key'] ?? ''));
            if ($key === '') {
                $key = 'element-' . ($index + 1);
            }
            if (isset($seen[$key])) {
                throw new RuntimeException("Element-key '{$key}' findes mere end én gang.");
            }
            $seen[$key] = true;
            $type = sanitize_key((string) ($row['Type'] ?? 'text'));
            if (!in_array($type, self::SUPPORTED_TYPES, true)) {
                $type = 'text';
            }

            $bodyFont = (string) ($row['SectionBodyFontFamily'] ?? 'Global');
            $headingFont = (string) ($row['SectionHeadingFontFamily'] ?? 'Global');
            if (!in_array($bodyFont, self::FONTS, true)) { $bodyFont = 'Global'; }
            if (!in_array($headingFont, self::FONTS, true)) { $headingFont = 'Global'; }
            $alignment = (string) ($row['DesktopAlignment'] ?? 'Left');
            if (!in_array($alignment, self::ALIGNMENTS, true)) { $alignment = 'Left'; }
            $designMode = (string) ($row['DesignMode'] ?? 'Global');
            if (!in_array($designMode, ['Global','Custom'], true)) { $designMode = 'Global'; }

            $sections[] = [
                'Key' => $key,
                'Type' => $type,
                'LayoutParentKey' => sanitize_key((string) ($row['LayoutParentKey'] ?? '')),
                'Title' => sanitize_text_field((string) ($row['Title'] ?? '')),
                'Content' => wp_kses_post((string) ($row['Content'] ?? '')),
                'DesignMode' => $designMode,
                'SectionBodyFontFamily' => $bodyFont,
                'SectionHeadingFontFamily' => $headingFont,
                'BodyFontSizePx' => self::clampInt($row['BodyFontSizePx'] ?? 0, 0, 32),
                'H1FontSizePx' => self::clampInt($row['H1FontSizePx'] ?? 0, 0, 96),
                'H2FontSizePx' => self::clampInt($row['H2FontSizePx'] ?? 0, 0, 80),
                'H3FontSizePx' => self::clampInt($row['H3FontSizePx'] ?? 0, 0, 64),
                'DesktopAlignment' => $alignment,
                'CustomBackgroundColor' => sanitize_hex_color((string) ($row['CustomBackgroundColor'] ?? '#ffffff')) ?: '#ffffff',
                'CustomTextColor' => sanitize_hex_color((string) ($row['CustomTextColor'] ?? '#30382a')) ?: '#30382a',
                'CustomHeadingColor' => sanitize_hex_color((string) ($row['CustomHeadingColor'] ?? '#30382a')) ?: '#30382a',
                'PaddingPx' => self::clampInt($row['PaddingPx'] ?? 0, 0, 120),
            ];
        }
        if ($sections === []) {
            throw new RuntimeException('En Header/Footer template skal have mindst ét element.');
        }
        return $sections;
    }

    /** @return list<array<string,mixed>> */
    private static function starterSections(string $kind): array
    {
        $defaults = [
            'Title'=>'','Content'=>'','DesignMode'=>'Global',
            'SectionBodyFontFamily'=>'Global','SectionHeadingFontFamily'=>'Global',
            'BodyFontSizePx'=>0,'H1FontSizePx'=>0,'H2FontSizePx'=>0,'H3FontSizePx'=>0,
            'DesktopAlignment'=>'Left','CustomBackgroundColor'=>'#ffffff',
            'CustomTextColor'=>'#30382a','CustomHeadingColor'=>'#30382a','PaddingPx'=>0,
        ];
        if ($kind === 'header') {
            return [
                array_merge($defaults,['Key'=>'header-root','Type'=>'flex','LayoutParentKey'=>'']),
                array_merge($defaults,['Key'=>'brand','Type'=>'text','LayoutParentKey'=>'header-root','Content'=>'Hangar18']),
                array_merge($defaults,['Key'=>'navigation','Type'=>'menu','LayoutParentKey'=>'header-root']),
            ];
        }
        return [
            array_merge($defaults,['Key'=>'footer-root','Type'=>'container','LayoutParentKey'=>'']),
            array_merge($defaults,['Key'=>'footer-text','Type'=>'text','LayoutParentKey'=>'footer-root','Content'=>'Aalborg Kaserners Veteran Panser og Køretøjsforening']),
        ];
    }

    /** @param array<string,array<string,mixed>> $templates */
    private static function renderTemplateList(string $title, array $templates, string $selectedId): void
    {
        echo '<div class="h18-ud-template-list"><h3>' . esc_html($title) . '</h3>';
        if ($templates === []) {
            echo '<p class="description">Ingen templates endnu.</p>';
        }
        foreach ($templates as $template) {
            $id = (string) ($template['Id'] ?? '');
            $url = add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_template'=>$id], admin_url('admin.php'));
            echo '<a class="h18-ud-template-link' . ($selectedId === $id ? ' is-active' : '') . '" href="' . esc_url($url) . '"><strong>' . esc_html((string) ($template['Name'] ?? $id)) . '</strong><small>' . esc_html($id) . ' · rev ' . (int) ($template['Revision'] ?? 1) . '</small></a>';
        }
        echo '</div>';
    }

    private static function renderCreateForms(): void
    {
        echo '<div class="h18-ud-create-template-row">';
        foreach (['header'=>'Ny Header template','footer'=>'Ny Footer template'] as $kind => $label) {
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
            wp_nonce_field(self::NONCE_ACTION);
            echo '<input type="hidden" name="action" value="h18_ud_create_site_template"><input type="hidden" name="template_kind" value="' . esc_attr($kind) . '">';
            echo '<input type="text" name="template_name" placeholder="Navn (valgfri)" aria-label="Template navn">';
            echo '<button class="button" type="submit">' . esc_html($label) . '</button></form>';
        }
        echo '</div>';
    }

    /** @param array<string,mixed> $template */
    private static function renderEditor(array $template): void
    {
        $id = (string) $template['Id'];
        $kind = (string) $template['Kind'];
        $sections = is_array($template['Sections'] ?? null) ? array_values($template['Sections']) : [];

        echo '<form class="h18-ud-template-editor" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_save_site_template"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><input type="hidden" name="template_kind" value="' . esc_attr($kind) . '">';
        echo '<div class="h18-ud-template-toolbar"><div><strong>' . esc_html(strtoupper($kind)) . ' · ' . esc_html($id) . '</strong><small>Revision ' . (int) ($template['Revision'] ?? 1) . '</small></div><label>Navn <input type="text" name="template_name" value="' . esc_attr((string) ($template['Name'] ?? '')) . '"></label><button class="button button-primary" type="submit">Gem template</button></div>';

        echo '<div class="h18-ud-template-workspace"><div class="h18-ud-template-elements">';
        echo '<div class="h18-ud-element-list-head"><div><h3>Elementer</h3><p class="description">Træk i håndtaget eller brug ↑/↓. Parent key styrer nesting.</p></div><button type="button" class="button" id="h18-ud-add-template-element">+ Tilføj element</button></div>';
        echo '<div id="h18-ud-template-element-list" data-next-index="' . (int) count($sections) . '" data-supported-types="' . esc_attr(wp_json_encode(self::SUPPORTED_TYPES)) . '">';
        foreach ($sections as $index => $section) {
            self::renderSectionRow($index, is_array($section) ? $section : []);
        }
        echo '</div></div>';
        echo '<aside class="h18-ud-template-preview"><h3>Live preview</h3><p class="description">Admin-preview – ikke offentlig frontend.</p><div id="h18-ud-site-template-preview" aria-live="polite"></div></aside></div>';
        echo '</form>';

        echo '<form class="h18-ud-delete-template" method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Slet denne shadow-template?\');">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_delete_site_template"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><button type="submit" class="button-link-delete">Slet template</button></form>';
    }

    /** @param array<string,mixed> $section */
    private static function renderSectionRow(int $index, array $section): void
    {
        $key = (string) ($section['Key'] ?? 'element-' . ($index + 1));
        $type = (string) ($section['Type'] ?? 'text');
        echo '<article class="h18-ud-template-element" data-index="' . $index . '">';
        echo '<div class="h18-ud-template-element-head"><span class="dashicons dashicons-move h18-ud-drag-handle" aria-hidden="true"></span><strong class="h18-ud-element-summary">' . esc_html($key . ' · ' . $type) . '</strong><span class="h18-ud-move-controls"><button type="button" class="button-link h18-ud-move-up" aria-label="Flyt element op">↑</button><button type="button" class="button-link h18-ud-move-down" aria-label="Flyt element ned">↓</button></span><button type="button" class="button-link-delete h18-ud-remove-template-element">Fjern</button></div>';
        echo '<div class="h18-ud-template-element-grid">';
        self::textInput($index,'Key','Key',$key);
        self::selectInput($index,'Type','Type',$type,self::SUPPORTED_TYPES,'h18-ud-section-type');
        self::textInput($index,'LayoutParentKey','Parent key',(string) ($section['LayoutParentKey'] ?? ''));
        self::textInput($index,'Title','Overskrift (valgfri)',(string) ($section['Title'] ?? ''));
        echo '<label class="is-wide">Tekst/indhold<textarea rows="4" name="sections['.$index.'][Content]" class="h18-ud-section-content">'.esc_textarea((string) ($section['Content'] ?? '')).'</textarea></label>';
        self::renderStyleControls($index, $section);
        echo '<input type="hidden" name="sections['.$index.'][Remove]" value="0" class="h18-ud-section-remove">';
        echo '</div></article>';
    }

    /** @param array<string,mixed> $section */
    private static function renderStyleControls(int $index, array $section): void
    {
        echo '<div class="h18-ud-element-style-controls is-wide"><h4>Typografi og design</h4><div class="h18-ud-style-grid">';
        self::selectInput($index,'DesignMode','Design',(string) ($section['DesignMode'] ?? 'Global'),['Global','Custom'],'',true);
        self::selectInput($index,'SectionBodyFontFamily','Brødtekst-font',(string) ($section['SectionBodyFontFamily'] ?? 'Global'),self::FONTS,'',true);
        self::selectInput($index,'SectionHeadingFontFamily','Overskrift-font',(string) ($section['SectionHeadingFontFamily'] ?? 'Global'),self::FONTS,'',true);
        self::numberInput($index,'BodyFontSizePx','Brødtekst (px)',(int) ($section['BodyFontSizePx'] ?? 0),0,32,'0 = global');
        self::numberInput($index,'H1FontSizePx','H1 (px)',(int) ($section['H1FontSizePx'] ?? 0),0,96,'0 = global');
        self::numberInput($index,'H2FontSizePx','H2 (px)',(int) ($section['H2FontSizePx'] ?? 0),0,80,'0 = global');
        self::numberInput($index,'H3FontSizePx','H3 (px)',(int) ($section['H3FontSizePx'] ?? 0),0,64,'0 = global');
        self::selectInput($index,'DesktopAlignment','Justering',(string) ($section['DesktopAlignment'] ?? 'Left'),self::ALIGNMENTS,'',true);
        self::colorInput($index,'CustomBackgroundColor','Baggrund',(string) ($section['CustomBackgroundColor'] ?? '#ffffff'));
        self::colorInput($index,'CustomTextColor','Tekst',(string) ($section['CustomTextColor'] ?? '#30382a'));
        self::colorInput($index,'CustomHeadingColor','Overskrift',(string) ($section['CustomHeadingColor'] ?? '#30382a'));
        self::numberInput($index,'PaddingPx','Indvendig afstand (px)',(int) ($section['PaddingPx'] ?? 0),0,120,'');
        echo '</div></div>';
    }

    /** @param list<string> $options */
    private static function selectInput(int $index, string $field, string $label, string $value, array $options, string $class = '', bool $styleField = false): void
    {
        $data = $styleField ? ' data-style-field="' . esc_attr($field) . '"' : '';
        echo '<label>' . esc_html($label) . '<select name="sections['.$index.']['.esc_attr($field).']" class="'.esc_attr($class).'"'.$data.'>';
        foreach ($options as $option) {
            $display = $option === 'Global' && strpos($field,'FontFamily') !== false ? 'Global font' : $option;
            echo '<option value="'.esc_attr($option).'"'.selected($value,$option,false).'>'.esc_html($display).'</option>';
        }
        echo '</select></label>';
    }

    private static function textInput(int $index, string $field, string $label, string $value): void
    {
        echo '<label>'.esc_html($label).'<input type="text" name="sections['.$index.']['.esc_attr($field).']" value="'.esc_attr($value).'"></label>';
    }

    private static function numberInput(int $index, string $field, string $label, int $value, int $min, int $max, string $help): void
    {
        echo '<label>'.esc_html($label).'<input data-style-field="'.esc_attr($field).'" type="number" min="'.$min.'" max="'.$max.'" name="sections['.$index.']['.esc_attr($field).']" value="'.$value.'">';
        if ($help !== '') { echo '<small>'.esc_html($help).'</small>'; }
        echo '</label>';
    }

    private static function colorInput(int $index, string $field, string $label, string $value): void
    {
        echo '<label>'.esc_html($label).'<input data-style-field="'.esc_attr($field).'" type="color" name="sections['.$index.']['.esc_attr($field).']" value="'.esc_attr($value).'"></label>';
    }

    private static function service(): SiteTemplateService
    {
        return new SiteTemplateService(
            new WordPressOptionSiteTemplateRepository(),
            new SiteTemplateValidator(new PageSchemaValidator())
        );
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Du har ikke rettigheder til denne handling.', 'hangar18-manager'));
        }
        check_admin_referer(self::NONCE_ACTION);
    }

    private static function clampInt($value, int $min, int $max): int
    {
        return max($min, min($max, (int) $value));
    }

    private static function redirect(string $templateId, string $status, string $message): void
    {
        $args = ['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>$message];
        if ($templateId !== '') {
            $args['ud_template'] = $templateId;
        }
        wp_safe_redirect(add_query_arg($args, admin_url('admin.php')));
        exit;
    }
}
