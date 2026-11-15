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
    ("Why Malaysia", "/#why-malaysia"),
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

def header_html(lang: str = "en") -> str:
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
    languages = ''.join('<a href="' + escape(href, quote=True) +
                        '" lang="' + ("ar" if text == "العربية" else "zh-CN" if text == "中文" else "en") +
                        '">' + text + '</a>' for text, href in LANG_OPTIONS)
    language = ('<details class="ng-brand-language"><summary aria-label="Choose language">'
                + active + '<span class="ng-drop-chevron" aria-hidden="true">⌄</span></summary>'
                '<div class="ng-brand-language-list">' + languages + '</div></details>')
    advisory = ('<a class="ng-brand-advisory" href="https://wa.me/601167701210" '
                'target="_blank" rel="noopener noreferrer">Free Advisory <span aria-hidden="true">↗</span></a>')
    explore = ('<a class="ng-brand-explore" href="/programmes/" aria-label="Explore university programmes">'
               + SEARCH_ICON + 'Explore Programs</a>')
    mobile_links = (links +
                    '<a href="/programmes/">Explore Programs</a>'
                    '<a href="/programmes/subjects/">Find a Degree</a>'
                    '<a href="/guides/">Study guides</a>' +
                    '<div class="ng-mobile-lang">' + languages + '</div>' + advisory)
    return ('<header class="nav ng-brand-header" dir="ltr">'
            '<div class="ng-brand-shell">' + brand +
            '<nav class="ng-brand-primary" aria-label="Main website navigation">' + links + '</nav>'
            '<div class="ng-brand-tools">' + explore + language + advisory + '</div>'
            '<details class="ng-brand-mobile"><summary aria-label="Open website menu">'
            '<span class="ng-mobile-label">Menu</span>'
            '<span class="ng-menu-icon" aria-hidden="true"><i></i><i></i><i></i></span></summary>'
            '<nav class="ng-brand-mobile-list" aria-label="Mobile website navigation">' +
            mobile_links + '</nav></details>'
            '</div></header>')
