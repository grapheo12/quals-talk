"""Promote the existing logging-overhead evaluation and complete its script."""
from pathlib import Path
from lxml import etree as E
import json
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
O = 'http://xml.openoffice.org/svg/export'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
data = json.loads((R / 'deck.json').read_text())
slides = root.xpath('//*[@class="SlideGroup"]')[0]
backup = R / 'revisions/before-logging-evaluation-29'
backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, backup / f)
old = next(i for i, w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id') == 'id96')
at = next(i for i, s in enumerate(data) if s['title'] == 'Old slides below')
assert old > at and at == 39
w = slides[old]
rec = data.pop(old)
slides.remove(w)
slides.insert(at, w)
data.insert(at, rec)
page = w.xpath('.//*[@class="Page"]')[0]
plot_before = E.tostring(page.xpath('.//*[@data-repair="plot"]')[0])
title = page.xpath('./*[@class="TitleText"]//*[local-name()="text"]')[0]
title.clear()
title.attrib.update({'x': '2582', 'y': '3153', 'font-family': 'Rubik',
                     'font-size': '1270', 'font-weight': '700', 'fill': '#1F2328', 'stroke': 'none'})
title.text = 'Causal logging: 8% throughput overhead'
g = E.SubElement(page, '{'+S+'}g', {'transform': 'scale(26.45859375)', 'id': 'evaluation29-workload'})
subtitle = E.SubElement(g, '{'+S+'}text', {'x': '98', 'y': '180', 'font-family': 'Rubik',
                           'font-size': '20', 'fill': '#6B7785', 'stroke': 'none'})
subtitle.text = '16 workers · 3 storage servers · 100% writes · batch size 16'
script = """So how much impact does causal logging have?

We evaluated a causally consistent key-value store with 16 worker nodes, using a workload that is entirely writes. This plot shows latency against throughput as we increase the number of clients.

The unprotected baseline, without rollback detection, reaches 144 thousand requests per second. HarborMaster reaches 132 thousand: about an 8% reduction in peak throughput.

Now compare the alternatives. Nimble puts all workers' log entries into a single total order. That coordination limits it to 13 thousand requests per second. Multilog avoids that ordering, but logs the same shared writes at every node. With 16 workers, that creates 16-fold write amplification, and it saturates at just 9 thousand requests per second.

Causal logging avoids both bottlenecks. We don't force stronger consistency than the application needs, and we don't repeatedly log the same shared writes. In this write-heavy workload, that lets us add rollback detection while keeping throughput close to the unprotected application."""
rec.update(title=title.text, section='HarborMaster', speakerScript=script,
           text='Causal logging: 8% throughput overhead 16 workers 3 storage servers 100% writes batch size16 Latency Throughput Nimble HarborMaster Multilog Unprotected',
           notes=script+'\n\nSource: HarborMaster paper, Figure5 and Section6.1 (printed pp.2134–2135), /Users/shubham_mishra/Downloads/3819518.3819539.pdf. YCSB,300k keys,1000B values,100%writes;16 workers,3storage/endorser nodes,batch16,1–1024clients. Peak throughput:Unprotected144k/s,HarborMaster132k/s,Nimble13k/s,Multilog9k/s. (144−132)/144=8.33%,reported as8% in the paper. All worker/storage/auditor nodes use confidential VMs. Original recovered plot is unchanged.')

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
records['id96'].set('{'+O+'}display-name', rec['title'])
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
seen = {}
number = 0
for i, (s, wrapper) in enumerate(zip(data, slides)):
    sid = wrapper.xpath('.//*[@class="Slide"]')[0].get('id')
    m = records[sid]
    m.set('id', f'ooo:meta_slide_{i}')
    meta.append(m)
    if sid in items:
        index.append(items[sid])
    s['number'] = i+1
    group = s.get('slideGroup')
    if not group or group['id'] not in seen:
        number += 1
        if group:
            seen[group['id']] = number
    logical = seen[group['id']] if group else number
    s['displayNumber'] = logical
    if group:
        group['number'] = logical
    for e in wrapper.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):
        e.text = str(logical)
data[40]['notes'] = 'Editing divider after logical Slide29 (causal logging evaluation). Insert new content before this divider.'
assert data[39]['displayNumber'] == 29 and data[40]['title'] == 'Old slides below'
assert len(slides) == len(data) == 111 and number == 100
assert E.tostring(page.xpath('.//*[@data-repair="plot"]')[0]) == plot_before
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Promoted original id96 logging evaluation to29/physical40. Original recovered vector plot unchanged; title clarifies8% throughput overhead; workload subtitle added. Completed requested script with verified Figure5/§6.1 results144k/s vs132k/s, Nimble13k/s,Multilog9k/s and16x amplification. Sentinel30/physical41,counts111/100unchanged. Local only.\n')
print('Slide29: reused evaluation plot and completed the spoken script with verified results.')
