"""Group architecture builds and promote the original auditing examples."""
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
assert data[34]['displayNumber'] == 27 and data[35]['displayNumber'] == 28
assert data[36]['title'] == 'Old slides below'
b = R / 'revisions/before-auditor-checks-28-29'
b.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, b / f)
animations_before = {sid: E.tostring(root.xpath(f'//*[@id="{sid}-animations"]')[0]) for sid in ['id93', 'id94']}

for i in [34, 35]:
    data[i]['slideGroup'] = {'id': 'harbormaster-architecture-builds', 'number': 27,
                             'title': 'HarborMaster: architecture and auditor'}

scripts = [
    "The first thing it checks for each worker is if the log entries have monotonically increasing vector clocks. Remember: each node's vector clock is part of its disk state and can be rolled back independently.",
    "Then, for a given read log entry, it looks at the vector clock, which gives the causal history of all writes seen by that node while making that read. It then figures out what the state of the node should have been when the read was made. And then if it doesn't match, then it is a causality violation, likely to be caused by rollback attacks.",
]
titles = ['Check 1: Monotonic vector clocks', 'Check 2: Reconstruct and verify reads']

def text(parent, x, y, label, size=24, color='#1F2328', weight=400, anchor='start'):
    el = E.SubElement(parent, '{'+S+'}text', {'x': str(x), 'y': str(y),
         'font-family': 'Rubik', 'font-size': str(size), 'font-weight': str(weight),
         'fill': color, 'stroke': 'none', 'text-anchor': anchor})
    el.text = label
    return el

for n, sid in enumerate(['id93', 'id94']):
    old = next(i for i, w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id') == sid)
    at = next(i for i, s in enumerate(data) if s['title'] == 'Old slides below')
    assert old > at
    w = slides[old]
    rec = data.pop(old)
    slides.remove(w)
    slides.insert(at, w)
    data.insert(at, rec)
    page = w.xpath('.//*[@class="Page"]')[0]
    title = page.xpath('./*[@class="TitleText"]//*[local-name()="tspan" and @font-family]')[0]
    title.text = titles[n]
    title.attrib.pop('textLength', None)
    title.attrib.pop('lengthAdjust', None)

    # Keep the original causal-log diagrams, detective, thought bubbles, and
    # animation targets. Replace the old generic bullets with the dictated check.
    g = E.SubElement(page, '{'+S+'}g', {'transform': 'scale(26.45859375)', 'id': f'auditor-check-{28+n}-labels'})
    if n == 0:
        for outline in page.xpath('./*[@class="Outline"]'):
            outline.set('display', 'none')
        text(g, 650, 497, 'Check each worker independently', 25, '#A02B93', 500)
        text(g, 650, 538, 'No clock component may decrease', 23)
        example = text(g, 650, 583, '⟨1,1,0⟩ → ', 29, '#1F5F8B', 500)
        E.SubElement(example, '{'+S+'}tspan', {'fill': '#B54740'}).text = '⟨0,2,0⟩'
        text(g, 650, 630, 'The vector clock is disk state.', 22, '#6B7785')
        text(g, 650, 659, 'It can be rolled back independently.', 22, '#6B7785')
        note = 'Reuses original slide id93 and its monotonic-clock thought-bubble reveal. The first component falls from 1 to 0 even though the worker’s own component increases. Componentwise nondecreasing clocks implement the monotonicity check.'
    else:
        text(g, 98, 184, 'Use the read clock to reconstruct the expected state', 23, '#1F5F8B')
        text(g, 98, 671, 'Mismatch ⇒ causality violation', 25, '#B54740', 500)
        note = 'Reuses original slide id94, causal-write example and both clock-inspection animation steps. The original example reconstructs X=3 for the read clock while the log reports X=1. Background: HarborMaster Section 4.4, state recreation and Invariant 3; the application’s convergence semantics determine how concurrent writes are combined.'
    rec.update(title=titles[n], section='HarborMaster', speakerScript=scripts[n],
               notes=scripts[n]+'\n\n'+note)
    rec['text'] = ' '.join(''.join(e.itertext()) for e in page.xpath('.//*[local-name()="text"]'))

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
seen = {}
number = 0
for i, (rec, w) in enumerate(zip(data, slides)):
    sid = w.xpath('.//*[@class="Slide"]')[0].get('id')
    m = records[sid]
    m.set('id', f'ooo:meta_slide_{i}')
    if sid in ['id93', 'id94']:
        m.set('{'+O+'}display-name', rec['title'])
    meta.append(m)
    if sid in items:
        index.append(items[sid])
    rec['number'] = i+1
    group = rec.get('slideGroup')
    if not group or group['id'] not in seen:
        number += 1
        if group:
            seen[group['id']] = number
    logical = seen[group['id']] if group else number
    rec['displayNumber'] = logical
    if group:
        group['number'] = logical
    for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
data[38]['notes'] = 'Editing divider after logical Slide 29 (auditor checks). Insert new content before this divider.'

assert data[34]['displayNumber'] == data[35]['displayNumber'] == 27
assert data[36]['displayNumber'] == 28 and data[37]['displayNumber'] == 29
assert data[38]['title'] == 'Old slides below' and data[38]['displayNumber'] == 30
assert len(slides) == len(data) == 110 and number == 101
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
for sid, old in animations_before.items():
    assert E.tostring(root.xpath(f'//*[@id="{sid}-animations"]')[0]) == old
for e in root.xpath('//*[@*[local-name()="targetElement"]]'):
    for key, val in e.attrib.items():
        if key.endswith('targetElement'):
            assert val in ids, val
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text() + '\n- Grouped architecture/auditor focus as 27a–b (stable group harbormaster-architecture-builds). Promoted original id93/id94 into new logical28/29 (physical37/38), retaining their original animations and diagrams. New titles/check annotations and exact dictated narration: per-worker vector-clock monotonicity, then reconstructing and verifying read state. Sentinel30/physical39. Counts110 physical/101 logical. Local only.\n')
print('Grouped 27a–b and promoted original auditor examples to Slides 28 and 29.')
