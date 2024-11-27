from typing import Callable, List
import numpy as np
import sqlparse
from difflib import SequenceMatcher
from tools.database import Database


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
        self,
        approach: Callable[[str], str],
        input_texts: List[str],
        target_queries: List[str],
    ):
        """
        Initializes the ApproachEvaluator with the provided approach, inputs, and targets.

        Args:
            approach (Callable[[str], str]):
                A function or callable that generates a query from input text.
            input_texts (List[str]):
                The list of input texts for query generation.
            target_queries (List[str]):
                The list of expected (target) queries.

        Raises:
            AssertionError: If the lengths of input_texts and target_queries do not match.
        """
        self.approach = approach
        assert len(input_texts) == len(
            target_queries
        ), "Input texts and target queries must have the same length."
        self.input_texts = input_texts
        self.target_queries = target_queries
        self.accuracies = []

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

        for input_text, target_query in zip(self.input_texts, self.target_queries):
            predicted_query, database = self.approach(input_text)
            accuracy = evaluation_function(database, predicted_query, target_query)
            self.accuracies.append(accuracy)

        return np.mean(self.accuracies)

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
        db = Database(database)
        try:
            predicted_result = db.execute_query(predicted_query)
            target_result = db.execute_query(target_query)
            print(
                f"Predicted result: {predicted_result}, Target result: {target_result}"
            )
            return predicted_result == target_result
        except Exception as e:
            print(f"Error comparing query results: {e}")
            print(f"Target query: {target_query}")
            print(f"Predicted query: {predicted_query}")
            return False
