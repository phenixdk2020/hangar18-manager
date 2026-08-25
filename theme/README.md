# Hangar18 Base Theme

Dette repository publicerer både Hangar18 Manager-pluginet og Hangar18 Base Theme.

## Frossen visuel baseline

Den eksisterende **Hangar18 Base Theme 1.2.0** er nu bevaret både som installationspakke og som udpakket, verificeret source snapshot:

- `theme/legacy-v1.2.0/` – alle temaets kildefiler.
- `theme/legacy-v1.2.0/source-manifest.json` – SHA-256 og størrelse pr. fil.
- `dist/hangar18-base-theme-v1.2.0.zip.b64` – original versionspakke.
- `dist/hangar18-base-theme.zip.b64` – aktiv installationspakke.
- `theme-update.json` – versionsmanifest til WordPress.

Den dekodede 1.2.0-pakke har SHA-256:

`6d3c7a2e45d249e31a74a3703844364ed79c3122798b6e916ddaa1116e62e6bf`

## Clean-install strategi

Den nye 0.9.x-editor må **ikke** arve gamle editor-runtimes, proxy-renderere eller kompatibilitetslag fra 0.8.x. Temaet behandles separat som et visuelt fundament.

På det nye subdomæne installeres derfor først den verificerede Hangar18 Base Theme 1.2.0, så typografi, farvepalette, WordPress-reset og den eksisterende frontend-baseline følger med. Derefter installeres den nye Hangar18 Manager 0.9.x ovenpå.

Gamle sider og gammelt editor-state importeres ikke ved opstart. De konverteres først, når den nye editor, Undo/Redo, 120-unit fysisk canvas, re-parenting og frontend parity er QA-godkendt.

## Temaopdatering

Temaopdateringen bruger følgende separate filer:

- `theme-update.json` – versionsmanifest til WordPress.
- `dist/hangar18-base-theme.zip.b64` – stabil Base64-kodet opdateringspakke.
- `dist/hangar18-base-theme-v1.2.0.zip.b64` – versionsarkiv.

Pluginets `update.json` og `dist/hangar18-manager.zip` påvirkes ikke af temaversioner.

Temaet afkoder pakken lokalt i WordPress og kontrollerer den afkodede ZIP mod SHA-256-værdien i manifestet, før installationen fortsætter.
