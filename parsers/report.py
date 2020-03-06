from typing import List


class Report:
    def __init__(self, text: str, label: str, id: int = 0, tags: List[str] = [], sub_text: str = ""):
        self.id = id
        self.text = text
        self.sub_text = sub_text
        self.tags = tags
        self.label = label
