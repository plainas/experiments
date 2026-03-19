import json
from pathlib import Path


class DuplicateProcurementChecker:
    def __init__(self, data_path="parsed_json_data.json"):
        data_file = Path(data_path)
        parsed_data = json.loads(data_file.read_text(encoding="utf-8"))
        self._titles = {
            self._extract_title(item)
            for item in parsed_data
            if self._extract_title(item)
        }


    def is_duplicate(self, procurement):
        title = self._extract_title(procurement)
        return 1 if title and title in self._titles else 0


    def _extract_title(self, procurement):
        tender = procurement.get("tender") if isinstance(procurement, dict) else None
        if isinstance(tender, dict) and tender.get("title"):
            return tender["title"]
        if isinstance(procurement, dict) and procurement.get("title"):
            return procurement["title"]
        return None
