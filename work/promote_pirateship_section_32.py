"""Promote the Pirateship section with the revised detection/recovery pitch."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
data = json.loads((R / 'deck.json').read_text())
slides = root.xpath('//*[@class="SlideGroup"]')[0]
at = next(i for i, s in enumerate(data) if s['title'] == 'Old slides below')
old = next(i for i, w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id') == 'id21')
assert at == 43 and old == 44
backup = R / 'revisions/before-pirateship-section-32'
backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, backup / f)

w = slides[old]
rec = data.pop(old)
slides.remove(w)
slides.insert(at, w)
data.insert(at, rec)
slide = w.xpath('.//*[@class="Slide"]')[0]
old_page = slide.xpath('./*[@class="Page"]')[0]
page = copy.deepcopy(root.xpath('//*[@id="slide-harbormaster-section"]/*[@class="Page"]')[0])
slide.replace(old_page, page)
g = page[0]
g[1].text = 'Pirateship'
g[2].set('width', '360')
# Match the HarborMaster section slide, with one extra descriptor line.
descriptor = E.Element('{'+S+'}text', {'x': '98', 'y': '378', 'font-family': 'Rubik',
                       'font-size': '32', 'font-weight': '400', 'fill': '#6B7785', 'stroke': 'none'})
descriptor.text = 'An append-only ledger that'
main = g[3]
main.set('y', '442')
main.text = 'detects and recovers'
main[0].text = ' from integrity violations'
scope = g[4]
scope.set('y', '506')
scope[0].text = 'persistent storage, compute and memory'
g.insert(3, descriptor)
g[-1].text = '32'

script = 'This brings us to Pirateship, an append-only ledger that detects and recovers from integrity violations in both persistent storage, compute and memory.'
rec.update(title='Pirateship', section='Pirateship', speakerScript=script,
           text='Pirateship An append-only ledger that detects and recovers from integrity violations in persistent storage, compute and memory.',
           notes=script+'\n\nReuses the HarborMaster section-title layout. “detects and recovers” is bold purple; “persistent storage, compute and memory” is bold blue. Promotes the original Pirateship section slide id21 before the editing divider.')

for animations in root.xpath('//*[@class="Animations" and @ooo:slide="id21"]', namespaces={'ooo': O}):
    animations.getparent().remove(animations)
meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
records['id21'] = copy.deepcopy(records['slide-harbormaster-section'])
records['id21'].set('{'+O+'}slide', 'id21')
records['id21'].set('{'+O+'}display-name', 'Pirateship')
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
items['id21'].set('{'+O+'}id-list', '')
seen = {}
number = 0
for i, (record, wrapper) in enumerate(zip(data, slides)):
    sid = wrapper.xpath('.//*[@class="Slide"]')[0].get('id')
    m = records[sid]
    m.set('id', f'ooo:meta_slide_{i}')
    meta.append(m)
    if sid in items:
        index.append(items[sid])
    record['number'] = i+1
    build = record.get('slideGroup')
    if not build or build['id'] not in seen:
        number += 1
        if build:
            seen[build['id']] = number
    logical = seen[build['id']] if build else number
    record['displayNumber'] = logical
    if build:
        build['number'] = logical
    for e in wrapper.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
data[44]['notes'] = 'Editing divider after logical Slide32 (Pirateship section title). Insert new content before this divider.'
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 92 and number == 80
assert data[43]['displayNumber'] == 32 and data[44]['title'] == 'Old slides below'
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Promoted original Pirateship section id21 to32/physical44, matching HarborMaster section13 styling. Append-only ledger descriptor; bold purple “detects and recovers”; bold blue persistent storage, compute and memory. Exact dictated script with quotation/emphasis markup removed. Sentinel33/physical45;counts92frames/80logical unchanged. Local only.\n')
print('Pirateship section32 promoted; exact script and section styling applied.')
