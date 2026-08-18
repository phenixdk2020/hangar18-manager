from pathlib import Path
p=Path('.github/scripts/patch_v0526.py')
t=p.read_text()
start=t.index('# JS editor behavior + canvas preview')
a=t.index('js=once(js,', start)
b=t.index("query_js=r'''", a)
old_line="            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', container: 'Container', flex: 'Flex container', grid: 'Grid container', component: 'Linked component', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',\n"
new_line="            icon: 'Ikon / SVG', divider: 'Skillelinje', list: 'Liste', badge: 'Badge / mærkat', quote: 'Citat', tabs: 'Faner / tabs', accordion: 'Accordion', carousel: 'Carousel / slider', container: 'Container', flex: 'Flex container', grid: 'Grid container', query_list: 'Repeater / Query list', component: 'Linked component', embed: 'Embed / medie-URL', shortcode: 'Shortcode (avanceret)',\n"
block="js=once(js,\n\"\"\""+old_line+"\"\"\",\n\"\"\""+new_line+"\"\"\",'JS query list type label')\n\n"
t=t[:a]+block+t[b:]
p.write_text(t)
print('v0.5.26 JS anchor prepared')
