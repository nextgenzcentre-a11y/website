"""Check every published listing and admissions destination after a catalogue build."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
import re
import json
import xml.etree.ElementTree as ET
from build_programme_seo import ROOT, PUBLIC_BASE, normalize_unis, record_level, LEVEL_SLUG, slug
from programme_actions import PHONE

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.actions = []
        self.links = []
        self.canonical = None
        self.h1 = 0
        self.path = path
        self.feed(path.read_text())

    def handle_data(self, text):
        if "programmes" in self.path.parts:
            assert not re.search(r"unverified (?:finder )?reference", text, re.I), self.path
            for match in re.finditer(r"\b(?:MYR|USD|RM)\s*([0-9][0-9,.]*)", text):
                assert re.match(r"\s*[–-]\s*[0-9]", text[match.end():]), (self.path, text)


    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a['href']
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
            if a.get('data-ng-action'):
                self.actions.append((a['data-ng-action'], a['href']))

def main():
    urls = {e.text for e in ET.parse(ROOT/'sitemap.xml').findall('./{*}url/{*}loc')}
    docs = [p for folder in ('programmes','guides','services','ar','zh','fr','ms') for p in (ROOT/folder).rglob('*.html')]
    pages = {p:Page(p) for p in docs}
    fees = 0
    for path, page in pages.items():
        url = PUBLIC_BASE + '/' + path.relative_to(ROOT).as_posix().removesuffix('index.html')
        assert url in urls and page.canonical == url and page.h1 == 1, path
        counts = Counter(k for k,_ in page.actions)
        assert counts['consult'] >= 2 and counts['apply'] >= 2, path
        fees += counts['fee']
        for k, link in page.actions:
            dest = urlsplit(link)
            if k == 'apply':
                assert not dest.netloc and not dest.scheme and dest.path == '/' and dest.fragment == '/registerasstudent', path
                assert parse_qs(dest.query)['programme'][0].strip(), path
                continue
            assert dest.scheme == 'https' and dest.netloc == 'wa.me' and dest.path == '/'+PHONE, path
            assert parse_qs(dest.query)['text'][0].strip(), path
        for link in page.links:
            dest = urlsplit(link)
            if dest.netloc or dest.scheme or not dest.path.startswith('/'):
                continue
            target = ROOT / unquote(dest.path).lstrip('/')
            if target.is_dir():
                target = target/'index.html'
            assert target.is_file(), (path,link)
            if target in pages and dest.fragment:
                assert unquote(dest.fragment) in pages[target].ids, (path,link)
    mapping = json.loads((ROOT/'programmes/finder-links.json').read_text())
    total = 0
    decoded = {p: [(k,parse_qs(urlsplit(link).query)['text'][0]) for k,link in page.actions if k == "fee"]
               for p,page in pages.items() if p.parent.name in ('universities','levels')}
    for uni in normalize_unis():
        names = uni['programmes']
        links = mapping[uni['shortName']]
        assert set(links) == set(names)
        university = ROOT/'programmes/universities'/(slug(uni['shortName'])+'.html')
        for name in names:
            ref = urlsplit(links[name])
            target = pages[ROOT/ref.path.lstrip('/')]
            assert not ref.fragment or ref.fragment in target.ids
            level = ROOT/'programmes/levels'/(LEVEL_SLUG[record_level(name)]+'.html')
            assert links[name] in pages[level].links
            for path in (university,level):
                assert any(k=='fee' and name in value and uni['university'] in value for k,value in decoded[path]), (name,path)
            total += 1
    print(f'{total} listing mappings, {len(docs)} pages and {fees} fee enquiries validated.')

if __name__ == '__main__':
    main()
