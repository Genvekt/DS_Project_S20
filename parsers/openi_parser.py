from typing import List

import pandas as pd
from parsers.general_parser import Parser
from parsers.report import Report
from utils.config import OPENI_DIR


class OpenI:
    def __init__(self):
        self.dataset = []
        self.labels = []
        self.path = OPENI_DIR

    def parse_data(self):

        if not self.path.exists():
            return None

        parser = Parser()
        columns = ['FINDINGS', 'IMPRESSION', 'MeSH', 'LABEL']
        dfs = []

        # Get the list of all files
        files = self.path.glob('**/*')

        for file in files:
            # Process only files
            if not file.is_file():
                continue

            report = parser.parse_xml_report(file)

            # Parse Abstract section
            abstract = parser.get_tags(report=report,
                                       tag='abstracttext',
                                       labels=['FINDINGS', 'IMPRESSION'])

            findings = abstract['FINDINGS'][0].text if 'FINDINGS' in abstract.keys() else ''
            impression = abstract['IMPRESSION'][0].text if 'IMPRESSION' in abstract.keys() else ''

            # Parse mesh
            mesh = parser.get_tag_children(report=report, tag='mesh')
            tags = []
            for _, value in mesh.items():
                for v in value:
                    if not v in self.labels:
                        self.labels.append(v)
                tags.extend(value)

            # Define mesh label
            if 'major' in mesh and 'normal' in mesh['major']:
                mesh_label = 0
            else:
                mesh_label = 1

            self.dataset.append(Report(text=impression, sub_text=findings, label=str(mesh_label), tags=tags))

