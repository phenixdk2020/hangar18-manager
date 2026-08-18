from pathlib import Path

path = Path('assets/admin.css')
css = path.read_text(encoding='utf-8')
marker = '/* v0.6.1 – Inspector tabs må ikke overlappe settings */'
if marker in css:
    raise SystemExit('hotfix already applied')

patch = r'''

/* v0.6.1 – Inspector tabs må ikke overlappe settings */
.h18-pages-admin .h18-builder-inspector{overflow:auto;overscroll-behavior:contain}
.h18-pages-admin .h18-builder-inspector-heading{margin-bottom:12px}
.h18-pages-admin .h18-inspector-tabs{
    position:relative;
    z-index:2;
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    grid-auto-rows:minmax(36px,auto);
    gap:6px;
    width:100%;
    margin:0 0 18px;
    padding:0 0 2px;
    clear:both;
}
.h18-pages-admin .h18-inspector-tab{
    position:relative;
    float:none;
    display:flex;
    align-items:center;
    justify-content:center;
    width:100%;
    min-width:0;
    min-height:36px;
    height:auto;
    margin:0;
    padding:8px 6px;
    line-height:1.2;
    white-space:normal;
    text-align:center;
    overflow-wrap:anywhere;
    box-sizing:border-box;
}
.h18-pages-admin #h18-page-inspector-target,
.h18-pages-admin #h18-inspector-advanced-panel{
    position:relative;
    z-index:1;
    clear:both;
    width:100%;
    margin-top:0;
}
.h18-pages-admin #h18-page-inspector-target>.h18-page-section-body{margin:0;min-width:0}
.h18-pages-admin .h18-builder-inspector select,
.h18-pages-admin .h18-builder-inspector input,
.h18-pages-admin .h18-builder-inspector textarea{max-width:100%;box-sizing:border-box}
@media(min-width:1700px){
    .h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media(max-width:1180px){
    .h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media(max-width:782px){
    .h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(2,minmax(0,1fr))}
}
'''

path.write_text(css.rstrip() + patch + '\n', encoding='utf-8')
print('Inspector overlap CSS hotfix applied')
