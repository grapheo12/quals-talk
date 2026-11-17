from pathlib import Path
from lxml import etree as E
import json,shutil
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot();sid='slide-old-slides-divider'
assert not root.xpath(f'//*[@id="{sid}"]')
b=R/'revisions'/'before-old-slides-divider';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
w=E.Element('{'+S+'}g',visibility='hidden')
c=el(w,'g',id='container-old-slides-divider')
sl=el(c,'g',id=sid,**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
p=el(sl,'g',**{'class':'Page'});g=el(p,'g',transform='scale(26.45859375)')
def txt(x,y,s,size=26,color='#6B7785',weight=400,anchor='start'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=s
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
title='Old slides below'
txt(98,119,title,48,'#1F2328',700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill='#1F5F8B',stroke='none')
txt(640,294,'End of revised slides',30,'#A02B93',500,'middle')
el(g,'line',x1=170,y1=350,x2=1110,y2=350,stroke='#D5DDE2',stroke_width=2,stroke_dasharray='8 9')
el(g,'rect',x=598,y=326,width=84,height=105,fill='white',stroke='none')
el(g,'path',d='M640 334V414m-20-20 20 20 20-20',fill='none',stroke='#1F5F8B',stroke_width=4,stroke_linecap='round',stroke_linejoin='round')
txt(640,492,'The remaining slides are from the original deck.',28,'#6B7785',400,'middle')
txt(640,536,'Awaiting revision',22,'#6B7785',400,'middle')
m=json.loads((R/'deck.json').read_text());at=10;n=len(m)+1
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for item in meta:
 if item.get('id','').startswith('ooo:meta_slide_'):
  k=int(item.get('id').rsplit('_',1)[1])
  if k>=at:item.set('id',f'ooo:meta_slide_{k+1}')
record=E.Element('{'+S+'}g',id=f'ooo:meta_slide_{at}')
for k,v in {'slide':sid,'master':'id103','display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():record.set('{'+O+'}'+k,v)
meta.insert(at+1,record);meta.set('{'+O+'}number-of-slides',str(n))
root.xpath('//*[@class="SlideGroup"]')[0].insert(at,w)
idx=E.Element('{'+S+'}g');idx.set('{'+O+'}slide',sid);idx.set('{'+O+'}id-list','')
root.xpath('//*[@class="TextShapeIndex"]')[0].insert(at,idx)
m.insert(at,{'number':at+1,'section':'Old slides','title':title,'text':' '.join(p.itertext()),'notes':'Editing divider after user Slide 9. All slides following this divider are original material awaiting revision. Insert newly dictated slides before this divider so it continues to mark the boundary. The divider is not a numbered content slide.'})
for i,item in enumerate(m):
 item['number']=i+1
 if i>at and item['section']=='Opening':item['section']='Old slides'
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(m,ensure_ascii=False))
v=R/'viewer.html';v.write_text(v.read_text().replace(f'max="{n-1}"',f'max="{n}"'))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Inserted unnumbered sentinel slide-old-slides-divider after user Slide9 (viewer11); total106. "Old slides below" / "End of revised slides". All subsequent slides await revision. Insert newly dictated slides BEFORE this divider and keep it marking the revised/original boundary. Local only.\n')
print('Inserted divider at viewer 11; total',n)
