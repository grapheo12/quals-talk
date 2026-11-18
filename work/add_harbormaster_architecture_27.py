from pathlib import Path
from lxml import etree as E
import json,copy,shutil
R=Path(__file__).resolve().parent;S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();data=json.loads((R/'deck.json').read_text());slides=r.xpath('//*[@class="SlideGroup"]')[0]
b=R/'revisions'/'before-harbormaster-architecture-27';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
sl=r.xpath('//*[@id="id89"]')[0];source=copy.deepcopy(sl[0]);page=sl[0];page.clear();page.set('class','Page')
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
g=el(page,'g',transform='scale(26.45859375)')
blue='#1F5F8B';ink='#1F2328';gray='#6B7785';purple='#A02B93';green='#44B649'
def txt(x,y,text,size=24,color=ink,weight=400,anchor='middle'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
txt(98,119,'Cautious Trust in HarborMaster',48,weight=700,anchor='start');el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue)
# Preserve the original deck's compute, detective, disk, and lock vector artwork.
gear=source[4];auditor=source[6];db=source[2].xpath('.//*[local-name()="desc" and contains(text(),"Database")]')[0].getparent();lock=source[2].xpath('.//*[local-name()="desc" and contains(text(),"Lock")]')[0].getparent()
serial=0
def icon(node,x,y,w,h):
 global serial
 serial+=1;c=copy.deepcopy(node);bb=c.xpath('.//*[@class="BoundingBox"]')[0];bx,by,bw,bh=[float(bb.get(k)) for k in ['x','y','width','height']];scale=min(w/bw,h/bh)
 wrap=el(g,'g',transform=f'translate({x+(w-bw*scale)/2} {y+(h-bh*scale)/2}) scale({scale}) translate({-bx} {-by})')
 for e in c.iter():
  if e.get('id'):e.set('id',f'hm27-{serial}-'+e.get('id'))
 wrap.append(c)
def arrow(x1,y1,x2,y2,color=blue):
 el(g,'path',d=f'M{x1} {y1} L{x2-10} {y2}',stroke=color,stroke_width=3,fill='none');el(g,'path',d=f'M{x2} {y2} L{x2-12} {y2-6} L{x2-12} {y2+6} Z',fill=color,stroke='none')
txt(252,227,'Parallel computation',27,weight=500)
for x in [114,218,322]:
 el(g,'rect',x=x,y=306,width=70,height=88,fill='white',stroke=blue,stroke_width=2)
 icon(gear,x+10,317,50,50);icon(lock,x+50,367,32,32)
txt(252,446,'TEE-based worker nodes',23,color=gray)
txt(252,480,'Run in parallel',24,color=blue,weight=500)
# Same green ledger as Cautious Trust, now explicitly annotated with vector clocks.
txt(668,227,'Durable causal logs',27,weight=500)
arrow(406,355,553,355);txt(477,297,'Causal log',20);txt(477,323,'entries',20)
for i,label in enumerate(['⟨2,1,…⟩','⟨3,1,…⟩','⟨3,2,…⟩']):
 x=557+i*76;el(g,'rect',x=x,y=335,width=76,height=44,fill=green,stroke=ink,stroke_width=1.3);txt(x+38,363,label,17,weight=500)
txt(671,408,'Vector clocks',22,color=blue)
el(g,'path',d='M671 423 L671 445',stroke=gray,stroke_width=2,fill='none')
for x in [560,642,724]:icon(db,x,457,74,77)
icon(lock,788,503,32,32)
txt(671,569,'Fault-tolerant storage',24,weight=500)
txt(671,599,'2f + 1 TEE storage servers',20,color=gray)
# Audit consumes logs independently of ongoing worker execution.
arrow(799,355,959,355);txt(879,319,'Stream logs',20)
txt(1055,227,'Asynchronous auditing',27,weight=500)
icon(auditor,1003,287,102,112);icon(lock,1091,368,34,34)
txt(1055,446,'TEE-backed auditor',23,color=gray)
txt(1055,486,'Recreate worker state',22)
txt(1055,522,'Check causality',26,color=purple,weight=500)
txt(1182,692,'27',14.67,color=gray,anchor='end')
# Promote the existing HarborMaster architecture slide into the revised section.
old=next(i for i,w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id')=='id89');at=next(i for i,s in enumerate(data) if s['title']=='Old slides below');assert old>at and at==34
w=slides[old];slides.remove(w);slides.insert(at,w);rec=data.pop(old);data.insert(at,rec)
script="Let's now see the full cautious trust architecture for HarborMaster in action. It has many TEE-based compute nodes running in parallel, they emit causal log entries with vector clocks that are stored in a fault tolerant storage system, and then a TEE-backed auditor consumes this log entries to check for Causality violations."
rec.update(title='Cautious Trust in HarborMaster',text='Cautious Trust in HarborMaster Parallel computation TEE-based worker nodes Run in parallel Causal log entries Vector clocks Durable causal logs Fault-tolerant storage 2f + 1 TEE storage servers Stream logs Asynchronous auditing TEE-backed auditor Recreate worker state Check causality',speakerScript=script,notes=script+'\n\nVisual source: HarborMaster paper, Figure2 and Section3.1, p.4 (printed2129), /Users/shubham_mishra/Downloads/3819518.3819539.pdf. Workers, storage servers and auditors run in TEEs; N=2f+1 replicated storage servers stream per-worker causal logs to the auditor. Reuses original Cautious Trust green ledger, gears, detective, database and lock vectors.')
for a in r.xpath('//*[@id="id89-animations"]'):a.getparent().remove(a)
meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
for k,v in {'master-objects-visibility':'hidden','background-visibility':'hidden','has-transition':'false','display-name':rec['title']}.items():records['id89'].set('{'+O+'}'+k,v)
idx=r.xpath('//*[@class="TextShapeIndex"]')[0];indices={e.get('{'+O+'}slide'):e for e in idx};indices['id89'].set('{'+O+'}id-list','')
seen={};n=0
for i,(s,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
 if sid in indices:idx.append(indices[sid])
 s['number']=i+1;group=s.get('slideGroup')
 if not group or group['id'] not in seen:
  n+=1
  if group:seen[group['id']]=n
 num=seen[group['id']] if group else n;s['displayNumber']=num
 if group:group['number']=num
 for e in w.xpath('.//*[local-name()="text" and @y="692" and @x="1182"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(num)
assert len(data)==109 and n==101 and data[34]['displayNumber']==27
assert data[35]['title']=='Old slides below';data[35]['notes']='Editing divider after logical Slide27 (HarborMaster architecture). Insert new content before this divider.'
ids=r.xpath('//@id');assert len(ids)==len(set(ids))
assert meta[0].get('id')=='ooo:meta_dummy_slide'
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
p=R/'continuity.md';p.write_text(p.read_text()+'\n- Slide27 promotes original id89 HarborMaster architecture, redrawn with original compute/detective/storage/lock vectors and green Cautious Trust ledger. Based on attached HarborMaster paper Fig2 (p4/2129): parallel TEE workers → vector-clock log entries → replicated TEE storage → asynchronous TEE auditor recreating worker state/checking causality. Exact narration retained. Divider28/physical36. Counts109/101 unchanged. Local only.\n')
print('Updated Slide27 using original vector assets and paper Figure2.')
