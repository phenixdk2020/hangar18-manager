# Visual Designer Manager 0.1.50 – status

## Leveret
- Nyt hovedpunkt **Konvertering**.
- Enkelt, markeret og alle-ikke-konverterede kan forberedes som QA-kandidater.
- Batch er staging-only; ingen automatisk live-cutover.
- Preview bruger Header + kandidat + Footer via canonical Renderer.
- Godkendelse opretter en ny LayoutModel-version og sætter Header/Footer til Auto.
- Original WordPress `post_content` ændres ikke.
- Legacy Header/Footer shell-markører fjernes fra kandidatens body.
- Theme/Shell-admin viser aktiv shell korrekt.
- AKVPK theme 1.3.0: Theme URI `https://akvpk.dk/`, teknisk slug `akvpk`, Text Domain `akvpk`.
- Visual Designer Manager migrerer `theme_mods`, menu-locations og Custom CSS før switch fra `hangar18-base` til `akvpk`, når det nye theme er installeret.

## QA-kontrakt
Den automatiske converter er bevidst konservativ: eksisterende body-HTML bevares i første pass i en canonical Text-blok. Komplekse sider kan derfor kræve visuel efterbearbejdning/dekomponering i native Text/Image/Button/Kasse-elementer før de godkendes. Kandidaten må ikke ændre public frontend før eksplicit godkendelse.
