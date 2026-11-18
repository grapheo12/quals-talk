"""Revise only Slide 27: right-to-left flow and separate per-worker logs."""
from pathlib import Path
from lxml import etree as E
import copy
import json
import shutil

R = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
t = E.parse(str(R / 'editable-deck.svg'))
root = t.getroot()
data = json.loads((R / 'deck.json').read_text())
backup = R / 'revisions' / 'before-architecture-27-layout-fix'
backup.mkdir(exist_ok=True)
for name in ['editable-deck.svg', 'deck.json']:
    if not (backup / name).exists():
        shutil.copyfile(R / name, backup / name)

original = E.parse(str(R / 'revisions/before-harbormaster-architecture-27/editable-deck.svg'))
source = original.xpath('//*[@id="id89"]/*[@class="Page"]')[0]
gear, auditor = source[4], source[6]
db = source[2].xpath('.//*[local-name()="desc" and contains(text(),"Database")]')[0].getparent()
page = root.xpath('//*[@id="id89"]/*[@class="Page"]')[0]
page.clear()
page.set('class', 'Page')

def el(parent, tag, **attrs):
    return E.SubElement(parent, '{' + S + '}' + tag,
                        {k.replace('_', '-'): str(v) for k, v in attrs.items()})

g = el(page, 'g', transform='scale(26.45859375)')
blue, ink, gray, purple, green = '#1F5F8B', '#1F2328', '#6B7785', '#A02B93', '#44B649'

def txt(x, y, text, size=24, color=ink, weight=400, anchor='middle'):
    e = el(g, 'text', x=x, y=y, font_family='Rubik', font_size=size,
           font_weight=weight, text_anchor=anchor, fill=color, stroke='none')
    e.text = text
    return e

serial = 0
def icon(node, bounds, x, y, w, h):
    # Office's nominal icon boxes contain unequal blank padding. Fit the visible
    # artwork instead, keeping the original paths and their proportions.
    global serial
    serial += 1
    bx, by, bw, bh = bounds
    scale = min(w / bw, h / bh)
    wrap = el(g, 'g', transform=f'translate({x+(w-bw*scale)/2} {y+(h-bh*scale)/2}) scale({scale}) translate({-bx} {-by})')
    c = copy.deepcopy(node)
    for e in c.iter():
        if e.get('id'):
            e.set('id', f'hm27r-{serial}-' + e.get('id'))
    wrap.append(c)

def lock(x, y, size=22):
    # One consistent closed padlock, placed entirely within each TEE boundary.
    p = el(g, 'g', transform=f'translate({x} {y}) scale({size/24})',
           fill='none', stroke=blue, stroke_width=2, stroke_linecap='round',
           stroke_linejoin='round', **{'data-role': 'tee-lock'})
    el(p, 'path', d='M6 10 V6 A6 6 0 0 1 18 6 V10')
    el(p, 'rect', x=3, y=10, width=18, height=13, rx=1.5, fill='white')
    el(p, 'path', d='M12 15 V19')

def left_arrow(x1, y, x2):
    el(g, 'path', d=f'M{x1} {y} H{x2+10}', fill='none', stroke=blue, stroke_width=2.5)
    el(g, 'path', d=f'M{x2} {y} L{x2+11} {y-5.5} L{x2+11} {y+5.5} Z', fill=blue, stroke='none')

el(g, 'rect', x=0, y=0, width=1280, height=720, fill='white', stroke='none')
txt(98, 119, 'Cautious Trust in HarborMaster', 48, weight=700, anchor='start')
el(g, 'rect', x=98, y=140, width=67, height=4.8, fill=blue)

# Same convention as the earlier Cautious Trust diagrams: auditor left,
# computation right, logs between them. Each worker has its own causal log.
txt(238, 227, 'Asynchronous auditing', 26, weight=500)
txt(659, 227, 'Causal audit logs', 26, weight=500)
txt(1067, 227, 'Parallel computation', 26, weight=500)
txt(238, 264, 'TEE-backed auditor', 21, gray)
txt(659, 264, 'Vector clocks', 21, blue)
txt(1067, 264, 'TEE worker nodes', 21, gray)

# Three-component clocks correspond to the three workers. Example histories
# progress left-to-right within each separate log; arrows indicate data flow.
clocks = [
    ['⟨1,0,0⟩', '⟨2,0,0⟩', '⟨3,1,0⟩'],
    ['⟨0,1,0⟩', '⟨2,2,0⟩', '⟨2,3,1⟩'],
    ['⟨0,0,1⟩', '⟨0,1,2⟩', '⟨2,3,3⟩'],
]
for i, labels in enumerate(clocks):
    y = 307 + 80 * i
    txt(524, y-9, f'Log {i+1}', 17, gray, anchor='start')
    row = el(g, 'g', **{'data-role': 'causal-log', 'data-worker': i+1})
    for j, label in enumerate(labels):
        x = 524 + 90 * j
        el(row, 'rect', x=x, y=y, width=90, height=44, fill=green, stroke=ink, stroke_width=1.3)
        txt(x+45, y+29, label, 19, weight=500)
    left_arrow(974, y+22, 809)
    el(g, 'rect', x=991, y=y-12, width=154, height=68, fill='white', stroke=blue, stroke_width=2)
    icon(gear, (22051, 8597, 1707, 2065), 1004, y-1, 38, 46)
    txt(1087, y+18, f'Node {i+1}', 22, weight=500)
    lock(1116, y+25, 22)

txt(892, 298, 'Emit entries', 18, gray)
# Branches join at the consuming auditor, without suggesting a single log.
el(g, 'path', d='M510 329 H474 V489 H510 M474 409 H510',
   stroke=blue, stroke_width=2.5, fill='none')
left_arrow(474, 409, 315)
txt(394, 383, 'Stream logs', 19)
el(g, 'rect', x=177, y=343, width=122, height=132, fill='white', stroke=blue, stroke_width=2)
icon(auditor, (9919, 8564, 1675, 2114), 193, 353, 83, 105)
lock(269, 445, 22)
txt(238, 517, 'Recreate worker state', 21)
txt(238, 551, 'Check causality', 25, purple, 500)
txt(1067, 551, 'Run at its own pace', 22, blue, 500)

# All per-worker logs share the replicated storage service. Fit each cylinder
# to its actual visible bounds; keep each lock in its lower front compartment.
txt(659, 538, 'All logs replicated', 18, gray)
for x in [550, 632, 714]:
    icon(db, (12754, 12972, 2160, 2585), x, 552, 54, 65)
    el(g, 'rect', x=x+16, y=590, width=24, height=25, fill='white', stroke='none')
    lock(x+17, 590, 22)
txt(659, 648, 'Fault-tolerant storage', 24, weight=500)
txt(659, 676, '2f + 1 TEE storage servers', 19, gray)
txt(1182, 692, '27', 14.67, gray, anchor='end')

rec = data[34]
assert rec['displayNumber'] == 27 and rec['title'] == 'Cautious Trust in HarborMaster'
rec['text'] = ' '.join(page.itertext())
rec['notes'] = rec['speakerScript'] + '\n\nVisual source: HarborMaster paper, Figure 2 and Section 3.1, p.4 (printed 2129), /Users/shubham_mishra/Downloads/3819518.3819539.pdf. Same left-auditor/right-compute convention as the earlier Cautious Trust diagrams. Three separate per-worker causal logs, stored on the shared replicated TEE storage service. Three-component clocks are illustrative histories for the three displayed workers. Original gear, auditor and database paths reused with corrected visible bounds. Consistent native padlocks placed within component boundaries.'
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(page.xpath('.//*[@data-role="causal-log"]')) == 3
assert len(page.xpath('.//*[@data-role="tee-lock"]')) == 7
assert '…' not in ''.join(page.itertext())
assert len(data) == 109
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
print('Updated Slide 27: compute right, three logs, complete clocks, aligned icons and locks.')
