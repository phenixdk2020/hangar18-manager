from pathlib import Path


def once(text,old,new,label):
    c=text.count(old)
    if c!=1: raise SystemExit(f'{label}: expected 1 anchor, found {c}')
    return text.replace(old,new,1)

php_path=Path('hangar18-manager.php');js_path=Path('assets/admin.js');css_path=Path('assets/admin.css');readme_path=Path('readme.txt')
php=php_path.read_text();js=js_path.read_text();css=css_path.read_text();readme=readme_path.read_text()

php=once(php,' * Version: 0.5.21',' * Version: 0.5.22','plugin header')
php=once(php,"    const VERSION = '0.5.21';","    const VERSION = '0.5.22';",'plugin const')
php=once(php,"    const PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1';\n","    const PAGE_COMPONENTS_OPTION      = 'hangar18_manager_page_components_v1';\n    const PAGE_TEMPLATES_OPTION       = 'hangar18_manager_page_templates_v1';\n",'page template option')

php=once(php,
"""        add_action('wp_ajax_h18_save_page_component', [$this, 'ajax_save_page_component']);
        add_action('wp_ajax_h18_delete_page_component', [$this, 'ajax_delete_page_component']);
""",
"""        add_action('wp_ajax_h18_save_page_component', [$this, 'ajax_save_page_component']);
        add_action('wp_ajax_h18_delete_page_component', [$this, 'ajax_delete_page_component']);
        add_action('wp_ajax_h18_save_page_component_variant', [$this, 'ajax_save_page_component_variant']);
        add_action('wp_ajax_h18_delete_page_component_variant', [$this, 'ajax_delete_page_component_variant']);
        add_action('wp_ajax_h18_save_page_template', [$this, 'ajax_save_page_template']);
        add_action('wp_ajax_h18_delete_page_template', [$this, 'ajax_delete_page_template']);
        add_action('wp_ajax_h18_create_page_from_template', [$this, 'ajax_create_page_from_template']);
""",'v0522 ajax actions')

php=once(php,
"""            'pageComponentNonce'   => wp_create_nonce('h18_page_components_v0521'),
""",
"""            'pageComponentNonce'   => wp_create_nonce('h18_page_components_v0521'),
            'pageTemplateNonce'    => wp_create_nonce('h18_page_templates_v0522'),
""",'template nonce')

# Template-created managed pages become editable alongside the four fixed pages.
old="""    private function editable_page_definitions() {
        return [
            self::HOME_SLUG => 'Hjem',
            'om-foreningen' => 'Om foreningen',
            'bliv-medlem'   => 'Bliv medlem',
            'kontakt'       => 'Kontakt',
        ];
    }
"""
new="""    private function editable_page_definitions() {
        $definitions = [
            self::HOME_SLUG => 'Hjem',
            'om-foreningen' => 'Om foreningen',
            'bliv-medlem'   => 'Bliv medlem',
            'kontakt'       => 'Kontakt',
        ];
        $managed = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish','draft','private'],
            'posts_per_page' => -1,
            'meta_key' => '_h18_page_editor_managed',
            'meta_value' => '1',
            'orderby' => 'title',
            'order' => 'ASC',
        ]);
        foreach ($managed as $page) {
            if (!$page instanceof WP_Post || $page->post_name === '') { continue; }
            if (!isset($definitions[$page->post_name])) { $definitions[$page->post_name] = $page->post_title; }
        }
        return $definitions;
    }
"""
php=once(php,old,new,'dynamic managed pages')

# Component instance variant selection is persisted.
php=once(php,
"""            'ComponentId'           => '',
            'ComponentRevision'     => 0,
            'ComponentOverrides'    => [],
""",
"""            'ComponentId'           => '',
            'ComponentRevision'     => 0,
            'ComponentVariant'      => '',
            'ComponentOverrides'    => [],
""",'component variant default')
php=once(php,
"""        $component_id = sanitize_key((string) ($raw['ComponentId'] ?? ''));
        $component_revision = max(0, (int) ($raw['ComponentRevision'] ?? 0));
""",
"""        $component_id = sanitize_key((string) ($raw['ComponentId'] ?? ''));
        $component_revision = max(0, (int) ($raw['ComponentRevision'] ?? 0));
        $component_variant = sanitize_key((string) ($raw['ComponentVariant'] ?? ''));
""",'component variant normalize prelude')
php=once(php,
"""            'ComponentId'           => $component_id,
            'ComponentRevision'     => $component_revision,
            'ComponentOverrides'    => $component_overrides,
""",
"""            'ComponentId'           => $component_id,
            'ComponentRevision'     => $component_revision,
            'ComponentVariant'      => $component_variant,
            'ComponentOverrides'    => $component_overrides,
""",'component variant normalized')

if php.count("'Version'        => '1.17'") != 3: raise SystemExit('Expected 3 page schema 1.17 payloads')
php=php.replace("'Version'        => '1.17'","'Version'        => '1.18'")
php=php.replace("'Version' => '1.17',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,","'Version' => '1.18',\n                    'Saved'   => gmdate('c'),\n                    'Pages'   => $store,")
php=php.replace("'Version' => '1.17',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,","'Version' => '1.18',\n                'Saved'   => gmdate('c'),\n                'Pages'   => $store,")

# Upgrade old one-section presets into subtree-capable non-linked patterns while retaining backward compatibility.
start=php.index('    private function get_page_presets() {')
end=php.index('    public function ajax_delete_page_preset()',start)
patterns=r'''    private function normalize_page_pattern_sections(array $raw_sections) {
        $raw_sections = array_slice($raw_sections, 0, 25);
        if (!$raw_sections) { throw new RuntimeException('Pattern skal indeholde mindst ét element.'); }
        foreach ($raw_sections as $raw_section) {
            if (!is_array($raw_section)) { continue; }
            $type = sanitize_key((string) ($raw_section['Type'] ?? 'text'));
            if (in_array($type, ['legacy','component'], true)) { throw new RuntimeException('Legacy og linked components kan ikke gemmes inde i et ikke-linked pattern.'); }
        }
        $data = $this->normalize_page_editor_data(['Version'=>'1.18','PageSlug'=>self::HOME_SLUG,'PageTitle'=>'Pattern','ContentVersion'=>0,'Sections'=>$raw_sections], null);
        $sections = array_values((array) $data['Sections']);
        $roots = array_values(array_filter($sections, static function($section){ return sanitize_key((string) ($section['LayoutParentKey'] ?? '')) === ''; }));
        if (count($roots) !== 1) { throw new RuntimeException('Et pattern skal have præcis ét root-element.'); }
        foreach ($sections as &$section) {
            $section['NavigatorLabel']=''; $section['NavigatorLocked']=false; $section['ComponentId']=''; $section['ComponentRevision']=0; $section['ComponentVariant']=''; $section['ComponentOverrides']=[];
        }
        unset($section);
        return $sections;
    }

    private function get_page_presets() {
        $stored = get_option(self::PAGE_PRESETS_OPTION, []);
        if (!is_array($stored)) { return []; }
        $presets=[];
        foreach (array_slice($stored,0,50,true) as $id=>$entry) {
            if (!is_array($entry)) { continue; }
            $raw_sections = isset($entry['Sections']) && is_array($entry['Sections']) ? $entry['Sections'] : (isset($entry['Section']) && is_array($entry['Section']) ? [$entry['Section']] : []);
            if (!$raw_sections) { continue; }
            $preset_id=sanitize_key((string)($entry['Id']??$id)); $name=sanitize_text_field((string)($entry['Name']??'Pattern'));
            if($preset_id===''||$name==='')continue;
            try{$sections=$this->normalize_page_pattern_sections($raw_sections);}catch(Throwable $e){$this->log('WARN','PAGE_PATTERN_INVALID',"{$preset_id}: ".$e->getMessage());continue;}
            $presets[$preset_id]=['Id'=>$preset_id,'Name'=>$name,'UpdatedUtc'=>sanitize_text_field((string)($entry['UpdatedUtc']??'')),'Sections'=>$sections,'Section'=>$sections[0]];
        }
        return $presets;
    }

    public function ajax_save_page_preset() {
        if (!current_user_can('edit_pages')) { wp_send_json_error(['message'=>'Du har ikke rettigheder til at gemme patterns.'],403); }
        check_ajax_referer('h18_page_presets_v051','nonce');
        $name=sanitize_text_field((string)wp_unslash($_POST['name']??'')); $name=function_exists('mb_substr')?mb_substr($name,0,80):substr($name,0,80);
        if($name==='')wp_send_json_error(['message'=>'Pattern skal have et navn.'],400);
        $sections_json=(string)wp_unslash($_POST['sections']??''); $section_json=(string)wp_unslash($_POST['section']??'');
        $json=$sections_json!==''?$sections_json:$section_json;
        if($json===''||strlen($json)>350000)wp_send_json_error(['message'=>'Patterndata mangler eller er for stor.'],400);
        $decoded=json_decode($json,true); if(!is_array($decoded)||json_last_error()!==JSON_ERROR_NONE)wp_send_json_error(['message'=>'Patterndata er ikke gyldig JSON.'],400);
        if($sections_json==='')$decoded=[$decoded];
        try{$sections=$this->normalize_page_pattern_sections($decoded);}catch(Throwable $e){wp_send_json_error(['message'=>$e->getMessage()],400);}
        $presets=$this->get_page_presets(); $preset_id=sanitize_key((string)wp_unslash($_POST['preset_id']??''));
        if($preset_id===''||!isset($presets[$preset_id]))$preset_id='preset-'.sanitize_key(wp_generate_uuid4());
        $entry=['Id'=>$preset_id,'Name'=>$name,'UpdatedUtc'=>gmdate('c'),'Sections'=>$sections,'Section'=>$sections[0]];
        $presets[$preset_id]=$entry; if(count($presets)>50)$presets=array_slice($presets,-50,null,true);
        update_option(self::PAGE_PRESETS_OPTION,$presets,false);
        $this->log('INFO','PAGE_PATTERN_SAVED',"Pattern '{$name}' gemt som {$preset_id} med ".count($sections).' element(er).');
        wp_send_json_success(['preset'=>$entry]);
    }

'''
php=php[:start]+patterns+php[end:]
php=php.replace("Du har ikke rettigheder til at slette komponenter.","Du har ikke rettigheder til at slette patterns.",1)
php=php.replace("Komponenten blev ikke fundet.","Pattern blev ikke fundet.",1)
php=php.replace("Genbrugelig komponent '{$name}' ({$preset_id}) blev slettet.","Pattern '{$name}' ({$preset_id}) blev slettet.",1)

# Page templates are non-linked snapshots with fresh keys on instantiation.
template_methods=r'''

    private function normalize_page_template_sections(array $raw_sections) {
        $raw_sections=array_slice($raw_sections,0,25); if(!$raw_sections)throw new RuntimeException('Sidetemplaten skal indeholde mindst ét element.');
        foreach($raw_sections as $raw_section){if(!is_array($raw_section))continue;$type=sanitize_key((string)($raw_section['Type']??'text'));if(in_array($type,['legacy','component'],true))throw new RuntimeException('Page Templates kan ikke indeholde legacy eller linked components; templaten skal være en selvstændig kopi.');}
        $data=$this->normalize_page_editor_data(['Version'=>'1.18','PageSlug'=>self::HOME_SLUG,'PageTitle'=>'Page Template','ContentVersion'=>0,'Sections'=>$raw_sections],null);
        $sections=array_values((array)$data['Sections']);
        foreach($sections as &$section){$section['ComponentId']='';$section['ComponentRevision']=0;$section['ComponentVariant']='';$section['ComponentOverrides']=[];}unset($section);
        return $sections;
    }

    private function get_page_templates() {
        $stored=get_option(self::PAGE_TEMPLATES_OPTION,[]);if(!is_array($stored))return[];$templates=[];
        foreach(array_slice($stored,0,30,true) as $id=>$entry){if(!is_array($entry)||empty($entry['Sections'])||!is_array($entry['Sections']))continue;$template_id=sanitize_key((string)($entry['Id']??$id));$name=sanitize_text_field((string)($entry['Name']??'Page Template'));if($template_id===''||$name==='')continue;try{$sections=$this->normalize_page_template_sections($entry['Sections']);}catch(Throwable $e){continue;}$templates[$template_id]=['Id'=>$template_id,'Name'=>$name,'PageTitle'=>sanitize_text_field((string)($entry['PageTitle']??$name)),'UpdatedUtc'=>sanitize_text_field((string)($entry['UpdatedUtc']??'')),'Sections'=>$sections];}
        return $templates;
    }

    private function get_page_template_usage($template_id) {
        $template_id=sanitize_key((string)$template_id);if($template_id==='')return[];$posts=get_posts(['post_type'=>'page','post_status'=>['publish','draft','private'],'posts_per_page'=>-1,'meta_key'=>'_h18_page_template_origin','meta_value'=>$template_id,'orderby'=>'title','order'=>'ASC']);$usage=[];
        foreach($posts as $page){if($page instanceof WP_Post)$usage[]=['PageId'=>(int)$page->ID,'PageSlug'=>(string)$page->post_name,'PageTitle'=>(string)$page->post_title];}
        return $usage;
    }

    private function get_page_templates_for_editor() {$templates=$this->get_page_templates();foreach($templates as $id=>&$template){$template['Usage']=$this->get_page_template_usage($id);$template['UsageCount']=count($template['Usage']);}unset($template);return$templates;}

    public function ajax_save_page_template() {
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at gemme Page Templates.'],403);check_ajax_referer('h18_page_templates_v0522','nonce');
        $name=sanitize_text_field((string)wp_unslash($_POST['name']??''));$page_title=sanitize_text_field((string)wp_unslash($_POST['page_title']??$name));$json=(string)wp_unslash($_POST['sections']??'');if($name===''||$json===''||strlen($json)>450000)wp_send_json_error(['message'=>'Template-navn eller indhold mangler.'],400);$raw=json_decode($json,true);if(!is_array($raw)||json_last_error()!==JSON_ERROR_NONE)wp_send_json_error(['message'=>'Template-data er ikke gyldig JSON.'],400);
        try{$sections=$this->normalize_page_template_sections($raw);}catch(Throwable $e){wp_send_json_error(['message'=>$e->getMessage()],400);}
        $templates=$this->get_page_templates();$id=sanitize_key((string)wp_unslash($_POST['template_id']??''));if($id===''||!isset($templates[$id]))$id='template-'.sanitize_key(wp_generate_uuid4());$entry=['Id'=>$id,'Name'=>$name,'PageTitle'=>$page_title!==''?$page_title:$name,'UpdatedUtc'=>gmdate('c'),'Sections'=>$sections];$templates[$id]=$entry;if(count($templates)>30)wp_send_json_error(['message'=>'Der kan højst gemmes 30 Page Templates.'],400);update_option(self::PAGE_TEMPLATES_OPTION,$templates,false);$entry['Usage']=$this->get_page_template_usage($id);$entry['UsageCount']=count($entry['Usage']);wp_send_json_success(['template'=>$entry]);
    }

    public function ajax_delete_page_template() {
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at slette Page Templates.'],403);check_ajax_referer('h18_page_templates_v0522','nonce');$id=sanitize_key((string)wp_unslash($_POST['template_id']??''));$templates=$this->get_page_templates();if($id===''||!isset($templates[$id]))wp_send_json_error(['message'=>'Page Template blev ikke fundet.'],404);unset($templates[$id]);update_option(self::PAGE_TEMPLATES_OPTION,$templates,false);wp_send_json_success(['template_id'=>$id]);
    }

    private function instantiate_page_template_sections(array $sections) {
        $map=[];foreach($sections as $section){$old=sanitize_key((string)($section['Key']??''));if($old!=='')$map[$old]='sektion-'.substr(md5(wp_generate_uuid4()),0,12);}$result=[];
        foreach($sections as $index=>$section){$old=sanitize_key((string)($section['Key']??''));$parent=sanitize_key((string)($section['LayoutParentKey']??''));$copy=$section;$copy['Key']=$map[$old]??('sektion-'.substr(md5(wp_generate_uuid4()),0,12));$copy['LayoutParentKey']=$parent!==''&&isset($map[$parent])?$map[$parent]:'';$copy['Order']=($index+1)*10;$copy['ComponentId']='';$copy['ComponentRevision']=0;$copy['ComponentVariant']='';$copy['ComponentOverrides']=[];$result[]=$copy;}
        return$result;
    }

    public function ajax_create_page_from_template() {
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at oprette sider.'],403);check_ajax_referer('h18_page_templates_v0522','nonce');$template_id=sanitize_key((string)wp_unslash($_POST['template_id']??''));$title=sanitize_text_field((string)wp_unslash($_POST['page_title']??''));$slug=sanitize_title((string)wp_unslash($_POST['page_slug']??''));$templates=$this->get_page_templates();if(!isset($templates[$template_id]))wp_send_json_error(['message'=>'Page Template blev ikke fundet.'],404);if($title===''||$slug==='')wp_send_json_error(['message'=>'Ny side skal have titel og slug.'],400);if(get_page_by_path($slug,OBJECT,'page'))wp_send_json_error(['message'=>'Der findes allerede en side med denne slug.'],409);
        $post_id=wp_insert_post(['post_type'=>'page','post_status'=>'draft','post_title'=>$title,'post_name'=>$slug,'post_content'=>''],true);if(is_wp_error($post_id))wp_send_json_error(['message'=>$post_id->get_error_message()],400);$page=get_post($post_id);
        try{$sections=$this->instantiate_page_template_sections($templates[$template_id]['Sections']);$data=$this->normalize_page_editor_data(['Version'=>'1.18','PageSlug'=>$slug,'PageTitle'=>$title,'ContentVersion'=>1,'Sections'=>$sections],$page);update_post_meta($post_id,'_h18_page_editor_managed','1');update_post_meta($post_id,'_h18_page_template_origin',$template_id);$this->save_page_editor_data($slug,$data);$result=wp_update_post(['ID'=>$post_id,'page_template'=>'default','post_content'=>$this->wrap_with_shell($this->build_page_editor_core($slug,$data),$post_id)],true);if(is_wp_error($result))throw new RuntimeException($result->get_error_message());wp_send_json_success(['page_id'=>$post_id,'page_slug'=>$slug,'manager_url'=>admin_url('admin.php?page=hangar18-pages&page_slug='.rawurlencode($slug)),'edit_url'=>get_edit_post_link($post_id,'raw')]);}
        catch(Throwable $e){wp_delete_post($post_id,true);wp_send_json_error(['message'=>$e->getMessage()],400);}
    }
'''
php=once(php,"\n\n\n    private function page_component_allowed_input_fields() {",template_methods+"\n\n    private function page_component_allowed_input_fields() {",'page template methods')

# Component variants normalize only exposed input IDs.
variant_helpers=r'''

    private function normalize_page_component_variants($raw_variants, array $inputs, array $sections) {
        if(!is_array($raw_variants))return[];$input_map=[];foreach($inputs as $input){$id=sanitize_key((string)($input['InputId']??''));if($id!=='')$input_map[$id]=$input;}$section_map=[];foreach($sections as $section)$section_map[(string)$section['Key']]=$section;$variants=[];
        foreach(array_slice($raw_variants,0,12,true) as $id=>$variant){if(!is_array($variant))continue;$variant_id=sanitize_key((string)($variant['Id']??$id));$name=sanitize_text_field((string)($variant['Name']??'Variant'));if($variant_id===''||$name==='')continue;$values=[];$raw_values=isset($variant['Values'])&&is_array($variant['Values'])?$variant['Values']:[];foreach($raw_values as $input_id=>$value){$input_id=sanitize_key((string)$input_id);if(!isset($input_map[$input_id]))continue;$input=$input_map[$input_id];$field=(string)$input['Field'];$sanitized=$this->sanitize_page_component_override($field,$value);$section=$section_map[(string)$input['SectionKey']]??[];$base=$this->page_component_input_default($section,$field);if((string)$sanitized===(string)$base)continue;$values[$input_id]=$sanitized;}$variants[$variant_id]=['Id'=>$variant_id,'Name'=>$name,'Values'=>$values];}
        return$variants;
    }
'''
php=once(php,"\n    private function get_page_components() {",variant_helpers+"\n    private function get_page_components() {",'variant normalize helper')

# get_page_components now includes normalized Variants.
old="""            $components[$component_id] = [
                'Id' => $component_id,
                'Name' => $name,
                'Revision' => max(1, (int) ($entry['Revision'] ?? 1)),
                'UpdatedUtc' => sanitize_text_field((string) ($entry['UpdatedUtc'] ?? '')),
                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
            ];
"""
new="""            $variants = $this->normalize_page_component_variants($entry['Variants'] ?? [], $definition['Inputs'], $definition['Sections']);
            $components[$component_id] = [
                'Id' => $component_id,
                'Name' => $name,
                'Revision' => max(1, (int) ($entry['Revision'] ?? 1)),
                'UpdatedUtc' => sanitize_text_field((string) ($entry['UpdatedUtc'] ?? '')),
                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
                'Variants' => $variants,
            ];
"""
php=once(php,old,new,'component variants read')

# Usage reports the selected variant too.
php=once(php,
"""                    'SectionKey' => sanitize_key((string) ($section['Key'] ?? '')),
                ];
""",
"""                    'SectionKey' => sanitize_key((string) ($section['Key'] ?? '')),
                    'Variant' => sanitize_key((string) ($section['ComponentVariant'] ?? '')),
                ];
""",'component usage variant')

# Definition updates preserve variants.
php=once(php,
"""                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
            ];
""",
"""                'Sections' => $definition['Sections'],
                'Inputs' => $definition['Inputs'],
                'Variants' => $existing ? ($existing['Variants'] ?? []) : [],
            ];
""",'preserve variants on definition update')

variant_methods=r'''

    private function get_page_component_variant_usage($component_id,$variant_id){$usage=array_filter($this->get_page_component_usage($component_id),static function($item)use($variant_id){return sanitize_key((string)($item['Variant']??''))===sanitize_key((string)$variant_id);});return array_values($usage);}

    public function ajax_save_page_component_variant(){
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at gemme component variants.'],403);check_ajax_referer('h18_page_components_v0521','nonce');$component_id=sanitize_key((string)wp_unslash($_POST['component_id']??''));$variant_id=sanitize_key((string)wp_unslash($_POST['variant_id']??''));$name=sanitize_text_field((string)wp_unslash($_POST['name']??''));$json=(string)wp_unslash($_POST['values']??'{}');$components=$this->get_page_components();if(!isset($components[$component_id])||$name==='')wp_send_json_error(['message'=>'Komponent eller variantnavn mangler.'],400);$raw=json_decode($json,true);if(!is_array($raw)||json_last_error()!==JSON_ERROR_NONE)wp_send_json_error(['message'=>'Variantdata er ugyldig.'],400);$component=$components[$component_id];$input_map=[];foreach($component['Inputs'] as $input)$input_map[(string)$input['InputId']]=$input;$section_map=[];foreach($component['Sections'] as $section)$section_map[(string)$section['Key']]=$section;$values=[];foreach($raw as $input_id=>$value){$input_id=sanitize_key((string)$input_id);if(!isset($input_map[$input_id]))continue;$input=$input_map[$input_id];$field=(string)$input['Field'];$sanitized=$this->sanitize_page_component_override($field,$value);$base=$this->page_component_input_default($section_map[(string)$input['SectionKey']]??[],$field);if((string)$sanitized!==(string)$base)$values[$input_id]=$sanitized;}
        $variants=$component['Variants']??[];if($variant_id===''||!isset($variants[$variant_id]))$variant_id='variant-'.sanitize_key(wp_generate_uuid4());$variants[$variant_id]=['Id'=>$variant_id,'Name'=>$name,'Values'=>$values];if(count($variants)>12)wp_send_json_error(['message'=>'En komponent kan højst have 12 variants.'],400);$component['Variants']=$variants;$component['Revision']=(int)$component['Revision']+1;$component['UpdatedUtc']=gmdate('c');$components[$component_id]=$component;update_option(self::PAGE_COMPONENTS_OPTION,$components,false);$component['Usage']=$this->get_page_component_usage($component_id);$component['UsageCount']=count($component['Usage']);wp_send_json_success(['component'=>$component,'variant_id'=>$variant_id]);
    }

    public function ajax_delete_page_component_variant(){
        if(!current_user_can('edit_pages'))wp_send_json_error(['message'=>'Du har ikke rettigheder til at slette component variants.'],403);check_ajax_referer('h18_page_components_v0521','nonce');$component_id=sanitize_key((string)wp_unslash($_POST['component_id']??''));$variant_id=sanitize_key((string)wp_unslash($_POST['variant_id']??''));$components=$this->get_page_components();if(!isset($components[$component_id])||empty($components[$component_id]['Variants'][$variant_id]))wp_send_json_error(['message'=>'Varianten blev ikke fundet.'],404);$usage=$this->get_page_component_variant_usage($component_id,$variant_id);if($usage)wp_send_json_error(['message'=>'Varianten bruges stadig på '.count($usage).' side(r).','usage'=>$usage],409);unset($components[$component_id]['Variants'][$variant_id]);$components[$component_id]['Revision']=(int)$components[$component_id]['Revision']+1;$components[$component_id]['UpdatedUtc']=gmdate('c');update_option(self::PAGE_COMPONENTS_OPTION,$components,false);wp_send_json_success(['component_id'=>$component_id,'variant_id'=>$variant_id]);
    }
'''
php=once(php,"\n    private function resolve_page_component_instance_sections($page_id, array $instance) {",variant_methods+"\n    private function resolve_page_component_instance_sections($page_id, array $instance) {",'variant ajax methods')

# Resolve variant values first, local overrides last.
old="""        $sections = $component['Sections'];
        $overrides = isset($instance['ComponentOverrides']) && is_array($instance['ComponentOverrides']) ? $instance['ComponentOverrides'] : [];
        $section_index = [];
"""
new="""        $sections = $component['Sections'];
        $variant_id = sanitize_key((string) ($instance['ComponentVariant'] ?? ''));
        $variant_values = ($variant_id !== '' && isset($component['Variants'][$variant_id]) && is_array($component['Variants'][$variant_id]['Values'] ?? null)) ? $component['Variants'][$variant_id]['Values'] : [];
        $local_overrides = isset($instance['ComponentOverrides']) && is_array($instance['ComponentOverrides']) ? $instance['ComponentOverrides'] : [];
        $overrides = array_replace($variant_values, $local_overrides);
        $section_index = [];
"""
php=once(php,old,new,'variant resolution order')
# Clear internal component variant during render key remap.
php=once(php,"""            $section['ComponentRevision'] = 0;
            $section['ComponentOverrides'] = [];
""","""            $section['ComponentRevision'] = 0;
            $section['ComponentVariant'] = '';
            $section['ComponentOverrides'] = [];
""",'clear nested variant')

# Component admin selector supports variant.
old="""                            <input class="h18-component-revision" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentRevision]" value="<?php echo esc_attr($section['ComponentRevision']); ?>" />
                            <input class="h18-component-overrides-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentOverridesJson]" value="<?php echo esc_attr(wp_json_encode($section['ComponentOverrides'])); ?>" />
                        </div>
"""
new="""                            <input class="h18-component-revision" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentRevision]" value="<?php echo esc_attr($section['ComponentRevision']); ?>" />
                            <label><strong>Variant</strong></label>
                            <select class="h18-component-variant-select" name="<?php echo esc_attr($prefix); ?>[ComponentVariant]"><option value="">Base</option></select>
                            <input class="h18-component-overrides-json" type="hidden" name="<?php echo esc_attr($prefix); ?>[ComponentOverridesJson]" value="<?php echo esc_attr(wp_json_encode($section['ComponentOverrides'])); ?>" />
                        </div>
"""
php=once(php,old,new,'variant admin select')

# render_pages embeds Page Templates.
php=once(php,"""        $page_presets = $this->get_page_presets();
        $page_components = $this->get_page_components_for_editor();
""","""        $page_presets = $this->get_page_presets();
        $page_components = $this->get_page_components_for_editor();
        $page_templates = $this->get_page_templates_for_editor();
""",'page templates render data')

# UI Page Templates under Patterns.
old="""                                <div id="h18-user-presets-list" class="h18-user-presets-list"><p class="description">Vælg en sektion og brug “Gem som pattern” i Inspector.</p></div>
                            </div>
"""
new="""                                <div id="h18-user-presets-list" class="h18-user-presets-list"><p class="description">Vælg en sektion og brug “Gem som pattern” i Inspector.</p></div>
                                <div class="h18-user-components-heading"><h4>Page Templates</h4><span>Frie sidekopier</span></div>
                                <button type="button" class="button" id="h18-save-page-template">Gem denne side som template</button>
                                <div id="h18-page-templates-list" class="h18-user-presets-list"><p class="description">Gem hele den aktuelle side som en ikke-linked template.</p></div>
                            </div>
"""
php=once(php,old,new,'page template library UI')

# Template data JSON after component data.
old="""                <script id="h18-page-components-data" type="application/json"><?php echo wp_json_encode(array_values($page_components), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
"""
new="""                <script id="h18-page-components-data" type="application/json"><?php echo wp_json_encode(array_values($page_components), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
                <script id="h18-page-templates-data" type="application/json"><?php echo wp_json_encode(array_values($page_templates), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
"""
php=once(php,old,new,'template data json')

# JS refs/store/parse.
js=once(js,"""    const $pageLinkedComponentsList = $('#h18-linked-components-list');
    let pageSectionNextIndex = 0;
""","""    const $pageLinkedComponentsList = $('#h18-linked-components-list');
    const $pageTemplatesList = $('#h18-page-templates-list');
    let pageSectionNextIndex = 0;
""",'template list ref')
js=once(js,"""    const pageLinkedComponents = {};
    let navigatorLockedOrderSnapshotV0521 = null;
""","""    const pageLinkedComponents = {};
    const pageTemplatesV0522 = {};
    let navigatorLockedOrderSnapshotV0521 = null;
""",'template state')
parse_anchor="""    } catch (componentError) {
        window.console && console.warn('Hangar18: kunne ikke læse linked component-bibliotek.', componentError);
    }

    const builtInSectionPresets = {
"""
parse_new="""    } catch (componentError) {
        window.console && console.warn('Hangar18: kunne ikke læse linked component-bibliotek.', componentError);
    }
    try {
        const templateNode = document.getElementById('h18-page-templates-data');
        const parsedTemplates = templateNode ? JSON.parse(templateNode.textContent || '[]') : [];
        (Array.isArray(parsedTemplates) ? parsedTemplates : []).forEach(function(template){ if(template&&template.Id) pageTemplatesV0522[String(template.Id)]=template; });
    } catch(templateError){ window.console&&console.warn('Hangar18: kunne ikke læse Page Templates.',templateError); }

    const builtInSectionPresets = {
"""
js=once(js,parse_anchor,parse_new,'template data parse')

# Pattern library becomes subtree-aware.
old="""        presets.forEach(function (preset) {
            const $row = $('<div>', { class: 'h18-user-preset-row', 'data-preset-id': String(preset.Id) });
            $row.append($('<button>', { type: 'button', class: 'h18-user-preset-insert' }).append($('<strong>', { text: String(preset.Name || 'Komponent') })).append($('<small>', { text: inspectorTypeLabel(preset.Section && preset.Section.Type) })));
"""
new="""        presets.forEach(function (preset) {
            const patternSections = Array.isArray(preset.Sections) ? preset.Sections : (preset.Section ? [preset.Section] : []);
            const firstSection = patternSections.length ? patternSections[0] : null;
            const $row = $('<div>', { class: 'h18-user-preset-row', 'data-preset-id': String(preset.Id) });
            $row.append($('<button>', { type: 'button', class: 'h18-user-preset-insert' }).append($('<strong>', { text: String(preset.Name || 'Pattern') })).append($('<small>', { text: (firstSection ? inspectorTypeLabel(firstSection.Type) : 'Pattern') + ' · ' + patternSections.length + ' element(er)' })));
"""
js=once(js,old,new,'pattern list subtree')

# New pattern insertion creates fresh keys and internal parents.
pattern_js=r'''

    function applyPatternV0522(preset) {
        const sections = Array.isArray(preset && preset.Sections) ? preset.Sections : (preset && preset.Section ? [preset.Section] : []);
        if (!sections.length) { return $(); }
        const keyMap = {}; const rows = [];
        sections.forEach(function(section){
            const copy=Object.assign({},section); delete copy.LayoutParentKey; delete copy.Key; delete copy.Order;
            const $row=applySectionPreset(copy); if(!$row.length)return;
            const oldKey=String(section.Key||''); const newKey=String($row.find('.h18-page-section-key').val()||''); if(oldKey)keyMap[oldKey]=newKey; rows.push({row:$row,source:section});
        });
        rows.forEach(function(item){ const oldParent=String(item.source.LayoutParentKey||''); pageSectionControls(item.row,'.h18-layout-parent-key').val(oldParent&&keyMap[oldParent]?keyMap[oldParent]:''); });
        syncPageSectionOrder(); rebuildPageNavigator(); refreshLayoutHierarchyV0519(); refreshAllCanvasPreviews(); if(rows.length)inspectPageSection(rows[0].row); scheduleEditorHistoryCapture(0); return rows.length?rows[0].row:$();
    }
'''
js=once(js,"\n    function componentDefinitionSectionV0521(component, sectionKey) {",pattern_js+"\n    function componentDefinitionSectionV0521(component, sectionKey) {",'pattern apply function')

# Component variant defaults + editor.
old="""    function componentInputDefaultV0521(component, input) {
        const section = componentDefinitionSectionV0521(component, input && input.SectionKey);
        if (!section) { return ''; }
        const field = String(input.Field || '');
        return section[field] == null ? '' : section[field];
    }
"""
new="""    function componentInputDefaultV0521(component, input, variantId) {
        const section = componentDefinitionSectionV0521(component, input && input.SectionKey);
        if (!section) { return ''; }
        const field = String(input.Field || '');
        let value = section[field] == null ? '' : section[field];
        const variants = component && component.Variants && typeof component.Variants === 'object' ? component.Variants : {};
        const variant = variantId && variants[variantId] ? variants[variantId] : null;
        if (variant && variant.Values && Object.prototype.hasOwnProperty.call(variant.Values, String(input.InputId || ''))) value = variant.Values[String(input.InputId || '')];
        return value;
    }
"""
js=once(js,old,new,'variant input default')

# In component editor populate variant selector and use variant defaults.
old="""        pageSectionControls($row, '.h18-component-revision').val(parseInt(component.Revision,10)||1);
        const usage = parseInt(component.UsageCount,10)||0;
"""
new="""        pageSectionControls($row, '.h18-component-revision').val(parseInt(component.Revision,10)||1);
        const $variantSelect = pageSectionControls($row, '.h18-component-variant-select').first();
        const currentVariant = String($variantSelect.val() || '');
        const variants = component.Variants && typeof component.Variants === 'object' ? Object.values(component.Variants) : [];
        $variantSelect.empty().append($('<option>',{value:'',text:'Base'})); variants.forEach(function(variant){$variantSelect.append($('<option>',{value:String(variant.Id),text:String(variant.Name||'Variant')}));});
        $variantSelect.val(variants.some(function(v){return String(v.Id)===currentVariant;})?currentVariant:'');
        const activeVariant = String($variantSelect.val() || '');
        const usage = parseInt(component.UsageCount,10)||0;
"""
js=once(js,old,new,'variant selector populate')
js=once(js,"""            const defaultValue = componentInputDefaultV0521(component, input);
""","""            const defaultValue = componentInputDefaultV0521(component, input, activeVariant);
""",'variant default in editor')

# Variant actions placed before input loop/empty guard.
old="""        const overrides = parseComponentOverridesV0521($row);
        const inputs = Array.isArray(component.Inputs) ? component.Inputs : [];
        if (!inputs.length) {
"""
new="""        const overrides = parseComponentOverridesV0521($row);
        const inputs = Array.isArray(component.Inputs) ? component.Inputs : [];
        const $variantActions = $('<div>',{class:'h18-component-variant-actions'});
        if(inputs.length){$variantActions.append($('<button>',{type:'button',class:'button h18-component-save-variant',text:activeVariant?'Opdater valgt variant':'Gem aktuelle værdier som variant'}));if(activeVariant)$variantActions.append($('<button>',{type:'button',class:'button-link-delete h18-component-delete-variant',text:'Slet variant'}));$editor.append($variantActions);}
        if (!inputs.length) {
"""
js=once(js,old,new,'variant editor actions')

variant_js=r'''

    $(document).on('change','.h18-component-variant-select',function(){const $row=pageSectionForElement(this);writeComponentOverridesV0521($row,{});renderComponentInstanceEditorV0521($row);renderCanvasPreview($row);scheduleEditorHistoryCapture(0);});

    function componentVariantValuesV0522($row){const values={};pageSectionControls($row,'.h18-component-override-control').each(function(){const id=String($(this).attr('data-input-id')||'');if(id)values[id]=String($(this).val()==null?'':$(this).val());});return values;}

    $(document).on('click','.h18-component-save-variant',function(event){event.preventDefault();const $row=pageSectionForElement(this);const componentId=String(pageSectionControls($row,'.h18-component-select').val()||'');const component=pageLinkedComponents[componentId];if(!component)return;const variantId=String(pageSectionControls($row,'.h18-component-variant-select').val()||'');let currentName='';if(variantId&&component.Variants&&component.Variants[variantId])currentName=String(component.Variants[variantId].Name||'');const name=window.prompt(variantId?'Variantnavn:':'Navn til ny variant:',currentName||'Ny variant');if(!name)return;const $button=$(this).prop('disabled',true).text('Gemmer…');$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_save_page_component_variant',nonce:Hangar18Manager.pageComponentNonce,component_id:componentId,variant_id:variantId,name:String(name).trim(),values:JSON.stringify(componentVariantValuesV0522($row))}).done(function(response){if(!response||!response.success||!response.data||!response.data.component){window.alert((response&&response.data&&response.data.message)||'Varianten kunne ikke gemmes.');return;}pageLinkedComponents[componentId]=response.data.component;pageSectionControls($row,'.h18-component-variant-select').val(String(response.data.variant_id||''));writeComponentOverridesV0521($row,{});renderLinkedComponentsV0521();refreshAllComponentEditorsV0521();}).fail(function(xhr){window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Varianten kunne ikke gemmes.');}).always(function(){$button.prop('disabled',false);renderComponentInstanceEditorV0521($row);});});

    $(document).on('click','.h18-component-delete-variant',function(event){event.preventDefault();const $row=pageSectionForElement(this);const componentId=String(pageSectionControls($row,'.h18-component-select').val()||'');const variantId=String(pageSectionControls($row,'.h18-component-variant-select').val()||'');if(!componentId||!variantId||!window.confirm('Slet denne variant? Instanser der bruger den skal fjernes/skiftes først.'))return;$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_delete_page_component_variant',nonce:Hangar18Manager.pageComponentNonce,component_id:componentId,variant_id:variantId}).done(function(response){if(!response||!response.success){window.alert((response&&response.data&&response.data.message)||'Varianten kunne ikke slettes.');return;}const component=pageLinkedComponents[componentId];if(component&&component.Variants)delete component.Variants[variantId];pageSectionControls($row,'.h18-component-variant-select').val('');writeComponentOverridesV0521($row,{});renderComponentInstanceEditorV0521($row);renderCanvasPreview($row);});});
'''
js=once(js,"\n    function componentSubtreeRowsV0521($root) {",variant_js+"\n    function componentSubtreeRowsV0521($root) {",'variant JS actions')

# Component select resets variant too.
js=once(js,"""        writeComponentOverridesV0521($row, {});
        renderComponentInstanceEditorV0521($row); renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
""","""        pageSectionControls($row,'.h18-component-variant-select').val('');
        writeComponentOverridesV0521($row, {});
        renderComponentInstanceEditorV0521($row); renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0);
""",'component select resets variant')

# Pattern insert handler.
old="""        const preset = pageUserPresets[presetId];
        if (preset && preset.Section) {
            applySectionPreset(preset.Section);
        }
"""
new="""        const preset = pageUserPresets[presetId];
        if (preset) { applyPatternV0522(preset); }
"""
js=once(js,old,new,'pattern insert handler')

# Pattern save handler posts selected subtree.
old="""        const data = sectionPresetData($inspectedSection);
        if (!data) {
            return;
        }
        const defaultName = String(pageSectionControls($inspectedSection, '.h18-section-title-input').val() || inspectorTypeLabel(data.Type));
"""
new="""        const sections = componentSubtreeDataV0521($inspectedSection);
        if (!sections.length) { return; }
        const data = sections[0];
        const defaultName = String(pageSectionControls($inspectedSection, '.h18-section-title-input').val() || inspectorTypeLabel(data.Type));
"""
js=once(js,old,new,'pattern subtree save data')
js=once(js,"""            action: 'h18_save_page_preset', nonce: Hangar18Manager.pagePresetNonce, name: name, section: JSON.stringify(data)
""","""            action: 'h18_save_page_preset', nonce: Hangar18Manager.pagePresetNonce, name: name, sections: JSON.stringify(sections)
""",'pattern subtree post')

# Page Template JS.
template_js=r'''

    function pageTemplateSectionsV0522(){const rows=[];let invalid='';$pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function(index){const $row=$(this);const type=String($row.attr('data-section-type')||'text');if(['legacy','component'].includes(type)){invalid=type;return false;}const data=sectionPresetData($row);if(!data){invalid=type;return false;}data.Key=String($row.find('.h18-page-section-key').val()||'');data.Order=(index+1)*10;data.LayoutParentKey=String(pageSectionControls($row,'.h18-layout-parent-key').val()||'');rows.push(data);});return invalid?{error:invalid,sections:[]}:{error:'',sections:rows};}

    function renderPageTemplatesV0522(){if(!$pageTemplatesList.length)return;const templates=Object.values(pageTemplatesV0522).sort(function(a,b){return String(a.Name||'').localeCompare(String(b.Name||''),'da');});$pageTemplatesList.empty();if(!templates.length){$pageTemplatesList.html('<p class="description">Ingen Page Templates endnu.</p>');return;}templates.forEach(function(template){const usage=parseInt(template.UsageCount,10)||0;const $row=$('<div>',{class:'h18-user-preset-row h18-page-template-row','data-template-id':String(template.Id)});$row.append($('<button>',{type:'button',class:'h18-page-template-create'}).append($('<strong>',{text:String(template.Name||'Page Template')}),$('<small>',{text:(Array.isArray(template.Sections)?template.Sections.length:0)+' elementer · '+usage+' oprettede sider'})));$row.append($('<button>',{type:'button',class:'h18-page-template-usage',title:'Vis oprettede sider','aria-label':'Vis oprettede sider'}).append($('<span>',{class:'dashicons dashicons-admin-page'})));$row.append($('<button>',{type:'button',class:'h18-page-template-delete',title:'Slet template','aria-label':'Slet template'}).append($('<span>',{class:'dashicons dashicons-trash'})));$pageTemplatesList.append($row);});}

    $('#h18-save-page-template').on('click',function(){const collected=pageTemplateSectionsV0522();if(collected.error){window.alert('Page Template kan ikke gemmes, mens siden indeholder legacy eller linked component-instanser. Konvertér/detach dem først.');return;}if(!collected.sections.length){window.alert('Siden har ingen elementer at gemme.');return;}const currentTitle=String($('[name="editor_page_title"]').val()||'Side');const name=window.prompt('Navn til Page Template:',currentTitle);if(!name)return;const $button=$(this).prop('disabled',true).text('Gemmer…');$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_save_page_template',nonce:Hangar18Manager.pageTemplateNonce,name:String(name).trim(),page_title:currentTitle,sections:JSON.stringify(collected.sections)}).done(function(response){if(!response||!response.success||!response.data||!response.data.template){window.alert((response&&response.data&&response.data.message)||'Page Template kunne ikke gemmes.');return;}pageTemplatesV0522[String(response.data.template.Id)]=response.data.template;renderPageTemplatesV0522();}).fail(function(xhr){window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Page Template kunne ikke gemmes.');}).always(function(){$button.prop('disabled',false).text('Gem denne side som template');});});

    $(document).on('click','.h18-page-template-create',function(){const id=String($(this).closest('.h18-page-template-row').attr('data-template-id')||'');const template=pageTemplatesV0522[id];if(!template)return;const title=window.prompt('Titel på den nye WordPress-side:',String(template.PageTitle||template.Name||'Ny side'));if(!title)return;const suggested=String(title).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');const slug=window.prompt('Slug til den nye side:',suggested);if(!slug)return;$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_create_page_from_template',nonce:Hangar18Manager.pageTemplateNonce,template_id:id,page_title:String(title).trim(),page_slug:String(slug).trim()}).done(function(response){if(!response||!response.success){window.alert((response&&response.data&&response.data.message)||'Siden kunne ikke oprettes.');return;}if(response.data.manager_url)window.location.href=response.data.manager_url;}).fail(function(xhr){window.alert((xhr.responseJSON&&xhr.responseJSON.data&&xhr.responseJSON.data.message)||'Siden kunne ikke oprettes.');});});

    $(document).on('click','.h18-page-template-usage',function(){const id=String($(this).closest('.h18-page-template-row').attr('data-template-id')||'');const template=pageTemplatesV0522[id];if(!template)return;const usage=Array.isArray(template.Usage)?template.Usage:[];window.alert(usage.length?'Sider oprettet fra “'+String(template.Name||'Template')+'”:\n\n'+usage.map(function(item){return '• '+String(item.PageTitle||item.PageSlug)+' / '+String(item.PageSlug||'');}).join('\n'):'Ingen sider er oprettet fra denne template endnu.');});

    $(document).on('click','.h18-page-template-delete',function(){const id=String($(this).closest('.h18-page-template-row').attr('data-template-id')||'');const template=pageTemplatesV0522[id];if(!template)return;if(!window.confirm('Slet Page Template “'+String(template.Name||'Template')+'”? Allerede oprettede sider påvirkes ikke.'))return;$.post(Hangar18Manager.ajaxUrl||window.ajaxurl,{action:'h18_delete_page_template',nonce:Hangar18Manager.pageTemplateNonce,template_id:id}).done(function(response){if(response&&response.success){delete pageTemplatesV0522[id];renderPageTemplatesV0522();}else window.alert((response&&response.data&&response.data.message)||'Template kunne ikke slettes.');});});
'''
js=once(js,"\n    function restoreInspectedSection() {",template_js+"\n    function restoreInspectedSection() {",'page template JS insertion')

# Initial template render.
js=once(js,"""        renderLinkedComponentsV0521();
        refreshAllComponentEditorsV0521();
        rebuildPageNavigator();
""","""        renderLinkedComponentsV0521();
        renderPageTemplatesV0522();
        refreshAllComponentEditorsV0521();
        rebuildPageNavigator();
""",'initial template render')

# Canvas component summary includes selected variant.
old="""                $('<div>').append($('<strong>', { text: component ? String(component.Name || 'Linked component') : 'Vælg linked component' }), $('<small>', { text: component ? 'Global revision ' + String(component.Revision || 1) + ' · ' + Object.keys(overrides).length + ' lokal(e) override(s)' : 'Ingen definition valgt' }))
"""
new="""                $('<div>').append($('<strong>', { text: component ? String(component.Name || 'Linked component') : 'Vælg linked component' }), $('<small>', { text: component ? 'Global revision ' + String(component.Revision || 1) + (String(canvasFieldValue($row,'ComponentVariant','')) ? ' · variant' : ' · base') + ' · ' + Object.keys(overrides).length + ' lokal(e) override(s)' : 'Ingen definition valgt' }))
"""
js=once(js,old,new,'canvas variant label')

# CSS.
css_block=r'''

/* v0.5.22 – variants, subtree patterns and page templates */
.h18-component-variant-actions{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 12px;padding:8px 0;border-bottom:1px solid #dcdcde}.h18-page-template-row{grid-template-columns:minmax(0,1fr) auto auto}.h18-page-template-row .h18-page-template-create{text-align:left}.h18-page-template-row button{min-width:0}
'''
if '/* v0.5.22 – variants, subtree patterns and page templates */' in css:raise SystemExit('v0.5.22 CSS already present')
css=css.rstrip()+css_block+'\n'

readme=once(readme,'Version: 0.5.21','Version: 0.5.22','readme version')
anchor='== Version 0.5.21 – E4 linked component engine foundation ==\n'
new="""== Version 0.5.22 – E4 Components completion ==

Nyt:
- UD-047: linked component variants deler base-definition og gemmer kun kontrollerede værdier for allerede frigivne component inputs
- variant anvendes før lokale instance-overrides, så lokale overrides fortsat har højeste prioritet
- variants oprettes/opdateres direkte fra en component-instance; variant med usage kan ikke slettes
- component revision stiger ved variantændringer, og global definition-update bevarer eksisterende variants
- UD-048: eksisterende presets er nu eksplicit Patterns og kan gemme/indsætte et helt nested subtree med friske keys og bevaret intern parent-struktur
- gamle én-sektions presets migreres transparent til subtree Pattern-format ved læsning
- Patterns forbliver ikke-linked og indeholder aldrig linked component-instanser eller legacy
- UD-049: Page Templates gemmer hele selvstændige sider og kan oprette nye draft WordPress/Hangar18-sider med friske section keys
- template-oprettede sider markeres som Hangar18-managed og bliver automatisk tilgængelige i sideeditorens sidevælger
- Page Template usage spores som origin-metadata til audit, men siden er en fri kopi; senere template-ændringer påvirker den ikke
- Page Templates afviser legacy og linked component-instanser for at garantere ingen skjulte shared-instance side effects
- page-editor schema løftes bagudkompatibelt til 1.18

"""+anchor
readme=once(readme,anchor,new,'readme v0.5.21 anchor')

php_path.write_text(php);js_path.write_text(js);css_path.write_text(css);readme_path.write_text(readme)
print('v0.5.22 patch applied')
