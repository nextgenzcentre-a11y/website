"""Validate canonical, metadata and international SEO for every generated page."""
from pathlib import Path
import json
import re
from collections import Counter, defaultdict
from html import unescape
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.nextgenzcentre.space"
manifest=json.loads((ROOT/"programmes/catalog-manifest.json").read_text())
entries=[p for p in manifest["generated_files"] if p.endswith(".html")]
titles=defaultdict(list)
missing_schema=[]
long_titles=[]
short_descriptions=[]
duplicates=[]
total_alternates=0
for rel in entries:
    html=(ROOT/rel).read_text(encoding="utf-8")
    url=BASE+"/"+rel.removesuffix("index.html")
    def field(pattern):
        match=re.search(pattern,html,re.I|re.S)
        return unescape(match.group(1).strip()) if match else ""
    canonical=field(r'<link rel="canonical" href="([^"]+)"')
    title=field(r'<title>(.*?)</title>')
    desc=field(r'<meta name="description" content="([^"]*)"')
    lang=field(r'<html lang="([^"]+)"')
    og=field(r'<meta property="og:url" content="([^"]+)"')
    assert canonical==url,(rel,"canonical",canonical,url)
    assert og==url,(rel,"og:url")
    assert title and desc,(rel,"missing title or description")
    assert len(title)>15,(rel,"short search title",title)
    assert len(desc)>25,(rel,"short search description")
    assert lang in ("en","ar","zh-CN"),(rel,"language",lang)
    assert html.count("<h1")==1,(rel,"h1")
    locale="ar" if rel.startswith("programmes/ar/") else "zh" if rel.startswith("programmes/zh/") else "en"
    assert (lang=="en" if locale=="en" else lang.startswith(locale)),(rel,"wrong language")
    titles[(locale,title)].append(rel)
    if len(title)>70:long_titles.append((rel,len(title)))
    if len(desc)<75:short_descriptions.append((rel,len(desc)))
    scripts=re.findall(r'<script[^>]+type="application/ld\\+json"[^>]*>(.*?)</script>',html,re.I|re.S)
    for script in scripts:
        try:json.loads(script)
        except ValueError as exc:raise AssertionError((rel,"invalid JSON-LD",str(exc))) from exc
    if '/courses/' in rel:
        if locale=="en":
            assert 'BreadcrumbList' in html,(rel,"missing student breadcrumb schema")
        assert 'catalog-breadcrumb' in html,(rel,"missing visible breadcrumb")
        assert 'href="/programmes/find/"' in html,(rel,"missing search link")
    if not rel.startswith("programmes/find/") and (rel.startswith("programmes/ar/") or rel.startswith("programmes/zh/") or rel.startswith("programmes/courses/")):
        alternates=dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"',html))
        assert len(alternates)>=3,(rel,"missing hreflang links")
        assert alternates.get("x-default", "").startswith(BASE+"/programmes/"),(rel,"x-default")
        for code in ("en","ar","zh-Hans"):
            alt=alternates.get(code)
            assert alt,(rel,"missing locale "+code)
            target=ROOT/alt.removeprefix(BASE+"/").lstrip("/")
            if alt.endswith("/"):target=target/"index.html"
            assert target.is_file(),(rel,"broken alternate",alt)
        total_alternates+=1
duplicates=[(key,items) for key,items in titles.items() if len(items)>1]
assert not duplicates,duplicates[:6]
assert len(entries)>=3500
print("PASS: SEO canonical and title audit: ",len(entries),"pages;",total_alternates,"hreflang groups;",len(duplicates),"duplicate locale titles.")
print("Advisory: long page titles",len(long_titles),"and short descriptions",len(short_descriptions))
if long_titles:print("Example long titles:",long_titles[:4])
if short_descriptions:print("Example short descriptions:",short_descriptions[:4])
