from pathlib import Path

# Alpha.22 intentionally kept the historical CSS class name
# .h18-clean-front-menu-summary on the new <button>.  The first Alpha.23
# builder draft referred to it as *-toggle in one responsive selector only.
# Keep Alpha.22's now-working menu markup untouched and execute the Alpha.23
# transform with that class-name reference corrected at build time.
source_path = Path('.github/scripts/build_v3_alpha23.py')
source = source_path.read_text(encoding='utf-8')
source = source.replace('.h18-clean-front-menu-toggle', '.h18-clean-front-menu-summary')
source = source.replace("'h18-clean-front-menu-toggle'", "'h18-clean-front-menu-summary'")
exec(compile(source, str(source_path), 'exec'), {'__name__': '__main__'})
