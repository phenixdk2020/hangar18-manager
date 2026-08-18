from pathlib import Path
p=Path('hangar18-manager.php');j=Path('assets/admin.js');c=Path('assets/admin.css');r=Path('readme.txt')
php=p.read_text();js=j.read_text();css=c.read_text();readme=r.read_text()
def once(t,o,n,l):
    x=t.count(o)
    if x!=1: raise SystemExit(f'{l}: expected 1 anchor, found {x}')
    return t.replace(o,n,1)
php=once(php,' * Version: 0.5.28',' * Version: 0.5.29','header')
php=once(php,"    const VERSION = '0.5.28';","    const VERSION = '0.5.29';",'const')
php=once(php,"    const DATA_ENTRY_POST_TYPE        = 'h18_data_entry';","    const DATA_ENTRY_POST_TYPE        = 'h18_data_entry';\n    const DATA_TAG_TAXONOMY            = 'h18_data_tag';",'taxonomy constant')
php=once(php,"""        add_shortcode('hangar18_data_query', [$this, 'shortcode_data_query']);
""","""        add_shortcode('hangar18_data_query', [$this, 'shortcode_data_query']);
        add_shortcode('hangar18_data_query_advanced', [$this, 'shortcode_data_query_advanced']);
""",'advanced shortcode registration')
php=once(php,"""            'map_meta_cap' => true,
        ]);
    }

    private function custom_data_field_types() {
""","""            'map_meta_cap' => true,
        ]);
        register_taxonomy(self::DATA_TAG_TAXONOMY, [self::DATA_ENTRY_POST_TYPE], [
            'labels' => ['name'=>'Data Tags','singular_name'=>'Data Tag'],
            'public' => false,
            'show_ui' => false,
            'show_in_rest' => false,
            'hierarchical' => false,
            'rewrite' => false,
            'query_var' => false,
        ]);
    }

    private function custom_data_field_types() {
""",'register data taxonomy')
# Save data tags with entry.
php=once(php,"""        foreach (array_keys((array) get_post_meta($entry_id)) as $meta_key) {
            if (strpos((string) $meta_key, '_h18_field_') === 0 && !isset($valid_meta[$meta_key])) { delete_post_meta($entry_id, $meta_key); }
        }
        $this->log('INFO', 'CUSTOM_DATA_ENTRY_SAVED', "Data-entry ID {$entry_id} gemt i '{$type_key}'.");
""","""        foreach (array_keys((array) get_post_meta($entry_id)) as $meta_key) {
            if (strpos((string) $meta_key, '_h18_field_') === 0 && !isset($valid_meta[$meta_key])) { delete_post_meta($entry_id, $meta_key); }
        }
        $raw_tags = sanitize_text_field((string) wp_unslash($_POST['data_tags'] ?? ''));
        $tags = [];
        foreach (array_slice(preg_split('/\\s*,\\s*/', $raw_tags), 0, 20) as $tag) {
            $tag = sanitize_text_field((string) $tag); if ($tag !== '' && !in_array($tag, $tags, true)) { $tags[] = $tag; }
        }
        $term_result = wp_set_object_terms($entry_id, $tags, self::DATA_TAG_TAXONOMY, false);
        if (is_wp_error($term_result)) { $this->log('WARN','CUSTOM_DATA_TAG_SAVE_FAILED',$term_result->get_error_message()); }
        $this->log('INFO', 'CUSTOM_DATA_ENTRY_SAVED', "Data-entry ID {$entry_id} gemt i '{$type_key}'.");
""",'save data tags')
# Entry tag UI setup and field.
php=once(php,"""        $entry_values = $entry && $selected ? $this->custom_data_entry_values($entry->ID, $selected) : [];
        $entries = $selected ? $this->custom_data_entry_query($selected['Key'], 100) : [];
""","""        $entry_values = $entry && $selected ? $this->custom_data_entry_values($entry->ID, $selected) : [];
        $entry_tags = $entry ? wp_get_object_terms($entry->ID, self::DATA_TAG_TAXONOMY, ['fields'=>'names']) : [];
        if (is_wp_error($entry_tags)) { $entry_tags = []; }
        $entries = $selected ? $this->custom_data_entry_query($selected['Key'], 100) : [];
""",'load entry tags')
php=once(php,"""                            <div class=\"h18-field\"><label><strong>Titel</strong></label><input type=\"text\" name=\"entry_title\" value=\"<?php echo esc_attr($entry ? $entry->post_title : ''); ?>\" required /></div>
                            <?php foreach ($selected['Fields'] as $field) :
""","""                            <div class=\"h18-field\"><label><strong>Titel</strong></label><input type=\"text\" name=\"entry_title\" value=\"<?php echo esc_attr($entry ? $entry->post_title : ''); ?>\" required /></div>
                            <div class=\"h18-field\"><label><strong>Data Tags</strong><small>Taxonomy · kommasepareret</small></label><input type=\"text\" name=\"data_tags\" value=\"<?php echo esc_attr(implode(', ', array_map('strval',(array)$entry_tags))); ?>\" placeholder=\"fx aktiv, nordjylland\" /></div>
                            <?php foreach ($selected['Fields'] as $field) :
""",'entry tag input')
# Current entry form is actually one-line foreach in current source; prepare a fallback anchor later if needed.

advanced=r'''

    /* ================================================================
       ADVANCED QUERY ENGINE — v0.5.29 / E5 UD-056
       ================================================================ */

    private function advanced_data_query_field_map(array $schema) {
        $map=[]; foreach((array)($schema['Fields']??[]) as $field){if(is_array($field)&&!empty($field['Key']))$map[(string)$field['Key']]=$field;} return $map;
    }

    private function normalize_advanced_data_query(array $raw) {
        $types=$this->get_custom_data_types(); $type_key=sanitize_key((string)($raw['Type']??$raw['type']??''));
        if($type_key===''||!isset($types[$type_key]))throw new RuntimeException('Advanced Query: vælg en gyldig datatype.');
        $schema=$types[$type_key];$field_map=$this->advanced_data_query_field_map($schema);$group_relation=strtoupper((string)($raw['GroupRelation']??'AND'));if(!in_array($group_relation,['AND','OR'],true))$group_relation='AND';
        $groups_raw=$raw['Groups']??[];if(is_string($groups_raw)){ $decoded=json_decode($groups_raw,true);$groups_raw=is_array($decoded)?$decoded:[]; } if(!is_array($groups_raw))$groups_raw=[];
        $groups=[];
        foreach(array_slice(array_values($groups_raw),0,4) as $group_index=>$group){if(!is_array($group))continue;$relation=strtoupper((string)($group['Relation']??'AND'));if(!in_array($relation,['AND','OR'],true))$relation='AND';$filters=[];
            foreach(array_slice(array_values((array)($group['Filters']??[])),0,6) as $filter){if(!is_array($filter))continue;$kind=sanitize_key((string)($filter['Kind']??'field'));
                if($kind==='taxonomy'){$operator=sanitize_key((string)($filter['Operator']??'in'));if(!in_array($operator,['in','not_in'],true))$operator='in';$terms=[];foreach(array_slice(preg_split('/\\s*,\\s*/',(string)($filter['Value']??'')),0,10) as $term){$term=sanitize_title((string)$term);if($term!==''&&!in_array($term,$terms,true))$terms[]=$term;}if(!$terms)continue;$filters[]=['Kind'=>'taxonomy','Operator'=>$operator,'Terms'=>$terms];continue;}
                $field_key=sanitize_key((string)($filter['Field']??''));if($field_key===''||!isset($field_map[$field_key]))continue;$field=$field_map[$field_key];$field_type=(string)$field['Type'];if(in_array($field_type,['group','repeater'],true))continue;
                $operators=$field_type==='relation'?['eq','neq'] : array_keys($this->custom_data_query_operator_map($field_type));$operator=sanitize_key((string)($filter['Operator']??'eq'));if(!in_array($operator,$operators,true))continue;$value_raw=$filter['Value']??'';
                if(in_array($field_type,['number','relation','media'],true)){if(!is_numeric($value_raw))continue;$value=(string)(0+$value_raw);}elseif($field_type==='bool'){$value=$this->bool_value($value_raw,false)?'1':'0';}elseif($field_type==='date'){$value=sanitize_text_field((string)$value_raw);$date=DateTime::createFromFormat('!Y-m-d',$value);if(!$date||$date->format('Y-m-d')!==$value)continue;}else{$value=sanitize_text_field((string)$value_raw);}
                $filters[]=['Kind'=>'field','Field'=>$field_key,'FieldType'=>$field_type,'Operator'=>$operator,'Value'=>$value];
            }
            if($filters)$groups[]=['Relation'=>$relation,'Filters'=>$filters];
        }
        $sort_raw=(string)($raw['Sort']??'modified');$sort=in_array($sort_raw,['title','modified','created'],true)?$sort_raw:'';if($sort===''&&strpos($sort_raw,'field:')===0){$field_key=sanitize_key(substr($sort_raw,6));if(isset($field_map[$field_key])&&!in_array((string)$field_map[$field_key]['Type'],['bool','group','repeater'],true))$sort='field:'.$field_key;}if($sort==='')$sort='modified';
        $order=strtoupper((string)($raw['Order']??'DESC'));if(!in_array($order,['ASC','DESC'],true))$order='DESC';$per_page=$this->clamp_int($raw['PerPage']??12,1,50,12);$page=$this->clamp_int($raw['Page']??1,1,10000,1);
        return ['Type'=>$type_key,'Schema'=>$schema,'GroupRelation'=>$group_relation,'Groups'=>$groups,'Sort'=>$sort,'Order'=>$order,'PerPage'=>$per_page,'Page'=>$page];
    }

    private function advanced_data_query_compare_value($actual,array $filter) {
        $type=(string)($filter['FieldType']??'text');$op=(string)($filter['Operator']??'eq');$expected=$filter['Value']??'';
        if(in_array($type,['number','relation','media'],true)){$a=(float)$actual;$b=(float)$expected;}elseif($type==='bool'){$a=$this->bool_value($actual,false)?1:0;$b=$this->bool_value($expected,false)?1:0;}else{$a=(string)$actual;$b=(string)$expected;}
        if($op==='contains')return stripos((string)$a,(string)$b)!==false;if($op==='eq')return $a==$b;if($op==='neq')return $a!=$b;if($op==='gt'||$op==='after')return $a>$b;if($op==='gte')return $a>=$b;if($op==='lt'||$op==='before')return $a<$b;if($op==='lte')return $a<=$b;return false;
    }

    private function advanced_data_query_filter_matches(WP_Post $post,array $filter) {
        if(($filter['Kind']??'field')==='taxonomy'){$slugs=wp_get_object_terms($post->ID,self::DATA_TAG_TAXONOMY,['fields'=>'slugs']);if(is_wp_error($slugs))$slugs=[];$has=(bool)array_intersect((array)$filter['Terms'],array_map('strval',(array)$slugs));return ($filter['Operator']??'in')==='not_in'?!$has:$has;}
        $actual=get_post_meta($post->ID,'_h18_field_'.sanitize_key((string)$filter['Field']),true);return $this->advanced_data_query_compare_value($actual,$filter);
    }

    private function advanced_data_query_group_matches(WP_Post $post,array $group) {
        $results=[];foreach((array)$group['Filters'] as $filter)$results[]=$this->advanced_data_query_filter_matches($post,$filter);if(!$results)return true;return ($group['Relation']??'AND')==='OR'?in_array(true,$results,true):!in_array(false,$results,true);
    }

    private function advanced_data_query_post_matches(WP_Post $post,array $query) {
        if(!$query['Groups'])return true;$results=[];foreach($query['Groups'] as $group)$results[]=$this->advanced_data_query_group_matches($post,$group);return $query['GroupRelation']==='OR'?in_array(true,$results,true):!in_array(false,$results,true);
    }

    private function advanced_data_query_sort_value(WP_Post $post,array $query) {
        if($query['Sort']==='title')return mb_strtolower((string)$post->post_title);if($query['Sort']==='created')return strtotime((string)$post->post_date_gmt)?:0;if($query['Sort']==='modified')return strtotime((string)$post->post_modified_gmt)?:0;$field=sanitize_key(substr((string)$query['Sort'],6));$map=$this->advanced_data_query_field_map($query['Schema']);$value=get_post_meta($post->ID,'_h18_field_'.$field,true);$type=(string)($map[$field]['Type']??'text');return in_array($type,['number','relation','media'],true)?(float)$value:mb_strtolower((string)$value);
    }

    private function run_advanced_data_query(array $raw,&$normalized=null) {
        $query=$this->normalize_advanced_data_query($raw);$normalized=$query;$candidate_limit=2000;
        $candidates=get_posts(['post_type'=>self::DATA_ENTRY_POST_TYPE,'post_status'=>'publish','posts_per_page'=>$candidate_limit,'no_found_rows'=>true,'meta_key'=>'_h18_data_type','meta_value'=>$query['Type'],'orderby'=>'ID','order'=>'ASC']);
        $matches=[];foreach($candidates as $post){if($post instanceof WP_Post&&$this->advanced_data_query_post_matches($post,$query))$matches[]=$post;}
        usort($matches,function($a,$b)use($query){$av=$this->advanced_data_query_sort_value($a,$query);$bv=$this->advanced_data_query_sort_value($b,$query);$cmp=$av<=>$bv;if($cmp===0)$cmp=((int)$a->ID)<=>((int)$b->ID);return $query['Order']==='DESC'?-$cmp:$cmp;});
        $total=count($matches);$pages=max(1,(int)ceil($total/$query['PerPage']));$page=min($query['Page'],$pages);$offset=($page-1)*$query['PerPage'];$posts=array_slice($matches,$offset,$query['PerPage']);
        return ['Posts'=>$posts,'Total'=>$total,'TotalPages'=>$pages,'Page'=>$page,'PerPage'=>$query['PerPage'],'Truncated'=>count($candidates)>=$candidate_limit,'Query'=>$query];
    }

    private function advanced_data_query_public_config(array $query) {return ['Type'=>$query['Type'],'GroupRelation'=>$query['GroupRelation'],'Groups'=>$query['Groups'],'Sort'=>$query['Sort'],'Order'=>$query['Order'],'PerPage'=>$query['PerPage']];}
    private function advanced_data_query_encode(array $query) {$json=wp_json_encode($this->advanced_data_query_public_config($query));return rtrim(strtr(base64_encode((string)$json),'+/','-_'),'=');}
    private function advanced_data_query_decode($config) {$config=preg_replace('/[^A-Za-z0-9_-]/','',(string)$config);if($config===''||strlen($config)>12000)throw new RuntimeException('Advanced Query config mangler eller er for stor.');$pad=strlen($config)%4;if($pad)$config.=str_repeat('=',4-$pad);$json=base64_decode(strtr($config,'-_','+/'),true);$raw=$json!==false?json_decode($json,true):null;if(!is_array($raw))throw new RuntimeException('Advanced Query config er ugyldig.');return $raw;}
    private function advanced_data_query_shortcode(array $query) {return '[hangar18_data_query_advanced config="'.esc_attr($this->advanced_data_query_encode($query)).'"]';}

    public function shortcode_data_query_advanced($atts) {
        $atts=shortcode_atts(['config'=>''],$atts,'hangar18_data_query_advanced');try{$raw=$this->advanced_data_query_decode($atts['config']);$probe=$this->normalize_advanced_data_query($raw);$hash=substr(hash('sha256',$this->advanced_data_query_encode($probe)),0,12);$page_param='h18q_'.$hash;$raw['Page']=isset($_GET[$page_param])?absint($_GET[$page_param]):1;$normalized=null;$result=$this->run_advanced_data_query($raw,$normalized);}catch(Throwable $e){return current_user_can('edit_pages')?'<p class="h18-data-query-error">'.esc_html($e->getMessage()).'</p>':'';}
        if(!$result['Posts'])return '<div class="h18-data-query-results h18-data-query-results--empty">Ingen resultater.</div>';$html='<ul class="h18-data-query-results h18-data-query-results--advanced">';foreach($result['Posts'] as $post)$html.='<li data-entry-id="'.(int)$post->ID.'">'.esc_html((string)$post->post_title).'</li>';$html.='</ul>';
        if($result['TotalPages']>1){$html.='<nav class="h18-data-pagination" aria-label="Sider">';for($i=1;$i<=$result['TotalPages'];$i++){if($i>20&&abs($i-$result['Page'])>2&&$i!=$result['TotalPages'])continue;$url=add_query_arg($page_param,$i);$html.='<a '.($i===$result['Page']?'aria-current="page" ':'').'href="'.esc_url($url).'">'.(int)$i.'</a>';}$html.='</nav>';}
        return $html;
    }
'''
php=once(php,"""    public function render_data() {
""",advanced+"""

    public function render_data() {
""",'advanced query engine')
# Advanced state in render_data.
php=once(php,"""        $qb_results = []; $qb_normalized = null; $qb_error = '';
        if ($query_preview) {
            try { $qb_results = $this->run_custom_data_query($qb_raw, $qb_normalized); }
            catch (Throwable $e) { $qb_error = $e->getMessage(); }
        }
        ?>
""","""        $qb_results = []; $qb_normalized = null; $qb_error = '';
        if ($query_preview) {
            try { $qb_results = $this->run_custom_data_query($qb_raw, $qb_normalized); }
            catch (Throwable $e) { $qb_error = $e->getMessage(); }
        }
        $advanced_preview = !empty($_GET['advanced_preview']) && $selected;
        $aq_groups_json = isset($_GET['aq_groups']) ? (string) wp_unslash($_GET['aq_groups']) : '';
        $aq_groups = $aq_groups_json !== '' ? json_decode($aq_groups_json,true) : [];
        if (!is_array($aq_groups)) { $aq_groups=[]; }
        $aq_raw=['Type'=>$selected?$selected['Key']:'','GroupRelation'=>isset($_GET['aq_group_relation'])?wp_unslash($_GET['aq_group_relation']):'AND','Groups'=>$aq_groups,'Sort'=>isset($_GET['aq_sort'])?wp_unslash($_GET['aq_sort']):'modified','Order'=>isset($_GET['aq_order'])?wp_unslash($_GET['aq_order']):'DESC','PerPage'=>isset($_GET['aq_per_page'])?wp_unslash($_GET['aq_per_page']):12,'Page'=>isset($_GET['aq_page'])?wp_unslash($_GET['aq_page']):1];
        $aq_result=null;$aq_normalized=null;$aq_error='';if($advanced_preview){try{$aq_result=$this->run_advanced_data_query($aq_raw,$aq_normalized);}catch(Throwable $e){$aq_error=$e->getMessage();}}
        $aq_tags=get_terms(['taxonomy'=>self::DATA_TAG_TAXONOMY,'hide_empty'=>false,'fields'=>'all']);if(is_wp_error($aq_tags))$aq_tags=[];
        ?>
""",'advanced query render state')
# Insert advanced builder before schema details.
advanced_ui=r'''

                <section class="h18-panel h18-data-advanced-query">
                    <div class="h18-panel-heading-row"><div><h3>Advanced Query</h3><p>AND/OR-grupper, relationer, Data Tags og pagination. Samme normalized evaluator bruges i preview og frontend.</p></div><span>UD-056</span></div>
                    <form method="get" action="<?php echo esc_url(admin_url('admin.php')); ?>" id="h18-advanced-query-form">
                        <input type="hidden" name="page" value="hangar18-data" /><input type="hidden" name="type" value="<?php echo esc_attr($selected['Key']); ?>" /><input type="hidden" name="advanced_preview" value="1" /><input type="hidden" id="h18-aq-groups-json" name="aq_groups" value="<?php echo esc_attr(wp_json_encode($aq_groups)); ?>" />
                        <div class="h18-module-fields-grid h18-module-fields-grid--four"><div class="h18-field"><label><strong>Mellem grupper</strong></label><select name="aq_group_relation"><option value="AND" <?php selected(strtoupper((string)$aq_raw['GroupRelation']),'AND'); ?>>AND</option><option value="OR" <?php selected(strtoupper((string)$aq_raw['GroupRelation']),'OR'); ?>>OR</option></select></div><div class="h18-field"><label><strong>Sortér</strong></label><select name="aq_sort"><option value="modified" <?php selected($aq_raw['Sort'],'modified'); ?>>Senest ændret</option><option value="created" <?php selected($aq_raw['Sort'],'created'); ?>>Oprettet</option><option value="title" <?php selected($aq_raw['Sort'],'title'); ?>>Titel</option><?php foreach($selected['Fields'] as $field):if(in_array($field['Type'],['bool','group','repeater'],true))continue;?><option value="field:<?php echo esc_attr($field['Key']); ?>" <?php selected($aq_raw['Sort'],'field:'.$field['Key']); ?>><?php echo esc_html($field['Label']); ?></option><?php endforeach;?></select></div><div class="h18-field"><label><strong>Retning</strong></label><select name="aq_order"><option value="DESC" <?php selected(strtoupper((string)$aq_raw['Order']),'DESC'); ?>>Faldende</option><option value="ASC" <?php selected(strtoupper((string)$aq_raw['Order']),'ASC'); ?>>Stigende</option></select></div><div class="h18-field"><label><strong>Pr. side</strong></label><input type="number" min="1" max="50" name="aq_per_page" value="<?php echo esc_attr((int)$aq_raw['PerPage']); ?>" /></div></div>
                        <script id="h18-aq-schema" type="application/json"><?php echo wp_json_encode(['Fields'=>array_values($selected['Fields']),'Catalog'=>$this->dynamic_data_context_catalog_for_editor(),'Tags'=>array_map(static function($term){return ['slug'=>(string)$term->slug,'name'=>(string)$term->name];},(array)$aq_tags)],JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT); ?></script>
                        <div id="h18-aq-groups"></div><p><button type="button" class="button" id="h18-aq-add-group">+ Tilføj gruppe</button></p><p><button type="submit" class="button button-primary">Kør Advanced preview</button></p>
                    </form>
                    <?php if($advanced_preview):?><div class="h18-data-query-preview"><?php if($aq_error!==''):?><div class="notice notice-error inline"><p><?php echo esc_html($aq_error); ?></p></div><?php else:?><p><strong><?php echo esc_html((int)$aq_result['Total']); ?> resultat(er)</strong> · side <?php echo esc_html((int)$aq_result['Page']); ?>/<?php echo esc_html((int)$aq_result['TotalPages']); ?><?php echo !empty($aq_result['Truncated'])?' · kandidatgrænse nået':''; ?></p><table class="widefat striped"><thead><tr><th>ID</th><th>Titel</th></tr></thead><tbody><?php foreach($aq_result['Posts'] as $aq_post):?><tr><td><?php echo esc_html((int)$aq_post->ID); ?></td><td><?php echo esc_html($aq_post->post_title); ?></td></tr><?php endforeach;?></tbody></table><p><strong>Frontend:</strong> <code><?php echo esc_html($this->advanced_data_query_shortcode($aq_normalized)); ?></code></p><?php endif;?></div><?php endif;?>
                </section>
'''
php=once(php,"""                <?php if ($can_schema) : ?><details class=\"h18-panel h18-data-schema-details\"><summary><strong>Redigér datatype-schema</strong></summary>
""",advanced_ui+"""

                <?php if ($can_schema) : ?><details class=\"h18-panel h18-data-schema-details\"><summary><strong>Redigér datatype-schema</strong></summary>
""",'advanced builder UI')
# JS dynamic builder.
js += r'''

    /* v0.5.29 – UD-056 Advanced Query */
    (function(){const $root=$('#h18-aq-groups'),$hidden=$('#h18-aq-groups-json');if(!$root.length||!$hidden.length)return;let schema={Fields:[],Catalog:[],Tags:[]};try{schema=JSON.parse($('#h18-aq-schema').text()||'{}');}catch(e){}let groups=[];try{groups=JSON.parse(String($hidden.val()||'[]'));if(!Array.isArray(groups))groups=[];}catch(e){groups=[];}if(!groups.length)groups=[{Relation:'AND',Filters:[]}];
    function fieldMap(){const m={};(schema.Fields||[]).forEach(f=>{if(f&&f.Key)m[String(f.Key)]=f;});return m;}const fmap=fieldMap();function ops(type){if(type==='relation')return[['eq','= relation'],['neq','≠ relation']];if(type==='text')return[['eq','='],['neq','≠'],['contains','Indeholder']];if(type==='number')return[['eq','='],['neq','≠'],['gt','>'],['gte','≥'],['lt','<'],['lte','≤']];if(type==='date')return[['eq','På dato'],['before','Før'],['after','Efter']];return[['eq','='],['neq','≠']];}
    function sync(){const out=[];$root.children('.h18-aq-group').each(function(){const $g=$(this),filters=[];$g.find('>.h18-aq-filters>.h18-aq-filter').each(function(){const $f=$(this);filters.push({Kind:String($f.find('.h18-aq-kind').val()||'field'),Field:String($f.find('.h18-aq-field').val()||''),Operator:String($f.find('.h18-aq-op').val()||'eq'),Value:String($f.find('.h18-aq-value').val()||'')});});if(filters.length)out.push({Relation:String($g.find('>.h18-aq-head>.h18-aq-relation').val()||'AND'),Filters:filters});});$hidden.val(JSON.stringify(out));groups=out;}
    function filterRow(f){f=f||{Kind:'field',Field:'',Operator:'eq',Value:''};const $r=$('<div>',{class:'h18-aq-filter'}),$kind=$('<select>',{class:'h18-aq-kind'}).append('<option value="field">Datafelt</option><option value="taxonomy">Data Tag</option>').val(f.Kind||'field'),$field=$('<select>',{class:'h18-aq-field'}),$op=$('<select>',{class:'h18-aq-op'}),$value=$('<input>',{class:'h18-aq-value',type:'text'}).val(f.Value||'');function refresh(){const kind=String($kind.val());let current=String($field.val()||f.Field||'');$field.empty();if(kind==='taxonomy'){$field.append('<option value="__tags">Data Tags</option>').val('__tags');let o=String(f.Operator||$op.val()||'in');$op.empty().append('<option value="in">Har en af</option><option value="not_in">Har ingen af</option>').val(['in','not_in'].includes(o)?o:'in');$value.attr('placeholder','tag-slug, andet-tag');}else{(schema.Fields||[]).filter(x=>!['group','repeater'].includes(String(x.Type))).forEach(x=>$field.append($('<option>',{value:String(x.Key),text:String(x.Label)+' · '+String(x.Type)})));if(!$field.find('option').filter(function(){return String($(this).val())===current;}).length)current=$field.find('option').first().val()||'';$field.val(current);const type=fmap[current]?String(fmap[current].Type):'text';let o=String(f.Operator||$op.val()||'eq');$op.empty();ops(type).forEach(x=>$op.append($('<option>',{value:x[0],text:x[1]})));if(!$op.find('option').filter(function(){return String($(this).val())===o;}).length)o='eq';$op.val(o);if(type==='relation'){const target=String(fmap[current].RelationTargetType||''),cat=(schema.Catalog||[]).find(x=>String(x.Key)===target);$value.attr('placeholder',cat?'Entry-ID i '+String(cat.PluralLabel||target):'Target entry-ID');}else $value.attr('placeholder','Værdi');}}$r.attr('data-kind',kind);}
    $r.append($kind,$field,$op,$value,$('<button>',{type:'button',class:'button-link-delete h18-aq-remove-filter',text:'Fjern'}));$kind.on('change',function(){f.Field='';f.Operator='';refresh();sync();});$field.on('change',function(){f.Field=String($field.val()||'');f.Operator='';refresh();sync();});$op.add($value).on('change input',sync);refresh();return $r;}
    function groupRow(g){g=g||{Relation:'AND',Filters:[]};const $g=$('<div>',{class:'h18-aq-group'}),$head=$('<div>',{class:'h18-aq-head'}),$rel=$('<select>',{class:'h18-aq-relation'}).append('<option value="AND">AND i gruppen</option><option value="OR">OR i gruppen</option>').val(g.Relation||'AND'),$filters=$('<div>',{class:'h18-aq-filters'});(g.Filters||[]).slice(0,6).forEach(f=>$filters.append(filterRow(f)));$head.append($rel,$('<button>',{type:'button',class:'button h18-aq-add-filter',text:'+ Filter'}),$('<button>',{type:'button',class:'button-link-delete h18-aq-remove-group',text:'Fjern gruppe'}));$g.append($head,$filters);$rel.on('change',sync);return $g;}
    function render(){if(groups.length>4)groups=groups.slice(0,4);$root.empty();groups.forEach(g=>$root.append(groupRow(g)));sync();}render();$('#h18-aq-add-group').on('click',function(){if($root.children('.h18-aq-group').length>=4){window.alert('Maks. 4 grupper.');return;}$root.append(groupRow({Relation:'AND',Filters:[]}));sync();});$root.on('click','.h18-aq-add-filter',function(){const $g=$(this).closest('.h18-aq-group'),$filters=$g.find('>.h18-aq-filters');if($filters.children().length>=6){window.alert('Maks. 6 filtre pr. gruppe.');return;}$filters.append(filterRow({Kind:'field',Field:'',Operator:'eq',Value:''}));sync();}).on('click','.h18-aq-remove-filter',function(){$(this).closest('.h18-aq-filter').remove();sync();}).on('click','.h18-aq-remove-group',function(){$(this).closest('.h18-aq-group').remove();if(!$root.children().length)$root.append(groupRow({Relation:'AND',Filters:[]}));sync();});$('#h18-advanced-query-form').on('submit',sync);})();
'''
css += """

/* v0.5.29 – UD-056 Advanced Query */
.h18-aq-group{margin:12px 0;padding:12px;border:1px solid #dcdcde;border-radius:8px;background:#f6f7f7}.h18-aq-head{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}.h18-aq-filters{display:grid;gap:8px}.h18-aq-filter{display:grid;grid-template-columns:140px minmax(160px,1fr) 140px minmax(160px,1fr) auto;gap:8px;align-items:center}.h18-data-pagination{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0}.h18-data-pagination a{padding:5px 9px;border:1px solid currentColor;border-radius:5px;text-decoration:none}.h18-data-pagination a[aria-current=page]{font-weight:700;background:rgba(0,0,0,.06)}@media(max-width:1000px){.h18-aq-filter{grid-template-columns:1fr 1fr}.h18-aq-filter>*:last-child{justify-self:start}}
"""
readme=once(readme,'Version: 0.5.28','Version: 0.5.29','readme')
readme += """

## v0.5.29 – E5 UD-056 Advanced Query
- Advanced Query understøtter op til 4 AND/OR-grupper med op til 6 filtre pr. gruppe.
- Filtre kan blande primitive datafelter, Relation-felter og Data Tags taxonomy.
- Data entries får en privat `h18_data_tag` taxonomy med kommasepareret tag-editor.
- Relation-filter valideres mod relation-feltets scalar target-ID; Group/Repeater kan ikke bruges som direkte query-filter.
- Advanced preview og frontend-shortcode bruger samme normalized evaluator uden rå SQL.
- Pagination: 1–50 resultater pr. side, stabil sortering og separate query-string page keys pr. query.
- Kandidatsættet er bounded til 2000 publicerede entries og markerer `Truncated`, hvis grænsen nås.
- Page-editor schema forbliver 1.21; Data SchemaVersion forbliver 2.
"""
p.write_text(php);j.write_text(js);c.write_text(css);r.write_text(readme);print('v0.5.29 UD-056 Advanced Query patch applied')
