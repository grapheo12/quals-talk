"""Promote the old Cautious Trust slide into the revised recovery narrative."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import json,shutil
W=Path(__file__).resolve().parent;S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
p=W/'editable-deck.svg';t=E.parse(str(p));root=t.getroot();data=json.loads((W/'deck.json').read_text())
slides=root.xpath('//*[@class="SlideGroup"]')[0]
at=next(i for i,m in enumerate(data) if m['title']=='Old slides below')
old=next(i for i,w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id')=='id44')
assert at==50 and old==69
backup=W/'revisions'/'before-cautious-ledger-recovery-36';backup.mkdir(parents=True,exist_ok=True)
for f in ['editable-deck.svg','deck.json']:
 if not (backup/f).exists():shutil.copy2(W/f,backup/f)
wrapper=slides[old];record=data.pop(old);slides.remove(wrapper);slides.insert(at,wrapper);data.insert(at,record)
slide=wrapper.xpath('.//*[@class="Slide"]')[0]
page=deepcopy(root.xpath('//*[@id="slide-cautious-trust-audit"]/*[@class="Page"]')[0])
mapping={e.get('id'):'ledger36-'+e.get('id') for e in page.iter() if e.get('id')}
for e in page.iter():
 if e.get('id'):e.set('id',mapping[e.get('id')])
 for k,v in list(e.attrib.items()):
  for a,b in mapping.items():
   v=v.replace('url(#'+a+')','url(#'+b+')')
   if v=='#'+a:v='#'+b
  e.set(k,v)
slide.replace(slide.xpath('./*[@class="Page"]')[0],page)
g=page[0];parts=list(g)
title='Cautious Trust for ledger recovery'
for i,label in {1:title,3:'36',4:'BFT auditor',5:'Fast ledger (critical path)',6:'Checks asynchronously for tampering',7:'Unsafe under TEE compromise',9:'Audited prefix'}.items():parts[i].text=label
parts[9].set('x','436');parts[9].set('y','497');parts[9].set('font-size','22');parts[9].set('fill','#28714E')
for node in [parts[10],parts[11]]:g.remove(node)
ledger=parts[8][0]
for i,block in enumerate(ledger):
 for path in block.xpath('.//*[local-name()="path" and @fill!="none"]'):path.set('fill','#BFE2C5' if i<4 else '#F8CC8D')
def el(parent,tag,**attrs):return E.SubElement(parent,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def text(x,y,label,size=24,color='#1F2328',weight=400,anchor='start'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=label;return e
# Bracket only the newest entries; the older prefix has already been audited.
el(g,'path',d='M588 466 V478 H895 V466',fill='none',stroke='#A02B93',stroke_width='2.5',stroke_linejoin='round')
text(741.5,507,'Unaudited tail: keep it bounded',21,'#A02B93',500,'middle')
text(98,565,'1',28,'#A02B93',700)
text(138,565,'Survive a shared TEE vulnerability',27,'#1F2328',500)
text(138,597,'One vendor’s flaw must not compromise the entire auditor.',22,'#6B7785')
text(98,641,'2',28,'#A02B93',700)
text(138,641,'Bound the unaudited ledger',27,'#1F2328',500)
text(138,673,'Recovery cannot allow the auditor to fall arbitrarily behind.',22,'#6B7785')
script="Can we do something with the causal trust modeling? Well, we can run a fast but insecure-under-compromises ledger protocol in the critical path and asynchronously let a Byzantine fault tolerant auditor audit the ledger for tampering. But we need to solve two challenges to do this: first, we need to make sure that the auditor service isn't totally compromised by vulnerabilities in one type of TEE vendor. And secondly, in order to ensure recovery, we can't let the auditor fall arbitrarily behind. In other words, we need to bound the length of the audit log that remains unaudited at any given time."
record.update(title=title,section='Pirateship',speakerScript=script,notes=script+'\n\nReuses the earlier Cautious Trust diagram and promotes original id44. Auditor remains left, computation right. The ledger distinguishes an audited prefix from a bounded unaudited tail. Two requirements are stated without asserting a specific bound or proposing a vendor-diversity mechanism yet. Exact dictated narration is preserved, including “causal trust modeling”; the visible title uses the established Cautious Trust name.',text=' '.join(' '.join(slide.xpath('.//*[local-name()="text"]//text()')).split()))
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={e.get('{'+O+'}slide'):e for e in meta if e.get('id','').startswith('ooo:meta_slide_')}
records['id44']=deepcopy(records['slide-cautious-trust-audit']);records['id44'].set('{'+O+'}slide','id44');records['id44'].set('{'+O+'}display-name',title)
for e in list(meta):
 if e.get('id','').startswith('ooo:meta_slide_'):meta.remove(e)
index=root.xpath('//*[@class="TextShapeIndex"]')[0];items={e.get('{'+O+'}slide'):e for e in index};items['id44'].set('{'+O+'}id-list','')
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
data[at+1]['notes']='Editing divider after logical Slide36 (Cautious Trust for ledger recovery). Insert new content before this divider.'
ids=root.xpath('//@id');assert len(ids)==len(set(ids))
assert len(slides)==len(data)==94 and number==79
assert data[at]['displayNumber']==36 and data[at+1]['displayNumber']==37
assert meta[0].get('id')=='ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]]==[w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
t.write(str(p),encoding='utf-8',xml_declaration=True);(W/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
with (W/'continuity.md').open('a') as f:f.write('\n- Promoted original id44 to36/physical51 using the revised12a Cautious Trust artwork. Fast ledger on the right (critical path, unsafe under TEE compromise), asynchronous BFT auditor left. Reused eight-entry ledger now shows an audited prefix and explicitly bracketed bounded unaudited tail. Two flat requirements below: survive a shared-vendor TEE flaw and bound audit lag for recovery. Exact user script retained. Sentinel37/physical52;94frames/79logical unchanged. Backup revisions/before-cautious-ledger-recovery-36. Local only.\n')
print('Slide36 complete: fast ledger, asynchronous BFT auditor, and two recovery requirements.94frames/79logical; sentinel37.')
