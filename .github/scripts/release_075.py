from pathlib import Path

php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')
php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

for old,new,label in [
    (' * Version: 0.7.4',' * Version: 0.7.5','plugin header'),
    ("const VERSION = '0.7.4';","const VERSION = '0.7.5';",'runtime constant'),
]:
    if php.count(old) != 1:
        raise SystemExit(f'{label} anchor count: {php.count(old)}')
    php = php.replace(old,new,1)

if readme.count('Version: 0.7.4') != 1:
    raise SystemExit('readme version anchor mismatch')
readme = readme.replace('Version: 0.7.4','Version: 0.7.5',1)

entry = '''\n\n== Version 0.7.5 – I2 Visual Header/Footer Builder ==\n\nNyt:\n- Ultimate Designer har nu en visuel Header/Footer Builder i shadow mode.\n- Header/Footer templates bruger samme Sections-tree og property-navne som sideeditoren.\n- Opret, vælg, rediger, slet, tilføj/fjern elementer samt drag/drop og ↑/↓ rækkefølge.\n- Parent Key understøtter nested Container/Flex/Grid-struktur med live admin-preview.\n- Typografi/design gemmes server-side: body/heading fonts, body/H1/H2/H3 størrelser, alignment, padding samt global/custom farver.\n- Dedikeret Ultimate Designer admin-JS/CSS indlæses kun på den nye adminside og cache-bustes med version/filemtime.\n- Security QA skelner HTTP-controllerlaget fra service/domain-laget og kræver capability, nonce og sanitization ved mutationer.\n- Ingen global/public Header/Footer assignment aktiveres; eksisterende frontend og Vehicle/Event/Gallery forbliver legacy.\n'''
anchor = '\n\n== Version 0.7.4'
pos = readme.find(anchor)
if pos < 0:
    raise SystemExit('changelog anchor missing')
readme = readme[:pos] + entry + readme[pos:]

php_path.write_text(php, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
