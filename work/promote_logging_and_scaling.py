from pathlib import Path
from lxml import etree as E
import json,copy,shutil
R=Path(__file__).resolve().parent;S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();data=json.loads((R/'deck.json').read_text());slides=r.xpath('//*[@class="SlideGroup"]')[0]
b=R/'revisions'/'before-logging-and-scaling';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
def promote(title):
 old=next(i for i,s in enumerate(data) if s['title']==title);at=next(i for i,s in enumerate(data) if s['title']=='Old slides below');assert old>at
 w=slides[old];slides.remove(w);slides.insert(at,w);rec=data.pop(old);data.insert(at,rec)
 return rec,w.xpath('.//*[@class="Slide"]')[0]
rec,s=promote('Detecting Rollbacks through Logging');assert s.get('id')=='id74'
a=r.xpath('//*[@id="id74-animations"]')[0];before=E.tostring(a)
script='Now I am not the first one to look at rollback attacks for TEEs. The usual method for detecting such rollbacks is through fault tolerant logging. Every state update is logged to a separate persistent logging service. Since rollback attacks only affect TEEs that are restarted, a fault tolerant logging service maintains at least 1 logging server that has seen all log entries from the TEE and would therefore be able to detect inconsistencies.'
rec.update(speakerScript=script,notes=script+'\n\nVisual direction: Reuse the original replicated logging diagram and all five animation steps. Retain the latest logged X=2 across restart and compare it with rolled-back X=1.')
# Same original conversion artefacts as the preceding rollback example.
targets=set(a.xpath('.//@smil:targetElement',namespaces={'smil':'http://www.w3.org/2001/SMIL20/'}));hidden=0
for d in s.xpath('.//*[local-name()="desc" and contains(text(),"Gears")]'):
 if d.getparent().xpath('.//*[@class="BoundingBox"]')[0].get('width')!='1704':continue
 top=d
 while top.getparent()!=s[0]:top=top.getparent()
 assert not targets.intersection(top.xpath('.//@id'))
 top.set('display','none');top.set('data-conversion-repair','unused-source-icon-copy');hidden+=1
assert hidden==6 and E.tostring(a)==before
rec,s=promote('Scaling up…');assert s.get('id')=='id69'
p=s[0];p.clear();p.set('class','Page')
def el(parent,tag,**attrs):return E.SubElement(parent,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
g=el(p,'g',transform='scale(26.45859375)')
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white')
def txt(x,y,value,size=28,color='#1F2328',weight=400,anchor='start'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color);e.text=value;return e
title='What happens when we scale up?'
txt(98,119,title,48,weight=700);el(g,'rect',x=98,y=140,width=67,height=4.8,fill='#1F5F8B')
txt(98,228,'Spark  ·  Flink  ·  Microservice meshes',30,color='#1F5F8B',weight=500)
# Reuse the original editable service-mesh diagram from the HarborMaster overview.
mesh=el(g,'g',transform='translate(98 300) scale(0.04) translate(-7980 -4220)')
source=r.xpath('//*[@id="id71"]')[0][0]
for original in list(source)[1:11]:
 part=copy.deepcopy(original)
 for e in part.iter():
  if e.get('id'):e.set('id','scaling16-'+e.get('id'))
 mesh.append(part)
txt(994,410,'100s',82,color='#A02B93',weight=700,anchor='middle')
txt(994,460,'of nodes',30,color='#6B7785',anchor='middle')
txt(98,625,'How do we detect rollbacks across the cluster?',30,weight=500)
txt(1182,692,'16',14.67,color='#6B7785',anchor='end')
script='But what do we do when we scale up? Think modern cluster computing applications like Spark or Flink or microservice meshes with 100s of nodes.'
rec.update(title=title,text='What happens when we scale up? Spark Flink Microservice meshes Service Layer Svc A Svc B Svc C 100s of nodes How do we detect rollbacks across the cluster?',section='HarborMaster',speakerScript=script,notes=script+'\n\nVisual direction: Reused the original Scaling up slide and the service-layer mesh from the HarborMaster overview.')
for anim in r.xpath('//*[@id="id69-animations"]'):
 for child in list(anim):anim.remove(child)
meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
for k,v in {'display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','has-transition':'false'}.items():records['id69'].set('{'+O+'}'+k,v)
idx=r.xpath('//*[@class="TextShapeIndex"]')[0];indices={e.get('{'+O+'}slide'):e for e in idx}
if 'id69' in indices:indices['id69'].set('{'+O+'}id-list','')
seen={};n=0
for i,(record,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
 if sid in indices:idx.append(indices[sid])
 record['number']=i+1;group=record.get('slideGroup')
 if not group or group['id'] not in seen:
  n+=1
  if group:seen[group['id']]=n
 number=seen[group['id']] if group else n;record['displayNumber']=number
 if group:group['number']=number
 for e in w.xpath('.//*[local-name()="text" and @y="692" and @x="1182"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(number)
assert len(data)==112 and n==109
assert data[17]['displayNumber']==15 and data[18]['displayNumber']==16 and data[19]['title']=='Old slides below'
data[19]['notes']='Editing divider after logical Slide16 (scaling up). Insert new content before this divider.'
assert E.tostring(a)==before
assert meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(slides):assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- User preference: reuse existing slides and visual assets as much as possible for subsequent edits.\n- Slide15 promotes original id74 Detecting Rollbacks through Logging, all five animation builds preserved; six unused icon copies hidden as on14. Exact dictated speaker script. Physical18.\n- Slide16 promotes id69 Scaling up and reuses original id71 service-mesh vectors; Spark/Flink/microservices heading, 100s of nodes callout. Exact dictated script. Physical19; sentinel now logical17/physical20. Counts112/109 unchanged. Local only.\n')
print('Updated slides15/16; logging animations preserved; divider follows16.')
