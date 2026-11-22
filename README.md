# BKBoK - Beekeeping Book of Knowledge

The website at https://bkbok.info, as plain HTML pages. It was a PmWiki
site until 22 November 2026, when it was converted once to these files
(`tools/convert_pmwiki.py`, kept as a record). Edit the HTML files here
from now on; PmWiki is no longer the source.

## What's where

- `index.html` - the Index (the old wiki's HomePage), which is also the
  order of the Previous / Next links.
- One `.html` file per page, named as on the old wiki
  (`index.php?n=Main.Varroa` is `Varroa.html`).
- `Images/` - pictures and downloads, the same folder name as before so
  old links to them still work. `Images/BKBoK_Banner.png` is the header
  banner, recoloured for the honey header from `BKBoK_Logo.png`
  (`tools/recolour_logo.py`).
- `bkbok-docs.css` / `bkbok-docs.js` - the look, the search box and
  click-to-enlarge pictures (made from the Rosetta manuals' files).
- `search-index.js` - made by the builder; don't edit it.
- `tools/` - the builder, the one-time converter, the restored Bee Escape
  Board page, and `BKBoK_htaccess_redirects.txt` (the lines for the
  site's `.htaccess`). Not published.

## After editing, adding or renaming a page

    python3 tools/build_site.py

It rebuilds the search index and each page's Previous / Next links (in
the order the Index links the pages). A page needs a link on the Index
to get Previous / Next links; the exception is the Calendar's twelve
month pages, which go month by month round the year (December's Next is
January) with "All months" between. A second run changes nothing.

## Page rules

- Every page carries its own header and footer (copy an existing page).
- Links between pages and to pictures are relative (`Varroa.html`,
  `Images/Frame.png`).
- Links to other web sites get `class="online" target="_blank"
  rel="noopener"`; the stylesheet adds the arrow.
- No tab characters; dates as "dd Month yyyy".

## Colours (option B, chosen 22 November 2026)

Header honey gold `#ffc30b` with dark honey-brown text `#3b2500` (9:1),
cream page `#fffaf0`, headings `#6b4200` (8.4:1), links `#8a4b00`
(6.5:1). White text on the honey gold would be only 1.6:1.
