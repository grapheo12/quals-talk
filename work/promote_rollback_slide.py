from pathlib import Path
from lxml import etree as E
import json, shutil
R=Path(__file__).resolve().parent
O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
data=json.loads((R/'deck.json').read_text())
slides=root.xpath('//*[@class="SlideGroup"]')[0]
source=next(i for i,s in enumerate(data) if s['title']=='Disk Integrity Violation with Rollback Attacks')
at=next(i for i,s in enumerate(data) if s['title']=='Old slides below')
assert source>at and at==16
b=R/'revisions'/'before-rollback-slide-14';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
animations=root.xpath('//*[@id="id72-animations"]')[0]
before=E.tostring(animations)
w=slides[source];assert w.xpath('.//*[@class="Slide"]')[0].get('id')=='id72'
slides.remove(w);slides.insert(at,w)
s=data.pop(source)
intro="But first, let's see how a malicious cloud provider can tamper with persistent storage. Typically, if your TEEs are working correctly, it cannot change your application state with random garbage, as the TEE can simply put a cryptographic signature on the state before storing it in the disk. However, it can replace the current state with an older state, we call this a Rollback attack.\n\nLet's understand this with an example. A TEE first starts with the state X = 1."
example="\n\nNow you make a write, that updates X to 2.\n\nNext, your VM goes down.\n\nAnd while it is down, the malicious cloud provider rolls back the disk replacing the current state with an old copy.\n\nWhen the VM comes back online, you will have no idea what has happened."
s['speakerScript']=intro+example
s['notes']=intro+example+'\n\nVisual direction: Reused original rollback example and its four click-triggered builds unchanged. Write X = 2 → VM goes down → replace current disk state with X = 1 → VM restarts and reads X = 1.'
data.insert(at,s)
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
idx=root.xpath('//*[@class="TextShapeIndex"]')[0]
indices={e.get('{'+O+'}slide'):e for e in idx}
seen={};n=0
for i,(record,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id')
 m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
 if sid in indices:idx.append(indices[sid])
 record['number']=i+1;group=record.get('slideGroup')
 if not group or group['id'] not in seen:
  n+=1
  if group:seen[group['id']]=n
 number=seen[group['id']] if group else n;record['displayNumber']=number
 if group:group['number']=number
 for e in w.xpath('.//*[local-name()="text" and @y="692" and @x="1182"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(number)
data[at+1]['notes']='Editing divider after logical Slide 14 (rollback attacks). All following slides are original material awaiting revision. Insert new content before this divider.'
assert data[at]['displayNumber']==14 and data[at+1]['displayNumber']==15
assert len(data)==len(slides)==112 and n==109
assert E.tostring(animations)==before
assert meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(slides):assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
for target in animations.xpath('.//@smil:targetElement',namespaces={'smil':'http://www.w3.org/2001/SMIL20/'}):assert root.xpath('//*[@id=$id]',id=target)
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Logical Slide14: moved original rollback attacks slide id72 from physical84 to17, before the sentinel (now logical15/physical18). Original four-click animation XML, shape IDs and motion/fade effects preserved unchanged. User introduction plus original X=1 → write X=2 → VM down → rollback → restart/read X=1 narration saved as speakerScript, without directives. 112 frames/109 logical slides unchanged. Local only.\n')
print('Moved rollback example to logical14, all four animation builds preserved.')
