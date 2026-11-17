from pathlib import Path
from lxml import etree as E
import json, shutil, copy
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
b=R/'revisions'/'before-tee-slide';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
sl=root.xpath('//*[@id="id2"]')[0]
p=sl.find('{'+S+'}g[@class="Page"]')
assert p is not None and len(p)==7
assets=[copy.deepcopy(p[i]) for i in [2,4,6,5]]
p.clear();p.set('class','Page')
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
g=el(p,'g',transform='scale(26.45859375)')
blue='#1F5F8B';teal='#169C9A';ink='#1F2328';gray='#6B7785'
def txt(x,y,text,size=24,color=ink,weight=400,anchor='middle'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
def path(d,color=blue,width=2.5,fill='none'):return el(g,'path',d=d,stroke=color,stroke_width=width,fill=fill)
def rect(x,y,w,h,color=blue,fill='white',radius=5):return el(g,'rect',x=x,y=y,width=w,height=h,rx=radius,stroke=color,stroke_width=2.5,fill=fill)
def reuse(asset,x,y,w,h,bx,by,bw,bh):
 q=el(g,'g',transform=f'translate({x} {y}) scale({w/bw} {h/bh}) translate({-bx} {-by})');q.append(asset)
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
title='Trusted Execution Environments (TEEs)'
txt(98,119,title,48,weight=700,anchor='start')
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
txt(640,190,'CPU-enforced isolation',26,gray)
reuse(assets[0],414,215,46,46,10594,7087,2516,2361)
txt(478,248,'SEV-SNP',24,anchor='start')
reuse(assets[1],710,220,105,41,13970,7535,4927,1913)
txt(833,248,'TDX',24,anchor='start')
# Client and a CPU-isolated application. Attestation verifies identity before keys/data flow.
rect(135,350,110,72,blue,'#F6F8FA',4)
path('M123 431h134l-10 10H133Z',blue,2,'#F6F8FA')
txt(190,475,'Client',24,blue,500)
rect(630,304,475,194,teal,'#EAF6F5',12)
txt(867,340,'CPU-protected environment',25,teal,500)
rect(655,365,210,103,blue,'white',6)
txt(760,423,'Application',25,blue,500)
rect(885,365,195,103,blue,'white',6)
txt(982,423,'Memory',25,blue,500)
path('M615 375H278',blue,2.5)
path('M291 367l-14 8 14 8',blue,2.5)
txt(445,342,'Remote attestation',23,blue,500)
txt(445,403,'Verify code identity',20,gray)
path('M278 441H615',teal,2.5)
path('M291 433l-14 8 14 8 M602 433l14 8-14 8',teal,2.5)
txt(445,473,'Authenticated, encrypted channel',18,teal)
# Reuse the original deck's two outlined protection capsules, including its typography.
reuse(assets[2],140,534,350,100,2799,13193,9932,4533)
reuse(assets[3],790,534,350,100,20272,13193,9933,4533)
txt(315,660,'Protect running code & state',20,gray)
txt(965,660,'Hide memory from the cloud host',20,gray)
txt(1182,692,'5',14.67,gray,anchor='end')
m=root.xpath('//*[@id="ooo:meta_slide_5"]')[0]
for k,v in {'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
for idx in root.xpath('//*[@class="TextShapeIndex"]/*'):
 if idx.get('{'+O+'}slide')=='id2':idx.set('{'+O+'}id-list','')
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text())
script='''<Reuse some of the existing slides> In recent years, applications have switched to using Trusted Execution Environments or TEEs for short for this purpose. TEEs are sandbox environments provided by CPU vendors like Intel's TDX, Arm's SEV-SNP etc that claim to protect the execution integrity of the application, by providing a cryptographic proof that the cloud providers are running the exact application they are supposed to be running. They also provide memory confidentiality so that if the cloud provider can't access the memory of the running application. With correct cryptographic infrastructure, this will prevent cloud providers from pretending to be the application and tampering with the data.'''
notes=script+'''\n\nAuthoring clarification: SEV-SNP is AMD's technology. Remote attestation authenticates measured software/platform state; isolation protects execution and memory. Bind an authenticated, encrypted channel to attestation to resist application impersonation and in-transit tampering. Attestation alone is not a proof of every runtime computation, nor a guarantee of persistent-storage freshness.\n\nSources:\nIntel TDX: https://www.intel.com/content/www/us/en/support/articles/000097227/processors/intel-xeon-processors.html\nAMD SEV-SNP: https://www.amd.com/en/developer/sev.html'''
manifest[5].update(title=title,text=' '.join(p.itertext()),notes=notes)
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- User Slide 5 reuses original TEE slide id2 in place (viewer 6; total remains104). Original AMD/Intel logos and both protection capsules retained, with client attestation + authenticated encrypted channel into CPU-protected application/memory. Corrected AMD SEV-SNP; clarification and sources in notes. Original source backed up before-tee-slide.\n')
print('Updated existing TEE slide; 104 slides')
