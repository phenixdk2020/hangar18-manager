# Visual Designer Manager 0.1.49 – status

## Scope
- Aktiv public Theme Shell på Visual Designer-sider.
- Canonical live-rækkefølge: Header → side → Footer.
- Safe fallback: ikke-Designer sider urørte; manglende template udelades uden at skjule siden.
- Manager-side til valg af WordPress-hjemmeside.
- Hjem – Visual Designer kan publiceres og sættes som Hjem direkte.
- AKVPK theme 1.2.2 updater/version identity fix.

## Cutover-kontrakt
0.1.49 er det eksplicit godkendte cutover-punkt. `ThemeShell::activateApprovedCutover()` sætter cutover-flaget én gang. `Renderer::content()` går kun ind i shell-kompositionen, når siden har Visual Designer metadata eller er et Designer-preview. Legacy/non-Designer `post_content` returneres uændret.

## Hjemmeside-kontrakt
Manageren skriver WordPress' standardindstillinger `show_on_front=page` og `page_on_front=<ID>`. Hvis den valgte Visual Designer-side er en kladde, publiceres den først efter capability-check. Den tidligere forside slettes eller ændres ikke.

## QA
Release-gates kontrollerer PHP/JS-syntaks, eksisterende hierarchy/model QA, aktiv cutover, safe fallback-grenen, Header/Footer resolution, set-home WordPress options, 0.1.48 Lag/Button/Fit/BUG-02 regression og AKVPK 1.2.2 updater-version.
