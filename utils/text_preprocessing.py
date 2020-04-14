import re
import nltk
from typing import List
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

from index.prefix_tree import PrefixTree

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

codes = {
    '1': 'полость',
    '2': 'округлая тень',
    '3': 'затемнение в легочной ткани',
    '4': 'очаговые тени в легочной (более трех)',
    '5': 'единичные очаговые тени в легочной ткани',
    '6': 'ячеистость в легочной ткани',
    '7': 'затемнение, увеличение корней (кроме фиброза)',
    '8': 'фиброторакс',
    '9': 'фиброз ограниченный (1-2 поля)',
    '10': 'фиброз более двух легочных полей',
    '11': 'фиброз одного легочного поля',
    '12': 'фиброз корней выраженный',
    '13': 'диффузный пневмосклероз',
    '14': 'единичные фиброзные тяжи в легочной ткани',
    '15': 'единичные тяжи в корнях',
    '16': 'изменения в плевре (сросшееся плевра, наслоение, обызиствление)',
    '17': 'междолевая "волосяная" плевра',
    '18': 'деформации диафрагмы не связанные с плевральной патологией',
    '19': 'состояние после операции',
    '20': 'добавочная доля',
    '21': 'изменение скелета грудной клетки (костные мозоли, синостозы, добавочные ребра, остеофиты и т.д.)',
    '22': 'инородное тело, проецирующая на легочную ткань',
    '23': 'обызиствление в легочной ткани (инодородное тело)',
    '24': 'технический брак',
    '25': 'прочее',
    '26': 'обызиствление первичного комплекса',
    '27': 'петрификаты крупные в легочной ткани',
    '28': 'крупные петрификаты в корнях (диаметром не менее поперечного сечения ребра)',
    '29': 'мелкие петрификаты в легочной ткани',
    '30': ' множественные петрификаты (3 и более)',
    '31': 'единичные петрификаты (1-2)',
    '32': 'сомнительные петрификаты',
    '33': 'множественные петрификаты в корнях (3 и более)',
    '34': 'единичные петрификаты в корнях',
    '35': 'сомнительные петрификаты в корнях',
    '36': 'сердечно-сосудистая патология',
    '99': 'норма'

}


def normalize(text):
    # Replace all symbols that are not letters and not * with space.
    t1 = re.sub(r"(?u)[^\w+0-9]", ' ', text.lower())
    # Replace many spaces with one
    t2 = re.sub(r"[\s]+", ' ', t1)
    return t2


def tokenize(text):
    return nltk.word_tokenize(text)


def lemmatization(tokens):
    lemmatizer = WordNetLemmatizer()
    res = [lemmatizer.lemmatize(t) for t in tokens]
    return res


def remove_stop_words(tokens, lang):
    stop_words = set(stopwords.words(lang))
    filtered_sentence = [t for t in tokens if not t in stop_words]
    return filtered_sentence


def preprocess(text, lemmatize=True, without_stop_words=True, lang='english'):
    text = normalize(text)
    clear_text = tokenize(text)
    if lemmatize:
        clear_text = lemmatization(clear_text)
    if without_stop_words:
        clear_text = remove_stop_words(clear_text, lang)
    return clear_text


def categorize(tokens: List[str]):
    return nltk.pos_tag(tokens)


def create_prefix_tree(data):
    pt = PrefixTree()
    for word in data:
        pt.add(word + "$")
    return pt


def symbol_to_end(string, symbol, cut_symbol=False):
    '''
    aaaSaaa -> aaaaaaS where S is special symbol
    '''
    index = string.find(symbol)
    return string[index + 1:] + string[:index]


def resolve_norm(prefix, norm):
    return prefix + " " + norm


def resolve_reduction(before, word, after, mistakes, prefix_tree):
    # Check in mistakes
    # print(before+word+after)
    if before + word + after in mistakes:
        change = mistakes[before + word + after]
    else:
        query = after + '$' + before
        change = ''
        res = prefix_tree.find_all(query)
        if len(res) > 0:
            for i in range(len(res)):
                res[i] = symbol_to_end(res[i], '$', True)
                # print(before+word+after,"->",res)
            change = res[0]
        else:
            query = before + word + after
            res = prefix_tree.find_all(query)
            if len(res) > 0:
                for i in range(len(res)):
                    res[i] = symbol_to_end(res[i], '$', True)
                    # print(query,"->",res)
                change = res[0]
            else:
                change = before + word + after
    # print(before+word+after,"->",change)
    return change


def check_word(before, word, after, voc, stop_words, mistakes, prefix_tree):
    # print(word)
    if not word in voc and not word in stop_words:
        change = resolve_reduction("", "", word, mistakes, prefix_tree)
    else:
        change = word
        # print(word,"->",change)
    # print("Change: ",change)
    return before + change + after


def fix_double_numeration(numbers, after, mistakes, prefix_tree):
    first = resolve_reduction("", "", numbers[0] + "-м", mistakes, prefix_tree)
    second = resolve_reduction("", "", numbers[1] + "-м", mistakes, prefix_tree)
    return first + " и " + second + after


def fix_numeration(number, after, mistakes, prefix_tree):
    change = resolve_reduction("", "", number + "-м", mistakes, prefix_tree)
    return change + after


def fix_codes_loc(code, location, mistakes, prefix_tree):
    if int(code) > 0 and int(code) < 37 and code in codes:
        change = codes[code]
        loc = resolve_reduction("", "", location + "-м", mistakes, prefix_tree)
        return change + " в " + loc + " отделе"
    else:
        return code


def fix_code(code):
    if int(code) > 10 and int(code) < 37 and code in codes:
        return codes[code]
    else:
        return code


def fix_double_c(one, two):
    return "c" + one + " и " + "c" + two


def fix_c(one):
    return "c" + one


def cals_c_s(one, two):
    return one + two


def clean_text(rus_data):
    voc = []
    with open('resources/vocabulary.txt') as f:
        for line in f.readlines():
            voc.append(line[:len(line) - 1])
    stop_words = set(stopwords.words('russian'))
    mistakes = {}
    with open('resources/undecided.txt', 'r') as f:
        for line in f.readlines():
            words = line.split('&')
            w1 = words[0]
            change = ''
            for i in range(1, len(words)):
                change += words[i]
            mistakes[w1[:len(w1) - 1]] = change[1:len(change) - 1]
    prefix_tree = create_prefix_tree(voc)

    pattern_norm = re.compile(r'(?u)(\w+)(норма)')
    pattern_complex = re.compile(r'(?u)(\w+)(/|\\)(\w+)(-)(\w+)')
    pattern_dash = re.compile(r'(?u)(\w+)(-)(\w+)')
    pattern_slash = re.compile(r'(?u)(\w+)(/|\\)(\w+)')
    pattern_words = re.compile(r'(?u)(\w+)')
    pattert_double_num = re.compile(r'(?u)(\d)-(\d)(\s+межреберье|\s+межреберьях)')
    pattern_numeration = re.compile(r'(?u)(\d)(\s+межреберье|\s+межреберьях)')
    pattern_double_c = re.compile(r'(?u)(с )(\d+),(\d+)')
    pattern_c = re.compile(r'(?u)(с )(\d+)')
    pattern_c_num = re.compile(r'(?u)(с|s)(\d+)')
    pattern_code_loc = re.compile(r'(?u)(\d+)(\\|/)(\d+)')
    pattern_code = re.compile(r'(\d+)')
    for report in rus_data.dataset:
        text = report.text.lower()
        if text == 'норма':
            continue
        text = pattern_norm.sub((lambda s: resolve_norm(s.group(1), s.group(2))), text)
        # print(text)
        text = pattern_complex.sub(
            (lambda s: check_word("", s.group(1) + s.group(2) + s.group(3) + s.group(4) + s.group(5), "", voc,
                                  stop_words, mistakes, prefix_tree)), text)
        text = pattern_dash.sub(
            (lambda s: resolve_reduction(s.group(1), s.group(2), s.group(3), mistakes, prefix_tree)), text)
        # print(text)
        text = pattern_slash.sub(
            (lambda s: resolve_reduction(s.group(1), s.group(2), s.group(3), mistakes, prefix_tree)), text)
        # print(text)
        text = pattern_words.sub((lambda s: check_word("", s.group(1), "", voc, stop_words, mistakes, prefix_tree)),
                                 text)
        text = pattert_double_num.sub(
            (lambda s: fix_double_numeration([s.group(1), s.group(2)], s.group(3), mistakes, prefix_tree)), text)
        text = pattern_numeration.sub((lambda s: fix_numeration(s.group(1), s.group(2), mistakes, prefix_tree)), text)
        text = pattern_double_c.sub((lambda s: fix_double_c(s.group(2), s.group(3))), text)
        text = pattern_c.sub((lambda s: fix_c(s.group(2))), text)
        text = pattern_code_loc.sub((lambda s: fix_codes_loc(s.group(1), s.group(3), mistakes, prefix_tree)), text)
        text = pattern_code.sub((lambda s: fix_code(s.group(1))), text)
        text = pattern_c_num.sub((lambda s: cals_c_s(s.group(1), s.group(2))), text)

        report.text = text

    return rus_data
