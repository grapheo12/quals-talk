from pathlib import Path
from lxml import etree as E
import json,copy,re,shutil
R=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export';SM='http://www.w3.org/2001/SMIL20/'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();data=json.loads((R/'deck.json').read_text());slides=r.xpath('//*[@class="SlideGroup"]')[0]
b=R/'revisions'/'before-logging-choices-18';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
idx=r.xpath('//*[@class="TextShapeIndex"]')[0];indices={e.get('{'+O+'}slide'):e for e in idx}
def find(sid):return next(i for i,w in enumerate(slides) if w.xpath('.//*[@class="Slide"]')[0].get('id')==sid)
at=next(i for i,s in enumerate(data) if s['title']=='Old slides below');assert at==20
old=find('id76');w=slides[old];slides.remove(w);slides.insert(at,w);record=data.pop(old);data.insert(at,record)
script='So how do you perform logging for more than one node?\nThere are two options:\n\n1. You can force all nodes to log their state updates to a Single-log.\n\n2. Or you can let every node sends its updates to its own private log, which we will call the multi-log setup.\nBoth choices have their own problems!'
record['speakerScript']=script;record['notes']=script+'\n\nVisual direction: Original single-log versus multi-log comparison, both animation steps retained.'
for offset,(source,prefix) in enumerate([('id77','single-log-19'),('id78','multi-log-20'),('id79','multi-log-21')],1):
 source_index=find(source);w=copy.deepcopy(slides[source_index]);record=copy.deepcopy(data[source_index]);anim_source=r.xpath('//*[@id=$i]',i=source+'-animations')[0];anim=copy.deepcopy(anim_source)
 m=copy.deepcopy(records[source]);ix=copy.deepcopy(indices[source]) if source in indices else None
 nodes=[w,anim,m]+([ix] if ix is not None else [])
 mapping={e.get('id'):prefix+'-'+e.get('id') for tree in [w,anim] for e in tree.iter() if e.get('id')}
 pattern=re.compile(r'(?<![\w-])('+ '|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True))+r')(?![\w-])')
 for tree in nodes:
  for e in tree.iter():
   for k,v in list(e.attrib.items()):e.set(k,pattern.sub(lambda match:mapping[match.group(0)],v))
 sid=mapping[source];assert m.get('{'+O+'}slide')==sid
 records[sid]=m
 if ix is not None:indices[sid]=ix
 anim_source.getparent().append(anim);slides.insert(at+offset,w);data.insert(at+offset,record)
 # Validate the animation copy is identical apart from renamed identifiers.
 restored=copy.deepcopy(anim)
 reverse={v:k for k,v in mapping.items()};pat=re.compile('|'.join(re.escape(k) for k in sorted(reverse,key=len,reverse=True)))
 for e in restored.iter():
  for k,v in list(e.attrib.items()):e.set(k,pat.sub(lambda match:reverse[match.group(0)],v))
 assert [(e.tag, dict(e.attrib), e.text) for e in restored.iter()]==[(e.tag, dict(e.attrib), e.text) for e in anim_source.iter()]
 for target in anim.xpath('.//@smil:targetElement',namespaces={'smil':SM}):assert w.xpath('.//*[@id=$i]',i=target)
for m in list(meta):
 if m.get('id','').startswith('ooo:meta_slide_'):meta.remove(m)
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
meta.set('{'+O+'}number-of-slides',str(len(data)))
assert len(data)==115 and n==112 and data[20]['displayNumber']==18 and data[23]['displayNumber']==21
assert data[24]['title']=='Old slides below';data[24]['notes']='Editing divider after logical Slide21 (multi-log amplification). Insert new content before this divider.'
assert meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(slides):assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
ids=r.xpath('//@id');assert len(ids)==len(set(ids))
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Slide18 promotes original id76 single-log vs multi-log comparison, exact dictated script and both animations. Slides19–21 are requested unchanged copies of id77/id78/id79 (single-log overhead, multi-log independent writes, multi-log amplification). Clone IDs prefixed single-log-19-, multi-log-20-, multi-log-21-; all original animation steps copied and remapped with validation. Originals remain below divider. Footer numbers updated only. Divider logical22/physical25. Counts115 physical/112 logical. Local only.\n')
print('Added slides18–21; all source animation sequences preserved; originals19–21 retained below divider.')
