// Deterministic public-course presentation and shared interface localisation.
// Keep verified award names, URLs, fee amounts, canonical and hreflang intact.
// Only translate reviewed exact visible text; never invent programme facts.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..');
const rows=[
  [
    "Before applying as an international student",
    "قبل التقديم كطالب دولي",
    "国际学生申请前须知"
  ],
  [
    "Ask about this course",
    "استفسر عن هذا البرنامج",
    "咨询此课程"
  ],
  [
    "Tell us your qualifications, study budget and intended intake so we can discuss what to confirm with the university.",
    "أخبرنا بمؤهلاتك وميزانيتك وموعد الالتحاق المطلوب لنناقش ما يجب تأكيده مع الجامعة.",
    "请告知您的学历、学习预算和计划入学时间，以便我们讨论需要向大学确认的事项。"
  ],
  [
    "Free programme advice ↗",
    "استشارة مجانية حول البرنامج ↗",
    "免费课程咨询 ↗"
  ],
  [
    "Our advisory fee is free. Official charges may apply.",
    "استشاراتنا مجانية. قد تُطبق رسوم رسمية.",
    "我们的咨询免费，官方费用可能另计。"
  ],
  [
    "University information and NextGenz assistance",
    "معلومات الجامعة ومساعدة نكست جينز",
    "大学信息与 NextGenz 协助"
  ],
  [
    "Check your route.",
    "تحقق من مسارك الدراسي.",
    "确认学习路径。"
  ],
  [
    "Match your offer to the course.",
    "طابق عرض القبول مع البرنامج.",
    "核对录取通知与课程。"
  ],
  [
    "Confirm your total before paying.",
    "تأكد من إجمالي التكاليف قبل الدفع.",
    "付款前确认总费用。"
  ],
  [
    "Ask for the tuition basis and a written breakdown of extra charges for your intake.",
    "اطلب أساس احتساب الرسوم الدراسية وبياناً مكتوباً بالرسوم الإضافية لموعد التحاقك.",
    "请索取适用于您入学批次的学费计费依据及额外费用书面明细。"
  ],
  [
    "Confirm the coursework, mixed-mode or research route; ask about the required academic background, attendance format and any work experience.",
    "تحقق مما إذا كان المسار بالمقررات أو مختلطاً أو بحثياً، واستفسر عن الخلفية الأكاديمية المطلوبة ونمط الحضور والخبرة العملية.",
    "确认授课型、混合型或研究型路径，并询问所需学术背景、出勤方式和工作经验。"
  ],
  [
    "Ask which degrees this foundation leads to, the progression grades required, and whether the intended intake accepts international applicants.",
    "استفسر عن الدرجات الجامعية التي يؤهل لها البرنامج التأسيسي والمعدلات المطلوبة للانتقال وما إذا كانت الدفعة تقبل الطلاب الدوليين.",
    "询问预科可衔接的学位、升学成绩要求，以及计划入学批次是否接受国际申请者。"
  ],
  [
    "If you plan to continue to a degree, ask which credits the receiving university will accept and how many semesters remain after transfer.",
    "إذا كنت تخطط لمتابعة البكالوريوس، اسأل عن الساعات المعتمدة التي تقبلها الجامعة وعدد الفصول المتبقية بعد التحويل.",
    "如计划继续攻读学位，请确认接收大学认可的学分及转学后剩余学期数。"
  ],
  [
    "Confirm any subject prerequisites, where practical or professional placements take place, and who arranges them if the course includes one.",
    "تحقق من متطلبات المواد الدراسية ومواقع التدريب العملي أو المهني ومن يتولى ترتيبه إن كان البرنامج يشمله.",
    "确认先修科目、实践或专业实习地点，以及课程如包含实习时由谁安排。"
  ],
  [
    "Ask about supervisor availability, research proposal requirements and how the faculty handles milestones and examination.",
    "استفسر عن توفر المشرفين ومتطلبات مقترح البحث وآلية متابعة المراحل والتقييم في الكلية.",
    "询问导师 是否有名额、研究计划要求及院系对阶段考核和考试的安排。"
  ],
  [
    "Check the official programme requirements",
    "اطّلع على متطلبات البرنامج الرسمية",
    "查看官方课程要求"
  ],
  [
    "International application checklist",
    "قائمة التحقق للتقديم الدولي",
    "国际学生申请清单"
  ],
  [
    "Official programme name:",
    "اسم البرنامج الرسمي:",
    "官方课程名称："
  ],
  [
    "View original university programme source ↗",
    "اطّلع على المصدر الرسمي للبرنامج الجامعي ↗",
    "查看大学官方课程原文 ↗"
  ],
  [
    "Official university website ↗",
    "الموقع الرسمي للجامعة ↗",
    "大学官方网站 ↗"
  ],
  [
    "Coursework content",
    "محتوى البرنامج الدراسي",
    "课程教学内容"
  ],
  [
    "Full-time duration",
    "مدة الدراسة بدوام كامل",
    "全日制学制"
  ],
  [
    "Professional experience",
    "الخبرة المهنية",
    "工作经验"
  ],
  [
    "English proficiency",
    "إتقان اللغة الإنجليزية",
    "英语语言能力"
  ],
  [
    "UM publishes three semesters as the full-time duration for its coursework MBA.",
    "تنشر جامعة مالايا مدة ثلاثة فصول دراسية لبرنامج ماجستير إدارة الأعمال بالمقررات بدوام كامل.",
    "马来亚大学公布的授课型 MBA 全日制学制为三个学期。"
  ],
  [
    "UM's programme requirements include at least three years of full-time working experience after completing the first degree.",
    "تشمل متطلبات البرنامج في جامعة مالايا خبرة عمل بدوام كامل لا تقل عن ثلاث سنوات بعد إتمام الدرجة الجامعية الأولى.",
    "马来亚大学的课程要求包括取得第一学位后至少三年全职工作经验。"
  ],
  [
    "The current university requirements list IELTS Academic Band 6.0, with other accepted tests and thresholds shown on the university page.",
    "تتضمن متطلبات الجامعة الحالية درجة 6.0 في اختبار IELTS الأكاديمي، وتوضح صفحة الجامعة الاختبارات الأخرى المقبولة والدرجات المطلوبة.",
    "大学现行要求包括 IELTS 学术类 6.0 分，其他认可考试和分数要求见大学网页。"
  ],
  [
    "The official modules include strategy, finance, managerial economics, research and options in business-related concentration areas.",
    "تشمل المقررات الرسمية الاستراتيجية والتمويل والاقتصاد الإداري والبحث، وخيارات للتخصص في مجالات الأعمال.",
    "官方课程模块包括战略、金融、管理经济学、研究及商业相关专业方向选项。"
  ],
  [
    "UM's admissions rules also require an appropriate degree and a faculty interview; review the university's full entry criteria and current tuition schedule.",
    "تشترط قواعد القبول في جامعة مالايا أيضاً درجة جامعية مناسبة ومقابلة مع الكلية؛ راجع شروط القبول الكاملة وجدول الرسوم الحالي لدى الجامعة.",
    "马来亚大学招生规则还要求适当的学位和院系面试；请查看大学完整的入学标准与现行学费表。"
  ],
  [
    "Source reviewed 15 November 2026. Check the university’s latest admissions and fee conditions before paying.",
    "تمت مراجعة المصدر في 15 نوفمبر 2026. تحقق من أحدث شروط القبول والرسوم لدى الجامعة قبل الدفع.",
    "来源审核于2026年11月15日。付款前请核实大学最新招生及收费条件。"
  ],
  [
    "Master of Business Administration (Coursework). The NextGenz finder title uses a slightly different label, so confirm the exact award on your application.",
    "ماجستير إدارة الأعمال (بالمقررات الدراسية). يستخدم دليل نكست جينز تسمية مختلفة قليلاً، لذا تأكد من اسم المؤهل الدقيق في طلبك.",
    "工商管理硕士（授课型）。NextGenz 目录使用略有不同的名称，请在申请时确认准确的学位名称。"
  ],
  [
    "For postgraduate study, check whether the programme is taught, research-based or mixed mode, and whether a proposal, portfolio or relevant work experience is required.",
    "للدراسات العليا، تحقق مما إذا كان البرنامج بالمقررات أو البحث أو بنظام مختلط، وما إذا كان يتطلب مقترح بحث أو ملف أعمال أو خبرة مهنية ذات صلة.",
    "申请研究生课程时，请确认是授课型、研究型还是混合型，以及是否需要研究计划、作品集或相关工作经验。"
  ],
  [
    "For business-related courses, review the specialisation, practical work components and recognition by any professional body relevant to your goals.",
    "في برامج الأعمال، راجع التخصص ومكونات التدريب العملي واعتراف الهيئات المهنية ذات الصلة بأهدافك.",
    "商业相关课程请核实专业方向、实践环节及与目标相关的专业机构认可情况。"
  ],
  [
    "Your future starts with one conversation",
    "مستقبلك يبدأ بمحادثة",
    "未来从一次交流开始"
  ],
  [
    "Universities",
    "الجامعات",
    "大学"
  ],
  [
    "Our Services",
    "خدماتنا",
    "我们的服务"
  ],
  [
    "Student & Agent Portals",
    "بوابات الطلاب والوكلاء",
    "学生与代理门户"
  ],
  [
    "Admissions Process",
    "إجراءات القبول",
    "招生流程"
  ],
  [
    "Become an Agent",
    "كن وكيلاً",
    "成为代理"
  ],
  [
    "Study Articles & News",
    "مقالات وأخبار الدراسة",
    "留学资讯"
  ],
  [
    "Frequently Asked Questions",
    "الأسئلة الشائعة",
    "常见问题"
  ],
  [
    "All Malaysia University Programmes",
    "جميع البرامج الجامعية في ماليزيا",
    "马来西亚大学课程总览"
  ],
  [
    "MBA University Comparison",
    "مقارنة برامج ماجستير إدارة الأعمال",
    "MBA 大学比较"
  ],
  [
    "Foundation in Science Malaysia",
    "البرنامج التأسيسي في العلوم في ماليزيا",
    "马来西亚科学预科"
  ],
  [
    "Computer Science Degrees",
    "درجات علوم الحاسوب",
    "计算机科学学位"
  ],
  [
    "Nursing Degrees Malaysia",
    "درجات التمريض في ماليزيا",
    "马来西亚护理学位"
  ],
  [
    "Education Consultant in Malaysia",
    "مستشار تعليمي في ماليزيا",
    "马来西亚教育顾问"
  ],
  [
    "University Comparison Guide",
    "دليل مقارنة الجامعات",
    "大学比较指南"
  ],
  [
    "Free University Placement",
    "خدمة القبول الجامعي المجانية",
    "免费大学申请协助"
  ],
  [
    "Foundation & Diploma",
    "البرامج التأسيسية والدبلوم",
    "预科与文凭"
  ],
  [
    "Bachelor Degrees",
    "البكالوريوس",
    "学士学位"
  ],
  [
    "Master Degrees",
    "الماجستير",
    "硕士学位"
  ],
  [
    "PhD & Research",
    "الدكتوراه والبحث",
    "博士与研究"
  ],
  [
    "Search all degree subjects →",
    "ابحث في جميع التخصصات ←",
    "搜索全部学科 →"
  ],
  [
    "More programme fields",
    "مجالات دراسية إضافية",
    "更多课程领域"
  ],
  [
    "Psychology degrees",
    "درجات علم النفس",
    "心理学学位"
  ],
  [
    "Nursing diplomas",
    "دبلومات التمريض",
    "护理文凭"
  ],
  [
    "Mechanical engineering",
    "الهندسة الميكانيكية",
    "机械工程"
  ],
  [
    "Logistics & supply chain",
    "اللوجستيات وسلاسل الإمداد",
    "物流与供应链"
  ],
  [
    "Business foundation",
    "البرنامج التأسيسي في الأعمال",
    "商科预科"
  ],
  [
    "Master's in Data Science",
    "ماجستير علوم البيانات",
    "数据科学硕士"
  ],
  [
    "English Language & IELTS",
    "اللغة الإنجليزية و IELTS",
    "英语与 IELTS"
  ],
  [
    "EMGS Visa & Arrival",
    "تأشيرة EMGS والوصول",
    "EMGS 签证与抵达"
  ],
  [
    "Study in Malaysia guides",
    "أدلة الدراسة في ماليزيا",
    "马来西亚留学指南"
  ],
  [
    "Verified programme guides",
    "أدلة البرامج المتحقق منها",
    "已核实课程指南"
  ],
  [
    "Service area / address",
    "منطقة الخدمة / العنوان",
    "服务区域 / 地址"
  ],
  [
    "Selangor, Malaysia",
    "سيلانغور، ماليزيا",
    "马来西亚雪兰莪"
  ],
  [
    "Education advisory and admissions support across Malaysia.",
    "استشارات تعليمية ودعم للقبول في جميع أنحاء ماليزيا.",
    "在马来西亚各地提供教育咨询与入学支持。"
  ],
  [
    "Chat with an advisor",
    "تحدث مع مستشار",
    "与顾问交流"
  ],
  [
    "Privacy & Cookies",
    "الخصوصية وملفات تعريف الارتباط",
    "隐私与 Cookie"
  ],
  [
    "Admin",
    "الإدارة",
    "管理"
  ],
  [
    "Explore more courses at this university →",
    "استكشف المزيد من البرامج في هذه الجامعة ←",
    "浏览该大学更多课程 →"
  ],
  [
    "Compare its programmes, degree levels and finder-listed fees",
    "قارن البرامج والمراحل والرسوم المرجعية في الدليل",
    "比较课程、学历层次及目录参考学费"
  ],
  [
    "Search all university courses →",
    "ابحث في جميع البرامج الجامعية ←",
    "搜索全部大学课程 →"
  ],
  [
    "Filter 1,182 programmes by study level, university and subject",
    "صفِّ 1,182 برنامجاً بحسب المرحلة والجامعة والتخصص",
    "按学历层次、大学和学科筛选 1,182 门课程"
  ],
  [
    "MASTER STUDIES IN MALAYSIA",
    "دراسة الماجستير في ماليزيا",
    "马来西亚硕士课程"
  ],
  [
    "BACHELOR STUDIES IN MALAYSIA",
    "دراسة البكالوريوس في ماليزيا",
    "马来西亚学士课程"
  ],
  [
    "FOUNDATION STUDIES IN MALAYSIA",
    "الدراسة التأسيسية في ماليزيا",
    "马来西亚预科课程"
  ],
  [
    "DIPLOMA STUDIES IN MALAYSIA",
    "دراسة الدبلوم في ماليزيا",
    "马来西亚文凭课程"
  ],
  [
    "DOCTORATE STUDIES IN MALAYSIA",
    "دراسة الدكتوراه في ماليزيا",
    "马来西亚博士课程"
  ],
  [
    "Not listed",
    "غير مدرج",
    "未列出"
  ],
  [
    "Study in Malaysia",
    "الدراسة في ماليزيا",
    "留学马来西亚"
  ],
  [
    "Before applying",
    "قبل التقديم",
    "申请前"
  ],
  [
    "Your Malaysia education partner for 100% FREE university placement, English language school admissions and end-to-end student visa guidance.",
    "شريكك التعليمي في ماليزيا للحصول على دعم مجاني بالكامل للقبول الجامعي وقبول مدارس اللغة الإنجليزية وإرشاد شامل لتأشيرة الطالب.",
    "您的马来西亚教育伙伴：提供完全免费的大学申请协助、英语学校入学协助及全程学生签证指导。"
  ],
  [
    "Get 100% FREE university placement and English language school admissions support, plus end-to-end EMGS student visa guidance with progress tracking from 15% to 100%.",
    "احصل على دعم مجاني بالكامل للقبول الجامعي وقبول مدارس اللغة الإنجليزية، وإرشاد شامل لتأشيرة الطالب عبر EMGS مع متابعة التقدم من 15% إلى 100%.",
    "享受完全免费的大学及英语学校入学协助，以及 EMGS 学生签证全程指导和 15% 至 100% 的进度跟踪。"
  ]
];
const decode=s=>s.replace(/&#x27;|&#39;|&apos;/gi,"'").replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&nbsp;/g,' ');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const maps={ar:new Map(rows.map(r=>[r[0],r[1]])),zh:new Map(rows.map(r=>[r[0],r[2]]))};
function localise(segment,lang){
 const map=maps[lang];let n=0;
 // Tokenise only text, preserving attributes, scripts, comments and styles byte-for-byte.
 const result=segment.replace(/<!--[\s\S]*?-->|<script\b[\s\S]*?<\/script\s*>|<style\b[\s\S]*?<\/style\s*>|<(?:[^>"']|"[^"]*"|'[^']*')*>|[^<]+/gi,t=>{
  if(t.startsWith('<'))return t;
  const v=t.trim(),key=decode(v),translated=map.get(key);
  if(!translated)return t;
  n++;return t.slice(0,t.indexOf(v))+esc(translated)+t.slice(t.indexOf(v)+v.length);
 });
 return {result,n};
}
function markEnglish(s){
 // Scope to simple block elements with no existing language/direction attribute.
 // Keep English source details explicitly LTR until reviewed translation exists.
 return s.replace(/<(p|h2|h3|dt|dd|li)(\s[^>]*)?>([\s\S]*?)<\/\1>/gi,(m,tag,attrs='',inner)=>{
  if(/\b(?:lang|dir)\s*=/.test(attrs)||/<(?:p|h2|h3|dt|dd|li)\b/i.test(inner))return m;
  const visible=decode(inner.replace(/<[^>]+>/g,' '));
  if(!/[A-Za-z]{3,}/.test(visible)||/[\u0600-\u06ff\u3400-\u9fff]/u.test(visible))return m;
  return '<'+tag+attrs+' lang="en" dir="ltr">'+inner+'</'+tag+'>';
 });
}
function snapshot(s){
 return JSON.stringify({links:[...s.matchAll(/\b(?:href|src)="([^"]*)"/g)].map(m=>m[1]).filter(x=>!x.startsWith('/guides/style.css?v=')),head:s.match(/<head>[\s\S]*?<\/head>/i)?.[0]?.replace(/\/guides\/style\.css\?v=[^"]+/g,'/guides/style.css'),ads:[...s.matchAll(/<script\b[^>]*>[\s\S]*?<\/script>/gi)].map(m=>m[0])});
}
function patch(s,lang){
 const before=snapshot(s);
 let count=0;
 if(!/<body(?:\s[^>]*)?>/i.test(s)||!s.includes('class="ng-hero-media"'))throw Error('missing course markup');
 s=s.replace(/<body(\s[^>]*)?>/i,(m,a='')=>/\bclass="/.test(a)?'<body'+a.replace(/class="([^"]*)"/,'class="$1 ng-course-quality"')+'>':'<body'+a+' class="ng-course-quality">');
 s=s.replace(/\/guides\/style\.css\?v=[^"]+/g,'/guides/style.css?v=20261127-course-quality');
 if(lang!=='en'){
  const apply=x=>{const v=localise(x,lang);count+=v.n;return lang==='ar'?markEnglish(v.result):v.result;};
  s=s.replace(/<main>[\s\S]*?<\/main>/i,apply).replace(/<footer\b[\s\S]*?<\/footer>/i,apply);
 }
 if(before!==snapshot(s))throw Error('URL, head or script changed unexpectedly');
 return {s,count};
}
const stats={en:0,ar:0,zh:0,translated:0};
for(const lang of ['en','ar','zh']){
 const dir=path.join(root,'programmes',...(lang==='en'?[]:[lang]),'courses');
 for(const uni of fs.readdirSync(dir,{withFileTypes:true}).filter(x=>x.isDirectory())){
  for(const file of fs.readdirSync(path.join(dir,uni.name)).filter(x=>x.endsWith('.html'))){
   const p=path.join(dir,uni.name,file);
   const old=fs.readFileSync(p,'utf8');
   const {s,count}=patch(old,lang);
   fs.writeFileSync(p,s);stats[lang]++;stats.translated+=count;
  }
 }
}
if(!stats.en||!stats.ar||!stats.zh||!stats.translated)throw Error('Public course QA found no expected pages or translations');
const mba=fs.readFileSync(path.join(root,'programmes/ar/courses/um/master-of-business-administration-mba-ad2244.html'),'utf8');
if(!mba.includes('استفسر عن هذا البرنامج')||!mba.includes('محتوى البرنامج الدراسي')||!mba.includes('ng-course-quality'))throw Error('Arabic MBA regression');
console.log('Public course quality: '+JSON.stringify(stats));
