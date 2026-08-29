# Visual Designer Manager 0.1.43 – implementation status

- Header Desktop parity pass 2: source implemented, awaiting user QA.
- Header inner Container uses #30382A so editor preview no longer hides the dark bar.
- Header brand/menu use explicit vertical geometry.
- Header menu resolver validates the seven Hangar18 reference items and can create a dedicated Visual Designer Hovedmenu if necessary.
- Header logo resolver scans the WordPress media library if legacy/custom-logo/site-icon sources are missing.
- Footer – Standard first conversion follows the old Manager get_shell_source contract: the literal HANGAR18-FOOTER block from Hjem/another managed page is authoritative, together with FooterWidthPercent.
- Footer conversion is observable and repeatable with source page, excerpt and SHA-256 evidence. Missing legacy source stops with an explicit error; no Footer content is guessed.
- Theme Shell remains OFF.
