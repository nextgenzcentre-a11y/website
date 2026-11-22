"""Applicant guidance for dedicated programme pages, keyed to the actual award."""

from html import escape

PROGRAMME_GUIDANCE = {
    ("UPM", "Foundation Studies for Agricultural Science"): (
        ("ms", "Asasi Sains Pertanian UPM untuk pelajar antarabangsa",
         "Semak laluan antarabangsa P00053, tempoh dua semester, syarat kemasukan dan ijazah yang boleh dipohon selepas tamat asasi."),
        ("en", "UPM international intake and degree progression",
         "Ask UPM about the P00053 intake for international applicants. Before accepting, confirm in writing which UPM degrees you can apply for after the foundation and what grades you need to progress."),
    ),
    ("MMU", "Bachelor of Accounting (Hons.)"): (
        ("fr", "Licence en comptabilité à MMU : campus, durée et dossier",
         "MMU présente son Bachelor in Accounting (Honours) de Cyberjaya sur trois ans. Demandez à l’université de confirmer le campus, la durée et les critères d’admission correspondant à votre diplôme et à la rentrée souhaitée."),
        ("en", "MMU Accounting for international applicants",
         "Use the Cyberjaya programme page to check the three-year structure. If your offer names another campus or intake, confirm its programme duration, entry requirements and international fees separately. Ask the relevant professional body which exemptions apply to your award and graduating cohort."),
    ),
}

LEVEL_CHECKS = {
    "Foundation": "Ask which degrees this foundation leads to, the progression grades required, and whether the intended intake accepts international applicants.",
    "Diploma": "If you plan to continue to a degree, ask which credits the receiving university will accept and how many semesters remain after transfer.",
    "Bachelor": "Confirm any subject prerequisites, where practical or professional placements take place, and who arranges them if the course includes one.",
    "Master": "Confirm the coursework, mixed-mode or research route; ask about the required academic background, attendance format and any work experience.",
    "Doctorate": "Ask about supervisor availability, research proposal requirements and how the faculty handles milestones and examination.",
}


def programme_applicant_guidance(entry, checked):
    name = escape(entry["name"])
    institution = escape(entry["uni"])
    level_check = LEVEL_CHECKS.get(
        entry["level"], "Confirm the qualification level, award title and intended progression with the institution."
    )
    sections = PROGRAMME_GUIDANCE.get((entry["short"], entry["name"]), ())
    localized = "".join(
        f'<div lang="{lang}"><h3>{escape(title)}</h3><p>{escape(body)}</p></div>'
        for lang, title, body in sections
    )
    source = (checked or {}).get("source_url")
    reference = (
        f'<a href="{escape(source, quote=True)}">Check the official programme requirements</a>'
        if source else
        f'<a href="/programmes/universities/{escape(entry["uslug"], quote=True)}.html">Browse {institution}’s catalogue entries and university link</a>'
    )
    return (
        '<section class="catalog-wide" aria-labelledby="programme-applicant-guidance">'
        '<h2 id="programme-applicant-guidance">Before applying as an international student</h2>'
        f'{localized}<ol>'
        f'<li><strong>Check your route.</strong> {escape(level_check)}</li>'
        f'<li><strong>Match your offer to the course.</strong> For {name}, ask {institution} to confirm the exact award, campus, study mode and start date.</li>'
        '<li><strong>Confirm your total before paying.</strong> Ask for the tuition basis and a written breakdown of extra charges for your intake.</li>'
        f'</ol><p>{reference} · <a href="/guides/how-to-study-in-malaysia.html">International application checklist</a></p>'
        '</section>'
    )
