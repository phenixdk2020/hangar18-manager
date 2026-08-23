# Hangar18 backlog- og commitkonvention

Denne fil supplerer den canonical `docs/active-backlog-v*.md`.

## Backlog-ID

- Hvert aktivt arbejde har ét entydigt ID.
- ID'et bevares gennem commits, QA og releases.
- En opgave lukkes først, når dens Definition of done er opfyldt og canonical backlog er opdateret.
- Nye fund får nye ID'er; de må ikke skjules som ekstra scope under et afsluttet punkt.

## Commit messages

Større ændringer skal begynde med de relevante backlog-ID'er, fx:

`TRACE-077 TRACE-078: add persistent recording indicator and session metadata`

Flere tæt beslægtede ID'er kan stå i samme commit. Release-package commits fra workflow er undtaget, fordi de genereres automatisk.

## Release-config

`release-config.json` skal indeholde:

- `version`
- `title`
- `channel` (`test`, `staging` eller `production`)
- `backlog_ids` med mindst ét ID for ændrede backlogpunkter
- `changelog`

Changelog skal beskrive bruger-/driftsmæssig effekt. `backlog_ids` er den maskinlæsbare binding til master-backloggen.

## Release notes

`update.json` og `release-manifest.json` skal begge indeholde de relevante backlog-ID'er. Dermed kan en installeret ZIP spores tilbage til den opgave, QA og release der producerede den.

## Sikkerhed

Public I10 cutover er aldrig implicit godkendt af et backlog-ID, en commit, en release eller en QA PASS. Production cutover følger fortsat de særskilte I9/I10 gates.
