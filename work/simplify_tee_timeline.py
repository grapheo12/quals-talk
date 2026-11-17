from pathlib import Path
from lxml import etree as E
from datetime import date
import json, shutil
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg'; O='http://xml.openoffice.org/svg/export'; X='http://www.w3.org/1999/xlink'
t=E.parse(str(R/'editable-deck.svg')); root=t.getroot()
sid='slide-tee-vulnerability-timeline'
page=root.xpath(f'//*[@id="{sid}"]/*[@class="Page"]')[0]
b=R/'revisions'/'before-simplified-tee-timeline'; b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']: shutil.copyfile(R/f,b/f)
page.clear(); page.set('class','Page')
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
g=el(page,'g',transform='scale(26.45859375)')
blue='#1F5F8B';ink='#1F2328';gray='#6B7785';red='#A76B65';teal='#169C9A'
def txt(x,y,text,size=24,color=ink,weight=400,anchor='start',parent=None):
 e=el(g if parent is None else parent,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
def line(x1,y1,x2,y2,color,width=1,**a):return el(g,'line',x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=width,**a)
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
title='TEE integrity is not unconditional'
txt(98,119,title,48,weight=700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
txt(98,199,'A vulnerability leaves a window before a patch is available.',26)
left=340; span=780
for days,label in [(0,'0'),(90,'90'),(180,'180'),(270,'270'),(360,'360 days')]:
 x=left+span*days/360
 txt(x,264,label,16,gray,anchor='middle')
 line(x,279,x,565,'#EDF0F2',1)
rows=[('LVI¹','2019-04-04','2020-03-10','Discovered 4 Apr 2019','10 Mar 2020',315),
      ('SmashEx²','2021-05-03','2021-07-13','Reported 3 May 2021','13 Jul 2021',420),
      ('BadRAM³','2024-02-26','2024-10-01','Reported 26 Feb 2024','1 Oct 2024',525)]
for name,start,end,begin_label,end_label,y in rows:
 days=(date.fromisoformat(end)-date.fromisoformat(start)).days
 z=left+span*days/360
 txt(98,y+7,name,22,gray)
 line(left,y,1120,y,'#DFE4E8',2)
 line(left,y,z,y,red,6)
 el(g,'circle',cx=left,cy=y,r=5,fill=gray,stroke='white',stroke_width=1)
 el(g,'circle',cx=z,cy=y,r=5,fill=teal,stroke='white',stroke_width=1)
 txt((left+z)/2,y-17,'Vulnerable',19,red,anchor='middle')
 txt(left,y+30,begin_label,15,gray)
 txt(z,y+52,end_label+' · patch available',15,gray,anchor='middle')
txt(640,622,'Execution and memory integrity can fail during this window',26,'#A02B93',500,'middle')
txt(98,661,'Time since discovery / private report. Patch availability does not imply deployment.',14,gray)
for xx,label,url in [(98,'1. LVI · S&P 2020','https://lviattack.eu/lvi.pdf'),(365,'2. SmashEx · CCS 2021','https://www.shwetashinde.org/publications/smashex_ccs21.pdf'),(696,'3. BadRAM · S&P 2025','https://badram.eu/badram.pdf')]:
 a=el(g,'a');a.set('{'+X+'}href',url);a.set('target','_blank');txt(xx,694,label,12,gray,parent=a)
txt(1182,692,'8',14.67,gray,anchor='end')
manifest=json.loads((R/'deck.json').read_text()); record=manifest[8]
script=record['notes'].split('\n\nResearch scope:')[0]
record.update(title=title,text=' '.join(page.itertext()),notes=script+'''

Revision: replace Battering RAM and DDRop with LVI and SmashEx. Keep the figure understated: no logos, attack descriptions, platform lists, or prominent vulnerability branding. Bars share a days-since-start scale; calendar dates are printed at endpoints.

LVI: the authors explicitly date first discovery and reporting to 4 April 2019. Intel released SGX SDK/PSW mitigations on 10 March 2020, 341 days later. This is software mitigation availability, not a hardware root-cause fix or completed ecosystem deployment. Developers must rebuild/harden affected enclave code; attestation recovery is separate. LVI hijacks transient execution and leaks secrets; it should not be described as arbitrary persistent architectural memory modification.
Paper: https://lviattack.eu/lvi.pdf
Discovery: https://lviattack.eu/ (Who is behind LVI?)
Patch: https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00334.html (initial release 10 March 2020; Recommendations explicitly say SDK/PSW available today).

SmashEx: ETH Zurich dates discovery to early May 2021, without an exact day. Paper section 11 specifies private reports to Intel and Microsoft on 3 May 2021 and patches released 13 July 2021. Timeline uses the exact private-report date, a 71-day interval; do not relabel it as an exact discovery day. These are SGX runtime software patches (Intel SGX SDK / Microsoft Open Enclave), not CPU microcode. A malicious OS can exploit affected enclave exception handling to compromise memory and execution integrity.
Paper: https://www.shwetashinde.org/publications/smashex_ccs21.pdf (section 11, page 13)
Discovery: https://ethz.ch/en/news-and-events/eth-news/news/2021/10/vulnerability-discovered-in-intel.html
Project: https://jasonyu1996.github.io/SmashEx/

BadRAM retained: exact discovery date is not published in the checked sources. Reported to AMD 26 February 2024 (paper section 1, Responsible Disclosure). Complete required vendor firmware combination dated 1 October 2024, 218 days later, per AMD-SB-3015. Earlier PI releases: Milan 11 July / Genoa 20 August 2024; required SEV firmware 1.55.22 or 1.55.38 dated 1 October. Public disclosure was 10 December 2024. End is vendor firmware availability to OEMs, not verified cloud deployment.
Paper: https://badram.eu/badram.pdf
Patch: https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3015.html

All intervals concern affected implementations and attack conditions, not every TEE. Vulnerabilities pre-exist discovery/reporting. These dates do not establish exploitation in the wild. The two new examples are software-only attacks, so do not use them to substantiate a physical-access requirement on the following slide.
''')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Slide8 simplified: quiet relative-duration lines for LVI (4Apr2019 discovery→10Mar2020 software mitigation), SmashEx (3May2021 report→13Jul2021 runtime patches; discovery earlyMay only), BadRAM retained (26Feb2024 report→1Oct2024 firmware). BatteringRAM/DDrop removed. Exact date semantics and primary citations in notes.\n')
print('Revised user Slide 8; 105 slides retained.')
