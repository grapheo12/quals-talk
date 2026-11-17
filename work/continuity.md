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
