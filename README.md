# Qualifying exam talk

Shubham Mishra's Berkeley PhD qualifying-exam deck, covering HarborMaster and Pirateship.

Live site: https://grapheo12.github.io/quals-talk/

## Present

Use the outline or slide-number field to jump to a slide or lettered build (for example, `26b`). Space / right arrow advances an animation build; left arrow returns to the previous slide. **F** toggles presentation mode, **N** toggles reference notes, and Escape exits presentation mode. The spoken script remains visible in the bottom panel. Grouped builds share one slide number; URL hashes use the underlying frame index, including each build.

## Implementation

This is a custom viewer built with plain HTML, CSS and JavaScript, rather than a slide framework such as Reveal.js. Slides use editable SVG artwork with embedded fonts and images. The original conversion retains LibreOffice's JavaScript presentation and animation runtime; subsequent slides are edited directly in SVG. JSON supplies the outline, grouped builds and narration. A small Python server supplies local live reload and automatic selection of the edited slide, while GitHub Pages serves a static build without Python.

## Edit locally

Python 3 is sufficient to build and serve the deck:

```sh
python3 work/serve_web.py
```

Open http://127.0.0.1:8765/ in your browser. Editing the source refreshes the deck and selects the changed slide.

- `work/editable-deck.svg`: authoritative slide artwork and animation runtime, with fonts and images embedded.
- `work/deck.json`: outline, search text, scripts and source citations.
- `work/viewer.html`: presentation controls and live editing support.
- `work/build_web.py`: portable static/offline build.
- `source/Quals Talk Local.pptx`: unchanged original deck.
- Other files in `work/` preserve conversion assets, original slide references, and one-time editing scripts. Those scripts document past edits; do not rerun them on the current deck. SVG editing scripts use `lxml`.

The current SVG and JSON are the source of truth; conversion does not run during a normal build. Local revision snapshots and generated previews are omitted from Git.

## Publish

```sh
python3 work/build_web.py --static
```

This creates `outputs/site/index.html` and `outputs/site/deck.svg`. All asset references work under the `/quals-talk/` project path. The static site has no server dependency; live editing and automatic selection of changed slides remain local features.

Pushing `main` runs the GitHub Pages workflow. Repository **Settings → Pages → Source** must be **GitHub Actions**. The site includes the spoken scripts in the bottom panel and additional sources under **Reference notes**.

To build a single-file offline copy, run `python3 work/build_web.py` and open `outputs/Qualifying Exam.html`.

## Generate PPTX macro

“Generate PPTX N” exports the current deck through logical slide N, including all lettered builds. Text, diagrams, charts drawn as shapes, and icons remain native editable PowerPoint objects; company logos may remain images. Spoken scripts become speaker notes. The old-slide divider is excluded when it is beyond the requested cutoff.

The reusable local export workflow is `work/generate_pptx.py N` (run with the bundled Python runtime). Each exported file is validated, then visually reviewed before delivery. This does not publish the web deck.
