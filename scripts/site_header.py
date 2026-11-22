"""Canonical public NextGenz Centre header shared by static SEO pages.

The crest URL and wordmark are taken from the original homepage
HeaderNavbar component; do not substitute an invented text-only logo.
All homepage section links resolve from subpages via "/#..." URLs.
"""
from html import escape

# Original artwork recovered from NextGenz Centre's own Google Drive Logo.png.
# A transparent high-resolution crop of the genuine crest is hosted locally.
# Use a versioned URL to prevent any stale low-resolution screenshot caches.
BRAND_CREST = "/assets/brand/nextgenz-official-crest-fallback.png?v=drive-original-20261115"
ORIGINAL_CREST_CDN = "https://cdn.phototourl.com/free/2026-07-29-bc15283f-aa7c-4900-ba80-03dc631dd663.png"
NAV_LINKS = (
    ("Universities", "/#universities"),
    ("Why Malaysia", "/why-malaysia.html"),
    ("About Us", "/about-nextgenz-centre.html"),
    ("Services", "/#services"),
    ("Portals", "/#portals"),
    ("How it works", "/#process"),
    ("Agents", "/#agents"),
    ("FAQ", "/#faq"),
    ("Journal", "/#articles"),
)
SEARCH_ICON = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" '
               'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true">'
               '<circle cx="10.8" cy="10.8" r="7.2"></circle>'
               '<path d="m16.2 16.2 5 5"></path></svg>')
LANG_OPTIONS = (("English","/guides/how-to-study-in-malaysia.html"),
                ("العربية","/ar/study-in-malaysia.html"),
                ("中文","/zh/study-in-malaysia.html"))

def header_html(lang: str = "en", catalogue_path: str = "", page_path: str = "") -> str:
    active = {"en": "English", "ar": "العربية", "zh": "中文"}.get(lang, "English")
    links = ''.join(
        '<a href="' + escape(url, quote=True) + '">' + escape(text) + '</a>'
        for text, url in NAV_LINKS
    )
    # Use the identical logo image URL, wordmark case, gold CENTRE treatment
    # and homepage navigation labels; do not invent a new crest or brand mark.
    brand = ('<a href="/" class="ng-brand-lockup" aria-label="NextGenz Centre home">'
             '<img src="' + escape(BRAND_CREST, quote=True) +
             '" width="46" height="46" loading="eager" decoding="async" '
             'alt="NextGenz Centre official crest" data-logo-locked="true">'
             '<span class="ng-brand-wordmark">NEXTGENZ <span>CENTRE</span></span>'
             '</a>')
    if catalogue_path == "/programmes/find/":
        # No translated copy of the full interactive finder exists yet.
        # Identify links to broader course directories honestly.
        options = (
            ("English · course finder", "/programmes/find/", "en", "This course finder page in English"),
            ("العربية · دليل البرامج", "/programmes/ar/", "ar", "Arabic programme directory, not a translation of the interactive finder"),
            ("中文 · 课程目录", "/programmes/zh/", "zh-CN", "Chinese programme directory, not a translation of the interactive finder"),
        )
    elif catalogue_path:
        options = tuple(
            (name, catalogue_path if code == "en" else
             catalogue_path.replace("/programmes/", "/programmes/" + code + "/", 1),
             "zh-CN" if code == "zh" else code,
             "Same programme or catalogue page in " + name)
            for (name, _), code in zip(LANG_OPTIONS, ("en", "ar", "zh"))
        )
    elif page_path in ("/guides/how-to-study-in-malaysia.html",
                       "/ar/study-in-malaysia.html", "/zh/study-in-malaysia.html"):
        options = (
            ("English", "/guides/how-to-study-in-malaysia.html", "en", "English study guide"),
            ("العربية", "/ar/study-in-malaysia.html", "ar", "Arabic study guide"),
            ("中文", "/zh/study-in-malaysia.html", "zh-CN", "Chinese study guide"),
        )
    else:
        # Many editorial pages do not have same-page Arabic/Chinese versions.
        # Explicitly distinguish the related translated guide from a translation.
        current = page_path if page_path.startswith("/") else "/guides/how-to-study-in-malaysia.html"
        options = (
            ("English · this page", current, "en", "Current page in English"),
            ("العربية · دليل الدراسة", "/ar/study-in-malaysia.html", "ar",
             "Related Arabic study guide, not a translation of this page"),
            ("中文 · 留学指南", "/zh/study-in-malaysia.html", "zh-CN",
             "Related Chinese study guide, not a translation of this page"),
        )
    languages = ''.join(
        '<a href="' + escape(href, quote=True) +
        '" lang="' + code + '" title="' + escape(description, quote=True) +
        '">' + escape(label) + '</a>'
        for label, href, code, description in options
    )
    language = ('<details class="ng-brand-language"><summary aria-label="Choose language">'
                + active + '<span class="ng-drop-chevron" aria-hidden="true">⌄</span></summary>'
                '<div class="ng-brand-language-list">' + languages + '</div></details>')
    advisory = ('<a class="ng-brand-advisory" href="https://wa.me/601167701210" '
                'target="_blank" rel="noopener noreferrer">Free Advisory <span aria-hidden="true">↗</span></a>')
    explore = ('<a class="ng-brand-explore" href="/programmes/find/" aria-label="Find a university programme">'
               + SEARCH_ICON + 'Explore Programs</a>')
    mobile_links = (links +
                    '<a href="/programmes/find/">Explore Programs</a>'
                    '<a href="/programmes/subjects/">Find a Degree</a>'
                    '<a href="/guides/">Study guides</a>' +
                    '<div class="ng-mobile-lang">' + languages + '</div>' + advisory)
    header = ('<header class="nav ng-brand-header" dir="ltr">'
            '<div class="ng-brand-shell">' + brand +
            '<nav class="ng-brand-primary" aria-label="Main website navigation">' + links + '</nav>'
            '<div class="ng-brand-tools">' + explore + language + advisory + '</div>'
            '<details class="ng-brand-mobile"><summary aria-label="Open website menu">'
            '<span class="ng-mobile-label">Menu</span>'
            '<span class="ng-menu-icon" aria-hidden="true"><i></i><i></i><i></i></span></summary>'
            '<nav class="ng-brand-mobile-list" aria-label="Mobile website navigation">' +
            mobile_links + '</nav></details>'
            '</div></header>')

    if catalogue_path and lang in ('ar','zh'):
        labels = {
            'About Us':('من نحن','关于我们'), 'Universities':('الجامعات','大学'), 'Why Malaysia':('لماذا ماليزيا','为何选择马来西亚'),
            'Services':('الخدمات','服务'), 'Portals':('البوابات','门户'), 'How it works':('خطوات التقديم','申请流程'),
            'Agents':('الوكلاء','合作伙伴'), 'FAQ':('الأسئلة الشائعة','常见问题'), 'Journal':('المقالات','资讯'),
            'Explore Programs':('تصفح البرامج','浏览课程'), 'Find a Degree':('ابحث عن تخصص','查找专业'),
            'Study guides':('أدلة الدراسة','留学指南'), 'Menu':('القائمة','菜单'), 'Free Advisory':('استشارة مجانية','免费咨询')
        }
        for en, translations in labels.items():
            import re
            header = re.sub('(?<=>)'+en+'(?=[ <])',lambda m:translations[lang=='zh'],header)
        header = header.replace('href="/programmes/"','href="/programmes/'+lang+'/"').replace('href="/programmes/subjects/"','href="/programmes/'+lang+'/subjects/"').replace('href="/guides/"','href="/'+lang+'/study-in-malaysia.html"')
        # Restore the English switch when the current page is the catalogue root.
        header = header.replace('href="/programmes/'+lang+'/" lang="en"','href="/programmes/" lang="en"').replace('href="/programmes/'+lang+'/subjects/" lang="en"','href="/programmes/subjects/" lang="en"')
    return header
