import json
from typing import List, Optional, Union


class BirdDataLoader:
    """
    A class to load and process bird-related data from a JSON file.

    Attributes:
        file_path (str): The path to the JSON file containing bird data.
        data (Optional[List[dict]]): The loaded data from the JSON file,
            or None if the file could not be loaded.

    Methods:
        get_all_data() -> Optional[List[dict]]:
            Returns the entire loaded data.
        get_questions() -> Optional[List[str]]:
            Extracts and returns all questions from the data.
        get_target_sqls() -> Optional[List[str]]:
            Extracts and returns all SQL queries from the data.
    """

    def __init__(self, file_path: str):
        """
        Initializes the BirdDataLoader with the specified file path and loads the data.

        Args:
            file_path (str): The path to the JSON file containing bird data.

        Attributes:
            data (Optional[List[dict]]): The loaded JSON data as a list of dictionaries.

        Exceptions:
            Prints an error message if the file is not found or if the JSON is invalid.
        """
        self.file_path = file_path
        self.data: Optional[List[dict]] = None

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: File '{self.file_path}' is not a valid JSON file.")

    def get_all_data(self) -> Optional[List[dict]]:
        """
        Returns the entire loaded data.

        Returns:
            Optional[List[dict]]: The loaded data as a list of dictionaries,
            or None if the data could not be loaded.
        """
        return self.data

    def get_questions(self) -> Optional[List[str]]:
        """
        Extracts and returns all questions from the loaded data.

        Returns:
            Optional[List[str]]: A list of questions from the data,
            or None if the data is not loaded.
        """
        if self.data is None:
            return None
        return [entry.get("question") for entry in self.data if "question" in entry]

    def get_target_sqls(self) -> Optional[List[str]]:
        """
        Extracts and returns all SQL queries from the loaded data.

        Returns:
            Optional[List[str]]: A list of SQL queries from the data,
            or None if the data is not loaded.
        """
        if self.data is None:
            return None
        return [entry.get("SQL") for entry in self.data if "SQL" in entry]
