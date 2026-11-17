from pathlib import Path
import json, base64, zipfile, xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'outputs'
SOURCE = Path('/Users/shubham_mishra/Documents/Quals Talk Local.pptx')
SVG = ROOT / 'work' / 'editable-deck.svg'

def prepare():
    if not SVG.exists():
        svg = (ROOT / 'work' / 'Quals Talk Local.svg').read_text()
        css = ''
        for style, name in [('normal','Rubik-VariableFont_wght.ttf'),('italic','Rubik-Italic-VariableFont_wght.ttf')]:
            data = base64.b64encode((Path('/Users/shubham_mishra/Library/Fonts') / name).read_bytes()).decode()
            css += "@font-face{font-family:Rubik;src:url(data:font/ttf;base64,"+data+");font-weight:300 900;font-style:"+style+";}"
        svg = svg.replace('<defs', '<style type="text/css"><![CDATA['+css+']]></style><defs', 1)
        SVG.write_text(svg)
    manifest = ROOT / 'work' / 'deck.json'
    if not manifest.exists():
        ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
        slides=[]
        with zipfile.ZipFile(SOURCE) as z:
            for i in range(1,101):
                r=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
                texts=[''.join(p.itertext()) for p in r.findall('.//a:t',ns)]
                title=r.find('.//p:sp[p:nvSpPr/p:nvPr/p:ph]',ns) if False else None
                # The SVG's metadata retains PowerPoint's title, including its repeated-build suffix.
                section='Opening' if i<21 else 'Pirateship' if i<70 else 'HarborMaster' if i<98 else 'Next steps'
                notes=''
                npath=f'ppt/notesSlides/notesSlide{i}.xml'
                if npath in z.namelist():
                    nr=E.fromstring(z.read(npath))
                    parts=[]
                    for sp in nr.findall('.//p:sp',ns):
                        ph=sp.find('p:nvSpPr/p:nvPr/p:ph',ns)
                        if ph is not None and ph.get('type')=='body':
                            parts += [''.join(p.itertext()) for p in sp.findall('.//a:t',ns)]
                    notes='\n'.join(parts)
                slides.append({'number':i,'section':section,'text':' '.join(texts),'notes':notes})
        import re
        import html
        names=re.findall(r'ooo:display-name="([^"]*)"',SVG.read_text())
        for s,name in zip(slides,names): s['title']=html.unescape(name)
        manifest.write_text(json.dumps(slides,ensure_ascii=False))

def build(out=OUT, live=True):
    prepare()
    out=Path(out)
    out.mkdir(parents=True, exist_ok=True)
    template=(ROOT/'work'/'viewer.html').read_text()
    data=json.dumps(SVG.read_text(),ensure_ascii=False).replace('</','<\\/')
    meta=(ROOT/'work'/'deck.json').read_text().replace('</','<\\/')
    output=template.replace('__SVG_JSON__',data).replace('__DECK_JSON__',meta).replace('const livePreview=true;', 'const livePreview='+str(live).lower()+';')
    entry=out/('Qualifying Exam.html' if live else 'index.html')
    entry.write_text(output)
    (out/'deck.svg').write_text(SVG.read_text())
    if not live:(out/'.nojekyll').touch()
    return entry

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Build the qualifying-exam web deck.')
    parser.add_argument('--static', action='store_true', help='Build for static hosting without the local editing server.')
    parser.add_argument('--out', type=Path, default=None)
    args=parser.parse_args()
    print(build(args.out or (OUT/'site' if args.static else OUT), live=not args.static))
