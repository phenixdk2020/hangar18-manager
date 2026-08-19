# Ultimate Designer – implementeringsstatus

**Dokumentstatus:** 19. august 2026  
**Pluginbaseline:** Hangar18 Manager **v0.8.6**  
**GitHub main:** `39d713e4f64cc0c1540f85d8f3bc686a3579820d`  
**Designspecifikation:** `WordPress_Ultimate_Designer_Designspecifikation_v01.02.00.docx`

## Kort status

Ultimate Designer-arkitekturen og de planlagte core-/integrationselementer er i vid udstrækning implementeret. Den nuværende offentlige sidekonvertering er **ikke startet med vilje**. Legacy-renderingen er fortsat autoritativ for eksisterende sider, og Vehicle/Event/Gallery er fortsat beskyttede legacy-domæner.

| Område | Status | Bemærkning |
|---|---|---|
| Arkitektur / strangler foundation | ✅ Færdig | Modulær `src/`-arkitektur, contracts, registries, schema, compatibility, security og runtime bridge. |
| E6 Site Builder core | ✅ Færdig | Header/Footer/Menu/template-services og passiv runtime. |
| E7 Interaction core | ✅ Færdig | Forms, validation, action chains, modal/popup og sikre redirect/webhook-grænser. |
| E8 Workflow | ✅ Færdig | Autosave, permanente revisioner, preview, staging og pre-publish backup. |
| E9 Assets | ✅ Færdig | Asset metadata, usage, focal point, derivater og dubletdetektion. |
| E10 Permissions | ✅ Færdig | Named capabilities, additive rolleopskrifter, design lock og editable component inputs. |
| E11 Quality / Side Health | ✅ Færdig | Design, mobile, accessibility, performance og SEO-analyse. |
| E12 AI core | ✅ Færdig | Provider-neutral suggestion layer; ingen direkte writes. |
| E13 Portability | ✅ Færdig | Export/import, dry-run, conflict plan, ID/asset remap, backup og rollback. |
| E14 Automated QA | ✅ Færdig | PHP 8.0/8.2/8.3, security, performance, migration/rollback og browser-engine regression. |
| I1 Admin integration | ✅ Færdig | Ultimate Designer dashboard i wp-admin, shadow-only. |
| I2 Header/Footer Builder | ✅ Færdig i shadow/admin | Visuel templateeditor; ingen public assignment/cutover. |
| I3 Menu UI v2 | ✅ Færdig i shadow/admin | Nested menu, presets, keyboard-preview og eksplicit side-tilvalg/fravalg. |
| I4 Side Health editorpanel | ✅ Færdig | Live/read-only analyse i Sider-editoren; panelet er sammenklappet som standard. |
| I5 Asset Manager UI | ✅ Færdig | Collections/tags/usage/focal point/dubletscan/derivater; original og Media IDs bevares. |
| I6 Import/Export UI | ✅ Færdig | Dry-run-first, signeret plan og isoleret portability workspace. |
| I7 Permissions / Design Lock UI | ✅ Færdig | Additive-only installation; legacy `edit_pages` fjernes ikke. |
| I8 AI UI | ✅ Færdig | Provider-registry/settings uden credentials i options; pending suggestions + Apply/Undo-plan. |
| I9 Manual QA dashboard | 🟡 Teknik færdig | Evidensmodel/dashboard/preflight findes; live/manual evidens skal stadig udføres. |
| I10 Conversion planner | 🟡 Preflight færdig | Planner, shadow-copy, acceptance ledger, source-drift og signed cutover-preflight findes; public activation findes ikke. |
| Offentlig sidekonvertering | ⛔ Ikke startet | Bevidst låst bag manuel QA, acceptance, backup og rollback-bevis. |
| Vehicle/Event/Gallery | 🔒 Legacy beskyttet | Må først skifte renderer efter særskilt compatibility proof og senere kontrolleret konvertering. |

## Leverancer og versioner

- **v0.6.0 – Architecture Foundation:** autoloading, contracts, registries, compatibility policy, schema-validering og runtime bridge.
- **UD-060 – Starter schemas:** passive/generiske Vehicle/Event/Gallery-presets uden migration eller runtime-skift.
- **v0.6.x – E6–E13:** Site Builder, Interaction, Workflow, Assets, Permissions, Quality, AI og Portability core.
- **v0.7.0 – E14 Automated QA baseline:** browser-engine, security, performance, migration/rollback og end-to-end gates.
- **v0.7.1–v0.7.3 – Editor UX:** automatisk save-resumé, valgfri brugerkommentar, Typografi-fane, valgfri overskrift og korrekte linjeskift.
- **v0.7.4 – I1:** Ultimate Designer adminintegration/dashboard.
- **v0.7.5 – I2:** Visual Header/Footer Builder i shadow mode.
- **v0.7.6 – I3:** Menu UI v2.
- **v0.7.7 – I4:** Live Side Health i Sider-editoren.
- **v0.7.8 – I5:** Asset Manager UI samt eksplicit side-tilvalg/fravalg i menuen.
- **v0.7.9 – I6:** Import/Export UI med dry-run, signeret plan og isoleret workspace.
- **v0.8.0 – I7:** Permissions & Design Lock UI.
- **v0.8.1 – I8:** Provider-neutral AI UI/suggestion sandbox.
- **v0.8.2 – I9:** Manual QA evidence dashboard og copy-only rollback rehearsal/preflight.
- **v0.8.3 – I10-A:** Conversion Planner + shadow workspace.
- **v0.8.4 – I10-B:** Shadow Acceptance Ledger bundet til `SourceHash`.
- **v0.8.5 – Editor UX+:** Auto-kasser med lige kolonner, individuelt kasse-design, visuelt Tabel-værktøj og sammenklappet Side Health.
- **v0.8.6 – I10-C:** source-drift detection, WordPress page-ID/permalink checks og HMAC-signeret, tidsbegrænset, **ikke-eksekverbart** cutover-preflight.

## Aktuelle manuelle gates før public cutover

Følgende evidens skal stadig dokumenteres i I9-dashboardet:

1. Seneste Chrome – kerneflows.
2. Seneste Edge – kerneflows.
3. Seneste Firefox – kerneflows.
4. Seneste Safari – kerneflows.
5. Screen-reader core flow.
6. `test2` live-site E2E.
7. Vehicle/Event/Gallery visuel/funktionel regression.
8. Migration + rollback på en live copy.

Automatisk QA kan **ikke** sætte disse manuelle gates til PASS.

## Fastlagt konverteringsrækkefølge

1. Ikke-kritisk sammenligningsside.
2. Hjem.
3. Om foreningen.
4. Kontakt.
5. Bliv medlem.
6. Vehicle/Event/Gallery – **sidst**, og kun efter særskilt compatibility proof.
7. Legacy-kode fjernes først efter endelig acceptance og når rollback ikke længere er nødvendig.

## Næste arbejde

- Kør og dokumentér I9 manual QA på `test2`.
- Ret eventuelle fejl fundet af live QA/Side Health uden at konvertere eksisterende sider.
- Opret/genskab shadow-copy for sammenligningssiden og dokumentér side-specifik acceptance.
- Kør signed I10 preflight og verificér ingen source-drift, ID/permalink-fejl eller sekvens-blockers.
- Design/godkend derefter en **separat eksplicit public activation/cutover-mekanisme** med rollback. Den findes ikke i v0.8.6.
