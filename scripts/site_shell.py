"""Use the landing-page footer on every public document, including translated catalogues."""
import re
import subprocess
from hashlib import sha256
from pathlib import Path
from site_header import header_html

ROOT = Path(__file__).resolve().parents[1]
def build_public_assets():
    build = ROOT/'scripts/public-build'
    out = ROOT/'programmes/site-assets'
    out.mkdir(parents=True, exist_ok=True)
    signature = sha256()
    for p in (ROOT/'index.html', build/'build.cjs', build/'package-lock.json'):
        signature.update(p.read_bytes())
    marker = out/'build.sha256'
    products = ('public-app.js','public-utilities.css','react-runtime.js','site-footer.css','footer.fragment')
    if marker.exists() and marker.read_text() == signature.hexdigest() and all((out/p).exists() for p in products):
        return
    if not (build/'node_modules/esbuild').exists():
        subprocess.run(['npm','ci','--no-audit','--no-fund'],cwd=build,check=True)
    subprocess.run(['node',str(build/'build.cjs')],cwd=ROOT,check=True)
    marker.write_text(signature.hexdigest())

def sync_public_shell():
    footer = (ROOT/'programmes/site-assets/footer.fragment').read_text()
    docs = [p for folder in ('ar','zh','programmes','guides','services') for p in (ROOT/folder).rglob('*.html')]
    docs += [ROOT/'about-nextgenz-centre.html', ROOT/'why-malaysia.html']
    for p in docs:
        raw = p.read_text()
        lang = 'ar' if '<html lang="ar"' in raw else 'zh' if '<html lang="zh' in raw else 'en'
        path = '/'+p.relative_to(ROOT).as_posix().removesuffix('index.html')
        catalogue_path = path.replace('/programmes/'+lang+'/', '/programmes/',1) if path.startswith('/programmes/') else ''
        raw = re.sub(r'<header class="nav ng-brand-header".*?</header>', lambda _:header_html(lang,catalogue_path,page_path=path), raw, count=1, flags=re.S)
        localized = footer
        if lang != 'en':
            for en, ar, zh in [
                ('Free Consultation on WhatsApp','استشارة مجانية عبر واتساب','通过 WhatsApp 免费咨询'),('Apply Now','قدّم الآن','立即申请'),('Explore Programs','تصفّح البرامج','浏览课程'),('Quick Links','روابط سريعة','快捷链接'),('Study Pathways','المسارات الدراسية','升学路径'),('About NextGenz Centre','عن مركز نكست جينز','关于 NextGenz Centre'),('Why Malaysia','لماذا ماليزيا','为何选择马来西亚'),('Contact Us','تواصل معنا','联系我们'),('Primary WhatsApp','واتساب','WhatsApp 联系方式'),('Admissions email','بريد القبول','招生邮箱'),('Ready to study in Malaysia?','هل أنت مستعد للدراسة في ماليزيا؟','准备好来马来西亚留学了吗？'),('Apply with confidence.','قدّم بثقة.','安心申请。')]:
                localized = localized.replace(en, ar if lang=='ar' else zh)
            localized = localized.replace('href="/programmes/', 'href="/programmes/'+lang+'/')
        raw = re.sub(r'<div id="ng-site-footer"[^>]*><footer\b.*?</footer></div>', '<footer class="foot"></footer>', raw, flags=re.S)
        raw,n = re.subn(r'<footer\b.*?</footer>',lambda _:localized,raw,count=1,flags=re.S)
        if not n: raise ValueError(f'Missing public footer: {p}')
        raw = raw.replace('/assets/site-footer.css', '/programmes/site-assets/site-footer.css')
        if '/programmes/site-assets/site-footer.css' not in raw:
            raw=raw.replace('</head>', '<link rel="stylesheet" href="/programmes/site-assets/site-footer.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"></head>')
        if p.read_text()!=raw: p.write_text(raw)
