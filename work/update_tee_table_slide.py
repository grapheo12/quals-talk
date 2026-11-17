from pathlib import Path
from lxml import etree as E
import json, shutil, copy
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
b=R/'revisions'/'before-tee-table-slide';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
sl=root.xpath('//*[@id="id7"]')[0]
page=sl.find('{'+S+'}g[@class="Page"]')
table=copy.deepcopy(page.find('{'+S+'}g[@class="com.sun.star.drawing.TableShape"]'))
assert table is not None
page.clear();page.set('class','Page')
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
g=el(page,'g',transform='scale(26.45859375)')
blue='#1F5F8B';ink='#1F2328';gray='#6B7785';purple='#A02B93'
def txt(p,x,y,text,size=24,color=ink,weight=400,anchor='start'):
 e=el(p,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
title='What do TEEs actually protect?'
txt(g,98,119,title,48,weight=700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
# Retain the source table's cell geometry, blue header, alternating fills, and check/cross style.
wrap=el(page,'g',transform='translate(951 0)');wrap.append(table)
changes={'Ideal TEEs':'TEE claims','Memory integrity':'Execution integrity','Disk integrity':'Memory integrity','Execution integrity':'Persistent-state integrity'}
for e in table.iter():
 if e.text in changes:
  e.text=changes[e.text]
  for a in ['textLength','lengthAdjust']:e.attrib.pop(a,None)
  if e.text=='TEE claims':
   e.getparent().set('x','23459');e.set('text-anchor','middle');e.set('font-weight','500')
  if e.text=='Persistent-state integrity':e.set('fill',purple);e.set('font-weight','500')
marks=[e for e in table.iter() if e.tag=='{'+S+'}text' and e.text in ['✅','❌']]
for e,value in zip(marks,['✅','✅','❌']):e.text=value
txt(g,640,624,'Persistent state needs additional protection',28,purple,500,'middle')
txt(g,1182,692,'7',14.67,gray,anchor='end')
# Move the original table forward into the dictated sequence, rather than duplicate it.
slides=root.xpath('//*[@class="SlideGroup"]')[0]
wrapper=sl.getparent().getparent()
old_index=list(slides).index(wrapper)
assert old_index==10,old_index
slides.remove(wrapper);slides.insert(7,wrapper)
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
records={m.get('{'+O+'}slide'):m for m in meta if m.get('id','').startswith('ooo:meta_slide_')}
for m in records.values():meta.remove(m)
for i,w in enumerate(slides):
 sid=w.find('.//{'+S+'}g[@class="Slide"]').get('id')
 m=records[sid];m.set('id',f'ooo:meta_slide_{i}');meta.append(m)
m=records['id7']
for k,v in {'display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
for a in root.xpath('//*[@id="id7-animations"]'):
 for child in list(a):a.remove(child)
for idx in root.xpath('//*[@class="TextShapeIndex"]/*'):
 if idx.get('{'+O+'}slide')=='id7':idx.set('{'+O+'}id-list','')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text())
record=manifest.pop(old_index)
record.update(title=title,text=' '.join(page.itertext()),notes='''<Reuse table from below> Let's closely examine what TEEs afford us. Well they "claim" to protect execution and memory integrity. However, they still lack protection against tampering of persistent state.''')
manifest.insert(7,record)
for i,r in enumerate(manifest):r['number']=i+1
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- User Slide 7 reuses original ideal-TEE table id7, moved from viewer11 to viewer8 (no duplication; total104). Title “What do TEEs actually protect?” Header “TEE claims”; execution✅, memory✅, persistent-state integrity❌; purple takeaway “Persistent state needs additional protection”. Original table fills, geometry, symbols retained. Old animations cleared.\n')
print('Reused table as Slide 7; 104 slides')
