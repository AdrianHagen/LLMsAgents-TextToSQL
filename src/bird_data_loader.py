import json


class BirdDataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error: File '{self.file_path}' is not a valid JSON file.")
            return None

    def get_all_data(self):
        return self.data

    def get_questions(self):
        if self.data is None:
            return None
        return [entry.get("question") for entry in self.data if "question" in entry]

    def get_target_sqls(self):
        if self.data is None:
            return None
        return [entry.get("SQL") for entry in self.data if "SQL" in entry]
