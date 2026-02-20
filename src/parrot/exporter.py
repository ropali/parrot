import csv
import datetime
from enum import StrEnum
import json
from pathlib import Path
from typing import List

from parrot.data_models import Conversation


class ExportType(StrEnum):
    TEXT = "text"
    JSON = "json"
    CSV = "csv"

class Exporter:
    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_name = f"Parrot_Export_{self.timestamp}"

    def export(self, export_type: ExportType, file_path: str):
        """Main export method that delegates to specific format handlers"""
        export_methods = {
            ExportType.TEXT: self._to_text,
            ExportType.JSON: self._to_json,
            ExportType.CSV: self._to_csv
        }
        
        if export_type not in export_methods:
            raise ValueError(f"Unsupported export type: {export_type}")

        Path(file_path).mkdir(parents=True, exist_ok=True)
        
        export_methods[export_type](file_path)

    def _to_text(self, file_path: str):
        full_path = Path(file_path) / f"{self.file_name}.txt"
        with open(full_path, "w", encoding="utf-8") as file:
            for message in self.conversation.get_messages():
                file.write(f"{message}\n")

    def _to_json(self, file_path: str):
        full_path = Path(file_path) / f"{self.file_name}.json"
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "messages": [msg.to_dict() for msg in self.conversation.get_messages()],
                    "total_messages": len(self.conversation)
                },
                file,
                indent=2
            )

    def _to_csv(self, file_path: str):
        full_path = Path(file_path) / f"{self.file_name}.csv"
        with open(full_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Sender", "Content"])  # Header
            for message in self.conversation.get_messages():
                writer.writerow([message.sender, message.content])
