from typing import Callable
import numpy as np
import nltk

nltk.download("punkt_tab")
from nltk.tokenize import word_tokenize


class Appraoch_Evaluator:
    def __init__(self, approach: Callable[[str], str], input_texts, target_queries):
        self.approach = approach
        assert len(input_texts) == len(target_queries)
        self.input_texts = input_texts
        self.target_queries = target_queries
        self.accuracies = []

    def evaluate(self):
        for idx, input_text in enumerate(self.input_texts):
            predicted_query = self.approach(input_text)
            accuracy = self.jaccard_similarity(
                predicted_query, self.target_queries[idx]
            )
            self.accuracies.append(accuracy)
        return np.mean(self.accuracies)

    def jaccard_similarity(self, predicted, target):
        """The jaccard similarity is just a placeholder for an evaluation method
        and should be replaced with something more suitable."""
        set1 = set(word_tokenize(predicted))
        set2 = set(word_tokenize(target))
        return (
            len(set1.intersection(set2)) / len(set1.union(set2))
            if len(set1.union(set2)) > 0
            else 0
        )
