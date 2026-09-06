# Visual Designer Manager V3 — 3.0.0-alpha.10

## Mobile Rendered Reflow

Alpha.10 addresses the mobile defects reproduced on test4 after Alpha.9:

- cards/content can retain geometry that is technically inside the 120-unit model but still clips on a real narrow viewport;
- wrapped headings/body text can exceed their stored grid row span and overlap following content;
- root section grid positions can leave very large blank gaps on mobile;
- overlay buttons can remain positioned from desktop-style coordinates and become clipped.

### Runtime strategy

Alpha.10 keeps the stored Designer geometry as the first choice. On screens up to the existing 782 px mobile breakpoint, a small page-only runtime safeguard measures the rendered result after DOM load, font load and resize.

A parent is locally switched to natural vertical flow only when the real rendered result shows one of these defects:

1. horizontal clipping beyond the parent viewport;
2. intrinsic content overflow;
3. visible overlap between normal-flow siblings;
4. an extreme root-level blank gap without an intentional Spacer.

This means valid mobile layouts are left alone. The repair is scoped to `.h18-vd-live-shell-page`; Header and Footer continue to use their independently scoped stored mobile template geometry from Alpha.8.

### Safety

- no stored layout data is rewritten;
- no V1 baseline runtime is changed;
- Alpha.9 event/detail/gallery/form/padding repairs are retained;
- existing 782 px mobile runtime breakpoint is retained;
- frontend script is syntax-gated and the full retained V1 regression chain runs before merge/release.
