from pathlib import Path
from lxml import etree as E
import copy, json, shutil

R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg'; O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg')); root=t.getroot()
slides=root.xpath('//*[@class="SlideGroup"]')[0]
data=json.loads((R/'deck.json').read_text())
at=next(i for i,x in enumerate(data) if x['title']=='Old slides below')
assert at==11 and len(data)==107
backup=R/'revisions'/'before-cautious-trust-sequence'; backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json','viewer.html']: shutil.copyfile(R/f,backup/f)

def el(p,tag,**a):
 return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
def txt(p,x,y,s,size=26,color='#1F2328',weight=400,anchor='middle'):
 e=el(p,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=s
 return e
def renamed(node,prefix):
 node=copy.deepcopy(node)
 for x in node.iter():
  if x.get('id'): x.set('id',prefix+'-'+x.get('id'))
 return node
def blank(sid,title,num):
 w=E.Element('{'+S+'}g',visibility='hidden')
 c=el(w,'g',id='container-'+sid)
 s=el(c,'g',id=sid,**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
 p=el(s,'g',**{'class':'Page'}); g=el(p,'g',transform='scale(26.45859375)')
 el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
 txt(g,98,119,title,48,weight=700,anchor='start')
 el(g,'rect',x=98,y=140,width=67,height=4.8,fill='#1F5F8B',stroke='none')
 txt(g,1182,692,str(num),14.67,'#6B7785',anchor='end')
 return w,g

new=[]
source=root.xpath('//*[@id="slide-tee-plus-question"]/*[@class="Page"]/*')[0]
for num,sid,title in [(11,'slide-tee-not-bft','We need something more'),(12,'slide-cautious-trust-principle','A new design principle')]:
 w,g=blank(sid,title,num)
 # Stable circle, vendor logos and plus sign across all three builds.
 for child in source:
  if E.QName(child).localname in ['circle','g'] or child.text in ['TEEs','+']:
   g.append(renamed(child,sid))
 if num==11:
  txt(g,640,196,'Starting from an imperfect, incomplete TEE abstraction',26,'#6B7785')
  txt(g,950,366,'Byzantine',39,'#6B7785',500)
  txt(g,950,421,'agreement',39,'#6B7785',500)
  el(g,'path',d='M 784 313 L 1116 459 M 784 459 L 1116 313',fill='none',stroke='#B54740',stroke_width=9,stroke_linecap='round')
  txt(g,640,622,'Full-fledged Byzantine agreement is too costly',28,'#A02B93',500)
  notes="Well we need something more. Clearly, full fledged Byzantine agreement isn't an option."
 else:
  txt(g,640,196,'Preserve the performance and cost benefits of TEEs',26,'#6B7785')
  txt(g,950,370,'Cautious',53,'#A02B93',500)
  txt(g,950,436,'Trust',53,'#A02B93',500)
  notes='I am going to propose a new design principle called Cautious Trust. Let\'s see what that is.'
 new.append((w,sid,title,notes))

# Reuse the original vector ledger, gears, detective and progress arrows.
original=root.xpath('//*[@id="id15"]/*[@class="Page"]')[0]
for num,sid,title in [(13,'slide-cautious-trust-audit','Cautious Trust: Abstract Design'),(14,'slide-cautious-trust-systems','Two systems built on Cautious Trust')]:
 w,g=blank(sid,title,num)
 txt(g,326,237,'Auditor service',27,weight=500)
 txt(g,895,237,'TEE-enabled computation',27,weight=500)
 txt(g,326,274,'Checks for integrity violations',20,'#6B7785')
 txt(g,895,274,'Runs at its own pace',20,'#6B7785')
 diagram=el(g,'g',transform='translate(-165 -80) scale(0.045354331)')
 for child in original:
  if child.get('class')=='Group' or any(child.xpath('.//*[@id="'+i+'"]') for i in ['id419','id420','id421','id422']):
   diagram.append(renamed(child,sid))
 txt(g,589,494,'Audit log',26,weight=500)
 if num==13:
  txt(g,895,523,'No extra checks on the computation path',19,'#6B7785')
  txt(g,640,622,'Compute at full pace. Audit asynchronously.',28,'#A02B93',500)
  notes='In Cautious Trust, we let the TEE-enabled system work at its own pace without any extra checks. The computation leaves behind an audit log. An auditor service consumes this log to look for evidence of integrity violations.'
 else:
  txt(g,408,581,'HarborMaster',37,'#1F5F8B',500)
  txt(g,408,623,'VLDB 2026',23,'#6B7785')
  txt(g,872,581,'Pirateship',37,'#A02B93',500)
  txt(g,872,623,'SOSP 2026',23,'#6B7785')
  notes='I built two systems following this cautious trust principle: HarborMaster (VLDB 2026) and Pirateship (SOSP 2026).'
 new.append((w,sid,title,notes))

meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={x.get('{'+O+'}slide'):x for x in meta if x.get('{'+O+'}slide')}
idx=root.xpath('//*[@class="TextShapeIndex"]')[0]
for j,(w,sid,title,notes) in enumerate(new):
 slides.insert(at+j,w)
 rec=E.Element('{'+S+'}g')
 for k,v in {'slide':sid,'master':'id103','display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():rec.set('{'+O+'}'+k,v)
 records[sid]=rec
 ti=E.Element('{'+S+'}g');ti.set('{'+O+'}slide',sid);ti.set('{'+O+'}id-list','');idx.insert(at+j,ti)
 data.insert(at+j,{'number':at+j+1,'section':'Opening','title':title,'text':' '.join(w.itertext()),'notes':'User script: '+notes+'\n\nVisual: incremental build from the preceding slide; original vector artwork reused.'})
for rec in list(meta):
 if rec.get('{'+O+'}slide') and rec.get('id')!='ooo:meta_dummy_slide':meta.remove(rec)
for i,w in enumerate(slides):
 sid=w.xpath('.//*[@class="Slide"]')[0].get('id');rec=records[sid];rec.set('id',f'ooo:meta_slide_{i}');meta.append(rec)
meta.set('{'+O+'}number-of-slides',str(len(data)))
for i,x in enumerate(data):x['number']=i+1
data[at+4]['notes']='Editing divider after user Slide 14. All slides following this divider are original material awaiting revision. Insert newly dictated slides before this divider. The divider is not a numbered content slide.'
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
v=R/'viewer.html';v.write_text(v.read_text().replace('max="107"','max="111"'))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Added user Slides11–14 (viewer12–15): crossed-out Byzantine agreement; Cautious Trust reveal; original vector abstract audit diagram reused with readable labels; then same diagram plus HarborMaster (VLDB 2026) and Pirateship (SOSP 2026). Original id15 remains below divider as reference. Sentinel now viewer16; total111. Local only.\n')
print('Added user Slides 11–14; total',len(data))
