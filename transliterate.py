"""
O'zbek tilidagi lotin harflarini kirillga o'giradigan modul.

Qoidaga asoslangan (tashqi kutubxonasiz), shu sabab Railway'da qo'shimcha
pip paketi kerak emas va ishonchli ishlaydi. Quyidagilarga tegmaydi:
- URL'lar (https://..., t.me/..., www...)
- @mention'lar va #hashtag'lar
- Telefon raqamlari va boshqa raqamlar
- HTML teglari (<b>, <a href="...">, ...) va HTML entity'lar (&amp; va h.k.)
- Allaqachon kirill yozuvidagi matn (chunki faqat lotin harflari — A-Z/a-z —
  ushlanadi)
"""

import re

# O'zbek tilida o' / g' uchun ishlatiladigan turli apostrof belgilari
# (odamlar turli klaviaturada turlicha yozadi)
_APOSTROPHES = "ʻʼ'`´ʹ"

_LATIN_TO_CYR_SINGLE = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ",
    "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о",
    "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
    "x": "х", "y": "й", "z": "з",
}

# Ikki harfli birikmalar (uzunroq mos kelishi birinchi tekshiriladi)
_DIGRAPHS = [
    ("yo", "ё"), ("yu", "ю"), ("ya", "я"),
    ("sh", "ш"), ("ch", "ч"), ("ts", "ц"),
]

# Texnik elementlar — bularga tegmaymiz
_SKIP_PATTERN = re.compile(
    r"(https?://\S+|t\.me/\S+|www\.\S+|"
    r"@[A-Za-z0-9_]+|#[\w']+|"
    r"&[a-zA-Z]+;|&#\d+;|"
    r"\+?\d[\d\-\s()]{3,}\d)"
)

# Lotin so'z (harflar va ular orasidagi apostrof, masalan "bo'ylab")
_WORD_PATTERN = re.compile(r"[A-Za-z]+(?:[" + re.escape(_APOSTROPHES) + r"][A-Za-z]+)*")

_TAG_SPLIT = re.compile(r"(<[^>]+>)")


def _cased(source_char: str, cyrillic: str) -> str:
    return cyrillic.upper() if source_char.isupper() else cyrillic


def _translit_word(word: str) -> str:
    out = []
    i = 0
    n = len(word)
    while i < n:
        c = word[i]

        # o' / g'  ->  ў / ғ
        if c.lower() in ("o", "g") and i + 1 < n and word[i + 1] in _APOSTROPHES:
            cyr = "ў" if c.lower() == "o" else "ғ"
            out.append(_cased(c, cyr))
            i += 2
            continue

        # sh, ch, ts, yo, yu, ya
        two = word[i:i + 2].lower()
        matched = False
        for lat, cyr in _DIGRAPHS:
            if two == lat:
                out.append(_cased(c, cyr))
                i += 2
                matched = True
                break
        if matched:
            continue

        # so'z boshidagi "e" -> "э" (masalan "elon" -> "элон")
        if c.lower() == "e" and i == 0:
            out.append(_cased(c, "э"))
            i += 1
            continue

        if c.lower() in _LATIN_TO_CYR_SINGLE:
            out.append(_cased(c, _LATIN_TO_CYR_SINGLE[c.lower()]))
            i += 1
            continue

        # o'/g' bilan band bo'lmagan, ammo so'z ichida qolgan apostrof
        # (masalan "ta'sir", "san'at") -> tutuq belgisi
        if c in _APOSTROPHES:
            out.append("ъ")
            i += 1
            continue

        out.append(c)
        i += 1

    return "".join(out)


def _translit_plain_text(text: str) -> str:
    """Oddiy (HTML teglarisiz) matndagi lotin so'zlarni kirillga o'giradi."""
    if not text:
        return text

    def repl(match: "re.Match[str]") -> str:
        return _translit_word(match.group(0))

    parts = []
    last = 0
    for m in _SKIP_PATTERN.finditer(text):
        before = text[last:m.start()]
        parts.append(_WORD_PATTERN.sub(repl, before))
        parts.append(m.group(0))  # texnik element — o'zgarishsiz
        last = m.end()
    parts.append(_WORD_PATTERN.sub(repl, text[last:]))
    return "".join(parts)


def translit_html(html: str) -> str:
    """
    HTML formatlangan matndagi (masalan aiogram'ning html_text natijasi)
    lotin so'zlarni kirillga o'giradi, teglar va ularning atributlariga
    (masalan href="...") tegmaydi.
    """
    if not html:
        return html
    parts = _TAG_SPLIT.split(html)
    for i, part in enumerate(parts):
        if part.startswith("<") and part.endswith(">"):
            continue  # HTML tegi — o'zgarishsiz qoladi
        parts[i] = _translit_plain_text(part)
    return "".join(parts)
