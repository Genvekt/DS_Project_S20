from typing import List
from collections import Counter
from utils.text_preprocessing import preprocess, categorize

from parsers.report import Report


class DatasetStat:
    def __init__(self):
        self.size = 0
        self.words_frequency = Counter()
        self.words_frequency_by_label = {}
        self.tag_frequency = Counter()
        self.mean_doc_length = 0
        self.mean_doc_length_by_label = {}
        self.size_by_label = {}
        self.doc_frequency = Counter()
        self.doc_frequency_by_label = {}

    def calculate_statistics(self, dataset: List[Report], lang: str = 'english'):
        # Calculate the words frequencies
        self.size = len(dataset)
        self.words_frequency = self.get_words_frequency(dataset, lang=lang)
        self.words_frequency_by_label = self.get_words_frequency_by_label(dataset, lang=lang)
        self.mean_doc_length = self.get_mean_doc_length(dataset, lang=lang)
        self.tag_frequency = self.get_tag_frequency(dataset, lang=lang)
        self.mean_doc_length_by_label = self.get_mean_doc_length_by_label(dataset, lang=lang)
        self.doc_frequency = self.get_doc_frequency(dataset, lang=lang)
        self.doc_frequency_by_label = self.get_doc_frequency_by_label(dataset, lang=lang)

    def get_words_frequency(self, dataset: List[Report], lang: str = 'english'):
        main_counter = Counter()
        for report in dataset:
            c = Counter(preprocess(report.text, lang=lang))
            main_counter += c
        return main_counter

    def get_mean_doc_length(self, dataset: List[Report], lang: str = 'english'):
        result = 0
        for report in dataset:
            result += len(preprocess(report.text, lang=lang))

        return result / len(dataset)

    def get_tag_frequency(self, dataset: List[Report], lang: str = 'english'):
        main_counter = Counter()
        for report in dataset:
            tockens = preprocess(report.text, lang=lang)
            tags = categorize(tockens)
            c = Counter(map((lambda t: t[1]), tags))
            main_counter += c
        return main_counter

    def get_mean_doc_length_by_label(self, dataset: List[Report], lang: str = 'english'):
        result = {}
        sizes = {}
        for report in dataset:
            if not report.label in result.keys():
                result[report.label] = 0
                sizes[report.label] = 0
            result[report.label] += len(preprocess(report.text, lang=lang))
            sizes[report.label] += 1
        for key in result.keys():
            result[key] = result[key] / sizes[key]
            self.size_by_label[key] = sizes[key]
        return result

    def get_words_frequency_by_label(self, dataset: List[Report], lang: str = 'english'):
        result = {}
        for report in dataset:
            if not report.label in result.keys():
                result[report.label] = Counter()
            c = Counter(preprocess(report.text, lang=lang))
            result[report.label] += c
        return result

    def get_doc_frequency(self, dataset: List[Report], lang: str = 'english'):
        main_counter = Counter()
        for report in dataset:
            c = Counter(preprocess(report.text, lang=lang))
            main_counter += Counter(list(c.keys()))
        return main_counter

    def get_doc_frequency_by_label(self, dataset: List[Report], lang: str = 'english'):
        result = {}
        for report in dataset:
            if not report.label in result.keys():
                result[report.label] = Counter()
            c = Counter(preprocess(report.text, lang=lang))
            result[report.label] += Counter(list(c.keys()))
        return result
