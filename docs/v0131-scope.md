# Visual Designer Manager 0.1.31 – arbejdsomfang

Status: igangsat

## Fejlrettelser

1. Floating Button skal være et ægte overlay i sin aktuelle parent og må ikke reservere normal layout-plads.
2. Rich-text Fed og Kursiv skal bevare den aktive tekst-selektion efter formattering, på samme måde som Understreget.

## Header/Footer/Theme

3. Kortlæg og begynd konvertering af den eksisterende Hangar18 header og footer til native globale Visual Designer-modeller.
4. Begynd Theme Shell-konverteringen: WordPress-temaet skal på sigt kun levere lifecycle, hooks, wrappers, fallback og integration, mens Visual Designer leverer den visuelle Header/Page/Footer-model.
5. Eksisterende Hangar18 Base Theme 1.2.0 bevares som frossen visuel baseline, og cutover må først ske efter visuel parity og QA.

## QA

- Save/Reload af canonical model.
- Desktop/Laptop/Mobile.
- Ingen dobbelt Header/Footer rendering.
- Ingen regression i nuværende frontend før cutover.
