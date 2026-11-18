"""Build the PBFT motivation from the existing timeline, spectrum and cost plot."""
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
SIDS = ['slide-pbft-rare-compromises', 'slide-operation-risk-spectrum', 'slide-pbft-operation-cost']
assert not root.xpath(f'//*[@id="{SIDS[0]}"]')
backup = R / 'revisions/before-pbft-tradeoff-33'
backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg', 'deck.json']:
    shutil.copyfile(R / f, backup / f)

def clone_slide(source_id, sid, prefix):
    source = root.xpath(f'//*[@id="{source_id}"]')[0]
    w = copy.deepcopy(source.getparent().getparent())
    mapping = {e.get('id'): prefix+e.get('id') for e in w.iter() if e.get('id')}
    mapping[source_id] = sid
    for e in w.iter():
        for k, value in list(e.attrib.items()):
            if k == 'id':
                e.set(k, mapping[value])
            else:
                for old, new in mapping.items():
                    value = re.sub(r'(?<![\w.-])'+re.escape(old)+r'(?![\w.-])', new, value)
                e.set(k, value)
    return w, w.xpath('.//*[@class="Page"]')[0][0]

wa, ga = clone_slide('slide-tee-vulnerability-timeline', SIDS[0], 'pbft33a-')
title_a = 'Isn’t PBFT sufficient?'
ga[1].text = title_a
ga[3].text = 'Remember the vulnerability windows of TEEs.'
ga[36].text = 'Design premise: actual TEE compromises are rare'
ga[36].set('font-size', '28')

wb, gb = clone_slide('slide-risk-tolerance-recovery', SIDS[1], 'pbft33b-')
title_b = 'Not every operation has the same risk'
gb[1].text = title_b
gb[6].text = 'Detection + replay'
gb[8].text = '$10 COFFEE'
gb[9].text = 'THOUSANDS IN ACCOUNT'
gb[9].set('font-size', '18')
gb[10].text = '$1M TRANSFER'
gb[10].set('font-size', '24')
gb[11].text = 'DELETE'
gb[12].text = 'ACCOUNT'
gb[13].text = 'Even within a bank, operations differ in risk'

wc, gc = clone_slide('slide-security-cost', SIDS[2], 'pbft33c-')
title_c = 'Does every operation need full BFT?'
gc[1].text = title_c
gc[23].text = 'BFT on every operation'
gc[24].text = 'Replicated ledger safety'
# Retain the earlier qualitative cost/security comparison, emphasizing BFT.
# Reposition the existing chart as a whole to leave room for the replay premise.
children = list(gc)
plot = E.Element('{'+S+'}g', {'transform': 'translate(64 5) scale(.9)',
                             'data-source': 'earlier-security-cost-plot'})
for i in range(3, 49):
    if 13 <= i <= 20:
        children[i].set('opacity', '.28')
    gc.remove(children[i])
    plot.append(children[i])
gc.insert(3, plot)
takeaway = E.SubElement(gc, '{'+S+'}text', {'x': '640', 'y': '653',
                        'font-family': 'Rubik', 'font-size': '26', 'font-weight': '500',
                        'text-anchor': 'middle', 'fill': '#A02B93', 'stroke': 'none'})
takeaway.text = 'For replayable transactions: correct the ledger, then re-execute'

scripts = [
    '''So you might think, "Wait another ledger? Isn't Byzantine fault tolerant ledgers like PBFT sufficient for such goals." Well you are partially right. There are two things, remember the timeline of TEE vulnerabilities? At any given time, the risk that a TEE is actually compromised is quite low.''',
    '''We see that even within applications that need recovery, not all operations are equally security sensitive. For example, in a bank, buying a $10 coffee when your account has thousands of dollars is perhaps less security sensitive than transferring millions of dollars, or deleting your account.''',
    '''BFT doesn't allow any tampering of the ledger, but it is also very expensive. For less security critical operation, where performance is paramount, and where I am ok to just re-execute a transaction once a ledger tampering is corrected, you might not want to pay this extra cost''',
]
timeline_record = next(s for s in data if s['displayNumber'] == 9)
notes_extra = [
    'Reuses the original vulnerability timeline, all dates, interval lengths and citations. Rarity is presented explicitly as a design premise; the timeline is not a measurement of compromise probability.\n\nOriginal timeline references:\n'+timeline_record['notes'],
    'Reuses Slide31b’s original application-risk spectrum and native callouts, adapted to operations within one bank: a $10 coffee against an account containing thousands, a large transfer, and account deletion. Risk tolerance is qualitative and application-dependent. The dictated millions-of-dollars example is abbreviated visually as a $1M transfer.',
    'Reuses the original qualitative cost/security plot. Secure boot and dm-verity are dimmed; BFT, replicated compute icons and axes are retained. Replay is an explicitly acceptable application behavior in the dictated scenario, not a guarantee that arbitrary side effects can be undone. BFT ledger safety assumes the protocol’s fault bound and other system assumptions.',
]
group = {'id': 'pbft-tradeoff-builds', 'number': 33, 'title': 'Why another ledger?'}
wrappers = [wa, wb, wc]
new_records = []
for title, script, notes, g in zip([title_a, title_b, title_c], scripts, notes_extra, [ga, gb, gc]):
    words = ' '.join(''.join(e.itertext()) for e in g.xpath('.//*[local-name()="text"]'))
    new_records.append({'title': title, 'section': 'Pirateship', 'speakerScript': script,
                        'text': words, 'notes': script+'\n\n'+notes, 'slideGroup': copy.deepcopy(group)})
at = next(i for i, s in enumerate(data) if s['title'] == 'Old slides below')
assert at == 44
for offset, (w, rec) in enumerate(zip(wrappers, new_records)):
    slides.insert(at+offset, w)
    data.insert(at+offset, rec)

meta = root.xpath('//*[@id="ooo:meta_slides"]')[0]
records = {e.get('{'+O+'}slide'): e for e in meta if e.get('id', '').startswith('ooo:meta_slide_')}
for sid, rec in zip(SIDS, new_records):
    records[sid] = copy.deepcopy(records['slide-risk-tolerance-recovery'])
    records[sid].set('{'+O+'}slide', sid)
    records[sid].set('{'+O+'}display-name', rec['title'])
for m in list(meta):
    if m.get('id', '').startswith('ooo:meta_slide_'):
        meta.remove(m)
meta.set('{'+O+'}number-of-slides', str(len(data)))
index = root.xpath('//*[@class="TextShapeIndex"]')[0]
items = {e.get('{'+O+'}slide'): e for e in index}
for sid in SIDS:
    items[sid] = E.Element('{'+S+'}g', {'{'+O+'}slide': sid, '{'+O+'}id-list': ''})
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
data[47]['notes'] = 'Editing divider after logical Slide33a–c (PBFT tradeoff). Insert new content before this divider.'
ids = root.xpath('//@id')
assert len(ids) == len(set(ids))
assert len(slides) == len(data) == 95 and number == 81
assert [data[i]['displayNumber'] for i in [44, 45, 46]] == [33, 33, 33]
assert data[47]['title'] == 'Old slides below'
assert meta[0].get('id') == 'ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]] == [w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
t.write(str(R / 'editable-deck.svg'), encoding='utf-8', xml_declaration=True)
(R / 'deck.json').write_text(json.dumps(data, ensure_ascii=False))
p = R / 'continuity.md'
p.write_text(p.read_text()+'\n- Added33a–c (at most3 builds as requested), group pbft-tradeoff-builds:33a reuses the exact vulnerability timeline and citations, introducing rare actual compromise as a design premise;33b adapts31b spectrum to $10 coffee/thousands in account, $1M transfer, account deletion;33c reuses qualitative cost/security plot highlighting full BFT and replayable-transaction premise. Exact dictated script split contiguously across3builds. IDs slide-pbft-rare-compromises,slide-operation-risk-spectrum,slide-pbft-operation-cost.95frames/81logical;33a–c physical45–47,sentinel34/physical48. Local only.\n')
print('Added33a–c from existing components; exact script split across three builds.')
