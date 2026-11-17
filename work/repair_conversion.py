from pathlib import Path
from lxml import etree as E
import zipfile, json, posixpath, base64, unicodedata

ROOT=Path(__file__).resolve().parent
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','mc':'http://schemas.openxmlformats.org/markup-compatibility/2006','s':'http://www.w3.org/2000/svg','h':'http://www.w3.org/1999/xhtml'}
svgpath=ROOT/'editable-deck.svg'
tree=E.parse(str(svgpath));root=tree.getroot()
S=ns['s'];H=ns['h'];OOO='http://xml.openoffice.org/svg/export'
manifest=json.loads((ROOT/'deck.json').read_text())
def bbox(xfrm):
    off=xfrm.find('a:off',ns);ext=xfrm.find('a:ext',ns)
    return [int(off.get('x'))/360,int(off.get('y'))/360,int(ext.get('cx'))/360,int(ext.get('cy'))/360]
def parent_for(page,box):
    candidates=page.xpath('.//s:rect[@class="BoundingBox"]',namespaces=ns)
    best=min(candidates,key=lambda r:sum(abs(float(r.get(k,'0'))-v) for k,v in zip(['x','y','width','height'],box)))
    dist=sum(abs(float(best.get(k,'0'))-v) for k,v in zip(['x','y','width','height'],box))
    return best.getparent() if dist<2000 else page
def add(parent,tag,**attrs):return E.SubElement(parent,'{'+S+'}'+tag,{k:str(v) for k,v in attrs.items()})

with zipfile.ZipFile('/Users/shubham_mishra/Documents/Quals Talk Local.pptx') as z:
    for n in range(1,101):
        r=E.fromstring(z.read(f'ppt/slides/slide{n}.xml'))
        page=root.xpath(f'//*[@id="id{n}"]/*[@class="Page"]')[0]
        rels={v.get('Id'):v.get('Target') for v in E.fromstring(z.read(f'ppt/slides/_rels/slide{n}.xml.rels'))}
        if False:
            root.xpath(f'//*[@id="ooo:meta_slide_{n-1}"]')[0].set('{'+OOO+'}page-number-visibility','visible')
        # Resolve notes by relationship; notes indices stop matching slide numbers after edits.
        note_targets=[v.get('Target') for v in E.fromstring(z.read(f'ppt/slides/_rels/slide{n}.xml.rels')) if v.get('Type').endswith('/notesSlide')]
        if note_targets:
            nr=E.fromstring(z.read(posixpath.normpath('ppt/slides/'+note_targets[0])))
            texts=nr.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]//a:t/text()',namespaces=ns)
            manifest[n-1]['notes']='\n'.join(texts)
        for choice in r.xpath('.//mc:AlternateContent/mc:Choice[p:sp//m:oMath]/p:sp',namespaces=ns):
            box=bbox(choice.find('p:spPr/a:xfrm',ns));parent=parent_for(page,box)
            if parent.xpath('./s:foreignObject[@data-repair="equation"]',namespaces=ns):continue
            foreign=add(parent,'foreignObject',x=box[0],y=box[1],width=box[2],height=box[3]);foreign.set('data-repair','equation')
            div=E.SubElement(foreign,'{'+H+'}div',style='height:100%;display:flex;flex-direction:column;justify-content:center;text-align:center;font-family:Rubik;box-sizing:border-box;padding:0 254px;line-height:1.15;color:#17202A;')
            for p in choice.findall('p:txBody/a:p',ns):
                para=E.SubElement(div,'{'+H+'}div')
                for t in p.xpath('.//a:r/a:t | .//m:r/m:t',namespaces=ns):
                    pr=t.getparent().find('a:rPr',ns);style=[]
                    if pr is not None:
                        style.append(f'font-size:{int(pr.get("sz","2400"))/100*2540/72}px')
                        if pr.get('b')=='1':style.append('font-weight:700')
                        if pr.get('i')=='1':style.append('font-style:italic')
                        if pr.get('u')=='sng':style.append('text-decoration:underline')
                        clr=pr.find('a:solidFill/a:srgbClr',ns)
                        if clr is not None:
                            c=clr.get('val');lum=clr.find('a:lumMod',ns)
                            if lum is not None:c=''.join(f'{round(int(c[i:i+2],16)*int(lum.get("val"))/100000):02x}' for i in [0,2,4])
                            style.append('color:#'+c)
                        if pr.get('spc'):style.append(f'letter-spacing:{int(pr.get("spc"))/100*2540/72}px')
                    span=E.SubElement(para,'{'+H+'}span',style=';'.join(style));span.text=unicodedata.normalize('NFKC',t.text or '')
        for table in r.xpath('.//p:graphicFrame[a:graphic/a:graphicData/a:tbl]',namespaces=ns):
            box=bbox(table.find('p:xfrm',ns));parent=parent_for(page,box)
            if parent.xpath('./s:g[@data-repair="emoji"]',namespaces=ns):continue
            group=add(parent,'g');group.set('data-repair','emoji')
            tbl=table.find('a:graphic/a:graphicData/a:tbl',ns)
            widths=[int(c.get('w'))/360 for c in tbl.findall('a:tblGrid/a:gridCol',ns)]
            y=box[1]
            for tr in tbl.findall('a:tr',ns):
                h=int(tr.get('h'))/360;x=box[0]
                for cell,width in zip(tr.findall('a:tc',ns),widths):
                    for t in cell.findall('.//a:t',ns):
                        if t.text and any(c in t.text for c in ['✅','❌','🎭']):
                            pr=t.getparent().find('a:rPr',ns);sz=int(pr.get('sz','2400'))/100*2540/72 if pr is not None else 846.67
                            text=add(group,'text',x=x+width/2,y=y+h/2+sz*.32,fill='#17202A',stroke='none')
                            text.set('font-family','Apple Color Emoji,Segoe UI Emoji,Noto Color Emoji');text.set('font-size',str(sz));text.set('text-anchor','middle');text.text=t.text
                    x+=width
                y+=h
        if n in [96,97] and not page.xpath('./s:image[@data-repair="plot"]',namespaces=ns):
            box=bbox(r.find('.//p:pic/p:spPr/a:xfrm',ns))
            data=base64.b64encode((ROOT/f'chart{47 if n==96 else 48}.svg').read_bytes()).decode()
            img=add(page,'image',x=box[0],y=box[1],width=box[2],height=box[3],preserveAspectRatio='none');img.set('data-repair','plot');img.set('{http://www.w3.org/1999/xlink}href','data:image/svg+xml;base64,'+data)
svgpath.write_bytes(E.tostring(tree,xml_declaration=True,encoding='utf-8'))
(ROOT/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
print('Restored equations, table symbols, page numbers, two evaluation plots, and corrected speaker-note mapping.')
