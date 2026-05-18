export const SEDARIM = [
    {
        en: 'Zeraim', he: 'זרעים',
        tractates: [{ en: 'Berakhot', he: 'ברכות' }],
    },
    {
        en: 'Moed', he: 'מועד',
        tractates: [
            { en: 'Shabbat', he: 'שבת' },
            { en: 'Eruvin', he: 'עירובין' },
            { en: 'Pesachim', he: 'פסחים' },
            { en: 'Shekalim', he: 'שקלים' },
            { en: 'Yoma', he: 'יומא' },
            { en: 'Sukkah', he: 'סוכה' },
            { en: 'Beitzah', he: 'ביצה' },
            { en: 'Rosh Hashanah', he: 'ראש השנה' },
            { en: 'Taanit', he: 'תענית' },
            { en: 'Megillah', he: 'מגילה' },
            { en: 'Moed Katan', he: 'מועד קטן' },
            { en: 'Chagigah', he: 'חגיגה' },
        ],
    },
    {
        en: 'Nashim', he: 'נשים',
        tractates: [
            { en: 'Yevamot', he: 'יבמות' },
            { en: 'Ketubot', he: 'כתובות' },
            { en: 'Nedarim', he: 'נדרים' },
            { en: 'Nazir', he: 'נזיר' },
            { en: 'Sotah', he: 'סוטה' },
            { en: 'Gittin', he: 'גיטין' },
            { en: 'Kiddushin', he: 'קידושין' },
        ],
    },
    {
        en: 'Nezikin', he: 'נזיקין',
        tractates: [
            { en: 'Bava Kamma', he: 'בבא קמא' },
            { en: 'Bava Metzia', he: 'בבא מציעא' },
            { en: 'Bava Batra', he: 'בבא בתרא' },
            { en: 'Sanhedrin', he: 'סנהדרין' },
            { en: 'Makkot', he: 'מכות' },
            { en: 'Shevuot', he: 'שבועות' },
            { en: 'Avodah Zarah', he: 'עבודה זרה' },
            { en: 'Horayot', he: 'הוראות' },
        ],
    },
    {
        en: 'Kodashim', he: 'קדשים',
        tractates: [
            { en: 'Zevachim', he: 'זבחים' },
            { en: 'Menachot', he: 'מנחות' },
            { en: 'Chullin', he: 'חולין' },
            { en: 'Bekhorot', he: 'בכורות' },
            { en: 'Arakhin', he: 'ערכין' },
            { en: 'Temurah', he: 'תמורה' },
            { en: 'Keritot', he: 'כריתות' },
            { en: 'Meilah', he: 'מעילה' },
            { en: 'Tamid', he: 'תמיד' },
        ],
    },
    {
        en: 'Tahorot', he: 'טהרות',
        tractates: [{ en: 'Niddah', he: 'נדה' }],
    },
];

export function findTractate(nameEn) {
    for (const seder of SEDARIM) {
        for (const t of seder.tractates) {
            if (t.en === nameEn) return { ...t, seder: seder.he, sederEn: seder.en };
        }
    }
    return { en: nameEn, he: nameEn, seder: '', sederEn: '' };
}

function toHebrewNum(n) {
    if (n === 15) return 'טו';
    if (n === 16) return 'טז';
    const hundreds = ['', 'ק', 'ר', 'ש', 'ת', 'תק', 'תר', 'תש', 'תת', 'תתק'];
    const tens     = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ'];
    const ones     = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט'];
    return (hundreds[Math.floor(n / 100)] || '') +
           (tens[Math.floor((n % 100) / 10)] || '') +
           (ones[n % 10] || '');
}

// Converts "Berakhot 2a" → "ברכות ב." and "Shabbat 24b" → "שבת כד:"
export function toHebrewRef(ref) {
    const m = /^(.+?)\s+(\d+)([ab])$/.exec(decodeURIComponent(ref || ''));
    if (!m) return decodeURIComponent(ref || '');
    return `${findTractate(m[1]).he} ${toHebrewNum(parseInt(m[2]))}${m[3] === 'a' ? '.' : ':'}`;
}
