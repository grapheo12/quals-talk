from pathlib import Path
from lxml import etree as E
import json,re,shutil
R=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));r=t.getroot();data=json.loads((R/'deck.json').read_text());slides=r.xpath('//*[@class="SlideGroup"]')[0]
assert len(data)==115
remove=[i for i,s in enumerate(data) if 23<=s.get('displayNumber',0)<=37];assert len(remove)==15
b=R/'revisions'/'before-removing-slides-23-37';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
removed=[{'number':data[i]['displayNumber'],'title':data[i]['title'],'id':slides[i].xpath('.//*[@class="Slide"]')[0].get('id')} for i in remove]
(b/'removed-slides.json').write_text(json.dumps(removed,indent=2))
def broken_refs():
 ids=set(r.xpath('//@id'));refs=set()
 for e in r.iter():
  for k,v in e.attrib.items():
   local=k.split('}')[-1]
   if local in ['targetElement','slide','master']:refs.add(v)
   if local=='href' and v.startswith('#'):refs.add(v[1:])
   refs.update(re.findall(r'url\(#([^)]*)\)',v))
 return refs-ids
before=broken_refs();removed_ids={s['id'] for s in removed}
for i in reversed(remove):slides.remove(slides[i]);data.pop(i)
meta=r.xpath('//*[@id="ooo:meta_slides"]')[0]
records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
for node in list(r.xpath('//*[@class="Animations"]')):
 if node.get('{'+O+'}slide') in removed_ids:node.getparent().remove(node)
idx=r.xpath('//*[@class="TextShapeIndex"]')[0]
for node in list(idx):
 if node.get('{'+O+'}slide') in removed_ids:idx.remove(node)
seen={};n=0
for i,(record,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
 record['number']=i+1;group=record.get('slideGroup')
 if not group or group['id'] not in seen:
  n+=1
  if group:seen[group['id']]=n
 number=seen[group['id']] if group else n;record['displayNumber']=number
 if group:group['number']=number
 for e in w.xpath('.//*[local-name()="text" and @y="692" and @x="1182"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(number)
meta.set('{'+O+'}number-of-slides',str(len(data)))
assert len(data)==len(slides)==100 and n==97
assert data[24]['title']=='Old slides below' and data[25]['title']=='Pirateship' and data[25]['displayNumber']==23
assert meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(slides):assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
assert not (broken_refs()-before),broken_refs()-before
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True);(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Removed the then-current logical Slides23–37 inclusive at user request (15 original slides from TEE application popularity through At a glance (2)). Recoverable backup and title list in revisions/before-removing-slides-23-37. Divider stays22; Pirateship now23. 100 physical frames/97 logical slides. Remaining animation/metadata references validated. Local only.\n')
print('Removed 15 slides. 97 logical slides /100 frames. Pirateship is now23.')
