from bird_data_loader import BirdDataLoader
from approach_evaluator import Appraoch_Evaluator

bird_data_loader = BirdDataLoader("data/dev/dev.json")


def nl_to_sql(nl_input: str):
    """
    Function to turn a natural language prompt to SQL.
    This is just a placeholder and should be replaced with a function actually performing transformation.
    """
    return nl_input.capitalize()


approach_evaluator = Appraoch_Evaluator(
    nl_to_sql, bird_data_loader.get_questions(), bird_data_loader.get_target_sqls()
)

print(approach_evaluator.evaluate())
