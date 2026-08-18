# E11 Quality / Side Health core — UD-098 to UD-103

## UD-098 Accessibility analyzer

Static page-state checks report element references for heading-order jumps, missing image alt text, missing control/form labels, explicitly disabled focus indication and measurable low text/background contrast.

## UD-099 Responsive analyzer

Checks fixed widths against desktop/tablet/mobile viewport budgets, explicit touch targets below 44 px, very small responsive text and critical navigation/form content explicitly hidden on mobile.

## UD-100 Design consistency

Reports off-token local colors, local font overrides and excessive unique spacing/radius values. The analyzer is advisory; it never rewrites design values automatically.

## UD-101 SEO analyzer + metadata model

`SeoMetadata` normalizes title, meta description, canonical/index/follow and social metadata. `SeoAnalyzer` checks title/description limits, exactly-one-H1 policy, HTTPS canonical validity and social metadata fallbacks.

## UD-102 Performance analyzer

Checks oversized used assets, deep layout hierarchy, excessive element count and known frontend modules loaded without corresponding element types.

## UD-103 Side Health aggregator

Combines Design, Mobile, Accessibility, Performance and SEO scores into a 0–100 Side Health score while separately returning all issues and `HardFailures`. Critical/error findings are never hidden just because the numeric score remains high.

## Activation boundary

This release establishes the generic analysis engine and report format. It does not automatically rewrite pages or change Vehicle/Event/Gallery. The visible Side Health panel can consume this report when the new editor runtime is activated after migration/security QA.
