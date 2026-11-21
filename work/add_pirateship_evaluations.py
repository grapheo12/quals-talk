"""Copy requested Pirateship evaluation/recovery slides before the editing divider."""
from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import hashlib,json,re,shutil
W=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export';S='http://www.w3.org/2000/svg';X='http://www.w3.org/1999/xlink'
p=W/'editable-deck.svg';tree=E.parse(str(p));root=tree.getroot();data=json.loads((W/'deck.json').read_text())
slides=root.xpath('//*[@class="SlideGroup"]')[0]
source={w.xpath('.//*[@class="Slide"]')[0].get('id'):(w,m) for w,m in zip(slides,data)}
source_ids=[f'id{i}' for i in range(61,68)];prefix='pirateship-eval-'
assert not root.xpath('//*[starts-with(@id,"'+prefix+'")]')
at=next(i for i,m in enumerate(data) if m['title']=='Old slides below');assert at==77
backup=W/'revisions'/'before-pirateship-evaluations';backup.mkdir(parents=True,exist_ok=True)
for f in ['editable-deck.svg','deck.json']:
 if not (backup/f).exists():shutil.copy2(W/f,backup/f)
ns={'o':O};meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={e.get('{'+O+'}slide'):e for e in meta if e.get('id','').startswith('ooo:meta_slide_')}
index=root.xpath('//*[@class="TextShapeIndex"]')[0];items={e.get('{'+O+'}slide'):e for e in index}
animations={sid:root.xpath('//*[@class="Animations" and @o:slide="'+sid+'"]',namespaces=ns) for sid in source_ids}
mapping={sid:prefix+sid for sid in source_ids}
for sid in source_ids:
 for part in [source[sid][0]]+animations[sid]:mapping.update({e.get('id'):prefix+e.get('id') for e in part.iter() if e.get('id')})
pattern=re.compile(r'(?<![\w.-])('+'|'.join(sorted(map(re.escape,mapping),key=len,reverse=True))+r')(?![\w.-])')
def clone(part):
 c=deepcopy(part)
 for e in c.iter():
  for k,v in list(e.attrib.items()):e.set(k,pattern.sub(lambda m:mapping[m[1]],v))
 return c
def digest(w):
 c=deepcopy(w)
 for e in c.xpath('.//*[@class="CustomPageNumber"] | .//*[local-name()="text" and @x="1182" and @y="692"]'):e.getparent().remove(e)
 return hashlib.sha256(E.tostring(c,method='c14n',exclusive=True)).hexdigest()
existing={sid:digest(w) for sid,(w,m) in source.items()}
# The original later recovery builds reference an absent bitmap definition. Embed
# the same plot image from the first build, preserving the original reveal masks.
recovery_image=source['id64'][0].xpath('.//*[local-name()="image"]')[0]
recovery_scripts=[
 'Now I promised you recovery. Here is what happens when the leader starts equivocating. Initially, commit and audit are both making progress. Once equivocation starts, audit throughput drops.',
 'The first follower then times out. Commit throughput drops too, and the system begins recovery.',
 'The leader steps down. A new view is established, and commit and audit throughput begin to recover.',
 'Once the new view stabilizes, commit and audit return to their steady-state throughput.'
]
created=[];animation_parent=root.xpath('//*[@id="presentation-animations"]')[0]
for offset,sid in enumerate(source_ids):
 w=clone(source[sid][0]);m=deepcopy(source[sid][1]);m.pop('slideGroup',None);m['section']='Pirateship'
 if sid in ['id65','id66','id67']:
  uses=w.xpath('.//*[local-name()="use" and @xlink:href="#bitmap(449338366)"]',namespaces={'xlink':X});assert len(uses)==1
  uses[0].getparent().replace(uses[0],deepcopy(recovery_image))
 if int(sid[2:])>=64:
  k=int(sid[2:])-64;m['slideGroup']={'id':'pirateship-recovery-builds','title':'Recovery under equivocation'}
  m['speakerScript']=recovery_scripts[k]
  m['notes']=recovery_scripts[k]+'\n\nOriginal recovery plot and progressive reveal preserved. Replaces unrelated/misaligned imported speaker notes for this plot.'
 else:
  m['speakerScript']=m.get('speakerScript',re.sub(r'<[^>]*>','',m.get('notes','')).strip())
 expected=digest(w);new_sid=mapping[sid];slides.insert(at+offset,w);data.insert(at+offset,m)
 records[new_sid]=clone(records[sid]);items[new_sid]=clone(items[sid])
 for a in animations[sid]:animation_parent.append(clone(a))
 created.append((sid,new_sid,w,m,expected))
for e in list(meta):
 if e.get('id','').startswith('ooo:meta_slide_'):meta.remove(e)
seen={};logical_count=0
for i,(w,m) in enumerate(zip(slides,data)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');mr=records[sid];mr.set('id',f'ooo:meta_slide_{i}');meta.append(mr)
 if sid in items:index.append(items[sid])
 m['number']=i+1;g=m.get('slideGroup')
 if not g or g['id'] not in seen:
  logical_count+=1
  if g:seen[g['id']]=logical_count
 n=seen[g['id']] if g else logical_count;m['displayNumber']=n
 if g:g['number']=n
 for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(n)
meta.set('{'+O+'}number-of-slides',str(len(data)))
for sid,new_sid,w,m,expected in created:
 assert digest(w)==expected
 m['text']=' '.join(' '.join(w.xpath('.//*[local-name()="text"]//text()')).split())
divider=at+7;data[divider]['notes']='Editing divider after Slide54a–d (Pirateship recovery plots). Revised deck includes the three comparison plots and progressive recovery builds.'
assert len(slides)==len(data)==125 and logical_count==95
assert [d['displayNumber'] for d in data[at:divider]]==[51,52,53,54,54,54,54]
assert data[divider]['displayNumber']==55 and data[divider]['title']=='Old slides below'
ids=root.xpath('//@id');assert len(ids)==len(set(ids));idset=set(ids)
for sid,(w,m) in source.items():assert digest(w)==existing[sid],sid+' changed unexpectedly'
for sid,new_sid,w,m,expected in created:
 for e in w.iter():
  for v in e.attrib.values():
   for ref in re.findall(r'url\(#([^)]*)\)',v):assert ref in idset,(sid,ref)
  if E.QName(e).localname=='use':
   href=e.get('{'+X+'}href','');assert not href.startswith('#') or href[1:] in idset,(sid,href)
assert meta[0].get('id')=='ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]]==[w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
manifest=[{'source':sid,'id':nsid,'number':m['displayNumber'],'physical':m['number'],'title':m['title']} for sid,nsid,w,m,e in created]
(backup/'copied-slides.json').write_text(json.dumps(manifest,indent=2))
tmp=p.with_suffix('.tmp.svg');tree.write(str(tmp),encoding='utf-8',xml_declaration=True);tmp.replace(p)
j=W/'deck.json';tmp=j.with_suffix('.tmp.json');tmp.write_text(json.dumps(data,ensure_ascii=False));tmp.replace(j)
with (W/'continuity.md').open('a') as f:f.write('\n- Added requested Pirateship evaluation plots after50:51 Commit vs CFT (copyid61),52 Commit vs Audit (id62),53 Audit vs BFT (id63),54a–d Recovery (id64–67), all prefixed pirateship-eval-. Original native comparison charts and original recovery plot/reveal masks preserved. Later recovery builds referenced absent bitmap(449338366); embedded the identical first-build plot in each copy. Comparison scripts retained; recovery scripts repaired to describe the plotted stages because original65–67 notes described unrelated HarborMaster/material. Originals remain below divider.125frames/95logical;sentinel55/physical85. Backup revisions/before-pirateship-evaluations. Local only.\n')
print('Added51–53 comparisons and54a–d recovery;125frames/95logical;sentinel55. Artwork, references and original slides verified.')
