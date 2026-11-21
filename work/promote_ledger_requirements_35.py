"""One-time promotion of the original animated ledger requirements slide."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import json,shutil
W=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg'; O='http://xml.openoffice.org/svg/export'
p=W/'editable-deck.svg';t=E.parse(str(p));root=t.getroot();data=json.loads((W/'deck.json').read_text())
slides=root.xpath('//*[@class="SlideGroup"]')[0]
at=next(i for i,m in enumerate(data) if m['title']=='Old slides below')
old=next(i for i,w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id')=='id31')
assert at==49 and old==56
backup=W/'revisions'/'before-ledger-requirements-35';backup.mkdir(parents=True,exist_ok=True)
for f in ['editable-deck.svg','deck.json']:
 if not (backup/f).exists():shutil.copy2(W/f,backup/f)
wrapper=slides[old];record=data.pop(old);slides.remove(wrapper);slides.insert(at,wrapper);data.insert(at,record)
# Reuse the existing two panels, risk spectrum and three click reveals.
# Replace the left panel's old bitmap outlines/bolts with the current cracked replicas.
left=root.xpath('//*[@id="id145"]')[0]
network=deepcopy(root.xpath('//*[@data-source="original-correlated-compromise-network"]')[0])
mapping={e.get('id'):'requirements35-'+e.get('id') for e in network.iter() if e.get('id')}
for e in network.iter():
 if e.get('id'):e.set('id',mapping[e.get('id')])
 for key,value in list(e.attrib.items()):
  for a,b in mapping.items():
   value=value.replace('url(#'+a+')','url(#'+b+')')
   if value=='#'+a:value='#'+b
  e.set(key,value)
network.set('transform','translate(-8707.66 5547.87) scale(.67767)')
network.set('data-source','reused-cracked-replica-network')
left.replace(left[1],network)
conclusion=root.xpath('//*[@id="id147"]//*[local-name()="tspan" and text()="No ledger provides either"]')[0]
conclusion.text='No ledger provides both'
position=conclusion.getparent();position.set('x','17951');position.set('text-anchor','middle')
for child in position:
 child.attrib.pop('textLength',None);child.attrib.pop('lengthAdjust',None)
script='So what do we want in a ledger? It should be aware of the reality of TEE compromises, and it should provide flexible protection with according to the risk tolerance of the operation. Currently no ledger provides both.'
record.update(title='What do we want in a ledger?',section='Pirateship',speakerScript=script,notes=script+'\n\nPromotes the original ledger-requirements slide, preserving its two panels, original risk-spectrum artwork and three click reveals. The replica diagram reuses the cracked-open nodes from34c. The conclusion is updated from either to both, matching the new dictated script.')
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={e.get('{'+O+'}slide'):e for e in meta if e.get('id','').startswith('ooo:meta_slide_')}
for e in list(meta):
 if e.get('id','').startswith('ooo:meta_slide_'):meta.remove(e)
index=root.xpath('//*[@class="TextShapeIndex"]')[0]
items={e.get('{'+O+'}slide'):e for e in index}
valid={e.get('id') for e in wrapper.iter() if e.get('id')}
items['id31'].set('{'+O+'}id-list',' '.join(x for x in items['id31'].get('{'+O+'}id-list','').split() if x in valid))
seen={};number=0
for i,(m,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');r=records[sid];r.set('id',f'ooo:meta_slide_{i}');meta.append(r)
 if sid in items:index.append(items[sid])
 m['number']=i+1;group=m.get('slideGroup')
 if not group or group['id'] not in seen:
  number+=1
  if group:seen[group['id']]=number
 logical=seen[group['id']] if group else number;m['displayNumber']=logical
 if group:group['number']=logical
 for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(logical)
record['text']=' '.join(' '.join(wrapper.xpath('.//*[local-name()="text"]//text()')).split())
data[at+1]['notes']='Editing divider after logical Slide35 (ledger requirements). Insert new content before this divider.'
ids=root.xpath('//@id');assert len(ids)==len(set(ids))
assert len(slides)==len(data)==94 and number==79
assert data[at]['displayNumber']==35 and data[at+1]['displayNumber']==36
assert meta[0].get('id')=='ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]]==[w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
previous=E.parse(str(backup/'editable-deck.svg'))
ns={'o':O}
a=root.xpath('//*[@class="Animations" and @o:slide="id31"]',namespaces=ns)[0]
b=previous.xpath('//*[@class="Animations" and @o:slide="id31"]',namespaces=ns)[0]
assert E.tostring(a)==E.tostring(b)
for target in a.xpath('.//@*[local-name()="targetElement"]'):assert target in ids
t.write(str(p),encoding='utf-8',xml_declaration=True)
(W/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
with (W/'continuity.md').open('a') as f:f.write('\n- Promoted original id31 ledger requirements to35/physical50. Reused both requirement panels and original risk spectrum, retaining all three click reveals. Left diagram reuses34c’s cracked native replicas; conclusion now says “No ledger provides both.” Exact dictated script stored. Sentinel now36/physical51;94frames/79logical unchanged. Text-shape index repaired for replaced diagram; metadata and numbering synchronized. Backup revisions/before-ledger-requirements-35. Local only.\n')
print('Promoted animated ledger requirements to35; sentinel36.94frames/79logical. Exact narration and all three reveals preserved.')
