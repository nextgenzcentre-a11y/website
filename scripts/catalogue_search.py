"""Render the catalogue search controls in each existing catalogue language."""

from html import escape


COPY = {
    "en": (
        "Search all university programmes",
        "Search by course, university abbreviation or qualification, such as software engineering, MBA, BSc or PhD. Common short forms and small spelling mistakes are supported.",
        "Course or university", "Search", "Clear", "Searching the catalogue…",
        "{count} matching listings. Showing up to 25.",
        "No matching programme. Try the subject, qualification or university on its own.",
        "Search is temporarily unavailable. Use the course and university links below.",
    ),
    "ar": (
        "ابحث في جميع التخصصات الجامعية",
        "ابحث باسم التخصص أو المؤهل أو اختصار الجامعة، مثل هندسة البرمجيات أو ماجستير أو MBA.",
        "التخصص أو الجامعة", "بحث", "مسح", "جارٍ البحث في الدليل…",
        "{count} نتيجة مطابقة. يُعرض ما يصل إلى 25 نتيجة.",
        "لا توجد نتيجة مطابقة. جرّب اسم التخصص أو المؤهل أو الجامعة وحده.",
        "البحث غير متاح مؤقتًا. استخدم روابط التخصصات والجامعات أدناه.",
    ),
    "zh": (
        "搜索全部大学课程",
        "可输入专业名称、学历层次或大学简称，例如软件工程、计算机科学、硕士或 MBA。",
        "课程或大学", "搜索", "清空", "正在搜索课程目录…",
        "找到 {count} 条课程记录，最多显示 25 条。",
        "没有找到匹配的课程。请尝试仅输入专业、学历或大学名称。",
        "搜索暂时不可用。请使用下方的课程和大学链接。",
    ),
}


def catalogue_search(lang="en"):
    title, hint, label, search, clear, loading, matches, empty, error = map(escape, COPY[lang])
    return (
        f'<form data-catalogue-search data-loading="{loading}" data-matches="{matches}" '
        f'data-empty="{empty}" data-error="{error}" hidden>'
        f'<h2>{title}</h2><p>{hint}</p><label for="catalogueKeyword">{label}</label> '
        '<input id="catalogueKeyword" type="search" class="catalog-search" maxlength="120" required> '
        f'<button class="button" type="submit">{search}</button> '
        f'<button class="button secondary" type="reset">{clear}</button>'
        '<p role="status" class="catalog-count"></p><ul></ul></form>'
        '<script type="module" src="/programmes/site-assets/catalogue-search.mjs"></script>'
    )
