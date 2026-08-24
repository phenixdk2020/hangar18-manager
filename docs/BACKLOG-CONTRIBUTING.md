# Hangar18 backlog- og commitkonvention

Den aktuelle backlog findes altid via **`docs/BACKLOG-CANONICAL.md`**. Filnavnet må ikke gættes ud fra en gammel `active-backlog-v*.md`.

Alle andre versionerede backlogfiler end den pointeren angiver er historiske snapshots. Historisk tekst som siger “aktuel/current/canonical” beskriver kun filens daværende tidspunkt og må ikke bruges som nutidig status.

## Backlog-ID

- Hvert aktivt arbejde har ét entydigt ID.
- ID'et bevares gennem commits, QA og releases.
- En opgave lukkes først, når dens Definition of done er opfyldt og canonical backlog er opdateret.
- Nye fund får nye ID'er; de må ikke skjules som ekstra scope under et afsluttet punkt.
- Det maskinlæsbare `docs/backlog-index.json` har altid feltet `dependencies` for hver post. Ingen afhængigheder repræsenteres som `[]`.
- Eksplicitte afhængigheder skrives enten som `BLOKERET AF BACKLOG-ID` i status eller som `Dependencies: BACKLOG-ID, ...` / `Afhænger af: BACKLOG-ID, ...` i DoD. Almindelige teksthenvisninger tæller ikke automatisk som dependencies.
- Governance fejler hvis en eksplicit dependency peger på et ukendt backlog-ID.

## Commit messages

Større ændringer skal begynde med de relevante backlog-ID'er, fx:

`TRACE-077 TRACE-078: add persistent recording indicator and session metadata`

Flere tæt beslægtede ID'er kan stå i samme commit. Release-package commits fra workflow er undtaget, fordi de genereres automatisk.

## Canonical og snapshots

- `docs/BACKLOG-CANONICAL.md` indeholder den eneste autoritative canonical-pointer.
- `tools/backlog-snapshot-guard.py` kræver at pointeren er den højeste versionerede backlogfil.
- Alle øvrige `docs/active-backlog-v*.md` klassificeres maskinelt som `historical_snapshot`.
- Statusændringer skrives i den aktuelle canonical delta/extends-kæde; historiske snapshots ændres ikke for at omskrive fortiden.

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
