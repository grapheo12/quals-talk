"""Insert the paper's original detection-delay plot and dictated narration."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import re
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
XL = 'http://www.w3.org/1999/xlink'
SID = 'slide-detection-latency'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
data = json.loads((R / 'deck.json').read_text())
assert not root.xpath(f'//*[@id="{SID}"]'), 'Slide already inserted'
b = R / 'revisions/before-detection-latency-30'
b.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, b / f)

def el(parent, tag, **attrs):
    return E.SubElement(parent, '{'+S+'}'+tag,
                        {k.replace('_', '-'): str(v) for k, v in attrs.items()})

wrapper = E.Element('{'+S+'}g', {'visibility': 'hidden'})
container = el(wrapper, 'g', id='container-detection-latency')
slide = el(container, 'g', id=SID, **{'class': 'Slide', 'clip-path': 'url(#presentation_clip_path)'})
page = el(slide, 'g', **{'class': 'Page'})
g = el(page, 'g', transform='scale(26.45859375)')

def text(x, y, label, size=24, color='#1F2328', weight=400, anchor='start'):
    e = el(g, 'text', x=x, y=y, font_family='Rubik', font_size=size,
           font_weight=weight, fill=color, stroke='none', text_anchor=anchor)
    e.text = label
    return e

el(g, 'rect', x=0, y=0, width=1280, height=720, fill='white', stroke='none')
title = 'Eventual detection, scalable auditing'
text(98, 119, title, 48, weight=700)
el(g, 'rect', x=98, y=140, width=67, height=4.8, fill='#1F5F8B', stroke='none')
text(98, 180, '16 workers · key-value workload · 100% reads', 20, '#6B7785')

# Figure 6, extracted as vector paths from printed p.2135 (PDF page 10).
# Measurements, curve, axes, and typography remain exactly as published.
asset = R / 'chart-detection.svg'
shutil.copyfile(R / 'paper-reference/detection-figure6.svg', asset)
chart = E.parse(str(asset)).getroot()
chart.attrib.update({'x': '98', 'y': '226', 'width': '740',
                     'height': str(740 * 85 / 171), 'data-source': 'HarborMaster-Figure-6'})
id_map = {e.get('id'): 'detection30-'+e.get('id') for e in chart.iter() if e.get('id')}
for e in chart.iter():
    for key, value in list(e.attrib.items()):
        if key == 'id':
            e.set(key, id_map[value])
        else:
            for old, new in id_map.items():
                value = re.sub(r'(?<![\w.-])'+re.escape(old)+r'(?![\w.-])', new, value)
            e.set(key, value)
# Expand font glyph references into paths for future editable PowerPoint export.
by_id = {e.get('id'): e for e in chart.iter() if e.get('id')}
for use in list(chart.xpath('.//*[local-name()="use"]')):
    glyph = by_id[use.get('{'+XL+'}href')[1:]]
    instance = E.Element('{'+S+'}g', {'transform': f'translate({use.get("x", "0")} {use.get("y", "0")})'})
    for child in glyph:
        instance.append(copy.deepcopy(child))
    use.getparent().replace(use, instance)
g.append(chart)

el(g, 'path', d='M868 236 V564', stroke='#DDE3E8', stroke_width=1.5, fill='none')
text(906, 266, '1 auditor', 27, '#1F5F8B', 500)
text(906, 306, 'Falls behind', 24, '#6B7785')
text(906, 400, '16 auditors', 27, '#A02B93', 500)
text(906, 469, '158 ms', 60, '#A02B93', 700)
text(906, 503, 'measured detection delay', 18, '#6B7785')
text(906, 552, 'Eventual detection only', 21, '#1F2328', 500)

el(g, 'path', d='M98 620 H1182', stroke='#DDE3E8', stroke_width=1.5, fill='none')
text(98, 658, 'High user load', 22, '#1F5F8B', 500)
text(277, 658, '→ fewer auditors', 22)
text(662, 658, 'Low user load', 22, '#A02B93', 500)
text(828, 658, '→ drain the log backlog', 22)
text(98, 692, 'HarborMaster · Figure 6 and §6.2', 13, '#6B7785')
text(1182, 692, '30', 14.67, '#6B7785', anchor='end')

script = """We provide eventual detection. Let's see how long it takes for the auditor to catch a rollback attack once it happens. What I am showing here is the time it takes for 1 auditor node to catch a rollback attack with 16 nodes continuously running a Key-Value workload. With just one auditor, you can't maintain line rate, and the auditor falls behind. However, the auditor is also parallelizable. More auditors improve auditing throughput so much so that you can detect rollback attacks within a few 100 ms. You can scale up and scale down auditing nodes as the load on the system changes. Scale it down when there is high user load so all the compute goes to the application which generates a lot of read/write logs. Scale it back up when the load is low to consume all these logs. HarborMaster only supports eventual detection."""
rec = {'title': title, 'section': 'HarborMaster', 'speakerScript': script,
       'text': title+' 16 workers key-value workload 100% reads Detection delay (s) Number of Auditor Nodes 1 auditor falls behind 16 auditors 158 ms measured detection delay Eventual detection only High user load fewer auditors Low user load drain the log backlog',
       'notes': script+'\n\nSource: supplied HarborMaster paper, Figure 6 and §6.2, printed p.2135 (PDF page10), /Users/shubham_mishra/Downloads/3819518.3819539.pdf. Original vector plot extracted unchanged. Experiment:16 workers,100%reads,YCSB300k keys,maximum throughput,1–16 auditors; workers and auditors have equal VM compute capacity. Paper prose reports8 auditors=1.03s and16=158ms. First plotted point is approximately22s although the prose says25s; no exact first-point callout is added. Asynchronous auditing may accumulate a backlog; off-peak scaling is discussed in §6.2. 158ms is a measured result, not a fixed detection-time guarantee. Exact dictated speaker script preserved.'}
slides = root.xpath('//*[@class="SlideGroup"]')[0]
at = next(i for i, s in enumerate(data) if s['title'] == 'Old slides below')
assert at == 40
slides.insert(at, wrapper)
data.insert(at, rec)

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
records[SID] = copy.deepcopy(records['slide-vector-clock-pointers'])
records[SID].set('{'+O+'}slide', SID)
records[SID].set('{'+O+'}display-name', title)
for e in list(meta):
    if e.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(e)
meta.set('{'+O+'}number-of-slides', str(len(data)))
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
items[SID] = E.Element('{'+S+'}g', {'{'+O+'}slide': SID, '{'+O+'}id-list': ''})
seen = {}
number = 0
for i, (record, w) in enumerate(zip(data, slides)):
    sid = w.xpath('.//*[@class="Slide"]')[0].get('id')
    m = records[sid]
    m.set('id', f'ooo:meta_slide_{i}')
    meta.append(m)
    if sid in items:
        index.append(items[sid])
    record['number'] = i+1
    group = record.get('slideGroup')
    if not group or group['id'] not in seen:
        number += 1
        if group:
            seen[group['id']] = number
    logical = seen[group['id']] if group else number
    record['displayNumber'] = logical
    if group:
        group['number'] = logical
    for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
data[at+1]['notes'] = 'Editing divider after logical Slide30 (detection latency). Insert new content before this divider.'

ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 112 and number == 101
assert data[40]['displayNumber'] == 30 and data[41]['title'] == 'Old slides below'
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Added30/physical41: Eventual detection, scalable auditing. Exact dictated narration; original Figure6 vector plot from supplied HarborMaster paper, with16-worker/100%-read workload and158ms measured result at16auditors. Native SVG text/callouts show1auditor falls behind, eventual-only guarantee and dynamic resource allocation. Paper plot first point appears~22s vs prose25s; preserve plot and avoid exact first-point callout. Newchart asset chart-detection.svg; glyph uses expanded to paths inline. Sentinel31/physical42;112frames/101logical. Local only.\n')
print('Slide30 inserted with original Figure6 vector graph and exact narration.')
