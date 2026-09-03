# Visual Designer Manager v0.1.87 status

## Unified color picker

Status: release candidate

- Én canonical VDM color picker ejer alle `input[type="color"]` på side-Designer og Global Header/Footer Designer.
- Historisk v0.1.35 picker-JS/CSS er ikke længere en del af runtime dependency chain.
- v0.1.81 WordPress `wp-color-picker` er den eneste aktive picker.
- Temafarver, senest brugte farver, fri HEX og WordPress/Iris-farvevalg bevares.
- Inspector kalder `VDMColorPicker.refresh(host)` direkte efter hver render.
- MutationObserver håndterer øvrige dynamisk indsatte farveinputs som fallback.
- `Anvend` er eneste commit-path; `Annuller` og Escape ændrer ikke canonical model.
- QA kræver at Baggrund, Tekstfarve, Overskriftsfarve og Rammefarve alle er dækket.
