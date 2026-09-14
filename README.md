# Becca's Closet

A tiny static shop: 393 curated pieces, filters, a saved list, and no backend.
Everything is plain HTML, CSS and JavaScript, so it runs from any static host.

## Files

- `index.html`, `styles.css`, `app.js` — the site
- `data.js` — the catalog (generated from the spreadsheet)
- `images/full/` — full-size product photos for nearly every piece, `images/thumbs/` — small previews for the handful that could not be fetched
- `build/` — the scripts that turned the spreadsheet into `data.js` and the images, plus the scraped
  descriptions (`desc_final.json`) and the occasion re-tagging (`occ/out_*.json`). Not needed to run the site.

## Put it online with GitHub Pages

1. Sign in to GitHub and create a **new repository**. If you name it `<username>.github.io`
   the site lives at `https://<username>.github.io/`. Any other name gives
   `https://<username>.github.io/<repo>/`. Both work.
2. Upload everything in this folder. The web uploader only takes 100 files at a time,
   so use GitHub Desktop or the command line:

   ```bash
   cd "/Users/piano/Documents/Claude Code/Beccas Closet"
   git init && git add -A && git commit -m "Becca's Closet"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```
3. In the repository, open **Settings → Pages**. Under *Build and deployment* choose
   **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
4. Wait a minute or two, then open the URL shown on that page. Point Bitly at it if you like.

## Things you might want to change

- `app.js`, top of the file: `HER_EMAIL` and `BCC_EMAIL` control where "Email me my list" goes.
  Set `BCC_EMAIL` to `''` to stop copying yourself.
- The headline copy lives in `index.html` under `<header class="hero">`.
- To change the catalog, edit the spreadsheet and rerun `build/extract.py`, `build/merge_desc.py`, then
  `build/make_data.py` (see the scripts for paths).
- Occasion tags were re-assigned from each item's fabric and cut using this rubric: *teaching* = polished,
  modest, comfortable all day; *dance* = breathable fabric, room to move, hides sweat; *hang* = casual and
  comfy; plus *friend*, *dressy*, *outdoors*. Each item's detail view shows the one-line reason. To override a
  tag, edit the matching entry in `build/occ/out_*.json` and rerun `build/make_data.py`.

## How the saved list works

Hearts are stored in the browser's local storage and mirrored into the page URL as
`#saved=…`. Reloading keeps the list; copying the share link carries it to any other
device; "Email me my list" opens a pre-written email with every piece and the link.
