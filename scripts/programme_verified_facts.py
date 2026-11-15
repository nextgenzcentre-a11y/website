"""Editorially verified programme facts from official university admissions webpages.

The finder is preserved as-is. These source-specific facts are displayed
separately, with their own official citations and date checked. They should
be re-checked when official university pages change. University requirements
or fees shown here are NOT guarantees of admission or a price quotation.
"""
VERIFIED_PROGRAMMES = {
  ("UM", "Foundation in Life Sciences"): {
    "official_name": "Foundation in Life Sciences",
    "source_url": "https://study.um.edu.my/foundation-in-life-sciences",
    "source_label": "Universiti Malaya official Foundation in Life Sciences programme page",
    "facts": [
      ("Published international tuition", "The university's programme page shows RM 35,000 for international students, excluding 6% Sales and Service Tax. This is the university's published reference, not a NextGenz quotation."),
      ("University intake reference", "The published page names its July intake for the 2026/2027 academic session. Ask UM about later intake availability."),
      ("Academic entry requirements", "UM publishes science subject requirements covering Biology, Mathematics, Physics, Chemistry and English. Minimum grades depend on the applicant's qualification type; check the official table."),
    ],
    "advice": "Ask UM to confirm the entry route for your nationality and the exact degree progression available after completion."
  },
  ("APU", "Foundation in Engineering"): {
    "official_name": "Foundation Programme (Engineering Route)",
    "source_url": "https://training.apu.edu.my/node/252",
    "source_label": "APU official Foundation Programme (Engineering Route) webpage",
    "facts": [
      ("Official programme naming", "APU's own site calls the route 'Foundation Programme (Engineering Route)'. The finder uses the shorter label 'Foundation in Engineering'."),
      ("Subject prerequisites", "APU lists O-Level or IGCSE routes needing five credits including Mathematics and Physics, Chemistry or Technical Science, subject to its equivalent-qualification rules."),
      ("Progression options", "APU identifies engineering-related degree pathways after completion, including electrical and electronic engineering and mechatronic or mechanical engineering."),
      ("University intake information", "APU's intake calendar lists a 12-month Foundation Programme with an Engineering route; the specific next available intake should be reconfirmed.")
    ],
    "second_source_url": "https://www.apu.edu.my/node/37",
    "second_source_label": "APU official intake calendar",
    "advice": "Check the exact certificate title and whether the Engineering Route is available for your chosen intake and entry qualification."
  },
  ("MMU", "Foundation in Engineering"): {
    "official_name": "Foundation in Engineering",
    "source_url": "https://www.mmu.edu.my/programmes-by-faculty-all/programmes-by-faculty-faie/foundation-in-engineering/",
    "source_label": "Multimedia University official Foundation in Engineering page",
    "facts": [
      ("Duration and language", "MMU lists a one-year foundation delivered entirely in English."),
      ("Entry requirements", "For the SPM or O-Level route, MMU describes five Grade C credits including English, Mathematics and an engineering-related subject, or accepted equivalents."),
      ("Progression", "MMU describes degree pathways in its Faculty of Artificial Intelligence and Engineering and Faculty of Engineering and Technology after the foundation."),
      ("Study content", "The university's listed modules include mathematics, mechanics, physics, engineering-related concepts and academic English across trimesters.")
    ],
    "second_source_url": "https://www.mmu.edu.my/fee-structure-international/",
    "second_source_label": "MMU official international fee schedule",
    "advice": "MMU's international fee schedule includes promotional and previous prices that can differ from the legacy NextGenz finder amount. Request a written 2026/2027 international quote, including dates and eligibility."
  },
  ("UniRazak", "Foundation in Arts"): {
    "official_name": "Foundation in Arts",
    "source_url": "https://unirazak.edu.my/programmes/foundation-in-arts-2/",
    "source_label": "UNIRAZAK official Foundation in Arts programme page",
    "facts": [
      ("Duration", "UNIRAZAK lists a minimum of one year of full-time study, comprising a 50-credit foundation pathway."),
      ("Intakes", "The programme page lists March, July and November intakes. Verify which date is open to international students."),
      ("Study content", "UNIRAZAK identifies introductory economics, management, ICT, English, social sciences, law and related subjects."),
      ("International English condition", "The programme's listed international applicant requirement is IELTS Band 4.0 or TOEFL 450, with a conditional-offer possibility when English evidence is not yet met.")
    ],
    "advice": "Conventional and open-distance-learning modes are listed. International applicants should verify which mode qualifies for the intended immigration/student-pass pathway."
  },
  ("UniRazak", "Diploma in Management"): {
    "official_name": "Diploma in Management",
    "source_url": "https://unirazak.edu.my/programmes/diploma-in-management/",
    "source_label": "UNIRAZAK official Diploma in Management programme page",
    "facts": [
      ("Duration", "UNIRAZAK lists a full-time minimum duration of 2 years and 4 months."),
      ("Intakes", "The official programme page lists March, July and November intakes."),
      ("Academic subjects", "The course introduces key areas including accounting, management, marketing and human resource management."),
      ("Programme recognition", "The UNIRAZAK programme page identifies the Diploma in Management under the reference A10617, with current status subject to the university and MQA register.")
    ],
    "second_source_url": "https://unirazak.edu.my/admission/programmes-accreditations/",
    "second_source_label": "UNIRAZAK official programme accreditation listing",
    "advice": "Obtain the current international tuition schedule and confirm whether the selected delivery format is eligible for your intended student-pass arrangements."
  },
  ("UCSI", "Foundation in Arts"): {
    "official_name": "Foundation in Arts",
    "public_fee_note": "UCSI official approx. international total: MYR 44,940 (country-dependent); old finder reference MYR 20,000",
    "source_url": "https://www.ucsiuniversity.edu.my/programmes/foundation-in-arts",
    "source_label": "UCSI University official Foundation in Arts programme page",
    "facts": [
      ("Duration and location", "UCSI lists a one-year full-time programme at Springhill."),
      ("Intakes", "The current programme page lists January, May and September intakes."),
      ("Entry routes", "UCSI lists five SPM/O-Level credits or three UEC credits, or recognised equivalents, in its published academic entry criteria."),
      ("Published international fee", "UCSI's official page currently displays approximate total international fees of RM 44,940. The page says visa and administration charges may vary by country. This substantially differs from the older RM 20,000 figure in the NextGenz finder; use the university's updated written quotation.")
    ],
    "advice": "Check that the Springhill campus and the exact programme's progression pathway match your degree plans."
  },
  ("UM", "Master of Business Administration (MBA)"): {
    "official_name": "Master of Business Administration (Coursework)",
    "source_url": "https://study.um.edu.my/master-of-business-administration-coursework",
    "source_label": "Universiti Malaya official Master of Business Administration (Coursework) page",
    "facts": [
      ("Full-time duration", "UM publishes three semesters as the full-time duration for its coursework MBA."),
      ("Professional experience", "UM's programme requirements include at least three years of full-time working experience after completing the first degree."),
      ("English proficiency", "The current university requirements list IELTS Academic Band 6.0, with other accepted tests and thresholds shown on the university page."),
      ("Coursework content", "The official modules include strategy, finance, managerial economics, research and options in business-related concentration areas.")
    ],
    "advice": "UM's admissions rules also require an appropriate degree and a faculty interview; review the university's full entry criteria and current tuition schedule."
  }
}
