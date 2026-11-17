from pathlib import Path
p=Path(__file__).with_name('viewer.html')
s=p.read_text()
css='''
/* Presenter script stays visible in normal and presentation modes. */
.app{grid-template-rows:62px minmax(0,1fr) 58px 30vh}
aside{grid-column:1;grid-row:2/4}
main{grid-column:2;grid-row:2;padding:16px}
footer{grid-row:3}
#speakerPanel{grid-column:1/-1;grid-row:4;min-height:0;display:flex;flex-direction:column;background:#1b2528;border-top:2px solid #3e6666;padding:16px 28px 20px}
.script-heading{display:flex;align-items:center;gap:16px;flex:none;margin-bottom:12px;color:#a7c0c3;font-size:12px;letter-spacing:.06em;text-transform:uppercase}
#scriptSlide{color:#87d6cc;text-transform:none;letter-spacing:0}
#speakerScript{overflow:auto;white-space:pre-wrap;line-height:1.55;font-size:clamp(20px,1.4vw,28px);color:#f2f5f5;max-width:1450px;width:100%;margin:0 auto;padding:0 12px 12px;scrollbar-gutter:stable}
#speakerScript.empty{color:#91a7ac;font-style:italic}
#jump{width:68px}
.build-group{margin:4px 0;border:1px solid #34494d;border-radius:7px;overflow:hidden}
.build-group summary{display:flex;gap:10px;align-items:baseline;padding:11px 9px;cursor:pointer;font-size:12px;line-height:1.45;color:#d2dfe1;list-style:none}
.build-group summary::-webkit-details-marker{display:none}
.build-group summary::before{content:'▸';color:#91a7ac;flex:none}
.build-group[open] summary::before{content:'▾'}
.build-group summary .group-number{min-width:22px;color:#89d5cd}
.build-group summary:focus-visible{outline:2px solid #39b9b5;outline-offset:-3px}
.build-group.contains-active{border-color:#4b8882}
.build-group .slide-link{padding-left:30px;margin:0;border-radius:0}
.build-group .slide-link span{min-width:30px}
body.focus .app{grid-template-columns:1fr;grid-template-rows:minmax(0,1fr) 30vh}
body.focus main{grid-column:1;grid-row:1}
body.focus #speakerPanel{grid-column:1;grid-row:2}
@media(max-width:850px){.app{grid-template-rows:52px minmax(0,1fr) 52px 30vh}main{grid-column:1;padding:8px}#speakerPanel{padding:12px 14px}#speakerScript{font-size:20px}.script-heading{margin-bottom:8px}}
'''
s=s.replace('</style>',css+'</style>')
s=s.replace('title="Speaker notes (N)">Notes','title="Research and authoring notes (N)">Reference notes')
s=s.replace('type="number" min="1" max="111"','type="text"')
s=s.replace('aria-label="Slide number"','aria-label="Slide or build number"')
s=s.replace('</footer></div>','</footer><section id="speakerPanel" aria-label="Speaker notes"><div class="script-heading"><strong>Speaker notes</strong><span id="scriptSlide"></span></div><div id="speakerScript" tabindex="0"></div></section></div>')
s=s.replace("const frame=document.getElementById('slides'),outline=document.getElementById('outline');",'''const frame=document.getElementById('slides'),outline=document.getElementById('outline');
const buildGroups=new Map();
deck.forEach((s,n)=>{if(s.slideGroup){const id=s.slideGroup.id;if(!buildGroups.has(id))buildGroups.set(id,[]);buildGroups.get(id).push(n)}});
function buildLabel(n){const s=deck[n],group=s.slideGroup;if(!group)return String(n+1);return group.number+String.fromCharCode(97+buildGroups.get(group.id).indexOf(n))}
function cleanScript(s){
 if(s.speakerScript!==undefined)return s.speakerScript;
 return (s.notes||'').split(/\\n\\s*(?:Authoring clarification:|Sources?:|Measurement scope:|Revision:|Visual direction:|Visual:)/)[0].replace(/^User script:\\s*/,'').replace(/<[^>]*>/g,'').trim();
}''')
a=s.index('function update(n)');b=s.index('function go(n)',a)
s=s[:a]+'''function update(n){
 const changed=current!==n;current=n;
 document.getElementById('jump').value=buildLabel(n);
 document.getElementById('total').textContent='/ '+deck.length+' builds';
 document.getElementById('title').textContent=deck[n].title;
 document.getElementById('notes').textContent=deck[n].notes||'No reference notes for this slide.';
 const script=document.getElementById('speakerScript'),text=cleanScript(deck[n]);
 script.textContent=text||'No speaker script for this slide yet.';script.classList.toggle('empty',!text);
 if(changed)script.scrollTop=0;
 document.getElementById('scriptSlide').textContent='Slide '+buildLabel(n)+' · '+deck[n].title;
 document.querySelectorAll('.slide-link').forEach(b=>{const active=+b.dataset.n===n;b.classList.toggle('active',active);if(active)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current')});
 document.querySelectorAll('.build-group').forEach(d=>{const active=d.dataset.group===deck[n].slideGroup?.id;d.classList.toggle('contains-active',active);if(active)d.open=true});
 history.replaceState(null,'','#'+(n+1));
}
''' +s[b:]
a=s.index("function list(q='')");b=s.index('function resize()',a)
s=s[:a]+'''function list(q=''){
 const expanded=new Set([...outline.querySelectorAll('.build-group[open]')].map(d=>d.dataset.group));
 outline.replaceChildren();let section='';const seen=new Set();q=q.toLowerCase();
 const matches=n=>!q||(deck[n].title+' '+deck[n].text+' '+buildLabel(n)+' '+(deck[n].slideGroup?.title||'')).toLowerCase().includes(q);
 function link(n,parent){const s=deck[n],b=document.createElement('button');b.className='slide-link'+(n===current?' active':'');b.dataset.n=n;if(n===current)b.setAttribute('aria-current','step');const number=document.createElement('span');number.textContent=buildLabel(n);b.append(number,document.createTextNode(s.title));b.onclick=()=>go(n);parent.append(b)}
 deck.forEach((s,n)=>{
  const g=s.slideGroup;if(g&&seen.has(g.id))return;
  const members=g?buildGroups.get(g.id):[n];if(g)seen.add(g.id);
  if(!members.some(matches))return;
  if(s.section!==section){section=s.section;const h=document.createElement('div');h.className='group';h.textContent=section;outline.append(h)}
  if(!g){link(n,outline);return}
  const details=document.createElement('details');details.className='build-group';details.dataset.group=g.id;
  details.open=!!q||members.includes(current)||expanded.has(g.id);details.classList.toggle('contains-active',members.includes(current));
  const summary=document.createElement('summary'),number=document.createElement('span');number.className='group-number';number.textContent=g.number;
  summary.append(number,document.createTextNode(g.title));details.append(summary);members.forEach(i=>link(i,details));outline.append(details);
 });
}
function jumpTo(value){
 const label=value.trim().toLowerCase();
 let n=deck.findIndex((s,i)=>buildLabel(i).toLowerCase()===label);
 if(n<0)n=deck.findIndex(s=>s.slideGroup&&String(s.slideGroup.number)===label);
 if(n>=0)go(n);else document.getElementById('jump').value=buildLabel(current);
}
''' +s[b:]
s=s.replace("document.getElementById('jump').onchange=e=>go((parseInt(e.target.value)||1)-1)","document.getElementById('jump').onchange=e=>jumpTo(e.target.value)")
s=s.replace("go((parseInt(e.target.value)||1)-1);e.target.blur()","jumpTo(e.target.value);e.target.blur()")
p.write_text(s)
