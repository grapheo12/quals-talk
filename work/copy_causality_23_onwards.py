from pathlib import Path
from lxml import etree as E
import copy,json,re,shutil
R=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();d=json.loads((R/'deck.json').read_text());ws=r.xpath('//*[@class="SlideGroup"]')[0];meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];ix=r.xpath('//*[@class="TextShapeIndex"]')[0]
b=R/'revisions'/'before-copying-78-85';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')};indices={e.get('{'+O+'}slide'):e for e in ix}
sources=[(copy.deepcopy(s),copy.deepcopy(ws[i])) for i,s in enumerate(d) if 78<=s['displayNumber']<=85];assert len(sources)==8
at=next(i for i,s in enumerate(d) if s['title']=='Old slides below');assert at==26
for j,(s,w) in enumerate(sources):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');prefix=f'causality-copy-{j}-';animsrc=r.xpath('//*[@id=$i]',i=sid+'-animations');anim=copy.deepcopy(animsrc[0]) if animsrc else None;m=copy.deepcopy(records[sid]);index=copy.deepcopy(indices[sid]) if sid in indices else None
 trees=[w]+([anim] if anim is not None else []);mapping={e.get('id'):prefix+e.get('id') for tree in trees for e in tree.iter() if e.get('id')};pat=re.compile(r'(?<![\w-])('+'|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True))+r')(?![\w-])')
 for tree in trees+[m]+([index] if index is not None else []):
  for e in tree.iter():
   for k,v in list(e.attrib.items()):e.set(k,pat.sub(lambda q:mapping[q.group()],v))
 if anim is not None:
  animsrc[0].getparent().append(anim)
  for target in anim.xpath('.//@smil:targetElement',namespaces={'smil':'http://www.w3.org/2001/SMIL20/'}):assert w.xpath('.//*[@id=$i]',i=target)
  assert len(list(anim.iter()))==len(list(animsrc[0].iter()))
 records[mapping[sid]]=m
 if index is not None:ix.append(index)
 if 1<=j<=4:s['slideGroup']={'id':'causal-history-builds','number':24,'title':'Causality across nodes'}
 if j>=6:s['slideGroup']={'id':'vector-clock-builds','number':26,'title':'Vector clocks'}
 ws.insert(at+j,w);d.insert(at+j,s)
for m in list(meta):
 if m.get('id','').startswith('ooo:meta_slide_'):meta.remove(m)
seen={};n=0
for i,(s,w) in enumerate(zip(d,ws)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m);s['number']=i+1;g=s.get('slideGroup')
 if not g or g['id'] not in seen:
  n+=1
  if g:seen[g['id']]=n
 num=seen[g['id']] if g else n;s['displayNumber']=num
 if g:g['number']=num
 for e in w.xpath('.//*[local-name()="text" and @y="692" and @x="1182"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(num)
meta.set('{'+O+'}number-of-slides',str(len(d)))
assert len(d)==109 and n==101 and d[26]['displayNumber']==23 and d[33]['displayNumber']==26
assert d[34]['title']=='Old slides below';d[34]['notes']='Editing divider after logical Slide26 (vector clocks). Insert new content before this divider.'
ids=r.xpath('//@id');assert len(ids)==len(set(ids))
assert meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(ws):assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(d,ensure_ascii=False))
p=R/'continuity.md';p.write_text(p.read_text()+'\n- Copied then-current logical78–85 after22, retaining originals and animation trees with uniquely prefixed IDs causality-copy-0- through7-. New23 single-node causality;24a–d multi-node causal history;25 tracking-causality transition;26a–b vector clocks. Original speaker scripts retained. Divider27/physical35. 109 physical/101 logical. Local only.\n')
print('Copied8 frames as23,24a–d,25,26a–b; original animation targets validated.')
