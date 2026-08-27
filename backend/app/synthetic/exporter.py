import os
import json
import csv
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List


class DecimalAndDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class SyntheticDataExporter:
    """Exports generated dataset into structured JSON and individual entity CSVs."""

    @staticmethod
    def export_to_json(dataset: Dict[str, Any], filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dataset, f, cls=DecimalAndDateTimeEncoder, indent=2)
        return filepath

    @staticmethod
    def export_to_csv_directory(dataset: Dict[str, Any], directory_path: str) -> Dict[str, str]:
        os.makedirs(directory_path, exist_ok=True)
        exported_files = {}

        for entity_name, records in dataset.items():
            if not records:
                continue
            
            file_path = os.path.join(directory_path, f"{entity_name}.csv")
            fieldnames = list(records[0].keys())

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in records:
                    formatted_row = {}
                    for k, v in row.items():
                        if isinstance(v, Decimal):
                            formatted_row[k] = str(v)
                        elif isinstance(v, datetime):
                            formatted_row[k] = v.isoformat()
                        elif isinstance(v, (list, dict)):
                            formatted_row[k] = json.dumps(v)
                        else:
                            formatted_row[k] = v
                    writer.writerow(formatted_row)

            exported_files[entity_name] = file_path

        return exported_files
