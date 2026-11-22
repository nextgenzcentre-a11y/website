"""Publish Arabic and Simplified Chinese catalogue views from the Finder's original records."""
from html import escape
import re
from programme_verified_facts import VERIFIED_PROGRAMMES
from programme_actions import tuition_range, action, labelled_catalogue
from programme_level_subjects import field_for
from programme_topics import TOPICS, matches_topic
from catalogue_search import catalogue_search
from site_header import header_html

BASE = 'https://www.nextgenzcentre.space'
LEVEL = {'Foundation':('السنة التأسيسية','预科'),'Diploma':('الدبلوم','文凭'),
         'Bachelor':('البكالوريوس','学士'),'Master':('الماجستير','硕士'),
         'Doctorate':('الدكتوراه','博士'),'Other':('مسارات أخرى','其他课程')}
FIELDS = dict(line.split('|',1) for line in """computer-science|علوم الحاسوب/计算机科学
information-technology|تقنية المعلومات/信息技术
software-engineering|هندسة البرمجيات/软件工程
data-science|علم البيانات/数据科学
artificial-intelligence|الذكاء الاصطناعي/人工智能
cybersecurity|الأمن السيبراني/网络安全
business-administration|إدارة الأعمال/工商管理
business-management|إدارة المؤسسات/商业管理
accounting|المحاسبة/会计
finance|التمويل/金融
marketing|التسويق/市场营销
logistics|الخدمات اللوجستية/物流
psychology|علم النفس/心理学
nursing|التمريض/护理学
medicine|الطب/医学
dentistry|طب الأسنان/牙科
pharmacy|الصيدلة/药学
education|التربية والتعليم/教育学
early-childhood|التربية في مرحلة الطفولة المبكرة/幼儿教育
electrical-engineering|الهندسة الكهربائية والإلكترونية/电气与电子工程
mechanical-engineering|الهندسة الميكانيكية/机械工程
civil-engineering|الهندسة المدنية/土木工程
architecture|العمارة/建筑学
tourism-hospitality|السياحة والضيافة/旅游与酒店管理
law|القانون/法学
biotechnology|التقنية الحيوية/生物技术
public-health|الصحة العامة/公共卫生""".splitlines())
TOPIC_LABELS = {'mba':'ماجستير إدارة الأعمال/工商管理硕士','masters-data-science':'ماجستير علم البيانات/数据科学硕士',
 'foundation-in-science':'السنة التأسيسية في العلوم/理科预科','foundation-in-business':'السنة التأسيسية في الأعمال/商科预科',
 'foundation-engineering':'السنة التأسيسية في الهندسة/工程预科','foundation-arts':'السنة التأسيسية في الآداب/文科预科',
 'diploma-in-nursing':'دبلوم التمريض/护理文凭'}

# Short search labels for awards whose official names are long or list multiple tracks.
COURSE_LABELS = {
    'Foundation Studies for Agricultural Science': ('السنة التأسيسية في العلوم الزراعية', '农业科学预科'),
    'Foundation in Engineering': ('السنة التأسيسية في الهندسة', '工程预科'),
    'Foundation in Science and Technology': ('السنة التأسيسية في العلوم والتكنولوجيا', '科学与技术预科'),
    'Foundation in Life Sciences': ('السنة التأسيسية في علوم الحياة', '生命科学预科'),
    'Bachelor of Computer Science': ('بكالوريوس علوم الحاسوب', '计算机科学学士'),
    'Master of Philosophy (Software Engineering, Computer Science, Informatics) (Research Mode)':
        ('ماجستير بحثي في مجالات الحوسبة', '计算机相关方向研究型哲学硕士'),
}

def localized(path, lang):
    return path if lang=='en' else path.replace('/programmes/', '/programmes/'+lang+'/',1)

def variants(path):
    return {code:localized(path,lang) for code,lang in [('en','en'),('ar','ar'),('zh-Hans','zh'),('x-default','en')]}

def alternates(path):
    return ''.join(f'<link rel="alternate" hreflang="{k}" href="{BASE}{v}">' for k,v in variants(path).items())

def mirror_english_layout(path, title, description, lang, level, root):
    """Retain complete English page structure while localising navigation labels.

    Avoid the old alternate one-card template which dropped verified course
    facts, costs, comparisons, admissions questions and application guidance.
    Official award names and university-source details remain unaltered.
    """
    source_file = root / path.lstrip("/")
    if path.endswith("/"):
        source_file = source_file / "index.html"
    english = source_file.read_text(encoding="utf-8")
    first, last = english.find("<main>"), english.rfind("</main>")
    if first < 0 or last < first:
        raise ValueError("Source page has no content: " + path)
    main = english[first:last + len("</main>")]
    main = re.sub(r'(<p class="lead(?: [^"]*)?">).*?(</p>)',
                  lambda m: m.group(1) + escape(description) + m.group(2),
                  main, count=1, flags=re.S)
    translations = {
        "ar": {
            "Finder-listed tuition is indicative and may not match the current international quote. Use Fee breakdown for the billing period, taxes and additional charges.": "رسوم الدليل هي أرقام مرجعية وليست عرضاً رسمياً محدثاً للطلاب الدوليين. اطلب تفاصيل الرسوم لمعرفة فترة السداد والضرائب والرسوم الإضافية.",
            "Programme details":"تفاصيل البرنامج",
            "Home":"الرئيسية",
            "Course finder":"البحث عن البرامج",
            "University programmes":"برامج الجامعة",
            "Programme title in finder":"اسم البرنامج في الدليل",
            "Institution":"الجامعة",
            "Study level grouping":"المرحلة الدراسية",
            "University location":"موقع الجامعة",
            "Tuition fee (finder reference)":"الرسوم الدراسية (مرجع الدليل)",
            "Intake reference":"مواعيد الالتحاق المرجعية",
            "Is this programme right for you?":"هل هذا البرنامج مناسب لك؟",
            "How to apply in Malaysia":"كيفية التقديم في ماليزيا",
            "Questions to ask before you apply":"أسئلة يجب طرحها قبل التقديم",
            "University confirmation required":"يلزم تأكيد الجامعة",
            "Explore similar university options":"استكشف برامج جامعية مشابهة",
            "Questions for international applicants":"أسئلة المتقدمين الدوليين",
            "Entry guidance":"إرشادات القبول",
            "Application questions":"أسئلة التقديم",
            "University information":"معلومات الجامعة",
            "Student visa guide":"دليل تأشيرة الطالب",
            "Current information from":"معلومات حالية من",
            "Current information to confirm with":"معلومات يجب تأكيدها مع",
            "Official university website":"الموقع الرسمي للجامعة",
            "Free Consultation on WhatsApp":"استشارة مجانية عبر واتساب",
            "Apply Now":"قدّم الآن",
            "Fee breakdown":"تفاصيل الرسوم",
            "View programme details":"عرض تفاصيل البرنامج",
            "Explore more courses at this university":"استكشف برامج أخرى في هذه الجامعة",
            "Search all university courses":"ابحث في جميع البرامج الجامعية",
            "Finder-listed ":"وفق الدليل ",
            "Choose the exact programme":"اختر التخصص الدقيق",
        },
        "zh": {
            "Finder-listed tuition is indicative and may not match the current international quote. Use Fee breakdown for the billing period, taxes and additional charges.": "目录学费仅供参考，不代表最新国际学生官方报价。请索取费用明细以确认计费周期、税费和其他必要费用。",
            "Programme details":"课程详情",
            "Home":"首页",
            "Course finder":"课程搜索",
            "University programmes":"大学课程",
            "Programme title in finder":"目录中的课程名称",
            "Institution":"大学",
            "Study level grouping":"学历层次",
            "University location":"大学所在地",
            "Tuition fee (finder reference)":"学费（目录参考）",
            "Intake reference":"入学批次参考",
            "Is this programme right for you?":"这项课程适合你吗？",
            "How to apply in Malaysia":"如何申请马来西亚大学",
            "Questions to ask before you apply":"申请前应确认的问题",
            "University confirmation required":"需向大学核实",
            "Explore similar university options":"探索类似大学课程",
            "Questions for international applicants":"国际学生常见问题",
            "Entry guidance":"入学指导",
            "Application questions":"申请问题",
            "University information":"大学信息",
            "Student visa guide":"学生签证指南",
            "Current information from":"大学最新资料：",
            "Current information to confirm with":"需与大学确认的信息：",
            "Official university website":"大学官方网站",
            "Free Consultation on WhatsApp":"通过 WhatsApp 免费咨询",
            "Apply Now":"立即申请",
            "Fee breakdown":"费用明细",
            "View programme details":"查看课程详情",
            "Explore more courses at this university":"浏览这所大学的其他课程",
            "Search all university courses":"搜索全部大学课程",
            "Finder-listed ":"目录参考 ",
            "Choose the exact programme":"选择准确的课程",
        },
    }
    for source, translated in translations[lang].items():
        # Only replace visible labels or explicit fee prefixes; never modify
        # institution URLs or source citations.
        if source.endswith(" "):
            main = main.replace(source, translated)
        else:
            main = main.replace(">" + source + "<", ">" + translated + "<")
    main = main.replace(">Current information from ",
                        ">معلومات حالية من " if lang == "ar" else ">大学最新资料：")
    main = main.replace(">Current information to confirm with ",
                        ">معلومات يجب تأكيدها مع " if lang == "ar" else ">需与大学确认的信息：")
    main = re.sub(r"<h1(?:\s[^>]*)?>.*?</h1>",
                  "<h1>" + escape(title) + "</h1>", main, count=1,flags=re.S)
    for category in ("courses/", "universities/", "levels/", "subjects/", "topics/",
                     "english-language-centres.html"):
        main = main.replace('href="/programmes/' + category,
                            'href="/programmes/' + lang + '/' + category)
    main = main.replace('href="/programmes/"',
                        'href="/programmes/' + lang + '/"')
    notice = ("<p class=\"ng-language-context-notice\" lang=\"ar\">تحتفظ معلومات الجامعة بأسماء الشهادات والتفاصيل الرسمية بلغتها الأصلية لضمان الدقة. انتقل إلى نفس الأقسام كما في الصفحة الإنجليزية.</p>"
              if lang == "ar" else
              "<p class=\"ng-language-context-notice\" lang=\"zh-CN\">为保持准确性，官方学位名称和大学来源信息保留原文。本页面与英文版具有相同的课程详情和申请部分。</p>")
    main = main.replace('<article class="article">',
                        '<article class="article">' + notice, 1)
    return main

def publish(records, centres, subjects, levels, outputs, root, write, head, photo):
    english=sorted('/'+p.removesuffix('index.html') for p in outputs if p.endswith('.html'))
    by_path={}
    search_titles = {}
    for lang,i in [('ar',0),('zh',1)]:
        def tr(ar,zh):return (ar,zh)[i]
        def field(key):return FIELDS[key].split('/')[i]
        def link(url,label):return f'<a href="{escape(url,quote=True)}">{escape(label)}</a>'
        def local_link(path,label):return link(localized(path,lang),label)
        directory='/programmes/'
        university=lambda r:directory+'universities/'+r['uslug']+'.html'
        title={directory:tr('دليل الجامعات والتخصصات في ماليزيا','马来西亚大学与专业目录'),
               directory+'subjects/':tr('تصفّح التخصصات والدرجات في الجامعات الماليزية','按专业和学历浏览马来西亚大学课程'),
               directory+'english-language-centres.html':tr('معاهد ودورات اللغة الإنجليزية في ماليزيا','马来西亚英语语言学校与课程')}
        rows={}
        for r in records:
            path=university(r)
            title[path]=tr('تخصصات ورسوم جامعة ','大学专业与学费 · ')+r['uni']
            rows.setdefault(path,[]).append(r)
            if r.get('detail'):
                path=r['detail'];title[path]=LEVEL[r['level']][i]+' · '+r['name']+' · '+r['short'];rows[path]=[r]
        for lev,slug in levels.items():
            path=directory+'levels/'+slug+'.html'
            title[path]=tr('برامج '+LEVEL[lev][i]+' في ماليزيا','马来西亚'+LEVEL[lev][i]+'课程')
            rows[path]=[r for r in records if r['level']==lev]
        for (lev,key),spec in subjects.items():
            if not spec['editorial']:
                path=spec['path'];title[path]=tr(LEVEL[lev][i]+' في '+field(key)+' في ماليزيا','马来西亚'+field(key)+LEVEL[lev][i]+'课程')
                rows[path]=[r for r in records if r['level']==lev and any(f['slug']==key for f in field_for(r['name']))]
        for topic in TOPICS:
            path=directory+'topics/'+topic['slug']+'.html'
            if path not in english:continue
            key=topic['slug'].removesuffix('-malaysia').removesuffix('-degree')
            title[path]=(TOPIC_LABELS.get(key) or FIELDS[key]).split('/')[i]+tr(' في ماليزيا',' · 马来西亚课程')
            rows[path]=[r for r in records if matches_topic(r,topic)]
        assert set(title)==set(english),set(english)^set(title)
        for path in english:
            label=title[path];entries=rows.get(path,[])
            desc=tr('استكشف '+label+'، وراجع خيارات القبول والرسوم المناسبة لموعد التحاقك مع مستشار يتحدث العربية.',
                    '查看'+label+'，了解大学课程、入学条件、申请步骤和学费参考，核对英语要求并向顾问咨询最新的费用明细和入学时间。')
            address=localized(path,lang)
            # Keep the complete official programme name in the visible H1.
            # Shorten search-only titles when concatenating a long English
            # qualification and Arabic level would make Google truncate them.
            seo_title = label + ' | NextGenz Centre'
            if len(seo_title) > 60:
                suffix = ' | NextGenz'
                seo_title = label + suffix
                if len(seo_title) > 60:
                    short = entries[0]['short'] if len(entries) == 1 and entries[0].get('detail') == path else ''
                    if short:
                        course_fields = [f for f in field_for(entries[0]['name']) if f['slug'] in FIELDS]
                        if course_fields:
                            academic_subject = field(course_fields[0]['slug'])
                            concise = LEVEL[entries[0]['level']][i] + ' · ' + academic_subject + ' · ' + short + suffix
                            if len(concise) <= 60:
                                seo_title = concise
                    if len(seo_title) > 60 and short:
                        # For long or composite qualifications, preserve a
                        # complete study subject instead of truncating mid-name.
                        core = entries[0]['name'].split('(', 1)[0].strip()
                        course_name = entries[0]['name']
                        translated = COURSE_LABELS.get(course_name) or COURSE_LABELS.get(core)
                        local_core = translated[i] if translated else LEVEL[entries[0]['level']][i] + ' · ' + core
                        concise = local_core + ' · ' + short + suffix
                        if len(concise) <= 60:
                            seo_title = concise
                    if len(seo_title) > 60:
                        label_without_short = label.removesuffix(' · ' + short) if short else label
                        reserved = len(suffix) + (len(' · ' + short) if short else 0)
                        budget = 60 - reserved
                        clipped = label_without_short[:budget].rsplit(' ', 1)[0].strip(' ·,')
                        if len(clipped) < 20:
                            clipped = label_without_short[:budget].rstrip(' ·,')
                        seo_title = clipped + (' · ' + short if short else '') + suffix
            if seo_title in search_titles:
                # Shortened multilingual course labels can collide for distinct
                # finder entries. Keep the complete H1 and distinguish their
                # search titles using a stable URL-derived suffix.
                from hashlib import sha1
                unique_tail = ' · ' + sha1(address.encode('utf-8')).hexdigest()[:8]
                seo_title = seo_title[:60-len(unique_tail)].rstrip(' ·,') + unique_tail
                if seo_title in search_titles:
                    raise ValueError(f"Duplicate translated search title: {address}")
            search_titles[seo_title] = address
            # The full lead paragraph stays visible. Only the search
            # description is condensed when the original exceeds 160 chars.
            seo_desc = desc
            if len(seo_desc) > 158:
                short_topic = seo_title.split(' | ')[0]
                seo_desc = tr(
                    'اطلع على ' + short_topic + ' وشروط القبول والرسوم الرسمية المحدثة. استشارة مجانية.',
                    '查看' + short_topic + '的课程资料、入学资格、英语语言要求、学费参考和申请流程。与NextGenz教育顾问确认最新入学批次、正式费用明细及必要文件。',
                )
            page=head(seo_title,seo_desc,address).replace('<html lang="en">','<html lang="'+tr('ar" dir="rtl','zh-CN')+'">')
            page=page.replace('<head>', '<head><!-- AUTO-GENERATED NEXTGENZ PROGRAMME DIRECTORY -->')
            page=page.replace('</head>',alternates(path)+'<script defer src="/assets/language-choice.js"></script></head>')
            # Use the SAME full information architecture as the English
            # university, course and guide page. Language changes do not
            # switch to a truncated list-only template.
            if path in english:
                body = mirror_english_layout(path, label, desc, lang, entries[0]['level'] if entries else '', root)
                page += header_html(lang,path) + body + (
                    '<footer class="foot"><div class="wrap">'
                    + action('consult',label,lang) + ' ' + action('apply',label,lang)
                    + '</div></footer></body></html>')
                filename=address+('index.html' if address.endswith('/') else '')
                write(filename, page, outputs)
                by_path[path]=True
                continue
            def actions(topic):return action('consult',topic,lang)+' '+action('apply',topic,lang)
            src,_=photo(path)
            page+=header_html(lang,path)+'<main><section class="hero"><div class="wrap"><span class="eyebrow">NEXTGENZ CENTRE</span><h1>'+escape(label)+'</h1><p class="lead">'+escape(desc)+'</p><p>'+actions(label)+'</p></div><div class="ng-hero-media"><img src="'+src+'" alt="'+escape(label)+'"></div></section><section class="section"><div class="wrap"><article class="article">'
            if path == directory:
                page += catalogue_search(lang)
            page+='<p>'+local_link(directory,title[directory])+' · '+link('/'+lang+'/study-in-malaysia.html',tr('دليل الدراسة في ماليزيا','马来西亚留学指南'))+'</p>'
            if entries:
                page+='<h2>'+tr('التخصصات وشروط التقديم','课程与申请须知')+'</h2><p>'+tr('تظهر أسماء المؤهلات بصيغتها الرسمية لتسهيل مطابقتها مع خطاب القبول. اختر البرنامج واذكر جنسيتك وموعد التحاقك عند طلب بيان الرسوم. اسأل عن مدة الدراسة ولغة التدريس وأي تدريب إلزامي قبل التقديم.','下表保留官方课程名称，方便与录取通知书核对。咨询时请注明国籍和计划入学时间，并确认授课语言、学制和实习要求。')+'</p><ul class="catalog-list">'
                for r in entries:
                    up=university(r)
                    subject_labels = []
                    for f in field_for(r['name']):
                        label_text = field(f['slug'])
                        hub = subjects.get((r['level'], f['slug']))
                        subject_labels.append(local_link(hub['path'], label_text) if hub and hub['path'] != path else escape(label_text))
                    subject = tr('، ', '、').join(subject_labels)
                    context=r['name']+' · '+r['uni']
                    dest=r.get('detail') or up+'#'+r['id']
                    fee = tuition_range(r['raw_fee'], r['currency'], lang)
                    course=escape(r['name']) if path==dest.split('#')[0] else local_link(dest,r['name'])
                    page+='<li id="'+escape(r['uslug']+'-'+r['id'] if path!=up else r['id'])+'"><div><bdi>'+course+'</bdi><br>'+(escape(r['uni']) if path==up else local_link(up,r['uni']))+' · '+escape(LEVEL[r['level']][i]+' · '+r['location'])+(' · '+subject if subject else '')+'</div><small>'+escape(fee)+' · '+action('fee',context,lang)+'</small></li>'
                page+='</ul>'
                level_paths = [directory+'levels/'+levels[lev]+'.html' for lev in levels if any(r['level']==lev for r in entries)]
                links = [local_link(p,title[p]) for p in level_paths if p != path]
                if links:
                    page += '<h2>'+tr('تصفّح البرامج في الجامعات الماليزية حسب المرحلة','按学历浏览马来西亚各大学课程')+'</h2><div class="catalog-links">'+''.join(links)+'</div>'
                if len(entries)==1:
                    r=entries[0];page+='<p>'+link(r['website'],tr('الموقع الرسمي للجامعة','大学官网'))+' · '+link(path,tr('تفاصيل البرنامج والرسوم بالإنجليزية','查看英文课程与费用详情'))+'</p>'
                if len(entries) == 1 and entries[0].get('detail') == path and entries[0].get('other_providers'):
                    page += '<h2>' + tr('جامعات أخرى تقدم برنامجًا بالاسم نفسه', '开设同名课程的其他大学') + '</h2><ul>'
                    for provider, url in entries[0]['other_providers']:
                        page += '<li>' + local_link(url, provider) + '</li>'
                    page += '</ul>'
            elif path.endswith('english-language-centres.html'):
                page+='<p>'+tr('قارن الدورات المتاحة واسأل عن عدد ساعات التدريس واختبار تحديد المستوى وتكلفة التسجيل لكل معهد.','选择语言学校时，请核对每周课时、分班测试、开课日期及报名费用。')+'</p>'
                for c in centres:
                    page+='<h2>'+escape(c['university'])+'</h2><p>'+escape(' · '.join(c['programmes']))+'</p><p>'+action('fee',c['university'],lang)+'</p>'
            else:
                for group,heading in [('levels',tr('مراحل الدراسة','按学历浏览')),('subjects',tr('التخصصات','按专业浏览')),('topics',tr('تصفّح البرامج حسب المجال','按热门专业浏览')),('universities',tr('الجامعات','按大学浏览'))]:
                    page+='<h2>'+heading+'</h2><div class="catalog-links">'+''.join(local_link(p,title[p]) for p in english if '/'+group+'/' in p and p!=path and not p.endswith('/'))+'</div>'
                page+='<p>'+local_link(directory+'english-language-centres.html',title[directory+'english-language-centres.html'])+'</p>'
            page+='<p>'+action('fee',label,lang)+'</p><p>'+actions(label)+'</p></article></div></section></main><footer class="foot"><div class="wrap">NEXTGENZ CENTRE · '+local_link(directory,tr('تصفّح البرامج في الجامعات الماليزية','浏览马来西亚各大学课程'))+'</div></footer></body></html>'
            filename=address+('index.html' if address.endswith('/') else '')
            write(filename,labelled_catalogue(page,lang),outputs)
            by_path[path]=True
    for path in by_path:
        file=path+('index.html' if path.endswith('/') else '')
        s=(root/file.lstrip('/')).read_text()
        s=s.replace(header_html(),header_html('en',path)).replace('</head>',alternates(path)+'<script defer src="/assets/language-choice.js"></script></head>')
        write(file,s,outputs)
