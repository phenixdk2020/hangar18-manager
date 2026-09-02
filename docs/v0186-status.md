# Visual Designer Manager v0.1.86 – Siteindstillinger og portabel site-identitet

Status: release candidate

## Leverance

- Ny Manager-side: Siteindstillinger.
- Webstedstitel og slogan redigeres direkte og gemmes i WordPress `blogname` / `blogdescription`.
- Virksomhed/forening, kontakt-e-mail og kontakttelefon gemmes i VDM-navngivne options.
- Logo og site-ikon/favicon vælges via WordPress mediebibliotek.
- Portabel eksport indeholder eksplicit `settings.siteIdentity`.
- Import remapper logo og site-ikon gennem den importerede mediemap.
- VDM 0.1.85 og ældre pakker uden `siteIdentity` bevarer målsitets identitet.
- Den brugerleverede 0.1.85 ZIP er verificeret separat: schema 1.0 og alle manifest-hashes matcher.
