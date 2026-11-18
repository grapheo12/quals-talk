"""Reuse the original correlated-compromise network as the third PBFT build."""
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
old = next(i for i, w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id') == 'id30')
assert at == 46 and old > at
backup = R / 'revisions/before-correlated-compromise-33c'
backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, backup / f)

w = slides[old]
record = data.pop(old)
slides.remove(w)
slides.insert(at, w)
data.insert(at, record)
slide = w.xpath('.//*[@class="Slide"]')[0]
old_page = slide.xpath('./*[@class="Page"]')[0]
old_parts = list(old_page)
page = E.Element('{'+S+'}g', {'class': 'Page'})
g = E.SubElement(page, '{'+S+'}g', {'transform': 'scale(26.45859375)'})

def el(tag, **attrs):
    return E.SubElement(g, '{'+S+'}'+tag, {k.replace('_', '-'): str(v) for k, v in attrs.items()})

def text(x, y, label, size=24, color='#1F2328', weight=400, anchor='start'):
    e = el('text', x=x, y=y, font_family='Rubik', font_size=size,
           font_weight=weight, fill=color, stroke='none', text_anchor=anchor)
    e.text = label
    return e

title = 'TEE compromises are correlated'
el('rect', x=0, y=0, width=1280, height=720, fill='white', stroke='none')
text(98, 119, title, 48, weight=700)
el('rect', x=98, y=140, width=67, height=4.8, fill='#1F5F8B', stroke='none')
text(98, 284, 'One vendor across all replicas', 29, '#1F5F8B', 500)
text(98, 335, 'One shared vulnerability', 28, '#6B7785')
el('path', d='M306 363 V410 M299 402 L306 411 L313 402', fill='none',
   stroke='#A02B93', stroke_width=2.5, stroke_linecap='round', stroke_linejoin='round')
text(98, 461, 'Correlated compromises', 32, '#A02B93', 500)
text(916, 209, 'Every node: AMD SEV-SNP', 26, '#1F5F8B', 500, 'middle')

# Reuse the original network, native malicious-replica vectors and attack marks.
# Omit bitmap/outline duplicates from the old Office conversion.
network = el('g', transform='translate(96.088 62.958) scale(.031)',
             data_source='original-correlated-compromise-network')
for i in [*range(4, 10), *range(22, 30)]:
    network.append(old_parts[i])
text(640, 623, 'If every replica is compromised…', 24, '#6B7785', anchor='middle')
text(640, 666, 'Neither detection nor recovery is guaranteed', 29, '#A02B93', 500, 'middle')
text(1182, 692, '33', 14.67, '#6B7785', anchor='end')
slide.replace(old_page, page)

script = "There's another issue. Current BFT protocols that use TEEs will use the same vendor, say AMD SEV-SNP, for all nodes. TEE vulnerabilities may be rare, but when they are found, they make all TEEs from the same vendor vulnerable! If actually everything is compromised together, current BFT deployments can not guarantee either detection or recovery."
record.update(title=title, section='Pirateship', speakerScript=script,
              text='TEE compromises are correlated One vendor across all replicas One shared vulnerability Correlated compromises Every node AMD SEV-SNP If every replica is compromised Neither detection nor recovery is guaranteed',
              notes=script+'\n\nReuses original slide id30’s four connected malicious-replica vectors and attack marks, omitting overlapping bitmap/outline duplicates. The diagram shows a homogeneous deployment using the same affected TEE. A vulnerability’s reach depends on affected implementations, versions, patch status and exploitation conditions; discovery does not itself establish successful exploitation. The loss of guarantees is explicitly conditional on every replica being compromised, beyond the protocol’s fault bound. Exact dictated narration preserved.',
              slideGroup=copy.deepcopy(data[at-1]['slideGroup']))
assert record['slideGroup']['id'] == 'pbft-tradeoff-builds'

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
records['id30'] = copy.deepcopy(records['slide-operation-risk-spectrum'])
records['id30'].set('{'+O+'}slide', 'id30')
records['id30'].set('{'+O+'}display-name', title)
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
items['id30'].set('{'+O+'}id-list', '')
seen = {}
number = 0
for i, (rec, wrapper) in enumerate(zip(data, slides)):
    sid = wrapper.xpath('.//*[@class="Slide"]')[0].get('id')
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
    for e in wrapper.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
data[47]['notes'] = 'Editing divider after logical Slide33a–c (PBFT tradeoffs and correlated compromise). Insert new content before this divider.'
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 94 and number == 80
assert [data[i]['displayNumber'] for i in [44, 45, 46]] == [33, 33, 33]
assert data[47]['title'] == 'Old slides below'
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
for target in root.xpath('//@smil:targetElement', namespaces={'smil': 'http://www.w3.org/2001/SMIL20/'}):
    assert target in set(ids), target
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Added new33c by promoting original id30 correlated-compromise slide into pbft-tradeoff-builds. Reuses native four-replica network and red compromise artwork, omits bitmap/outline duplicates, adds same-AMD-SEV-SNP label and conditional loss of both detection/recovery guarantees. Exact new script. Earlier removed cost33c stays removed; its narration remains in33b.94frames/80logical;33a–c physical45–47,sentinel34/physical48. Local only.\n')
print('Promoted correlated-compromise diagram to new33c;94frames/80logical.')
