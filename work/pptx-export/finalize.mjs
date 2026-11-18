import path from 'node:path';
import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const here=path.dirname(fileURLToPath(import.meta.url));
const workspaceDir=path.resolve(here,'../..');
const skill='/Users/shubham_mishra/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11011/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const scene=JSON.parse(await fs.readFile(path.join(here,'scene.json'),'utf8'));
const last=scene.at(-1).number;
const source=path.join(workspaceDir,'source/Quals Talk Local.pptx');
const finalPath=process.argv[2]||path.join(workspaceDir,'outputs',`Qualifying Exam through Slide ${last}.pptx`);
const result=await finalizePresentation({workspaceDir,candidatePath:path.join(here,'candidate.pptx'),finalPath,
 pythonExecutable:'/Users/shubham_mishra/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:scene.length,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'reference',families:['Rubik'],referencePath:source,referenceSha256:createHash('sha256').update(await fs.readFile(source)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:path.join(here,path.basename(finalPath)+'.validation.json')});
console.log(JSON.stringify(result));
