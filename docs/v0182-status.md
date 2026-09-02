# Visual Designer Manager v0.1.82 – status

## Scope

- `VisualBlockConversionService` opretter knapper med `placementMode = overlay`.
- Ny selektiv migration reparerer allerede konverterede knapper, herunder sider som **Bliv medlem – kopi (ID 228)** når plugin-opdateringen kører på sitet.
- Kun knapper med converterens deterministiske `button-<source-suffix>-...` ID ændres.
- Almindelige Designer-knapper og allerede flydende knapper ændres ikke.
- Aktive layouts får backup og en ny Designer-version før ændringen.
- Pending konverteringskandidater repareres uden automatisk godkendelse.

## Release gate

Release candidate; central ZIP/manifest-build kræves efter grøn QA.
