"""Restore the original final three slides after rereading the source PPTX."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import json,re,shutil,zipfile
W=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export';S='http://www.w3.org/2000/svg'
p=W/'editable-deck.svg';tree=E.parse(str(p));r=tree.getroot();base=E.parse(str(W/'baseline-editable-deck.svg'));d=json.loads((W/'deck.json').read_text());bd=json.loads((W/'baseline-deck.json').read_text());slides=r.xpath('//*[@class="SlideGroup"]')[0]
assert len(slides)==len(d)==84
backup=W/'revisions'/'before-restoring-next-steps';backup.mkdir(parents=True,exist_ok=True)
for f in ['editable-deck.svg','deck.json']:
 if not (backup/f).exists():shutil.copy2(W/f,backup/f)
# Confirm the preserved conversion corresponds to the user-supplied originals.
with zipfile.ZipFile('/Users/shubham_mishra/Documents/Quals Talk Local.pptx') as z,zipfile.ZipFile(W.parent/'source/Quals Talk Local.pptx') as old:
 for n in [98,99,100]:
  name=f'ppt/slides/slide{n}.xml';assert z.read(name)==old.read(name)
prefix='next-steps-restored-';parts=[]
for n in [98,99,100]:
 sid=f'id{n}';source=base.xpath('//*[@class="SlideGroup"]/*[.//*[@class="Slide" and @id="'+sid+'"]]')[0]
 a=base.xpath('//*[@class="Animations" and @ooo:slide="'+sid+'"]',namespaces={'ooo':O});parts.append((n,sid,source,a))
mapping={e.get('id'):prefix+e.get('id') for n,sid,w,aa in parts for part in [w]+aa for e in part.iter() if e.get('id')}
pat=re.compile(r'(?<![\w.-])('+'|'.join(sorted(map(re.escape,mapping),key=len,reverse=True))+r')(?![\w.-])')
def clone(el):
 c=deepcopy(el)
 for e in c.iter():
  for k,v in list(e.attrib.items()):e.set(k,pat.sub(lambda m:mapping[m[1]],v))
 return c
meta=r.xpath('//*[@id="ooo:meta_slides"]')[0];idx=r.xpath('//*[@class="TextShapeIndex"]')[0];ap=r.xpath('//*[@id="presentation-animations"]')[0];before=[E.tostring(w) for w in slides]
for offset,(n,sid,w,aa) in enumerate(parts):
 c=clone(w);page=c.xpath('.//*[@class="Page"]')[0];num=55+offset
 footer=E.SubElement(page,'{'+S+'}text',{'x':'1182','y':'692','transform':'scale(26.45859375)','font-family':'Rubik','font-size':'14.67','font-weight':'400','text-anchor':'end','fill':'#6B7785','stroke':'none'});footer.text=str(num)
 slides.append(c);m=deepcopy(bd[n-1]);m.update(number=85+offset,displayNumber=num,speakerScript='');d.append(m)
 mr=clone(base.xpath('//*[@id="ooo:meta_slides"]/*[@ooo:slide="'+sid+'"]',namespaces={'ooo':O})[0]);mr.set('id',f'ooo:meta_slide_{84+offset}');meta.append(mr)
 for e in base.xpath('//*[@class="TextShapeIndex"]/*[@ooo:slide="'+sid+'"]',namespaces={'ooo':O}):idx.append(clone(e))
 for a in aa:ap.append(clone(a))
meta.set('{'+O+'}number-of-slides','87')
assert [E.tostring(w) for w in list(slides)[:84]]==before
ids=r.xpath('//@id');assert len(ids)==len(set(ids));idset=set(ids)
for w in list(slides)[84:]:
 for e in w.iter():
  for v in e.attrib.values():
   for ref in re.findall(r'url\(#([^)]*)\)',v):assert ref in idset,ref
  if E.QName(e).localname=='use':assert e.get('{http://www.w3.org/1999/xlink}href','')[1:] in idset
assert len(slides)==len(d)==87 and d[-1]['displayNumber']==57
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]]==[w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
tmp=p.with_suffix('.tmp.svg');tree.write(str(tmp),encoding='utf-8',xml_declaration=True);tmp.replace(p)
j=W/'deck.json';tmp=j.with_suffix('.tmp.json');tmp.write_text(json.dumps(d,ensure_ascii=False));tmp.replace(j)
with (W/'continuity.md').open('a') as f:f.write('\n- Reread original user PPTX and restored its final slides98–100 starting Where do we go now? as new55–57 (physical85–87). Source XML matches preserved source exactly. Reused original editable conversion/image, native project timeline and transactional model, with unique next-steps-restored- IDs; added consistent numbered footers. Originals have no speaker notes, so no script invented.57logical/87physical; all prior84frames unchanged. Backup revisions/before-restoring-next-steps. Local only.\n')
print('Restored original98–100 as55–57;57logical/87physical. Original artwork and prior slides preserved.')
