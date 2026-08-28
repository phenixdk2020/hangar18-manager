# Visual Designer Manager 0.1.42 – implementation status

- BUG-11: FIXED in source; awaiting user QA.
- Header conversion now records visible status instead of silently returning when legacy source data is absent.
- Header/Footer shows source diagnosis and a manual re-conversion action.
- Approved Desktop screenshot reference 2026-08-28 is the deterministic fallback: 90% centred, about 120 px, #30382A, logo/brand left and Menu right.
- WordPress Menu remains a data source, not copied content.
- Logo source resolution: legacy Header → WordPress Custom Logo → Site Icon; Image geometry is retained even when the image file cannot be resolved.
- Re-conversion uses TemplateLayoutModel::saveVersion and is therefore non-destructive.
- Theme Shell cutover remains OFF pending Desktop/Laptop/Mobile user QA.
- BUG-02 remains user-QA PASS.
- BUG-10 remains fixed.
