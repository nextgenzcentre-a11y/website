"""Public admissions actions shared by catalogue pages and study guides."""
from html import escape, unescape
from urllib.parse import quote
import re

PHONE = "601167701210"
COPY = {
    "en": ("Free Consultation on WhatsApp", "Apply Now",
           "Need the exact tuition and fee breakdown for your intake? Ask us on WhatsApp.",
           "I'd like a free consultation about {topic}.",
           "I'd like to start my free application for {topic}.",
           "Please send me the exact tuition and itemised fees for my intake for {topic}."),
    "ar": ("استشارة مجانية عبر واتساب", "قدّم الآن",
           "هل تريد معرفة الرسوم الدراسية وتفاصيلها لموعد التحاقك؟ اسألنا عبر واتساب.",
           "أرغب في استشارة مجانية بخصوص {topic}.", "أرغب في بدء طلب التقديم بخصوص {topic}.",
           "أرجو إرسال تفاصيل الرسوم الدراسية لموعد التحاقي بخصوص {topic}."),
    "zh": ("通过 WhatsApp 免费咨询", "立即申请", "想了解入学批次的确切学费和费用明细？通过 WhatsApp 咨询我们。",
           "我想免费咨询：{topic}。", "我想开始申请：{topic}。", "请提供我所选入学批次的学费和费用明细：{topic}。"),
}

MORE = {"en": "Fee breakdown", "ar": "تفاصيل الرسوم", "zh": "费用明细"}

def tuition_range(raw, currency, lang="en"):
    """Show finder-listed numbers without implying a verified official price.

    Preserve per-semester / total / duration notes when the source has them.
    An unknown billing basis must never silently become an annual or total fee.
    """
    fallback = {
        "en": "Tuition not listed in finder",
        "ar": "الرسوم غير متاحة في الدليل",
        "zh": "目录暂无学费",
    }[lang]
    raw = str(raw or "").strip()
    match = re.fullmatch(
        r"(?:(USD|MYR|RM)\s*)?([\d,]+(?:\.\d+)?)\s*"
        r"(?:([-–/])\s*([\d,]+(?:\.\d+)?))?\s*"
        r"(?:\(([^)]{1,85})\))?",
        raw, re.I,
    )
    if not match:
        return fallback
    leading, first, separator, second, note = match.groups()
    amounts = [float(first.replace(",", ""))]
    if second is not None:
        amounts.append(float(second.replace(",", "")))
    if not all(0 < n < 10_000_000 for n in amounts):
        return fallback
    chosen_currency = (leading or currency or "MYR").upper()
    note = (note or "").strip()
    if note.upper() == "USD":
        chosen_currency, note = "USD", ""
    if chosen_currency == "RM":
        chosen_currency = "MYR"
    if chosen_currency not in ("MYR", "USD"):
        return fallback
    def number(n):
        return f"{n:,.0f}" if n.is_integer() else f"{n:,.2f}"
    amount_text = (number(amounts[0]) if len(amounts) == 1 else
                   number(min(amounts)) + "–" + number(max(amounts)))
    prefix = {"en":"Finder-listed", "ar":"في الدليل", "zh":"目录参考"}[lang]
    value = f"{prefix} {chosen_currency} {amount_text}"
    if note:
        lower = note.casefold()
        if lower == "per semester":
            note = {"en":"per semester", "ar":"لكل فصل", "zh":"每学期"}[lang]
        elif lower == "per year":
            note = {"en":"per year", "ar":"سنوياً", "zh":"每年"}[lang]
        elif lower == "total" or lower.startswith("total "):
            note = {"en":"total", "ar":"الإجمالي", "zh":"总费用"}[lang] + (note[5:] if lower.startswith("total ") else "")
        else:
            note = note  # Original source duration/billing note, not inferred.
        value += " (" + note + ")"
    return value


def action(kind, topic, lang="en"):
    index = ("consult", "apply", "fee").index(kind)
    label = COPY[lang][index]
    if kind == "apply":
        return (f'<a class="button secondary" data-ng-action="apply" '
                f'href="/?programme={quote(topic, safe="")}#/registerasstudent">{escape(label)}</a>')
    message = COPY[lang][index + 3].format(topic=topic)
    description = f' aria-label="{escape(MORE[lang] + " · " + label + " " + topic, quote=True)}"' if kind == "fee" else ""
    if kind == "fee":
        label = MORE[lang]
    css = (' class="button"', ' class="button secondary"', '')[index]
    return (f'<a{css}{description} data-ng-action="{kind}" href="https://wa.me/{PHONE}?text={quote(message, safe="")}"'
            f' target="_blank" rel="noopener noreferrer">{escape(label)}</a>')

def fee_link(topic, lang="en"):
    return action("fee", topic, lang)

def plain(markup):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", markup)).split())

def add_page_actions(main, lang="en"):
    heading = re.search(r"<h1\b[^>]*>(.*?)</h1>", main, re.S)
    if not heading:
        raise ValueError("Programme page needs a main heading")
    topic = plain(heading[1])
    pair = action("consult", topic, lang) + " " + action("apply", topic, lang)
    # Replace the existing hero enquiry, retaining its paragraph and any sibling links.
    top = main.find("</section>")
    hero, rest = main[:top], main[top:]
    old = r'<a class="button" href="https://wa\.me/[^"]+"[^>]*>[^<]*</a>'
    if '<section class="hero">' in hero and re.search(old, hero):
        hero = re.sub(old, lambda _: pair, hero, count=1)
    else:
        intro = re.search(r'<p class="(?:intro|lead)(?: [^"]*)?">.*?</p>', hero, re.S)
        at = intro.end() if intro else heading.end()
        hero = hero[:at] + '<p>' + pair + '</p>' + hero[at:]
    main = hero + rest
    if '</article><aside' in main:
        at = main.index('</article><aside')
    else:
        at = main.rfind('</div></section>')
        if at < 0:
            at = main.rfind('</section>')
    if at < 0:
        raise ValueError("No closing section for " + topic)
    if 'data-ng-action="fee"' not in main:
        pair = fee_link(topic, lang) + '</p><p>' + pair
    return main[:at] + '<p>' + pair + '</p>' + main[at:]

def labelled_catalogue(main, lang="en"):
    programme, fee = {
        "en": ("Programme", "Tuition range"),
        "ar": ("البرنامج الدراسي", "نطاق الرسوم"),
        "zh": ("课程名称", "学费区间"),
    }[lang]
    heading = f'<div class="catalog-list-labels"><span>{programme}</span><span>{fee}</span></div>'
    def label_list(match):
        rows = re.sub(r'(<span class="fee">|<small>)',
                      lambda m: m[0] + f'<span class="mobile-fee-label">{fee} · </span>', match[1])
        return heading + '<ul class="catalog-list">' + rows + '</ul>'
    return re.sub(r'<ul class="catalog-list">(.*?)</ul>', label_list, main, flags=re.S)
