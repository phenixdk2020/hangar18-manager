# Hangar18 Manager Clean 0.1.7 – række/kolonne drop-kontrakt

Status: godkendt designregel, 25. august 2026.

## Fysisk geometri

Elementets canonical `x/y/w/h` beskriver kun det synlige element. Editorlabel, elementtype, kort ID og drag-håndtag er editor-chrome og må ikke indgå i fysisk højde eller bredde.

## Drop-zoner

Et almindeligt element har fire drop-zoner:

- **Over** – opret selvstændig række før mål-rækken.
- **Under** – opret selvstændig række efter mål-rækken.
- **Venstre** – placer i samme række før målelementet.
- **Højre** – placer i samme række efter målelementet.

En `Sektion` eller `Kasse` har desuden en central **Ind i Kassen**-zone. Slip i denne zone ændrer `parentId` til den valgte parent.

Når markøren ligger på den tomme indre flade i en Sektion/Kasse, betyder drop `Ind i Kassen`. Når markøren ligger ved parentens ydre kant, rout'es drop til parentens sibling-zoner, så en Kasse kan placeres Over/Under/Venstre/Højre i forhold til en anden Kasse.

## Rækker og breddefordeling

Venstre/Højre danner en fælles fysisk række. Rækken fordeles deterministisk over alle 120 units:

- 1 element: 120 units.
- 2 elementer: 60/60.
- 3 elementer: 40/40/40.
- Andre antal fordeles så jævnt som muligt; eventuelle rest-units fordeles fra venstre mod højre.

Flyttes et element ud af en række, fordeles de resterende elementer igen over 120 units.

Over/Under opretter en fuldbredde-række (`x=0`, `w=120`) før eller efter den visuelle mål-række. Elementet kan derefter resizes manuelt.

## Parent auto-grow

Sektion/Kasse bruger valgt højde som minimum. Den synlige parent skal vokse, hvis børnenes faktiske bundkant kræver mere plads. Fjernes eller flyttes børn, må auto-grow falde tilbage mod den valgte minimumshøjde.

## Canonical state

Drop ændrer modellen først. Canvas renderes derefter fra modellen. DOM må ikke være Save-kilde. `order`, `parentId` og `geometry.desktop` opdateres i samme Undo/Redo-transaktion.

## Diagnostics

Drag/drop-logning skal mindst indeholde `id/type`, fra/til-parent, `dropZone`, række-reference og resulterende strukturel modelsummary. Rå tekst, credentials, nonces og tokens må ikke logges.
