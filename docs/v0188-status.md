# Visual Designer Manager 0.1.88 status

## VDM-COLOR-POPUP-002

- Gendan kompakt popup-adfærd uden at rulle Siteindstillinger eller øvrige v0.1.87-rettelser tilbage.
- Ingen farveflade eller temapalette må optage plads i Inspector før brugeren klikker på farvefeltet.
- Popup starter i almindelig farvevælger med SV-flade, hue, HEX og standardfarver.
- Tema-knappen skifter samme popup til Temafarver + Senest brugt; knappen skifter tilbage til Farvevælger.
- Annuller/Escape/klik udenfor gendanner original farve; Anvend committer én change-event.
- Alle input[type=color] i side-Designer og Header/Footer Designer enhanced via direkte refresh + MutationObserver.
- WordPress/Iris picker er ikke runtime-afhængighed i denne version.
