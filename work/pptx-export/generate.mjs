import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const dir=path.dirname(new URL(import.meta.url).pathname);
const scene=JSON.parse(await fs.readFile(path.join(dir,'scene.json'),'utf8'));
const pres=Presentation.create({slideSize:{width:1280,height:720}});
for(const [i,page] of scene.entries()){
 const slide=pres.slides.add();slide.background.fill='#ffffff';slide.speakerNotes.text=page.notes;
 const isUnderline=o=>o.kind==='shape'&&o.geometry==='rect'&&o.position.left===98&&o.position.top===140;
 const ordered=[...page.objects.filter(o=>!isUnderline(o)),...page.objects.filter(isUnderline)];
 for(const [j,obj] of ordered.entries()){
  try{
   if(obj.kind==='text'){
    const shape=slide.shapes.add({geometry:'textbox',name:obj.name,position:obj.position,...(obj.link?{hyperlink:{uri:obj.link,isExternal:true}}:{}),fill:'none',line:{fill:'none',width:0}});
    shape.text.style={fontSize:obj.size,typeface:'Rubik',bold:obj.weight>=600,color:obj.color,insets:0,autoFit:'none',wrap:'none',verticalAlignment:'top'};
    shape.text=obj.runs?[{runs:obj.runs}]:obj.text;
   }else if(obj.kind==='image'){
    const [head,data]=obj.data.split(',');const bytes=Buffer.from(data,'base64');
    slide.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:head.slice(5).split(';')[0],alt:obj.name,fit:'contain',position:obj.position});
   }else{
    const {kind,...config}=obj;
    slide.shapes.add(config);
   }
  }catch(e){throw new Error(`Slide ${i+1} object ${j} ${obj.name}: ${e.message}`)}
 }
 console.log('Created',i+1,page.title);
}
await (await PresentationFile.exportPptx(pres)).save(path.join(dir,'candidate.pptx'));
if(process.env.RENDER_ARTIFACT==='1')for(const [i,slide] of pres.slides.items.entries()){
 const b=await pres.export({slide,format:'png',scale:1});await fs.writeFile(path.join(dir,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
 console.log('Rendered',i+1);
}
