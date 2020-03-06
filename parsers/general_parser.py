from bs4 import BeautifulSoup, NavigableString, Tag
from pathlib import Path
from typing import List


class Parser:
    def parse_xml_report(self, path: Path) -> BeautifulSoup:
        """
        Convert xml file to BeautifulSoup instance
        :return: BeautifulSoup instance containing file data
        """

        # Check if report path exists
        if not path.exists():
            return None

        with open(path, 'r') as report_file:
            raw_report = report_file.read()
            parsed_report = BeautifulSoup(raw_report, "lxml")

        return parsed_report

    def get_tag_children(self, report: BeautifulSoup, tag: str) -> dict:
        """
        Return all children tags of some tag
        :param report: Parsed document
        :param tag: Parent tag
        :return: Dict with keys as child tags names and values as the text they contain
        """
        result = {}
        tag_content = report.find(tag)
        for element in tag_content.children:
            if isinstance(element, NavigableString):
                continue
            if isinstance(element, Tag):
                if not element.name in result:
                    result[element.name] = []
                result[element.name].append(element.text)
        return result

    def get_tags(self, report: BeautifulSoup, tag: str, labels: List[str] = None) -> dict:
        """
        Searches for specified tag
        :param report: Parsed document
        :param tag: Tag name to search
        :param labels: Filter by labels, optional
        :return: Dict filtered tags by specified label value as key, in "no-label" otherwise
        """
        result = {"no-label": []}
        for element in report.find_all(tag):
            if labels:
                label = element.get('label')
                if label in labels:
                    if not label in result:
                        result[label] = []
                    result[label].append(element)
            else:
                result["no-label"].append(element)
        return result
