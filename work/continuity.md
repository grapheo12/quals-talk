# Qualifying exam web deck: working context

User wants to dictate changes in this chat, possibly rebuilding the narrative from scratch. Follow their original slide style. The new narrative is being dictated one slide at a time. User calls the first content slide “Slide 1”, excluding the title.

## Live editing

- Authoritative editable source: `work/editable-deck.svg`. This contains editable SVG text, vector diagrams, embedded pictures, and LibreOffice's SVG animation player. Do not replace it with screenshots.
- Metadata, search, titles, source speaker notes: `work/deck.json` (100 records). Notes have been resolved via relationships, not assumed note-slide numbers.
- Shell: `work/viewer.html`. Builder: `work/build_web.py`.
- Local live server: `python3 work/serve_web.py`, port 8765, loopback only. Server watches the source SVG, metadata and viewer template and builds the HTML automatically when `/api/revision` is polled. Browser refreshes on change and retains its slide number via hash. Restart server if Python code changes. Use an existing server if already running.
- Deliverable: `outputs/Qualifying Exam.html`; `outputs/deck.svg` is its HTTP companion. HTML embeds the SVG as an offline fallback. The live link is http://127.0.0.1:8765/ .
- Do not regenerate from the original PPTX for routine edits: this would erase conversion repairs. Before substantial edits, copy corrected editable SVG and JSON into a versioned work backup.
- The original PPTX at `/Users/shubham_mishra/Documents/Quals Talk Local.pptx` has not been changed.
- Spaces import was attempted: Page page_67a1928001f081918f1d6702d3590a32, attachments_incomplete warning; local connection unavailable, direct Artifact Session import also failed. This Page is NOT the authoritative working deck. Use the web deck.

## Style learned from all 100 slides

- Wide 16:9 format, 13.333 by 7.5 inches. SVG viewBox 0 0 33867 19050. At a 1280px slide width, the ordinary content left edge is about 98px.
- Rubik throughout. Bold 36pt titles, 48pt cover title, mostly 18–24pt content, smaller diagram labels. Dark charcoal #1F2328, muted gray #6B7785. White backgrounds with lots of whitespace.
- Keep the user's short blue underline below titles (approximately #1F5F8B). Cover/section dividers use a longer rule. Do not remove this just because generic slide guidance dislikes underlines.
- Blue/teal describes normal computation and trusted paths. Green denotes successful/audited/committed states. Purple signals the separate protection/audit dimension. Red is malicious behavior, rollback or error. Use existing semantic colors consistently.
- Familiar hand-built diagrams: database cylinders, TEE boxes and locks, auditor detective, gears, timelines, ledgers of little blocks, arrows, speech/thought bubbles, pill outlines, shaded callout panels and braces.
- Explanation proceeds through concrete examples and incremental builds, often duplicating a slide to show one changed state. Maintain stable coordinates across these builds. Retain the teaching rhythm instead of collapsing everything into dense bullets.
- Titles often ask a direct question or state the technical takeaway; occasional emphatic uppercase/italic/underline. Keep selective humor and visual metaphors.
- Results emphasize paired latency/throughput plots and short numeric takeaways. Preserve real plots and values. Do not invent data.
- Original storyline: 1–20 opening/Cautious Trust; 21–68 Pirateship; 69 transition/scaling; 70–97 HarborMaster; 98–100 next steps. Do not assume this order is fixed once user dictates a new pitch.

## Conversion repairs and cautions

- Removed one exposed cover master subtitle placeholder.
- Original source has NULL fallback-image relationships for Office equations on 26,27,45,46. Reconstructed exact text/inline variables from source Choice nodes as XHTML foreignObjects inside the original shape groups, so build/dimming layers still work.
- Windows EMFs image47 and image48 embed original PDFs. Extracted these, converted to SVG, and restored the two plots on 96 and 97 at original coordinates. The assets are in work/chart47.svg and chart48.svg.
- Emoji table symbols: added correctly sized native emoji glyphs and blanked the original distorted glyph spans. Tables on 7,9,22,71 are particularly relevant.
- Page numbers: renamed original per-slide PageNumber groups to CustomPageNumber and set visibility to inherit (never visible, which overrides hidden parent slides). The final page-number text uses a simple right-aligned SVG text node at (31284,18319), size 388. Do NOT enable ooo:page-number-visibility on metadata; the animation player stretches master placeholder text when generating numbers.
- `repair_conversion.py` is the one-time recovery source. Do not rerun blindly; additional finishing repairs were applied after it (custom page numbers and blanking duplicate emoji spans).
- Browser controls: arrows change slides; Next build/Space advances animation; enter a number and press Enter to jump; F toggles presentation view; N toggles notes. Outline appears at wider browser widths.
- Original slide sequences retained, but transitions may differ from PowerPoint. Native PowerPoint visual verification was not completed (app launch timed out).

- Fixed two rotated chart-label text runs on evaluation slides: subsequent run positions were exported on the wrong axis. Shifted them along the rotated baseline.
- Browser testing verified slide navigation, numbered jump, animation advance, two recovered HarborMaster plots, equation pills, and live refresh retaining the active slide. All original text fragments matched the web source in a deck-wide check.

## New narrative edits

- Inserted the user-dictated first content slide after the title (viewer slide 2, on-slide label 1). SVG slide ID `slide-cloud-opening`; 101 slides total. Original slides remain after it.
- Title: Applications are moving to the cloud. Diagram: Services, Analytics and LLM-powered apps feed licensed cloud services; compute servers connect to a locked proprietary-LLM model; two benefit pills show massive scale and less hardware management.
- User verbatim script is saved in this slide’s speaker notes in deck.json. Framing scopes model ownership/access to proprietary LLMs.
- New slide built in editable SVG, using Rubik, blue title rule, thin outlined diagrams and teal benefit pills. No animations yet on this new slide.
- Backup before insertion: work/revisions/before-cloud-opening/. One-time authoring script: work/add_cloud_slide.py; DO NOT rerun because it inserts a duplicate.

## Browser preference and automatic focus

- User explicitly wants the live deck in their default browser, Brave, NOT the in-app browser. Do not create or show IAB tabs for this task. Open and verify in Brave.
- Viewer now hashes each authored SVG slide and stores signatures in sessionStorage. On live refresh it automatically selects the first new/changed slide by ID; unchanged refreshes retain the current slide. Playback state does not count as an edit. No separate focus update is needed for normal SVG edits.

- Verified automatic focus in Brave: navigated to title, changed a harmless attribute on the cloud slide, and observed Brave refresh and jump back to viewer slide 2. Closed the IAB preview. Reuse the existing Brave deck tab via native CUA; do not open another browser tab.

- User requests silent edits from now on: no progress narration or screenshots in replies. Apply each dictated addition and verify in the existing Brave tab.
- Slide 1 addition: explicitly labels entire application stacks with “Many companies now run”; names GCP, AWS, Azure inside the cloud. Added verbatim script to notes.

- Added user Slide 2 (viewer slide 3), SVG ID slide-cloud-trust: “Can we trust the cloud provider?” Entire platform stack (application, OS, hypervisor, CPU, memory, disks, network) paired with questions about correct execution, snooping, tampering. User script preserved in notes. 102 slides total.

- Slide 2 revision: merged snooping and tampering into one question box, “Snoops on / tampers with my data?”, beneath the correct-execution question.

- Added user Slide 3 (viewer slide 4), SVG slide-integrity-scope: “This talk: Application integrity”. Application branches into execution/memory (CPU and RAM icons) and persistent storage (disk cylinder). Script in notes. 103 slides total.

- Added user Slide 4 (viewer slide 5), SVG slide-security-cost: qualitative security/cost scatterplot with secure boot, dm-verity and Byzantine agreement, plus compute replicas. No numeric measurements implied; source script preserved. 104 slides total.

- User Slide 5 reuses original TEE slide id2 in place (viewer 6; total remains104). Original AMD/Intel logos and both protection capsules retained, with client attestation + authenticated encrypted channel into CPU-protected application/memory. Corrected AMD SEV-SNP; clarification and sources in notes. Original source backed up before-tee-slide.

- User Slide 5 pill fix: replaced stretched source capsules with 350×68 softly rounded panels, 25px Rubik, thin blue outlines.
- User Slide 6 replaces original overhead slide id3 (viewer7) with Slide4 graph at identical coordinates, adding low-cost TEE point and <10% memory-suite overhead callout (AMD7.29%, Intel4.06%). Paper verified; workload scope explicit, citation linked and notes explain exceptions. Total104.

- User Slide 7 reuses original ideal-TEE table id7, moved from viewer11 to viewer8 (no duplication; total104). Title “What do TEEs actually protect?” Header “TEE claims”; execution✅, memory✅, persistent-state integrity❌; purple takeaway “Persistent state needs additional protection”. Original table fills, geometry, symbols retained. Old animations cleared.

- User Slide8 inserted viewer9, slide-tee-vulnerability-timeline, total105. Three-paper BadRAM→BatteringRAM→DDRop timeline. Reports instead of unknown discovery dates; BadRAM complete vendor firmware1Oct2024 vs public10Dec; subsequent two unpatched under physical-interposer model as of16Nov2026. Detailed dates, caveats and primary-source citations in notes.

- User Slide9 reuses real-TEE table id9, moved viewer14→viewer10; total105. Same ordered rows as Slide7, TEE claims and Real TEEs columns. Original mask icons retained at natural aspect with explicit “Conditional” labels for execution/memory; persistent-state cross in both columns. Takeaways emphasize uncompromised TEE and difficult exploitation/physical access.

- Slide8 simplified: quiet relative-duration lines for LVI (4Apr2019 discovery→10Mar2020 software mitigation), SmashEx (3May2021 report→13Jul2021 runtime patches; discovery earlyMay only), BadRAM retained (26Feb2024 report→1Oct2024 firmware). BatteringRAM/DDrop removed. Exact date semantics and primary citations in notes.

- Slide8 now has one chronological line, LVI → SmashEx → BadRAM. Vulnerable durations proportional, inter-study gaps compressed with breaks; date ranges below each interval.

- Project published to git@github.com:grapheo12/quals-talk.git (main), GitHub Pages at https://grapheo12.github.io/quals-talk/. GitHub Actions builds with python work/build_web.py --static into outputs/site. Static viewer disables local revision polling/autofocus; existing localhost live deck still works. Source PPTX included in source/. Generated outputs/revision backups ignored by Git.

- Publishing instruction: continue editing and previewing on localhost. Do NOT push commits or publish updates after ordinary edits. Only push to git@github.com:grapheo12/quals-talk.git when the user explicitly says "push remote" (or otherwise explicitly requests publishing). GitHub Pages deploys automatically after that push.

- Inserted unnumbered sentinel slide-old-slides-divider after user Slide9 (viewer11); total106. "Old slides below" / "End of revised slides". All subsequent slides await revision. Insert newly dictated slides BEFORE this divider and keep it marking the revised/original boundary. Local only.

- User Slide10 inserted before sentinel as viewer11, slide-tee-plus-question. Large blue circle containing TEEs + original AMD/Intel logos, blue plus, purple question mark. Preserve performance/cost takeaway. Sentinel now viewer12; total107. Local edits only.

- Added user Slides11–14 (viewer12–15): crossed-out Byzantine agreement; Cautious Trust reveal; original vector abstract audit diagram reused with readable labels; then same diagram plus HarborMaster (VLDB 2026) and Pirateship (SOSP 2026). Original id15 remains below divider as reference. Sentinel now viewer16; total111. Local only.

- Speaker notes now always visible in a bottom panel occupying 30vh, including Present mode. deck.json speakerScript is the exact dictated narration with angle-bracket directives and research/editorial notes removed. Preserve exact user wording; write future narration to speakerScript as well as notes. Reference notes button retains research/authoring material. Original slides use their source spoken notes, minus directives.
- Build groups use deck.json slideGroup {id,number,title}. Viewer positions11–13 (TEE + ? / crossed-out BFT / Cautious Trust) grouped as11a–c, on-slide footer11. Positions14–15 (audit diagram / two systems) grouped14a–b, footer14. User explicitly used viewer numbering for these groupings; retain group numbers11 and14. Sidebar dropdowns; build-specific script; navigation preserves all frames in order; jump accepts11b,14b or basegroup11/14. Hashes still physical viewer indices for stable links. Total111 frames, sentinel position16. No remote push.

- Numbering correction: logical slide numbers now advance once per group, automatically computed by viewer. Groups11a–c then12a–b; sentinel13, subsequent original slide14, etc. 108 logical slides /111 physical frames. All existing footer numbers synchronized with logical sidebar numbers (title remains without a footer; divider remains unnumbered on canvas). deck.json displayNumber records the logical number; number and URL hashes retain physical indices. Future insertions must synchronize SVG footer numbers. This supersedes the earlier instruction to keep group14.

- Logical Slide13 added: HarborMaster section title, slide-harbormaster-section, physical viewer16. Large Rubik title with long blue underline; detects bold purple, persistent storage bold blue. Exact narration in speakerScript. Divider now logical14/viewer17;109 logical slides/112 frames. Local only.

## User macro: Generate PPTX <slide number>

- Explicit user-defined macro, saved 2026-11-16: “Generate PPTX N” means export the current live deck from the title through logical Slide N inclusive into a new downloadable .pptx. Include every lettered build, maintaining its shared on-slide number. For N=13 this is 16 PowerPoint slides (11a–c and12a–b included), ending at HarborMaster and excluding the old-slides divider.
- Required: native editable PowerPoint text, shapes, freeform paths and icons for diagrams. Only company logos or genuinely image-specific assets may be pictures. Never flatten a slide to an image. Preserve Rubik, colors, dimensions, source positions and exact spoken scripts as speaker notes. Do not alter/reimport the live deck or push remote as part of this macro.
- Reusable export entry: work/generate_pptx.py N. Uses work/pptx-export/extract_native_scene.py, generate.mjs (Artifact Tool) and finalize.mjs. Read the presentations/PPTX skill when exporting, execute the wrapper with bundled Python, and visually review the final PPTX rendered through LibreOffice before delivery. The extraction supports the SVG features currently used through Slide13; inspect and extend explicitly for future source constructs. All four AMD logo instances are the only pictures in the initial export; Intel and diagrams are native paths.
- Initial export checks: 16 slides, original 13.3333×7.5in dimensions, Rubik text, package integrity, layout/font policy and reimport passed. Built-in chart/table geometry is represented by native shapes, preserving the qualitative plots. Round check/cross/mask emoji converted to editable native icon shapes. Final PPTX contains no full-slide images. Speaker notes exclude authoring directives.
- Restored the qualitative-comparison footnotes on Slides5/7 and Misono citation on7 after discovering that broad y=692 footer replacement had overwritten them. Future footer renumbering must target x=1182,y=692 (or CustomPageNumber), never every text node at y=692.

- Logical Slide14: moved original rollback attacks slide id72 from physical84 to17, before the sentinel (now logical15/physical18). Original four-click animation XML, shape IDs and motion/fade effects preserved unchanged. User introduction plus original X=1 → write X=2 → VM down → rollback → restart/read X=1 narration saved as speakerScript, without directives. 112 frames/109 logical slides unchanged. Local only.

- Rollback slide conversion repair: six unused static TEE-icon copies were exposed by the original SVG conversion (absent from original slide-072.jpg). Hidden their nonanimated top-level groups with display=none, retaining source vectors. Four original timeline nodes and all animation targets/effects remain unchanged.

- Slide14 narration completed: signed write X=2; VM goes down; provider restores signed X=1; restart verifies the old signature and reads stale X=1. Ends with authenticity versus freshness. User introduction preserved; animation and artwork unchanged.

- User preference: reuse existing slides and visual assets as much as possible for subsequent edits.
- Slide15 promotes original id74 Detecting Rollbacks through Logging, all five animation builds preserved; six unused icon copies hidden as on14. Exact dictated speaker script. Physical18.
- Slide16 promotes id69 Scaling up and reuses original id71 service-mesh vectors; Spark/Flink/microservices heading, 100s of nodes callout. Exact dictated script. Physical19; sentinel now logical17/physical20. Counts112/109 unchanged. Local only.

- Slide17 promotes original id75 Logging problems at scale (physical20), preserving both animation steps including message motion. Node2 state and message changed X=3 to X=2 to match dictated script. Exact speaker wording saved with formatting backslashes removed. Divider logical18/physical21; counts112/109 unchanged. Local only.

- Slide18 promotes original id76 single-log vs multi-log comparison, exact dictated script and both animations. Slides19–21 are requested unchanged copies of id77/id78/id79 (single-log overhead, multi-log independent writes, multi-log amplification). Clone IDs prefixed single-log-19-, multi-log-20-, multi-log-21-; all original animation steps copied and remapped with validation. Originals remain below divider. Footer numbers updated only. Divider logical22/physical25. Counts115 physical/112 logical. Local only.

- Removed the then-current logical Slides23–37 inclusive at user request (15 original slides from TEE application popularity through At a glance (2)). Recoverable backup and title list in revisions/before-removing-slides-23-37. Divider stays22; Pirateship now23. 100 physical frames/97 logical slides. Remaining animation/metadata references validated. Local only.

- Slide22a/b reuses original id80 scalable rollback requirements and its exact callout artwork. Converted the original click reveal to two grouped frames: 22a hides id266; 22b cloned IDs requirements22b-* shows it. Exact new narration per build; shared footer22. Divider23/physical27. 101 frames/97 logical slides (original moved, one build added). Local only.

- Copied then-current logical78–85 after22, retaining originals and animation trees with uniquely prefixed IDs causality-copy-0- through7-. New23 single-node causality;24a–d multi-node causal history;25 tracking-causality transition;26a–b vector clocks. Original speaker scripts retained. Divider27/physical35. 109 physical/101 logical. Local only.

- Slide27 promotes original id89 HarborMaster architecture, redrawn with original compute/detective/storage/lock vectors and green Cautious Trust ledger. Based on attached HarborMaster paper Fig2 (p4/2129): parallel TEE workers → vector-clock log entries → replicated TEE storage → asynchronous TEE auditor recreating worker state/checking causality. Exact narration retained. Divider28/physical36. Counts109/101 unchanged. Local only.

- Slide27 layout correction: compute stays RIGHT, auditor LEFT, matching the earlier Cautious Trust convention. Three separate per-worker logs with explicit three-component vector clocks; shared fault-tolerant storage below. Reused vectors fitted to visible artwork bounds; consistent blue closed padlocks inside worker/auditor boundaries and cylinder fronts. Exact narration unchanged. Verified live in Brave on27. Only id89 and its metadata changed. Authoring helper refine_harbormaster_architecture_27.py. Local only.

- Slide26b font repair: five causal-history vector-clock labels still referenced unavailable Neue Haas Grotesk Text Pro and fell back to a serif face. All six history-clock labels now use Rubik bold, without forced glyph stretching, centered at their original label centers. Geometry, clock values, narration and animation definitions unchanged.
