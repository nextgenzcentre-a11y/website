#!/usr/bin/env python3
"""Audit static NextGenz links and sitemap targets without modifying the website."""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import sys

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = {"nextgenzcentre.space", "www.nextgenzcentre.space"}
VIRTUAL_ROUTES = {
    "student", "studentportal", "agent", "agentportal",
    "registerasstudent", "registerasagent",
}

def local_target(source: Path, ref: str) -> Path | None:
    ref = ref.strip()
    if not ref or ref[0] == "#" or "${" in ref or "{{" in ref:
        return None
    parsed = urlsplit(ref)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc and parsed.netloc.lower().split(":")[0] not in DOMAINS:
        return None
    if not parsed.path:
        return None
    url_path = unquote(parsed.path)
    if url_path.startswith("/"):
        relative = url_path.lstrip("/")
    else:
        relative = str(source.parent.relative_to(ROOT) / url_path)
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        return None
    if relative in VIRTUAL_ROUTES or relative.startswith("api/"):
        return None
    if path.is_dir() or url_path.endswith("/"):
        path /= "index.html"
    return path

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for attr in ("href", "src", "poster"):
            if attrs.get(attr):
                self.refs.append(attrs[attr])
        if attrs.get("srcset"):
            for value in attrs["srcset"].split(","):
                self.refs.append(value.strip().split()[0])
        if tag == "meta" and attrs.get("property") in {"og:image", "og:url"}:
            self.refs.append(attrs.get("content", ""))

def inspect() -> int:
    failures = defaultdict(list)
    html_files = sorted(ROOT.rglob("*.html"))
    href_total = 0
    for html in html_files:
        parser = Extractor()
        parser.feed(html.read_text(encoding="utf-8"))
        for ref in parser.refs:
            local = local_target(html, ref)
            if local is None:
                continue
            href_total += 1
            if not local.is_file():
                display = str(local.relative_to(ROOT))
                failures[display].append(str(html.relative_to(ROOT)) + " -> " + ref)
    tree = ET.parse(ROOT / "sitemap.xml")
    urls = [el.text for el in tree.iter() if el.tag.endswith("}loc") or el.tag == "loc"]
    for url in urls:
        target = local_target(ROOT / "index.html", url or "")
        if target is None or not target.is_file():
            failures[str(target.relative_to(ROOT)) if target else url or "(empty)"].append("sitemap.xml -> " + str(url))
    print(f"Checked {len(html_files)} HTML pages, {href_total} local references, and {len(urls)} sitemap URLs.")
    if not failures:
        print("PASS: no broken local links or missing sitemap targets")
        return 0
    print(f"FAIL: {len(failures)} distinct missing local targets")
    for path, refs in sorted(failures.items(), key=lambda p: (-len(p[1]), p[0])):
        print(f"  {path} [{len(refs)} occurrences]")
        for ref in refs[:4]:
            print("    ", ref)
    return 1

if __name__ == "__main__":
    sys.exit(inspect())
