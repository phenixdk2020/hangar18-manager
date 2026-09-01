from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'clean/hangar18-manager/src/Admin/EditorController.php'
s=p.read_text(encoding='utf-8')
old="        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];"
new="        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $collectionMode = $isCollectionPage && sanitize_key((string) ($_GET['h18_collection_mode'] ?? 'content')) === 'module' ? 'module' : 'content';\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];"
if new not in s:
    if old not in s: raise SystemExit('EditorController render collection anchor missing')
    s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
print('v0.1.78 pre-apply anchor fix ready')
