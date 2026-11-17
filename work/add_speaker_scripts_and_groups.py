from pathlib import Path
import json, re
from lxml import etree as E

R=Path(__file__).resolve().parent
data=json.loads((R/'deck.json').read_text())
def script(notes):
    notes=re.split(r'\n\s*(?:Authoring clarification:|Sources?:|Measurement scope:|Revision:|Visual direction:|Visual:)',notes,maxsplit=1)[0]
    notes=re.sub(r'^User script:\s*','',notes)
    notes=re.sub(r'<[^>]*>','',notes)
    return re.sub(r'\n{3,}','\n\n',notes).strip()
for s in data:
    s['speakerScript']=script(s.get('notes',''))
    if s['title']=='Old slides below':s['speakerScript']=''
for indices,number,title in [([10,11,12],11,'Finding a design principle'),([13,14],14,'Cautious Trust: design and systems')]:
    for i in indices:
        data[i]['slideGroup']={'id':f'builds-{number}','number':number,'title':title}
t=E.parse(str(R/'editable-deck.svg'))
wrappers=t.xpath('//*[@class="SlideGroup"]')[0]
for indices,number in [([10,11,12],11),([13,14],14)]:
    for i in indices:
        footer=wrappers[i].xpath('.//*[local-name()="text" and @y="692"]')
        assert len(footer)==1
        footer[0].text=str(number)
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(data,ensure_ascii=False))
print('Stored clean speaker scripts and two build groups.')
