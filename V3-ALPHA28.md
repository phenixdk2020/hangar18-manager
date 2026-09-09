# Visual Designer Manager V3 – Alpha.28

Version: `3.0.0-alpha.28`

## Formål

Mobil skal følge layoutet, der bygges i Desktop-designeren. V3 skal ikke have et separat mobil-layout med egne x/y/w/h-positioner, som kan drive væk fra Desktop.

## Layout-kontrakt

- Desktop er master for mobilens placering og visuelle rækkefølge.
- Samme node-træ, parent/child-hierarki, tekst, farver og elementtyper bruges på alle breakpoints.
- Mobil må ændre præsentation responsivt, fx stacke kolonner til én kolonne, bruge hamburger-menu og anvende mobile sideafstande.
- Mobil må ikke have en separat kanonisk nodeplacering eller separat rækkefølge.
- Flytning, resize og reorder i Desktop-designeren følger automatisk med til Mobile.

## Teknisk ændring

### LayoutModel

`geometry.mobile` normaliseres direkte fra `geometry.desktop` med `inheritDesktop=true`. Historiske mobile x/y/w/h-værdier fra tidligere V1/V3-migreringer ignoreres som layoutkilde.

Laptop og Tablet beholder deres eksisterende responsive kontrakt i denne version; ændringen er målrettet Mobile.

### Designer

Ved hver normalize/save synkroniseres Mobile-geometrien til Desktop-geometrien. Nye elementer oprettes ligeledes med Mobile som direkte Desktop-arv.

### Frontend

Mobile `effectiveGeometry()` bruger Desktop direkte. One-column mobil-flowet sorterer elementer efter Desktop `y`, derefter `x`, derefter `order`, så mobilrækkefølgen følger det visuelle Desktop-layout.

Responsive CSS må stadig ændre bredde, stacking, spacing og hamburger-præsentation, men ikke layoutets kanoniske rækkefølge.

## Bevarede kontrakter

- V1 0.1.93 er fortsat låst byte-for-byte ved `dc3bad403c764f4ec123a526333a781d05dde491`.
- Alpha.27 fælles Paint Source bevares: Desktop og Mobile bruger samme Designer-farver/kasser.
- Alpha.26 Footer Genveje følger den valgte Website-menu.
- Alpha.22 menu-controlleren med button/is-open bevares.
- Alpha.25 natural-flow/mobile height reset bevares.
- Responsive Sideindstillinger for afstande bevares.

## Acceptance

På Mobile skal en ændring i Desktop-designeren kunne verificeres uden separat mobilredigering:

1. Flyt to sektioner i Desktop → mobil rækkefølge følger samme visuelle rækkefølge.
2. Flyt elementer inde i en Section/Container → mobil stacking følger Desktop top/venstre-rækkefølgen.
3. Ændr tekst/farve/kasse på Desktop → samme indhold/paint på Mobile.
4. Flere Desktop-kolonner må stacke til én kolonne på Mobile uden at oprette et separat node-træ.
5. Header må stadig skifte til hamburger-præsentation på Mobile.
6. Footer Genveje skal fortsat afspejle Website-menuen.
