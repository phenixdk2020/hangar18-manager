<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Model\LayoutModel;

final class ExportController
{
    private const ACTION = 'h18_clean_export_package';
    private const NONCE = 'h18_clean_export_package';
    private const SCHEMA = 1;

    /** @var array<string,string> */
    private const LABELS = [
        'all' => 'Alt',
        'plugin' => 'Plugin',
        'theme' => 'Tema',
        'pages' => 'Webpages',
        'navigation' => 'Navigation',
        'images' => 'Billeder',
        'documents' => 'Dokumenter',
        'videos' => 'Video',
        'media' => 'Alle medier',
    ];

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 7);
        add_action('admin_post_' . self::ACTION, [self::class, 'export']);
    }

    public static function menu(): void
    {
        add_submenu_page(
            AdminController::MENU,
            'Export',
            'Export',
            'manage_options',
            'h18-clean-export',
            [self::class, 'render']
        );
    }

    public static function render(): void
    {
        self::guard();
        $theme = wp_get_theme();
        $zipReady = class_exists('ZipArchive');
        $parent = $theme->parent();

        echo '<div class="wrap h18-manager-admin">';
        echo '<h1>Export</h1>';
        echo '<p class="h18-manager-description">Eksportér hele installationens VDM-indhold eller vælg enkelte dele. <strong>Eksporter alt</strong> samler plugin, aktivt tema og en komplet portabel sitepakke i én ZIP.</p>';

        if (!$zipReady) {
            echo '<div class="notice notice-error"><p><strong>ZIP er ikke tilgængelig.</strong> PHP-udvidelsen <code>ZipArchive</code> skal være aktiv, før eksport kan køres.</p></div>';
        }

        echo '<div class="h18-manager-card-grid">';
        self::card('all', 'Eksporter alt', 'Komplet arkiv med Visual Designer Manager-plugin, aktivt tema/parent-theme og en direkte importerbar portabel VDM-sitepakke med sider/layouts/historik, Header/Footer, Events, Køretøjer, Billedgalleri, feltdefinitioner, navigation, medier og Siteindstillinger.', $zipReady);
        self::card('plugin', 'Export Plugin', 'Hele den installerede Visual Designer Manager-pluginmappe med filmanifest og SHA-256 pr. fil.', $zipReady);

        $themeText = 'Aktivt tema: ' . esc_html((string) $theme->get('Name')) . ' ' . esc_html((string) $theme->get('Version')) . '.';
        if ($parent instanceof \WP_Theme) {
            $themeText .= ' Parent-theme <strong>' . esc_html((string) $parent->get('Name')) . '</strong> inkluderes også, så child-theme pakken kan flyttes samlet.';
        }
        self::card('theme', 'Export Tema', $themeText, $zipReady);

        self::card('pages', 'Export Webpages', 'Alle WordPress-sider som struktureret JSON inklusive canonical Visual Designer-model, versionshistorik og kendte mediereferencer.', $zipReady);
        self::card('navigation', 'Export Navigation', 'WordPress-menuer, menupunkter, parent-hierarki og aktive theme-locations som struktureret JSON.', $zipReady);
        self::card('images', 'Export Billeder', 'Billeder fra Media Library med filer, attachment-metadata, alt-tekst og checksums.', $zipReady);
        self::card('documents', 'Export Dokumenter', 'Dokumenter som PDF, Word, Excel, tekst/CSV m.fl. fra Media Library.', $zipReady);
        self::card('videos', 'Export Video', 'Uploadede videofiler fra Media Library med metadata og checksums.', $zipReady);
        self::card('media', 'Export Alle medier', 'Alle uploadede Media Library-filer samlet i én ZIP.', $zipReady);

        echo '</div>';

        echo '<section class="h18-manager-card"><h2>Integritet og sikkerhed</h2><ul class="h18-manager-list">';
        echo '<li>Kun administratorer med <code>manage_options</code> kan køre Export.</li>';
        echo '<li>ZIP-filer oprettes i et midlertidigt område og slettes efter download.</li>';
        echo '<li>Hver pakke indeholder <code>visual-designer-export.json</code> med filmanifest, content-digest og SHA-256 pr. fil.</li>';
        echo '<li>Den færdige ZIPs SHA-256 sendes desuden i HTTP-headeren <code>X-Visual-Designer-SHA256</code>.</li>';
        echo '<li>Kendte secret-filer og filer uden for plugin/theme/upload-roden eksporteres ikke.</li>';
        echo '</ul></section>';
        echo '</div>';
    }

    public static function export(): void
    {
        self::guard();
        $kind = sanitize_key((string) ($_POST['export_kind'] ?? ''));
        if (!isset(self::LABELS[$kind])) {
            wp_die(esc_html__('Ukendt exporttype.', 'visual-designer-manager'));
        }
        check_admin_referer(self::NONCE . '_' . $kind);
        if (!class_exists('ZipArchive')) {
            wp_die(esc_html__('PHP ZipArchive er ikke tilgængelig på serveren.', 'visual-designer-manager'));
        }

        if (function_exists('set_time_limit')) {
            @set_time_limit(0);
        }

        $tmp = wp_tempnam('visual-designer-export-' . $kind . '.zip');
        if (!is_string($tmp) || $tmp === '') {
            wp_die(esc_html__('Kunne ikke oprette midlertidig exportfil.', 'visual-designer-manager'));
        }

        $zip = new \ZipArchive();
        $opened = $zip->open($tmp, \ZipArchive::OVERWRITE);
        if ($opened !== true) {
            @unlink($tmp);
            wp_die(esc_html__('Kunne ikke oprette ZIP-export.', 'visual-designer-manager'));
        }

        $files = [];
        $recordCount = 0;
        $portableTmp = null;

        try {
            switch ($kind) {
                case 'all':
                    $recordCount += self::addDirectory(
                        $zip,
                        H18_CLEAN_DIR,
                        'plugin/' . basename(untrailingslashit(H18_CLEAN_DIR)),
                        $files
                    );
                    self::addJson($zip, 'plugin.json', [
                        'schemaVersion' => self::SCHEMA,
                        'product' => 'Visual Designer Manager',
                        'internalVersion' => H18_CLEAN_VERSION,
                        'sourceDirectory' => basename(untrailingslashit(H18_CLEAN_DIR)),
                    ], $files);
                    $recordCount += self::addTheme($zip, $files);

                    $portableTmp = tempnam(get_temp_dir(), 'vdm-portable-all-');
                    if (!is_string($portableTmp) || $portableTmp === '') {
                        throw new \RuntimeException('Kunne ikke oprette midlertidig portabel sitepakke.');
                    }
                    $portable = PortableTransferController::buildPortablePackage($portableTmp);
                    self::addFile($zip, $portableTmp, 'portable-site/' . sanitize_file_name((string) $portable['filename']), $files);
                    $portableCounts = isset($portable['counts']) && is_array($portable['counts']) ? $portable['counts'] : [];
                    $recordCount += array_sum(array_map('intval', $portableCounts));
                    self::addJson($zip, 'all.json', [
                        'schemaVersion' => self::SCHEMA,
                        'type' => 'all',
                        'portableSite' => [
                            'filename' => (string) $portable['filename'],
                            'sha256' => (string) $portable['sha256'],
                            'counts' => $portableCounts,
                        ],
                        'includes' => ['plugin', 'active-theme', 'parent-theme-when-used', 'portable-site'],
                    ], $files);
                    break;
                case 'plugin':
                    $recordCount = self::addDirectory(
                        $zip,
                        H18_CLEAN_DIR,
                        'plugin/' . basename(untrailingslashit(H18_CLEAN_DIR)),
                        $files
                    );
                    self::addJson($zip, 'plugin.json', [
                        'schemaVersion' => self::SCHEMA,
                        'product' => 'Visual Designer Manager',
                        'internalVersion' => H18_CLEAN_VERSION,
                        'sourceDirectory' => basename(untrailingslashit(H18_CLEAN_DIR)),
                    ], $files);
                    break;

                case 'theme':
                    $recordCount = self::addTheme($zip, $files);
                    break;

                case 'pages':
                    $records = self::pageRecords();
                    $recordCount = count($records);
                    self::addJson($zip, 'pages.json', [
                        'schemaVersion' => self::SCHEMA,
                        'type' => 'pages',
                        'siteSettings' => [
                            'showOnFront' => (string) get_option('show_on_front', 'posts'),
                            'frontPageSourceId' => absint(get_option('page_on_front', 0)),
                            'postsPageSourceId' => absint(get_option('page_for_posts', 0)),
                        ],
                        'records' => $records,
                    ], $files);
                    break;

                case 'navigation':
                    $navigation = self::navigationData();
                    $recordCount = count($navigation['menus']);
                    self::addJson($zip, 'navigation.json', $navigation, $files);
                    break;

                case 'images':
                case 'documents':
                case 'videos':
                case 'media':
                    $recordCount = self::addMedia($zip, $kind, $files);
                    break;
            }

            $manifest = self::manifest($kind, $files, $recordCount);
            $manifestJson = wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if (!is_string($manifestJson)) {
                throw new \RuntimeException('Manifest kunne ikke serialiseres.');
            }
            if (!$zip->addFromString('visual-designer-export.json', $manifestJson . "\n")) {
                throw new \RuntimeException('Manifest kunne ikke tilføjes til ZIP.');
            }
            if (!$zip->close()) {
                throw new \RuntimeException('ZIP-export kunne ikke afsluttes.');
            }
        } catch (\Throwable $error) {
            $zip->close();
            if (is_string($portableTmp) && $portableTmp !== '') { @unlink($portableTmp); }
            @unlink($tmp);
            wp_die(esc_html('Export fejlede: ' . $error->getMessage()));
        }

        if (is_string($portableTmp) && $portableTmp !== '') { @unlink($portableTmp); }

        if (!is_file($tmp) || filesize($tmp) === 0) {
            @unlink($tmp);
            wp_die(esc_html__('Exportpakken blev ikke oprettet korrekt.', 'visual-designer-manager'));
        }

        $filename = self::downloadName($kind);
        nocache_headers();
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . (string) filesize($tmp));
        header('X-Content-Type-Options: nosniff');

        $packageSha = hash_file('sha256', $tmp);
        if (is_string($packageSha) && $packageSha !== '') {
            header('X-Visual-Designer-SHA256: ' . $packageSha);
        }

        readfile($tmp);
        @unlink($tmp);
        exit;
    }

    private static function card(string $kind, string $title, string $description, bool $enabled): void
    {
        echo '<section class="h18-manager-card"><h2>' . esc_html($title) . '</h2><p>' . wp_kses_post($description) . '</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION) . '">';
        echo '<input type="hidden" name="export_kind" value="' . esc_attr($kind) . '">';
        wp_nonce_field(self::NONCE . '_' . $kind);
        echo '<button class="button button-primary" type="submit"' . ($enabled ? '' : ' disabled') . '>Export ' . esc_html(self::LABELS[$kind]) . '</button>';
        echo '</form></section>';
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addTheme(\ZipArchive $zip, array &$files): int
    {
        $theme = wp_get_theme();
        $stylesheet = sanitize_file_name((string) $theme->get_stylesheet());
        $template = sanitize_file_name((string) $theme->get_template());

        $count = self::addDirectory(
            $zip,
            get_stylesheet_directory(),
            'themes/' . $stylesheet,
            $files
        );

        $parent = $theme->parent();
        $parentIncluded = false;
        if ($parent instanceof \WP_Theme && $template !== '' && $template !== $stylesheet) {
            $count += self::addDirectory(
                $zip,
                get_template_directory(),
                'themes/' . $template,
                $files
            );
            $parentIncluded = true;
        }

        self::addJson($zip, 'theme.json', [
            'schemaVersion' => self::SCHEMA,
            'active' => [
                'name' => (string) $theme->get('Name'),
                'version' => (string) $theme->get('Version'),
                'stylesheet' => $stylesheet,
                'template' => $template,
            ],
            'parentIncluded' => $parentIncluded,
            'parent' => $parent instanceof \WP_Theme ? [
                'name' => (string) $parent->get('Name'),
                'version' => (string) $parent->get('Version'),
                'stylesheet' => (string) $parent->get_stylesheet(),
            ] : null,
            'themeMods' => get_theme_mods(),
            'menuLocations' => get_nav_menu_locations(),
        ], $files);

        return $count;
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addDirectory(\ZipArchive $zip, string $root, string $zipRoot, array &$files): int
    {
        $realRoot = realpath($root);
        if (!is_string($realRoot) || !is_dir($realRoot)) {
            throw new \RuntimeException('Kildemappen findes ikke.');
        }

        $rootNormalized = rtrim(str_replace('\\', '/', $realRoot), '/') . '/';
        $count = 0;
        $iterator = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($realRoot, \FilesystemIterator::SKIP_DOTS),
            \RecursiveIteratorIterator::LEAVES_ONLY
        );

        foreach ($iterator as $item) {
            if (!$item instanceof \SplFileInfo || !$item->isFile() || !$item->isReadable()) {
                continue;
            }

            $path = $item->getPathname();
            $realPath = realpath($path);
            if (!is_string($realPath) || !is_file($realPath)) {
                continue;
            }

            $fileNormalized = str_replace('\\', '/', $realPath);
            if (strpos($fileNormalized, $rootNormalized) !== 0) {
                continue;
            }

            $relative = ltrim(substr($fileNormalized, strlen($rootNormalized)), '/');
            if ($relative === '' || self::skipFilesystemPath($relative)) {
                continue;
            }

            $archivePath = trim($zipRoot, '/') . '/' . $relative;
            self::addFile($zip, $realPath, $archivePath, $files);
            $count++;
        }
        return $count;
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addMedia(\ZipArchive $zip, string $kind, array &$files): int
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

        $records = [];
        $added = [];
        foreach ($attachments as $attachment) {
            if (!$attachment instanceof \WP_Post) {
                continue;
            }
            $mime = (string) get_post_mime_type($attachment->ID);
            if (!self::includeMime($mime, $kind)) {
                continue;
            }

            $attachmentFiles = [];
            $paths = self::attachmentPaths($attachment->ID, $baseDir);
            foreach ($paths as $path) {
                $real = realpath($path);
                if (!is_string($real) || !is_file($real)) {
                    continue;
                }

                $prefix = rtrim(str_replace('\\', '/', $baseDir), '/') . '/';
                $normalized = str_replace('\\', '/', $real);
                if (strpos($normalized, $prefix) !== 0) {
                    continue;
                }

                $relative = substr($normalized, strlen($prefix));
                if ($relative === '') {
                    continue;
                }
                $attachmentFiles[] = $relative;

                if (!isset($added[$real])) {
                    self::addFile($zip, $real, 'uploads/' . ltrim($relative, '/'), $files);
                    $added[$real] = true;
                }
            }

            $records[] = [
                'sourceId' => $attachment->ID,
                'title' => (string) $attachment->post_title,
                'slug' => (string) $attachment->post_name,
                'mimeType' => $mime,
                'dateGmt' => (string) $attachment->post_date_gmt,
                'modifiedGmt' => (string) $attachment->post_modified_gmt,
                'caption' => (string) $attachment->post_excerpt,
                'description' => (string) $attachment->post_content,
                'alt' => (string) get_post_meta($attachment->ID, '_wp_attachment_image_alt', true),
                'attachedFile' => (string) get_post_meta($attachment->ID, '_wp_attached_file', true),
                'archiveFiles' => array_values(array_unique($attachmentFiles)),
                'metadata' => wp_get_attachment_metadata($attachment->ID),
            ];
        }

        self::addJson($zip, 'media.json', [
            'schemaVersion' => self::SCHEMA,
            'type' => $kind,
            'records' => $records,
        ], $files);

        return count($records);
    }

    /** @return array<int,string> */
    private static function attachmentPaths(int $attachmentId, string $baseDir): array
    {
        $paths = [];
        $main = get_attached_file($attachmentId, true);
        if (is_string($main) && $main !== '') {
            $paths[] = $main;
        }

        $meta = wp_get_attachment_metadata($attachmentId);
        if (!is_array($meta)) {
            return array_values(array_unique($paths));
        }

        $relativeMain = (string) ($meta['file'] ?? '');
        $dir = $relativeMain !== '' ? dirname($relativeMain) : '';
        if ($dir === '.') {
            $dir = '';
        }

        if (!empty($meta['original_image'])) {
            $paths[] = trailingslashit($baseDir) . ($dir !== '' ? trailingslashit($dir) : '') . basename((string) $meta['original_image']);
        }

        if (!empty($meta['sizes']) && is_array($meta['sizes'])) {
            foreach ($meta['sizes'] as $size) {
                if (!is_array($size) || empty($size['file'])) {
                    continue;
                }
                $paths[] = trailingslashit($baseDir) . ($dir !== '' ? trailingslashit($dir) : '') . basename((string) $size['file']);
            }
        }

        return array_values(array_unique($paths));
    }

    /** @return array<int,array<string,mixed>> */
    private static function pageRecords(): array
    {
        $pages = get_pages([
            'sort_column' => 'ID',
            'sort_order' => 'ASC',
            'post_status' => ['publish', 'draft', 'private', 'pending', 'future'],
        ]);

        $records = [];
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post) {
                continue;
            }

            $record = [
                'sourceId' => $page->ID,
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
                'mediaSourceIds' => self::pageMediaSourceIds($page),
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
        return $records;
    }

    /** @return array<int,int> */
    private static function pageMediaSourceIds(\WP_Post $page): array
    {
        $ids = [];
        $featured = (int) get_post_thumbnail_id($page->ID);
        if ($featured > 0) {
            $ids[$featured] = true;
        }

        if (metadata_exists('post', $page->ID, LayoutModel::META)) {
            $model = LayoutModel::get($page->ID);
            foreach ($model['nodes'] as $node) {
                if (!is_array($node) || (string) ($node['type'] ?? '') !== 'image') {
                    continue;
                }
                $mediaId = absint($node['props']['mediaId'] ?? 0);
                if ($mediaId > 0) {
                    $ids[$mediaId] = true;
                }
            }
        }

        if (preg_match_all('/wp-image-(\d+)/', (string) $page->post_content, $matches)) {
            foreach ($matches[1] as $match) {
                $id = absint($match);
                if ($id > 0) {
                    $ids[$id] = true;
                }
            }
        }

        $galleries = get_post_galleries($page, false);
        foreach (is_array($galleries) ? $galleries : [] as $gallery) {
            if (!is_array($gallery) || empty($gallery['ids'])) {
                continue;
            }
            foreach (explode(',', (string) $gallery['ids']) as $rawId) {
                $id = absint($rawId);
                if ($id > 0) {
                    $ids[$id] = true;
                }
            }
        }

        $result = array_map('intval', array_keys($ids));
        sort($result, SORT_NUMERIC);
        return $result;
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
            'type' => 'navigation',
            'registeredLocations' => get_registered_nav_menus(),
            'locations' => get_nav_menu_locations(),
            'menus' => $menus,
        ];
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addJson(\ZipArchive $zip, string $archivePath, array $value, array &$files): void
    {
        $json = wp_json_encode($value, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) {
            throw new \RuntimeException($archivePath . ' kunne ikke serialiseres.');
        }

        $payload = $json . "\n";
        if (!$zip->addFromString($archivePath, $payload)) {
            throw new \RuntimeException($archivePath . ' kunne ikke tilføjes til ZIP.');
        }

        $files[] = [
            'path' => $archivePath,
            'size' => strlen($payload),
            'sha256' => hash('sha256', $payload),
        ];
    }

    /** @param array<int,array<string,mixed>> $files */
    private static function addFile(\ZipArchive $zip, string $source, string $archivePath, array &$files): void
    {
        if (!$zip->addFile($source, $archivePath)) {
            throw new \RuntimeException('Filen kunne ikke tilføjes: ' . $archivePath);
        }

        $hash = hash_file('sha256', $source);
        $size = filesize($source);
        $files[] = [
            'path' => $archivePath,
            'size' => $size !== false ? (int) $size : 0,
            'sha256' => is_string($hash) ? $hash : '',
        ];
    }

    /** @param array<int,array<string,mixed>> $files @return array<string,mixed> */
    private static function manifest(string $kind, array $files, int $recordCount): array
    {
        usort($files, static fn(array $a, array $b): int => strcmp((string) ($a['path'] ?? ''), (string) ($b['path'] ?? '')));
        $digestJson = wp_json_encode($files, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $contentDigest = is_string($digestJson) ? hash('sha256', $digestJson) : '';

        return [
            'schemaVersion' => self::SCHEMA,
            'product' => 'Visual Designer Manager',
            'internalVersion' => H18_CLEAN_VERSION,
            'exportType' => $kind,
            'exportLabel' => self::LABELS[$kind],
            'createdUtc' => gmdate('c'),
            'site' => [
                'name' => (string) get_bloginfo('name'),
                'url' => home_url('/'),
            ],
            'environment' => [
                'wordpress' => (string) get_bloginfo('version'),
                'php' => PHP_VERSION,
            ],
            'recordCount' => $recordCount,
            'fileCount' => count($files),
            'contentSha256' => $contentDigest,
            'files' => $files,
        ];
    }

    private static function includeMime(string $mime, string $kind): bool
    {
        if ($kind === 'media') {
            return true;
        }
        if ($kind === 'images') {
            return strpos($mime, 'image/') === 0;
        }
        if ($kind === 'videos') {
            return strpos($mime, 'video/') === 0;
        }
        if ($kind === 'documents') {
            if (strpos($mime, 'image/') === 0 || strpos($mime, 'video/') === 0 || strpos($mime, 'audio/') === 0) {
                return false;
            }
            return strpos($mime, 'application/') === 0 || strpos($mime, 'text/') === 0;
        }
        return false;
    }

    private static function skipFilesystemPath(string $relative): bool
    {
        $normalized = '/' . trim(str_replace('\\', '/', $relative), '/') . '/';
        $lower = strtolower($normalized);

        foreach (['/.git/', '/node_modules/', '/.idea/', '/.vscode/', '/vendor/bin/'] as $blocked) {
            if (strpos($lower, $blocked) !== false) {
                return true;
            }
        }

        $base = strtolower(basename($relative));
        if ($base === '.env' || str_starts_with($base, '.env.')) {
            return true;
        }

        return in_array($base, [
            'auth.json',
            'credentials.json',
            'secrets.json',
            'secret.json',
            'id_rsa',
            'id_dsa',
            '.npmrc',
            '.pypirc',
        ], true);
    }

    private static function downloadName(string $kind): string
    {
        $site = sanitize_title((string) get_bloginfo('name'));
        if ($site === '') {
            $site = 'wordpress-site';
        }
        return 'visual-designer-' . $site . '-' . $kind . '-' . gmdate('Ymd-His') . '.zip';
    }

    private static function guard(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
    }
}
