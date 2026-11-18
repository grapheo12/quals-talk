"""Add grouped summary/spectrum builds and remove the superseded tail."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import re
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
root_tree = E.parse(str(R / 'editable-deck.svg'))
root = root_tree.getroot()
data = json.loads((R / 'deck.json').read_text())
slides = root.xpath('//*[@class="SlideGroup"]')[0]
SID_A = 'slide-harbormaster-detect-rerun'
SID_B = 'slide-risk-tolerance-recovery'
assert not root.xpath(f'//*[@id="{SID_A}"]')
backup = R / 'revisions/before-detection-recovery-31-and-old-harbormaster-removal'
backup.mkdir(exist_ok=True)
for name in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / name, backup / name)

def clone(element, prefix, overrides=None):
    result = copy.deepcopy(element)
    mapping = {e.get('id'): prefix+e.get('id') for e in result.iter() if e.get('id')}
    mapping.update(overrides or {})
    for e in result.iter():
        for k, value in list(e.attrib.items()):
            if k == 'id':
                e.set(k, mapping[value])
            else:
                for old, new in mapping.items():
                    value = re.sub(r'(?<![\w.-])'+re.escape(old)+r'(?![\w.-])', new, value)
                e.set(k, value)
    return result

def el(parent, tag, **attrs):
    return E.SubElement(parent, '{'+S+'}'+tag,
                        {k.replace('_', '-'): str(v) for k, v in attrs.items()})

def text(parent, x, y, label, size=24, color='#1F2328', weight=400, anchor='start'):
    e = el(parent, 'text', x=x, y=y, font_family='Rubik', font_size=size,
           font_weight=weight, fill=color, stroke='none', text_anchor=anchor)
    e.text = label
    return e

# Reuse the earlier Cautious Trust diagram, keeping compute on the right.
source_a = root.xpath('//*[@id="slide-cautious-trust-audit"]')[0]
wrapper_a = clone(source_a.getparent().getparent(), 'summary31a-',
                  {'slide-cautious-trust-audit': SID_A})
g_a = wrapper_a.xpath('.//*[@class="Page"]')[0][0]
title_a = 'HarborMaster: Detect, then rerun'
for i, value in {
    1: title_a,
    3: '31',
    4: 'HarborMaster auditor',
    5: 'Flink analytics',
    6: 'Detects persistent-state tampering',
    7: 'Stateful stream processing',
    9: 'Persistent-state logs',
    11: 'Detection + rerun may be enough for analytics',
}.items():
    g_a[i].text = value

# Adapt the original application-risk spectrum rather than inventing new art.
wrapper_b = E.Element('{'+S+'}g', {'visibility': 'hidden'})
container = el(wrapper_b, 'g', id='container-risk-tolerance-recovery')
slide = el(container, 'g', id=SID_B, **{'class': 'Slide', 'clip-path': 'url(#presentation_clip_path)'})
page = el(slide, 'g', **{'class': 'Page'})
g_b = el(page, 'g', transform='scale(26.45859375)')
el(g_b, 'rect', x=0, y=0, width=1280, height=720, fill='white', stroke='none')
title_b = 'Applications differ in risk tolerance'
text(g_b, 98, 119, title_b, 48, weight=700)
el(g_b, 'rect', x=98, y=140, width=67, height=4.8, fill='#1F5F8B', stroke='none')
text(g_b, 224, 205, 'More risk tolerant', 23, '#6B7785')
text(g_b, 1056, 205, 'Less risk tolerant', 23, '#6B7785', anchor='end')
spectrum_source = root.xpath('//*[@id="id29"]/*[@class="Page"]')[0]
spectrum = el(g_b, 'g', transform='translate(-622.65 -125.9) scale(.05)',
              data_source='original-application-risk-spectrum')
for i in [4, 5, 6, 7]:
    part = clone(spectrum_source[i], 'spectrum31b-')
    for old_text in part.xpath('.//*[local-name()="text"]'):
        old_text.getparent().remove(old_text)
    if i == 6:
        for path in part.xpath('.//*[local-name()="path"]'):
            path.set('fill', '#A74B40')
    spectrum.append(part)
text(g_b, 389.45, 301, 'Detection + rerun', 29, '#1F5F8B', 500, 'middle')
text(g_b, 389.45, 337, 'may be acceptable', 23, '#6B7785', anchor='middle')
text(g_b, 389.45, 554, 'FLINK', 27, 'white', 700, 'middle')
text(g_b, 389.45, 588, 'ANALYTICS', 27, 'white', 700, 'middle')
text(g_b, 841.5, 317, 'BANKS', 31, 'white', 700, 'middle')
text(g_b, 871.1, 554, 'KEY', 27, 'white', 700, 'middle')
text(g_b, 871.1, 588, 'MANAGEMENT', 27, 'white', 700, 'middle')
text(g_b, 640, 666, 'Detection alone is not enough. We need recovery.', 28, '#A02B93', 500, 'middle')
text(g_b, 1182, 692, '31', 14.67, '#6B7785', anchor='end')

script_a = "To summarize, I talked about how a cautious trust mechanism can detect integrity violations in persistent storage. This is perhaps ok when the effect of eventually detecting an attack is perhaps rerunning the computation. For example, a stateful stream processing service like Flink doing some analytics work."
script_b = "But applications sit on a spectrum of risk tolerance. Some applications like banks and key management services are so security sensitive, detection will not cut it. They need recovery from such attacks."
group = {'id': 'detection-to-recovery-builds', 'number': 31, 'title': 'From detection to recovery'}
records_new = [
    {'title': title_a, 'section': 'HarborMaster', 'speakerScript': script_a,
     'text': title_a+' HarborMaster auditor Detects persistent-state tampering Flink analytics Stateful stream processing Persistent-state logs No extra checks on the computation path Detection + rerun may be enough for analytics',
     'notes': script_a+'\n\nReuses the earlier Cautious Trust audit-log-compute diagram at the same coordinates. This is an application-level detect-and-rerun scenario, not a claim that HarborMaster itself provides automatic recovery.',
     'slideGroup': copy.deepcopy(group)},
    {'title': title_b, 'section': 'HarborMaster', 'speakerScript': script_b,
     'text': title_b+' More risk tolerant Less risk tolerant Detection + rerun may be acceptable Flink analytics Banks Key management Detection alone is not enough We need recovery',
     'notes': script_b+'\n\nReuses and adapts the original green-to-red application-risk spectrum from id29: native gradient arrow and application callouts. Analytics is labeled Flink; the model-serving example is replaced with banks; key management is retained. Qualitative application spectrum, not a quantitative risk scale.',
     'slideGroup': copy.deepcopy(group)},
]

# User explicitly requested all then-current logical slides 80 onward removed.
cut = next(i for i, record in enumerate(data) if record['displayNumber'] == 80)
assert cut == 90 and data[cut]['title'] == 'HarborMaster'
removed = data[cut:]
removed_ids = {w.xpath('.//*[@class="Slide"]')[0].get('id') for w in list(slides)[cut:]}
(backup / 'removed-slides.json').write_text(json.dumps(removed, ensure_ascii=False, indent=2))
for w in list(slides)[cut:]:
    slides.remove(w)
del data[cut:]
for element in list(root.xpath('//*[@ooo:slide]', namespaces={'ooo': O})):
    if element.get('{'+O+'}slide') in removed_ids:
        element.getparent().remove(element)

at = next(i for i, record in enumerate(data) if record['title'] == 'Old slides below')
assert at == 41
for offset, (wrapper, record) in enumerate(zip([wrapper_a, wrapper_b], records_new)):
    slides.insert(at+offset, wrapper)
    data.insert(at+offset, record)

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
meta_records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
for sid, record in zip([SID_A, SID_B], records_new):
    meta_records[sid] = copy.deepcopy(meta_records['slide-cautious-trust-audit'])
    meta_records[sid].set('{'+O+'}slide', sid)
    meta_records[sid].set('{'+O+'}display-name', record['title'])
for e in list(meta):
    if e.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(e)
meta.set('{'+O+'}number-of-slides', str(len(data)))
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
for sid in [SID_A, SID_B]:
    items[sid] = E.Element('{'+S+'}g', {'{'+O+'}slide': sid, '{'+O+'}id-list': ''})
seen = {}
number = 0
for i, (record, w) in enumerate(zip(data, slides)):
    sid = w.xpath('.//*[@class="Slide"]')[0].get('id')
    m = meta_records[sid]
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
    for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
data[43]['notes'] = 'Editing divider after logical Slide31a–b (detection to recovery). Insert new content before this divider.'

ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 92 and number == 80
assert len(removed) == 22
assert data[41]['displayNumber'] == data[42]['displayNumber'] == 31
assert data[43]['title'] == 'Old slides below'
assert data[-1]['title'] == 'More interesting things'
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
ids_set = set(ids)
for target in root.xpath('//@smil:targetElement', namespaces={'smil': 'http://www.w3.org/2001/SMIL20/'}):
    assert target in ids_set, target
root_tree.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Added31a–b, group detection-to-recovery-builds:31a reuses the Cautious Trust diagram (auditor left, Flink analytics right) for persistent-state detection followed by rerunning computation;31b adapts original id29 green-to-red spectrum with Flink analytics, banks and key management and the need for recovery. Exact dictated scripts, directives excluded. Removed all22 then-current logical slides80–101 as explicitly requested (old HarborMaster section onward, id70 through id100 with gaps), including their metadata/text-index/animation references. Backup and removed-slide list in revisions/before-detection-recovery-31-and-old-harbormaster-removal. Current92frames/80logical;31a–b physical42–43,sentinel32/physical44,Pirateship33/physical45;last80 More interesting things. Local only.\n')
print('Added31a–b and removed22 superseded slides. 92frames/80logical, divider32.')
