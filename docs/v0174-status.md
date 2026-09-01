# Visual Designer Manager v0.1.74

Status: release candidate

## VD-MODULE-CUTOVER-001
- `events`, `billedgalleri` og `koeretoejer-og-materiel` er dedikerede ModuleStore-sider.
- `_old`-screenshots er visuel reference for kort, overskrifter, tekniske data og spacing.
- Modulerne bruger almindeligt dokumentflow, så recordantal bestemmer højden og Footeren følger efter indholdet.
- ThemeShell ejer fortsat Header/Footer.
- Eventdato afgør automatisk Kommende/Tidligere; historiske records slettes ikke.

## BUG-23 / BUG-24
- Release-history loader understøtter canonical `{"versions":[...]}`.
- Side-save viser `Siden er gemt`, `Ingen ændringer at gemme` eller reel fejl med årsag.

## QA-gate
- Alle tidligere module-, canvas-, Header/Footer- og editor/frontend-paritetstests skal forblive grønne.
- Central release skal pakke `CollectionPageRenderer.php` og genkøre v0.1.74-QA før ZIP/SHA-256-manifest.
