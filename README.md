# Qualifying exam talk

Shubham Mishra's Berkeley PhD qualifying-exam deck, covering HarborMaster and Pirateship.

Live site: https://grapheo12.github.io/quals-talk/

## Present

Use the outline or slide-number field to jump to a slide. Space / right arrow advances an animation build; left arrow returns to the previous slide. **F** toggles presentation mode, **N** toggles speaker notes, and Escape exits presentation mode. A URL ending in `#9` opens viewer slide 9 (content slide 8, because the title is counted in the viewer).

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

Pushing `main` runs the GitHub Pages workflow. Repository **Settings → Pages → Source** must be **GitHub Actions**. The site includes the deck's speaker notes, available using the Notes button.

To build a single-file offline copy, run `python3 work/build_web.py` and open `outputs/Qualifying Exam.html`.
