"""Adapt the old solution roadmap into builds36b/c of the recovery diagram."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import json,shutil
W=Path(__file__).resolve().parent;S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
p=W/'editable-deck.svg';tree=E.parse(str(p));root=tree.getroot();data=json.loads((W/'deck.json').read_text())
slides=root.xpath('//*[@class="SlideGroup"]')[0];source=root.xpath('//*[@id="id44"]/*[@class="Page"]')[0]
assert data[50]['displayNumber']==36 and data[51]['title']=='Old slides below'
backup=W/'revisions'/'before-recovery-roadmap-36bc';backup.mkdir(parents=True,exist_ok=True)
for f in ['editable-deck.svg','deck.json']:
 if not (backup/f).exists():shutil.copy2(W/f,backup/f)
selected=[]
for sid in ['id32','id33']:
 i=next(i for i,w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id')==sid)
 wrapper=slides[i];record=data.pop(i);slides.remove(wrapper);selected.append((sid,wrapper,record))
at=next(i for i,m in enumerate(data) if m['title']=='Old slides below')
group={'id':'ledger-recovery-builds','number':36,'title':'Cautious Trust: challenges and solutions'}
data[50]['slideGroup']=deepcopy(group)
scripts=[
 'Accordingly, I will first propose a new failure model for correlated TEE compromises, which I will call Platform Fault Tolerance and then, I will propose a new ledger protocol that will bound this gap, called Pirateship.',
 "Let's look at Platform Fault Tolerance first."
]
titles=['Two parts of the solution','First: Platform Fault Tolerance']
for offset,(sid,wrapper,record) in enumerate(selected):
 page=deepcopy(source);mapping={e.get('id'):sid+'-roadmap-'+e.get('id') for e in page.iter() if e.get('id')}
 for e in page.iter():
  if e.get('id'):e.set('id',mapping[e.get('id')])
  for key,value in list(e.attrib.items()):
   for a,b in mapping.items():
    value=value.replace('url(#'+a+')','url(#'+b+')')
    if value=='#'+a:value='#'+b
   e.set(key,value)
 g=page[0];g[1].text=titles[offset]
 g[13].text='Platform Fault Tolerance (PFT)';g[13].set('fill','#A02B93');g[13].set('font-weight','700')
 g[14].text='A failure model for correlated TEE compromises.'
 g[16].text='Pirateship';g[16].set('fill','#1F5F8B');g[16].set('font-weight','700')
 g[17].text='A ledger protocol that bounds the unaudited gap.'
 if offset==1:
  # Keep the diagram fixed, focus on the auditor/failure model, dim the protocol context.
  for idx in [5,7,9,10,11,15,16,17]:g[idx].set('opacity','.22')
  for idx in [0,1,2]:g[8][idx].set('opacity','.22')
  g[4].set('fill','#A02B93')
  for e in g[8][3].xpath('.//*[local-name()="path" and @fill!="none"]'):e.set('fill','#A02B93')
  for e in g[8][4].xpath('.//*[local-name()="path" and @fill!="none"]'):e.set('fill','#A02B93')
 slide=wrapper.xpath('.//*[@class="Slide"]')[0];slide.replace(slide.xpath('./*[@class="Page"]')[0],page)
 for a in root.xpath('//*[@class="Animations" and @ooo:slide="'+sid+'"]',namespaces={'ooo':O}):a.getparent().remove(a)
 record.update(title=titles[offset],section='Pirateship',speakerScript=scripts[offset],slideGroup=deepcopy(group),text=' '.join(' '.join(slide.xpath('.//*[local-name()="text"]//text()')).split()),notes=scripts[offset]+'\n\nReuses36a’s diagram and maps its two requirements to Platform Fault Tolerance and Pirateship, adapting the original solution-roadmap slide. Build36c focuses the auditor/failure-model branch and dims the protocol context. No new mechanism or quantitative bound is introduced.')
 slides.insert(at+offset,wrapper);data.insert(at+offset,record)
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={e.get('{'+O+'}slide'):e for e in meta if e.get('id','').startswith('ooo:meta_slide_')}
for i,sid in enumerate(['id32','id33']):
 records[sid]=deepcopy(records['id44']);records[sid].set('{'+O+'}slide',sid);records[sid].set('{'+O+'}display-name',titles[i])
for e in list(meta):
 if e.get('id','').startswith('ooo:meta_slide_'):meta.remove(e)
index=root.xpath('//*[@class="TextShapeIndex"]')[0];items={e.get('{'+O+'}slide'):e for e in index}
for sid in ['id32','id33']:items[sid].set('{'+O+'}id-list','')
seen={};number=0
for i,(m,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');r=records[sid];r.set('id',f'ooo:meta_slide_{i}');meta.append(r)
 if sid in items:index.append(items[sid])
 m['number']=i+1;build=m.get('slideGroup')
 if not build or build['id'] not in seen:
  number+=1
  if build:seen[build['id']]=number
 logical=seen[build['id']] if build else number;m['displayNumber']=logical
 if build:build['number']=logical
 for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(logical)
data[53]['notes']='Editing divider after logical Slide36a–c (Cautious Trust, recovery challenges and solution roadmap). Insert new content before this divider.'
ids=root.xpath('//@id');assert len(ids)==len(set(ids))
assert len(slides)==len(data)==94 and number==77
assert all(data[i]['displayNumber']==36 for i in [50,51,52]) and data[53]['displayNumber']==37
assert data[53]['title']=='Old slides below' and data[60]['title']=='Platform Fault Tolerance (PFT)'
assert meta[0].get('id')=='ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]]==[w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
tree.write(str(p),encoding='utf-8',xml_declaration=True);(W/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
with (W/'continuity.md').open('a') as f:f.write('\n- Added36b/c by promoting original id32/id33 solution-roadmap slides and adapting36a’s exact diagram/coordinates. New36b names Platform Fault Tolerance as the correlated-compromise failure model and Pirateship as the protocol bounding the unaudited gap.36c focuses the auditor/PFT branch while dimming ledger/protocol context. Exact scripts. Group ledger-recovery-builds now36a–c, physical51–53;sentinel37/physical54.94frames/77logical; original PFT section now44/physical61. Backup revisions/before-recovery-roadmap-36bc. Local only.\n')
print('36a–c grouped; roadmap and PFT focus added.94frames/77logical; sentinel37.')
