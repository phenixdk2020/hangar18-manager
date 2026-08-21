# Ultimate Designer — Slet side sikkert

**Funktion:** PAGE-DELETE-001  
**Status:** frigivet i **Hangar18 Manager v0.8.42**; automatiseret QA PASS, manuel test2 UI-sanity PENDING.  
**Princip:** safety backup → WordPress Papirkurv → eksisterende B1 restore.

## Hvad funktionen gør

`Slet side` er en kontrolleret måde at fjerne en almindelig side fra aktiv brug uden permanent destruktion.

```text
Åben almindelig side
      ↓
Slet side
      ↓
skriv sidens titel præcist
      ↓
bekræft én gang mere
      ↓
B1-kompatibel safety backup
      ↓
WordPress Papirkurv
      ↓
Audit-log
```

Den bruger **ikke** permanent WordPress-delete og sletter ikke råt i databasen.

## Hvilke sider kan slettes

Funktionen er beregnet til almindelige sider, fx en midlertidig kladde/testside.

Følgende kernesider er eksplicit beskyttede og kan ikke slettes gennem PAGE-DELETE-001:

- Hjem (`hjem`)
- Køretøjer og materiel (`koeretoejer-og-materiel`)
- Events (`events`)
- Billedgalleri (`billedgalleri`)

Vehicle/Event/Gallery forbliver dermed under de eksisterende protected-domain-regler.

## Sådan slettes en almindelig side

1. Åbn **Hangar18 Manager → Sider**.
2. Åbn den almindelige side, der skal fjernes.
3. Klik **Slet side**.
4. En dialog viser sidens aktuelle titel.
5. Skriv titlen **præcist**.
6. Bekræft den sidste advarsel.
7. Systemet opretter safety backup **før** WordPress Trash udføres.
8. Siden flyttes til WordPress Papirkurv.
9. Success-beskeden viser safety-backup-filnavnet.

Hvis prompten annulleres, titlen er forkert eller den sidste bekræftelse annulleres, udføres ingen mutation.

## Rettigheder

Serveren kræver alle disse kontroller:

- WordPress capability `delete_pages`;
- objektspecifik `delete_post` for den konkrete side;
- gyldig WordPress nonce;
- den aktuelle sidetitel som eksakt bekræftelse.

Browserdialogen er kun UX. Serverkontrollen er autoritativ.

## Safety backup

Før Trash gemmes en B1-kompatibel JSON-backup i den eksisterende Hangar18 backupmappe.

Backupen indeholder bl.a.:

- side-ID;
- titel og slug;
- status før Trash;
- parent/excerpt/content;
- featured image ID;
- Page Editor-state for samme slug, hvis den findes;
- pluginversion og tidspunkt;
- reason markeret som PAGE-DELETE-001.

Backupen oprettes før `wp_trash_post()` kaldes. Hvis Trash bagefter skulle fejle, bevares backupen.

## Gendan en slettet side

Der oprettes ikke en ny restore-motor. Brug det eksisterende **B1 · Gendan sidebackup**-panel:

1. Åbn **Ultimate Designer → B1 · Gendan sidebackup**.
2. Find PAGE-DELETE safety-backupen fra success-beskeden/auditten.
3. Kontrollér side-ID, slug og backupdato.
4. Vælg **Erstat original**, når preflight tillader det.
5. B1 opretter sin normale sikkerhedsbackup af den aktuelle tilstand før restore.
6. Den oprindelige side-ID og slug bevares, mens status/indhold/Page Editor-state gendannes fra PAGE-DELETE-backupen.

## Audit

En gennemført Trash-operation registrerer:

- UTC-tid;
- mode `trash-page`;
- side-ID;
- slug;
- titel;
- tidligere WordPress-status;
- safety-backup-filnavn;
- bruger-ID.

Afviste/annullerede handlinger skal ikke optræde som succesfulde Trash-auditposter.

## Manuel QA

Brug kun en ny midlertidig testside.

| Test | Forventning |
|---|---|
| Klik Slet side → Cancel | ingen mutation |
| Forkert titel | ingen mutation |
| Korrekt titel → sidste Cancel | ingen mutation |
| Korrekt titel → bekræft | side i WordPress Trash + safety backup |
| Restore fra safety backup | oprindelig status/indhold/editor-state tilbage |
| Forsøg på Hjem/Vehicle/Event/Gallery | funktionen blokeret |
| Bruger uden delete-rettighed | serveren afviser handlingen |

## Sikkerhedsgrænse

PAGE-DELETE-001 er en administrativ sidefunktion. Den:

- konverterer ikke public-sider til Ultimate Designer;
- ændrer ikke I9-gates;
- autoriserer ikke I10;
- ændrer ikke protected Vehicle/Event/Gallery runtime;
- må ikke bruges som genvej til legacy removal.
