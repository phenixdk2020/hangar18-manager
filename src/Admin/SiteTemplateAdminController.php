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
 * Stores data in the extracted Site Builder options and never activates frontend rendering.
 */
final class SiteTemplateAdminController
{
    private const NONCE_ACTION = 'h18_ud_site_template';
    private const SUPPORTED_TYPES = ['container','flex','grid','text','image','menu','buttons','spacer'];

    public static function register(): void
    {
        add_action('admin_post_h18_ud_create_site_template', [self::class, 'create']);
        add_action('admin_post_h18_ud_save_site_template', [self::class, 'save']);
        add_action('admin_post_h18_ud_delete_site_template', [self::class, 'delete']);
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
            $sections[] = [
                'Key' => $key,
                'Type' => $type,
                'LayoutParentKey' => sanitize_key((string) ($row['LayoutParentKey'] ?? '')),
                'Title' => sanitize_text_field((string) ($row['Title'] ?? '')),
                'Content' => wp_kses_post((string) ($row['Content'] ?? '')),
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
        if ($kind === 'header') {
            return [
                ['Key'=>'header-root','Type'=>'flex','LayoutParentKey'=>'','Title'=>'','Content'=>''],
                ['Key'=>'brand','Type'=>'text','LayoutParentKey'=>'header-root','Title'=>'','Content'=>'Hangar18'],
                ['Key'=>'navigation','Type'=>'menu','LayoutParentKey'=>'header-root','Title'=>'','Content'=>''],
            ];
        }
        return [
            ['Key'=>'footer-root','Type'=>'container','LayoutParentKey'=>'','Title'=>'','Content'=>''],
            ['Key'=>'footer-text','Type'=>'text','LayoutParentKey'=>'footer-root','Title'=>'','Content'=>'Aalborg Kaserners Veteran Panser og Køretøjsforening'],
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
        echo '<div class="h18-ud-element-list-head"><h3>Elementer</h3><button type="button" class="button" id="h18-ud-add-template-element">+ Tilføj element</button></div>';
        echo '<div id="h18-ud-template-element-list">';
        foreach ($sections as $index => $section) {
            self::renderSectionRow($index, is_array($section) ? $section : []);
        }
        echo '</div></div>';
        echo '<aside class="h18-ud-template-preview"><h3>Live preview</h3><p class="description">Admin-preview – ikke offentlig frontend.</p><div id="h18-ud-site-template-preview"></div></aside></div>';
        echo '</form>';

        echo '<form class="h18-ud-delete-template" method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Slet denne shadow-template?\');">';
        wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_delete_site_template"><input type="hidden" name="template_id" value="' . esc_attr($id) . '"><button type="submit" class="button-link-delete">Slet template</button></form>';

        self::renderClientScript(count($sections));
    }

    /** @param array<string,mixed> $section */
    private static function renderSectionRow(int $index, array $section): void
    {
        $key = (string) ($section['Key'] ?? 'element-' . ($index + 1));
        $type = (string) ($section['Type'] ?? 'text');
        echo '<article class="h18-ud-template-element" data-index="' . $index . '">';
        echo '<div class="h18-ud-template-element-head"><span class="dashicons dashicons-move"></span><strong class="h18-ud-element-summary">' . esc_html($key . ' · ' . $type) . '</strong><button type="button" class="button-link-delete h18-ud-remove-template-element">Fjern</button></div>';
        echo '<div class="h18-ud-template-element-grid">';
        self::input($index,'Key','Key',$key);
        echo '<label>Type<select name="sections['.$index.'][Type]" class="h18-ud-section-type">';
        foreach (self::SUPPORTED_TYPES as $candidate) {
            echo '<option value="'.esc_attr($candidate).'"'.selected($type,$candidate,false).'>'.esc_html($candidate).'</option>';
        }
        echo '</select></label>';
        self::input($index,'LayoutParentKey','Parent key',(string) ($section['LayoutParentKey'] ?? ''));
        self::input($index,'Title','Overskrift (valgfri)',(string) ($section['Title'] ?? ''));
        echo '<label class="is-wide">Tekst/indhold<textarea rows="4" name="sections['.$index.'][Content]" class="h18-ud-section-content">'.esc_textarea((string) ($section['Content'] ?? '')).'</textarea></label>';
        echo '<input type="hidden" name="sections['.$index.'][Remove]" value="0" class="h18-ud-section-remove">';
        echo '</div></article>';
    }

    private static function input(int $index, string $field, string $label, string $value): void
    {
        echo '<label>'.$label.'<input type="text" name="sections['.$index.']['.esc_attr($field).']" value="'.esc_attr($value).'" class="h18-ud-section-'.esc_attr(strtolower($field)).'"></label>';
    }

    private static function renderClientScript(int $nextIndex): void
    {
        $types = wp_json_encode(self::SUPPORTED_TYPES);
        echo '<script>(function(){const list=document.getElementById("h18-ud-template-element-list"),preview=document.getElementById("h18-ud-site-template-preview"),add=document.getElementById("h18-ud-add-template-element");if(!list||!preview)return;let next='.(int)$nextIndex.',types='.$types.';function esc(v){const d=document.createElement("div");d.textContent=v||"";return d.innerHTML}function rows(){return Array.from(list.querySelectorAll(".h18-ud-template-element")).filter(r=>!r.classList.contains("is-removed"))}function render(){preview.innerHTML="";rows().forEach(r=>{const key=r.querySelector("[name*=\"[Key]\"]")?.value||"element",type=r.querySelector(".h18-ud-section-type")?.value||"text",title=r.querySelector("[name*=\"[Title]\"]")?.value||"",content=r.querySelector(".h18-ud-section-content")?.value||"";const box=document.createElement(type==="container"||type==="flex"||type==="grid"?"section":"div");box.className="h18-ud-preview-node h18-ud-preview-"+type;box.dataset.key=key;box.innerHTML=(title?"<strong>"+esc(title)+"</strong>":"")+(content?"<div>"+esc(content).replace(/\\n/g,"<br>")+"</div>":"")+(type==="menu"?"<div class=\"h18-ud-preview-menu\">Hjem · Om · Kontakt</div>":"")+(type==="image"?"<div class=\"h18-ud-preview-image\">Billede</div>":"");preview.appendChild(box);const summary=r.querySelector(".h18-ud-element-summary");if(summary)summary.textContent=key+" · "+type})}function html(i){const options=types.map(t=>"<option value=\""+t+"\">"+t+"</option>").join("");return `<article class="h18-ud-template-element" data-index="${i}"><div class="h18-ud-template-element-head"><span class="dashicons dashicons-move"></span><strong class="h18-ud-element-summary">element-${i+1} · text</strong><button type="button" class="button-link-delete h18-ud-remove-template-element">Fjern</button></div><div class="h18-ud-template-element-grid"><label>Key<input type="text" name="sections[${i}][Key]" value="element-${i+1}"></label><label>Type<select name="sections[${i}][Type]" class="h18-ud-section-type">${options}</select></label><label>Parent key<input type="text" name="sections[${i}][LayoutParentKey]"></label><label>Overskrift (valgfri)<input type="text" name="sections[${i}][Title]"></label><label class="is-wide">Tekst/indhold<textarea rows="4" name="sections[${i}][Content]" class="h18-ud-section-content"></textarea></label><input type="hidden" name="sections[${i}][Remove]" value="0" class="h18-ud-section-remove"></div></article>`}add?.addEventListener("click",()=>{list.insertAdjacentHTML("beforeend",html(next++));render()});list.addEventListener("click",e=>{const b=e.target.closest(".h18-ud-remove-template-element");if(!b)return;const r=b.closest(".h18-ud-template-element");r.classList.add("is-removed");r.querySelector(".h18-ud-section-remove").value="1";render()});list.addEventListener("input",render);list.addEventListener("change",render);render()})();</script>';
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
