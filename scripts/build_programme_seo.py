#!/usr/bin/env python3
"""Build crawlable programme directories from the existing React ProgramFinder rawData.

Only reads index.html as the source of truth and writes /programmes/ plus the
auto-generated part of sitemap.xml. Does not change portal/Firebase behavior.

This is deliberately a staged search rollout: all finder names appear in
university and study-level directories, while a small set of high-intent,
non-composite programmes gets a detailed standalone page. Automatically
creating 1,182 near-identical search pages would not help students or SEO.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from datetime import date
from hashlib import sha1
from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re
import unicodedata
from programme_topics import TOPICS, matching_topics, generate_topic_pages
from programme_verified_facts import VERIFIED_PROGRAMMES

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE = "https://www.nextgenzcentre.space"
OUT = ROOT / "programmes"
TODAY = date.today().isoformat()
MARKER = "<!-- AUTO-GENERATED NEXTGENZ PROGRAMME DIRECTORY -->"
SITEMAP_START = "  <!-- NEXTGENZ PROGRAMME SEO START -->"
SITEMAP_END = "  <!-- NEXTGENZ PROGRAMME SEO END -->"
LEVELS = ["Foundation", "Diploma", "Bachelor", "Master", "Doctorate", "Other"]
LABELS = {
    "Foundation": "Foundation programmes",
    "Diploma": "Diploma programmes",
    "Bachelor": "Bachelor degree programmes",
    "Master": "Master degree programmes",
    "Doctorate": "PhD and doctorate programmes",
    "Other": "Other study pathways",
}
LEVEL_SLUG = {
    "Foundation": "foundation",
    "Diploma": "diploma",
    "Bachelor": "bachelor",
    "Master": "master",
    "Doctorate": "phd",
    "Other": "other",
}

def h(x: object) -> str:
    return escape(str(x or ""), quote=True)

def slug(text: str, length: int = 78) -> str:
    clean = unicodedata.normalize("NFKD", text)
    clean = clean.encode("ascii", errors="ignore").decode("ascii").lower()
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return (clean[:length].rstrip("-") or "programme")

def record_level(name: str) -> str:
    t = name.casefold()
    if re.search(r"\b(foundation|pre-university|a-level|ausmat)\b", t):
        return "Foundation"
    if "diploma" in t or "certificate" in t:
        return "Diploma"
    if re.search(r"\b(phd|ph\.d|doctorate)\b", t) or "doctor of philosophy" in t or "doctor of business administration" in t or "doctor of education" in t:
        return "Doctorate"
    if re.search(r"\b(master|masters|mba|msc|m\.sc|mmed|mphil|m\.phil|llm)\b", t):
        return "Master"
    if re.search(r"\b(bachelor|bsc|b\.sc|beng|b\.eng|bba|bca|bmus|ba \(hons\)|b\.a\.|llb)\b", t):
        return "Bachelor"
    if re.search(r"\b(doctor of medicine|doctor of dental|dental surgery|mbbs)\b", t):
        return "Bachelor"
    return "Other"

def normalize_unis() -> list[dict]:
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    opening = "const rawData = ["
    closing = "\n];\n\nconst allProgrammes"
    at = src.find(opening)
    if at < 0:
        raise RuntimeError("ProgramFinder database was not found; refusing to generate pages")
    end = src.find(closing, at)
    if end < 0:
        raise RuntimeError("ProgramFinder database end was not found")
    literal = src[at + len("const rawData = "):end + 2]
    # The existing database is a plain JavaScript object literal. Convert its
    # known unquoted property names and optional trailing commas to strict JSON.
    literal = re.sub(r'([,{]\s*)(university|shortName|type|currency|website|location|intakes|programmes)\s*:', r'\1"\2":', literal)
    literal = re.sub(r",\s*([}\]])", r"\1", literal)
    unis = json.loads(literal)
    if len(unis) < 20 or sum(len(u.get("programmes", {})) for u in unis) < 900:
        raise RuntimeError("ProgramFinder data appears incomplete; aborting rather than losing listings")
    return unis

def english_centres_from_finder() -> list[dict]:
    """Read the original public university/English-centre directory block."""
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    opening = "const NEXTGENZ_OTHER_INSTITUTIONS = ["
    closing = "\n];\nconst NG_FEATURED_CODES"
    at = src.find(opening)
    end = src.find(closing, at)
    if at < 0 or end < 0:
        raise RuntimeError("English-centre reference block not found")
    literal = src[at + len("const NEXTGENZ_OTHER_INSTITUTIONS = "):end+2]
    literal = re.sub(r'([,{]\s*)(university|shortName|type|currency|website|location|programmes)\s*:', r'\1"\2":', literal)
    literal = re.sub(r"\bnull\b", "None", literal)
    data = ast.literal_eval(literal)
    centres = [x for x in data if x.get("type") == "Language Centre" and isinstance(x.get("programmes"), dict)]
    if len(centres) != 7:
        raise RuntimeError("Unexpected English-centre count; aborting rather than publishing stale data")
    return centres

def safe_official_url(url: str) -> str:
    url = str(url or "").strip()
    return url if url.startswith("https://") or url.startswith("http://") else ""

def level_note(level: str) -> str:
    return {
      "Foundation": "A foundation pathway may prepare students for a later degree. Ask the university which degrees accept the foundation qualification and whether progression is conditional.",
      "Diploma": "For a diploma, check entry requirements, practical components, how credits transfer to future study and the exact award printed on graduation documents.",
      "Bachelor": "For undergraduate applications, review academic prerequisites, course-specific language requirements and the duration and location of the actual degree programme.",
      "Master": "For postgraduate study, check whether the programme is taught, research-based or mixed mode, and whether a proposal, portfolio or relevant work experience is required.",
      "Doctorate": "For research degrees, discuss supervisor availability, proposal suitability, research requirements, study mode and institutional progression rules before applying.",
      "Other": "This is a finder listing that does not clearly map to one qualification level. Confirm the exact qualification title and admissions pathway with the university."
    }[level]

def subject_note(name: str) -> str:
    t = name.lower()
    tests = [
      (["medicine", "mbbs", "dental", "dentistry", "nursing", "pharmacy", "clinical"], "For a healthcare-related course, ask about clinical placements and any professional registration or recognition that applies in your home country."),
      (["engineering", "mechatronic", "mechanical", "civil", "electrical", "chemical", "aerospace"], "For engineering courses, verify the exact discipline, laboratory or industry-training requirements and relevant programme accreditation."),
      (["computer", "software", "information technology", "cyber", "artificial intelligence", "data science"], "For technology courses, compare programming and practical-project content, specialist modules and the opportunities for applied experience."),
      (["account", "business", "marketing", "finance", "logistics", "management", "economics"], "For business-related courses, review the specialisation, practical work components and recognition by any professional body relevant to your goals."),
      (["education", "tesl", "tesol", "early childhood", "teaching"], "For education courses, ask about teaching practice, local licensing rules and whether the qualification meets the teaching requirements in your intended country."),
      (["architecture", "design", "media", "creative", "animation"], "For design-based study, confirm portfolio requirements, available studios or labs and any profession-specific recognition."),
      (["law", "shariah", "syariah", "islamic"], "For law and related pathways, check whether the award satisfies any academic or professional requirements in the country where you hope to work."),
      (["english", "language", "linguistic"], "For language programmes, confirm placement assessments, required English level, taught hours and any progression agreement with a university.")
    ]
    for terms, note in tests:
        if any(tk in t for tk in terms):
            return note
    return "Before selecting any programme, compare its curriculum, university award, entry requirements and the latest intake information from the official provider."

def seo_program_title(title: str, uni_code: str) -> str:
    """Keep concise titles without losing the complete visible H1 name."""
    suffix = " | " + uni_code + " Malaysia"
    max_name = max(20, 60 - len(suffix))
    if len(title) <= max_name:
        return title + suffix
    shortened = title[:max_name]
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]
    shortened = shortened.rstrip(" -/(,")
    return shortened + suffix

def page_head(title: str, desc: str, path: str, schema: dict | None = None) -> str:
    canonical = PUBLIC_BASE + path
    jsonld = ""
    if schema:
        data = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        jsonld = '<script type="application/ld+json">' + data + '</script>'
    return (
      '<!doctype html><html lang="en"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<title>' + h(title) + '</title>'
      '<meta name="description" content="' + h(desc[:155]) + '">'
      '<meta name="robots" content="index,follow,max-image-preview:large">'
      '<link rel="canonical" href="' + h(canonical) + '">'
      '<meta property="og:type" content="website">'
      '<meta property="og:title" content="' + h(title) + '">'
      '<meta property="og:description" content="' + h(desc[:155]) + '">'
      '<meta property="og:url" content="' + h(canonical) + '">'
      '<meta property="og:site_name" content="NextGenz Centre">'
      '<link rel="stylesheet" href="/guides/style.css">'
      '<link rel="stylesheet" href="/programmes/catalog.css">'
      + jsonld + '</head><body>' + MARKER
    )

def wrap_page(head: str, main: str) -> str:
    return (
      head
      + '<header class="nav"><div class="wrap nav-inner">'
      '<a href="/" class="brand">NEXTGENZ <span>CENTRE</span></a>'
      '<nav class="nav-actions" aria-label="Website navigation">'
      '<a href="/">Home</a><a href="/programmes/">University programmes</a>'
      '<a href="/services/education-consultant-malaysia.html">Education consultant</a>'
      '<a href="/guides/">Study guides</a>'
      '<a class="cta" href="https://wa.me/601167701210">Free guidance</a>'
      '</nav></div></header><main>'
      + main +
      '</main><footer class="foot"><div class="wrap foot-flex">'
      '<div><strong>NEXTGENZ CENTRE</strong><p>Programme comparisons for international students planning to study in Malaysia.</p>'
      '<small>Finder data is indicative. Confirm availability, prices and admission rules directly with the institution.</small></div>'
      '<div><a href="/programmes/">All programmes</a><br>'
      '<a href="/guides/how-to-study-in-malaysia.html">How to study in Malaysia</a><br>'
      '<a href="/about-nextgenz-centre.html">About us</a></div>'
      '</div></footer></body></html>\n'
    )

CSS = """
.catalog-lead{max-width:780px}
.catalog-stats{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}
.catalog-stats span{background:#fff;border:1px solid #c3e5e5;border-radius:999px;padding:7px 15px;color:#17425a;font-weight:800;font-size:.85rem}
.catalog-links{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 28px}
.catalog-links a{background:#fff;border:1px solid #c8e2ed;border-radius:999px;padding:8px 15px;text-decoration:none;font-weight:800}
.catalog-links a:hover{border-color:#0c8b86;background:#e6faf8}
.catalog-list{list-style:none;padding:0;margin:20px 0 34px}
.catalog-list li{display:flex;flex-wrap:wrap;gap:9px;align-items:baseline;justify-content:space-between;border-bottom:1px solid #dce8ef;padding:12px 0;scroll-margin-top:92px}
.catalog-list a{font-weight:700;color:#096e77}
.catalog-list .fee{font-size:.78rem;color:#577086;font-weight:600}
.catalog-wide{background:#fff;border:1px solid #dce8ef;border-radius:22px;padding:30px;margin-bottom:28px}
.catalog-wide h2{margin-top:0}
.catalog-note{border-left:4px solid #06a89e;background:#e8f7f7;padding:17px 20px;border-radius:12px;margin:22px 0;font-size:.92rem}
.catalog-facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:22px 0}
.catalog-fact{border:1px solid #d9e9ef;background:#fff;padding:14px 17px;border-radius:14px}
.catalog-fact strong{display:block;color:#17425a;font-size:.85rem}
.catalog-fact span{font-size:.96rem;color:#445b72}
.catalog-search{max-width:560px;width:100%;border:1px solid #b8d6de;border-radius:12px;padding:13px 16px;font:inherit}
.catalog-count{color:#476579;font-weight:700;font-size:.9rem}
.catalog-verified{background:#f3fbf9;border:1px solid #a7dace;border-radius:22px;padding:22px 25px;margin:30px 0}.catalog-verified h2{margin:12px 0 18px}.catalog-verified-eyebrow{font-size:.73rem;font-weight:900;letter-spacing:.05em;color:#086d66}.catalog-verified-list{margin:0 0 16px}.catalog-verified-list>div{margin:14px 0;padding-bottom:12px;border-bottom:1px solid #cce7df}.catalog-verified-list dt{font-weight:900;color:#0b504d}.catalog-verified-list dd{margin:5px 0 0;color:#264a56;line-height:1.75}.catalog-fact-date{color:#4c6f76;font-size:.82rem}.catalog-verified a{font-weight:800}
.catalog-comparison{overflow-x:auto;border:1px solid #dce8ef;border-radius:16px;margin:25px 0}.catalog-table{border-collapse:collapse;width:100%;min-width:620px;font-size:.94rem}.catalog-table th{text-align:left;background:#e7f8f6;color:#1a3c53;padding:13px 15px;font-weight:800}.catalog-table td{border-bottom:1px solid #e5edf2;padding:13px 15px;vertical-align:top}.catalog-table tr:last-child td{border-bottom:0}.catalog-table a{font-weight:700}.catalog-loc{display:block;color:#667d8d;margin-top:3px;font-size:.77rem}.catalog-money{font-weight:700;color:#3b5872;white-space:nowrap}
@media(max-width:650px){.catalog-facts{grid-template-columns:1fr}.catalog-wide{padding:20px}.catalog-list li{display:block}.catalog-list .fee{display:block;margin-top:4px}}
"""

def write(relative: str, data: str, output: set[str]) -> None:
    path = ROOT / relative.lstrip("/")
    if not str(path.resolve()).startswith(str(OUT.resolve()) + "/"):
        raise RuntimeError("Generator attempted to write outside programme directory: " + relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != data:
        path.write_text(data, encoding="utf-8")
    output.add(relative.lstrip("/"))

def main() -> None:
    unis = normalize_unis()
    english_centres = english_centres_from_finder()
    records = []
    by_uni = defaultdict(list)
    by_level = defaultdict(list)
    uni_slugs = {}
    for uni in unis:
        uname = str(uni["university"])
        uslug = slug(str(uni.get("shortName") or uname), 36)
        if uslug in uni_slugs.values():
            uslug = slug(uname, 48)
        uni_slugs[uname] = uslug
        for title, fee in uni["programmes"].items():
            level = record_level(title)
            item = {
                "name": str(title), "raw_fee": str(fee), "level": level,
                "uni": uname, "uslug": uslug, "short": str(uni.get("shortName") or ""),
                "location": str(uni.get("location") or "Malaysia"),
                "intakes": str(uni.get("intakes") or ""),
                "currency": str(uni.get("currency") or "MYR"),
                "type": str(uni.get("type") or ""),
                "website": safe_official_url(uni.get("website", "")),
                "id": slug(title, 72) + "-" + sha1(title.encode("utf-8")).hexdigest()[:6],
            }
            records.append(item)
            by_uni[uname].append(item)
            by_level[level].append(item)

    if len(unis) != 25 or len(records) < 1100:
        raise RuntimeError("Unexpected programme data scope, refusing to publish")
    unique_names = len(set(x["name"] for x in records))

    # Start with individual pages for clear, high-value searches:
    # one foundation (or diploma) and one bachelor's degree per university,
    # plus a limited set of master's programmes. All other names still appear
    # as crawlable, exact-match text in the university and level directories.
    selected = {}
    priority_terms = [
      "foundation in engineering", "foundation in science", "foundation in arts",
      "foundation in business", "computer science", "software engineering",
      "artificial intelligence", "medicine", "business administration",
      "information technology", "accounting", "electrical engineering",
      "mechanical engineering", "education", "nursing", "data science",
    ]
    def quality(rec: dict) -> int:
        t = rec["name"].lower()
        if any(x in t for x in (" / ", " e.g.", "various", "etc.", "other programmes", "all specialisations", "mixed mode variants")):
            return -10000
        score = 500 - len(t)
        for idx, kw in enumerate(priority_terms):
            if kw in t:
                score += (len(priority_terms) - idx) * 8
        return score
    for uni in unis:
        entries = by_uni[uni["university"]]
        for group in (["Foundation", "Diploma"], ["Bachelor"]):
            possible = sorted((e for e in entries if e["level"] in group and quality(e) > -1000), key=quality, reverse=True)
            if possible:
                e = possible[0]
                selected[(e["uni"], e["name"])] = e
    # Representative postgraduate pages; focus only on concise, unambiguous
    # programme titles to prevent thousands of near-identical landing pages.
    postgraduate_candidates = sorted((e for e in records if e["level"] == "Master" and quality(e) > 380), key=quality, reverse=True)
    seen_uni = set()
    for e in postgraduate_candidates:
        if e["uni"] in seen_uni:
            continue
        selected[(e["uni"], e["name"])] = e
        seen_uni.add(e["uni"])
        if len(seen_uni) >= 12:
            break

    # Publish carefully fact-checked university programmes even when the
    # staged SEO selector would otherwise pick a different course.
    for e in records:
        if (e["short"], e["name"]) in VERIFIED_PROGRAMMES:
            selected[(e["uni"], e["name"])] = e
    found_verified = {(e["short"], e["name"]) for e in selected.values() if (e["short"], e["name"]) in VERIFIED_PROGRAMMES}
    if len(found_verified) != len(VERIFIED_PROGRAMMES):
        raise RuntimeError("A verified programme entry disappeared from the finder: " + str(set(VERIFIED_PROGRAMMES)-found_verified))
    for e in selected.values():
        e["detail"] = "/programmes/courses/" + e["uslug"] + "/" + e["id"] + ".html"
    selected_urls = {k: v["detail"] for k, v in selected.items()}

    outputs = set()
    write("programmes/catalog.css", CSS, outputs)
    topic_pages = generate_topic_pages(records, selected_urls, uni_slugs, write, wrap_page, page_head, h, outputs)
    # English language centres also appear in the website's public directory,
    # separately from the original 25-university portal programme finder.
    english_path = "/programmes/english-language-centres.html"
    english_main = (
        '<section class="hero"><div class="wrap"><span class="eyebrow">MALAYSIA ENGLISH LANGUAGE STUDY</span>'
        '<h1>English language courses in Malaysia: <span class="accent">compare language centres</span></h1>'
        '<p class="lead">Explore English study and IELTS preparation listings from seven language centres shown in the NextGenz Centre public institution directory. Compare listed course names, formats and potential pathways before verifying options with each provider.</p></div></section>'
        '<section class="section"><div class="wrap"><div class="catalog-note">The course names and prices below are references from our existing public institution directory. Prices may use different units, and current availability or tuition has not been independently verified. Ask each centre for a current course schedule, quote, placement test details and any applicable visa arrangements before booking.</div>'
        '<h2>Compare English language centres and their programmes</h2>'
    )
    english_count = 0
    for centre in english_centres:
        english_main += '<section class="catalog-wide"><h2>' + h(centre["university"]) + '</h2><p>' + h(centre.get("location", "Malaysia")) + ' · Programmes listed in NextGenz Centre public directory</p><ul class="catalog-list">'
        for name, fee in centre["programmes"].items():
            english_main += '<li><strong>' + h(name) + '</strong><span class="fee">Finder reference: ' + h(centre.get("currency") or "MYR") + ' ' + h(fee) + '</span></li>'
            english_count += 1
        english_main += '</ul>'
        official = safe_official_url(centre.get("website") or "")
        if official:
            english_main += '<p><a target="_blank" rel="noopener noreferrer" href="' + h(official) + '">Visit the centre’s official website ↗</a></p>'
        english_main += '</section>'
    english_main += (
        '<h2>Which English programme is right for an international student?</h2>'
        '<p><strong>General English</strong> typically focuses on language development, while <strong>intensive English</strong> may involve more scheduled class time. <strong>IELTS preparation</strong> focuses on assessment preparation; it is not automatically an accepted university admission pathway. Ask about level placement, class duration, expected outcomes, class hours, availability and whether the specific centre supports an eligible student pass route.</p>'
        '<p>Students planning to progress to a university should check the chosen university’s language requirements rather than assuming any centre course guarantees entry. Read our <a href="/guides/english-courses-in-malaysia.html">English courses guide</a> and <a href="/guides/malaysia-student-visa-emgs-guide.html">EMGS student visa overview</a>.</p>'
        '<p><a class="button" href="https://wa.me/601167701210?text=Hello%20NextGenz%20Centre%2C%20I%20need%20English%20language%20course%20guidance%20in%20Malaysia.">Ask for English course guidance</a><a class="button secondary" href="/programmes/">Explore university programmes</a></p>'
        '</div></section>'
    )
    write(english_path.lstrip("/"), wrap_page(page_head(
        "English Language Courses in Malaysia | Centre Comparison",
        "Compare English language courses, General English and IELTS preparation at seven language centres in Malaysia. Check course names, locations and admission guidance.",
        english_path, {"@context":"https://schema.org","@type":"CollectionPage","name":"English Language Courses at Malaysia Language Centres","url":PUBLIC_BASE+english_path}
    ),english_main),outputs)
    counts = defaultdict(int)
    for rec in records:
        counts[rec["level"]] += 1

    about = (
      '<section class="hero"><div class="wrap"><span class="eyebrow">UNIVERSITIES · FOUNDATION · BACHELOR · MASTER</span>'
      '<h1>Study in Malaysia: <span class="accent">explore university programmes</span></h1>'
      '<p class="lead catalog-lead">Browse actual programme names from the NextGenz Centre programme finder. Explore foundation, diploma, bachelor’s, master’s and doctoral options across 25 Malaysian universities, then ask our education consultancy team for free placement guidance.</p>'
      '<div class="catalog-stats"><span>' + str(len(unis)) + ' universities</span><span>' + str(len(records)) + ' listed university programmes</span><span>' + str(unique_names) + ' distinct programme names</span></div></div></section>'
      '<section class="section"><div class="wrap">'
      '<div class="catalog-note"><strong>Important:</strong> These are reference records in our programme finder, not a live official university admissions database. Some programme names group multiple awards. Fees, campus availability, study mode, intakes and entry requirements must be verified directly with the institution. Inclusion does not imply a confirmed university recruitment partnership.</div>'
      '<h2>Search by study level</h2><div class="grid">'
    )
    for level in LEVELS:
        href = "/programmes/levels/" + LEVEL_SLUG[level] + ".html"
        about += ('<a class="tile" data-tone="teal" href="' + href + '"><span class="tag">Malaysia degree pathways</span>'
                  '<h2>' + LABELS[level] + '</h2><p>' + str(counts[level]) + ' programme listings from the finder, organized by university.</p>'
                  '<span class="arrow">Explore programmes →</span></a>')
    about += '</div><h2>Compare popular programme subjects</h2><p>Use these focused course comparisons to weigh real programme names across different Malaysian universities. They are reference listings, not guarantees of current admission or tuition.</p><div class="grid">' 
    for topic in TOPICS:
        if topic["slug"] not in topic_pages:
            continue
        info = topic_pages[topic["slug"]]
        about += ('<a class="tile" data-tone="purple" href="' + info["url"] + '"><span class="tag">Compare Malaysia courses</span><h2>' + h(topic["label"]) + '</h2><p>' + str(info["entries"]) + ' listed options across ' + str(info["universities"]) + ' universities, with decision checks and admissions questions.</p><span class="arrow">Compare programmes →</span></a>')
    about += '</div><p><a class="button secondary" href="/programmes/english-language-centres.html">Explore English language courses and centres →</a></p><h2>Browse programmes by university</h2><div class="grid">'
    for uni in unis:
        name = uni["university"]
        href = "/programmes/universities/" + uni_slugs[name] + ".html"
        about += ('<a class="tile" data-tone="blue" href="' + href + '"><span class="tag">'
                  + h(uni.get("location") or "Malaysia") + '</span><h2>' + h(name)
                  + '</h2><p>' + str(len(by_uni[name])) + ' programme titles available to explore.</p><span class="arrow">View course list →</span></a>')
    about += (
      '</div><h2>Need help choosing a university in Malaysia?</h2>'
      '<p>NextGenz Centre can explain how to compare admission requirements, quoted tuition and official EMGS student pass steps. Our core university-placement advice is free, although university and government charges are separate.</p>'
      '<p><a class="button" href="/services/education-consultant-malaysia.html">Education consultant in Malaysia</a>'
      '<a class="button secondary" href="/guides/how-to-study-in-malaysia.html">International student guide</a></p>'
      '</div></section>'
    )
    write("programmes/index.html", wrap_page(page_head(
        "Malaysia University Programmes | NextGenz Centre Finder",
        "Explore 1,182 university programme listings across 25 Malaysian universities. Search foundation, diploma, bachelor's, master's and PhD courses by university.",
        "/programmes/", {"@context":"https://schema.org","@type":"CollectionPage","name":"Malaysia University Programmes","url":PUBLIC_BASE+"/programmes/","isPartOf":{"@type":"WebSite","name":"NextGenz Centre","url":PUBLIC_BASE}}
    ),about),outputs)

    # 25 university pages: every single programme is readable in initial HTML.
    for uni in unis:
        name = str(uni["university"])
        uslug = uni_slugs[name]
        dest = "/programmes/universities/" + uslug + ".html"
        official = safe_official_url(uni.get("website",""))
        counts_uni = {lev: sum(e["level"] == lev for e in by_uni[name]) for lev in LEVELS}
        main = (
          '<section class="hero"><div class="wrap"><span class="eyebrow">MALAYSIA UNIVERSITY PROGRAMME DIRECTORY</span>'
          '<h1>Study programmes at <span class="accent">' + h(name) + '</span></h1>'
          '<p class="lead">' + str(len(by_uni[name])) + ' programme titles from the NextGenz Centre finder, including university foundation, degree and postgraduate options where listed. Compare course names before checking admissions with the institution.</p>'
          '<div class="catalog-stats"><span>' + h(uni.get("type","University")) + ' university</span><span>' + h(uni.get("location","Malaysia")) + '</span><span>' + str(len(by_uni[name])) + ' programme listings</span></div></div></section>'
          '<section class="section"><div class="wrap"><div class="catalog-note">Programme titles and amounts below are references from our existing finder. They are <strong>not confirmed current university offers</strong>. Any listed fee may be per semester, year or total, depending on the programme; verify the basis, currency, eligibility and intake with the official university.</div>'
        )
        main += '<h2>Find a course at ' + h(name) + '</h2><input type="search" class="catalog-search" id="courseFilter" placeholder="Filter programme titles on this page..." aria-label="Filter programmes">'
        main += '<div class="catalog-links">'
        for lev in LEVELS:
            if counts_uni[lev]:
                main += '<a href="#' + LEVEL_SLUG[lev] + '">' + h(LABELS[lev]) + ' (' + str(counts_uni[lev]) + ')</a>'
        main += '</div>'
        for lev in LEVELS:
            entries = [e for e in by_uni[name] if e["level"] == lev]
            if not entries:
                continue
            main += '<section class="catalog-wide" id="' + LEVEL_SLUG[lev] + '"><h2>' + h(LABELS[lev]) + ' at ' + h(name) + '</h2>'
            main += '<p>Review these ' + str(len(entries)) + ' listed titles. <a href="/programmes/levels/' + LEVEL_SLUG[lev] + '.html">Compare ' + h(lev.lower()) + ' choices across Malaysian universities</a>.</p>'
            main += '<ul class="catalog-list">'
            for e in entries:
                title = h(e["name"])
                path = selected_urls.get((name, e["name"]))
                if path:
                    title = '<a href="' + h(path) + '">' + title + '</a>'
                else:
                    title = '<strong>' + title + '</strong>'
                fee = h(e["raw_fee"])
                main += ('<li id="' + e["id"] + '" class="finder-program" data-title="' + h(e["name"].lower()) + '"><span>' + title
                         + '</span><span class="fee">Finder reference: ' + h(e["currency"]) + ' ' + fee + '</span></li>')
            main += '</ul></section>'
        if official:
            main += '<p><a class="button secondary" target="_blank" rel="noopener noreferrer" href="' + h(official) + '">Check the university’s official website ↗</a></p>'
        main += (
          '<h2>How to apply for a programme at ' + h(name) + '</h2>'
          '<p>First confirm the exact degree title, campus, start date, entry qualifications, accepted English evidence, university registration rules and the latest written international fee schedule. A title in this directory is not proof that an intake remains open. Ask the institution about visa processing and the appropriate EMGS stage before travelling.</p>'
          '<p><a class="button" href="https://wa.me/601167701210?text=' + quote("Hello NextGenz Centre, please help me compare programmes at " + name + ".") + '">Discuss this university with NextGenz</a></p>'
          '<p><a href="/programmes/">All Malaysia university programmes</a> · <a href="/services/education-consultant-malaysia.html">Education consultant in Malaysia</a></p>'
          '</div></section>'
          '<script>document.getElementById("courseFilter").addEventListener("input",function(){var q=this.value.toLowerCase().trim();document.querySelectorAll(".finder-program").forEach(function(item){item.hidden=!!q&&!item.dataset.title.includes(q)});});</script>'
        )
        write(dest.lstrip("/"),wrap_page(page_head(
            name + " Programmes in Malaysia | NextGenz Centre",
            "Explore " + str(len(by_uni[name])) + " programme names at " + name + ". Compare foundation, degree, postgraduate and admissions options for international students.",
            dest, {"@context":"https://schema.org","@type":"CollectionPage","name":name+" study programmes in Malaysia","url":PUBLIC_BASE+dest}
        ),main),outputs)

    # Six level pages link every listed title to its university anchor, unless
    # a dedicated, higher-value programme page exists for that exact entry.
    for lev in LEVELS:
        dest = "/programmes/levels/" + LEVEL_SLUG[lev] + ".html"
        main = (
          '<section class="hero"><div class="wrap"><span class="eyebrow">MALAYSIA COURSE FINDER</span>'
          '<h1>' + h(LABELS[lev]) + ' <span class="accent">in Malaysia</span></h1>'
          '<p class="lead">Compare ' + str(len(by_level[lev])) + ' ' + h(lev.lower()) + ' programme entries across Malaysian institutions. See exact course names, university locations and finder fee references, then confirm admission and current fees directly with the university.</p></div></section>'
          '<section class="section"><div class="wrap"><div class="catalog-note">' + h(level_note(lev)) + ' All names and fee amounts come from the NextGenz Centre finder. They require verification with the institution before applying or paying.</div>'
          '<p><a class="button" href="/services/education-consultant-malaysia.html">Talk to an education consultant</a><a class="button secondary" href="/programmes/">Browse all study levels</a></p>'
        )
        related_topics = [t for t in TOPICS if t["level"] == lev and t["slug"] in topic_pages]
        if related_topics:
            main += '<h2>Compare related ' + h(lev.lower()) + ' programme types</h2><div class="catalog-links">'
            for topic in related_topics:
                main += '<a href="' + topic_pages[topic["slug"]]["url"] + '">' + h(topic["label"]) + '</a>'
            main += '</div>'
        for uni in unis:
            name = str(uni["university"])
            entries = [e for e in by_uni[name] if e["level"] == lev]
            if not entries:
                continue
            uhref = "/programmes/universities/" + uni_slugs[name] + ".html"
            main += '<section class="catalog-wide"><h2><a href="' + h(uhref) + '">' + h(name) + '</a></h2><p>' + h(uni.get("location", "Malaysia")) + ' · ' + str(len(entries)) + ' programmes in this study category.</p><ul class="catalog-list">'
            for e in entries:
                href = selected_urls.get((name, e["name"]), uhref + "#" + e["id"])
                main += ('<li><a href="' + h(href) + '">' + h(e["name"]) + '</a><span class="fee">' + h(e["currency"]) + ' ' + h(e["raw_fee"]) + ' (finder reference)</span></li>')
            main += '</ul></section>'
        main += '<p>For applying to university in Malaysia, review our <a href="/guides/how-to-study-in-malaysia.html">international student admission guide</a> or <a href="/guides/malaysia-student-visa-emgs-guide.html">EMGS visa overview</a>.</p></div></section>'
        write(dest.lstrip("/"), wrap_page(page_head(
            LABELS[lev] + " in Malaysia | NextGenz Centre",
            "Search " + LABELS[lev].lower() + " at Malaysian universities. Explore official institutions, named programmes and admissions guidance for international students.",
            dest, {"@context":"https://schema.org","@type":"CollectionPage","name":LABELS[lev]+" in Malaysia","url":PUBLIC_BASE+dest}
        ),main),outputs)

    # Detailed pages for the initial focused set.
    for e in selected.values():
        dest = e["detail"]
        official_link = ('<a href="' + h(e["website"]) + '" target="_blank" rel="noopener noreferrer">Official university website ↗</a>' if e["website"] else 'Ask the institution for its official admissions website')
        main = (
          '<section class="hero"><div class="wrap"><span class="eyebrow">' + h(e["level"].upper()) + ' STUDIES IN MALAYSIA</span>'
          '<h1>' + h(e["name"]) + ' <span class="accent">at ' + h(e["uni"]) + '</span></h1>'
          '<p class="lead">Review the ' + h(e["name"]) + ' listing at ' + h(e["uni"]) + ' in ' + h(e["location"]) + ', Malaysia. Explore the finder’s available reference information and the admission questions to check before applying.</p>'
          '<a class="button" href="https://wa.me/601167701210?text=' + quote("Hello NextGenz Centre. I would like information about " + e["name"] + " at " + e["uni"] + ".") + '">Ask about this programme</a></div></section>'
          '<section class="section"><div class="wrap"><div class="article-layout"><article class="article"><h2>Programme details to compare</h2>'
          '<div class="catalog-facts">'
          '<div class="catalog-fact"><strong>Programme title in finder</strong><span>' + h(e["name"]) + '</span></div>'
          '<div class="catalog-fact"><strong>Institution</strong><span>' + h(e["uni"]) + '</span></div>'
          '<div class="catalog-fact"><strong>Study level grouping</strong><span>' + h(e["level"]) + ' (categorised from title)</span></div>'
          '<div class="catalog-fact"><strong>University location</strong><span>' + h(e["location"]) + '</span></div>'
          '<div class="catalog-fact"><strong>Finder fee reference</strong><span>' + h(e["currency"]) + ' ' + h(e["raw_fee"]) + '</span></div>'
          '<div class="catalog-fact"><strong>Intake reference</strong><span>' + h(e["intakes"] or "Not listed") + '</span></div></div>'
          '<div class="catalog-note"><strong>Fee and intake disclaimer:</strong> These values are taken from the NextGenz programme finder and have not been checked against the university’s current offer. The fee basis may be a semester, year, whole programme or other unit; the reference amount is not a final quotation. Check availability, fees and entry rules with the university before making decisions.</div>'
          '<h2>Is this programme right for you?</h2><p>' + h(level_note(e["level"])) + '</p><p>' + h(subject_note(e["name"])) + '</p>'
          '<h2>Questions to ask before you apply</h2><ol>'
          '<li>Is <strong>' + h(e["name"]) + '</strong> still accepting international applicants for the next intake at ' + h(e["uni"]) + '?</li>'
          '<li>What grades, prior qualifications and English-language evidence are required for this exact programme?</li>'
          '<li>Which campus delivers the programme, what is the teaching mode, and what is the official award title?</li>'
          '<li>Is the current quoted tuition per semester, academic year, or entire qualification? What additional deposits and official fees apply?</li>'
          '<li>Which steps must be completed before a student visa application or entry to Malaysia?</li></ol>'
          '<h2>How to apply in Malaysia</h2><p>Compare eligibility and budget first, then collect the documents stated in the university’s current instructions. Review any written offer and payment schedule before committing. Visa and student pass procedures depend on your nationality and study level; use the official <a href="https://visa.educationmalaysia.gov.my/" target="_blank" rel="noopener noreferrer">EMGS website</a> for current information.</p>'
          '<h2>University information and NextGenz assistance</h2><p>' + official_link + '. The NextGenz Centre team can help you understand programme comparisons and the application workflow. Our core university-placement advisory is free to students, but university and government charges remain separate. No programme availability, scholarship, admission or visa outcome is guaranteed.</p>'
          '<p><a href="/programmes/universities/' + e["uslug"] + '.html">View all programmes at ' + h(e["uni"]) + '</a> · '
          '<a href="/programmes/levels/' + LEVEL_SLUG[e["level"]] + '.html">Compare ' + h(e["level"].lower()) + ' programmes in Malaysia</a></p>'
          '</article><aside class="aside"><h2>Ask about this course</h2><p>Tell us your qualifications, study budget and intended intake so we can discuss what to confirm with the university.</p>'
          '<a class="button" href="https://wa.me/601167701210?text=' + quote("Please guide me on " + e["name"] + " at " + e["uni"]) + '">Free programme advice ↗</a><p><small>Our advisory fee is free. Official charges may apply.</small></p></aside></div></div></section>'
        )
        # Independent source-check section. Finder's original amounts remain
        # unchanged, while up-to-date university facts appear with attribution.
        checked = VERIFIED_PROGRAMMES.get((e["short"], e["name"]))
        if checked:
            verified = '<section class="catalog-verified" aria-labelledby="verified-facts-heading"><div class="catalog-verified-eyebrow">OFFICIAL UNIVERSITY SOURCE · VERIFIED 15 NOVEMBER 2026</div>'
            verified += '<h2 id="verified-facts-heading">Current information from ' + h(e["uni"]) + '</h2>'
            if checked["official_name"] != e["name"]:
                verified += '<p><strong>Official programme name:</strong> ' + h(checked["official_name"]) + '. The NextGenz finder title uses a slightly different label, so confirm the exact award on your application.</p>'
            verified += '<dl class="catalog-verified-list">'
            for label, fact in checked["facts"]:
                verified += '<div><dt>' + h(label) + '</dt><dd>' + h(fact) + '</dd></div>'
            verified += '</dl><p>' + h(checked["advice"]) + '</p>'
            verified += '<p><a href="' + h(checked["source_url"]) + '" target="_blank" rel="noopener noreferrer">View original university programme source ↗</a></p>'
            if checked.get("second_source_url"):
                verified += '<p><a href="' + h(checked["second_source_url"]) + '" target="_blank" rel="noopener noreferrer">' + h(checked["second_source_label"]) + ' ↗</a></p>'
            verified += '<p class="catalog-fact-date">Source reviewed 15 November 2026. University pages can change; verify the latest admissions and fee conditions before paying.</p></section>'
            marker = '<h2>Is this programme right for you?</h2>'
            if main.count(marker) != 1:
                raise RuntimeError("Could not add official facts to programme "+ e["name"])
            main = main.replace(marker, verified + marker, 1)
        if '</article><aside' not in main:
            raise RuntimeError("Could not insert relevant course comparison links")
        cross_links = [t for t in matching_topics(e) if t["slug"] in topic_pages]
        related = '<h2>Explore similar university options</h2>'
        for t in cross_links:
            related += '<p><a href="' + topic_pages[t["slug"]]["url"] + '">Compare ' + h(t["label"]) + ' courses across Malaysian universities</a></p>'
        sibling = [a for a in by_uni[e["uni"]] if a["level"] == e["level"] and a["name"] != e["name"]][:4]
        if sibling:
            related += '<p>Other ' + h(e["level"].lower()) + ' titles at ' + h(e["uni"]) + ' worth checking as alternatives:</p><ul>'
            for other in sibling:
                alt_url = selected_urls.get((other["uni"], other["name"]), '/programmes/universities/' + other["uslug"] + '.html#' + other["id"])
                related += '<li><a href="' + h(alt_url) + '">' + h(other["name"]) + '</a></li>'
            related += '</ul>'
        main = main.replace('</article><aside', related + '</article><aside', 1)
        write(dest.lstrip("/"),wrap_page(page_head(
            seo_program_title(e["name"], e["short"]),
            "Explore " + e["name"] + " at " + e["uni"] + " in Malaysia. Compare finder fee reference, university admissions and student application steps.",
            dest,
            {"@context":"https://schema.org","@type":"WebPage","name":e["name"]+" at "+e["uni"],"url":PUBLIC_BASE+dest,"about":{"@type":"EducationalOrganization","name":e["uni"]}}
        ),main),outputs)

    # Manifest is only used to safely remove older generated files if a title
    # disappears from the original programme finder in a future update.
    manifest = OUT / "catalog-manifest.json"
    previous = []
    if manifest.exists():
        try:
            previous = json.loads(manifest.read_text(encoding="utf-8")).get("generated_files", [])
        except (ValueError, OSError):
            previous = []
    for relative in previous:
        old = ROOT / str(relative)
        if relative not in outputs and str(old.resolve()).startswith(str(OUT.resolve()) + "/") and old.is_file():
            if old.suffix == ".html" and MARKER in old.read_text(encoding="utf-8", errors="replace"):
                old.unlink()
    manifest.write_text(json.dumps({
      "source": "index.html / ProgramFinderApp.rawData",
      "universities": len(unis),
      "programme_listings": len(records),
      "distinct_programme_names": unique_names,
      "detailed_programme_pages": len(selected),
      "topic_comparison_pages": len(topic_pages),
      "university_verified_programme_pages": len(found_verified),
      "english_language_centres": len(english_centres),
      "english_course_reference_entries": english_count,
      "generated_files": sorted(outputs)
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    outputs.add("programmes/catalog-manifest.json")

    # Include only HTML indexable pages, not CSS/JSON, in the existing sitemap.
    sitemap_path = ROOT / "sitemap.xml"
    sm = sitemap_path.read_text(encoding="utf-8")
    sm = re.sub(re.escape(SITEMAP_START) + r"[\s\S]*?" + re.escape(SITEMAP_END) + r"\s*", "", sm)
    sm = re.sub(r"\s+</urlset>", "\n</urlset>", sm)
    links = sorted(x for x in outputs if x.endswith(".html"))
    auto_xml = SITEMAP_START + "\n" + "\n".join(
      "  <url><loc>" + PUBLIC_BASE + ("/programmes/" if url == "programmes/index.html" else "/" + url)
      + "</loc><lastmod>" + TODAY + "</lastmod></url>" for url in links
    ) + "\n" + SITEMAP_END + "\n"
    if "</urlset>" not in sm:
        raise RuntimeError("Existing sitemap malformed")
    sm = sm.replace("</urlset>", auto_xml + "</urlset>")
    sitemap_path.write_text(sm, encoding="utf-8")

    print(json.dumps({
        "universities":len(unis),"source_listings":len(records),
        "distinct_names":unique_names,"detailed_pages":len(selected),"topic_pages":len(topic_pages),"official_source_verified":len(found_verified),
        "university_pages":len(unis),"study_level_pages":len(LEVELS),
        "published_html":len(links),"sitemap_total":sm.count("<url>")
    },ensure_ascii=False))

if __name__ == "__main__":
    main()
