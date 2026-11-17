from pathlib import Path
from lxml import etree as E
import json,shutil,copy
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot();sid='slide-tee-plus-question'
assert not root.xpath(f'//*[@id="{sid}"]')
b=R/'revisions'/'before-tee-question';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
logos=[copy.deepcopy(x[0]) for x in root.xpath('//*[@id="id2"]/*[@class="Page"]/*/*[@transform]')]
assert len(logos)==2
for i,logo in enumerate(logos):
 for e in logo.iter():
  if e.get('id'):e.set('id','question-logo-'+str(i)+'-'+e.get('id'))
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
w=E.Element('{'+S+'}g',visibility='hidden');c=el(w,'g',id='container-tee-plus-question')
sl=el(c,'g',id=sid,**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
p=el(sl,'g',**{'class':'Page'});g=el(p,'g',transform='scale(26.45859375)')
def txt(x,y,s,size=26,color='#1F2328',weight=400,anchor='middle'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=s
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
title='How do we build safe, fast systems?'
txt(98,119,title,48,weight=700,anchor='start')
el(g,'rect',x=98,y=140,width=67,height=4.8,fill='#1F5F8B',stroke='none')
txt(640,196,'Starting from an imperfect, incomplete TEE abstraction',26,'#6B7785')
el(g,'circle',cx=430,cy=391,r=166,fill='white',stroke='#1F5F8B',stroke_width=3)
txt(430,364,'TEEs',68,'#1F5F8B',500)
# Original vendor artwork, scaled uniformly to preserve its proportions.
for logo,x,y,width,bx,by,bw in [(logos[0],329,407,66,10594,7087,2516),(logos[1],427,416,116,13970,7535,4927)]:
 wrap=el(g,'g',transform=f'translate({x} {y}) scale({width/bw}) translate({-bx} {-by})');wrap.append(logo)
txt(686,426,'+',96,'#1F5F8B',400)
txt(885,465,'?',192,'#A02B93',500)
txt(640,622,'Preserve the performance and cost benefits of TEEs',28,'#A02B93',500)
txt(1182,692,'10',14.67,'#6B7785',anchor='end')
m=json.loads((R/'deck.json').read_text())
at=next(i for i,r in enumerate(m) if r['title']=='Old slides below');n=len(m)+1
assert at==10
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for item in meta:
 if item.get('id','').startswith('ooo:meta_slide_'):
  k=int(item.get('id').rsplit('_',1)[1])
  if k>=at:item.set('id',f'ooo:meta_slide_{k+1}')
record=E.Element('{'+S+'}g',id=f'ooo:meta_slide_{at}')
for k,v in {'slide':sid,'master':'id103','display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():record.set('{'+O+'}'+k,v)
meta.insert(at+1,record);meta.set('{'+O+'}number-of-slides',str(n))
root.xpath('//*[@class="SlideGroup"]')[0].insert(at,w)
idx=E.Element('{'+S+'}g');idx.set('{'+O+'}slide',sid);idx.set('{'+O+'}id-list','');root.xpath('//*[@class="TextShapeIndex"]')[0].insert(at,idx)
m.insert(at,{'number':at+1,'section':'Opening','title':title,'text':' '.join(p.itertext()),'notes':'User script: So how do we build safe high performance systems with this leaky incomplete abstraction of a TEE, while preserving the performance and cost characteristics?\n\nVisual direction: TEEs (with company logos in a circle) + ? in big size. Reuses the original AMD and Intel artwork.\n'})
m[at+1]['notes']='Editing divider after user Slide 10. All slides following this divider are original material awaiting revision. Insert newly dictated slides before this divider so it continues to mark the boundary. The divider is not a numbered content slide.'
for i,item in enumerate(m):item['number']=i+1
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(m,ensure_ascii=False))
v=R/'viewer.html';v.write_text(v.read_text().replace(f'max="{n-1}"',f'max="{n}"'))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- User Slide10 inserted before sentinel as viewer11, slide-tee-plus-question. Large blue circle containing TEEs + original AMD/Intel logos, blue plus, purple question mark. Preserve performance/cost takeaway. Sentinel now viewer12; total107. Local edits only.\n')
print('Added user Slide 10; sentinel viewer 12; total',n)
