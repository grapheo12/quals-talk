"""Insert a vector-clock pointer build using the existing causal history."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
SM = 'http://www.w3.org/2001/SMIL20/'
PR = 'http://sun.com/xmlns/staroffice/presentation'
SID = 'slide-vector-clock-pointers'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
data = json.loads((R / 'deck.json').read_text())
assert not root.xpath(f'//*[@id="{SID}"]')
b = R / 'revisions/before-vector-clock-pointers-26c'
b.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, b / f)

def el(parent, tag, **attrs):
    return E.SubElement(parent, '{'+S+'}'+tag, {k.replace('_', '-'): str(v) for k, v in attrs.items()})

wrapper = E.Element('{'+S+'}g', {'visibility': 'hidden'})
container = el(wrapper, 'g', id='container-vector-clock-pointers')
slide = el(container, 'g', id=SID, **{'class': 'Slide', 'clip-path': 'url(#presentation_clip_path)'})
page = el(slide, 'g', **{'class': 'Page'})
g = el(page, 'g', transform='scale(26.45859375)')
def text(x, y, label, size=24, color='#1F2328', weight=400, anchor='start'):
    e = el(g, 'text', x=x, y=y, font_family='Rubik', font_size=size,
           font_weight=weight, fill=color, stroke='none', text_anchor=anchor)
    e.text = label
    return e

el(g, 'rect', x=0, y=0, width=1280, height=720, fill='white', stroke='none')
text(98, 119, 'Vector clocks act like pointers', 48, weight=700)
el(g, 'rect', x=98, y=140, width=67, height=4.8, fill='#1F5F8B')

# Preserve the causal-history nodes, edges and repaired Rubik labels from 26b.
source = root.xpath('//*[@id="causality-copy-7-id88"]/*[@class="Page"]')[0]
history = el(g, 'g', transform='translate(-73 65) scale(0.037795052191)')
for i in [7, 9, 10, 11, 13, 14, 15, 16, 18, 19, 20, 21]:
    c = copy.deepcopy(source[i])
    for e in c.iter():
        if e.get('id'):
            e.set('id', 'pointers26c-'+e.get('id'))
        # This build emphasizes references, rather than the rollback verdict.
        if e.get('stroke') == 'rgb(255,0,0)':
            e.set('stroke', '#1F5F8B')
        if e.get('fill') == 'rgb(255,0,0)':
            e.set('fill', '#1F5F8B')
    history.append(c)

text(270, 260, 'Read log entry', 26, '#A02B93', 500, 'middle')
el(g, 'rect', x=126, y=291, width=288, height=143, fill='white', stroke='#1F5F8B', stroke_width=2.5)
text(270, 341, 'R(X) = 1', 30, anchor='middle')
text(270, 397, '⟨3,1,1,1⟩', 35, '#A02B93', 500, 'middle')
el(g, 'path', d='M434 365 H630', fill='none', stroke='#A02B93', stroke_width=3)
el(g, 'path', d='M642 365 L628 358 L628 372 Z', fill='#A02B93', stroke='none')
text(537, 342, 'refers to', 22, '#A02B93', anchor='middle')
text(270, 476, 'Read value + vector clock', 22, '#6B7785', anchor='middle')
text(640, 622, 'Each write is logged once', 29, '#A02B93', 500, 'middle')
text(640, 663, 'Other nodes refer to it through their vector clocks', 25, '#1F2328', 400, 'middle')
text(1182, 692, '26', 14.67, '#6B7785', anchor='end')

script = "Did you see something interesting here? If we just log these vector clocks with each Read and Write, we don't need the redundant log entries which caused the log amplification in multi-log entries. The vector clocks sort of act like pointers!"
rec = {'number': 35, 'displayNumber': 26, 'section': 'HarborMaster',
       'title': 'Vector clocks act like pointers',
       'text': 'Vector clocks act like pointers Read log entry R(X)=1 ⟨3,1,1,1⟩ refers to causal history Each write is logged once Other nodes refer to it through their vector clocks',
       'speakerScript': script,
       'notes': script+'\n\nReuses the causal-history diagram and corrected typography from Slide26b. A read’s vector clock identifies its causal history, avoiding repeated logging of shared writes. HarborMaster Section4.4; each worker logs its own events.',
       'slideGroup': copy.deepcopy(data[33]['slideGroup'])}
assert data[33]['displayNumber'] == 26 and data[34]['displayNumber'] == 27
slides = root.xpath('//*[@class="SlideGroup"]')[0]
slides.insert(34, wrapper)
data.insert(34, rec)

# Repair an invalid empty animation target inherited from the PPTX conversion.
# Keep the clock magnifier's appearance, upward motion, and mismatch reveal.
a = root.xpath('//*[@id="id94-animations"]')[0]
for bad in a.xpath('.//*[local-name()="set" and not(@smil:targetElement)]', namespaces={'smil': SM}):
    par = bad.getparent()
    parent = par.getparent()
    parent.remove(par)
    if len(parent):
        parent[0].set('{'+PR+'}node-type', 'on-click')

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
records[SID] = copy.deepcopy(records['slide-harbormaster-auditor-focus'])
records[SID].set('{'+O+'}slide', SID)
records[SID].set('{'+O+'}display-name', rec['title'])
for e in list(meta):
    if e.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(e)
meta.set('{'+O+'}number-of-slides', str(len(data)))
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
items[SID] = E.Element('{'+S+'}g', {'{'+O+'}slide': SID, '{'+O+'}id-list': ''})
seen = {}
n = 0
for i, (s, w) in enumerate(zip(data, slides)):
    sid = w.xpath('.//*[@class="Slide"]')[0].get('id')
    m = records[sid]
    m.set('id', f'ooo:meta_slide_{i}')
    meta.append(m)
    if sid in items:
        index.append(items[sid])
    s['number'] = i+1
    group = s.get('slideGroup')
    if not group or group['id'] not in seen:
        n += 1
        if group:
            seen[group['id']] = n
    logical = seen[group['id']] if group else n
    s['displayNumber'] = logical
    if group:
        group['number'] = logical
    for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
assert len(data) == len(slides) == 111 and n == 101
assert [data[i]['displayNumber'] for i in range(32, 40)] == [26, 26, 26, 27, 27, 28, 29, 30]
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Added26c “Vector clocks act like pointers” to vector-clock-builds, reusing26b’s causal-history graph with a read-log entry pointing to it. Exact new narration, one-write-once takeaway. Counts111/101;27a–b physical36–37,28 physical38,29 physical39,sentinel30 physical40. Also repaired a missing animation target inherited on id94 by removing its empty entrance node; magnifier appearance/motion and mismatch reveal retained. Local only.\n')
print('Added26c and repaired the inherited read-verification animation.')
