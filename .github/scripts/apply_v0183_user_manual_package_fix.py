from pathlib import Path

path = Path('.github/workflows/visual-designer-release.yml')
text = path.read_text(encoding='utf-8')
anchor = "          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/src/Admin/GalleryAdminController.php$')\" = '1'\n"
insert = anchor + "          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/src/Admin/ManualController.php$')\" = '1'\n          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/docs/user-manual.html$')\" = '1'\n          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/docs/visual-designer-manager-brugermanual.docx$')\" = '1'\n          test \"$(unzip -Z1 \"$VERSIONED\" | grep -c '^hangar18-manager/docs/user-manual-assets/page-anatomy.svg$')\" = '1'\n"
needle = "^hangar18-manager/src/Admin/ManualController.php$"
if needle not in text:
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f'package verification anchor: expected 1 match, got {count}')
    text = text.replace(anchor, insert, 1)
    path.write_text(text, encoding='utf-8')
print('Ensured v0.1.83 manual artifacts are verified inside the release ZIP.')
