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

def header_html(lang: str = "en", catalogue_path: str = "") -> str:
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
        # The new interactive finder is English-only: language alternatives
        # return to the real translated course directories, not 404 paths.
        options = (("English", "/programmes/find/"),
                   ("العربية", "/programmes/ar/"),
                   ("中文", "/programmes/zh/"))
    else:
        options = LANG_OPTIONS if not catalogue_path else tuple((name, catalogue_path if code=="en" else catalogue_path.replace("/programmes/", "/programmes/"+code+"/", 1)) for (name,_),code in zip(LANG_OPTIONS, ("en","ar","zh")))
    languages = ''.join('<a href="' + escape(href, quote=True) +
                        '" lang="' + ("ar" if text == "العربية" else "zh-CN" if text == "中文" else "en") +
                        '">' + text + '</a>' for text, href in options)
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
