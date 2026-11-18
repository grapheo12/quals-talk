"""Generate PPTX N: export through logical slide N, with every build editable.

Run with the bundled Python. After generating, visually inspect the rendered
slides before delivery. New SVG constructs must be supported in the extractor.
"""
from pathlib import Path
import os, subprocess, sys, datetime

ROOT=Path(__file__).resolve().parent.parent
BUILD=ROOT/'work'/'pptx-export'
RUNTIME=Path('/Users/shubham_mishra/.cache/codex-runtimes/codex-primary-runtime/dependencies')
SKILL=Path('/Users/shubham_mishra/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11011/skills/presentations')
N=int(sys.argv[1])
env=os.environ.copy();env['RUNTIME_NODE_MODULES']=str(RUNTIME/'node'/'node_modules')
node=str(RUNTIME/'node'/'bin'/'node');python=str(RUNTIME/'python'/'bin'/'python3')
def run(args,cwd=ROOT):subprocess.run(list(map(str,args)),cwd=cwd,env=env,check=True)
modules=BUILD/'node_modules'
if not modules.exists():modules.symlink_to(RUNTIME/'node'/'node_modules',target_is_directory=True)
run([node,SKILL/'container_tools'/'mark_artifact_operation_started.mjs','--operation-kind','create','--expected-output-count','1','--output-format','pptx'],SKILL)
run([python,BUILD/'extract_native_scene.py',N])
run([node,BUILD/'generate.mjs'])
out=ROOT/'outputs'/f'Qualifying Exam through Slide {N} - Editable.pptx'
if out.exists():out=out.with_stem(out.stem+' '+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
run([node,BUILD/'finalize.mjs',out])
run([RUNTIME/'bin'/'override'/'soffice','--headless','--convert-to','pdf','--outdir',BUILD,out])
print('Validated PPTX:',out)
print('Render its PDF and inspect every slide before delivering.')
