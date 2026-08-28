# Visual Designer Manager 0.1.41 – implementation status

- BUG-10: FIXED in source; awaiting user QA.
- Blank slug derives from title and is made unique before wp_insert_post, including drafts.
- Existing blank page slugs are repaired once, non-destructively.
- Legacy HeaderDesign conversion reads hangar18_manager_header_design_v25 plus the existing HANGAR18-HEADER block.
- Header – Standard receives Section → Container → Logo/Brand/Menu as available.
- Active legacy WordPress menu ID is retained as the Menu data source.
- Existing Visual Designer Header state is retained through normal template version history.
- Theme Shell cutover remains OFF; visual 1:1 parity awaits user QA.
- BUG-02 rich-text selection remains user-QA PASS.
