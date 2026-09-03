from pathlib import Path
import json

ROOT=Path('.')
PLUGIN=ROOT/'clean/hangar18-manager/hangar18-manager.php'
EXPORT=ROOT/'clean/hangar18-manager/src/Admin/ExportController.php'
HISTORY=ROOT/'clean/hangar18-manager/release-history.json'
NOTES=ROOT/'clean-release-notes.html'
BACKLOG=ROOT/'docs/BACKLOG-CANONICAL.md'
STATUS=ROOT/'docs/v0193-status.md'


def read(p): return p.read_text(encoding='utf-8')
def write(p,s): p.write_text(s,encoding='utf-8')
def rep(text,old,new,label):
    if old not in text: raise SystemExit('Missing marker: '+label)
    return text.replace(old,new,1)

plugin=read(PLUGIN)
plugin=rep(plugin,'Version: 0.1.92','Version: 0.1.93','plugin header')
plugin=rep(plugin,"define('VDM_VERSION', '0.1.92');","define('VDM_VERSION', '0.1.93');",'VDM_VERSION')
plugin=rep(plugin,"define('H18_CLEAN_VERSION', '0.1.92');","define('H18_CLEAN_VERSION', '0.1.93');",'compat version')
write(PLUGIN,plugin)

export=read(EXPORT)
repls=[
("'pages' => 'Webpages'","'pages' => 'Websider'",'pages label'),
("'videos' => 'Video'","'videos' => 'Videoer'",'videos label'),
("            'Export',\n            'Export',","            'Eksport',\n            'Eksport',",'menu title'),
("        echo '<h1>Export</h1>';","        echo '<h1>Eksport</h1>';",'page heading'),
("self::card('plugin', 'Export Plugin'","self::card('plugin', 'Eksporter plugin'",'plugin card'),
("self::card('theme', 'Export Tema'","self::card('theme', 'Eksporter tema'",'theme card'),
("self::card('pages', 'Export Webpages'","self::card('pages', 'Eksporter websider'",'pages card'),
("self::card('navigation', 'Export Navigation'","self::card('navigation', 'Eksporter navigation'",'navigation card'),
("self::card('images', 'Export Billeder'","self::card('images', 'Eksporter billeder'",'images card'),
("self::card('documents', 'Export Dokumenter'","self::card('documents', 'Eksporter dokumenter'",'documents card'),
("self::card('videos', 'Export Video'","self::card('videos', 'Eksporter videoer'",'video card'),
("self::card('media', 'Export Alle medier'","self::card('media', 'Eksporter alle medier'",'media card'),
("kan køre Export.","kan køre eksport.",'security wording'),
("Ukendt exporttype.","Ukendt eksporttype.",'unknown type'),
("midlertidig exportfil.","midlertidig eksportfil.",'temp error'),
("ZIP-export.","ZIP-eksport.",'zip error'),
("Export fejlede:","Eksport fejlede:",'generic error'),
("Exportpakken blev ikke oprettet korrekt.","Eksportpakken blev ikke oprettet korrekt.",'package error'),
("'>Export ' . esc_html(self::LABELS[$kind]) . '</button>'","'>Eksporter ' . esc_html(self::LABELS[$kind]) . '</button>'",'button label'),
]
for old,new,label in repls:
    export=rep(export,old,new,label)
write(EXPORT,export)

history=json.loads(read(HISTORY))
history['versions'].insert(0,{
 'version':'0.1.93','date':'2026-09-03','items':[
  'VDM-RELEASE-GATE-003: den centrale release-workflow kræver nu de aktuelle QA-gates for v0.1.92 eksportintegritet, v0.1.91 formulardesign, v0.1.90 WYSIWYG, v0.1.89 Manager-oprydning samt site/event/portable regressioner.',
  'En release kan derfor ikke længere publiceres alene på de ældre foundation-tests.',
  'Eksport-siden bruger nu konsekvent dansk terminologi: Eksport, Eksporter plugin/tema/websider/navigation/billeder/dokumenter/videoer/medier.',
  'Canonical backlog-pointeren er opdateret til Visual Designer Manager og markerer 0.1.93 som vedligeholdelsesbaseline før den kontrollerede v0.2.0 navne-/basename-migration.'
 ]
})
write(HISTORY,json.dumps(history,ensure_ascii=False,indent=2)+'\n')
notes=read(NOTES)
section='<section data-version="0.1.93"><h2>0.1.93</h2><ul><li><strong>Release-gate hærdet:</strong> den centrale release kører nu automatisk de aktuelle 0.1.92/0.1.91/0.1.90/0.1.89 QA-gates før pakning.</li><li>Siteindstillinger, Event/Editor og portable transfer-regressioner er også en obligatorisk del af releaseflowet.</li><li><strong>Eksport</strong>-siden bruger nu konsekvent dansk terminologi i menu, overskrifter, knapper og fejltekster.</li><li>Canonical backlog er synkroniseret med den aktuelle 0.1.93-baseline og næste store v0.2.0-migration.</li></ul></section>\n'
anchor='<section data-version="0.1.92">'
if anchor not in notes: raise SystemExit('release notes anchor missing')
notes=notes.replace(anchor,section+anchor,1)
write(NOTES,notes)

write(BACKLOG,'''# Visual Designer Manager — canonical backlog pointer\n\n**Canonical arbejdsbacklog:** `docs/clean-backlog-v0100.md`  \n**Aktuel vedligeholdelsesbaseline:** `v0.1.93`  \n**Næste planlagte hovedmilepæl:** `v0.2.0`\n\nDette dokument er den entydige indgang til projektets aktuelle backlog og fortolker den historiske clean-backlog i forhold til den nuværende Visual Designer Manager-arkitektur.\n\n## Aktuel status · 2026-09-03\n\n- Visual Designer Manager er frigivet gennem v0.1.93.\n- Konvertering og den gamle Eksport / import-menu er skjult; migrations- og recovery-motorerne bevares internt.\n- Eksport har én normal indgang med **Eksporter alt**, komplet portable site-ZIP og to-lags SHA-256-verifikation.\n- Siteindstillinger, farvevælger, formular-WYSIWYG og formulardesign er på den aktuelle regression-gate.\n- Den centrale release-workflow skal bestå de aktuelle QA-gates før en ny updater-ZIP publiceres.\n- Den kontrollerede navne-/plugin-basename-migration er fortsat reserveret til v0.2.0 og må ikke sniges ind i 0.1.x vedligeholdelsesversioner.\n\n## Canonical regler\n\n- `clean/hangar18-manager/` er fortsat den autoritative plugin-kilde indtil v0.2.0-migrationen gennemføres kontrolleret.\n- Nye produkt-/runtime-navne skal bruge **Visual Designer Manager / VDM**. Historiske H18/Clean-identifikatorer må kun overleve som dokumenteret compatibility-, storage- eller migrationskontrakt.\n- `docs/clean-backlog-v0100.md` er den detaljerede historiske/arkitektoniske arbejdsbacklog. Punkter, der allerede er implementeret i nyere releases, skal læses som historik og ikke som åbne opgaver.\n- `docs/v01xx-status.md`, releasehistorik og grønne QA-gates er autoritativ dokumentation for gennemførte 0.1.x-opgaver.\n- Gamle webpages/data må først destruktivt ændres, når en verificeret portable eksport og rollback-vej findes.\n- Historiske backlogfiler ændres ikke for at omskrive fortiden; denne pointer angiver nutidig status.\n\n## v0.2.0 — reserveret migrationsscope\n\nNår den verificerede siteeksport er klar, omfatter v0.2.0 den planlagte kontrollerede oprydning af aktiv `clean`/`h18`/Hangar18-frameworknavngivning, pluginfolder/main-file identity, admin/AJAX/REST-identifikatorer og updater/activation-basename. Legacy storageværdier bevares kun gennem eksplicit compatibility/migration, indtil import og før/efter-QA er bestået.\n''')
write(STATUS,'''# Visual Designer Manager v0.1.93 status\n\n- Candidate: central release-gate hardening + Danish Export UI cleanup.\n- Central release workflow already contains current v0.1.92 → v0.1.89 gates plus site/event/portable regressions.\n- Canonical backlog pointer synchronized to v0.1.93 and reserves basename/naming migration for v0.2.0.\n- Release only after v0.1.93 QA and the newly hardened central release gate both pass.\n''')
print('Applied v0.1.93 candidate')
