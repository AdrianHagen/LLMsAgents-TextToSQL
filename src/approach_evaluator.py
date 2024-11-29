import os
from typing import Callable, List
import numpy as np
import pandas as pd
import sqlparse
from difflib import SequenceMatcher
from tools.database import Database
import csv
import pandas as pd
from datetime import datetime
import json


class ApproachEvaluator:
    """
    A class to evaluate the performance of a given approach for query generation
    against a set of target queries using specified evaluation methods.

    Attributes:
        approach (Callable[[str], str]):
            The function or callable that generates a predicted query from input text.
        input_texts (List[str]):
            A list of input texts for which queries will be generated.
        target_queries (List[str]):
            A list of target queries corresponding to the input texts.
        accuracies (List[float]):
            A list storing evaluation scores for each input.

    Methods:
        evaluate(evaluation_method: str = "exact_matching") -> float:
            Evaluates the approach based on the chosen method and returns the average accuracy.
        exact_matching(predicted: str, target: str) -> int:
            Compares predicted and target queries for an exact match (case-insensitive).
        compare_tokenized(query1: str, query2: str) -> float:
            Compares predicted and target queries based on their tokenized similarity.
    """

    def __init__(
        self, run_config: dict, question_ids: List[int], approach: Callable[[str], str]
    ):
        """
        Initializes the ApproachEvaluator with the provided approach, inputs, and targets.

        Args:
            run_config (dict): The configuration for the run.
            question_ids (List[int]): The list of query IDs to filter the data.
            approach (Callable[[str], str]): A function or callable that generates a query from input text.

        Raises:
            AssertionError: If the lengths of input_texts and target_queries do not match.
        """
        self.run_config = run_config
        self.approach = approach
        self.question_ids = question_ids
        dev_data = pd.read_json(os.path.join(os.getenv("DATA_DIRECTORY"), "dev.json"))

        # Filter the data based on question_ids
        filtered_data = dev_data[dev_data["question_id"].isin(self.question_ids)]

        self.input_texts = filtered_data["question"].tolist()
        self.target_queries = filtered_data["SQL"].tolist()

        # Ensure the lengths of input_texts and target_queries match
        assert len(self.input_texts) == len(
            self.target_queries
        ), "Input texts and target queries lengths do not match."

    def evaluate(self, evaluation_method: str = "compare_query_results") -> float:
        """
        Evaluates the approach using the specified evaluation method.

        Args:
            evaluation_method (str):
                The method to use for evaluation. Options are:
                - "exact_matching": Checks for exact matches between predicted and target queries.
                - "compare_queries": Compares queries using tokenized similarity.
                - "compare_query_results": Compares the results of the queries.

        Returns:
            float: The average accuracy or similarity score across all inputs.

        Raises:
            ValueError: If the provided evaluation method is not recognized.
        """
        method_map = {
            "exact_matching": self.exact_matching,
            "compare_tokenized": self.compare_tokenized,
            "compare_query_results": self.compare_query_results,
        }

        if evaluation_method not in method_map:
            raise ValueError(f"Invalid evaluation method: {evaluation_method}")

        evaluation_function = method_map[evaluation_method]

        results = {
            "question_id": [],
            "predicted_query": [],
            "predicted_database": [],
            "feedbacks": [],
            "errors": [],
            "is_correct": [],
        }

        for question_id, input_text, target_query in zip(
            self.question_ids, self.input_texts, self.target_queries
        ):
            predicted_query, database, feedbacks, errors = self.approach(input_text)
            is_correct = [
                1 if evaluation_function(database, predicted_query, target_query) else 0
            ]
            results["question_id"].append(question_id)
            results["predicted_query"].append(predicted_query)
            results["predicted_database"].append(database)
            results["feedbacks"].append(feedbacks)
            results["errors"].append(errors)
            results["is_correct"].append(is_correct)

        self.log_results(results)

        return results

    def log_results(self, results: dict):
        """
        Logs the results of the evaluation to a CSV file and saves the run configuration.

        Args:
            results (dict): The results of the evaluation.
        """
        # Convert any Pandas Series in the results to lists
        for key, value in results.items():
            if isinstance(value, pd.Series):
                results[key] = value.tolist()

        # Generate the timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create a directory with the timestamp
        results_dir = os.path.join(
            os.getenv("EVAL_DIRECTORY"), "results", f"results_{timestamp}"
        )
        os.makedirs(results_dir, exist_ok=True)

        # Save the run configuration as a JSON file in the directory
        run_config_path = os.path.join(results_dir, "run_config.json")
        with open(run_config_path, "w") as json_file:
            json.dump(self.run_config, json_file, indent=4)

        # Determine the CSV file path in the directory
        csv_file_path = os.path.join(results_dir, "results.csv")

        # Write the results to the CSV file
        with open(csv_file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=results.keys())
            writer.writeheader()
            writer.writerows(
                [dict(zip(results.keys(), row)) for row in zip(*results.values())]
            )

    def exact_matching(self, database: str, predicted: str, target: str) -> int:
        """
        Compares two queries for exact (case-insensitive) matches.

        Args:
            predicted (str): The predicted query.
            target (str): The target (expected) query.

        Returns:
            int: 1 if the queries match exactly (case-insensitive), otherwise 0.
        """
        return 1 if predicted.lower() == target.lower() else 0

    def _normalize_sql(self, query: str) -> str:
        """
        Normalizes an SQL query by reformatting and standardizing keyword casing.

        Args:
            query (str): The SQL query to normalize.

        Returns:
            str: The normalized SQL query.
        """
        return sqlparse.format(query, reindent=True, keyword_case="upper")

    def compare_tokenized(self, database: str, query1: str, query2: str) -> float:
        """
        Compares two SQL queries based on tokenized similarity.

        Args:
            query1 (str): The first SQL query.
            query2 (str): The second SQL query.

        Returns:
            float: A similarity score between 0 and 1 based on tokenized content.
        """
        normalized_query1 = self._normalize_sql(query1)
        normalized_query2 = self._normalize_sql(query2)
        similarity = SequenceMatcher(None, normalized_query1, normalized_query2).ratio()
        return similarity

    def compare_query_results(
        self, database: str, predicted_query: str, target_query: str
    ) -> bool:
        """
        Compares the results of two SQL queries.

        Args:
            predicted_query (str): The predicted SQL query.
            query2 (str): The target SQL query.

        Returns:
            bool: A boolean value indicating whether the query results are the same.
        """
        try:
            predicted_result, _ = db.execute_query(predicted_query)
            target_result, _ = db.execute_query(target_query)
            print(
                f"Predicted result: {predicted_result}, Target result: {target_result}"
            )
            return predicted_result == target_result
        except Exception as e:
            print(f"Error with final query: {e}")
            print(f"Target query: {target_query}")
            print(f"Predicted query: {predicted_query}")
            return False


def avg_execution_time(db_ids: List[str], queries: List[str]) -> List[float]:
    outer_execution_times = []

    for db_id, query in zip(db_ids, queries):
        execution_times = []

        db = Database(db_id)

        for i in range(100):
            _, execution_time = db.execute_query(query)
            if execution_time > 30:
                execution_time = 30
            execution_times.append(execution_time)

        execution_times = np.array(execution_times)
        mean = execution_times.mean()
        std = execution_times.std()

        ma = mean + 3 * std
        mi = mean - 3 * std

        execution_times = execution_times[
            (execution_times >= mi) & (execution_times <= ma)
        ]
        mean = execution_times.mean()

        outer_execution_times.append(execution_times.mean())

    return outer_execution_times


def valid_efficiency_score(df: pd.DataFrame) -> float:
    """
    Calculates the valid efficiency score for the given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the evaluation data.

    Returns:
        float: The valid efficiency score.
    """
    # Read the development dataset
    dev = pd.read_csv("../sample/dev.csv")

    n = len(dev)

    dev = dev[df["is_correct"] == 1]
    df = df[df["is_correct"] == 1]

    # Calculate the average predicted execution times
    avg_predicted_execution_times = avg_execution_time(
        df["predicted_database"], df["predicted_query"]
    )

    # Calculate the valid efficiency score
    score = (
        df["is_correct"]
        * np.sqrt(dev["execution_time"] / avg_predicted_execution_times)
    ).sum() / n

    return score
