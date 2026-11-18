"""Insert the distributed-trust setup after Pirateship, reusing original art."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import re
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
data = json.loads((R / 'deck.json').read_text())
slides = root.xpath('//*[@class="SlideGroup"]')[0]
backup = R / 'revisions/before-distributed-trust-33'
backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, backup / f)

def el(parent, tag, **attrs):
    return E.SubElement(parent, '{'+S+'}'+tag, {k.replace('_', '-'): str(v) for k, v in attrs.items()})

def text(parent, x, y, value, size=24, color='#1F2328', weight=400, anchor='start'):
    e = el(parent, 'text', x=x, y=y, font_family='Rubik', font_size=size,
           font_weight=weight, fill=color, stroke='none', text_anchor=anchor)
    e.text = value
    return e

def clone(element, prefix):
    c = copy.deepcopy(element)
    mapping = {e.get('id'): prefix+e.get('id') for e in c.iter() if e.get('id')}
    for e in c.iter():
        for k, value in list(e.attrib.items()):
            if k == 'id':
                e.set(k, mapping[value])
            else:
                for old, new in mapping.items():
                    value = re.sub(r'(?<![\w.-])'+re.escape(old)+r'(?![\w.-])', new, value)
                e.set(k, value)
    return c

source_a = root.xpath('//*[@id="id23"]')[0]
source_b = root.xpath('//*[@id="id24"]')[0]
old_page_a = source_a.xpath('./*[@class="Page"]')[0]
old_page_b = source_b.xpath('./*[@class="Page"]')[0]
red_replica = old_page_b[12]
page_a = E.Element('{'+S+'}g', {'class': 'Page'})
ga = el(page_a, 'g', transform='scale(26.45859375)')
el(ga, 'rect', x=0, y=0, width=1280, height=720, fill='white', stroke='none')
title_a = 'Distributed trust for recovery'
title_b = 'Recovery needs correct replicas'
text(ga, 98, 119, title_a, 48, weight=700)
el(ga, 'rect', x=98, y=140, width=67, height=4.8, fill='#1F5F8B', stroke='none')
text(ga, 98, 180, 'One totally ordered ledger. Each node executes it independently.', 25)
diagram_a = el(ga, 'g', transform='scale(0.037795052191)', data_source='original-distributed-trust-ledger')
for e in list(old_page_a)[2:]:
    diagram_a.append(e)
text(ga, 98, 327, 'Independent', 27, '#1F5F8B', 500)
text(ga, 98, 363, 'executions', 27, '#1F5F8B', 500)
text(ga, 98, 505, 'Totally ordered transaction ledger', 24, '#1F5F8B', 500)
text(ga, 1182, 692, '33', 14.67, '#6B7785', anchor='end')
source_a.replace(old_page_a, page_a)

# Keep exactly the same network and ledger positions in the second build.
page_b = clone(page_a, 'distributed33b-')
gb = page_b[0]
gb[1].text = title_b
gb[3].text = 'Only a minority of nodes may be compromised at a time'
gb[5].text = 'Enough correct'
gb[6].text = 'replicas remain'
gb[5].set('font-size', '24')
gb[6].set('font-size', '24')
diagram_b = gb[4]
assert diagram_b[7].get('class') == 'Graphic'
# Fit the original red malicious-replica vector to the right node's original box.
scale = 2434 / 2114
tx = 22084 + (2399 - 1493 * scale) / 2 - 30289 * scale
ty = 7761 - 9606 * scale
replacement = E.Element('{'+S+'}g', {'transform': f'translate({tx} {ty}) scale({scale})'})
replacement.append(red_replica)
diagram_b.replace(diagram_b[7], replacement)
for i in [0, 3, 5]:
    for e in diagram_b[i].iter():
        for key in ['fill', 'stroke']:
            if e.get(key) == 'rgb(31,95,139)':
                e.set(key, '#A02B93')
text(gb, 982, 305, 'Compromised', 23, '#B54740', 500)
text(gb, 982, 359, 'Recover using', 22, '#A02B93', 500)
text(gb, 982, 391, 'correct replicas', 22, '#A02B93', 500)
source_b.replace(old_page_b, page_b)

scripts = [
    'For recovery to work, we need to operate in a distributed trust model. Here multiple nodes come together to realize a totally ordered ledger of transactions and execute them individually.',
    'Distributed Trust works in the assumption that only a minority of the nodes are compromised at a time. So enough nodes must have executed transactions correctly so that they can be used to recover the state of the compromised nodes.',
]
group = {'id': 'distributed-trust-builds', 'number': 33, 'title': 'Distributed trust'}
moved = []
for sid, title, script in zip(['id23', 'id24'], [title_a, title_b], scripts):
    i = next(i for i, w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id') == sid)
    w = slides[i]
    slides.remove(w)
    rec = data.pop(i)
    rec.update(title=title, section='Pirateship', speakerScript=script,
               text=' '.join(''.join(e.itertext()) for e in w.xpath('.//*[local-name()="text"]')),
               notes=script+'\n\nPromotes the original distributed-trust slides id23/id24. Both builds reuse id23’s connected replicas and four-transaction ledger at identical coordinates; the second swaps one replica for id24’s native red malicious-node vector and highlights its recovery links. The four-node/one-compromised illustration is qualitative; the tolerated fault count depends on the protocol and assumptions, not simply a universal less-than-half threshold.',
               slideGroup=copy.deepcopy(group))
    moved.append((w, rec))
at = next(i for i, w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id') == 'id21') + 1
assert at == 44
for offset, (w, rec) in enumerate(moved):
    slides.insert(at+offset, w)
    data.insert(at+offset, rec)

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
for sid, title in zip(['id23', 'id24'], [title_a, title_b]):
    records[sid] = copy.deepcopy(records['slide-operation-risk-spectrum'])
    records[sid].set('{'+O+'}slide', sid)
    records[sid].set('{'+O+'}display-name', title)
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
for sid in ['id23', 'id24']:
    items[sid].set('{'+O+'}id-list', '')
seen = {}
number = 0
for i, (rec, w) in enumerate(zip(data, slides)):
    sid = w.xpath('.//*[@class="Slide"]')[0].get('id')
    m = records[sid]
    m.set('id', f'ooo:meta_slide_{i}')
    meta.append(m)
    if sid in items:
        index.append(items[sid])
    rec['number'] = i+1
    build = rec.get('slideGroup')
    if not build or build['id'] not in seen:
        number += 1
        if build:
            seen[build['id']] = number
    logical = seen[build['id']] if build else number
    rec['displayNumber'] = logical
    if build:
        build['number'] = logical
    for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
divider = next(s for s in data if s['title'] == 'Old slides below')
divider['notes'] = 'Editing divider after logical Slide34a–c (PBFT tradeoffs and correlated compromise). Insert new content before this divider.'
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 94 and number == 79
assert [data[i]['displayNumber'] for i in [44, 45]] == [33, 33]
assert [data[i]['displayNumber'] for i in [46, 47, 48]] == [34, 34, 34]
assert data[49]['title'] == 'Old slides below' and data[49]['displayNumber'] == 35
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
for target in root.xpath('//@smil:targetElement', namespaces={'smil': 'http://www.w3.org/2001/SMIL20/'}):
    assert target in set(ids), target
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Inserted requested two-build group immediately after32 by promoting original id23/id24: new33a–b distributed-trust-builds. Reused id23’s full transaction ledger and four-node network, matching coordinates across builds;33b uses id24’s native malicious-replica vector and purple recovery links. Exact scripts. Prior33a–c now34a–c;sentinel35/physical50. Original old copies ofid23/id24 moved, not duplicated.94frames/79logical. Local only.\n')
print('Added distributed trust33a–b after32; prior33 becomes34;94frames/79logical.')
