import pandas as pd
from parsers.general_parser import Parser
from parsers.report import Report
from utils.config import RUSSIAN_DIR


class Russian:
    def __init__(self):
        self.dataset = []
        self.path = RUSSIAN_DIR

    def parse_data(self):

        if not self.path.exists():
            return None

        parser = Parser()
        columns = ['IDBMP', 'DIAGNOSISEND1', 'NORMAL']


        # Get the list of all files
        files = self.path.glob('**/*')

        for file in files:
            # Process only files
            if not file.is_file():
                continue

            report = parser.parse_xml_report(file)

            main_tag = parser.get_tags(report=report, tag='ns0:studymain')['no-label'][0]

            report_id = main_tag.get('idbmp')
            normal = main_tag.get('normal')
            diagnosis = main_tag.get('diagnosisend1')
            if not diagnosis:
                print("No diagnosis in ", report_id)
                continue
            if not normal:
                print("No label in ", report_id)
                continue
            self.dataset.append(Report(text=diagnosis, label=normal, id=report_id))

