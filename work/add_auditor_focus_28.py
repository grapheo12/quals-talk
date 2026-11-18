"""One-time insertion of the transition into HarborMaster auditing."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import re
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
SID = 'slide-harbormaster-auditor-focus'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
assert not root.xpath(f'//*[@id="{SID}"]'), 'Slide 28 already exists'
data = json.loads((R / 'deck.json').read_text())
backup = R / 'revisions/before-auditor-focus-28'
backup.mkdir(exist_ok=True)
for name in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / name, backup / name)

slides = root.xpath('//*[@class="SlideGroup"]')[0]
source = root.xpath('//*[@id="id89"]')[0]
wrapper = copy.deepcopy(source.getparent().getparent())
id_map = {e.get('id'): 'audit-focus-28-' + e.get('id') for e in wrapper.iter() if e.get('id')}
id_map['id89'] = SID
for e in wrapper.iter():
    for k, value in list(e.attrib.items()):
        if k == 'id':
            e.set(k, id_map[value])
        else:
            for old, new in id_map.items():
                value = re.sub(r'(?<![\w.-])' + re.escape(old) + r'(?![\w.-])', new, value)
            e.set(k, value)

slide = wrapper.xpath('.//*[@class="Slide"]')[0]
g = slide[0][0]
children = list(g)
assert len(children) == 66
children[1].text = 'What does the auditor do?'
children[3].text = 'Inside the auditor'
children[3].set('fill', '#A02B93')
children[47].set('stroke', '#A02B93')
children[47].set('stroke-width', '3')
children[47].set('fill', '#FCF7FB')
children[49].set('stroke', '#A02B93')
for i in [43, 44, 45]:
    for key in ['fill', 'stroke']:
        if children[i].get(key) == '#1F5F8B':
            children[i].set(key, '#A02B93')

# Preserve the preceding architecture's exact coordinates; only the auditor
# and its incoming stream remain fully emphasized on this transition slide.
logs = {4, 7, *range(9, 14), *range(20, 25), *range(31, 36)}
focus = {3, 6, *range(43, 52)}
fixed = {0, 1, 2, 65}
context = set(range(len(children))) - logs - focus - fixed
for child in children:
    g.remove(child)
for i in [0, 1, 2]:
    g.append(children[i])
for indices, opacity, role in [(context, '.24', 'architecture-context'), (logs, '.55', 'audit-inputs'), (focus, '1', 'auditor-focus')]:
    group = E.SubElement(g, '{'+S+'}g', {'opacity': opacity, 'data-role': role})
    for i in sorted(indices):
        group.append(children[i])
g.append(children[65])

at = next(i for i, s in enumerate(data) if s['title'] == 'Old slides below')
assert at == 35
slides.insert(at, wrapper)
script = "Now, for the sake of time I won't go into the details of how the persistent logging system works, but let's dig a little deeper about what the Auditor actually does."
data.insert(at, {'number': at+1, 'displayNumber': 28, 'section': 'HarborMaster',
                'title': 'What does the auditor do?',
                'text': 'What does the auditor do? Inside the auditor TEE-backed auditor Stream logs Recreate worker state Check causality',
                'speakerScript': script,
                'notes': script + '\n\nReuses Slide 27 at identical coordinates, emphasizing the auditor and incoming log stream. Compute and storage are dimmed as context. Based on HarborMaster Figure 2, as cited on Slide 27.'})

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
new_meta = copy.deepcopy(records['id89'])
new_meta.set('{'+O+'}slide', SID)
new_meta.set('{'+O+'}display-name', data[at]['title'])
records[SID] = new_meta
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
meta.set('{'+O+'}number-of-slides', str(len(data)))
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
items[SID] = E.Element('{'+S+'}g', {'{'+O+'}slide': SID, '{'+O+'}id-list': ''})
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
data[at+1]['notes'] = 'Editing divider after logical Slide 28 (auditor transition). Insert new content before this divider.'

ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 110 and number == 102
assert data[35]['displayNumber'] == 28 and data[36]['title'] == 'Old slides below'
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text() + '\n- Added Slide 28, “What does the auditor do?”, reusing Slide 27 at identical coordinates. Auditor and incoming stream highlighted in purple; per-worker logs retained, compute/storage dimmed. Exact dictated narration. New slide id slide-harbormaster-auditor-focus, physical36; sentinel29/physical37. Counts110 physical/102 logical. Local only after the 7cd6940 push.\n')
print('Inserted Slide 28 with the auditor highlighted; exact narration preserved.')
