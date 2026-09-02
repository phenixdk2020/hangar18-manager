# Visual Designer Manager v0.1.80 – status

Status: release candidate implementeret.

## Scope
- Collection-H1 for Events, Billedgalleri og Køretøjer er et normalt Designer-element.
- Eventdetalje er opdelt i flytbare Eventværdi/Eventbillede/Eventfelt-elementer.
- H1 er understøttet som almindelig Tekst-overskrifttype.
- Data-menuen er skjult; intern ModuleBinding/ModuleStore bevares.
- Migration gemmer backup før ændring af eksisterende layouts.

## QA
Se `.github/scripts/v0180_composable_qa.py` og apply-workflowets fulde regression-gate.
