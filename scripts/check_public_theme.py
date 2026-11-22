"""Audit the complete generated public catalogue and its shared brand palette."""
from pathlib import Path
from html import escape
import sys
import json

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_programme_seo import normalize_unis, slug
from programme_actions import tuition_range
from hashlib import sha1

manifest=json.loads((ROOT/"programmes/catalog-manifest.json").read_text())
generated=[ROOT/p for p in manifest["generated_files"] if p.endswith(".html")]
assert len(generated)>=3500, "Incomplete generated programme catalogue"
for file in generated:
    assert file.is_file(),file
    body=file.read_text(encoding="utf-8")
    assert "/guides/style.css?v=20261119-landing" in body, f"No public brand stylesheet: {file}"
    assert '/programmes/catalog.css' in body, f"No catalogue palette: {file}"
    assert body.count("<h1") == 1, f"Expected one programme heading: {file}"

total=0
priced=0
for uni in normalize_unis():
    code=str(uni["shortName"])
    university_slug=slug(code,36)
    for course, raw in uni["programmes"].items():
        filename=slug(course,72)+"-"+sha1(course.encode("utf-8")).hexdigest()[:6]+".html"
        rel=f"courses/{university_slug}/{filename}"
        eng=(ROOT/"programmes"/rel)
        assert eng.is_file(),eng
        html=eng.read_text(encoding="utf-8")
        for marker in ("catalog-breadcrumb","catalog-course-nav","catalog-fact","catalog-application-questions",
                       "ng-related-actions","catalog-verified","data-ng-action=\"apply\""):
            assert marker in html,(eng,marker)
        assert "ng-related-media" not in html, f"Decorative gallery remains on {eng}"
        assert '<a href="/programmes/find/">Course finder</a>' in html,(eng,"finder breadcrumb")
        assert f'<a href="/programmes/universities/{university_slug}.html">University programmes</a>' in html,(eng,"university breadcrumb")
        assert '"BreadcrumbList"' in html,(eng,"structured breadcrumb")
        expected=tuition_range(raw,uni.get("currency","MYR"))
        if expected != "Tuition not listed in finder":
            assert escape(expected,quote=True) in html,(eng,expected)
            priced+=1
        for lang in ("ar","zh"):
            mirror=ROOT/"programmes"/lang/rel
            assert mirror.is_file(),mirror
            localized=mirror.read_text(encoding="utf-8")
            for marker in ("catalog-breadcrumb","catalog-course-nav","catalog-fact","catalog-application-questions",
                           "ng-related-actions","catalog-verified"):
                assert marker in localized,(mirror,marker)
            assert localized.count('class="catalog-fact"') == html.count('class="catalog-fact"'),mirror
            assert f'/programmes/{lang}/courses/' in localized, f"Missing localized course URLs: {mirror}"
        total+=1
assert total==manifest["programme_listings"]==manifest["detailed_programme_pages"],(total,manifest)

for folder in ("guides","services","ar","zh","fr","ms"):
    for file in (ROOT/folder).rglob("*.html"):
        body=file.read_text(encoding="utf-8")
        assert "/guides/style.css" in body,(file,"shared stylesheet")
for file in (ROOT/"about-nextgenz-centre.html", ROOT/"why-malaysia.html"):
    contents = file.read_text(encoding="utf-8")
    assert "/guides/style.css" in contents,file
    assert 'lang="en" title="Current page in English"' in contents,file
    assert "Related Arabic study guide, not a translation of this page" in contents,file
    assert "Related Chinese study guide, not a translation of this page" in contents,file
    assert ('href="' + '/' + file.name + '" lang="en"') in contents,file
theme=(ROOT/"guides/style.css").read_text(encoding="utf-8")
landing=(ROOT/"index.html").read_text(encoding="utf-8")
for colour in ("#F0E3D2","#C5A059","#0F1F38"):
    assert colour in theme and colour in landing,colour
assert "NEXTGENZ PUBLIC THEME CONTRACT" in theme
assert "ng-landing-nude-theme" in landing
assert "featuredShown" in landing and "featuredAutoplay" in landing
print(f"PASS: {len(generated):,} generated pages themed, {total:,} courses with Arabic/Chinese layout parity and {priced:,} displayed finder fee references.")
