"""Portable subset of the desktop dialogue rules. No casing or wording corrections."""
import re

DASH = r"[-—–－]"
TRANSLATION = str.maketrans({"，": ",", "、": ",", "。": ".", "？": "?", "！": "!",
    "：": ":", "；": ";", "“": '"', "”": '"', "「": '"', "」": '"',
    "‘": "'", "’": "'", "«": '"', "»": '"', "（": "(", "）": ")",
    "【": "[", "】": "]", "《": '"', "》": '"', "¿": None, "¡": None})
SMALL = {
    "en": "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),
    "pt-BR": "zero um dois três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis dezessete dezoito dezenove".split(),
    "es-MX": "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciséis diecisiete dieciocho diecinueve veinte veintiuno veintidós veintitrés veinticuatro veinticinco veintiséis veintisiete veintiocho veintinueve".split(),
}
TENS = {
    "en": ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'],
    "pt-BR": ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa'],
    "es-MX": ['', '', '', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa'],
}
HUNDREDS = {
    "pt-BR": ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos'],
    "es-MX": ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'],
}


def number_to_words(n, language):
    if not 0 <= n < 1_000_000:
        raise ValueError('数字超出规则范围')
    if n < len(SMALL[language]):
        return SMALL[language][n]
    joiner = {'en': ' ', 'pt-BR': ' e ', 'es-MX': ' y '}[language]
    if n < 100:
        return TENS[language][n // 10] + (joiner + SMALL[language][n % 10] if n % 10 else '')
    if n < 1000:
        if language == 'en':
            prefix = SMALL[language][n // 100] + ' hundred'
            return prefix + (' and ' + number_to_words(n % 100, language) if n % 100 else '')
        if n == 100:
            return 'cem' if language == 'pt-BR' else 'cien'
        prefix = HUNDREDS[language][n // 100]
        return prefix + ((' e ' if language == 'pt-BR' else ' ') + number_to_words(n % 100, language) if n % 100 else '')
    thousands, rest = divmod(n, 1000)
    prefix = (number_to_words(thousands, language) + ' thousand' if language == 'en' else
              'mil' if thousands == 1 else number_to_words(thousands, language) + ' mil')
    separator = ' e ' if language == 'pt-BR' and rest < 100 else ' '
    return prefix + (separator + number_to_words(rest, language) if rest else '')


def plural_card(n, language):
    special = {
        'en': {1: 'aces', 2: 'twos', 3: 'threes', 5: 'fives', 6: 'sixes', 8: 'eights', 9: 'nines'},
        'pt-BR': {1: 'ases', 2: 'dois', 3: 'três', 6: 'seises', 7: 'setes', 10: 'dezes'},
        'es-MX': {1: 'ases', 3: 'treses', 6: 'seises', 7: 'sietes', 10: 'dieces'},
    }
    return special[language].get(n, number_to_words(n, language) + 's')


def numeric_review_reason(text, language, context=''):
    if not re.search(r'\d', text):
        return ''
    if language not in SMALL:
        return '需确认实际语言；暂不转换数字。'
    combined = text + ' ' + context
    if re.search(r'\d\s*[.,:/%‰' + '\uFF05' + r']\s*\d|\d\s*[%‰％]|\d\s*' + DASH + r'\s*\d|(?:^|[\s(])' + DASH + r'\s*\d', text):
        return '小数、千分位、日期、时间、比例、区间或负数需人工确认。'
    if re.search(r'\b0\d+\b|\b\d{7,}\b|\b(?:phone|telephone|mobile|tel|id|code|serial|year|date|number|número|telefone|日期|电话|编号|年份)\b', combined, re.I):
        return '前导零、大整数、年份、电话号码或编号需人工确认。'
    # A card-number suffix is the only supported digit-letter combination.
    without_cards = re.sub(r'\b(par\s+de|pair\s+of)\s+\d{1,2}s?\b', '', text, flags=re.I)
    if re.search(r'[^\W\d_]\d|\d[^\W\d_]', without_cards):
        return '字母数字混合表达需人工确认。'
    amount = bool(re.search(r'r\$|\$|€|reais|real|pesos?|dollars?|dólares?', combined, re.I))
    dice = bool(re.search(r'骰子|点数|dados?|dice|\bdie\b|roll|tirada', combined, re.I))
    if not amount and not dice and re.search(r'\b(?:661|666)\b', text):
        return '需确认这是普通数量还是骰子点数。'
    return ''


def convert_numbers(text, language, context=''):
    reason = numeric_review_reason(text, language, context)
    if reason:
        return text, reason
    if not re.search(r'\d', text):
        return text, ''
    combined = text + ' ' + context
    amount = bool(re.search(r'r\$|\$|€|reais|real|pesos?|dollars?|dólares?', combined, re.I))
    dice = not amount and bool(re.search(r'骰子|点数|dados?|dice|\bdie\b|roll|tirada', combined, re.I))
    output = re.sub(r'\b(par\s+de|pair\s+of)\s+(\d{1,2})s?\b',
                    lambda m: m[1] + ' ' + plural_card(int(m[2]), language), text, flags=re.I)
    output = re.sub(r'\b\d+\b', lambda m: ', '.join(number_to_words(int(d), language) for d in m[0])
                    if dice else number_to_words(int(m[0]), language), output)
    return output, ''


def clean_punctuation(text):
    """No number verbalization. Preserve numeric dashes requiring semantic review."""
    output = text.strip()
    match = re.fullmatch(r'[「“"](.*?)[」”"]\s*([.!?]?)', output)
    if match:
        inner, trailing = match[1].strip(), match[2]
        output = inner + (trailing if trailing and not re.search(r'[.!?]$', inner) else '')
    output = output.translate(TRANSLATION)
    output = re.sub(r'…+', '...', output)
    output = re.sub(r',\s*\.{3}', ',', output)
    output = re.sub(r'\.{3}\s*([?!])', r'\1', output)
    output = re.sub(r'[?!]{2,}', lambda m: '?' if '?' in m[0] else '!', output)
    output = re.sub(r'\.{3}\s*[-—–]|[-—–]\s*\.{3}', '', output)
    output = re.sub(r'\s*[-—–]\s*$', '', output)
    output = re.sub(r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.(?=[A-Z])', lambda m: m[0] + ' ', output)
    # Protect numeric dash spans, including dates/ranges and signed numbers.
    protected = {}
    def protect(m):
        key = '\x00' + str(len(protected)) + '\x00'
        protected[key] = m[0]
        return key
    output = re.sub(r'\d(?:\s*' + DASH + r'\s*\d)+|(?:^|(?<=[\s(]))' + DASH + r'\s*\d+', protect, output)
    output = re.sub(r'\s*' + DASH + r'+\s*', ' ', output)
    output = re.sub(r'\s{2,}', ' ', output).strip()
    for key, value in protected.items():
        output = output.replace(key, value)
    return output
