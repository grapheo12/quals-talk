"""Copy original Pirateship slides34–59 verbatim, stopping before evaluations."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import hashlib,json,re,shutil
W=Path(__file__).resolve().parent;O='http://xml.openoffice.org/svg/export';S='http://www.w3.org/2000/svg'
p=W/'editable-deck.svg';tree=E.parse(str(p));root=tree.getroot();baseline=E.parse(str(W/'baseline-editable-deck.svg'))
data=json.loads((W/'deck.json').read_text());base_data=json.loads((W/'baseline-deck.json').read_text())
slides=root.xpath('//*[@class="SlideGroup"]')[0];base_slides=baseline.xpath('//*[@class="SlideGroup"]')[0]
base_by_id={w.xpath('.//*[@class="Slide"]')[0].get('id'):(w,m) for w,m in zip(base_slides,base_data)}
source_ids=[f'id{i}' for i in range(34,60)];prefix='pirateship-continuation-'
assert not root.xpath('//*[starts-with(@id,"'+prefix+'")]')
at=next(i for i,m in enumerate(data) if m['title']=='Old slides below');assert at==53
backup=W/'revisions'/'before-pirateship-verbatim-continuation';backup.mkdir(parents=True,exist_ok=True)
for f in ['editable-deck.svg','deck.json']:
 if not (backup/f).exists():shutil.copy2(W/f,backup/f)
ns={'o':O}
base_meta={e.get('{'+O+'}slide'):e for e in baseline.xpath('//*[@id="ooo:meta_slides"]/*') if e.get('{'+O+'}slide')}
base_index={e.get('{'+O+'}slide'):e for e in baseline.xpath('//*[@class="TextShapeIndex"]/*')}
animations={sid:baseline.xpath('//*[@class="Animations" and @o:slide="'+sid+'"]',namespaces=ns) for sid in source_ids}
# One ID map also preserves references that cross original slide boundaries.
mapping={sid:prefix+sid for sid in source_ids}
for sid in source_ids:
 for part in [base_by_id[sid][0]]+animations[sid]:
  mapping.update({e.get('id'):prefix+e.get('id') for e in part.iter() if e.get('id')})
pattern=re.compile(r'(?<![\w.-])('+'|'.join(sorted(map(re.escape,mapping),key=len,reverse=True))+r')(?![\w.-])')
def clone(part):
 result=deepcopy(part)
 for e in result.iter():
  for key,value in list(e.attrib.items()):e.set(key,pattern.sub(lambda m:mapping[m.group(1)],value))
 return result

def artwork_digest(wrapper):
 copy=deepcopy(wrapper)
 for e in copy.xpath('.//*[@class="CustomPageNumber"] | .//*[local-name()="text" and @x="1182" and @y="692"]'):
  e.getparent().remove(e)
 return hashlib.sha256(E.tostring(copy,method='c14n',exclusive=True)).hexdigest()
# Consecutive builds share a number; their titles/artwork/narration remain verbatim.
groups={}
for name,members,title in [
 ('platforms',[35,36],'Platforms: Independent Failure Domains'),
 ('platform-definition',[37,38,39],'What constitutes a platform?'),
 ('cautious-trust',[44,45],'Cautious Trust to rescue'),
 ('cft-execution',[48,49,50],'CFT Protocol Execution'),
 ('bft-execution',[51,52,53],'BFT Protocol Execution'),
 ('embedding',[55,56,57,58],'Embedding BFT in CFT')]:
 for n in members:groups[f'id{n}']={'id':'pirateship-original-'+name,'title':title}
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={e.get('{'+O+'}slide'):e for e in meta if e.get('id','').startswith('ooo:meta_slide_')}
index=root.xpath('//*[@class="TextShapeIndex"]')[0];items={e.get('{'+O+'}slide'):e for e in index}
animation_parent=root.xpath('//*[@id="presentation-animations"]')[0]
expected_art={};copied_animations=[];new_records=[]
for offset,sid in enumerate(source_ids):
 source,source_record=base_by_id[sid];w=clone(source);new_sid=mapping[sid];expected_art[new_sid]=artwork_digest(w)
 m=deepcopy(source_record);m.pop('slideGroup',None);m['section']='Pirateship';m['speakerScript']=re.sub(r'<[^>]*>','',m.get('notes','')).strip()
 if sid in groups:m['slideGroup']=deepcopy(groups[sid])
 if sid=='id44':
  # This original master has no footer. Add only the shared logical page number.
  page=w.xpath('.//*[@class="Page"]')[0]
  e=E.SubElement(page,'{'+S+'}text',{'x':'1182','y':'692','transform':'scale(26.45859375)','font-family':'Rubik','font-size':'14.67','font-weight':'400','text-anchor':'end','fill':'#6B7785','stroke':'none'});e.text='44'
 slides.insert(at+offset,w);data.insert(at+offset,m);new_records.append((new_sid,w,m,source_record))
 records[new_sid]=clone(base_meta[sid]);items[new_sid]=clone(base_index[sid])
 for a in animations[sid]:
  copied=clone(a);animation_parent.append(copied);copied_animations.append((sid,copied,E.tostring(copied,method='c14n',exclusive=True)))
for e in list(meta):
 if e.get('id','').startswith('ooo:meta_slide_'):meta.remove(e)
seen={};number=0
for i,(m,w) in enumerate(zip(data,slides)):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');r=records[sid];r.set('id',f'ooo:meta_slide_{i}');meta.append(r)
 if sid in items:index.append(items[sid])
 m['number']=i+1;build=m.get('slideGroup')
 if not build or build['id'] not in seen:
  number+=1
  if build:seen[build['id']]=number
 logical=seen[build['id']] if build else number;m['displayNumber']=logical
 if build:build['number']=logical
 for e in w.xpath('.//*[local-name()="text" and @x="1182" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(logical)
meta.set('{'+O+'}number-of-slides',str(len(data)))
divider=at+len(source_ids);data[divider]['notes']='Editing divider after logical Slide51 (Ledger-view of Pirateship). Original Pirateship continuation copied verbatim through the last pre-evaluation slide. Evaluation slides remain in the old-slide section.'
ids=root.xpath('//@id');assert len(ids)==len(set(ids));idset=set(ids)
assert len(slides)==len(data)==120 and number==92
assert data[at]['displayNumber']==37 and data[divider-1]['displayNumber']==51 and data[divider]['displayNumber']==52
assert data[divider]['title']=='Old slides below'
for sid,w,m,source_record in new_records:
 assert artwork_digest(w)==expected_art[sid],sid+' artwork changed'
 assert m['title']==source_record['title'] and m['notes']==source_record['notes']
 for value in w.xpath('.//@*'):
  for ref in re.findall(r'url\(#([^)]*)\)',value):assert ref in idset,(sid,ref)
for sid,a,expected in copied_animations:
 assert E.tostring(a,method='c14n',exclusive=True)==expected
 for target in a.xpath('.//@*[local-name()="targetElement"]'):assert target in idset,(sid,target)
assert meta[0].get('id')=='ooo:meta_dummy_slide'
assert [e.get('{'+O+'}slide') for e in list(meta)[1:]]==[w.xpath('.//*[@class="Slide"]')[0].get('id') for w in slides]
manifest=[{'source':sid,'new_id':new_sid,'number':m['displayNumber'],'physical':m['number'],'title':m['title'],'group':m.get('slideGroup',{}).get('id')} for sid,(new_sid,w,m,old) in zip(source_ids,new_records)]
(backup/'copied-slides.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
tree.write(str(p),encoding='utf-8',xml_declaration=True);(W/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
with (W/'continuity.md').open('a') as f:f.write('\n- Verbatim copied original Pirateship slides id34–id59 (26 frames, PFT through Ledger-view, excluding evals) from baseline after36c. Prefix pirateship-continuation- remaps all artwork/animation/text-index IDs; source text, notes and animations preserved byte-for-byte apart from IDs and page numbers. Grouped consecutive platform-domain, platform-definition, Cautious-Trust, CFT-execution, BFT-execution and embedding builds. New logical37–51 (physical54–79), sentinel52/physical80.120frames/92logical. Original reference slides retained below divider, including evaluations. Original id44 restored as its own verbatim copy, while revised36a remains unchanged. Backup and copied-slides.json in revisions/before-pirateship-verbatim-continuation. Local only.\n')
print(f'Copied26 original frames as logical37–51; sentinel52.120frames/92logical. Verified all26 artwork digests, original notes/titles and{len(copied_animations)} animation trees.')
for m in manifest:print(m['physical'],m['number'],m['title'])
