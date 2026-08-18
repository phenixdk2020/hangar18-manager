from pathlib import Path
p=Path('assets/admin.js')
t=p.read_text()
old="else $value.attr('placeholder','Værdi');}}$r.attr('data-kind',kind);}"
new="else $value.attr('placeholder','Værdi');}$r.attr('data-kind',kind);}"
count=t.count(old)
if count != 1:
    raise SystemExit(f'Advanced Query filterRow scope anchor: expected 1, found {count}')
t=t.replace(old,new,1)
p.write_text(t)
print('v0.5.29 Advanced Query filterRow scope hardened')
