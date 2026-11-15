"""Useful qualification + subject comparison hubs from NextGenz's actual finder.

Purpose: rank naturally for searches like "Master in Computer Science Malaysia".
Not a page farm: only publish subject/level combinations with multiple
distinct university options, evidence from the source finder, decision advice,
working internal links and truthful official-source disclaimers.

Subject matching uses programme names only. It does not assert entry criteria,
current availability, professional licensing, or a university partnership.
"""
from __future__ import annotations
from collections import defaultdict
from urllib.parse import quote
from programme_subject_enrichment import SUBJECT_ENRICHMENT
import re

BASE = "https://www.nextgenzcentre.space"

# Each family is separately useful for a student making a decision. Add a field
# only when there's real content differentiation and relevant programme records.
FIELDS = [
    {
        "slug":"computer-science","name":"Computer Science",
        "pattern":r"computer science",
        "overview":"Computer science can involve programming, algorithms, mathematics, databases, computing systems and optional specialisations. A broadly named Computer Science degree and one focused on networks, multimedia or security may teach different modules.",
        "checks":[
            ("Curriculum depth","Review algorithms, programming, mathematics and practical projects in the actual module list rather than judging the subject from the course title."),
            ("Specialisation and award","Check whether the university awards Computer Science, Computer Science with an emphasis, or a separate Information Technology qualification."),
            ("Practical experience","Compare capstone projects, industrial placements, computing facilities and any specialist laboratory requirements.")
        ],
        "question":"Can a computer science programme include software engineering or data science?",
        "answer":"It may include related modules, but that is not the same as obtaining an independently named specialist award. Check the actual modules and qualification title."
    },
    {
        "slug":"information-technology","name":"Information Technology",
        "pattern":r"information technology",
        "overview":"Information technology often concentrates on the use, management and integration of information systems. Students should distinguish IT from Computer Science, software development and information security before deciding on a qualification.",
        "checks":[
            ("Programme focus","Compare networking, databases, cloud infrastructure, systems administration and business information systems modules."),
            ("Technical versus management content","Ask whether the programme focuses on technology implementation, software development or organisational IT."),
            ("Hands-on study","Review assessment projects and practical placement requirements when available.")
        ],
        "question":"Is an information technology qualification equivalent to computer science?",
        "answer":"Not automatically. Universities award different qualifications and their curricula can differ significantly. Check the subject modules and recognised award."
    },
    {
        "slug":"software-engineering","name":"Software Engineering",
        "pattern":r"software engineering",
        "overview":"Software engineering programmes can emphasise requirements analysis, code quality, testing, architecture and the software delivery lifecycle. Some universities place software engineering within a broader computer science programme.",
        "checks":[
            ("Award type","Confirm whether the final award is Software Engineering or Computer Science with a software focus."),
            ("Development lifecycle","Compare system design, secure development, testing, teamwork, DevOps and capstone requirements."),
            ("Industry relevance","Ask about real projects, company placements and opportunities to build a practical portfolio.")
        ],
        "question":"Does a software engineering course always teach the same programming languages?",
        "answer":"No. Programming tools and modules vary by university and intake. Review the latest official handbook."
    },
    {
        "slug":"data-science","name":"Data Science and Analytics",
        "pattern":r"data science|data analytics",
        "overview":"Data science and analytics programmes blend statistics, data handling, programming and quantitative methods in different proportions. Some courses emphasise business analytics while others emphasise machine learning and technical research.",
        "checks":[
            ("Prerequisite skills","Check mathematics, statistics and programming entry requirements, particularly for postgraduate courses."),
            ("Taught content","Compare machine learning, data engineering, visualisation, databases and quantitative methods in the curriculum."),
            ("Research versus applied projects","Ask whether the course includes an independent thesis, business capstone or placement.")
        ],
        "question":"Is data science the same as business analytics?",
        "answer":"They overlap, but analytics programmes may focus more on business decisions while data science can emphasise computing and statistics. Compare actual course modules."
    },
    {
        "slug":"artificial-intelligence","name":"Artificial Intelligence",
        "pattern":r"artificial intelligence",
        "overview":"Artificial intelligence titles can refer to dedicated degrees or specialist tracks within broader computing qualifications. The difference matters when comparing awarded qualifications.",
        "checks":[
            ("Award name","Identify whether artificial intelligence is the degree title or a specialisation."),
            ("Mathematical foundations","Review probability, linear algebra, algorithms and programming requirements."),
            ("Practical research","Compare computer vision, machine learning, data ethics and project options.")
        ],
        "question":"Can I specialise in AI within computer science?",
        "answer":"Some universities offer computing qualifications with AI-focused modules or named tracks. Check the published award and pathway."
    },
    {
        "slug":"cybersecurity","name":"Cybersecurity",
        "pattern":r"cyber ?security|information security",
        "overview":"Cybersecurity courses cover differing balances of secure systems, networks, digital forensics, risk and governance. Titles that include information security may be narrower or more management-oriented.",
        "checks":[
            ("Technical scope","Compare networks, operating systems, cryptography, secure development and security testing modules."),
            ("Practical exposure","Ask about controlled labs, secure exercises, dissertation projects or supervised industry work."),
            ("Qualification alignment","Check whether the programme is technical computing, information systems or security management.")
        ],
        "question":"Is cybersecurity the same as information security?",
        "answer":"They are related, but individual courses may emphasise different technical, organisational and risk-management skills."
    },
    {
        "slug":"business-administration","name":"Business Administration",
        "pattern":r"business administration",
        "overview":"Business administration courses may cover marketing, finance, operations, leadership, strategy and organisational decision-making. At postgraduate level, an MBA has different entry expectations from an undergraduate business degree.",
        "checks":[
            ("Programme stage","Confirm whether you need an undergraduate business degree, a specialised master's degree or an MBA route."),
            ("Specialisation and cases","Compare accounting, finance, HR, leadership and applied case-study modules."),
            ("Experience expectations","Ask about professional experience and project requirements, particularly for postgraduate study.")
        ],
        "question":"Is a bachelor's in business administration the same as an MBA?",
        "answer":"No. Bachelor's and MBA qualifications are different levels, with different entry requirements and academic objectives."
    },
    {
        "slug":"business-management","name":"Business Management",
        "pattern":r"business management|management studies",
        "overview":"Business management programmes may emphasise organisational leadership, operations, decision-making and strategy. Some are broad management awards, while others target a specialised industry.",
        "checks":[
            ("Management subject area","Review leadership, finance, marketing, people management and operations content."),
            ("Industry context","Check whether the award focuses on general management, project management or a professional sector."),
            ("Applied work","Ask about case studies, placement or dissertation requirements.")
        ],
        "question":"Should I choose business management or business administration?",
        "answer":"Both may contain similar modules. Choose based on the published curriculum, qualification level and specialisation."
    },
    {
        "slug":"accounting","name":"Accounting",
        "pattern":r"accounting|accountancy",
        "overview":"Accounting courses vary in financial reporting, tax, audit, managerial accounting and professional preparation. A course name alone does not verify exemptions from professional examinations.",
        "checks":[
            ("Professional recognition","Check the specific award against the latest information from the relevant accounting professional bodies."),
            ("Subject coverage","Compare tax, auditing, financial reporting, financial systems and business law."),
            ("Career location","Ask whether extra examinations or work experience are needed in the country where you hope to practise.")
        ],
        "question":"Does an accounting degree guarantee professional accountant status?",
        "answer":"No. Professional status may depend on accreditation, exams, work experience and the relevant jurisdiction."
    },
    {
        "slug":"finance","name":"Finance and Banking",
        "pattern":r"\bfinance\b|\bbanking\b",
        "overview":"Finance and banking qualifications may focus on corporate finance, investments, risk, quantitative finance or financial institutions. The exact specialisation is more important than the general word 'finance'.",
        "checks":[
            ("Core modules","Compare investment analysis, financial markets, corporate finance, risk and statistics."),
            ("Quantitative emphasis","Check mathematics, economics and computational requirements."),
            ("Professional aims","Consider the local regulatory environment and the expectations of your intended career.")
        ],
        "question":"Is a finance degree the same as an accounting degree?",
        "answer":"No. Finance often focuses on funding, markets and investment decisions, while accounting concentrates more on reporting, compliance and related analysis."
    },
    {
        "slug":"marketing","name":"Marketing",
        "pattern":r"marketing",
        "overview":"Marketing programmes may combine consumer behaviour, brand management, research, digital channels and business strategy. Degrees with 'integrated marketing communication' may have a communication emphasis.",
        "checks":[
            ("Digital and analytical focus","Review digital marketing, data interpretation, research methods and campaign assessment."),
            ("Brand and consumer modules","Compare strategy, consumer behaviour, advertising and communications content."),
            ("Portfolio experience","Ask about practical campaigns, industry briefs and internship options.")
        ],
        "question":"Does every marketing degree include digital marketing?",
        "answer":"Not necessarily to the same depth. Review the current module list and project requirements."
    },
    {
        "slug":"logistics","name":"Logistics and Supply Chain Management",
        "pattern":r"logistics|supply chain",
        "overview":"Logistics and supply-chain qualifications may prepare students for operations, procurement, distribution, manufacturing logistics and transport management. Industrial logistics and business-focused supply-chain awards are not necessarily identical.",
        "checks":[
            ("Study emphasis","Compare procurement, transportation, warehouse operations, analytics and industrial planning."),
            ("Industry learning","Check site visits, placements, simulation labs and projects."),
            ("Study costs","Request written fees that clarify whether amounts are annual, semester-based or total.")
        ],
        "question":"Is logistics the same as supply-chain management?",
        "answer":"They overlap; supply-chain management may cover planning and procurement across a wider system, while logistics often focuses on goods and transport operations."
    },
    {
        "slug":"psychology","name":"Psychology",
        "pattern":r"psycholog",
        "overview":"Psychology courses differ in research, behavioural science, social, developmental and clinical emphases. Qualification level matters for professional practice pathways.",
        "checks":[
            ("Professional pathway","Check the training and postgraduate steps needed for clinical psychology or counselling in the country where you plan to practise."),
            ("Core syllabus","Review research methods, statistics, development, social cognition and specialist modules."),
            ("Practice opportunities","Ask about supervised practice, research placements and assessment formats.")
        ],
        "question":"Can a psychology degree automatically qualify me as a clinical psychologist?",
        "answer":"No. Clinical qualifications and licensing often require recognised postgraduate education and supervised training."
    },
    {
        "slug":"nursing","name":"Nursing",
        "pattern":r"nursing",
        "overview":"Nursing qualifications require special attention to clinical placements, language requirements and professional registration. A nursing diploma and bachelor's nursing qualification have different progression and licensing implications.",
        "checks":[
            ("Clinical placements","Ask where practice placements take place, which requirements apply and whether international students can access them."),
            ("Professional registration","Check qualification recognition for the country where you plan to work as a nurse."),
            ("Entry conditions","Review science prerequisites, language evidence and any health checks.")
        ],
        "question":"Is a Malaysian nursing qualification automatically recognised overseas?",
        "answer":"No. Professional registration rules vary by destination country and qualification level."
    },
    {
        "slug":"medicine","name":"Medicine",
        "pattern":r"\bmedicine\b|\bmbbs\b",
        "overview":"Medical study involves regulated professional pathways and clinical placements. Programmes using MBBS, Doctor of Medicine or other titles must be evaluated against the exact award, curriculum and recognition rules.",
        "checks":[
            ("Professional eligibility","Check the specific qualification and its recognition by medical authorities where you intend to practise."),
            ("Clinical training","Confirm clinical placement arrangements, language requirements and programme duration directly with the university."),
            ("Academic admission","Review science prerequisites, admissions assessments and any country-specific conditions.")
        ],
        "question":"Does a medical degree automatically let me practise in another country?",
        "answer":"No. Licensing, exams, internship and qualification recognition may be separately required."
    },
    {
        "slug":"dentistry","name":"Dentistry",
        "pattern":r"dentistry|dental surgery",
        "overview":"Dental programmes lead through professional training and specific licensing processes. Dentistry degrees can differ in curriculum structure, clinical requirements and the qualification ultimately awarded.",
        "checks":[
            ("Clinical learning","Ask about patient exposure, supervised practical work and training arrangements."),
            ("Professional recognition","Check accreditation and licensing requirements in your intended working country."),
            ("Entry rules and duration","Confirm science subjects, language conditions, selection steps and total programme cost.")
        ],
        "question":"Is an international dentistry degree automatically valid for registration at home?",
        "answer":"No. Dental authorities may impose separate recognition, examination or practice requirements."
    },
    {
        "slug":"pharmacy","name":"Pharmacy",
        "pattern":r"pharmacy",
        "overview":"Pharmacy programmes may include pharmaceutical chemistry, pharmacology, therapeutics, laboratory practice and professional placements. Exact recognition is essential for anyone intending to practise as a pharmacist.",
        "checks":[
            ("Laboratory and placements","Review laboratory modules, clinical or community placements, and supervision arrangements."),
            ("Professional accreditation","Check whether the exact programme meets applicable registration rules and what additional training is required."),
            ("Admission requirements","Confirm science and English prerequisites and up-to-date full tuition.")
        ],
        "question":"Will a pharmacy degree qualify me to practise in any country?",
        "answer":"No. Pharmacist registration depends on local professional rules and qualification recognition."
    },
    {
        "slug":"education","name":"Education and Teaching",
        "pattern":r"education|teaching|tesol|tesl",
        "overview":"Education programmes can focus on primary, secondary, language teaching, leadership, educational technology or research. An education degree is not necessarily a teaching licence.",
        "checks":[
            ("Age range and subject","Check if the programme prepares students for a specific school level, subject or specialist education role."),
            ("Professional requirements","Confirm teaching registration and practice requirements where you intend to work."),
            ("Delivery and research","Review teaching practice, school placements, academic projects and research requirements.")
        ],
        "question":"Does an education degree guarantee a teaching licence?",
        "answer":"Not in every country. Registration, practical teaching requirements and qualification recognition vary by jurisdiction."
    },
    {
        "slug":"early-childhood","name":"Early Childhood Education",
        "pattern":r"early childhood",
        "overview":"Early childhood education courses focus on young children's development, learning environments, child welfare and pedagogical methods. Check whether the programme includes supervised childcare or school practice.",
        "checks":[
            ("Practical teaching","Ask about observation, supervised practice and institution placement."),
            ("Qualification purpose","Check whether the award is designed for classroom teaching, childcare or early years leadership."),
            ("Professional rules","Verify any required registration or safeguarding checks in your intended location.")
        ],
        "question":"Is early childhood education the same as a general education degree?",
        "answer":"Not necessarily. Early childhood pathways focus on younger learners and may have different practice and professional requirements."
    },
    {
        "slug":"electrical-engineering","name":"Electrical and Electronic Engineering",
        "pattern":r"electrical|electronic engineering",
        "overview":"Electrical and electronic engineering studies may involve circuits, signal processing, control, telecommunications or power systems. A degree's specialisation and accreditation affect progression and career pathways.",
        "checks":[
            ("Engineering discipline","Compare power, electronics, communications, control and embedded systems in official module lists."),
            ("Accreditation","Check whether the actual award and campus have relevant current engineering programme recognition."),
            ("Hands-on practice","Ask about laboratories, industrial training and design projects.")
        ],
        "question":"Is electrical engineering the same as electronic engineering?",
        "answer":"They overlap, but individual programmes can focus on different technologies and applications."
    },
    {
        "slug":"mechanical-engineering","name":"Mechanical Engineering",
        "pattern":r"mechanical engineering",
        "overview":"Mechanical engineering courses can include mechanics, materials, thermodynamics, fluid systems and design. Distinguish conventional engineering awards from engineering technology qualifications.",
        "checks":[
            ("Degree award","Confirm whether the qualification is mechanical engineering or mechanical engineering technology."),
            ("Practical projects","Check laboratories, design work, industrial training and software tools."),
            ("Professional route","Verify the relevant programme recognition for the specific course and study period.")
        ],
        "question":"Are all mechanical engineering degrees equivalent for professional registration?",
        "answer":"No. The exact award, accreditation, delivery mode and relevant professional rules matter."
    },
    {
        "slug":"civil-engineering","name":"Civil Engineering",
        "pattern":r"civil engineering",
        "overview":"Civil engineering programmes may focus on structures, geotechnics, construction, transportation, water or environmental systems. Programme recognition and practical learning are important when selecting a course.",
        "checks":[
            ("Specialisation","Review structures, geotechnics, transport and environmental module coverage."),
            ("Engineering accreditation","Confirm recognition for the exact degree and intended professional pathway."),
            ("Applied experience","Ask about laboratories, fieldwork, construction projects and industrial placements.")
        ],
        "question":"Can I become a professional engineer immediately after a civil engineering degree?",
        "answer":"Professional registration may require additional practice, supervision or assessments. Verify local rules."
    },
    {
        "slug":"architecture","name":"Architecture and Architectural Design",
        "pattern":r"architecture",
        "overview":"Architecture qualifications may be professional architecture degrees, interior architecture or design-oriented courses. Their studio requirements and professional recognition routes can be very different.",
        "checks":[
            ("Exact award","Differentiate architecture, interior architecture and architectural technology degrees."),
            ("Studio and portfolio","Check design studios, software, model-making and portfolio requirements."),
            ("Professional recognition","Ask whether the course satisfies a relevant professional architectural qualification stage in your intended country.")
        ],
        "question":"Is interior architecture the same as professional architecture?",
        "answer":"No. The two may have different learning objectives and professional recognition."
    },
    {
        "slug":"tourism-hospitality","name":"Tourism and Hospitality",
        "pattern":r"tourism|hospitality|hotel management",
        "overview":"Tourism and hospitality programmes may emphasise tourism planning, hotel operations, visitor management, events and customer experience. Study delivery and placement opportunities matter.",
        "checks":[
            ("Specialisation","Compare hospitality operations, event management, tourism planning and business content."),
            ("Work placements","Check the conditions for internships and practical workplace exposure, particularly for international students."),
            ("Campus and format","Confirm the specific campus, practical facilities and delivery mode.")
        ],
        "question":"Is a hospitality degree the same as a tourism degree?",
        "answer":"They overlap, but hotel operations, tourism planning and event-focused courses can emphasise different skills."
    },
    {
        "slug":"law","name":"Law",
        "pattern":r"\blaw\b|\bllb\b",
        "overview":"Law programmes can focus on domestic law, comparative law, commercial law or Shariah law. Professional recognition must be considered in the jurisdiction where the student wants to practise.",
        "checks":[
            ("Legal system","Review whether the course addresses Malaysian law, Shariah law, international law or another system."),
            ("Professional pathway","Check the additional training and qualification route needed for professional legal practice."),
            ("Research and practical work","Compare legal research, writing, placements and moot-court options.")
        ],
        "question":"Does an LL.B. automatically permit legal practice in another country?",
        "answer":"No. Each jurisdiction sets its own professional admission requirements."
    },
    {
        "slug":"biotechnology","name":"Biotechnology",
        "pattern":r"biotechnology|biomedical sciences",
        "overview":"Biotechnology and biomedical science degrees can include molecular biology, genetics, laboratory research and industrial applications. Their programme focuses and professional recognition may differ.",
        "checks":[
            ("Subject modules","Compare microbiology, genetics, biochemistry and laboratory techniques."),
            ("Research facilities","Review facilities, supervised projects and internship requirements."),
            ("Career qualifications","Confirm whether specialised laboratory or healthcare roles require additional certification.")
        ],
        "question":"Is biotechnology the same as biomedical science?",
        "answer":"Not necessarily. Biotechnology may emphasise applications across sectors, while biomedical sciences can focus on human disease and health research."
    },
    {
        "slug":"public-health","name":"Public Health",
        "pattern":r"public health",
        "overview":"Public health programmes may address epidemiology, policy, population health, biostatistics, environmental health or health promotion. They can be taught or research-focused.",
        "checks":[
            ("Epidemiology and statistics","Compare research methods, quantitative training and population-health topics."),
            ("Professional focus","Review health policy, programme evaluation and practical field placements."),
            ("Entry prerequisites","Ask whether a healthcare qualification, relevant experience or other prior degree is required.")
        ],
        "question":"Do all public health master's programmes require a medical degree?",
        "answer":"No. Entry requirements differ and may accept several relevant academic backgrounds. Check the university's criteria."
    }
]

LEVEL_LABELS = {
    "Foundation": "Foundation",
    "Diploma": "Diploma",
    "Bachelor": "Bachelor's",
    "Master": "Master's",
    "Doctorate": "PhD and Doctoral"
}
LEVEL_KEYWORDS = {
    "Foundation": "Foundation in",
    "Diploma": "Diploma in",
    "Bachelor": "Bachelor in",
    "Master": "Master in",
    "Doctorate": "Doctorate in"
}
LEVEL_GUIDANCE = {
    "Foundation": {
        "overview":"A foundation is generally a preparatory study route. Its value depends on which subsequent degree recognises the qualification and the grades required to progress.",
        "questions":[("Progression","Which specific bachelor's degrees accept the foundation, and are there additional subject or grade conditions?"),("Qualifications","Which school-leaving certificates and subject results does the institution accept?"),("Total costs","What is the full cost of the foundation and any later degree separately?")]
    },
    "Diploma": {
        "overview":"Diplomas have their own award level and often differ from preparatory foundation programmes. Ask whether the specific diploma provides relevant practical training or credit transfer toward a later degree.",
        "questions":[("Academic entry","What school qualifications, language evidence and subject prerequisites are required?"),("Credit transfer","Which bachelor's degrees accept this diploma and how many credits, if any, can transfer?"),("Work components","Are internships, supervised practice or placements included, and are they accessible to international students?")]
    },
    "Bachelor": {
        "overview":"Bachelor's degrees vary in professional recognition, study duration, curriculum and campus delivery. A broad subject title does not guarantee the same modules or award across universities.",
        "questions":[("Pre-requisites","Which school, foundation or diploma qualifications and English evidence are accepted?"),("Qualification recognition","What is the exact named award and its current recognition for the student's intended future use?"),("Duration and total fee","How long is the degree, which campus hosts it, and how is international tuition billed?")]
    },
    "Master": {
        "overview":"Master's programmes may follow taught coursework, research or mixed modes and may require prior degrees in specific subjects, a research proposal or professional experience.",
        "questions":[("Entry background","Is an undergraduate degree in a related subject necessary, and is professional experience required?"),("Taught or research","How many taught modules are included, and what dissertation, project or thesis is required?"),("Visa and format","Does the actual study mode support an international student pass where necessary?")]
    },
    "Doctorate": {
        "overview":"Doctoral programmes may involve independent research, supervision and progress reviews. Availability is influenced by project fit and supervision capacity as well as general entry eligibility.",
        "questions":[("Research proposal","What research area, proposal and previous academic qualifications are required?"),("Supervision and facilities","Is a qualified supervisor available for the intended topic?"),("Study mode and regulations","What are the official full-time or part-time rules, research milestones and any international student requirements?")]
    }
}
# Existing hand-edited subject pages are generally stronger answers for their
# exact study-level + keyword searches, so do not generate a duplicate.
EXISTING_EDITORIAL = {
    ("Master","business-administration"):"/programmes/topics/mba-malaysia.html",
    ("Foundation","business-administration"):"/programmes/topics/foundation-in-business-malaysia.html",
    ("Foundation","business-management"):"/programmes/topics/foundation-in-business-malaysia.html",
    ("Bachelor","accounting"):"/programmes/topics/accounting-degree-malaysia.html",
    ("Bachelor","computer-science"):"/programmes/topics/computer-science-degree-malaysia.html",
    ("Bachelor","software-engineering"):"/programmes/topics/software-engineering-degree-malaysia.html",
    ("Bachelor","psychology"):"/programmes/topics/psychology-degree-malaysia.html",
    ("Bachelor","nursing"):"/programmes/topics/nursing-degree-malaysia.html",
    ("Diploma","nursing"):"/programmes/topics/diploma-in-nursing-malaysia.html",
    ("Bachelor","mechanical-engineering"):"/programmes/topics/mechanical-engineering-degree-malaysia.html",
    ("Bachelor","logistics"):"/programmes/topics/logistics-degree-malaysia.html",
    ("Master","data-science"):"/programmes/topics/masters-data-science-malaysia.html",
}
# A fairly strict programme match avoids treating "Medical Imaging / Pharmacy
# / Nursing" as three separate programmes and claiming false offerings.
def clean_course(name: str) -> bool:
    low = name.lower()
    if len(name) > 140:
        return False
    if any(x in low for x in (" / ", " /", "/ ", "etc.", "all specialisations", "various specialisations", "all programmes", "other programmes", "miscellaneous")):
        return False
    if low.count(",") >= 2:
        return False
    return True


def field_for(name: str) -> list[dict]:
    if not clean_course(name):
        return []
    return [x for x in FIELDS if re.search(x["pattern"], name, flags=re.I)]


def _display_title(level: str, field: dict) -> str:
    return f"{LEVEL_KEYWORDS[level]} {field['name']} in Malaysia"


def generate_level_subject_pages(records, selected_urls, write, wrap_page, page_head, h, outputs, public_fee_note):
    """Publish only substantial comparison pages grounded in several universities."""
    groups = defaultdict(list)
    for rec in records:
        if rec["level"] not in LEVEL_GUIDANCE:
            continue
        for field in field_for(rec["name"]):
            groups[(rec["level"], field["slug"])].append(rec)
    pages = {}
    for (level, field_slug), rows in sorted(groups.items()):
        fld = next(f for f in FIELDS if f["slug"] == field_slug)
        by_uni = defaultdict(list)
        # No inflated count from repeated titles at the same institution.
        for rec in rows:
            if not any(q["name"] == rec["name"] for q in by_uni[rec["uni"]]):
                by_uni[rec["uni"]].append(rec)
        entries = [r for group in by_uni.values() for r in group]
        count_uni = len(by_uni)
        # Avoid single-university pages and highly sparse/near-duplicate topics.
        if count_uni < 2 or len(entries) < 3:
            continue
        editorial = EXISTING_EDITORIAL.get((level, field_slug))
        if editorial:
            pages[(level, field_slug)] = {"path": editorial, "entries":len(entries), "universities":count_uni, "editorial":True}
            continue

        page_path = f"/programmes/subjects/{level.lower()}-{field_slug}-malaysia.html"
        heading = _display_title(level, fld)
        enrichment = SUBJECT_ENRICHMENT.get((level, field_slug))
        title = enrichment["title"] if enrichment else f"{heading} | NextGenz Centre"
        if len(title) > 67:
            title = heading[:48].rsplit(" ",1)[0] + " | NextGenz"
        desc = enrichment["description"] if enrichment else f"Compare {LEVEL_LABELS[level].lower()} {fld['name'].lower()} programme names across {count_uni} Malaysian universities, with course links and entry, fee and pathway questions."
        intro = LEVEL_GUIDANCE[level]["overview"]
        main = (
            '<section class="hero"><div class="wrap"><span class="eyebrow">MALAYSIA UNIVERSITY PROGRAMME COMPARISON</span>'
            '<h1>' + h(heading) + '</h1>'
            '<p class="lead">' + h(enrichment["lead"] if enrichment else fld["overview"]) + '</p>'
            '<div class="catalog-stats"><span>' + str(count_uni) + ' listed universities</span><span>' + str(len(entries)) + ' relevant course names</span><span>' + h(LEVEL_LABELS[level]) + ' study level</span></div>'
            '<p><a class="button" href="https://wa.me/601167701210?text=' + quote("Hello NextGenz Centre. I am interested in " + heading + ". Please help me compare programmes.") + '">Ask for course guidance</a></p></div></section>'
            '<section class="section"><div class="wrap"><div class="article-layout"><article class="article">'
            '<h2>What does ' + h(fld["name"]) + ' study involve?</h2><p>' + h(fld["overview"]) + '</p>'
            '<h2>What to know about this qualification level</h2><p>' + h(intro) + '</p>'
            '<div class="catalog-note"><strong>Source and availability:</strong> Programme names, university locations, fee references and links below come from the NextGenz Centre existing finder database, not a live university admissions feed. A listed title does not mean that an intake is currently open or that NextGenz has an official relationship with that university. Current fees, entry requirements, course mode and availability must be checked in the university’s written information. Finder fees can differ in billing basis, and should never be treated as final quotes.</div>'
            '<h2>Compare universities with ' + h(LEVEL_LABELS[level].lower()) + ' ' + h(fld["name"].lower()) + ' programmes</h2>'
            '<p>Use the exact course names below to shortlist institutions. A course may contain this subject as one area of study or a specialisation, so read the full title before deciding whether it is the qualification you want.</p>'
            '<div class="catalog-comparison" role="region" aria-label="Compare actual listed university courses" tabindex="0">'
            '<table class="catalog-table"><thead><tr><th scope="col">University</th><th scope="col">Actual finder programme title</th><th scope="col">Reference fee — confirm basis</th></tr></thead><tbody>'
        )
        if enrichment:
            table_heading = '<h2>Compare universities with ' + h(LEVEL_LABELS[level].lower()) + ' ' + h(fld["name"].lower()) + ' programmes</h2>'
            if main.count(table_heading) != 1:
                raise RuntimeError("Could not place verified subject information for " + heading)
            main = main.replace(table_heading, enrichment["before_table"] + table_heading, 1)
        for uni, recs in sorted(by_uni.items(),key=lambda x:x[0]):
            for rec in recs:
                uh = "/programmes/universities/" + rec["uslug"] + ".html"
                detail = selected_urls.get((rec["uni"], rec["name"]), uh + "#" + rec["id"])
                main += (
                    '<tr><td><a href="' + h(uh) + '">' + h(rec["uni"]) + '</a><small class="catalog-loc">' + h(rec["location"]) + '</small></td>'
                    '<td><a href="' + h(detail) + '">' + h(rec["name"]) + '</a></td>'
                    '<td><span class="catalog-money">' + h(public_fee_note(rec)) + '</span></td></tr>'
                )
        main += '</tbody></table></div>'
        if enrichment:
            main += enrichment["after_table"]
        main += '<h2>How to compare ' + h(fld["name"].lower()) + ' options</h2>'
        for check,body in fld["checks"]:
            main += '<h3>' + h(check) + '</h3><p>' + h(body) + '</p>'
        main += '<h2>Questions for international applicants</h2>'
        for label,body in LEVEL_GUIDANCE[level]["questions"]:
            main += '<h3>' + h(label) + '</h3><p>' + h(body) + '</p>'
        main += '<h2>Frequently asked questions</h2>'
        main += '<h3>' + h(fld["question"]) + '</h3><p>' + h(fld["answer"]) + '</p>'
        main += '<h3>Are all listed ' + h(LEVEL_LABELS[level].lower()) + ' options currently accepting international students?</h3>'
        main += '<p>No. The listed titles are reference entries. Each university must confirm its current admissions status, recognised entry qualifications, course language, campus, fee schedule and visa-related eligibility. Your nationality and chosen study mode may affect the applicable student-pass route.</p>'
        main += '<h3>Can I ask NextGenz Centre to help me compare the universities?</h3>'
        main += '<p>Yes. NextGenz Centre offers free core university-placement guidance. Tell us your latest qualification, target field, budget and preferred intake. University, medical, immigration and other third-party charges remain separate; no admission or visa approval is guaranteed.</p>'
        main += (
            '<h2>Next steps to apply</h2><p>Use our <a href="/guides/how-to-study-in-malaysia.html">study in Malaysia admissions guide</a> to prepare academic documents, and consult the <a href="/guides/malaysia-student-visa-emgs-guide.html">Malaysia student visa and EMGS guide</a> for general process information. Confirm every official condition directly with the university before paying.</p>'
            '<p><a href="/programmes/">All Malaysian university programmes</a> · '
            '<a href="/programmes/levels/' + level.lower().replace("doctorate","phd") + '.html">All ' + h(LEVEL_LABELS[level]) + ' pathways</a> · '
            '<a href="/services/education-consultant-malaysia.html">Education consultant in Malaysia</a></p>'
            '</article><aside class="aside"><h2>Get an informed university shortlist</h2>'
            '<p>Send us your qualification, study budget and planned intake. We can help you confirm the current details for the programmes in your shortlist.</p>'
            '<a class="button" href="https://wa.me/601167701210?text=' + quote("Hello NextGenz Centre, please help me with " + heading) + '">Request free guidance ↗</a>'
            '<p><small>University and government fees are separate. University decisions and visa outcomes are not guaranteed.</small></p></aside></div></div></section>'
        )
        schema = {
            "@context":"https://schema.org",
            "@type":"CollectionPage",
            "name":heading,
            "url":BASE+page_path,
            "about":{"@type":"Thing","name":fld["name"]},
            "isPartOf":{"@type":"WebSite","name":"NextGenz Centre","url":BASE+"/"}
        }
        write(page_path.lstrip("/"),wrap_page(page_head(title,desc,page_path,schema),main),outputs)
        pages[(level,field_slug)] = {"path":page_path,"entries":len(entries),"universities":count_uni,"editorial":False}
    return pages
