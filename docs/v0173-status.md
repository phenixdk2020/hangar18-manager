# Visual Designer Manager v0.1.73

Status: release candidate

## VD-EDITOR-FRONTEND-PARITY-001

- Editorens 28 px elementheader er flyttet ud af layoutflowet og vises som overlay ved hover/selection/drag/resize.
- Generisk `.h18-clean-node-preview` har ikke længere 8 px editor-padding eller 48 px editor-minimum.
- Billedpreview bruger hele den canonical elementhøjde i stedet for `calc(100% - 28px)`.
- Sektion/Kasse-surface har ingen editor-margin eller border, kun en ikke-pladsforbrugende outline.
- Canvas bruger stretch som frontend-grid, så eksplícitte gridområder udfyldes efter den gemte geometri.
- Ingen layout-JSON, node-IDer, hierarchy, Desktop/Laptop/Tablet/Mobil-geometri eller frontend Renderer ændres af denne release.

## QA-gate

1. PHP- og JavaScript-syntax skal være grøn.
2. Historiske Header/Footer-, hierarchy-, clipboard-, element-, module- og canvas-regressionstests skal fortsat bestå.
3. Statisk parity-QA skal bekræfte, at editor-chrome ikke længere kan optage canonical layoutplads.
4. Release bygges fortsat af den centrale Visual Designer Manager Release-workflow med ZIP + SHA-256 manifest.
