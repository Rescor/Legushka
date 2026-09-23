import pymorphy3

import config

morph = pymorphy3.MorphAnalyzer()


def froggify(word: str) -> str:
    if not word:
        return word

    up = word[0].isupper()
    whole_up = word.isupper()
    if up:
        word = word[0].lower() + word[1:]

    for i in range(len(word)):
        if word[i] in config.VOWELS:
            prefix = "qw" if word[i] in config.ENG_LETTERS else "кв"
            word = prefix + word[i:]
            break

    if up:
        word = word[0].upper() + word[1:]
    if whole_up:
        word = word.upper()
    return word


def correct(s: str) -> str:
    # Убирает пробел перед знаком препинания
    i = 0
    while i < len(s):
        if s[i] in config.MARKS and i > 0 and s[i - 1] == " ":
            s = s[: i - 1] + s[i:]
            i -= 1
        i += 1
    return s


def substitute(phrase: list, subject_word: str) -> str:
    # Собирает фразу по шаблону: 0 - подставить subject_word в заданной
    # форме, 1 - подставить другое слово, согласованное по роду/числу с
    # subject_word, иначе - вставить токен как есть.
    res = ""
    subject = morph.parse(subject_word)[0]
    base_grammems = {subject.tag.gender, subject.tag.number}

    i = 0
    while i < len(phrase):
        token = phrase[i]
        if token == 0:
            form = subject.normalized.inflect(phrase[i + 1])
            res += (form.word if form else subject_word) + " "
            i += 2
        elif token == 1:
            grammems = set(phrase[i + 1]) | base_grammems
            parsed = morph.parse(phrase[i + 2])[0]
            form = parsed.inflect(grammems)
            res += (form.word if form else phrase[i + 2]) + " "
            i += 3
        else:
            res += str(token) + " "
            i += 1
    return res
