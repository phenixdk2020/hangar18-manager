# Visual Designer Manager V3 — 3.0.0-alpha.18

## Scope

Alpha.18 bygger videre på den godkendte Alpha.17-baseline og retter de resterende visuelle mobilforskelle mod V1:

- for meget samlet luft mellem top-level afsnit;
- store V3-sidegutters omkring sektioner, som i V1 går til skærmkanten;
- hero/image-band der stadig er indrykket af page-shell;
- dobbelte/triple spacing-effekter fra gamle Spacer-noder, node margin og hero margin.

V1 bruges som visuel/responsiv reference. Den aktuelle V3-menu og V3-indhold er fortsat autoritative.

## Mobilkontrakt

På konverterede V1-sider ved `<=782px`:

- `.h18-clean-front-surface` mister vandret page-shell padding;
- top-level image/text/section/container/event/gallery-bands kan male `100vw` til viewportens kant;
- almindelige tekst/section/container-bands beholder 18 px indvendig tekstpadding;
- hero/image-bands bruger full-bleed uden ekstra sidegutter;
- root Spacer-noder skjules;
- alle øvrige root-noder får `margin-bottom:0`;
- der anvendes præcis ét kontrolleret V1-afsnitsgab på 24 px mellem normale top-level afsnit;
- Bevaring/Formidling/Fællesskab forbliver inset og får 14 px mellem hinanden;
- Alpha.17 Eventlistens 280–360 px kortformat og Designer-controls ændres ikke;
- Alpha.14/16 mobilmenu/header/footer ændres ikke.

## Acceptance på test4

Alpha.18 er visuelt godkendt når:

1. hero-billedet går helt til mobilskærmens sidekanter;
2. tagline/Om/øvrige store sektioner maler til kanten som V1, men teksten har læsbar indvendig padding;
3. der ikke længere er dobbelte store hvide mellemrum mellem afsnit;
4. normale sektioner har ca. 24 px separation;
5. Bevaring/Formidling/Fællesskab fortsat fremstår som inset cards;
6. Eventliste og menu fortsat fungerer som i Alpha.17.
