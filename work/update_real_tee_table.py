from pathlib import Path
from lxml import etree as E
import json, shutil, copy
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
b=R/'revisions'/'before-real-tee-table';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
sl=root.xpath('//*[@id="id9"]')[0]
page=sl.find('{'+S+'}g[@class="Page"]')
table=copy.deepcopy(page.find('{'+S+'}g[@class="com.sun.star.drawing.TableShape"]'))
assert table is not None
page.clear();page.set('class','Page')
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
g=el(page,'g',transform='scale(26.45859375)')
blue='#1F5F8B';ink='#1F2328';gray='#6B7785';purple='#A02B93'
def txt(parent,x,y,text,size=24,color=ink,weight=400,anchor='start'):
 e=el(parent,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
title='What can we expect from real TEEs?'
txt(g,98,119,title,48,weight=700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
wrap=el(page,'g',transform='translate(0 2122)');wrap.append(table)
changes={'Ideal TEEs':'TEE claims','Real TEEs':'Real TEEs','Memory integrity':'Execution integrity','Disk integrity':'Memory integrity','Execution integrity':'Persistent-state integrity'}
for e in table.iter():
 if e.text in changes:
  e.text=changes[e.text]
  for a in ['textLength','lengthAdjust']:e.attrib.pop(a,None)
  if e.text in ['TEE claims','Real TEEs']:
   e.getparent().set('x','20857' if e.text=='TEE claims' else '27986')
   e.set('text-anchor','middle');e.set('font-weight','500')
  if e.text=='Persistent-state integrity':e.set('fill',purple);e.set('font-weight','500')
marks=[e for e in table.iter() if e.tag=='{'+S+'}text' and e.text in ['✅','❌','🎭']]
for e,value in zip(marks,['✅','🎭','✅','🎭','❌','❌']):
 e.text=value
 if value=='🎭':
  y=float(e.get('y'));e.set('font-size','900');e.set('y',str(y-300))
  txt(e.getparent(),e.get('x'),y+200,'Conditional',450,purple,500,'middle')
txt(g,640,610,'Integrity holds while the TEE remains uncompromised',26,purple,500,'middle')
txt(g,640,649,'Exploitation is difficult; many attacks require physical access.',22,gray,anchor='middle')
txt(g,1182,692,'9',14.67,gray,anchor='end')
slides=root.xpath('//*[@class="SlideGroup"]')[0]
wrapper=sl.getparent().getparent();old_index=list(slides).index(wrapper)
assert old_index==13,old_index
slides.remove(wrapper);slides.insert(9,wrapper)
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
for i,w in enumerate(slides):
 sid=w.find('.//{'+S+'}g[@class="Slide"]').get('id')
 m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
m=records['id9']
for k,v in {'display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
for a in root.xpath('//*[@id="id9-animations"]'):
 for child in list(a):a.remove(child)
for idx in root.xpath('//*[@class="TextShapeIndex"]/*'):
 if idx.get('{'+O+'}slide')=='id9':idx.set('{'+O+'}id-list','')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text());record=manifest.pop(old_index)
record.update(title=title,text=' '.join(page.itertext()),notes='''<reuse the table> So what guarantee do "Real" TEEs provide? Well the execution and memory integrity depends on whether there is a zero-day attack and if TEEs are actively being compromised. This is still very hard. Many of the attacks need physical access.''')
manifest.insert(9,record)
for i,r in enumerate(manifest):r['number']=i+1
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- User Slide9 reuses real-TEE table id9, moved viewer14→viewer10; total105. Same ordered rows as Slide7, TEE claims and Real TEEs columns. Original mask icons retained at natural aspect with explicit “Conditional” labels for execution/memory; persistent-state cross in both columns. Takeaways emphasize uncompromised TEE and difficult exploitation/physical access.\n')
print('Updated Slide 9; total105')
