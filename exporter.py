import datetime
from typing import List


class Exporter:

    def __init__(self, data: List):
        self.data = data

        self.file_name = f"Parrot-History-{datetime.datetime.now()}"


    def to_text(self, file_path: str):
        file_name = f"{self.file_name}.txt"

        with open(f"{file_path}/{file_name}", "w") as file:
            file.writelines("\n".join([f"{k}>{v}" for k,v in self.data]))
