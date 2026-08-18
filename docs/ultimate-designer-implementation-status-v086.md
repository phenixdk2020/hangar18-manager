# Ultimate Designer — implementeringsstatus pr. v0.8.6

**Opdateret:** 18. august 2026  
**Aktuel public pluginversion:** Hangar18 Manager 0.8.6  
**Main release commit:** `39d713e4f64cc0c1540f85d8f3bc686a3579820d`  
**Release package SHA-256:** `efbba85372410d0818bcd7d4aea7decdb329f75b0c63290a28600c3eb2e1ec29`

## Kort status

Ultimate Designer er ikke længere kun en design-/arkitekturbacklog. Den generelle arkitektur, services, QA-kontrakter og de vigtigste wp-admin integrationslag er implementeret frem til v0.8.6.

Den offentlige sidekonvertering er **bevidst ikke startet**. Det er et krav, ikke en mangel: eksisterende sider konverteres til sidst, og Vehicle/Event/Gallery forbliver på beskyttet legacy-runtime indtil deres separate kompatibilitets- og rollback-gates er godkendt.

## Leverancestatus

| Område | Status | Leveret | Næste gate |
|---|---|---|---|
| Design-QA + UD-001..120 | ✅ Færdig | Godkendt designspecifikation samt arkitektur/core-dækning med tests og dokumentation. | Ingen designblokering. |
| I1 Admin integration | ✅ Færdig | Ultimate Designer admin-overblik i shadow mode. | Bevares admin-only frem til cutover. |
| I2 Header/Footer Builder | ✅ Færdig · shadow | Visuel template-editor, assignments og preview-flow. | Public assignment først efter I10. |
| I3 Menu Builder v2 | ✅ Færdig · shadow | Nested menu, presets, sidevalg og accessibility-preview. | Public menu-skift først efter acceptance. |
| I4 Side Health | ✅ Færdig | Design/Mobile/A11y/Performance/SEO-analyse med elementlinks. Fra v0.8.5 sammenklappet som standard. | Manuel live-verifikation på test2. |
| I5 Asset Manager | ✅ Færdig | Collections/tags/usage/focal point/duplicates/derivatives. | Manuel live-verifikation. |
| I6 Portability | ✅ Færdig · isoleret | Export/import, dry-run, remap, backup og restore i workspace. | Live import/cutover holdes adskilt. |
| I7 Permissions / Design Lock | ✅ Færdig · shadow | Capability/rolle-preview, additive installation og design-lock policy. | Håndhæves fuldt i ny runtime efter cutover. |
| I8 AI | ✅ Færdig · sandbox | Provider-neutral forslag/accept med signeret proposal-flow. | Ingen direkte page-write. |
| I9 Manual QA dashboard | 🟡 Værktøj færdigt · evidens mangler | Dashboard, manuelle gates og copy-only rollback preflight. | Browser/a11y/test2/V-E-G/rollback evidens skal dokumenteres. |
| I10-A Planner / shadow | ✅ Færdig · v0.8.3 | Fast konverteringsrækkefølge og copy-only shadow workspace. | Kræver I9 + acceptance. |
| I10-B Shadow acceptance | ✅ Færdig · v0.8.4 | Desktop/tablet/mobile + save/preview/revision/rollback evidens bundet til `SourceHash`. | Udføres på aktuel shadow-copy. |
| UX v0.8.5 | ✅ Færdig | Auto-kasser, visuelt Tabel-værktøj, Inspector-kobling og kompakt Side Health. | Manuel editor-QA på test2. |
| I10 Signed preflight | ✅ Færdig · v0.8.6 | Source-drift, WP Page ID/permalink, sekvens/QA/acceptance checks og HMAC-snapshot. | `Executable=false` / `PublicMutationAvailable=false` indtil godkendt næste fase. |
| I10-C Sammenligningsside | 🔒 Blokeret | Ingen public cutover-handler er eksponeret. | Alle I9-gates PASS + gyldig acceptance/preflight. |
| I10-D Kernesider | 🔒 Blokeret | Hjem → Om → Kontakt → Bliv medlem er planlagt, men ikke konverteret. | Forrige trin accepteres ét ad gangen. |
| I10-E Vehicle/Event/Gallery | 🔒 Blokeret · protected legacy | Legacy runtime og kompatibilitetskontrakt er bevaret. | Separat visuel/funktionel regression + rollback + compatibility accept. |
| I10-F Legacy removal | 🔒 Blokeret | Ingen legacy-kode fjernes endnu. | Kun efter final acceptance af alle sider/domæner. |

## v0.8.5 — editor-UX

v0.8.5 lukkede konkrete UX-gaps i den eksisterende sideeditor:

- **Auto-kasser** bruger eksisterende Grid/Container-schema og fordeler kasser i lige desktop-kolonner.
- Hver kasse beholder individuelle design-, typografi-, spacing-, border-, shadow- og responsive indstillinger.
- **Tabel** er et visuelt værktøj oven på det eksisterende sanitiserede HTML-element.
- Inspector-koblingen følger det valgte element korrekt, også når indstillings-body flyttes ind i Inspector.
- **Side Health starter sammenklappet**, så analysepanelet ikke overskygger de almindelige Inspector-indstillinger.

## v0.8.6 — signed cutover preflight

v0.8.6 gør det muligt at dokumentere, om en side er teknisk klar til en fremtidig cutover, uden at give mulighed for at udføre den:

- source-drift sammenligner shadow `SourceHash` med den aktuelle legacy editor-state;
- WordPress Page ID og permalink skal fortsat være til stede;
- globale I9-gates og I10-rækkefølgen evalueres;
- shadow acceptance skal være gyldig for den aktuelle `SourceHash`;
- et eligible snapshot kan HMAC-signeres og tidsbegrænses;
- ændres state, identity eller hash, matcher det tidligere snapshot ikke længere;
- `Executable=false`;
- `PublicMutationAvailable=false`;
- der findes ingen activate/cutover/publish-handler i denne fase.

## Fast migrationsregel

Den faktiske konvertering af eksisterende sider ligger **sidst**:

1. tag backup og fastlås rollback-reference;
2. brug én ikke-kritisk sammenligningsside;
3. sammenlign legacy/new på desktop, tablet og mobil;
4. verificer save, preview, revision og rollback;
5. konverter Hjem;
6. konverter Om foreningen;
7. konverter Kontakt;
8. konverter Bliv medlem;
9. konverter først derefter Vehicle/Event/Gallery efter deres separate compatibility-gates;
10. fjern først legacy-kode efter final acceptance og dokumenteret rollback.

## QA-status

Den automatiserede architecture/contract matrix er grøn på PHP **8.0, 8.2 og 8.3** for den aktuelle v0.8.6-kode. Den automatiske matrix er ikke en erstatning for den manuelle I9-evidens.

Før I10-C kan åbnes, skal følgende manuelle/live evidens være dokumenteret:

- Chrome;
- Edge;
- Firefox;
- Safari/WebKit;
- keyboard/screen-reader kerneflow;
- test2 live end-to-end;
- Vehicle/Event/Gallery visuel og funktionel regression;
- migration/rollback rehearsal på live-kopi.

## Dokumenter der udgør den aktuelle styringspakke

- `docs/WordPress_Ultimate_Designer_Designspecifikation_v01.01.00.docx`
- `docs/ultimate-designer-implementation-status-v086.md`
- `docs/integration-backlog-after-ud120.md`
- `docs/architecture-migration.md`
- `docs/architecture-legacy-domain-contract-v0530.md`
- `DESIGN-MANUAL.md`

Designspecifikationen er fortsat produktets designmæssige baseline. Denne statusfil er den korte tekniske sandhed for, hvor implementeringen står lige nu.
