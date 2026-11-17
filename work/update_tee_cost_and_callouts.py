from pathlib import Path
from lxml import etree as E
import json, shutil, copy
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export';X='http://www.w3.org/1999/xlink'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
b=R/'revisions'/'before-tee-cost-and-callouts';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
blue='#1F5F8B';teal='#169C9A';ink='#1F2328';gray='#6B7785'
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
def txt(g,x,y,text,size=24,color=ink,weight=400,anchor='start'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
# Replace the stretched original pills with unscaled, quiet callout panels.
tee=root.xpath('//*[@id="id2"]')[0]
g=tee.find('.//{'+S+'}g[@transform="scale(26.45859375)"]')
for shape in list(g):
 if shape.xpath('.//*[@class="com.sun.star.drawing.CustomShape"]'):g.remove(shape)
for x,label in [(140,'Execution integrity'),(790,'Memory confidentiality')]:
 el(g,'rect',x=x,y=554,width=350,height=68,rx=10,fill='#F6F8FA',stroke=blue,stroke_width=2.5)
 txt(g,x+175,597,label,25,blue,500,'middle')
# Reuse Slide 4's graph at identical coordinates in the existing overhead slide.
source=root.xpath('//*[@id="slide-security-cost"]')[0]
page=copy.deepcopy(source.find('{'+S+'}g[@class="Page"]'))
target=root.xpath('//*[@id="id3"]')[0]
for child in list(target):target.remove(child)
target.append(page)
title='TEEs offer a lower-cost defence'
page.set('{'+O+'}name',title)
g=page.find('{'+S+'}g')
for text in g.findall('{'+S+'}text'):
 if text.text=='Stronger integrity comes at a cost':text.text=title
 if text.text=='4' and text.get('y')=='692':text.text='6'
# New highlighted point; it remains a qualitative comparison, not a measured security scale.
el(g,'circle',cx=823,cy=500,r=23,fill='#EAF6F5',stroke='none')
el(g,'circle',cx=823,cy=500,r=14,fill='white',stroke=blue,stroke_width=3)
el(g,'circle',cx=823,cy=500,r=8,fill=blue,stroke='none')
txt(g,860,448,'TEEs',30,blue,700)
txt(g,860,489,'<10%',38,teal,700)
txt(g,860,520,'Memory-suite overhead¹',19,gray)
txt(g,860,546,'SEV-SNP 7.29% · TDX 4.06%',17,gray)
txt(g,300,187,'Defence in depth against a malicious cloud provider',22,gray)
a=el(g,'a');a.set('{'+X+'}href','https://syssec.dpss.inesc-id.pt/papers/misono_sigmetrics25.pdf');a.set('target','_blank')
txt(a,385,692,'1. Misono et al., Confidential VMs Explained (2024), §4.3',13,gray)
meta=root.xpath('//*[@id="ooo:meta_slide_6"]')[0]
for k,v in {'display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():meta.set('{'+O+'}'+k,v)
for a in root.xpath('//*[@id="id3-animations"]'):
 for child in list(a):a.remove(child)
for idx in root.xpath('//*[@class="TextShapeIndex"]/*'):
 if idx.get('{'+O+'}slide')=='id3':idx.set('{'+O+'}id-list','')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text())
manifest[5]['text']=' '.join(tee.itertext())
script='''<Reuse the slide 4 graph> So developers have started using TEEs as an alternative approach for defence-in-depth against malicious cloud providers at a lower cost than full-fledged Byzantine agreement. In fact, a recent paper measured that the cost of running TEEs is within 10% of the unprotected application.'''
notes=script+'''\n\nMeasurement scope: The paper used in the original overhead slide is Misono et al., Confidential VMs Explained: An Empirical Analysis of AMD SEV-SNP and Intel TDX, POMACS December 2024 / SIGMETRICS 2025. Section 4.3, Takeaway 3 reports 7.29% and 4.06% overhead for the Phoronix Memory Test Suite. The slide's <10% callout applies to these aggregate memory-suite results, not every application or monetary cloud pricing. The paper reports higher overhead for some application and I/O workloads. The scatterplot placement is conceptual; TEEs and Byzantine replication have different trust assumptions and protection scopes.\nSource: https://syssec.dpss.inesc-id.pt/papers/misono_sigmetrics25.pdf'''
manifest[6].update(title=title,text=' '.join(page.itertext()),notes=notes)
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- User Slide 5 pill fix: replaced stretched source capsules with 350×68 softly rounded panels, 25px Rubik, thin blue outlines.\n- User Slide 6 replaces original overhead slide id3 (viewer7) with Slide4 graph at identical coordinates, adding low-cost TEE point and <10% memory-suite overhead callout (AMD7.29%, Intel4.06%). Paper verified; workload scope explicit, citation linked and notes explain exceptions. Total104.\n')
print('Updated slides 5 and 6')
