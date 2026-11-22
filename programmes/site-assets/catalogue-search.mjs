const aliases = [
  [/\basasi sains pertanian\b/gu, 'foundation agricultural science'],
  [/العلوم الزراعية|农业科学|sciences agricoles|sains pertanian/gu, 'agricultural science'],
  [/علوم الحياة|生命科学|sciences de la vie|sains hayat/gu, 'life sciences'],
  [/بكالوريوس المحاسبة|会计学士|ijazah sarjana muda perakaunan/gu, 'bachelor accounting'],
  [/\bhonours?\b|\bhons\b|\bkepujian\b|مع مرتبة الشرف|荣誉/gu, 'honours'],
  [/علوم الحاسوب|علوم الكمبيوتر|计算机科学|informatique|sains komputer|\bcomp sci\b/gu, 'computer science'],
  [/هندسة البرمجيات|软件工程|genie logiciel|kejuruteraan perisian|\bsoft(?:ware)? eng\b/gu, 'software engineering'],
  [/الهندسة الميكانيكية|机械工程|genie mecanique|kejuruteraan mekanikal|\bmech eng\b/gu, 'mechanical engineering'],
  [/تقنية المعلومات|تكنولوجيا المعلومات|信息技术|teknologi maklumat|\bit\b/gu, 'information technology'],
  [/المسار الهندسي|الهندسة|工程方向|工程|\bgenie\b|kejuruteraan/gu, 'engineering'],
  [/علم البيانات|数据科学|science des donnees|sains data/gu, 'data science'],
  [/الذكاء الاصطناعي|人工智能|intelligence artificielle|kecerdasan buatan|\bai\b/gu, 'artificial intelligence'],
  [/ادارة الاعمال|工商管理|administration des affaires|pentadbiran perniagaan/gu, 'business administration'],
  [/\bmba\b/gu, 'master business administration'],
  [/المحاسبة|会计|comptabilite|perakaunan/gu, 'accounting'],
  [/التمريض|护理|sciences infirmieres|kejururawatan/gu, 'nursing'],
  [/الصيدلة|药学|pharmacie|farmasi/gu, 'pharmacy'],
  [/بكالوريوس|本科|学士|\blicence\b|ijazah sarjana muda|\bbsc\b/gu, 'bachelor'],
  [/ماجستير|硕士|\bmasters\b|\bsarjana\b|\bmsc\b/gu, 'master'],
  [/دكتوراه|博士|\bdoctorat\b|\bph d\b/gu, 'phd'],
  [/دبلوم|文凭|\bdiplome\b/gu, 'diploma'],
  [/السنة التاسيسية|البرنامج التاسيسي|预科|\basasi\b|\bprepa\b|programme preparatoire/gu, 'foundation'],
  [/في ماليزيا|ماليزيا|马来西亚|\bmalaisie\b/gu, 'malaysia'],
];
const context = new Set('a an in of the at for degree degrees course courses programme programmes program programs malaysia university universities study studying international students en de du des etudes formation formations universite universites di kursus program universiti في تخصص دراسة جامعة الجامعات 留学 课程'.split(' '));

function normalize(value) {
  return value.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase()
    .replace(/[ʻ’']/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
}

function tokens(value) {
  for (const [pattern, replacement] of aliases) value = value.replace(pattern, ' ' + replacement + ' ');
  return value.trim().split(/\s+/).filter(Boolean);
}

function oneEdit(a, b) {
  if (Math.abs(a.length - b.length) > 1) return false;
  if (a.length > b.length) return oneEdit(b, a);
  let i = 0;
  while (i < a.length && a[i] === b[i]) i++;
  if (i === a.length) return b.length - a.length <= 1;
  if (a.length < b.length) return a.slice(i) === b.slice(i + 1);
  return a.slice(i + 1) === b.slice(i + 1) ||
    (a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2));
}

export function catalogueEntries(index, details = {}) {
  return Object.entries(index).flatMap(([university, courses]) =>
    Object.entries(courses).map(([name, url]) => {
      const institution = details.universities?.[university] ?? university;
      const officialAward = details.awards?.[university]?.[name] ?? '';
      const title = tokens(normalize(name));
      return {
        name, university, url, title,
        words: tokens(normalize([name, officialAward, university, institution].join(' '))),
      };
    }));
}

export function findProgrammes(entries, query) {
  const terms = [...new Set(tokens(normalize(query)).filter(term => !context.has(term)))];
  if (!terms.length) return [];
  const matches = (term, word) => word === term || (term.length >= 3 && word.startsWith(term));
  const exact = entries.filter(entry => terms.every(term => entry.words.some(word => matches(term, word))));
  if (exact.length) {
    const phrase = terms.join(' ');
    return exact.sort((a, b) =>
      Number(b.title.join(' ').includes(phrase)) - Number(a.title.join(' ').includes(phrase)));
  }
  return entries.filter(entry => {
    const unmatched = terms.filter(term => !entry.words.some(word => matches(term, word)));
    if (!unmatched.length || unmatched.length > 2) return false;
    const minLength = unmatched.length === 2 ? 6 : 4;
    return unmatched.every(term => term.length >= minLength &&
      entry.words.some(word => word.length >= minLength - 1 && oneEdit(term, word)));
  });
}

function attach(form) {
  const input = form.querySelector('input');
  const status = form.querySelector('[role="status"]');
  const results = form.querySelector('ul');
  let request;
  let latest = 0;
  async function search() {
    const run = ++latest;
    const query = input.value.trim();
    results.replaceChildren();
    if (!query) {
      status.textContent = '';
      return;
    }
    status.textContent = form.dataset.loading;
    try {
      request ??= Promise.all([
        fetch('/programmes/finder-links.json').then(response => {
          if (!response.ok) throw new Error('Catalogue unavailable');
          return response.json();
        }),
        fetch('/programmes/catalogue-search-details.json').then(response =>
          response.ok ? response.json() : {}).catch(() => ({})),
      ]).then(([index, details]) => catalogueEntries(index, details)).catch(error => {
        request = undefined;
        throw error;
      });
      const entries = await request;
      if (run !== latest) return;
      const matches = findProgrammes(entries, query);
      status.textContent = matches.length ? form.dataset.matches.replace('{count}', matches.length) : form.dataset.empty;
      results.replaceChildren(...matches.slice(0, 25).map(({name, university, url}) => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = url;
        link.textContent = name + ' · ' + university;
        item.append(link);
        return item;
      }));
    } catch {
      if (run === latest) status.textContent = form.dataset.error;
    }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    search();
  });
  form.addEventListener('reset', () => {
    latest++;
    status.textContent = '';
    results.replaceChildren();
  });
  form.hidden = false;
}

if (typeof document !== 'undefined') document.querySelectorAll('[data-catalogue-search]').forEach(attach);
