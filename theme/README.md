# Hangar18 Base Theme

Dette repository publicerer både Hangar18 Manager-pluginet og Hangar18 Base Theme.

Temaopdateringen bruger følgende separate filer:

- `theme-update.json` – versionsmanifest til WordPress.
- `dist/hangar18-base-theme.zip.b64` – stabil Base64-kodet opdateringspakke.
- `dist/hangar18-base-theme-v1.2.0.zip.b64` – versionsarkiv.

Pluginets `update.json` og `dist/hangar18-manager.zip` påvirkes ikke af temaversioner.

Temaet afkoder pakken lokalt i WordPress og kontrollerer den afkodede ZIP mod SHA-256-værdien i manifestet, før installationen fortsætter.
