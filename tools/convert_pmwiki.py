#!/usr/bin/env python3
#######################################################################
#                                                                     #
#              BKBoK - Beekeeping Book of Knowledge                   #
#                                                                     #
#######################################################################
#
# File:
#   tools/convert_pmwiki.py (BKBoK repo)
#
# Purpose:
#   One-time conversion of the PmWiki site at https://bkbok.info into
#   plain HTML pages at the top of this repo. Kept as a record of how the pages
#   were made; from now on the HTML files are edited directly and this
#   is not run again (it would overwrite those edits).
#
#   Input is a folder made by fetching the live site:
#       html/Main.<Page>.html   each page as PmWiki showed it
#       src/Main.<Page>.txt     each page's ?action=source
#       files/<name>            everything in bkbok.info/Images/
#
#       python3 tools/convert_pmwiki.py <that folder>
#       python3 tools/build_site.py
#
#   For each page it takes PmWiki's <div id='wikitext'>, drops the
#   hidden ">>comment<<" blocks and the standard footer table, turns
#   wiki links into relative X.html links, marks links to other sites
#   class="online" (the stylesheet adds the arrow, so the hand-typed
#   arrows after them go), points bkbok.info/Images/ at the local
#   Images/ folder and wraps it all in the site's header and footer.
#   Needs BeautifulSoup (beautifulsoup4).
#
# Version
#   1.0 - 22 November 2026
#   1.1 - 22 November 2026 - class="online" no longer split into letters
#
#######################################################################

import html
import os
import re
import shutil
import sys
import unicodedata
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment, NavigableString

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = REPO                           # the site is the repo's top level
SITE_URL = "https://bkbok.info/"

# Pages not carried over: PmWiki's own, the page template, and pages
# whose only use was editing the wiki.
SKIP = {"Template", "WikiSandbox", "RecentChanges",
        # left out 22 November 2026 (Rich): how to edit the wiki, and
        # empty "still in development" pages nothing linked to
        "Guidelines", "LangstrothHives", "QueenRearing", "RecordKeeping",
        "ShookSwarm", "SmallHiveBeetle", "SpanningCover", "SwarmTraps",
        "VarroaSensitiveHygiene"}
# Page -> the page it now is.
SAME_AS = {"HomePage": "index", "About": "AboutThisSite",
           # old copies of other pages, left out 22 November 2026 (Rich)
           "SplittingHives": "SplittingColonies",
           "InspectionInspectionAndActionRecord": "InspectionAndActionRecord",
           "VarroaSensitiveQueen": "GeneticStock"}


def file_name(page):
    '''PmWiki page name (after "Main.") -> HTML file name without .html.'''
    page = SAME_AS.get(page, page)
    return unicodedata.normalize("NFKD", page).encode("ascii", "ignore").decode()


def page_link(n):
    '''"Main.X#frag" from an index.php?n= link -> (href or None).'''
    n = unquote(n)
    target, _, frag = n.partition("#")
    target = target.split("?")[0]
    group, _, page = target.partition(".")
    if group == "Main" and page and page not in SKIP:
        return file_name(page) + ".html" + ("#" + frag if frag else "")
    if group == "PmWiki":
        return "https://www.pmwiki.org/wiki/PmWiki/" + page
    return None


def slug(text, used):
    s = re.sub(r"[^A-Za-z0-9]+", "-", unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()).strip("-")
    s = s or "section"
    base, n = s, 2
    while s in used:
        s = "%s-%d" % (base, n)
        n += 1
    used.add(s)
    return s


def local_image(url):
    m = re.match(r"https?://bkbok\.info/images/(.+)$", url, re.I)
    return "Images/" + m.group(1) if m else None


def clean(soup, this_file):
    '''Tidy PmWiki's wikitext in place.'''
    # hidden ">>comment<<" blocks
    for d in soup.find_all(style=re.compile(r"display:\s*none")):
        d.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    # the standard footer (About this Site / Disclaimer) - the page footer has it now
    for t in soup.find_all("table"):
        if "Disclaimer" in t.get_text() and "About this Site" in t.get_text():
            t.decompose()
    # the "----" every page starts with, under the title
    for el in list(soup.children):
        if isinstance(el, NavigableString) and not el.strip():
            continue
        if el.name == "div" and "vspace" in el.get("class", []) and not el.contents:
            el.decompose()
            continue
        if el.name == "hr":
            el.decompose()
        break

    # wiki links
    for a in soup.find_all("a"):
        cls = a.get("class", [])
        href = a.get("href", "")
        if "createlink" in cls:            # the "?" after a link to a page that doesn't exist
            a.decompose()
            continue
        if "createlinktext" in cls:        # ... and its text
            a.unwrap()
            continue
        m = re.match(r"https?://bkbok\.info/index\.php\?n=([^'\"]+)$", href, re.I)
        if m or re.match(r"https?://bkbok\.info/(index\.php)?$", href, re.I):
            new = page_link(m.group(1)) if m else "index.html"
            if new is None:                # e.g. Profiles.RichColvin
                a.unwrap()
                continue
            a.attrs = {"href": new}
            if new.startswith("https://"):
                a.attrs.update({"class": "online", "target": "_blank", "rel": "noopener"})
            continue
        img = local_image(href)
        if img:
            a.attrs = {"href": img}
            if not img.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                a["download"] = img.split("/")[-1]
            continue
        if re.match(r"https?://bkbok\.info/images/?$", href, re.I):
            a.unwrap()                     # "the image will be in the folder https://BKBoK.info/Images"
            continue
        if href.startswith(("http://", "https://")):
            a.attrs = {"class": "online", "href": href, "target": "_blank", "rel": "noopener"}
            # the hand-typed arrow after it - the stylesheet draws one now
            nxt = a.next_sibling
            if isinstance(nxt, NavigableString) and re.match(r"\s*[↗]", str(nxt)):
                nxt.replace_with(re.sub(r"^(\s*)↗", r"\1", str(nxt), count=1))
            continue
        if href.startswith("mailto:"):
            a.attrs = {"href": href}
            continue
        if href.startswith("#"):
            a.attrs = {"href": href}
            continue

    for img in soup.find_all("img"):
        src = img.get("src", "")
        img["src"] = local_image(src) or src
        img.attrs.pop("title", None)
        if img.get("width", "").endswith("px"):
            img["width"] = img["width"][:-2]
        if img.get("height", "").endswith("px"):
            img["height"] = img["height"][:-2]
        if src.startswith("http") and not local_image(src):
            img["loading"] = "lazy"

    # %new% / %newwin% wrappers, and the old "navy" colour on headings
    for s in soup.find_all("span", class_="new"):
        s.unwrap()
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        for s in h.find_all("span", style=re.compile(r"color:\s*navy")):
            s.unwrap()
    # PmWiki's anchors ([[#IPM]]) stay; headings get ids for search and linking
    used = {a["id"] for a in soup.find_all(id=True)}
    for h in soup.find_all(["h1", "h2", "h3"]):
        if not h.get("id"):
            text = h.get_text(" ", strip=True)
            if text:
                h["id"] = slug(text, used)
        for s in list(h.contents):
            if isinstance(s, NavigableString) and s.startswith(" ") and s is h.contents[0]:
                s.replace_with(s.lstrip())
    for el in soup.find_all(class_=True):
        cls = el["class"].split() if isinstance(el["class"], str) else el["class"]
        el["class"] = [c for c in cls if c not in ("wikilink", "urllink", "selflink")]
        if not el["class"]:
            del el["class"]
    for el in soup.find_all(rel="nofollow"):
        del el["rel"]


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_text}</title>
<link rel="stylesheet" href="bkbok-docs.css">
<script src="search-index.js" defer></script>
<script src="bkbok-docs.js" defer></script>
<link rel="icon" href="favicon.ico">
</head>
<body>
<header class="site-header">
  <a class="brand" href="index.html" title="Index">
    <img src="Images/BKBoK_Banner.png" alt="Beekeeping Book of Knowledge" width="716" height="60">
  </a>
  <nav class="site-nav" aria-label="Site">
    <a href="index.html">Index</a>
    <a href="AboutThisSite.html">About This Site</a>
  </nav>
</header>
<main class="page">
  <p class="crumbs">{crumbs}</p>
  <h1>{title}</h1>

  <div class="content">
{content}
  </div>
<!--pager--><!--/pager-->
</main>
<footer class="site-footer">
  <div class="footer-links">
    <div><a href="AboutThisSite.html">About this Site</a></div>
    <div class="footer-contact">Questions or comments?<br>
      <a href="mailto:BeekeepingBoK@gmail.com">BeekeepingBoK@gmail.com</a></div>
  </div>
  <p><strong>Disclaimer:</strong> The process of beekeeping can cause injury or be a health hazard unless proper precautions are taken, including the wearing of appropriate protective equipment.</p>
  <p class="copyright">This work is licensed under a <a class="online" href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">Creative Commons Attribution-ShareAlike 4.0 International License</a>.</p>
</footer>
</body>
</html>
"""


def title_of(raw_html, src):
    m = re.search(r"\(:title\s+(.*?)\s*:\)", src)
    if m:
        return html.unescape(m.group(1))
    m = re.search(r"class='pagetitle'[^>]*>(.*?)<", raw_html, re.S)
    return html.unescape(m.group(1).strip()) if m else ""


def main():
    raw = sys.argv[1]
    os.makedirs(os.path.join(OUT, "Images"), exist_ok=True)
    pages = {}
    for f in sorted(os.listdir(os.path.join(raw, "html"))):
        page = f[len("Main."):-len(".html")]
        if page in SKIP or page in SAME_AS and SAME_AS[page] != "index":
            continue
        pages[page] = f

    for page, f in pages.items():
        raw_html = open(os.path.join(raw, "html", f), encoding="utf-8").read()
        src = open(os.path.join(raw, "src", f[:-5] + ".txt"), encoding="utf-8").read()
        name = file_name(page)
        override = os.path.join(REPO, "tools", "restored", page + ".html")
        if os.path.exists(override):       # pages put back from their history (spam)
            body = open(override, encoding="utf-8").read()
        else:
            a = raw_html.index("<div id='wikitext'>")
            b = raw_html.index("<!--PageFooterFmt-->")
            body = raw_html[a:b]
            body = body[:body.rindex("</main>")]
            body = body[:body.rindex("</div>")] + "</div>"
        soup = BeautifulSoup(body, "html.parser")
        wt = soup.find("div", id="wikitext") or soup
        clean(wt, name)
        content = "".join(str(c) for c in wt.contents).strip()
        title = title_of(raw_html, src)
        if name == "index":
            crumbs = "<span>Beekeeping Book of Knowledge</span>"
            title_text = "Index – Beekeeping Book of Knowledge (BKBoK)"
        else:
            crumbs = '<a href="index.html">Index</a> <span aria-hidden="true">›</span> <span>%s</span>' % html.escape(title)
            title_text = "%s – Beekeeping Book of Knowledge" % title
        text = PAGE.format(title_text=html.escape(title_text, quote=False), crumbs=crumbs,
                           title=html.escape(title, quote=False), content=content)
        text = text.replace("\t", "    ")
        open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8").write(text)

    for f in os.listdir(os.path.join(raw, "files")):
        if f in ("favicon.ico",):
            shutil.copy(os.path.join(raw, "files", f), os.path.join(OUT, f))
        else:
            shutil.copy(os.path.join(raw, "files", f), os.path.join(OUT, "Images", f))
    print("%d pages written to %s" % (len(pages), OUT))


if __name__ == "__main__":
    main()
