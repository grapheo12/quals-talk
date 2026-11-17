from pathlib import Path
from lxml import etree as E
import json, shutil
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg'; O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg')); root=t.getroot()
data=json.loads((R/'deck.json').read_text())
sid='slide-harbormaster-section'
assert not root.xpath(f'//*[@id="{sid}"]')
b=R/'revisions'/'before-harbormaster-section';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
w=E.Element('{'+S+'}g',visibility='hidden')
c=el(w,'g',id='container-harbormaster-section')
sl=el(c,'g',id=sid,**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
p=el(sl,'g',**{'class':'Page'});g=el(p,'g',transform='scale(26.45859375)')
def txt(x,y,text,size=40,color='#1F2328',weight=400,anchor='start'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
txt(98,282,'HarborMaster',76,weight=700)
el(g,'rect',x=98,y=312,width=480,height=5,fill='#1F5F8B',stroke='none')
e=txt(98,410,'detects',42,'#A02B93',700)
el(e,'tspan',fill='#1F2328',font_weight=400).text=' integrity violations'
e=txt(98,474,'in ',42)
el(e,'tspan',fill='#1F5F8B',font_weight=700).text='persistent storage'
el(e,'tspan').text='.'
txt(1182,692,'13',14.67,'#6B7785',anchor='end')
at=next(i for i,s in enumerate(data) if s['title']=='Old slides below')
assert at==15
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for rec in meta:
 if rec.get('id','').startswith('ooo:meta_slide_'):
  n=int(rec.get('id').rsplit('_',1)[1])
  if n>=at:rec.set('id',f'ooo:meta_slide_{n+1}')
rec=E.Element('{'+S+'}g',id=f'ooo:meta_slide_{at}')
for k,v in {'slide':sid,'master':'id103','display-name':'HarborMaster','master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():rec.set('{'+O+'}'+k,v)
meta.insert(at+1,rec);meta.set('{'+O+'}number-of-slides',str(len(data)+1))
wrappers=root.xpath('//*[@class="SlideGroup"]')[0];wrappers.insert(at,w)
idx=el(E.Element('{'+S+'}g'),'g');idx.set('{'+O+'}slide',sid);idx.set('{'+O+'}id-list','');root.xpath('//*[@class="TextShapeIndex"]')[0].insert(at,idx)
script="Let's first talk about HarborMaster. HarborMaster detects integrity violations in persistent storage."
data.insert(at,{'number':at+1,'displayNumber':13,'section':'HarborMaster','title':'HarborMaster','text':'HarborMaster detects integrity violations in persistent storage.','speakerScript':script,'notes':script+'\n\nVisual direction: New section title. Bold and color “detects” and “persistent storage”.'})
data[at+1]['notes']='Editing divider after logical Slide 13 (HarborMaster section title). All following slides are original material awaiting revision. Insert new content before this divider.'
seen={};n=0
for i,(s,w) in enumerate(zip(data,wrappers)):
 s['number']=i+1;group=s.get('slideGroup')
 if not group or group['id'] not in seen:
  n+=1
  if group:seen[group['id']]=n
 number=seen[group['id']] if group else n;s['displayNumber']=number
 if group:group['number']=number
 for e in w.xpath('.//*[local-name()="text" and @y="692"] | .//*[@class="CustomPageNumber"]//*[local-name()="text"]'):e.text=str(number)
assert len(data)==112 and n==109
assert data[15]['displayNumber']==13 and data[16]['displayNumber']==14
assert meta[0].get('id')=='ooo:meta_dummy_slide'
for i,w in enumerate(wrappers):
 assert meta[i+1].get('id')==f'ooo:meta_slide_{i}'
 assert meta[i+1].get('{'+O+'}slide')==w.xpath('.//*[@class="Slide"]')[0].get('id')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Logical Slide13 added: HarborMaster section title, slide-harbormaster-section, physical viewer16. Large Rubik title with long blue underline; detects bold purple, persistent storage bold blue. Exact narration in speakerScript. Divider now logical14/viewer17;109 logical slides/112 frames. Local only.\n')
print('Added HarborMaster section as logical Slide 13; 109 slides / 112 frames.')
