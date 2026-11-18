from pathlib import Path
from lxml import etree as E
import copy,json,shutil,re
R=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export';S='http://www.w3.org/2000/svg'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();d=json.loads((R/'deck.json').read_text());ws=r.xpath('//*[@class="SlideGroup"]')[0];meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];ix=r.xpath('//*[@class="TextShapeIndex"]')[0]
b=R/'revisions'/'before-requirements-22';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
old=next(i for i,s in enumerate(d) if s['title']=='Scalable Rollback Detection Requirements');at=next(i for i,s in enumerate(d) if s['title']=='Old slides below');assert at==24
w=ws[old];ws.remove(w);ws.insert(at,w);rec=d.pop(old);d.insert(at,rec)
w2=copy.deepcopy(w);mapping={e.get('id'):'requirements22b-'+e.get('id') for e in w2.iter() if e.get('id')}
pat=re.compile(r'(?<![\w-])('+'|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True))+r')(?![\w-])')
for e in w2.iter():
 for k,v in list(e.attrib.items()):e.set(k,pat.sub(lambda m:mapping[m.group()],v))
ws.insert(at+1,w2);rec2=copy.deepcopy(rec);d.insert(at+1,rec2)
# Two navigation builds replace the original click reveal; keep its exact artwork.
callout=r.xpath('//*[@id="id266"]')[0];callout.set('display','none')
for a in r.xpath('//*[@id="id80-animations"]'):a.getparent().remove(a)
rec['speakerScript']='Remember the tenets of cautious trust. We wanted the application to run as fast as possible. So we really do not want to enforce stricter consistency guarantees than what the application already assumes. At the same time, an efficient rollback detection system must also be resource efficient. In this case, unlike multi-log setup, it should not be wasting disk bandwidth by redundant logging.'
rec2['speakerScript']='Can we do better? Turns out we can, by following this simple observation: Rollback attacks violate Causality.'
rec2['title']='Rollback attacks violate causality'
for s in [rec,rec2]:s['notes']=s['speakerScript'];s['slideGroup']={'id':'builds-requirements-22','number':22,'title':'Scalable rollback detection'}
records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
m2=copy.deepcopy(records['id80']);m2.set('{'+O+'}slide',mapping['id80']);records[mapping['id80']]=m2
for sid in ['id80',mapping['id80']]:records[sid].set('{'+O+'}has-transition','false')
sourceix=next((e for e in ix if e.get('{'+O+'}slide')=='id80'),None)
if sourceix is not None:
 ix2=copy.deepcopy(sourceix)
 for k,v in list(ix2.attrib.items()):ix2.set(k,pat.sub(lambda m:mapping[m.group()],v))
 ix.append(ix2)
for m in list(meta):
 if m.get('id','').startswith('ooo:meta_slide_'):meta.remove(m)
seen={};n=0
for i,(s,w) in enumerate(zip(d,ws)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
 s['number']=i+1;g=s.get('slideGroup')
 if not g or g['id'] not in seen:
  n+=1
  if g:seen[g['id']]=n
 num=seen[g['id']] if g else n;s['displayNumber']=num
 if g:g['number']=num
 for e in w.xpath('.//*[local-name()="text" and @y="692" and @x="1182"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(num)
meta.set('{'+O+'}number-of-slides',str(len(d)))
assert len(d)==101 and n==97 and d[24]['displayNumber']==d[25]['displayNumber']==22
assert d[26]['title']=='Old slides below';d[26]['notes']='Editing divider after logical Slide22 (requirements and causality observation). Insert new content before this divider.'
assert meta[0].get('id')=='ooo:meta_dummy_slide'
ids=r.xpath('//@id');assert len(ids)==len(set(ids))
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(d,ensure_ascii=False))
p=R/'continuity.md';p.write_text(p.read_text()+'\n- Slide22a/b reuses original id80 scalable rollback requirements and its exact callout artwork. Converted the original click reveal to two grouped frames: 22a hides id266; 22b cloned IDs requirements22b-* shows it. Exact new narration per build; shared footer22. Divider23/physical27. 101 frames/97 logical slides (original moved, one build added). Local only.\n')
print('Created grouped22a/22b from original requirements slide.')
