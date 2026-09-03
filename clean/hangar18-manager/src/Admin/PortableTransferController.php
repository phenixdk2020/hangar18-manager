<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Compatibility\LegacyStorageBridge;
use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;
use VisualDesignerManager\Modules\EventFieldRegistry;
use VisualDesignerManager\Modules\ModuleRegistry;
use VisualDesignerManager\Modules\ModuleStore;
use VisualDesignerManager\Modules\VehicleFieldRegistry;

final class PortableTransferController
{
    private const PAGE = 'vdm-transfer';
    private const EXPORT_ACTION = 'vdm_export_portable_site';
    private const PREFLIGHT_ACTION = 'vdm_import_preflight';
    private const IMPORT_ACTION = 'vdm_import_portable_site';
    private const EXPORT_NONCE = 'vdm_export_portable_site';
    private const PREFLIGHT_NONCE = 'vdm_import_preflight';
    private const IMPORT_NONCE = 'vdm_import_portable_site';
    private const FORMAT = 'Visual Designer Manager Portable Site';
    private const SCHEMA = '1.0';
    private const TRANSIENT_PREFIX = 'vdm_import_';
    private const RESULT_PREFIX = 'vdm_import_result_';
    private const STAGING_PREFIX = 'vdm-import-';
    private const MAX_ZIP_ENTRIES = 20000;
    private const MAX_UNCOMPRESSED_BYTES = 4294967296;

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 30);
        add_action('admin_post_' . self::EXPORT_ACTION, [self::class, 'exportSite']);
        add_action('admin_post_' . self::PREFLIGHT_ACTION, [self::class, 'preflightImport']);
        add_action('admin_post_' . self::IMPORT_ACTION, [self::class, 'importSite']);
    }

    public static function menu(): void
    {
        // Recovery/import route only. Normal users export from the unified Export page.
        add_submenu_page(
            null,
            'Import / recovery',
            'Import / recovery',
            'manage_options',
            self::PAGE,
            [self::class, 'render']
        );
    }

    public static function render(): void
    {
        self::guard();
        self::cleanupStaging();

        $token = sanitize_key((string) wp_unslash($_GET['vdm_token'] ?? ''));
        $status = sanitize_key((string) wp_unslash($_GET['vdm_status'] ?? ''));
        $staged = $token !== '' ? self::stagedPackage($token) : null;
        $lastResult = get_transient(self::RESULT_PREFIX . get_current_user_id());
        $maxUpload = size_format((int) wp_max_upload_size());
        ?>
        <div class="wrap vdm-transfer-admin">
            <style>.vdm-transfer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px;max-width:1100px}.vdm-transfer-card{background:#fff;border:1px solid #dcdcde;border-radius:4px;padding:20px;box-sizing:border-box}.vdm-transfer-card h2{margin-top:0}.vdm-transfer-card code{overflow-wrap:anywhere}</style>
            <h1>Visual Designer Manager – Eksport / import</h1>
            <p>Opret eller gendan en portabel VDM-sitepakke. Pakken er versionsstyret og kan bruges som migrationsgrundlag, når legacy-navne fjernes fra den aktive arkitektur.</p>

            <?php if ($status === 'preflight' && is_array($staged)) : ?>
                <div class="notice notice-info"><p><strong>Forhåndskontrol gennemført.</strong> Ingen data er importeret endnu.</p></div>
            <?php elseif ($status === 'imported' && is_array($lastResult)) : ?>
                <div class="notice notice-success"><p><strong>Import gennemført.</strong> VDM-data er gendannet fra den verificerede ZIP-pakke.</p></div>
                <?php self::renderCounts((array) ($lastResult['counts'] ?? []), 'Importerede elementer'); ?>
            <?php elseif ($status === 'error') : ?>
                <div class="notice notice-error"><p><strong>Overførslen blev afbrudt.</strong> <?php echo esc_html((string) wp_unslash($_GET['vdm_message'] ?? 'Kontrollér ZIP-pakken og prøv igen.')); ?></p></div>
            <?php endif; ?>

            <div class="vdm-transfer-grid">
                <section class="vdm-transfer-card">
                    <h2>Eksporter alt</h2>
                    <p>Samler VDM-sider og layouts, versionshistorik, Header/Footer-templates, moduldata, feltdefinitioner, navigation og mediebibliotekets originale filer i én portabel ZIP.</p>
                    <p><strong>Ekskluderet:</strong> WordPress core, brugerkonti/adgangskoder, database-login, API-hemmeligheder og andre plugins' filer.</p>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <input type="hidden" name="action" value="<?php echo esc_attr(self::EXPORT_ACTION); ?>">
                        <?php wp_nonce_field(self::EXPORT_NONCE); ?>
                        <?php submit_button('Eksporter alt som ZIP', 'primary', 'submit', false); ?>
                    </form>
                </section>

                <section class="vdm-transfer-card">
                    <h2>Importer ZIP</h2>
                    <p>Import starter altid med en read-only forhåndskontrol. ZIP'en valideres for format, schema, filstier og SHA-256 før knappen <em>Importer</em> bliver tilgængelig.</p>
                    <p>Maksimal uploadstørrelse på denne WordPress-installation: <strong><?php echo esc_html($maxUpload); ?></strong>.</p>
                    <form method="post" enctype="multipart/form-data" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <input type="hidden" name="action" value="<?php echo esc_attr(self::PREFLIGHT_ACTION); ?>">
                        <?php wp_nonce_field(self::PREFLIGHT_NONCE); ?>
                        <p><input type="file" name="vdm_package" accept=".zip,application/zip" required></p>
                        <?php submit_button('Kontrollér ZIP', 'secondary', 'submit', false); ?>
                    </form>
                </section>
            </div>

            <?php if (is_array($staged)) : ?>
                <section class="vdm-transfer-card" style="margin-top:20px;max-width:1100px">
                    <h2>Forhåndskontrol</h2>
                    <p><strong>Kilde:</strong> <?php echo esc_html((string) ($staged['summary']['sourceSite'] ?? 'Ukendt')); ?><br>
                       <strong>VDM-version:</strong> <?php echo esc_html((string) ($staged['summary']['managerVersion'] ?? 'Ukendt')); ?><br>
                       <strong>Schema:</strong> <?php echo esc_html((string) ($staged['summary']['schemaVersion'] ?? 'Ukendt')); ?><br>
                       <strong>ZIP SHA-256:</strong> <code><?php echo esc_html((string) ($staged['sha256'] ?? '')); ?></code></p>
                    <?php self::renderCounts((array) ($staged['summary']['counts'] ?? []), 'Indhold i pakken'); ?>
                    <?php if (!empty($staged['summary']['warnings']) && is_array($staged['summary']['warnings'])) : ?>
                        <h3>Bemærkninger</h3>
                        <ul>
                            <?php foreach ($staged['summary']['warnings'] as $warning) : ?>
                                <li><?php echo esc_html((string) $warning); ?></li>
                            <?php endforeach; ?>
                        </ul>
                    <?php endif; ?>
                    <p><strong>Importadfærd:</strong> eksisterende VDM-sider, templates, menuer, modulrecords og medier genbruges/matches hvor muligt. ID-referencer og interne URL'er remappes til målsitet.</p>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                        <input type="hidden" name="action" value="<?php echo esc_attr(self::IMPORT_ACTION); ?>">
                        <input type="hidden" name="vdm_token" value="<?php echo esc_attr($token); ?>">
                        <?php wp_nonce_field(self::IMPORT_NONCE); ?>
                        <?php submit_button('Importer verificeret ZIP', 'primary', 'submit', false); ?>
                    </form>
                </section>
            <?php endif; ?>
        </div>
        <?php
    }

    public static function exportSite(): void
    {
        self::guard();
        check_admin_referer(self::EXPORT_NONCE);
        if (!class_exists('ZipArchive')) {
            wp_die(esc_html__('PHP ZipArchive mangler på serveren.', 'visual-designer-manager'));
        }

        @set_time_limit(0);
        $tmp = tempnam(get_temp_dir(), 'vdm-export-');
        if (!is_string($tmp) || $tmp === '') {
            wp_die(esc_html__('Kunne ikke oprette midlertidig eksportfil.', 'visual-designer-manager'));
        }

        try {
            self::buildPortablePackage($tmp);
        } catch (\Throwable $error) {
            @unlink($tmp);
            wp_die(esc_html('Eksport fejlede: ' . $error->getMessage()));
        }

        $sha = hash_file('sha256', $tmp);
        $name = self::downloadName();
        nocache_headers();
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . $name . '"');
        header('Content-Length: ' . (string) filesize($tmp));
        if (is_string($sha)) {
            header('X-Visual-Designer-SHA256: ' . $sha);
        }
        readfile($tmp);
        @unlink($tmp);
        exit;
    }

    /**
     * Build the canonical portable site ZIP at a caller-provided path.
     * Used both by the hidden recovery route and Export > Eksporter alt.
     *
     * @return array{sha256:string,filename:string,counts:array<string,int>}
     */
    public static function buildPortablePackage(string $targetPath): array
    {
        if (!class_exists('ZipArchive')) {
            throw new \RuntimeException('PHP ZipArchive mangler på serveren.');
        }
        if ($targetPath === '') {
            throw new \RuntimeException('Målstien til portable sitepakken er tom.');
        }

        $zip = new \ZipArchive();
        $opened = $zip->open($targetPath, \ZipArchive::CREATE | \ZipArchive::OVERWRITE);
        if ($opened !== true) {
            throw new \RuntimeException('Kunne ikke oprette den portable ZIP-pakke.');
        }

        $files = [];
        try {
            $site = self::siteData();
            $pages = self::pageData();
            $templates = self::templateData();
            $modules = self::moduleData();
            $fields = self::fieldData();
            $navigation = self::navigationData();
            $media = self::addMedia($zip, $files);
            $legacyMap = self::legacyMap();

            self::addJson($zip, 'site.json', $site, $files);
            self::addJson($zip, 'pages/pages.json', $pages, $files);
            self::addJson($zip, 'templates/templates.json', $templates, $files);
            self::addJson($zip, 'modules/modules.json', $modules, $files);
            self::addJson($zip, 'modules/custom-fields.json', $fields, $files);
            self::addJson($zip, 'navigation/navigation.json', $navigation, $files);
            self::addJson($zip, 'media/media-index.json', $media, $files);
            self::addJson($zip, 'migration/legacy-map.json', $legacyMap, $files);

            $counts = [
                'pages' => count($pages['records']),
                'templates' => count($templates['records']),
                'modules' => count($modules['records']),
                'menus' => count($navigation['menus']),
                'media' => count($media['records']),
                'vehicleFields' => count($fields['vehicleFields']),
                'eventFields' => count($fields['eventFields']),
            ];
            $manifest = self::manifest($files, $counts, $site);
            $manifestJson = wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if (!is_string($manifestJson) || !$zip->addFromString('manifest.json', $manifestJson . "\n")) {
                throw new \RuntimeException('manifest.json kunne ikke oprettes.');
            }
        } catch (\Throwable $error) {
            $zip->close();
            @unlink($targetPath);
            throw $error;
        }

        if (!$zip->close()) {
            @unlink($targetPath);
            throw new \RuntimeException('ZIP-pakken kunne ikke afsluttes.');
        }
        if (!is_file($targetPath) || filesize($targetPath) === 0) {
            @unlink($targetPath);
            throw new \RuntimeException('Den portable sitepakke blev ikke oprettet korrekt.');
        }
        $sha = hash_file('sha256', $targetPath);
        if (!is_string($sha) || $sha === '') {
            @unlink($targetPath);
            throw new \RuntimeException('SHA-256 kunne ikke beregnes for den portable sitepakke.');
        }

        // v0.1.92: every newly built portable package passes the same full
        // schema/path/hash inspection that is used before import.
        $verification = self::inspectPackage($targetPath, true);

        return [
            'sha256' => $sha,
            'filename' => self::downloadName(),
            'counts' => $counts,
            'verification' => $verification,
        ];
    }

    /** @return array<string,mixed> */
    public static function verifyPortablePackage(string $path): array
    {
        if ($path === '' || !is_file($path)) {
            throw new \RuntimeException('Den portable sitepakke findes ikke.');
        }
        return self::inspectPackage($path, true);
    }

    public static function preflightImport(): void
    {
        self::guard();
        check_admin_referer(self::PREFLIGHT_NONCE);
        if (!class_exists('ZipArchive')) {
            self::redirectError('PHP ZipArchive mangler på serveren.');
        }
        if (!isset($_FILES['vdm_package']) || !is_array($_FILES['vdm_package'])) {
            self::redirectError('Der blev ikke modtaget en ZIP-fil.');
        }

        $upload = $_FILES['vdm_package'];
        $error = (int) ($upload['error'] ?? UPLOAD_ERR_NO_FILE);
        if ($error !== UPLOAD_ERR_OK) {
            self::redirectError('Upload fejlede med kode ' . $error . '.');
        }
        $source = (string) ($upload['tmp_name'] ?? '');
        $original = sanitize_file_name((string) ($upload['name'] ?? ''));
        if ($source === '' || !is_uploaded_file($source) || strtolower(pathinfo($original, PATHINFO_EXTENSION)) !== 'zip') {
            self::redirectError('Den uploadede fil er ikke en gyldig ZIP-upload.');
        }
        $size = (int) ($upload['size'] ?? 0);
        if ($size <= 0 || $size > (int) wp_max_upload_size()) {
            self::redirectError('ZIP-filen er tom eller overstiger WordPress uploadgrænsen.');
        }

        $path = tempnam(get_temp_dir(), self::STAGING_PREFIX);
        if (!is_string($path) || $path === '' || !move_uploaded_file($source, $path)) {
            if (is_string($path)) { @unlink($path); }
            self::redirectError('ZIP-filen kunne ikke flyttes til sikker staging.');
        }

        try {
            $summary = self::inspectPackage($path, true);
            $sha = hash_file('sha256', $path);
            if (!is_string($sha) || $sha === '') {
                throw new \RuntimeException('ZIP SHA-256 kunne ikke beregnes.');
            }
            $token = bin2hex(random_bytes(16));
            set_transient(self::TRANSIENT_PREFIX . get_current_user_id() . '_' . $token, [
                'path' => $path,
                'sha256' => $sha,
                'summary' => $summary,
                'createdUtc' => gmdate('c'),
            ], 30 * MINUTE_IN_SECONDS);
            wp_safe_redirect(admin_url('admin.php?page=' . self::PAGE . '&vdm_status=preflight&vdm_token=' . rawurlencode($token)));
            exit;
        } catch (\Throwable $error) {
            @unlink($path);
            self::redirectError('Forhåndskontrol fejlede: ' . $error->getMessage());
        }
    }

    public static function importSite(): void
    {
        self::guard();
        check_admin_referer(self::IMPORT_NONCE);
        $token = sanitize_key((string) wp_unslash($_POST['vdm_token'] ?? ''));
        $staged = $token !== '' ? self::stagedPackage($token) : null;
        if (!is_array($staged)) {
            self::redirectError('Den verificerede staging-pakke er udløbet eller mangler. Kør forhåndskontrol igen.');
        }
        $path = (string) ($staged['path'] ?? '');
        if ($path === '' || !is_file($path)) {
            self::redirectError('Staging-filen findes ikke længere. Kør forhåndskontrol igen.');
        }
        $sha = hash_file('sha256', $path);
        if (!is_string($sha) || !hash_equals((string) ($staged['sha256'] ?? ''), $sha)) {
            @unlink($path);
            delete_transient(self::TRANSIENT_PREFIX . get_current_user_id() . '_' . $token);
            self::redirectError('ZIP-filen er ændret efter forhåndskontrollen.');
        }

        @set_time_limit(0);
        try {
            self::inspectPackage($path, true);
            $result = self::applyPackage($path);
            set_transient(self::RESULT_PREFIX . get_current_user_id(), $result, 10 * MINUTE_IN_SECONDS);
            delete_transient(self::TRANSIENT_PREFIX . get_current_user_id() . '_' . $token);
            @unlink($path);
            wp_safe_redirect(admin_url('admin.php?page=' . self::PAGE . '&vdm_status=imported'));
            exit;
        } catch (\Throwable $error) {
            self::redirectError('Import fejlede: ' . $error->getMessage());
        }
    }

    /** @return array<string,mixed> */
    private static function siteData(): array
    {
        $theme = wp_get_theme();
        return [
            'schemaVersion' => self::SCHEMA,
            'product' => 'Visual Designer Manager',
            'managerVersion' => VDM_VERSION,
            'source' => [
                'name' => (string) get_bloginfo('name'),
                'homeUrl' => home_url('/'),
                'siteUrl' => site_url('/'),
                'language' => (string) get_bloginfo('language'),
            ],
            'settings' => [
                'siteIdentity' => [
                    'siteTitle' => (string) get_option('blogname', ''),
                    'tagline' => (string) get_option('blogdescription', ''),
                    'customLogoSourceId' => (int) get_theme_mod('custom_logo', 0),
                    'siteIconSourceId' => (int) get_option('site_icon', 0),
                    'organizationName' => (string) get_option(SiteSettingsController::OPTION_ORGANIZATION, ''),
                    'contactEmail' => (string) get_option(SiteSettingsController::OPTION_CONTACT_EMAIL, ''),
                    'contactPhone' => (string) get_option(SiteSettingsController::OPTION_CONTACT_PHONE, ''),
                ],
                'showOnFront' => (string) get_option('show_on_front', 'posts'),
                'pageOnFrontSourceId' => (int) get_option('page_on_front', 0),
                'pageForPostsSourceId' => (int) get_option('page_for_posts', 0),
                'permalinkStructure' => (string) get_option('permalink_structure', ''),
            ],
            'theme' => [
                'name' => (string) $theme->get('Name'),
                'stylesheet' => (string) $theme->get_stylesheet(),
                'template' => (string) $theme->get_template(),
            ],
        ];
    }

    /** @return array<string,mixed> */
    private static function pageData(): array
    {
        $pages = get_pages([
            'sort_column' => 'ID',
            'sort_order' => 'ASC',
            'post_status' => ['publish', 'draft', 'private', 'pending', 'future'],
        ]);
        $records = [];
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post) { continue; }
            $record = [
                'sourceId' => (int) $page->ID,
                'sourceUrl' => (string) get_permalink($page->ID),
                'path' => (string) get_page_uri($page->ID),
                'parentSourceId' => (int) $page->post_parent,
                'title' => (string) $page->post_title,
                'slug' => (string) $page->post_name,
                'status' => (string) $page->post_status,
                'dateGmt' => (string) $page->post_date_gmt,
                'modifiedGmt' => (string) $page->post_modified_gmt,
                'content' => (string) $page->post_content,
                'excerpt' => (string) $page->post_excerpt,
                'menuOrder' => (int) $page->menu_order,
                'template' => (string) get_post_meta($page->ID, '_wp_page_template', true),
                'featuredImageSourceId' => (int) get_post_thumbnail_id($page->ID),
                'headerTemplateChoice' => TemplateLayoutModel::pageChoice($page->ID, 'header'),
                'footerTemplateChoice' => TemplateLayoutModel::pageChoice($page->ID, 'footer'),
            ];
            if (metadata_exists('post', $page->ID, LayoutModel::META)) {
                $model = LayoutModel::get($page->ID);
                $record['visualDesigner'] = [
                    'version' => (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true),
                    'digest' => LayoutModel::structuralDigest($model),
                    'model' => $model,
                    'history' => LayoutModel::history($page->ID),
                ];
            }
            $records[] = $record;
        }
        return ['schemaVersion' => self::SCHEMA, 'records' => $records];
    }

    /** @return array<string,mixed> */
    private static function templateData(): array
    {
        TemplateLayoutModel::ensureMigrated();
        $records = [];
        foreach (['header', 'footer'] as $type) {
            foreach (TemplateLayoutModel::all($type) as $meta) {
                $id = (string) ($meta['id'] ?? '');
                if ($id === '') { continue; }
                $model = TemplateLayoutModel::model($id);
                $settings = TemplateLayoutModel::settings($id);
                $records[] = [
                    'sourceId' => $id,
                    'type' => $type,
                    'name' => (string) ($meta['name'] ?? ''),
                    'active' => !empty($meta['active']),
                    'createdUtc' => (string) ($meta['createdUtc'] ?? ''),
                    'updatedUtc' => (string) ($meta['updatedUtc'] ?? ''),
                    'version' => TemplateLayoutModel::version($id),
                    'digest' => TemplateLayoutModel::digest($model, $settings),
                    'model' => $model,
                    'settings' => $settings,
                    'history' => TemplateLayoutModel::history($id),
                ];
            }
        }
        return [
            'schemaVersion' => self::SCHEMA,
            'defaults' => [
                'header' => TemplateLayoutModel::defaultId('header'),
                'footer' => TemplateLayoutModel::defaultId('footer'),
            ],
            'records' => $records,
        ];
    }

    /** @return array<string,mixed> */
    private static function moduleData(): array
    {
        $ids = get_posts([
            'post_type' => ModuleStore::POST_TYPE,
            'post_status' => 'publish',
            'fields' => 'ids',
            'posts_per_page' => -1,
            'orderby' => 'ID',
            'order' => 'ASC',
            'no_found_rows' => true,
            'suppress_filters' => true,
        ]);
        $records = [];
        foreach ((array) $ids as $id) {
            $postId = (int) $id;
            $record = ModuleStore::get($postId);
            if (!is_array($record)) { continue; }
            $module = ModuleRegistry::key((string) get_post_meta($postId, ModuleStore::META_MODULE, true));
            if (!ModuleRegistry::supports($module)) { continue; }
            $records[] = [
                'sourcePostId' => $postId,
                'module' => $module,
                'record' => $record,
            ];
        }
        return [
            'schemaVersion' => self::SCHEMA,
            'catalog' => ModuleRegistry::editorCatalog(),
            'records' => $records,
        ];
    }

    /** @return array<string,mixed> */
    private static function fieldData(): array
    {
        return [
            'schemaVersion' => self::SCHEMA,
            'vehicleFields' => VehicleFieldRegistry::all(),
            'eventFields' => EventFieldRegistry::all(),
        ];
    }

    /** @return array<string,mixed> */
    private static function navigationData(): array
    {
        $menus = [];
        foreach (wp_get_nav_menus() as $menu) {
            $items = [];
            $rawItems = wp_get_nav_menu_items((int) $menu->term_id, ['post_status' => 'any']);
            foreach (is_array($rawItems) ? $rawItems : [] as $item) {
                $items[] = [
                    'sourceId' => (int) $item->ID,
                    'title' => (string) $item->title,
                    'url' => (string) $item->url,
                    'type' => (string) $item->type,
                    'object' => (string) $item->object,
                    'objectId' => (int) $item->object_id,
                    'parentSourceId' => (int) $item->menu_item_parent,
                    'order' => (int) $item->menu_order,
                    'target' => (string) $item->target,
                    'classes' => is_array($item->classes) ? array_values($item->classes) : [],
                    'attrTitle' => (string) $item->attr_title,
                    'description' => (string) $item->description,
                    'xfn' => (string) $item->xfn,
                ];
            }
            $menus[] = [
                'sourceId' => (int) $menu->term_id,
                'name' => (string) $menu->name,
                'slug' => (string) $menu->slug,
                'items' => $items,
            ];
        }
        return [
            'schemaVersion' => self::SCHEMA,
            'registeredLocations' => get_registered_nav_menus(),
            'locations' => get_nav_menu_locations(),
            'menus' => $menus,
        ];
    }

    /** @param array<int,array<string,mixed>> $files @return array<string,mixed> */
    private static function addMedia(\ZipArchive $zip, array &$files): array
    {
        $attachments = get_posts([
            'post_type' => 'attachment',
            'post_status' => 'inherit',
            'posts_per_page' => -1,
            'orderby' => 'ID',
            'order' => 'ASC',
        ]);
        $upload = wp_upload_dir();
        $baseDir = isset($upload['basedir']) ? realpath((string) $upload['basedir']) : false;
        if (!is_string($baseDir) || !is_dir($baseDir)) {
            throw new \RuntimeException('WordPress uploads-mappen kan ikke læses.');
        }
        $prefix = rtrim(str_replace('\\', '/', $baseDir), '/') . '/';
        $records = [];
        $added = [];
        foreach ($attachments as $attachment) {
            if (!$attachment instanceof \WP_Post) { continue; }
            $relative = ltrim(str_replace('\\', '/', (string) get_post_meta($attachment->ID, '_wp_attached_file', true)), '/');
            $archiveFile = '';
            $main = get_attached_file($attachment->ID, true);
            $real = is_string($main) ? realpath($main) : false;
            if (is_string($real) && is_file($real)) {
                $normalized = str_replace('\\', '/', $real);
                if (strpos($normalized, $prefix) === 0) {
                    if ($relative === '') { $relative = substr($normalized, strlen($prefix)); }
                    $archiveFile = 'media/files/' . ltrim($relative, '/');
                    if (!isset($added[$real])) {
                        self::addFile($zip, $real, $archiveFile, $files);
                        $added[$real] = true;
                    }
                }
            }
            $records[] = [
                'sourceId' => (int) $attachment->ID,
                'sourceUrl' => (string) wp_get_attachment_url($attachment->ID),
                'title' => (string) $attachment->post_title,
                'slug' => (string) $attachment->post_name,
                'mimeType' => (string) get_post_mime_type($attachment->ID),
                'dateGmt' => (string) $attachment->post_date_gmt,
                'modifiedGmt' => (string) $attachment->post_modified_gmt,
                'caption' => (string) $attachment->post_excerpt,
                'description' => (string) $attachment->post_content,
                'alt' => (string) get_post_meta($attachment->ID, '_wp_attachment_image_alt', true),
                'attachedFile' => $relative,
                'archiveFile' => $archiveFile,
                'metadata' => wp_get_attachment_metadata($attachment->ID),
            ];
        }
        return ['schemaVersion' => self::SCHEMA, 'records' => $records];
    }

    /** @return array<string,mixed> */
    private static function legacyMap(): array
    {
        return [
            'schemaVersion' => self::SCHEMA,
            'purpose' => 'Migration metadata only. Legacy identifiers are not canonical names for new VDM code.',
            'identifiers' => [
                ['legacy' => 'H18_CLEAN_VERSION/H18_CLEAN_FILE/H18_CLEAN_DIR/H18_CLEAN_URL', 'canonical' => 'VDM_VERSION/VDM_FILE/VDM_DIR/VDM_URL', 'policy' => 'compatibility-alias'],
                ['legacy' => '_h18_clean_layout_v1', 'canonical' => 'vdm.layout', 'policy' => 'portable-data-mapping'],
                ['legacy' => '_h18_clean_layout_history_v1', 'canonical' => 'vdm.layout.history', 'policy' => 'portable-data-mapping'],
                ['legacy' => '_h18_clean_layout_version_v1', 'canonical' => 'vdm.layout.version', 'policy' => 'portable-data-mapping'],
                ['legacy' => 'h18_module_item', 'canonical' => 'vdm.module.item', 'policy' => 'portable-data-mapping'],
                ['legacy' => '_h18_module_*', 'canonical' => 'vdm.module.*', 'policy' => 'portable-data-mapping'],
                ['legacy' => 'h18_vehicle_fields_v1', 'canonical' => 'vdm.fields.vehicles', 'policy' => 'portable-data-mapping'],
                ['legacy' => 'h18_event_fields_v1', 'canonical' => 'vdm.fields.events', 'policy' => 'portable-data-mapping'],
                ['legacy' => 'h18_clean_global_template_* / h18_clean_tpl_*', 'canonical' => 'vdm.templates.*', 'policy' => 'portable-data-mapping'],
                ['legacy' => 'h18-clean-* / h18_clean_*', 'canonical' => 'vdm-* / vdm_*', 'policy' => 'compatibility-or-migration'],
                ['legacy' => 'Hangar18_Manager', 'canonical' => 'none', 'policy' => 'temporary-theme-compatibility'],
            ],
        ];
    }

    /** @param array<int,array<string,mixed>> $files @param array<string,int> $counts @param array<string,mixed> $site */
    private static function manifest(array $files, array $counts, array $site): array
    {
        usort($files, static fn(array $a, array $b): int => strcmp((string) ($a['path'] ?? ''), (string) ($b['path'] ?? '')));
        $digestJson = wp_json_encode($files, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        return [
            'format' => self::FORMAT,
            'schemaVersion' => self::SCHEMA,
            'product' => 'Visual Designer Manager',
            'managerVersion' => VDM_VERSION,
            'exportType' => 'site',
            'createdUtc' => gmdate('c'),
            'sourceSite' => (string) ($site['source']['homeUrl'] ?? home_url('/')),
            'counts' => $counts,
            'fileCount' => count($files),
            'contentSha256' => is_string($digestJson) ? hash('sha256', $digestJson) : '',
            'files' => $files,
        ];
    }

    /** @return array<string,mixed> */
    private static function inspectPackage(string $path, bool $verifyHashes): array
    {
        $zip = new \ZipArchive();
        $opened = $zip->open($path, \ZipArchive::RDONLY);
        if ($opened !== true) {
            throw new \RuntimeException('ZIP-filen kan ikke åbnes.');
        }
        try {
            if ($zip->numFiles <= 0 || $zip->numFiles > self::MAX_ZIP_ENTRIES) {
                throw new \RuntimeException('ZIP indeholder et ugyldigt antal filer.');
            }
            $total = 0;
            for ($i = 0; $i < $zip->numFiles; $i++) {
                $stat = $zip->statIndex($i);
                if (!is_array($stat)) { throw new \RuntimeException('ZIP-indeks kunne ikke læses.'); }
                $name = (string) ($stat['name'] ?? '');
                if (!self::safeArchivePath($name)) {
                    throw new \RuntimeException('Usikker sti i ZIP: ' . $name);
                }
                $total += max(0, (int) ($stat['size'] ?? 0));
                if ($total > self::MAX_UNCOMPRESSED_BYTES) {
                    throw new \RuntimeException('ZIP overstiger den tilladte udpakkede størrelse.');
                }
            }

            $manifest = self::readJson($zip, 'manifest.json');
            if ((string) ($manifest['format'] ?? '') !== self::FORMAT || (string) ($manifest['exportType'] ?? '') !== 'site') {
                throw new \RuntimeException('ZIP er ikke en Visual Designer Manager sitepakke.');
            }
            $schema = (string) ($manifest['schemaVersion'] ?? '');
            if ($schema === '' || explode('.', $schema)[0] !== '1') {
                throw new \RuntimeException('Ikke-understøttet eksport-schema: ' . $schema);
            }
            foreach (['site.json', 'pages/pages.json', 'templates/templates.json', 'modules/modules.json', 'modules/custom-fields.json', 'navigation/navigation.json', 'media/media-index.json', 'migration/legacy-map.json'] as $required) {
                if ($zip->locateName($required, \ZipArchive::FL_NOCASE) === false) {
                    throw new \RuntimeException('Påkrævet fil mangler: ' . $required);
                }
            }

            if ($verifyHashes) {
                $manifestFiles = isset($manifest['files']) && is_array($manifest['files']) ? $manifest['files'] : [];
                foreach ($manifestFiles as $file) {
                    if (!is_array($file)) { throw new \RuntimeException('Ugyldig filpost i manifest.'); }
                    $entry = (string) ($file['path'] ?? '');
                    $expected = strtolower((string) ($file['sha256'] ?? ''));
                    if ($entry === '' || !self::safeArchivePath($entry) || $expected === '' || strlen($expected) !== 64) {
                        throw new \RuntimeException('Ugyldig filsignatur i manifest.');
                    }
                    $actual = self::hashZipEntry($zip, $entry);
                    if (!hash_equals($expected, $actual)) {
                        throw new \RuntimeException('SHA-256 matcher ikke for ' . $entry . '.');
                    }
                }
            }

            $site = self::readJson($zip, 'site.json');
            $pages = self::readJson($zip, 'pages/pages.json');
            $templates = self::readJson($zip, 'templates/templates.json');
            $modules = self::readJson($zip, 'modules/modules.json');
            $fields = self::readJson($zip, 'modules/custom-fields.json');
            $navigation = self::readJson($zip, 'navigation/navigation.json');
            $media = self::readJson($zip, 'media/media-index.json');
            $warnings = [];
            $siteSettings = isset($site['settings']) && is_array($site['settings']) ? $site['settings'] : [];
            if (!isset($siteSettings['siteIdentity']) || !is_array($siteSettings['siteIdentity'])) {
                $warnings[] = 'Pakken har ikke eksplicit site-identitet (VDM 0.1.85 eller ældre). Målsitets webstedstitel, slogan, logo, site-ikon og VDM-kontaktfelter bevares ved import.';
            }
            $sourceSite = (string) ($manifest['sourceSite'] ?? '');
            if ($sourceSite !== '' && untrailingslashit($sourceSite) !== untrailingslashit(home_url('/'))) {
                $warnings[] = 'Kildesitet er forskelligt fra målsitet. Side-, menu- og mediereferencer remappes hvor muligt.';
            }
            if ((string) ($manifest['managerVersion'] ?? '') !== VDM_VERSION) {
                $warnings[] = 'Pakken er oprettet med en anden VDM-version end den installerede. Schema 1.x er kompatibelt, men resultatet bør QA-kontrolleres.';
            }
            $missingMedia = 0;
            foreach ((array) ($media['records'] ?? []) as $record) {
                if (is_array($record) && (string) ($record['attachedFile'] ?? '') !== '' && (string) ($record['archiveFile'] ?? '') === '') { $missingMedia++; }
            }
            if ($missingMedia > 0) {
                $warnings[] = $missingMedia . ' medieposter mangler en fysisk originalfil i kildens uploads-mappe.';
            }
            return [
                'schemaVersion' => $schema,
                'managerVersion' => (string) ($manifest['managerVersion'] ?? ''),
                'sourceSite' => $sourceSite,
                'counts' => [
                    'pages' => count((array) ($pages['records'] ?? [])),
                    'templates' => count((array) ($templates['records'] ?? [])),
                    'modules' => count((array) ($modules['records'] ?? [])),
                    'menus' => count((array) ($navigation['menus'] ?? [])),
                    'media' => count((array) ($media['records'] ?? [])),
                    'vehicleFields' => count((array) ($fields['vehicleFields'] ?? [])),
                    'eventFields' => count((array) ($fields['eventFields'] ?? [])),
                ],
                'warnings' => $warnings,
            ];
        } finally {
            $zip->close();
        }
    }

    /** @return array<string,mixed> */
    private static function applyPackage(string $path): array
    {
        $zip = new \ZipArchive();
        $opened = $zip->open($path, \ZipArchive::RDONLY);
        if ($opened !== true) { throw new \RuntimeException('ZIP-filen kan ikke åbnes til import.'); }
        try {
            $site = self::readJson($zip, 'site.json');
            $sameSite = untrailingslashit((string) ($site['source']['homeUrl'] ?? '')) === untrailingslashit(home_url('/'));
            $pages = self::readJson($zip, 'pages/pages.json');
            $templates = self::readJson($zip, 'templates/templates.json');
            $modules = self::readJson($zip, 'modules/modules.json');
            $fields = self::readJson($zip, 'modules/custom-fields.json');
            $navigation = self::readJson($zip, 'navigation/navigation.json');
            $media = self::readJson($zip, 'media/media-index.json');

            [$mediaMap, $mediaUrlMap, $mediaCount] = self::importMedia($zip, (array) ($media['records'] ?? []));
            [$pageMap, $pageCount] = self::importPageSkeletons((array) ($pages['records'] ?? []), $sameSite);
            $pageUrlMap = self::pageUrlMap((array) ($pages['records'] ?? []), $pageMap);
            [$menuMap, $menuCount] = self::importNavigation((array) ($navigation['menus'] ?? []), (array) ($navigation['locations'] ?? []), $pageMap, $pageUrlMap, $mediaUrlMap);

            $maps = [
                'media' => $mediaMap,
                'page' => $pageMap,
                'menu' => $menuMap,
                'template' => [],
                'urls' => $pageUrlMap + $mediaUrlMap,
            ];
            [$templateMap, $templateCount] = self::importTemplates((array) ($templates['records'] ?? []), (array) ($templates['defaults'] ?? []), $maps);
            $maps['template'] = $templateMap;
            self::applyPagePayloads((array) ($pages['records'] ?? []), $pageMap, $maps);

            VehicleFieldRegistry::save((array) ($fields['vehicleFields'] ?? []));
            EventFieldRegistry::save((array) ($fields['eventFields'] ?? []));
            $moduleCount = self::importModules((array) ($modules['records'] ?? []), $maps);
            self::applySiteSettings($site, $pageMap, $mediaMap);
            flush_rewrite_rules(false);

            return [
                'completedUtc' => gmdate('c'),
                'counts' => [
                    'pages' => $pageCount,
                    'templates' => $templateCount,
                    'modules' => $moduleCount,
                    'menus' => $menuCount,
                    'media' => $mediaCount,
                    'vehicleFields' => count((array) ($fields['vehicleFields'] ?? [])),
                    'eventFields' => count((array) ($fields['eventFields'] ?? [])),
                ],
            ];
        } finally {
            $zip->close();
        }
    }

    /** @param array<int,mixed> $records @return array{0:array<int,int>,1:array<string,string>,2:int} */
    private static function importMedia(\ZipArchive $zip, array $records): array
    {
        $upload = wp_upload_dir();
        $baseDir = (string) ($upload['basedir'] ?? '');
        if ($baseDir === '' || !wp_mkdir_p($baseDir)) {
            throw new \RuntimeException('Målsitets uploads-mappe kan ikke klargøres.');
        }
        require_once ABSPATH . 'wp-admin/includes/image.php';
        $idMap = [];
        $urlMap = [];
        $count = 0;
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = absint($row['sourceId'] ?? 0);
            $relative = self::safeRelativeUploadPath((string) ($row['attachedFile'] ?? ''));
            $archive = (string) ($row['archiveFile'] ?? '');
            if ($sourceId <= 0 || $relative === '') { continue; }

            $existing = self::findAttachmentByRelativePath($relative);
            $targetPath = trailingslashit($baseDir) . $relative;
            if ($existing > 0) {
                if (!is_file($targetPath) && $archive !== '') {
                    if (!wp_mkdir_p(dirname($targetPath))) { throw new \RuntimeException('Medie-mappe kunne ikke oprettes: ' . dirname($targetPath)); }
                    self::extractZipFile($zip, $archive, $targetPath);
                }
                self::updateAttachmentRecord($existing, $row, $targetPath);
                $targetId = $existing;
            } else {
                if ($archive === '' || $zip->locateName($archive) === false) {
                    continue;
                }
                $targetDir = dirname($targetPath);
                if (!wp_mkdir_p($targetDir)) { throw new \RuntimeException('Medie-mappe kunne ikke oprettes: ' . $targetDir); }
                if (is_file($targetPath)) {
                    $base = wp_unique_filename($targetDir, basename($targetPath));
                    $targetPath = trailingslashit($targetDir) . $base;
                }
                self::extractZipFile($zip, $archive, $targetPath);
                $attachment = [
                    'post_mime_type' => sanitize_mime_type((string) ($row['mimeType'] ?? 'application/octet-stream')),
                    'post_title' => sanitize_text_field((string) ($row['title'] ?? pathinfo($targetPath, PATHINFO_FILENAME))),
                    'post_name' => sanitize_title((string) ($row['slug'] ?? '')),
                    'post_content' => wp_kses_post((string) ($row['description'] ?? '')),
                    'post_excerpt' => wp_kses_post((string) ($row['caption'] ?? '')),
                    'post_status' => 'inherit',
                ];
                $targetId = wp_insert_attachment($attachment, $targetPath, 0, true);
                if (is_wp_error($targetId)) { throw new \RuntimeException('Medie kunne ikke oprettes: ' . $targetId->get_error_message()); }
                $targetId = (int) $targetId;
                update_attached_file($targetId, $targetPath);
                self::updateAttachmentRecord($targetId, $row, $targetPath);
            }
            $idMap[$sourceId] = $targetId;
            $sourceUrl = (string) ($row['sourceUrl'] ?? '');
            $targetUrl = (string) wp_get_attachment_url($targetId);
            if ($sourceUrl !== '' && $targetUrl !== '') { $urlMap[$sourceUrl] = $targetUrl; }
            $count++;
        }
        return [$idMap, $urlMap, $count];
    }

    /** @param array<string,mixed> $row */
    private static function updateAttachmentRecord(int $attachmentId, array $row, string $path): void
    {
        wp_update_post([
            'ID' => $attachmentId,
            'post_title' => sanitize_text_field((string) ($row['title'] ?? '')),
            'post_content' => wp_kses_post((string) ($row['description'] ?? '')),
            'post_excerpt' => wp_kses_post((string) ($row['caption'] ?? '')),
        ]);
        update_post_meta($attachmentId, '_wp_attachment_image_alt', sanitize_text_field((string) ($row['alt'] ?? '')));
        if (is_file($path)) {
            update_attached_file($attachmentId, $path);
            $meta = wp_generate_attachment_metadata($attachmentId, $path);
            if (is_array($meta)) { wp_update_attachment_metadata($attachmentId, $meta); }
        }
    }

    private static function findAttachmentByRelativePath(string $relative): int
    {
        $ids = get_posts([
            'post_type' => 'attachment',
            'post_status' => 'inherit',
            'fields' => 'ids',
            'posts_per_page' => 1,
            'no_found_rows' => true,
            'suppress_filters' => true,
            'meta_query' => [[
                'key' => '_wp_attached_file',
                'value' => $relative,
                'compare' => '=',
            ]],
        ]);
        return !empty($ids) ? (int) $ids[0] : 0;
    }

    /** @param array<int,mixed> $records @return array{0:array<int,int>,1:int} */
    private static function importPageSkeletons(array $records, bool $sameSite): array
    {
        $map = [];
        $count = 0;
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = absint($row['sourceId'] ?? 0);
            $slug = sanitize_title((string) ($row['slug'] ?? ''));
            if ($sourceId <= 0 || $slug === '') { continue; }

            $targetId = 0;
            if ($sameSite) {
                $target = get_post($sourceId);
                $targetId = $target instanceof \WP_Post && $target->post_type === 'page' ? (int) $target->ID : 0;
            }
            if ($targetId <= 0) {
                $rawPath = trim((string) ($row['path'] ?? $slug), '/');
                $sourcePath = implode('/', array_filter(array_map('sanitize_title', explode('/', $rawPath))));
                $byPath = get_page_by_path($sourcePath !== '' ? $sourcePath : $slug, OBJECT, 'page');
                if ($byPath instanceof \WP_Post) { $targetId = (int) $byPath->ID; }
            }
            $status = sanitize_key((string) ($row['status'] ?? 'draft'));
            if (!in_array($status, ['publish', 'draft', 'private', 'pending', 'future'], true)) { $status = 'draft'; }
            $payload = [
                'post_type' => 'page',
                'post_title' => sanitize_text_field((string) ($row['title'] ?? '')),
                'post_name' => $slug,
                'post_status' => $status,
                'post_excerpt' => wp_kses_post((string) ($row['excerpt'] ?? '')),
                'menu_order' => (int) ($row['menuOrder'] ?? 0),
            ];
            $dateGmt = trim((string) ($row['dateGmt'] ?? ''));
            if ($dateGmt !== '' && $dateGmt !== '0000-00-00 00:00:00') {
                $payload['post_date_gmt'] = $dateGmt;
                $payload['post_date'] = get_date_from_gmt($dateGmt);
            }
            if ($targetId > 0) {
                $payload['ID'] = $targetId;
                $result = wp_update_post(wp_slash($payload), true);
            } else {
                $result = wp_insert_post(wp_slash($payload), true);
            }
            if (is_wp_error($result)) { throw new \RuntimeException('Side kunne ikke importeres: ' . $result->get_error_message()); }
            $targetId = (int) $result;
            $map[$sourceId] = $targetId;
            $count++;
        }
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = absint($row['sourceId'] ?? 0);
            $targetId = $map[$sourceId] ?? 0;
            if ($targetId <= 0) { continue; }
            $parentSource = absint($row['parentSourceId'] ?? 0);
            $parentTarget = $parentSource > 0 ? (int) ($map[$parentSource] ?? 0) : 0;
            wp_update_post(['ID' => $targetId, 'post_parent' => $parentTarget, 'post_name' => sanitize_title((string) ($row['slug'] ?? ''))]);
        }
        return [$map, $count];
    }

    /** @param array<int,mixed> $records @param array<int,int> $pageMap @return array<string,string> */
    private static function pageUrlMap(array $records, array $pageMap): array
    {
        $map = [];
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = absint($row['sourceId'] ?? 0);
            $sourceUrl = (string) ($row['sourceUrl'] ?? '');
            $targetId = (int) ($pageMap[$sourceId] ?? 0);
            $targetUrl = $targetId > 0 ? get_permalink($targetId) : '';
            if ($sourceUrl !== '' && is_string($targetUrl) && $targetUrl !== '') { $map[$sourceUrl] = $targetUrl; }
        }
        return $map;
    }

    /** @param array<int,mixed> $menus @param array<string,mixed> $locations @param array<int,int> $pageMap @param array<string,string> $pageUrlMap @param array<string,string> $mediaUrlMap @return array{0:array<int,int>,1:int} */
    private static function importNavigation(array $menus, array $locations, array $pageMap, array $pageUrlMap, array $mediaUrlMap): array
    {
        $menuMap = [];
        $count = 0;
        foreach ($menus as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = absint($row['sourceId'] ?? 0);
            $name = sanitize_text_field((string) ($row['name'] ?? ''));
            $slug = sanitize_title((string) ($row['slug'] ?? $name));
            if ($sourceId <= 0 || $name === '') { continue; }
            $object = wp_get_nav_menu_object($sourceId);
            if (!$object || (string) $object->slug !== $slug) { $object = wp_get_nav_menu_object($slug); }
            if (!$object) {
                $created = wp_create_nav_menu($name);
                if (is_wp_error($created)) { throw new \RuntimeException('Menu kunne ikke oprettes: ' . $created->get_error_message()); }
                $targetMenuId = (int) $created;
            } else {
                $targetMenuId = (int) $object->term_id;
                foreach ((array) wp_get_nav_menu_items($targetMenuId, ['post_status' => 'any']) as $existingItem) {
                    if ($existingItem instanceof \WP_Post) { wp_delete_post($existingItem->ID, true); }
                }
            }
            $menuMap[$sourceId] = $targetMenuId;
            $itemMap = [];
            $itemArgs = [];
            $items = isset($row['items']) && is_array($row['items']) ? $row['items'] : [];
            usort($items, static fn($a, $b): int => ((int) ($a['order'] ?? 0)) <=> ((int) ($b['order'] ?? 0)));
            foreach ($items as $item) {
                if (!is_array($item)) { continue; }
                $sourceItemId = absint($item['sourceId'] ?? 0);
                if ($sourceItemId <= 0) { continue; }
                $type = sanitize_key((string) ($item['type'] ?? 'custom'));
                $objectName = sanitize_key((string) ($item['object'] ?? 'custom'));
                $objectId = absint($item['objectId'] ?? 0);
                if ($type === 'post_type' && $objectName === 'page') {
                    $objectId = (int) ($pageMap[$objectId] ?? 0);
                    if ($objectId <= 0) { $type = 'custom'; $objectName = 'custom'; }
                }
                $url = self::remapString((string) ($item['url'] ?? ''), $pageUrlMap + $mediaUrlMap);
                $args = [
                    'menu-item-title' => sanitize_text_field((string) ($item['title'] ?? '')),
                    'menu-item-status' => 'publish',
                    'menu-item-type' => $type,
                    'menu-item-object' => $objectName,
                    'menu-item-object-id' => $objectId,
                    'menu-item-url' => esc_url_raw($url),
                    'menu-item-parent-id' => 0,
                    'menu-item-position' => max(1, (int) ($item['order'] ?? 1)),
                    'menu-item-target' => sanitize_key((string) ($item['target'] ?? '')),
                    'menu-item-classes' => implode(' ', array_map('sanitize_html_class', (array) ($item['classes'] ?? []))),
                    'menu-item-attr-title' => sanitize_text_field((string) ($item['attrTitle'] ?? '')),
                    'menu-item-description' => sanitize_textarea_field((string) ($item['description'] ?? '')),
                    'menu-item-xfn' => sanitize_text_field((string) ($item['xfn'] ?? '')),
                ];
                if ($type !== 'custom' && $objectId <= 0) {
                    $args['menu-item-type'] = 'custom';
                    $args['menu-item-object'] = 'custom';
                    $args['menu-item-object-id'] = 0;
                }
                $newItemId = wp_update_nav_menu_item($targetMenuId, 0, $args);
                if (is_wp_error($newItemId)) { throw new \RuntimeException('Menupunkt kunne ikke oprettes: ' . $newItemId->get_error_message()); }
                $itemMap[$sourceItemId] = (int) $newItemId;
                $itemArgs[$sourceItemId] = $args;
            }
            foreach ($items as $item) {
                if (!is_array($item)) { continue; }
                $sourceItemId = absint($item['sourceId'] ?? 0);
                $targetItemId = (int) ($itemMap[$sourceItemId] ?? 0);
                if ($targetItemId <= 0 || !isset($itemArgs[$sourceItemId])) { continue; }
                $parentSource = absint($item['parentSourceId'] ?? 0);
                $args = $itemArgs[$sourceItemId];
                $args['menu-item-parent-id'] = (int) ($itemMap[$parentSource] ?? 0);
                $updated = wp_update_nav_menu_item($targetMenuId, $targetItemId, $args);
                if (is_wp_error($updated)) { throw new \RuntimeException('Menupunktets hierarki kunne ikke gendannes: ' . $updated->get_error_message()); }
            }
            $count++;
        }

        $registered = get_registered_nav_menus();
        $targetLocations = get_nav_menu_locations();
        foreach ($locations as $location => $sourceMenuId) {
            $location = sanitize_key((string) $location);
            if (!isset($registered[$location])) { continue; }
            $sourceMenuId = absint($sourceMenuId);
            if (isset($menuMap[$sourceMenuId])) { $targetLocations[$location] = $menuMap[$sourceMenuId]; }
        }
        set_theme_mod('nav_menu_locations', $targetLocations);
        return [$menuMap, $count];
    }

    /** @param array<int,mixed> $records @param array<string,mixed> $defaults @param array<string,mixed> $maps @return array{0:array<string,string>,1:int} */
    private static function importTemplates(array $records, array $defaults, array $maps): array
    {
        $idMap = [];
        $count = 0;
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = sanitize_key((string) ($row['sourceId'] ?? ''));
            if ($sourceId === '') { continue; }
            $payload = $row;
            $payload['model'] = self::remapValue((array) ($row['model'] ?? []), $maps);
            $history = [];
            foreach ((array) ($row['history'] ?? []) as $entry) {
                if (!is_array($entry)) { continue; }
                $entry['model'] = self::remapValue((array) ($entry['model'] ?? []), $maps);
                $history[] = $entry;
            }
            $payload['history'] = $history;
            $targetId = LegacyStorageBridge::importTemplateSnapshot($payload);
            $idMap[$sourceId] = $targetId;
            $count++;
        }
        LegacyStorageBridge::importTemplateDefaults($defaults, $idMap);
        return [$idMap, $count];
    }

    /** @param array<int,mixed> $records @param array<int,int> $pageMap @param array<string,mixed> $maps */
    private static function applyPagePayloads(array $records, array $pageMap, array $maps): void
    {
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $sourceId = absint($row['sourceId'] ?? 0);
            $targetId = (int) ($pageMap[$sourceId] ?? 0);
            if ($targetId <= 0) { continue; }
            $content = self::remapString((string) ($row['content'] ?? ''), (array) ($maps['urls'] ?? []));
            wp_update_post(wp_slash(['ID' => $targetId, 'post_content' => $content]));
            $template = sanitize_text_field((string) ($row['template'] ?? ''));
            if ($template !== '') { update_post_meta($targetId, '_wp_page_template', $template); }

            $featuredSource = absint($row['featuredImageSourceId'] ?? 0);
            if ($featuredSource > 0 && isset($maps['media'][$featuredSource])) {
                set_post_thumbnail($targetId, (int) $maps['media'][$featuredSource]);
            } else {
                delete_post_thumbnail($targetId);
            }

            if (isset($row['visualDesigner']) && is_array($row['visualDesigner'])) {
                $vd = $row['visualDesigner'];
                $model = LayoutModel::normalize((array) self::remapValue((array) ($vd['model'] ?? []), $maps));
                $history = [];
                foreach ((array) ($vd['history'] ?? []) as $entry) {
                    if (!is_array($entry)) { continue; }
                    if (isset($entry['model']) && is_array($entry['model'])) {
                        $entry['model'] = LayoutModel::normalize((array) self::remapValue($entry['model'], $maps));
                        $entry['digest'] = LayoutModel::structuralDigest($entry['model']);
                    }
                    $history[] = $entry;
                }
                update_post_meta($targetId, LayoutModel::META, $model);
                update_post_meta($targetId, LayoutModel::HISTORY_META, array_slice($history, -LayoutModel::MAX_HISTORY));
                update_post_meta($targetId, LayoutModel::VERSION_META, max(0, (int) ($vd['version'] ?? 0)));
            } else {
                delete_post_meta($targetId, LayoutModel::META);
                delete_post_meta($targetId, LayoutModel::HISTORY_META);
                delete_post_meta($targetId, LayoutModel::VERSION_META);
            }

            $headerChoice = sanitize_key((string) ($row['headerTemplateChoice'] ?? 'auto'));
            $footerChoice = sanitize_key((string) ($row['footerTemplateChoice'] ?? 'auto'));
            if (isset($maps['template'][$headerChoice])) { $headerChoice = (string) $maps['template'][$headerChoice]; }
            if (isset($maps['template'][$footerChoice])) { $footerChoice = (string) $maps['template'][$footerChoice]; }
            TemplateLayoutModel::setPageChoice($targetId, 'header', $headerChoice !== '' ? $headerChoice : 'auto');
            TemplateLayoutModel::setPageChoice($targetId, 'footer', $footerChoice !== '' ? $footerChoice : 'auto');
        }
    }

    /** @param array<int,mixed> $records @param array<string,mixed> $maps */
    private static function importModules(array $records, array $maps): int
    {
        $count = 0;
        foreach ($records as $row) {
            if (!is_array($row)) { continue; }
            $module = ModuleRegistry::key((string) ($row['module'] ?? ''));
            $record = isset($row['record']) && is_array($row['record']) ? $row['record'] : [];
            if (!ModuleRegistry::supports($module) || $record === []) { continue; }
            $record = (array) self::remapValue($record, $maps);
            $recordId = (string) ($record['id'] ?? '');
            $existing = $recordId !== '' ? ModuleStore::findByRecordId($module, $recordId) : null;
            $targetPostId = is_array($existing) ? (int) ($existing['postId'] ?? 0) : 0;
            $saved = ModuleStore::save($module, $record, $targetPostId);
            if (is_wp_error($saved)) { throw new \RuntimeException('Modulrecord kunne ikke importeres: ' . $saved->get_error_message()); }
            $count++;
        }
        return $count;
    }

    /** @param array<string,mixed> $site @param array<int,int> $pageMap @param array<int,int> $mediaMap */
    private static function applySiteSettings(array $site, array $pageMap, array $mediaMap): void
    {
        $settings = isset($site['settings']) && is_array($site['settings']) ? $site['settings'] : [];
        $identity = isset($settings['siteIdentity']) && is_array($settings['siteIdentity']) ? $settings['siteIdentity'] : null;
        if (is_array($identity)) {
            if (array_key_exists('siteTitle', $identity)) { update_option('blogname', sanitize_text_field((string) $identity['siteTitle'])); }
            if (array_key_exists('tagline', $identity)) { update_option('blogdescription', sanitize_text_field((string) $identity['tagline'])); }
            if (array_key_exists('organizationName', $identity)) { update_option(SiteSettingsController::OPTION_ORGANIZATION, sanitize_text_field((string) $identity['organizationName'])); }
            if (array_key_exists('contactEmail', $identity)) { update_option(SiteSettingsController::OPTION_CONTACT_EMAIL, sanitize_email((string) $identity['contactEmail'])); }
            if (array_key_exists('contactPhone', $identity)) { update_option(SiteSettingsController::OPTION_CONTACT_PHONE, sanitize_text_field((string) $identity['contactPhone'])); }

            if (array_key_exists('customLogoSourceId', $identity)) {
                $sourceLogo = absint($identity['customLogoSourceId']);
                if ($sourceLogo === 0) {
                    remove_theme_mod('custom_logo');
                } elseif (isset($mediaMap[$sourceLogo])) {
                    set_theme_mod('custom_logo', (int) $mediaMap[$sourceLogo]);
                }
            }
            if (array_key_exists('siteIconSourceId', $identity)) {
                $sourceIcon = absint($identity['siteIconSourceId']);
                if ($sourceIcon === 0) {
                    delete_option('site_icon');
                } elseif (isset($mediaMap[$sourceIcon])) {
                    update_option('site_icon', (int) $mediaMap[$sourceIcon]);
                }
            }
        }

        $show = (string) ($settings['showOnFront'] ?? 'posts');
        update_option('show_on_front', $show === 'page' ? 'page' : 'posts');
        $frontSource = absint($settings['pageOnFrontSourceId'] ?? 0);
        $postsSource = absint($settings['pageForPostsSourceId'] ?? 0);
        update_option('page_on_front', (int) ($pageMap[$frontSource] ?? 0));
        update_option('page_for_posts', (int) ($pageMap[$postsSource] ?? 0));
        if (array_key_exists('permalinkStructure', $settings)) {
            update_option('permalink_structure', (string) $settings['permalinkStructure']);
        }
    }

    /** @param mixed $value @param array<string,mixed> $maps @return mixed */
    private static function remapValue($value, array $maps, string $key = '')
    {
        $lower = strtolower($key);
        if (is_int($value) || (is_string($value) && ctype_digit($value))) {
            $number = (int) $value;
            if (in_array($lower, ['mediaid', 'featuredmediaid', 'imageid', 'attachmentid', 'logoid'], true) && isset($maps['media'][$number])) {
                return is_string($value) ? (string) $maps['media'][$number] : (int) $maps['media'][$number];
            }
            if ($lower === 'pageid' && isset($maps['page'][$number])) {
                return is_string($value) ? (string) $maps['page'][$number] : (int) $maps['page'][$number];
            }
            if ($lower === 'menuid' && isset($maps['menu'][$number])) {
                return is_string($value) ? (string) $maps['menu'][$number] : (int) $maps['menu'][$number];
            }
        }
        if (is_string($value)) {
            if ($lower === 'templateid' && isset($maps['template'][$value])) { return (string) $maps['template'][$value]; }
            return self::remapString($value, (array) ($maps['urls'] ?? []));
        }
        if (!is_array($value)) { return $value; }
        $out = [];
        foreach ($value as $childKey => $child) {
            if (in_array(strtolower((string) $childKey), ['imageids', 'mediaids', 'attachmentids'], true) && is_array($child)) {
                $mapped = [];
                foreach ($child as $id) {
                    $source = absint($id);
                    if ($source > 0) { $mapped[] = (int) ($maps['media'][$source] ?? $source); }
                }
                $out[$childKey] = $mapped;
                continue;
            }
            $out[$childKey] = self::remapValue($child, $maps, (string) $childKey);
        }
        return $out;
    }

    /** @param array<string,string> $urlMap */
    private static function remapString(string $value, array $urlMap): string
    {
        if ($value === '' || !$urlMap) { return $value; }
        uksort($urlMap, static fn(string $a, string $b): int => strlen($b) <=> strlen($a));
        return strtr($value, $urlMap);
    }

    private static function extractZipFile(\ZipArchive $zip, string $archivePath, string $targetPath): void
    {
        if (!self::safeArchivePath($archivePath) || strpos($archivePath, 'media/files/') !== 0) {
            throw new \RuntimeException('Ugyldig mediesti i ZIP.');
        }
        $stream = $zip->getStream($archivePath);
        if (!is_resource($stream)) { throw new \RuntimeException('Mediefilen kan ikke læses fra ZIP: ' . $archivePath); }
        $out = fopen($targetPath, 'wb');
        if (!is_resource($out)) { fclose($stream); throw new \RuntimeException('Mediefilen kan ikke skrives: ' . $targetPath); }
        try {
            while (!feof($stream)) {
                $chunk = fread($stream, 1048576);
                if ($chunk === false) { throw new \RuntimeException('Fejl under læsning af mediefil.'); }
                if ($chunk !== '' && fwrite($out, $chunk) === false) { throw new \RuntimeException('Fejl under skrivning af mediefil.'); }
            }
        } finally {
            fclose($stream);
            fclose($out);
        }
    }

    /** @return array<string,mixed> */
    private static function readJson(\ZipArchive $zip, string $name): array
    {
        $payload = $zip->getFromName($name);
        if (!is_string($payload) || $payload === '') { throw new \RuntimeException($name . ' mangler eller er tom.'); }
        $decoded = json_decode($payload, true);
        if (!is_array($decoded)) { throw new \RuntimeException($name . ' indeholder ugyldig JSON.'); }
        return $decoded;
    }

    private static function hashZipEntry(\ZipArchive $zip, string $name): string
    {
        $stream = $zip->getStream($name);
        if (!is_resource($stream)) { throw new \RuntimeException('ZIP-filen mangler: ' . $name); }
        $hash = hash_init('sha256');
        try {
            while (!feof($stream)) {
                $chunk = fread($stream, 1048576);
                if ($chunk === false) { throw new \RuntimeException('ZIP-fil kunne ikke hashes: ' . $name); }
                if ($chunk !== '') { hash_update($hash, $chunk); }
            }
        } finally {
            fclose($stream);
        }
        return hash_final($hash);
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addJson(\ZipArchive $zip, string $archivePath, array $value, array &$files): void
    {
        $json = wp_json_encode($value, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) { throw new \RuntimeException($archivePath . ' kunne ikke serialiseres.'); }
        $payload = $json . "\n";
        if (!$zip->addFromString($archivePath, $payload)) { throw new \RuntimeException($archivePath . ' kunne ikke tilføjes til ZIP.'); }
        $files[] = ['path' => $archivePath, 'size' => strlen($payload), 'sha256' => hash('sha256', $payload)];
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addFile(\ZipArchive $zip, string $source, string $archivePath, array &$files): void
    {
        if (!self::safeArchivePath($archivePath) || !$zip->addFile($source, $archivePath)) {
            throw new \RuntimeException('Filen kunne ikke tilføjes: ' . $archivePath);
        }
        $hash = hash_file('sha256', $source);
        $size = filesize($source);
        $files[] = ['path' => $archivePath, 'size' => $size !== false ? (int) $size : 0, 'sha256' => is_string($hash) ? $hash : ''];
    }

    private static function safeArchivePath(string $path): bool
    {
        if ($path === '' || strpos($path, "\0") !== false || str_contains($path, '\\') || str_starts_with($path, '/') || preg_match('/^[A-Za-z]:/', $path)) { return false; }
        $parts = explode('/', $path);
        foreach ($parts as $part) {
            if ($part === '..') { return false; }
        }
        return true;
    }

    private static function safeRelativeUploadPath(string $path): string
    {
        $path = ltrim(str_replace('\\', '/', trim($path)), '/');
        if ($path === '' || !self::safeArchivePath($path) || str_contains($path, '://')) { return ''; }
        return implode('/', array_map('sanitize_file_name', explode('/', $path)));
    }

    /** @return array<string,mixed>|null */
    private static function stagedPackage(string $token): ?array
    {
        if (!preg_match('/^[a-f0-9]{32}$/', $token)) { return null; }
        $value = get_transient(self::TRANSIENT_PREFIX . get_current_user_id() . '_' . $token);
        return is_array($value) ? $value : null;
    }

    private static function cleanupStaging(): void
    {
        $pattern = trailingslashit(get_temp_dir()) . self::STAGING_PREFIX . '*';
        foreach ((array) glob($pattern) as $path) {
            if (is_string($path) && is_file($path) && filemtime($path) !== false && filemtime($path) < time() - (2 * HOUR_IN_SECONDS)) {
                @unlink($path);
            }
        }
    }

    /** @param array<string,mixed> $counts */
    private static function renderCounts(array $counts, string $title): void
    {
        $labels = [
            'pages' => 'Sider',
            'templates' => 'Header/Footer-templates',
            'modules' => 'Modulrecords',
            'menus' => 'Menuer',
            'media' => 'Medier',
            'vehicleFields' => 'Køretøjsfelter',
            'eventFields' => 'Eventfelter',
        ];
        echo '<h3>' . esc_html($title) . '</h3><table class="widefat striped" style="max-width:720px"><thead><tr><th>Type</th><th>Antal</th></tr></thead><tbody>';
        foreach ($labels as $key => $label) {
            echo '<tr><td>' . esc_html($label) . '</td><td>' . esc_html((string) ((int) ($counts[$key] ?? 0))) . '</td></tr>';
        }
        echo '</tbody></table>';
    }

    private static function downloadName(): string
    {
        $site = sanitize_title((string) get_bloginfo('name'));
        if ($site === '') { $site = 'wordpress-site'; }
        return 'visual-designer-' . $site . '-site-' . gmdate('Ymd-His') . '.zip';
    }

    private static function redirectError(string $message): void
    {
        wp_safe_redirect(admin_url('admin.php?page=' . self::PAGE . '&vdm_status=error&vdm_message=' . rawurlencode($message)));
        exit;
    }

    private static function guard(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
    }

    private function __construct()
    {
    }
}
