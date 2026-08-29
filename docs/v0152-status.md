# Visual Designer Manager 0.1.52 – CONV-03 visual conversion

## Scope
- External page conversion now targets canonical visual structure instead of one giant Text node.
- Source site remains read-only. Approval is still a separate explicit action.
- Global Header/Footer/Menu are not part of page conversion.

## test2 home reference contract
- Source: `https://test2.hangar18.dk/` read-only.
- Prefer `.h18-page-frame` over generic `.entry-content`.
- Desktop/Laptop root sections: x=6, w=108 (90%). Mobile: x=0, w=120 (100%).
- Frame top/gaps: 32 px desktop/laptop; 24 px mobile.
- Hero: canonical Image with cover fit; source reference Banner-6.jpg; ~260/180 px.
- Tagline: #c3ae83 / #30382a, centered.
- `.avpf-section`: canonical Section with #f2f0e8 default and structured Text/Button/Columns/Cards.

## Safety
- External scripts/styles are not imported.
- Source images remain external/source-linked and are surfaced as QA warnings.
- Existing live model is not replaced until Godkend og aktivér.
- Original local post_content is not overwritten.
- Source hash is rechecked before approval.
