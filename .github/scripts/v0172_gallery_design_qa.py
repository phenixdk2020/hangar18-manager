from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def text(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f'Missing required file: {path}')
    return p.read_text(encoding='utf-8')


def require(path: str, *needles: str) -> None:
    value = text(path)
    for needle in needles:
        if needle not in value:
            raise SystemExit(f'{path}: missing contract marker: {needle}')


def require_compact(path: str, needle: str) -> None:
    value = re.sub(r'\s+', '', text(path))
    compact = re.sub(r'\s+', '', needle)
    if compact not in value:
        raise SystemExit(f'{path}: missing compact contract marker: {needle}')


plugin = text('clean/hangar18-manager/hangar18-manager.php')
require('clean/hangar18-manager/hangar18-manager.php',
        "src/Admin/GalleryAdminController.php",
        "src/Migration/SiteDesignHarmonizer.php",
        'GalleryAdminController::register()',
        'SiteDesignHarmonizer::register()',
        "'galleryRecords' => $galleryRecords",
        "'galleryAdminUrl' => admin_url('admin.php?page=h18-clean-gallery')")

require('clean/hangar18-manager/src/Admin/GalleryAdminController.php',
        'final class GalleryAdminController',
        "public const PAGE = 'h18-clean-gallery'",
        'function saveGallery', 'function deleteGallery',
        "ModuleStore::save('galleries'",
        'featured_media_id', 'image_ids', 'data-multiple="1"',
        'Billederne er bevaret i Media Library')
require('clean/hangar18-manager/src/Admin/AdminController.php',
        "[GalleryAdminController::class, 'render']")
require('clean/hangar18-manager/assets/admin-v0123.js',
        "'h18-clean-gallery': ['Klar', 'ready']")

require('clean/hangar18-manager/src/Modules/ModuleRegistry.php',
        "'galleries' => [", "'imageIds' =>", "'media_list'", "'description' =>")
require('clean/hangar18-manager/src/Modules/ModuleRecord.php',
        "case 'media_list':", 'MAX_MEDIA_ITEMS')

require('clean/hangar18-manager/src/Model/LayoutModel.php',
        "'gallerylist'", "'gallerydetail'",
        "'module' => 'galleries'",
        "'view' => 'list'", "'view' => 'detail'",
        "'showCount'", "'detailPageId'")
require('clean/hangar18-manager/src/Admin/EditorController.php',
        "'gallerylist' => 'Gallerioversigt'",
        "'gallerydetail' => 'Albumvisning'")
require('clean/hangar18-manager/assets/editor-v018-core.js',
        "'gallerylist'", "'gallerydetail'",
        'Gallerioversigt', 'Albumvisning',
        'galleryRecords()', 'galleryRecordById', 'galleryImageCount',
        'galleryDetailPageId', 'galleryRecordId', 'h18_gallery=record-id')
require('clean/hangar18-manager/assets/editor-v0166-foundation.css',
        'h18-vd-gallery-list-preview', 'h18-vd-gallery-detail-preview',
        'h18-vd-gallery-images-preview')

require('clean/hangar18-manager/src/Frontend/Renderer.php',
        "if ($type === 'gallerylist')", "if ($type === 'gallerydetail')",
        "ModuleStore::listRecords('galleries'", "ModuleStore::findByRecordId('galleries'",
        "$_GET['h18_gallery']",
        "(string)($record['status']??'draft')!=='publish'",
        'h18-clean-front-gallery-list', 'h18-clean-front-gallery-detail',
        'h18-clean-front-gallery-images')

harmonizer = text('clean/hangar18-manager/src/Migration/SiteDesignHarmonizer.php')
require('clean/hangar18-manager/src/Migration/SiteDesignHarmonizer.php',
        'final class SiteDesignHarmonizer',
        "public const CONTRACT = 'VD-SITE-DESIGN-HARMONY-001'",
        "public const BACKUP_META = '_h18_vd_layout_pre_theme_v0172'",
        "public const DONE_META = '_h18_vd_theme_harmonized_v0172'",
        "'om-foreningen'", "'koeretoejer-og-materiel'", "'events'",
        "'billedgalleri'", "'bliv-medlem'", "'kontakt'",
        "get_option('page_on_front'",
        'LayoutModel::saveVersion(',
        'Design harmoniseret med Hjem (v0.1.72)',
        'layoutFingerprint(',
        "'geometry' => $node['geometry'] ?? []",
        'referenceDigest', 'beforeDigest', 'afterDigest')

# Safety contract: style migration must explicitly compare a layout-only fingerprint,
# and it must not use wp_update_post or mutate page content/title/slug.
if harmonizer.count('self::layoutFingerprint(') < 3:
    raise SystemExit('SiteDesignHarmonizer: layout fingerprint is not enforced before/save/after')
for forbidden in ('wp_update_post(', 'post_content', 'post_title', 'post_name'):
    if forbidden in harmonizer:
        raise SystemExit(f'SiteDesignHarmonizer must not mutate WordPress page content/identity: {forbidden}')

# The migration may update props but never write geometry fields directly.
if re.search(r"\['geometry'\]\s*=", harmonizer):
    raise SystemExit('SiteDesignHarmonizer must not assign canonical geometry')
require_compact('clean/hangar18-manager/src/Migration/SiteDesignHarmonizer.php',
                "if($beforeFingerprint!==self::layoutFingerprint($after)){return;")

for manual in ('CLEAN-DESIGN-MANUAL.md', 'CLEAN-USER-MANUAL.md', 'CLEAN-TECHNICAL-MANUAL.md'):
    require(manual, 'Billedgalleri')
require('CLEAN-DESIGN-MANUAL.md', 'VD-GALLERY-MODULE-001', 'VD-SITE-DESIGN-HARMONY-001')
require('CLEAN-TECHNICAL-MANUAL.md', 'VD-GALLERY-MODULE-001', 'VD-SITE-DESIGN-HARMONY-001')
require('CLEAN-USER-MANUAL.md', 'Sådan bruger du Billedgalleriet', 'Automatisk designharmonisering i v0.1.72')
require('docs/clean-backlog-v0100.md',
        'VD-GALLERY-MODULE-001 — FÆRDIG I v0.1.72',
        'VD-SITE-DESIGN-HARMONY-001 — FÆRDIG I v0.1.72')
require('docs/v0172-status.md', 'VD-GALLERY-MODULE-001', 'VD-SITE-DESIGN-HARMONY-001')

history = json.loads(text('clean/hangar18-manager/release-history.json'))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.72' for row in versions):
    raise SystemExit('release-history.json: v0.1.72 missing')

admin = text('clean/hangar18-manager/src/Admin/AdminController.php')
if re.search(r"h18-clean-gallery'.*\[self::class,\s*'gallery'\]", admin):
    raise SystemExit('Billedgalleri submenu still points at placeholder AdminController::gallery')

print('v0.1.72 Gallery + Site Design Harmony QA: PASS')
