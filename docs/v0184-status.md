# Visual Designer Manager v0.1.84 – Portable site transfer

Status: release candidate

## Leverance

- Portabel siteeksport i ZIP med schema 1.0.
- Read-only import-preflight før ændringer.
- SHA-256-verifikation af alle manifest-filer.
- ZIP path-traversal- og størrelsesgrænser.
- Sider/layouts + versionshistorik.
- Header/Footer-templates + historik og standardvalg.
- Modulrecords samt køretøjs- og eventfelter.
- Navigation og menuplaceringer.
- Originale mediefiler med attachment-ID/URL-remapping.
- Nye VDM_* runtime-konstanter med deprecated compatibility-aliases.
- Legacy-storage er isoleret i `src/Compatibility/LegacyStorageBridge.php`.

## Ikke inkluderet i den portable pakke

WordPress core, brugerkonti/adgangskoder, database-login, API-hemmeligheder og andre plugins' filer.
