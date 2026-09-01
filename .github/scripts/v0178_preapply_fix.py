from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'clean/hangar18-manager/src/Admin/EditorController.php'
s=p.read_text(encoding='utf-8')

old="        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];"
new="        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $collectionMode = $isCollectionPage && sanitize_key((string) ($_GET['h18_collection_mode'] ?? 'content')) === 'module' ? 'module' : 'content';\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];"
if new not in s:
    if old not in s: raise SystemExit('EditorController render collection anchor missing')
    s=s.replace(old,new,1)

old_panel="        if ($isCollectionPage) {\n            $moduleSlug = sanitize_title((string) get_post_field('post_name', $postId));"
new_panel="        if ($isCollectionPage && $collectionMode === 'module') {\n            $moduleSlug = sanitize_title((string) get_post_field('post_name', $postId));"
if new_panel not in s:
    if old_panel not in s: raise SystemExit('EditorController module panel anchor missing')
    s=s.replace(old_panel,new_panel,1)

p.write_text(s,encoding='utf-8')
print('v0.1.78 pre-apply anchors ready')
