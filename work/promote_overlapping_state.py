from pathlib import Path
from lxml import etree as E
import json,shutil
R=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();data=json.loads((R/'deck.json').read_text());slides=r.xpath('//*[@class="SlideGroup"]')[0]
b=R/'revisions'/'before-overlapping-state-17';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
old=next(i for i,s in enumerate(data) if s['title']=='Logging problems at scale');at=next(i for i,s in enumerate(data) if s['title']=='Old slides below');assert old>at and at==19
w=slides[old];sl=w.xpath('.//*[@class="Slide"]')[0];assert sl.get('id')=='id75'
a=r.xpath('//*[@id="id75-animations"]')[0];before=E.tostring(a)
slides.remove(w);slides.insert(at,w);rec=data.pop(old);data.insert(at,rec)
# Match the dictated example in both the stored state and the animated message.
for e in sl.iter():
 if e.text in ['X = 3','W(X) = 3']:e.text=e.text.replace('= 3','= 2')
script='Two different nodes could have partially overlapping states. Two different nodes could have partially overlapping states, for example, this variable X here. And it can have different values: node 1 has X = 1, node 2 has X = 2.\nDepending on your applications consistency requirements, both versions may be valid at a given moment of time!\n\nAnd, the nodes are not isolated, they pass messages to share the state updates.'
rec.update(speakerScript=script,notes=script+'\n\nVisual direction: Reuse the original overlapping-state example with both animation steps preserved. Node1: X=1, Y=2; Node2: X=2, Z=4. The second build sends W(X)=2 from Node2 to Node1.',text=rec['text'].replace('X = 3','X = 2').replace('W(X) = 3','W(X) = 2'))
meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
idx=r.xpath('//*[@class="TextShapeIndex"]')[0];indices={e.get('{'+O+'}slide'):e for e in idx}
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
assert len(data)==112 and n==109 and data[19]['displayNumber']==17
assert data[20]['title']=='Old slides below';data[20]['notes']='Editing divider after logical Slide17 (overlapping node states). Insert new content before this divider.'
assert E.tostring(a)==before and meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(slides):assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Slide17 promotes original id75 Logging problems at scale (physical20), preserving both animation steps including message motion. Node2 state and message changed X=3 to X=2 to match dictated script. Exact speaker wording saved with formatting backslashes removed. Divider logical18/physical21; counts112/109 unchanged. Local only.\n')
print('Slide17 reused; node2 X=2; both original animation steps preserved.')
