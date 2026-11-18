"""Flatten the authored SVG into editable drawing primitives, never slide images."""
from pathlib import Path
from lxml import etree as E
from PIL import ImageFont
import json,re,math,copy,sys
R=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
SVG='http://www.w3.org/2000/svg'; XL='http://www.w3.org/1999/xlink'
root=E.parse(str(R/'editable-deck.svg')).getroot(); deck=json.loads((R/'deck.json').read_text())
limit=int(sys.argv[1]) if len(sys.argv)>1 else 13
F=1280/33867
FONT='/Users/shubham_mishra/Library/Fonts/Rubik-VariableFont_wght.ttf'
fonts={}
def font(weight):
 if weight not in fonts:
  f=ImageFont.truetype(FONT,1000);f.set_variation_by_axes([weight]);fonts[weight]=f
 return fonts[weight]
def num(x,default=0):
 if x is None:return default
 return float(re.match(r'[-+\d.eE]+',str(x))[0])
def mul(a,b):
 A,B,C,D,Ee,Ff=a;g,h,i,j,k,l=b
 return (A*g+C*h,B*g+D*h,A*i+C*j,B*i+D*j,A*k+C*l+Ee,B*k+D*l+Ff)
def point(m,x,y):a,b,c,d,e,f=m;return (a*x+c*y+e,b*x+d*y+f)
def transform(s):
 m=(1,0,0,1,0,0)
 for kind,arg in re.findall(r'(\w+)\s*\(([^)]*)\)',s or ''):
  v=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',arg)]
  if kind=='translate':q=(1,0,0,1,v[0],v[1] if len(v)>1 else 0)
  elif kind=='scale':q=(v[0],0,0,v[1] if len(v)>1 else v[0],0,0)
  elif kind=='matrix':q=tuple(v)
  elif kind=='rotate':
   a=math.radians(v[0]);q=(math.cos(a),math.sin(a),-math.sin(a),math.cos(a),0,0)
   if len(v)>1:q=mul(mul((1,0,0,1,v[1],v[2]),q),(1,0,0,1,-v[1],-v[2]))
  else:raise ValueError(kind)
  m=mul(m,q)
 return m
def color(s):
 if not s or s=='none':return 'none'
 if s.startswith('rgb'):return '#'+''.join(f'{int(x):02x}' for x in re.findall(r'\d+',s)[:3])
 return {'white':'#ffffff','black':'#000000'}.get(s,s)
def style(e,old):
 s=old.copy();s.update({k:v for k,v in e.attrib.items() if k in ['fill','stroke','stroke-width','font-size','font-weight','font-family','text-anchor','stroke-linecap','stroke-linejoin']})
 for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',e.get('style','')):s[k]=v
 return s

def arc(x,y,rx,ry,angle,large,sweep,X,Y):
 if abs(x-X)+abs(y-Y)<1e-10:return []
 if not rx or not ry:return [('L',X,Y)]
 rx,ry=abs(rx),abs(ry);a=math.radians(angle);c,s=math.cos(a),math.sin(a)
 xp=c*(x-X)/2+s*(y-Y)/2;yp=-s*(x-X)/2+c*(y-Y)/2
 ratio=xp*xp/rx**2+yp*yp/ry**2
 if ratio>1:rx*=math.sqrt(ratio);ry*=math.sqrt(ratio)
 coeff=(-1 if bool(large)==bool(sweep) else 1)*math.sqrt(max(0,(rx*rx*ry*ry-rx*rx*yp*yp-ry*ry*xp*xp)/(rx*rx*yp*yp+ry*ry*xp*xp)))
 cxp=coeff*rx*yp/ry;cyp=-coeff*ry*xp/rx
 cx=c*cxp-s*cyp+(x+X)/2;cy=s*cxp+c*cyp+(y+Y)/2
 start=math.atan2((yp-cyp)/ry,(xp-cxp)/rx);end=math.atan2((-yp-cyp)/ry,(-xp-cxp)/rx);delta=end-start
 if sweep and delta<0:delta+=2*math.pi
 if not sweep and delta>0:delta-=2*math.pi
 count=max(1,math.ceil(abs(delta)/(math.pi/2)));step=delta/count;out=[]
 def at(t):return (cx+rx*c*math.cos(t)-ry*s*math.sin(t),cy+rx*s*math.cos(t)+ry*c*math.sin(t))
 def deriv(t):return (-rx*c*math.sin(t)-ry*s*math.cos(t),-rx*s*math.sin(t)+ry*c*math.cos(t))
 for i in range(count):
  t=start+i*step;u=t+step;alpha=4/3*math.tan(step/4);p=at(t);q=at(u);dp=deriv(t);dq=deriv(u)
  out.append(('C',p[0]+alpha*dp[0],p[1]+alpha*dp[1],q[0]-alpha*dq[0],q[1]-alpha*dq[1],q[0],q[1]))
 return out

def parse_path(d):
 tok=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',d);i=0;cmd=None;x=y=sx=sy=0;out=[]
 while i<len(tok):
  if tok[i].isalpha():cmd=tok[i];i+=1
  op=cmd.upper();rel=cmd.islower()
  if op=='Z':out.append(('Z',));x,y=sx,sy;cmd=None;continue
  sizes={'M':2,'L':2,'H':1,'V':1,'C':6,'Q':4,'A':7};n=sizes[op];v=list(map(float,tok[i:i+n]));i+=n
  if op in ['M','L']:
   X,Y=v;X+=x if rel else 0;Y+=y if rel else 0;out.append((op,X,Y));x,y=X,Y
   if op=='M':sx,sy=x,y;cmd='l' if rel else 'L'
  elif op=='H':x=v[0]+(x if rel else 0);out.append(('L',x,y))
  elif op=='V':y=v[0]+(y if rel else 0);out.append(('L',x,y))
  elif op in ['C','Q']:
   for j in range(0,n,2):v[j]+=x if rel else 0;v[j+1]+=y if rel else 0
   out.append((op,*v));x,y=v[-2:]
  elif op=='A':
   X,Y=v[-2:];X+=x if rel else 0;Y+=y if rel else 0;out+=arc(x,y,*v[:5],X,Y);x,y=X,Y
 return out

def geom(commands,m,s,name):
 pts=[];out=[]
 for c in commands:
  vv=[]
  for j in range(1,len(c),2):p=point(m,c[j],c[j+1]);pts.append(p);vv.extend(p)
  out.append((c[0],*vv))
 if not pts:return None
 x=min(p[0] for p in pts);y=min(p[1] for p in pts);w=max(.01,max(p[0] for p in pts)-x);h=max(.01,max(p[1] for p in pts)-y)
 cmds=[]
 for c in out:
  v=c[1:];op=c[0]
  if op in ['M','L']:cmds.append({'moveTo' if op=='M' else 'lineTo':{'x':v[0]-x,'y':v[1]-y}})
  elif op=='C':cmds.append({'cubicBezTo':{'x1':v[0]-x,'y1':v[1]-y,'x2':v[2]-x,'y2':v[3]-y,'x':v[4]-x,'y':v[5]-y}})
  elif op=='Q':cmds.append({'quadBezTo':{'x1':v[0]-x,'y1':v[1]-y,'x':v[2]-x,'y':v[3]-y}})
  else:cmds.append({'close':{}})
 return {'kind':'shape','geometry':'custom','name':name,'position':{'left':x,'top':y,'width':w,'height':h},'fill':color(s.get('fill','#000000')),'line':line(s,m),'customPaths':[{'width':w,'height':h,'commands':cmds}]}
def line(s,m):return {'fill':color(s.get('stroke','none')),'width':num(s.get('stroke-width'),1)*math.hypot(m[0],m[1]),'style':'solid'}
def add_icon(out,text,x,y,size):
 # Native shapes replace platform-dependent emoji glyphs.
 top=y-size*.85;size*=.85
 if text=='✅':
  out.append({'kind':'shape','geometry':'roundRect','name':'Integrity check','position':{'left':x,'top':top,'width':size,'height':size},'fill':'#55a93f','line':{'fill':'none','width':0},'borderRadius':size*.15})
  out.append(geom([('M',x+size*.2,top+size*.53),('L',x+size*.43,top+size*.76),('L',x+size*.82,top+size*.22)],(1,0,0,1,0,0),{'fill':'none','stroke':'#ffffff','stroke-width':size*.13},'Check mark'))
 elif text=='❌':
  out.append(geom([('M',x+size*.16,top+size*.16),('L',x+size*.84,top+size*.84),('M',x+size*.84,top+size*.16),('L',x+size*.16,top+size*.84)],(1,0,0,1,0,0),{'fill':'none','stroke':'#e64747','stroke-width':size*.16},'Integrity cross'))
 elif text=='🎭':
  for dx,dy,fill in [(size*.35,0,'#a02b93'),(0,size*.2,'#1f5f8b')]:
   X=x+dx;Y=top+dy;W=size*.65;H=size*.75
   out.append(geom([('M',X,Y),('Q',X+W*.5,Y+H*.12,X+W,Y),('L',X+W*.9,Y+H*.65),('Q',X+W*.5,Y+H*1.15,X+W*.1,Y+H*.65),('Z',)],(1,0,0,1,0,0),{'fill':fill,'stroke':'none'},'Conditional integrity mask'))
   for ex in [.25,.7]:out.append({'kind':'shape','geometry':'ellipse','name':'Mask eye','position':{'left':X+W*ex,'top':Y+H*.3,'width':W*.13,'height':H*.10},'fill':'#ffffff','line':{'fill':'none','width':0}})
   out.append(geom([('M',X+W*.27,Y+H*.62),('Q',X+W*.5,Y+H*.78,X+W*.75,Y+H*.62)],(1,0,0,1,0,0),{'fill':'none','stroke':'white','stroke-width':size*.04},'Mask smile'))
 else:raise ValueError(text)

def text_nodes(e,m,base,out):
 cursor=[0,0]
 def run(node,s):
  s=style(node,s)
  if node.get('x') is not None:cursor[0]=num(node.get('x'))
  if node.get('y') is not None:cursor[1]=num(node.get('y'))
  def emit(value,st):
   if not value or not value.strip():return
   fs=num(st.get('font-size'),16);weight=int(st.get('font-weight',400));actual=num(node.get('textLength'),font(weight).getlength(value)/1000*fs)
   anchor=st.get('text-anchor','start');xx=cursor[0]-(actual/2 if anchor=='middle' else actual if anchor=='end' else 0)
   xx,yy=point(m,xx,cursor[1]);scale=math.hypot(m[0],m[1]);angle=math.degrees(math.atan2(m[1],m[0]));size=fs*scale;width=actual*scale
   if value in ['✅','❌','🎭']:add_icon(out,value,xx,yy,size)
   else:
    # Keep baseline and exact horizontal anchor from the SVG; text remains editable.
    top=yy-size*.94;boxw=max(width+size*.15,1);boxh=size*1.3
    left=xx
    if abs(angle)>1:
     # Rotation around the text origin, then convert to the center-based PPT rotation.
     a=math.radians(angle);dx=boxw/2;dy=boxh/2-size*.94
     cx=xx+math.cos(a)*dx-math.sin(a)*dy;cy=yy+math.sin(a)*dx+math.cos(a)*dy
     left=cx-boxw/2;top=cy-boxh/2
    out.append({'kind':'text','name':value[:70],'text':value,'position':{'left':left,'top':top,'width':boxw,'height':boxh,'rotation':angle},'size':size,'weight':weight,'color':color(st.get('fill','#000000')),'targetWidth':width})
   cursor[0]+=actual
  emit(node.text,s)
  for ch in node:
   run(ch,s);emit(ch.tail,s)
 run(e,base)

def walk(e,m,s,out):
 tag=E.QName(e).localname
 if tag in ['defs','desc','title','metadata','script']:return
 if tag in ['foreignObject','use','polygon','polyline']:raise ValueError(f'Add native export support for SVG {tag} before exporting this slide')
 if e.get('visibility')=='hidden' or e.get('class')=='BoundingBox':return
 s=style(e,s);m=mul(m,transform(e.get('transform')))
 if tag=='a':s['link']=e.get('{'+XL+'}href') or e.get('href')
 if tag=='text':
  chunks=[];text_nodes(e,m,s,chunks)
  if len(chunks)>1 and all(c['kind']=='text' and abs(c['position']['top']-chunks[0]['position']['top'])<.01 and c['size']==chunks[0]['size'] for c in chunks):
   combined=copy.deepcopy(chunks[0]);combined['text']=''.join(c['text'] for c in chunks)
   combined['runs']=[{'run':c['text'],'style':{'bold':c['weight']>=600,'color':c['color'],'typeface':'Rubik','fontSize':str(c['size'])+'px'}} for c in chunks]
   combined['position']['width']=sum(c['targetWidth'] for c in chunks)+combined['size']*.2;chunks=[combined]
  if s.get('link'):
   for chunk in chunks:chunk['link']=s['link']
  out.extend(chunks);return
 name=e.get('id') or tag
 if tag in ['rect','circle','ellipse']:
  if tag=='rect':x=num(e.get('x'));y=num(e.get('y'));w=num(e.get('width'));h=num(e.get('height'));kind='roundRect' if num(e.get('rx')) else 'rect'
  else:
   rx=num(e.get('r',e.get('rx')));ry=num(e.get('r',e.get('ry')));x=num(e.get('cx'))-rx;y=num(e.get('cy'))-ry;w=rx*2;h=ry*2;kind='ellipse'
  if color(s.get('fill','#000000'))=='none' and color(s.get('stroke','none'))=='none':return
  x,y=point(m,x,y);w*=math.hypot(m[0],m[1]);h*=math.hypot(m[2],m[3])
  sh={'kind':'shape','geometry':kind,'name':name,'position':{'left':x,'top':y,'width':w,'height':h},'fill':color(s.get('fill','#000000')),'line':line(s,m)}
  if kind=='roundRect':sh['borderRadius']=num(e.get('rx'))*math.hypot(m[0],m[1])
  out.append(sh)
 elif tag=='path':
  if color(s.get('fill','#000000'))=='none' and color(s.get('stroke','none'))=='none':return
  o=geom(parse_path(e.get('d')),m,s,name)
  if o:out.append(o)
 elif tag=='line':out.append(geom([('M',num(e.get('x1')),num(e.get('y1'))),('L',num(e.get('x2')),num(e.get('y2')))],m,s,name))
 elif tag=='image':
  x,y=point(m,num(e.get('x')),num(e.get('y')));w=num(e.get('width'))*math.hypot(m[0],m[1]);h=num(e.get('height'))*math.hypot(m[2],m[3])
  out.append({'kind':'image','name':'AMD logo','data':e.get('{'+XL+'}href'),'position':{'left':x,'top':y,'width':w,'height':h}})
 else:
  for ch in e:walk(ch,m,s,out)

result=[];wrappers=root.xpath('//*[@class="SlideGroup"]')[0]
for i,(entry,w) in enumerate(zip(deck,wrappers)):
 if entry['displayNumber']>limit:break
 out=[];slide=w.xpath('.//*[@class="Slide"]')[0]
 walk(slide,(F,0,0,F,0,0),{'fill':'black','stroke':'none','font-family':'Rubik'},out)
 result.append({'title':entry['title'],'number':entry['displayNumber'],'notes':entry.get('speakerScript',''),'objects':out})
 # Isolated SVG for reference-only visual QA.
 ref=E.Element('{'+SVG+'}svg',nsmap={None:SVG,'xlink':XL},width='1280',height='720',viewBox='0 0 33867 19050')
 for el in root:
  if E.QName(el).localname in ['style','defs'] and not el.xpath('.//*[@id="ooo:meta_slides"]'):ref.append(copy.deepcopy(el))
 ref.append(E.Element('{'+SVG+'}rect',width='33867',height='19050',fill='white'))
 ref.append(copy.deepcopy(slide));E.ElementTree(ref).write(str(OUT/f'reference-{i+1:02d}.svg'))
 print(i+1,entry['title'],len(out),'native objects')
(OUT/'scene.json').write_text(json.dumps(result))
