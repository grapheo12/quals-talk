from pathlib import Path
from lxml import etree as E
from datetime import date
import json, shutil
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
p=root.xpath('//*[@id="slide-tee-vulnerability-timeline"]/*[@class="Page"]')[0]
g=p[0]
b=R/'revisions'/'before-single-tee-timeline';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
# Retain the title, subtitle, citations and footer; replace only the timeline.
for e in list(g):
 y=float(e.get('y',e.get('y1',e.get('cy','-1'))))
 if 240<=y<=622:g.remove(e)
def el(tag,**a):return E.SubElement(g,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
gray='#6B7785';red='#A76B65';teal='#169C9A'
def txt(x,y,s,size=20,color=gray,weight=400):
 e=el('text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor='middle',fill=color,stroke='none');e.text=s
def line(a,z,y,color,width=2):el('line',x1=a,y1=y,x2=z,y2=y,stroke=color,stroke_width=width)
y=370
line(130,1150,y,'#DFE4E8')
el('path',d='M1143 364l8 6-8 6',fill='none',stroke='#DFE4E8',stroke_width=2)
rows=[('LVI¹',180,'2019-04-04','2020-03-10','4 Apr 2019 → 10 Mar 2020','Discovery → patch available'),
      ('SmashEx²',633,'2021-05-03','2021-07-13','3 May 2021 → 13 Jul 2021','Private report → patch available'),
      ('BadRAM³',870,'2024-02-26','2024-10-01','26 Feb 2024 → 1 Oct 2024','Private report → patch available')]
for name,a,start,end,dates,labels in rows:
 z=a+(date.fromisoformat(end)-date.fromisoformat(start)).days*.8
 mid=(a+z)/2
 txt(mid,294,name,22)
 txt(mid,344,'Vulnerable',19,red)
 line(a,z,y,red,6)
 for x,c in [(a,gray),(z,teal)]:el('circle',cx=x,cy=y,r=5,fill=c,stroke='white',stroke_width=1)
 txt(mid,432,dates,18)
 txt(mid,462,labels,15)
for x in [542,780]:
 el('rect',x=x-12,y=y-8,width=24,height=16,fill='white',stroke='none')
 el('path',d=f'M{x-8} {y+6}l7 -12m1 12l7 -12',fill='none',stroke='#BBC3CA',stroke_width=2)
txt(640,570,'Execution and memory integrity can fail during these windows',26,'#A02B93',500)
for e in g:
 if e.tag=='{'+S+'}text' and e.get('y')=='661':
  e.text='Intervals to scale; gaps compressed. Patch availability does not imply deployment.'
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
m=json.loads((R/'deck.json').read_text());m[8]['text']=' '.join(p.itertext())
m[8]['notes']=m[8]['notes'].replace('Bars share a days-since-start scale; calendar dates are printed at endpoints.','Intervals appear consecutively on one chronological timeline. Vulnerable segment lengths share a common scale (0.8 px/day), while gaps between studies are compressed and marked with axis breaks. Calendar date ranges appear below each segment.')
(R/'deck.json').write_text(json.dumps(m,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Slide8 now has one chronological line, LVI → SmashEx → BadRAM. Vulnerable durations proportional, inter-study gaps compressed with breaks; date ranges below each interval.\n')
print('Slide 8: single chronological timeline.')
