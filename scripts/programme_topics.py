"""Editorial topic directories backed by the existing NextGenz programme finder.

These are human-relevant comparison collections, not mass-generated thin
keyword pages. Each topic has its own decision criteria and study questions.
Course/fee records are only finder references, not current university offers.
"""
from __future__ import annotations

from collections import defaultdict
import re
from urllib.parse import quote
from programme_verified_facts import VERIFIED_PROGRAMMES

BASE = "https://www.nextgenzcentre.space"

# Highly targeted course groups. Titles match actual Malaysian search intents
# seen in a live first-page sample and OpenSEO search-demand metrics.
TOPICS = [
    {
        "slug": "mba-malaysia",
        "label": "MBA in Malaysia",
        "title": "MBA in Malaysia | Compare University Programmes",
        "description": "Compare MBA programmes in Malaysia, including on-campus and online options in university finder listings. Check course mode, current fees and admissions.",
        "level": "Master",
        "pattern": r"master of business administration|\bmba\b",
        "lead": "An MBA can be designed for different career stages and study formats. Compare the specific university, taught or online mode, specialisation and budget rather than treating all MBA awards as interchangeable.",
        "intro": "A Master of Business Administration is a postgraduate business qualification. Within Malaysian universities, MBA programme titles may describe conventional taught courses, online delivery, specialisations or mixed academic formats. One institution's listed programme may differ substantially from another's in entry requirements, total scheduled tuition, coursework and attendance.",
        "choose": [
            ("Study format", "Ask whether the exact programme is campus-based, blended or fully online. International student visa eligibility cannot be assumed for online study; confirm with the provider."),
            ("Experience and prerequisites", "Ask whether a prior degree, a certain academic grade or professional experience is required. Some pathways may accept different qualifications."),
            ("Specialisations and capstone", "Compare management modules, any research or practical project, optional pathways and the actual award title."),
            ("International budget", "A per-semester MBA figure cannot be compared directly with a total-course amount. Ask for the full itemised international student schedule.")
        ],
        "questions": [
            ("Can international students study an MBA in Malaysia?", "International students may apply to Malaysian universities offering eligible postgraduate routes, subject to the specific programme's rules, admissions decision and any required student-pass approvals."),
            ("Is an online MBA the same as an on-campus MBA for a student visa?", "Not necessarily. Study mode and immigration eligibility are separate issues. Verify the course format and immigration pathway before committing to an online programme."),
            ("How can I compare MBA tuition fees?", "Request the provider's dated international fee schedule and separate tuition by semester, year or entire programme. Include deposits and additional university and official charges.")
        ]
    },
    {
        "slug": "foundation-in-science-malaysia",
        "label": "Foundation in Science Malaysia",
        "title": "Foundation in Science Malaysia | Compare Universities",
        "description": "Compare Foundation in Science and related science foundation programme names in Malaysia by university, location and entry questions.",
        "level": "Foundation",
        "pattern": r"foundation.*(science|sciences)",
        "exclude": r"social sciences",
        "lead": "A science foundation may be one route toward further university study, but progression depends on the exact foundation award and the degree you want next.",
        "intro": "Science foundation programmes are often chosen by students planning a future undergraduate degree in a science-related area. However, a Foundation in Life Sciences, Foundation in Physical Sciences and a generic Foundation in Science are not necessarily equivalent. The subject modules, progression agreements, assessment requirements and admissions pathways vary by institution.",
        "choose": [
            ("Progression degree", "Ask which particular bachelor’s programmes can be entered after successful foundation completion, and whether extra subject or grade conditions apply."),
            ("Science subjects", "Review whether the actual timetable emphasizes biology, chemistry, physics, mathematics or specialist preparatory subjects."),
            ("Foundation recognition", "Check whether another institution or your intended home country would recognise the foundation when seeking a later degree."),
            ("Programme costs", "Ask for the official international student foundation tuition and its payment schedule, including any separate laboratory or registration charges.")
        ],
        "questions": [
            ("Does a Foundation in Science guarantee admission to medicine?", "No. Medicine and other regulated programmes commonly have their own entry and selection rules. Ask about exact progression and eligibility in writing."),
            ("Is Foundation in Life Sciences the same as Foundation in Physical Sciences?", "They can cover different subject combinations. Compare their official module lists and progression routes rather than relying on their names."),
            ("Can an international student enter a Malaysian foundation?", "Eligibility depends on the university and the applicant's school qualifications, nationality and English requirements. Confirm the specific course's current rules.")
        ]
    },
    {
        "slug": "nursing-degree-malaysia",
        "label": "Nursing Degree Malaysia",
        "title": "Nursing Degree Malaysia | Compare University Courses",
        "description": "Explore Malaysian nursing degree names by university and learn what to verify about clinical placements, professional recognition and admissions.",
        "level": "Bachelor",
        "pattern": r"nursing",
        "lead": "Nursing courses need careful comparison of the academic award, clinical experience and the professional rules that apply where you intend to work.",
        "intro": "Not all nursing qualifications or delivery formats have the same career implications. Some finder entries relate to a bachelor's nursing degree, while other institutions list diplomas or advanced nursing routes separately. If you plan to register as a nurse in Malaysia or another country, confirm whether the specific award meets the relevant professional body's requirements.",
        "choose": [
            ("Clinical training", "Ask how practice placements are arranged, where they happen and whether international students may participate in required clinical activities."),
            ("Professional recognition", "Check university accreditation and nursing registration rules in the country where you intend to practise."),
            ("Degree title", "Differentiate a Bachelor of Nursing, Bachelor of Nursing Science and other related titles; read the official academic programme description."),
            ("Entry and health checks", "Confirm science prerequisites, language evidence and any medical, vaccination or other clinical-placement checks required.")
        ],
        "questions": [
            ("Does a Malaysian nursing degree automatically let me work abroad?", "No. Professional licensing and qualification recognition are controlled by the relevant country's nursing authority."),
            ("What is the difference between a diploma and bachelor's nursing route?", "They have different qualification levels and may lead to different progression or registration requirements. Verify the programme and professional rules."),
            ("Do international nursing students need English test scores?", "Language requirements depend on the programme and clinical conditions. Ask the university for its current accepted English evidence.")
        ]
    },
    {
        "slug": "computer-science-degree-malaysia",
        "label": "Computer Science Degree Malaysia",
        "title": "Computer Science Degree Malaysia | University Finder",
        "description": "Compare Malaysian bachelor degree programmes in computer science: AI, networks, software and related options, universities and entry checks.",
        "level": "Bachelor",
        "pattern": r"computer science",
        "lead": "Computer science degrees in Malaysia can emphasise different areas, from software and data to networks, AI and cybersecurity. The exact course structure matters.",
        "intro": "A programme titled Bachelor of Computer Science may be broad or may name a specific pathway. When selecting a university, compare its real curriculum rather than assuming all programmes with similar titles contain the same programming languages, mathematics or applied projects. Some entries in the finder combine several specialisations, which must be separated and confirmed with the university.",
        "choose": [
            ("Curriculum", "Compare core programming, algorithms, databases, mathematics and computing modules in the published programme handbook."),
            ("Specialisation", "Clarify the exact options for software engineering, artificial intelligence, networking, data science or other focus areas."),
            ("Practical work", "Ask whether the course has an internship, final-year project, laboratory sessions or industry collaboration."),
            ("Entry rules", "Check the academic mathematics prerequisites and accepted English-language evidence for international admission.")
        ],
        "questions": [
            ("Is computer science the same as software engineering?", "The two may overlap, but software engineering often focuses more specifically on the software development process. Compare the actual modules."),
            ("Can international students apply to computer science degrees in Malaysia?", "They may apply to institutions offering eligible programmes, provided they meet the exact academic and language admission requirements."),
            ("Which Malaysian university has the best computing degree?", "There is no universally best choice. Compare course content, campus, costs and accreditation against your intended career and further-study plans.")
        ]
    },
    {
        "slug": "foundation-engineering-malaysia",
        "label": "Foundation in Engineering Malaysia",
        "title": "Foundation in Engineering Malaysia | University Options",
        "description": "Compare university foundation engineering options in Malaysia and check maths, physics, degree progression and entry requirements.",
        "level": "Foundation",
        "pattern": r"foundation.*engineering",
        "lead": "If you want to study an engineering degree in Malaysia, begin by checking whether a particular foundation pathway leads to your chosen engineering discipline.",
        "intro": "Foundation in Engineering programmes may help students prepare for undergraduate engineering study, but the relationship between a foundation and an engineering degree is not always automatic. Entry rules, mathematics or physics requirements, assessment and progression policies depend on the institution and the degree pursued next.",
        "choose": [
            ("Target engineering discipline", "Check progression to mechanical, electrical, civil, chemical or any other specific engineering award before enrolment."),
            ("Mathematics and physics", "Look for the actual foundation syllabus and prerequisites rather than assuming every engineering foundation has identical subjects."),
            ("University progression route", "Ask for the institution's current written policy on minimum grades needed to progress to the chosen degree."),
            ("Fees and intake", "Verify the academic start date, actual campus and current total foundation costs, including registration and laboratory charges.")
        ],
        "questions": [
            ("Does Foundation in Engineering guarantee a Bachelor of Engineering place?", "No. Progression may depend on passing the foundation and meeting programme-specific requirements."),
            ("Which universities in Malaysia list an engineering foundation?", "The directory below shows engineering foundation names currently recorded in the NextGenz finder. The university must confirm each course's current availability."),
            ("Can I change engineering discipline after the foundation?", "That depends on the foundation syllabus and the destination degree's subject requirements. Ask the institution before deciding.")
        ]
    },
    {
        "slug": "foundation-arts-malaysia",
        "label": "Foundation in Arts Malaysia",
        "title": "Foundation in Arts Malaysia | Compare Universities",
        "description": "Find Foundation in Arts programme listings across universities in Malaysia and check degree pathways, entry requirements and fees.",
        "level": "Foundation",
        "pattern": r"foundation.*arts",
        "lead": "A Foundation in Arts can prepare students for a range of undergraduate subjects, but the actual progression options vary between institutions.",
        "intro": "The term Foundation in Arts does not necessarily mean fine arts. Depending on the institution, it may be a broader academic pre-university pathway. Students intending to pursue business, communication, education, social sciences or other degrees should ask which outcomes the precise foundation qualification supports.",
        "choose": [
            ("Progression", "Get a written list of bachelor’s degrees for which the foundation is accepted and the minimum grades required."),
            ("Subjects and assessment", "Compare the syllabus, language requirements, general subjects and any available field-specific components."),
            ("Future flexibility", "Ask whether the foundation can be used at another university or only within the institution offering it."),
            ("Total cost", "Verify the current international foundation tuition and any extra administrative or student-pass costs.")
        ],
        "questions": [
            ("Is Foundation in Arts only for fine art degrees?", "No. The exact pathway depends on the institution. Check its official progression routes."),
            ("Can Foundation in Arts lead to a business bachelor's degree?", "It may at some institutions, subject to the destination degree's requirements. Confirm directly with the chosen university."),
            ("Is a foundation the same as a diploma?", "No. They generally serve different academic purposes and may have different qualification levels and progression rules.")
        ]
    },
    {
        "slug": "accounting-degree-malaysia",
        "label": "Bachelor of Accounting Malaysia",
        "title": "Accounting Degree Malaysia | Compare Universities",
        "description": "Compare bachelor accounting programme names in Malaysia, including professional body recognition, subject modules and entry requirements.",
        "level": "Bachelor",
        "pattern": r"accounting",
        "lead": "Accounting degrees can differ in the mix of financial reporting, taxation, auditing, management accounting and professional recognition.",
        "intro": "A Bachelor of Accounting, a Bachelor of Accountancy and an Accounting and Finance degree may have different module combinations. Students considering a later professional qualification should check the specific programme's exemptions, if any, with the relevant professional accountancy organisation. Do not infer professional recognition solely from a course name.",
        "choose": [
            ("Programme modules", "Compare auditing, taxation, corporate reporting, management accounting, analytics and practical case work."),
            ("Professional exemptions", "Confirm any accreditation or exemptions with the relevant professional body for the exact university course and study intake."),
            ("Internship or practice", "Ask whether practical placements or workplace experience are included or required."),
            ("International admission", "Check academic prerequisites, English proficiency and the full international tuition schedule.")
        ],
        "questions": [
            ("Does an accounting degree in Malaysia automatically qualify me as an accountant abroad?", "No. Professional registration may require separate exams and work experience in the relevant country."),
            ("What is the difference between Accounting and Accounting & Finance?", "Accounting and Finance programmes may include additional investment and corporate finance modules. Confirm the published curriculum."),
            ("How should I compare tuition for accounting degrees?", "Request a current written international fee schedule; many reference figures have different semester, year and total bases.")
        ]
    },
    {
        "slug": "software-engineering-degree-malaysia",
        "label": "Software Engineering Degree Malaysia",
        "title": "Software Engineering Degree Malaysia | Universities",
        "description": "Compare university software engineering degree names in Malaysia and review curriculum, project experience, admissions and programme selection.",
        "level": "Bachelor",
        "pattern": r"software engineering",
        "lead": "Software engineering degrees and computer science degrees with a software focus can lead through different curricula; compare the actual award and modules.",
        "intro": "Some universities advertise a Bachelor of Software Engineering, while others list software engineering as a computer science specialisation. These can be materially different qualifications. Before applying, read the current published programme description, confirm the degree name that will be awarded and check your preferred campus and attendance mode.",
        "choose": [
            ("Core engineering approach", "Review software requirements, testing, secure development, system design, quality assurance and delivery modules."),
            ("Project and work experience", "Ask about the final-year project, team development work and the duration of any placement."),
            ("Related degree names", "Compare the actual award title with Computer Science, Information Technology and other computing pathways."),
            ("Requirements and fees", "Confirm mathematics prerequisites, language evidence, start dates and the full international student payment schedule.")
        ],
        "questions": [
            ("Is software engineering different from computer science?", "Often yes in emphasis, but curricula overlap. Judge the actual modules and qualification title at the university."),
            ("Which Malaysian universities offer software engineering options?", "The finder directory below lists course names containing 'software engineering'; it is a reference list rather than confirmed current admissions availability."),
            ("Are online software degrees eligible for a Malaysian student pass?", "Visa eligibility depends on delivery mode and official rules. Check with the university and EMGS rather than assuming online programmes qualify.")
        ]
    }
]


def matches_topic(item: dict, topic: dict) -> bool:
    if item["level"] != topic["level"]:
        return False
    name = item["name"]
    if not re.search(topic["pattern"], name, flags=re.I):
        return False
    return not (topic.get("exclude") and re.search(topic["exclude"], name, flags=re.I))


def matching_topics(item: dict) -> list[dict]:
    return [t for t in TOPICS if matches_topic(item, t)]


def generate_topic_pages(records, selected_urls, uni_slugs, write, wrap_page, page_head, h, outputs):
    """Build useful subject comparison pages; return their count/URLs."""
    made = {}
    for topic in TOPICS:
        matching = [e for e in records if matches_topic(e, topic)]
        if len(matching) < 3:
            continue
        destination = "/programmes/topics/" + topic["slug"] + ".html"
        universities = len(set(e["uni"] for e in matching))
        visible = list(matching)
        main = (
          '<section class="hero"><div class="wrap"><span class="eyebrow">MALAYSIA UNIVERSITY COURSE COMPARISON</span>'
          '<h1>' + h(topic["label"]) + ': <span class="accent">compare university courses</span></h1>'
          '<p class="lead">' + h(topic["lead"]) + '</p>'
          '<div class="catalog-stats"><span>' + str(len(visible)) + ' finder entries</span><span>' + str(universities) + ' universities</span><span>' + h(topic["level"]) + ' study pathway</span></div>'
          '<p><a class="button" href="https://wa.me/601167701210?text=' + quote("Hello NextGenz Centre, I want to compare " + topic["label"] + " programmes at Malaysian universities.") + '">Get free programme advice →</a></p></div></section>'
          '<section class="section"><div class="wrap"><div class="article-layout"><article class="article">'
          '<h2>What should you know about ' + h(topic["label"]) + '?</h2>'
          '<p>' + h(topic["intro"]) + '</p>'
          '<div class="catalog-note"><strong>Source and accuracy:</strong> The course names below come from the existing NextGenz Centre programme finder, not live university admission feeds. They may include grouped titles or older prices. Check the current course availability, qualification, entry criteria, fees, study mode and intakes with the institution. A listing does not imply an agency partnership or a confirmed seat.</div>'
          '<h2>Compare programmes listed in the finder</h2>'
          '<p>These ' + str(len(visible)) + ' reference entries across ' + str(universities) + ' Malaysian universities are starting points for your shortlist. Follow a programme to its information page or university entry. Fee figures are displayed as originally recorded: a value may be per semester, per year or for a whole programme, and different currencies must not be treated as directly comparable.</p>'
          '<div class="catalog-comparison" role="region" aria-label="Compare programmes" tabindex="0"><table class="catalog-table"><thead><tr><th scope="col">University</th><th scope="col">Programme listing</th><th scope="col">Fee reference (basis unverified)</th></tr></thead><tbody>'
        )
        for e in visible:
            university_url = "/programmes/universities/" + e["uslug"] + ".html"
            programme_url = selected_urls.get((e["uni"],e["name"]), university_url + "#" + e["id"])
            main += (
              '<tr><td><a href="' + h(university_url) + '">' + h(e["uni"]) + '</a><small class="catalog-loc">' + h(e["location"]) + '</small></td>'
              '<td><a href="' + h(programme_url) + '">' + h(e["name"]) + '</a></td>'
              '<td><span class="catalog-money">' + h(VERIFIED_PROGRAMMES.get((e["short"],e["name"]),{}).get("public_fee_note") or (e["currency"] + " " + e["raw_fee"] + " (finder reference)")) + '</span></td></tr>'
            )
        main += '</tbody></table></div>'
        # Link to primary university sources where the exact course listing has
        # been individually verified, rather than treating finder entries as
        # official university statements.
        verified_examples = [(e, VERIFIED_PROGRAMMES[(e["short"], e["name"])])
                             for e in visible if (e["short"], e["name"]) in VERIFIED_PROGRAMMES]
        if verified_examples:
            main += '<h2>Examples checked against official university sources</h2><p>These particular programme entries have been compared with the universities’ own published programme pages. Other listings above are still finder references; do not infer their availability from these examples.</p>'
            for entry, verified in verified_examples[:4]:
                link = selected_urls.get((entry["uni"],entry["name"]))
                main += '<section class="catalog-verified"><h3>' + h(verified["official_name"]) + ' — ' + h(entry["uni"]) + '</h3>'
                main += '<ul>'
                for label, fact in verified["facts"][:2]:
                    main += '<li><strong>' + h(label) + ':</strong> ' + h(fact) + '</li>'
                fee = next((x for x in verified["facts"] if "fee" in x[0].lower() or "tuition" in x[0].lower()), None)
                if fee and fee not in verified["facts"][:2]:
                    main += '<li><strong>' + h(fee[0]) + ':</strong> ' + h(fee[1]) + '</li>'
                main += '</ul><p><a href="' + h(verified["source_url"]) + '" target="_blank" rel="noopener noreferrer">Read official university source ↗</a>'
                if link:
                    main += ' · <a href="' + h(link) + '">View NextGenz programme details</a>'
                main += '</p></section>'
        main += (
          '<h2>How to choose the right ' + h(topic["label"]) + ' option</h2>'
          '<p>The following are specific checks to make before submitting an application or paying a deposit. When comparing institutions, ask the admissions team to confirm the answers in writing.</p>'
        )
        for name, detail in topic["choose"]:
            main += '<h3>' + h(name) + '</h3><p>' + h(detail) + '</p>'
        main += '<h2>Frequently asked questions</h2>'
        for question, answer in topic["questions"]:
            main += '<h3>' + h(question) + '</h3><p>' + h(answer) + '</p>'
        main += (
          '<h2>Applying to university in Malaysia</h2><p>Start by confirming your latest qualification, desired study intake, budget, nationality and English evidence. Ask each university to verify the exact programme and current admissions requirements. After an appropriate offer, follow the provider and official EMGS instructions for any applicable international student-pass process.</p>'
          '<p>NextGenz Centre can help clarify the comparison and preparation steps. Our core placement guidance is free to students; tuition, university charges and government fees are separate. Admission, visa and scholarships are never guaranteed.</p>'
          '<p><a href="/guides/how-to-study-in-malaysia.html">University admission guide for international students</a> · <a href="/guides/malaysia-student-visa-emgs-guide.html">EMGS student visa guidance</a> · <a href="/programmes/">All university programmes</a></p>'
          '</article><aside class="aside"><h2>Get an informed shortlist</h2><p>Share your qualifications, study level, budget and preferred intake. We can help you work out which universities and questions are most relevant.</p>'
          '<a class="button" href="https://wa.me/601167701210?text=' + quote("I am interested in " + topic["label"] + ". Please help me compare Malaysian universities.") + '">Ask NextGenz Centre ↗</a>'
          '<p><small>The university is responsible for admission decisions and fee quotations.</small></p>'
          '<p><a href="/services/education-consultant-malaysia.html">About our free consultancy advice</a></p></aside></div></div></section>'
        )
        schema = {
          "@context":"https://schema.org",
          "@type":"CollectionPage",
          "name":topic["label"] + " university programme comparison",
          "url":BASE+destination,
          "isPartOf":{"@type":"WebSite","name":"NextGenz Centre","url":BASE+"/"}
        }
        write(destination.lstrip("/"),wrap_page(page_head(topic["title"],topic["description"],destination,schema),main),outputs)
        made[topic["slug"]] = {"url":destination, "entries":len(visible), "universities":universities}
    return made
