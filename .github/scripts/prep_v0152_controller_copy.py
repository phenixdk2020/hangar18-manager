from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'clean'/'hangar18-manager'/'src'/'Admin'/'ConversionController.php'
text=path.read_text(encoding='utf-8')
actual="echo '<p class=\"h18-manager-description\">Forbered Visual Designer-versioner af eksisterende WordPress-sider uden at ændre den offentlige side. Konvertering opretter først en QA-kandidat; først <strong>Godkend og aktivér</strong> gemmer kandidaten som en rigtig Visual Designer-version.</p>';"
expected="echo '<p class=\"h18-manager-description\">Forbered Visual Designer-versioner af lokale WordPress-sider eller hent en eksisterende side fra et andet offentligt HTTPS-site. Alt oprettes først som QA-kandidat; først <strong>Godkend og aktivér</strong> ændrer mål-sidens Visual Designer-model.</p>';"
if actual not in text:
    raise SystemExit('v0.1.51 conversion intro not found')
text=text.replace(actual,expected,1)
actual2="echo '<p class=\"description\">Til forsiden: brug <code>https://test2.hangar18.dk/</code> og vælg <strong>Hjem – Visual Designer</strong> som målside. Relative billeder og links gøres absolutte mod kildesitet; eksterne assets flyttes ikke til det nye mediebibliotek i denne version.</p></section>';"
expected2="echo '<p class=\"description\">Kilden læses kun. Scripts og stylesheets importeres ikke. Relative links/billeder gøres absolutte mod kildesiden, og billeder forbliver kilde-linkede i første version. Kandidaten kan forhåndsvises med den aktive Visual Designer Header/Footer.</p>';"
if actual2 not in text:
    raise SystemExit('v0.1.51 external source description not found')
text=text.replace(actual2,expected2+"\necho '</section>';",1)
path.write_text(text,encoding='utf-8')
print('Prepared v0.1.51 conversion copy for v0.1.52 patch')
