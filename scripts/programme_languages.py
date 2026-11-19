"""Publish Arabic and Simplified Chinese catalogue views from the Finder's original records."""
from html import escape
import re
from programme_verified_facts import VERIFIED_PROGRAMMES
from programme_actions import action
from programme_level_subjects import field_for
from programme_topics import TOPICS, matches_topic
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

def localized(path, lang):
    return path if lang=='en' else path.replace('/programmes/', '/programmes/'+lang+'/',1)

def variants(path):
    return {code:localized(path,lang) for code,lang in [('en','en'),('ar','ar'),('zh-Hans','zh'),('x-default','en')]}

def alternates(path):
    return ''.join(f'<link rel="alternate" hreflang="{k}" href="{BASE}{v}">' for k,v in variants(path).items())

def publish(records, centres, subjects, levels, outputs, root, write, head, photo):
    english=sorted('/'+p.removesuffix('index.html') for p in outputs if p.endswith('.html'))
    by_path={}
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
                    '查看'+label+'，了解课程选择、入学申请和学费，按计划入学时间咨询费用明细。')
            address=localized(path,lang)
            page=head(label+' | NextGenz Centre',desc,address).replace('<html lang="en">','<html lang="'+tr('ar" dir="rtl','zh-CN')+'">')
            page=page.replace('<head>', '<head><!-- AUTO-GENERATED NEXTGENZ PROGRAMME DIRECTORY -->')
            page=page.replace('</head>',alternates(path)+'<script defer src="/assets/language-choice.js"></script></head>')
            def actions(topic):return action('consult',topic,lang)+' '+action('apply',topic,lang)
            src,_=photo(path)
            page+=header_html(lang,path)+'<main><section class="hero"><div class="wrap"><span class="eyebrow">NEXTGENZ CENTRE</span><h1>'+escape(label)+'</h1><p class="lead">'+escape(desc)+'</p><p>'+actions(label)+'</p></div><div class="ng-hero-media"><img src="'+src+'" alt="'+escape(label)+'"></div></section><section class="section"><div class="wrap"><article class="article">'
            page+='<p>'+local_link(directory,title[directory])+' · '+link('/'+lang+'/study-in-malaysia.html',tr('دليل الدراسة في ماليزيا','马来西亚留学指南'))+'</p>'
            if entries:
                page+='<h2>'+tr('التخصصات وشروط التقديم','课程与申请须知')+'</h2><p>'+tr('تظهر أسماء المؤهلات بصيغتها الرسمية لتسهيل مطابقتها مع خطاب القبول. اختر البرنامج واذكر جنسيتك وموعد التحاقك عند طلب بيان الرسوم. اسأل عن مدة الدراسة ولغة التدريس وأي تدريب إلزامي قبل التقديم.','下表保留官方课程名称，方便与录取通知书核对。咨询时请注明国籍和计划入学时间，并确认授课语言、学制和实习要求。')+'</p><ul class="catalog-list">'
                for r in entries:
                    up=university(r);subject='، '.join(field(f['slug']) for f in field_for(r['name']))
                    context=r['name']+' · '+r['uni']
                    dest=r.get('detail') or up+'#'+r['id']
                    fee = tr('اطلب بيان الرسوم لموعد التحاقك','请咨询本次入学的费用')
                    amount = re.fullmatch(r'([\d,]+(?:\.\d+)?)\s*(?:\((Per Semester|Per Year|Total)\))?', r['raw_fee'], re.I)
                    if amount and not VERIFIED_PROGRAMMES.get((r['short'],r['name']),{}).get('public_fee_note'):
                        period = (amount[2] or '').lower()
                        periods = {'per semester':tr('للفصل','每学期'),'per year':tr('للسنة','每年'),'total':tr('إجمالي','课程总额'),'':tr('الفترة غير مؤكدة','计费周期待确认')}
                        fee = tr('تقدير غير مؤكد','待确认的参考费用')+' · '+r['currency']+' '+amount[1]+' · '+periods[period]
                    course=escape(r['name']) if path==dest.split('#')[0] else local_link(dest,r['name'])
                    page+='<li id="'+escape(r['uslug']+'-'+r['id'] if path!=up else r['id'])+'"><div><bdi>'+course+'</bdi><br>'+(escape(r['uni']) if path==up else local_link(up,r['uni']))+' · '+escape(LEVEL[r['level']][i]+' · '+r['location'])+(' · '+escape(subject) if subject else '')+'</div><small>'+escape(fee)+' · '+action('fee',context,lang)+'</small></li>'
                page+='</ul>'
                level_paths = [directory+'levels/'+levels[lev]+'.html' for lev in levels if any(r['level']==lev for r in entries)]
                links = [local_link(p,title[p]) for p in level_paths if p != path]
                if links:
                    page += '<h2>'+tr('تصفّح البرامج في الجامعات الماليزية حسب المرحلة','按学历浏览马来西亚各大学课程')+'</h2><div class="catalog-links">'+''.join(links)+'</div>'
                if len(entries)==1:
                    r=entries[0];page+='<p>'+link(r['website'],tr('الموقع الرسمي للجامعة','大学官网'))+' · '+link(path,tr('تفاصيل البرنامج والرسوم بالإنجليزية','查看英文课程与费用详情'))+'</p>'
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
            write(filename,page,outputs)
            by_path[path]=True
    for path in by_path:
        file=path+('index.html' if path.endswith('/') else '')
        s=(root/file.lstrip('/')).read_text()
        s=s.replace(header_html(),header_html('en',path)).replace('</head>',alternates(path)+'<script defer src="/assets/language-choice.js"></script></head>')
        write(file,s,outputs)
