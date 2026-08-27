# Visual Designer Manager 0.1.31 – testplan

## BUG-01 Floating Button
- Opret knap i Page root, Section og Box.
- Sæt knappen til Floating.
- Bekræft at den ikke reserverer en normal layout-række/celle.
- Flyt den over andre elementer og bekræft at andre elementer ikke skubbes.
- Bekræft at parentens auto-grow ikke øges alene pga. floating-knappen.
- Save/Reload og verificer samme position.
- Test Desktop/Laptop/Mobile separat.

## BUG-02 Rich text selection
- Markér tekst.
- Klik Fed og bekræft at samme tekst stadig er markeret.
- Klik derefter Kursiv uden at markere igen.
- Klik derefter Understreget uden at markere igen.
- Gentag i omvendt rækkefølge og med toggle off.

## Header/Footer/Theme
- Ingen cutover i denne pakke før parity er verificeret.
- Eksisterende theme-rendering skal fortsat være fallback.
- Native Header/Footer modeller må ikke give dobbelt header/footer.
